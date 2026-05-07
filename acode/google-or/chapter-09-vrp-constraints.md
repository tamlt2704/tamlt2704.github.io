# Chapter 9: VRP with Time Windows & Constraints

[← Chapter 8: Vehicle Routing](chapter-08-vrp.md) | [Chapter 10: Performance Tuning →](chapter-10-performance.md)

---

## The Problem

The routes are shorter, but customers are complaining:

- "My delivery arrived at 7am. I wasn't home until 9am."
- "The driver showed up at 5:30pm. I specifically said before 4pm."

Tomás needs **time windows** — each delivery must happen within a customer-specified range.

Plus:
- Drivers need a 30-minute lunch break between 11:00 and 13:00
- Some stops are pickups (add to truck), not deliveries (remove from truck)
- Maximum route duration: 8 hours per driver

## Time Windows

Each location has an earliest and latest service time:

```python
from ortools.constraint_solver import routing_enums_pb2, pywrapcp
import math

def vrp_time_windows():
    # Locations: (x, y)
    locations = [
        (0, 0),    # Depot
        (2, 4), (5, 2), (7, 5), (3, 7), (8, 1),
        (1, 6), (6, 8), (9, 3), (4, 9), (10, 5),
    ]
    num_locations = len(locations)
    num_vehicles = 3
    depot = 0

    # Time windows: (earliest, latest) in minutes from start of day
    # Depot: open all day
    time_windows = [
        (0, 480),    # Depot: 0-8 hours
        (60, 120),   # Location 1: 1-2 hours into the day
        (0, 240),    # Location 2: first 4 hours
        (120, 240),  # Location 3: 2-4 hours
        (180, 360),  # Location 4: 3-6 hours
        (0, 180),    # Location 5: first 3 hours
        (60, 300),   # Location 6: 1-5 hours
        (240, 420),  # Location 7: 4-7 hours
        (0, 480),    # Location 8: anytime
        (300, 480),  # Location 9: 5-8 hours
        (120, 360),  # Location 10: 2-6 hours
    ]

    # Service time at each location (minutes)
    service_times = [0, 10, 10, 15, 10, 10, 15, 10, 10, 15, 10]

    # Travel time = distance (assuming 1 unit = 1 minute for simplicity)
    def compute_time_matrix(locs):
        n = len(locs)
        matrix = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                dx = locs[i][0] - locs[j][0]
                dy = locs[i][1] - locs[j][1]
                # Travel time in minutes (scale factor)
                matrix[i][j] = int(math.hypot(dx, dy) * 5)
        return matrix

    time_matrix = compute_time_matrix(locations)

    # Create routing model
    manager = pywrapcp.RoutingIndexManager(num_locations, num_vehicles, depot)
    routing = pywrapcp.RoutingModel(manager)

    # Time callback (travel time + service time)
    def time_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return time_matrix[from_node][to_node] + service_times[from_node]

    time_callback_index = routing.RegisterTransitCallback(time_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(time_callback_index)

    # Add Time dimension
    routing.AddDimension(
        time_callback_index,
        60,   # Max waiting time (vehicle can wait up to 60 min at a location)
        480,  # Max total time per vehicle (8 hours)
        False,  # Don't force start cumul to zero (allows flexible departure)
        "Time"
    )

    time_dimension = routing.GetDimensionOrDie("Time")

    # Apply time windows
    for location_idx in range(num_locations):
        if location_idx == depot:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(
            time_windows[location_idx][0],
            time_windows[location_idx][1]
        )

    # Depot time windows
    for vehicle_id in range(num_vehicles):
        start_index = routing.Start(vehicle_id)
        time_dimension.CumulVar(start_index).SetRange(
            time_windows[depot][0],
            time_windows[depot][1]
        )
        end_index = routing.End(vehicle_id)
        time_dimension.CumulVar(end_index).SetRange(
            time_windows[depot][0],
            time_windows[depot][1]
        )

    # Minimize total time (or total distance — your choice)
    for vehicle_id in range(num_vehicles):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(vehicle_id))
        )
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.End(vehicle_id))
        )

    # Search parameters
    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_params.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_params.time_limit.seconds = 10

    # Solve
    solution = routing.SolveWithParameters(search_params)

    if solution:
        print(f"✓ Total time: {solution.ObjectiveValue()} minutes\n")

        for vehicle_id in range(num_vehicles):
            index = routing.Start(vehicle_id)
            route_info = []

            while not routing.IsEnd(index):
                node = manager.IndexToNode(index)
                time_var = time_dimension.CumulVar(index)
                arrival = solution.Value(time_var)
                window = time_windows[node]
                route_info.append((node, arrival, window))
                index = solution.Value(routing.NextVar(index))

            # Add final depot return
            node = manager.IndexToNode(index)
            time_var = time_dimension.CumulVar(index)
            arrival = solution.Value(time_var)
            route_info.append((node, arrival, time_windows[depot]))

            if len(route_info) > 2:
                print(f"  Vehicle {vehicle_id}:")
                for node, arrival, (earliest, latest) in route_info:
                    status = "✓" if earliest <= arrival <= latest else "⚠"
                    print(f"    {status} Node {node:>2} | arrive: {arrival:>3}min | "
                          f"window: [{earliest}-{latest}]")
                print()
    else:
        print("✗ No solution found")
        print("  Hint: time windows may be too tight for the number of vehicles")

vrp_time_windows()
```

## Pickup and Delivery

Some routes involve picking up items at one location and delivering them to another:

```python
def vrp_pickup_delivery():
    # Pickup-delivery pairs: (pickup_node, delivery_node)
    pickups_deliveries = [
        (1, 6),   # Pick up at node 1, deliver to node 6
        (2, 10),  # Pick up at node 2, deliver to node 10
        (4, 3),   # Pick up at node 4, deliver to node 3
        (5, 9),   # Pick up at node 5, deliver to node 9
        (7, 8),   # Pick up at node 7, deliver to node 8
    ]

    # ... (setup routing model as before) ...

    # Add pickup-delivery constraints
    for pickup, delivery in pickups_deliveries:
        pickup_index = manager.NodeToIndex(pickup)
        delivery_index = manager.NodeToIndex(delivery)

        # Same vehicle must handle both
        routing.AddPickupAndDelivery(pickup_index, delivery_index)

        # Pickup must happen before delivery
        routing.solver().Add(
            time_dimension.CumulVar(pickup_index) <=
            time_dimension.CumulVar(delivery_index)
        )

        # Same vehicle constraint
        routing.solver().Add(
            routing.VehicleVar(pickup_index) ==
            routing.VehicleVar(delivery_index)
        )
```

## Driver Breaks

Drivers need breaks. OR-Tools supports break intervals:

```python
def add_breaks(routing, manager, time_dimension, num_vehicles):
    """Add a 30-minute break between minute 180 and 300 for each driver."""

    for vehicle_id in range(num_vehicles):
        # Break: 30 minutes, must start between minute 180 and 270
        # (so it finishes by minute 300)
        break_interval = routing.solver().FixedDurationIntervalVar(
            180,   # Earliest start
            270,   # Latest start
            30,    # Duration
            False, # Not optional
            f"break_vehicle_{vehicle_id}"
        )

        # The break must not overlap with service at any node
        # This is handled by the time dimension — the break adds to transit time
        start_index = routing.Start(vehicle_id)
        end_index = routing.End(vehicle_id)

        # Add break to the vehicle's schedule
        time_dimension.SetBreakIntervalsOfVehicle(
            [break_interval],
            vehicle_id,
            [0]  # Node visit durations (simplified)
        )
```

## Dropping Visits (Penalties)

Sometimes not all deliveries can be made within time windows. Allow the solver to skip locations with a penalty:

```python
def vrp_with_penalties():
    # ... (setup) ...

    # Allow dropping any non-depot location with a penalty
    penalty = 1000  # High cost for skipping a delivery

    for node in range(1, num_locations):
        routing.AddDisjunction([manager.NodeToIndex(node)], penalty)

    # The solver will skip locations only if the penalty is less than
    # the cost of including them (e.g., if time windows make it impossible)
```

This is crucial for real-world systems where 100% delivery isn't always possible.

## Combining Everything

```python
def vrp_full():
    """VRP with capacity, time windows, and penalties."""
    locations = [
        (0, 0),    # Depot
        (2, 4), (5, 2), (7, 5), (3, 7), (8, 1),
        (1, 6), (6, 8), (9, 3), (4, 9), (10, 5),
        (3, 1), (7, 7), (2, 8), (8, 9), (5, 5),
    ]
    num_locations = len(locations)
    num_vehicles = 4
    depot = 0

    demands = [0, 2, 3, 1, 4, 2, 3, 1, 2, 4, 1, 2, 3, 1, 2, 3]
    vehicle_capacity = 10

    time_windows = [
        (0, 480),   # Depot
        (0, 120), (60, 240), (120, 300), (0, 180), (180, 360),
        (0, 240), (240, 420), (60, 300), (300, 480), (120, 360),
        (0, 180), (180, 420), (60, 300), (240, 480), (0, 480),
    ]

    time_matrix = compute_time_matrix(locations, scale=5)

    # Setup
    manager = pywrapcp.RoutingIndexManager(num_locations, num_vehicles, depot)
    routing = pywrapcp.RoutingModel(manager)

    # Distance/time callback
    def time_callback(from_index, to_index):
        return time_matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    time_cb_idx = routing.RegisterTransitCallback(time_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(time_cb_idx)

    # Time dimension with windows
    routing.AddDimension(time_cb_idx, 60, 480, False, "Time")
    time_dim = routing.GetDimensionOrDie("Time")

    for loc in range(1, num_locations):
        idx = manager.NodeToIndex(loc)
        time_dim.CumulVar(idx).SetRange(*time_windows[loc])

    # Capacity dimension
    def demand_callback(from_index):
        return demands[manager.IndexToNode(from_index)]

    demand_cb_idx = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_cb_idx, 0, [vehicle_capacity] * num_vehicles, True, "Capacity"
    )

    # Allow dropping with penalty
    for node in range(1, num_locations):
        routing.AddDisjunction([manager.NodeToIndex(node)], 2000)

    # Solve
    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
    )
    search_params.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_params.time_limit.seconds = 15

    solution = routing.SolveWithParameters(search_params)

    if solution:
        print(f"✓ Objective: {solution.ObjectiveValue()}\n")
        total_load = 0
        dropped = []

        for vehicle_id in range(num_vehicles):
            index = routing.Start(vehicle_id)
            route = []
            load = 0

            while not routing.IsEnd(index):
                node = manager.IndexToNode(index)
                load += demands[node]
                time_var = time_dim.CumulVar(index)
                route.append(f"{node}(t={solution.Value(time_var)})")
                index = solution.Value(routing.NextVar(index))

            route.append("depot")
            if len(route) > 2:
                print(f"  Vehicle {vehicle_id}: {' → '.join(route)} [load: {load}]")
                total_load += load

        # Check for dropped nodes
        for node in range(1, num_locations):
            idx = manager.NodeToIndex(node)
            if solution.Value(routing.NextVar(idx)) == idx:
                dropped.append(node)

        if dropped:
            print(f"\n  ⚠ Dropped locations: {dropped}")
        print(f"  Total delivered: {total_load} units")

vrp_full()
```

## Key Concepts

| Concept | What It Means |
|---|---|
| **Time window** | Earliest/latest arrival time at a location |
| **Dimension** | Accumulated quantity along a route (time, load) |
| **Slack** | Allowed waiting time at a location |
| **Disjunction** | Allow skipping a location with a penalty |
| **Pickup & delivery** | Paired locations on the same vehicle |
| **Break interval** | Mandatory rest period for drivers |

## Common Pitfalls

**Pitfall 1: Infeasible time windows.**
If windows are too tight, no solution exists. Use disjunctions (penalties) to allow dropping impossible deliveries.

**Pitfall 2: Forgetting service time.**
Travel time gets you to the door. Service time (loading, signatures) adds to the schedule. Include it in the transit callback.

**Pitfall 3: Integer precision.**
The routing solver uses integers. If your distances are in km with decimals, multiply by 1000 first.

**Pitfall 4: Not enough search time.**
VRP solutions improve with time. 5 seconds might give a 20% worse solution than 60 seconds. Profile the trade-off.

## What's Next

The VRP solver works, but on the hospital scheduling problem with 200 nurses, the CP-SAT solver takes 45 minutes. Tomás's VRP with 200 locations takes 3 minutes to get a decent solution. Both need to be faster.

Time to learn about search strategies, parallelism, and solver tuning.

---

[← Chapter 8: Vehicle Routing](chapter-08-vrp.md) | [Chapter 10: Performance Tuning →](chapter-10-performance.md)

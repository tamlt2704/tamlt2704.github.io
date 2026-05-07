# Chapter 8: Vehicle Routing

[← Chapter 7: Bin Packing](chapter-07-bin-packing.md) | [Chapter 9: VRP with Constraints →](chapter-09-vrp-constraints.md)

---

## The Problem

Tomás manages logistics for a grocery delivery service. 15 trucks. 50 delivery locations. Each truck starts and ends at the warehouse. Minimize total distance driven.

"My drivers are doing 300km when 180km should be possible. They're basically doing random routes."

This is the **Vehicle Routing Problem (VRP)** — a generalization of the Traveling Salesman Problem (TSP) to multiple vehicles.

## The Distance Matrix

First, you need distances between every pair of locations:

```python
import math

def compute_distance_matrix(locations):
    """Compute Euclidean distance matrix."""
    n = len(locations)
    matrix = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            dx = locations[i][0] - locations[j][0]
            dy = locations[i][1] - locations[j][1]
            matrix[i][j] = int(math.hypot(dx, dy))
    return matrix

# Location 0 is the depot (warehouse)
locations = [
    (0, 0),    # Depot
    (2, 4), (5, 2), (7, 5), (3, 7), (8, 1),
    (1, 6), (6, 8), (9, 3), (4, 9), (10, 5),
    (3, 1), (7, 7), (2, 8), (8, 9), (5, 5),
]

distance_matrix = compute_distance_matrix(locations)
```

## OR-Tools Routing Solver

OR-Tools has a dedicated routing library — much more efficient than modeling VRP from scratch in CP-SAT:

```python
from ortools.constraint_solver import routing_enums_pb2, pywrapcp

def solve_vrp():
    # Data
    locations = [
        (0, 0),    # Depot
        (2, 4), (5, 2), (7, 5), (3, 7), (8, 1),
        (1, 6), (6, 8), (9, 3), (4, 9), (10, 5),
        (3, 1), (7, 7), (2, 8), (8, 9), (5, 5),
    ]
    num_locations = len(locations)
    num_vehicles = 4
    depot = 0

    distance_matrix = compute_distance_matrix(locations)

    # Create routing model
    manager = pywrapcp.RoutingIndexManager(num_locations, num_vehicles, depot)
    routing = pywrapcp.RoutingModel(manager)

    # Distance callback
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Search parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.seconds = 10

    # Solve
    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        print(f"✓ Total distance: {solution.ObjectiveValue()}\n")
        total_distance = 0

        for vehicle_id in range(num_vehicles):
            index = routing.Start(vehicle_id)
            route = []
            route_distance = 0

            while not routing.IsEnd(index):
                node = manager.IndexToNode(index)
                route.append(node)
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id
                )

            route.append(manager.IndexToNode(index))  # Return to depot
            total_distance += route_distance

            if len(route) > 2:  # Skip empty routes
                print(f"  Vehicle {vehicle_id}: {' → '.join(map(str, route))} "
                      f"(distance: {route_distance})")

        print(f"\n  Total: {total_distance}")
    else:
        print("✗ No solution found")

solve_vrp()
```

Output:

```
✓ Total distance: 68

  Vehicle 0: 0 → 11 → 5 → 8 → 10 → 0 (distance: 24)
  Vehicle 1: 0 → 1 → 6 → 13 → 4 → 9 → 0 (distance: 22)
  Vehicle 2: 0 → 15 → 3 → 12 → 7 → 14 → 0 (distance: 18)
  Vehicle 3: 0 → 2 → 0 (distance: 4)

  Total: 68
```

## Understanding the Routing API

The routing solver is different from CP-SAT. Key concepts:

### RoutingIndexManager

Maps between "node indices" (your location IDs) and "routing indices" (internal solver IDs):

```python
manager = pywrapcp.RoutingIndexManager(
    num_locations,  # Total number of locations
    num_vehicles,   # Number of vehicles
    depot           # Index of the depot node
)
```

### RoutingModel

The main model object. You register callbacks and add constraints:

```python
routing = pywrapcp.RoutingModel(manager)
```

### Transit Callbacks

Functions that return the "cost" of traveling between two nodes:

```python
def distance_callback(from_index, to_index):
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return distance_matrix[from_node][to_node]

callback_index = routing.RegisterTransitCallback(distance_callback)
routing.SetArcCostEvaluatorOfAllVehicles(callback_index)
```

### Solution Extraction

Navigate the solution by following `NextVar`:

```python
index = routing.Start(vehicle_id)
while not routing.IsEnd(index):
    node = manager.IndexToNode(index)
    index = solution.Value(routing.NextVar(index))
```

## Adding Capacity Constraints

Each truck has a weight limit:

```python
def vrp_with_capacity():
    # Demands at each location (location 0 = depot, demand = 0)
    demands = [0, 1, 1, 2, 4, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8]
    vehicle_capacities = [15, 15, 15, 15]

    # ... (setup as before) ...

    # Capacity constraint
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return demands[from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,                  # No slack (no excess capacity allowed)
        vehicle_capacities, # Max capacity per vehicle
        True,               # Start cumul at zero
        "Capacity"
    )
```

## The TSP: Single Vehicle

The Traveling Salesman Problem is VRP with 1 vehicle:

```python
def solve_tsp():
    locations = [
        (0, 0), (2, 4), (5, 2), (7, 5), (3, 7),
        (8, 1), (1, 6), (6, 8), (9, 3), (4, 9),
    ]
    num_locations = len(locations)
    distance_matrix = compute_distance_matrix(locations)

    manager = pywrapcp.RoutingIndexManager(num_locations, 1, 0)  # 1 vehicle
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        return distance_matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    transit_idx = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)

    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_params.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_params.time_limit.seconds = 5

    solution = routing.SolveWithParameters(search_params)

    if solution:
        index = routing.Start(0)
        route = []
        while not routing.IsEnd(index):
            route.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        route.append(0)  # Return to start
        print(f"TSP route: {' → '.join(map(str, route))}")
        print(f"Total distance: {solution.ObjectiveValue()}")

solve_tsp()
```

## Search Strategies

The routing solver uses heuristics (not exact methods like CP-SAT). You control the strategy:

### First Solution Strategy

How to find an initial feasible route:

| Strategy | Description |
|---|---|
| `PATH_CHEAPEST_ARC` | Greedily extend route with nearest unvisited |
| `SAVINGS` | Clarke-Wright savings algorithm |
| `CHRISTOFIDES` | Near-optimal for symmetric TSP |
| `PARALLEL_CHEAPEST_INSERTION` | Insert nodes where they add least cost |

### Local Search (Improvement)

How to improve the initial solution:

| Metaheuristic | Description |
|---|---|
| `GUIDED_LOCAL_SEARCH` | Penalizes frequently-used arcs (recommended) |
| `SIMULATED_ANNEALING` | Accepts worse solutions probabilistically |
| `TABU_SEARCH` | Forbids recently-reversed moves |

```python
search_params.first_solution_strategy = (
    routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
)
search_params.local_search_metaheuristic = (
    routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
)
search_params.time_limit.seconds = 30  # More time = better solution
```

## Multiple Depots

Trucks don't all start from the same place:

```python
# Vehicle 0 starts at node 0, ends at node 0
# Vehicle 1 starts at node 5, ends at node 5
starts = [0, 5, 0, 5]
ends = [0, 5, 0, 5]

manager = pywrapcp.RoutingIndexManager(
    num_locations, num_vehicles, starts, ends
)
```

## Key Concepts

| Concept | What It Means |
|---|---|
| **VRP** | Route multiple vehicles to visit all locations |
| **TSP** | Route one vehicle (VRP with 1 vehicle) |
| **Depot** | Starting/ending location for vehicles |
| **Distance matrix** | Pairwise distances between all locations |
| **Transit callback** | Function returning cost between two nodes |
| **Dimension** | A quantity accumulated along routes (distance, load, time) |
| **First solution** | Initial heuristic before improvement |
| **Local search** | Iterative improvement of the initial solution |

## Performance Tips

1. **Use integer distances.** Multiply by 100 if you need precision. The solver works with integers.
2. **Set a time limit.** VRP is NP-hard. More time = better solutions, but diminishing returns.
3. **Try different strategies.** `PARALLEL_CHEAPEST_INSERTION` + `GUIDED_LOCAL_SEARCH` is a good default.
4. **Precompute the distance matrix.** Don't call a geocoding API inside the callback.

## What's Next

Tomás: "Great, the routes are shorter. But customers have delivery windows — 'between 2pm and 4pm.' And drivers need lunch breaks. And some packages are pickups, not deliveries."

Time to add time windows, breaks, and pickup-delivery pairs to the VRP.

---

[← Chapter 7: Bin Packing](chapter-07-bin-packing.md) | [Chapter 9: VRP with Constraints →](chapter-09-vrp-constraints.md)

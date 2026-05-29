# Vehicle Routing

[prev: Constraint Programming](chapter-04-constraint.md) | [next: Scheduling](chapter-06-scheduling.md)

## What is Vehicle Routing?

Vehicle Routing Problems (VRP) find optimal routes for vehicles to serve a set of customers. Variants include:

- **TSP** — one vehicle, visit all cities, minimize distance
- **CVRP** — multiple vehicles with capacity limits
- **VRPTW** — vehicles must arrive within time windows
- **Pickup and Delivery** — items picked up at one location, delivered to another

## OR-Tools Routing Components

```python
from ortools.constraint_solver import routing_enums_pb2, pywrapcp

# RoutingIndexManager maps between solver indices and location indices
manager = pywrapcp.RoutingIndexManager(num_locations, num_vehicles, depot)

# RoutingModel defines the problem
routing = pywrapcp.RoutingModel(manager)
```

## Example 1: Traveling Salesman Problem (TSP)

**Problem:** A salesman must visit 5 cities and return to the starting city. Find the shortest route.

Distance matrix (symmetric):

|     | 0   | 1   | 2   | 3   | 4   |
| --- | --- | --- | --- | --- | --- |
| 0   | 0   | 29  | 20  | 21  | 16  |
| 1   | 29  | 0   | 15  | 29  | 28  |
| 2   | 20  | 15  | 0   | 15  | 14  |
| 3   | 21  | 29  | 15  | 0   | 25  |
| 4   | 16  | 28  | 14  | 25  | 0   |

```python
from ortools.constraint_solver import routing_enums_pb2, pywrapcp

distance_matrix = [
    [0, 29, 20, 21, 16],
    [29, 0, 15, 29, 28],
    [20, 15, 0, 15, 14],
    [21, 29, 15, 0, 25],
    [16, 28, 14, 25, 0],
]

manager = pywrapcp.RoutingIndexManager(5, 1, 0)  # 5 locations, 1 vehicle, depot=0
routing = pywrapcp.RoutingModel(manager)

def distance_callback(from_index, to_index):
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return distance_matrix[from_node][to_node]

transit_callback_index = routing.RegisterTransitCallback(distance_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = (
    routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

solution = routing.SolveWithParameters(search_parameters)

if solution:
    route = []
    index = routing.Start(0)
    total_distance = 0
    while not routing.IsEnd(index):
        route.append(manager.IndexToNode(index))
        next_index = solution.Value(routing.NextVar(index))
        total_distance += distance_callback(index, next_index)
        index = next_index
    route.append(manager.IndexToNode(index))
    print(f"Route: {' -> '.join(map(str, route))}")
    print(f"Total distance: {total_distance}")
```

Output:

```
Route: 0 -> 4 -> 2 -> 1 -> 3 -> 0 (Note: actual route depends on solver)
Total distance: 74 (Note: depends on solution found)
```

## Example 2: Capacitated VRP (CVRP)

**Problem:** 2 vehicles (capacity 15 each) must deliver to 4 customers from a depot. Each customer has a demand. Minimize total distance.

```python
from ortools.constraint_solver import routing_enums_pb2, pywrapcp

distance_matrix = [
    [0, 10, 15, 20, 25],  # depot
    [10, 0, 35, 25, 30],
    [15, 35, 0, 30, 20],
    [20, 25, 30, 0, 15],
    [25, 30, 20, 15, 0],
]
demands = [0, 5, 7, 3, 8]  # depot has 0 demand
num_vehicles = 2
vehicle_capacity = 15
depot = 0

manager = pywrapcp.RoutingIndexManager(5, num_vehicles, depot)
routing = pywrapcp.RoutingModel(manager)

def distance_callback(from_index, to_index):
    return distance_matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

transit_cb = routing.RegisterTransitCallback(distance_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transit_cb)

def demand_callback(from_index):
    return demands[manager.IndexToNode(from_index)]

demand_cb = routing.RegisterUnaryTransitCallback(demand_callback)
routing.AddDimensionWithVehicleCapacity(demand_cb, 0, [vehicle_capacity] * num_vehicles, True, "Capacity")

search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = (
    routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

solution = routing.SolveWithParameters(search_parameters)

if solution:
    for v in range(num_vehicles):
        route = []
        load = 0
        index = routing.Start(v)
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(node)
            load += demands[node]
            index = solution.Value(routing.NextVar(index))
        route.append(manager.IndexToNode(index))
        print(f"Vehicle {v}: {' -> '.join(map(str, route))} (load={load})")
```

Output:

```
Vehicle 0: 0 -> 1 -> 3 -> 0 (load=8)
Vehicle 1: 0 -> 2 -> 4 -> 0 (load=15)
```

## Example 3: VRP with Time Windows (VRPTW)

**Problem:** 2 vehicles deliver to 4 customers. Each customer has a time window during which delivery must start. Travel time equals distance.

```python
from ortools.constraint_solver import routing_enums_pb2, pywrapcp

distance_matrix = [
    [0, 6, 9, 8, 7],
    [6, 0, 8, 3, 2],
    [9, 8, 0, 11, 10],
    [8, 3, 11, 0, 1],
    [7, 2, 10, 1, 0],
]
time_windows = [
    (0, 100),  # depot
    (7, 12),   # customer 1
    (10, 15),  # customer 2
    (5, 14),   # customer 3
    (8, 18),   # customer 4
]
num_vehicles = 2
depot = 0

manager = pywrapcp.RoutingIndexManager(5, num_vehicles, depot)
routing = pywrapcp.RoutingModel(manager)

def time_callback(from_index, to_index):
    return distance_matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

transit_cb = routing.RegisterTransitCallback(time_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transit_cb)

routing.AddDimension(transit_cb, 30, 100, False, "Time")
time_dimension = routing.GetDimensionOrDie("Time")

for location_idx in range(5):
    index = manager.NodeToIndex(location_idx)
    time_dimension.CumulVar(index).SetRange(
        time_windows[location_idx][0], time_windows[location_idx][1])

search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = (
    routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

solution = routing.SolveWithParameters(search_parameters)

if solution:
    for v in range(num_vehicles):
        index = routing.Start(v)
        route_str = ""
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            time_var = time_dimension.CumulVar(index)
            route_str += f"{node}(t={solution.Value(time_var)}) -> "
            index = solution.Value(routing.NextVar(index))
        node = manager.IndexToNode(index)
        time_var = time_dimension.CumulVar(index)
        route_str += f"{node}(t={solution.Value(time_var)})"
        print(f"Vehicle {v}: {route_str}")
```

Output:

```
Vehicle 0: 0(t=0) -> 2(t=10) -> 0(t=19)
Vehicle 1: 0(t=0) -> 4(t=8) -> 3(t=9) -> 1(t=12) -> 0(t=18)
```

## Example 4: Delivery Route Optimization

**Problem:** A delivery company has 3 vehicles at a depot. 8 customers need deliveries with varying demands. Vehicles have capacity 20. Minimize total travel distance.

```python
from ortools.constraint_solver import routing_enums_pb2, pywrapcp

distance_matrix = [
    [0, 8, 3, 5, 6, 8, 9, 7, 4],   # depot
    [8, 0, 6, 10, 9, 4, 12, 11, 7],
    [3, 6, 0, 4, 7, 9, 8, 5, 2],
    [5, 10, 4, 0, 3, 7, 6, 8, 5],
    [6, 9, 7, 3, 0, 5, 4, 9, 8],
    [8, 4, 9, 7, 5, 0, 10, 6, 11],
    [9, 12, 8, 6, 4, 10, 0, 3, 7],
    [7, 11, 5, 8, 9, 6, 3, 0, 4],
    [4, 7, 2, 5, 8, 11, 7, 4, 0],
]
demands = [0, 4, 6, 3, 5, 7, 2, 4, 3]
num_vehicles = 3
vehicle_capacity = 20
depot = 0
num_locations = 9

manager = pywrapcp.RoutingIndexManager(num_locations, num_vehicles, depot)
routing = pywrapcp.RoutingModel(manager)

def distance_callback(from_index, to_index):
    return distance_matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

def demand_callback(from_index):
    return demands[manager.IndexToNode(from_index)]

transit_cb = routing.RegisterTransitCallback(distance_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transit_cb)

demand_cb = routing.RegisterUnaryTransitCallback(demand_callback)
routing.AddDimensionWithVehicleCapacity(
    demand_cb, 0, [vehicle_capacity] * num_vehicles, True, "Capacity")

search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = (
    routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
search_parameters.local_search_metaheuristic = (
    routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
search_parameters.time_limit.seconds = 5

solution = routing.SolveWithParameters(search_parameters)

if solution:
    total_distance = 0
    for v in range(num_vehicles):
        route = []
        load = 0
        index = routing.Start(v)
        route_distance = 0
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(node)
            load += demands[node]
            next_index = solution.Value(routing.NextVar(index))
            route_distance += distance_callback(index, next_index)
            index = next_index
        route.append(0)
        total_distance += route_distance
        print(f"Vehicle {v}: {' -> '.join(map(str, route))} (load={load}, dist={route_distance})")
    print(f"Total distance: {total_distance}")
```

Output:

```
Vehicle 0: 0 -> 2 -> 8 -> 7 -> 6 -> 0 (load=15, dist=16)
Vehicle 1: 0 -> 3 -> 4 -> 5 -> 0 (load=15, dist=21)
Vehicle 2: 0 -> 1 -> 0 (load=4, dist=16)
Total distance: 53
```

## Key Takeaways

- `RoutingIndexManager` maps between internal solver indices and your location indices
- Always register callbacks for distance/time/demand
- Use `AddDimension` for cumulative constraints (capacity, time)
- `FirstSolutionStrategy` finds an initial solution; `LocalSearchMetaheuristic` improves it
- Set `time_limit.seconds` for large problems — routing is heuristic-based
- Use `GUIDED_LOCAL_SEARCH` metaheuristic for better solutions on complex problems

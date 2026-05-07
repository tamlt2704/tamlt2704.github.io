# Chapter 10: Finding Routes — Graphs, BFS, and DFS

[← Chapter 9: Binary Search Trees](chapter-09-bst.md) | [Chapter 11: Fastest Route →](chapter-11-dijkstra.md)

---

## The Problem

RouteMaster needs to find paths between addresses. The city is a network: intersections are nodes, roads are edges. "Can I get from the warehouse to 123 Main Street?" and "What's the shortest path?"

The intern's route planner uses a hardcoded lookup table of common routes. Any address not in the table: "Route not found." Marcus drove 15km in circles last Tuesday because the app couldn't find a path to a new housing development.

You need to model the city as a graph and search it.

## Graphs: The Data Structure

A **graph** is a set of **vertices** (nodes) connected by **edges** (links).

```
    A ---3--- B
    |         |
    2         4
    |         |
    C ---1--- D ---5--- E
```

Vertices: A, B, C, D, E
Edges: A-B (weight 3), A-C (weight 2), B-D (weight 4), C-D (weight 1), D-E (weight 5)

### Representation: Adjacency List

```python
class Graph:
    def __init__(self, directed=False):
        self.adjacency = {}  # vertex → [(neighbor, weight), ...]
        self.directed = directed

    def add_vertex(self, vertex):
        if vertex not in self.adjacency:
            self.adjacency[vertex] = []

    def add_edge(self, u, v, weight=1):
        self.add_vertex(u)
        self.add_vertex(v)
        self.adjacency[u].append((v, weight))
        if not self.directed:
            self.adjacency[v].append((u, weight))

    def neighbors(self, vertex):
        return self.adjacency.get(vertex, [])

    def vertices(self):
        return self.adjacency.keys()
```

### RouteMaster's City Graph

```python
city = Graph(directed=True)  # One-way streets exist

# Intersections
city.add_edge("Warehouse", "Main & 1st", weight=5)
city.add_edge("Main & 1st", "Main & 2nd", weight=2)
city.add_edge("Main & 2nd", "Main & 3rd", weight=2)
city.add_edge("Main & 1st", "Oak & 1st", weight=3)
city.add_edge("Oak & 1st", "Oak & 2nd", weight=2)
city.add_edge("Oak & 2nd", "Main & 3rd", weight=4)
city.add_edge("Main & 3rd", "Hospital", weight=1)
# ... 50,000 intersections, 120,000 road segments
```

## BFS: Breadth-First Search

BFS explores the graph level by level — all nodes 1 step away, then 2 steps, then 3. It finds the **shortest path by number of edges** (not by distance/weight).

```python
from collections import deque

def bfs(graph, start, target):
    """
    Find shortest path (fewest edges) from start to target.
    O(V + E) where V = vertices, E = edges.
    """
    queue = deque([(start, [start])])
    visited = {start}

    while queue:
        current, path = queue.popleft()

        if current == target:
            return path

        for neighbor, weight in graph.neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return None  # No path exists
```

### Trace

Finding path from Warehouse to Hospital:

```
Queue: [(Warehouse, [Warehouse])]
Visited: {Warehouse}

Step 1: Process Warehouse
  Neighbors: Main & 1st
  Queue: [(Main & 1st, [Warehouse, Main & 1st])]
  Visited: {Warehouse, Main & 1st}

Step 2: Process Main & 1st
  Neighbors: Main & 2nd, Oak & 1st
  Queue: [(Main & 2nd, [..., Main & 2nd]), (Oak & 1st, [..., Oak & 1st])]

Step 3: Process Main & 2nd
  Neighbors: Main & 3rd
  Queue: [(Oak & 1st, [...]), (Main & 3rd, [..., Main & 3rd])]

Step 4: Process Oak & 1st
  Neighbors: Oak & 2nd
  Queue: [(Main & 3rd, [...]), (Oak & 2nd, [...])]

Step 5: Process Main & 3rd
  Neighbors: Hospital
  Queue: [(Oak & 2nd, [...]), (Hospital, [..., Hospital])]

Step 6: Process Oak & 2nd (or Hospital next — depends on order)
  ...

Step 7: Process Hospital → TARGET FOUND!
  Path: [Warehouse, Main & 1st, Main & 2nd, Main & 3rd, Hospital]
```

BFS guarantees the shortest path in terms of **number of edges** (hops). But it treats all edges equally — a 1km road and a 20km highway both count as "1 hop."

## DFS: Depth-First Search

DFS explores as deep as possible before backtracking. It finds **a** path, not necessarily the shortest.

```python
def dfs(graph, start, target):
    """
    Find a path (not necessarily shortest) from start to target.
    O(V + E).
    """
    stack = [(start, [start])]
    visited = set()

    while stack:
        current, path = stack.pop()

        if current == target:
            return path

        if current in visited:
            continue
        visited.add(current)

        for neighbor, weight in graph.neighbors(current):
            if neighbor not in visited:
                stack.append((neighbor, path + [neighbor]))

    return None
```

### Recursive DFS

```python
def dfs_recursive(graph, start, target, visited=None, path=None):
    if visited is None:
        visited = set()
    if path is None:
        path = []

    visited.add(start)
    path = path + [start]

    if start == target:
        return path

    for neighbor, weight in graph.neighbors(start):
        if neighbor not in visited:
            result = dfs_recursive(graph, neighbor, target, visited, path)
            if result:
                return result

    return None
```

## BFS vs DFS

| Property | BFS | DFS |
|---|---|---|
| Data structure | Queue (FIFO) | Stack (LIFO) |
| Finds shortest path? | Yes (unweighted) | No |
| Memory usage | O(V) — stores entire frontier | O(V) worst, often less |
| Use case | Shortest path, level-order | Cycle detection, topological sort, maze solving |
| Explores | Wide first | Deep first |

## Cycle Detection

Marcus reports: "The app sent me in a loop — Main St → Oak St → Elm St → Main St → Oak St..." One-way streets can create cycles. DFS detects them:

```python
def has_cycle(graph):
    """Detect cycles in a directed graph using DFS."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {v: WHITE for v in graph.vertices()}

    def dfs_visit(v):
        color[v] = GRAY  # Currently being explored
        for neighbor, _ in graph.neighbors(v):
            if color[neighbor] == GRAY:
                return True  # Back edge = cycle!
            if color[neighbor] == WHITE:
                if dfs_visit(neighbor):
                    return True
        color[v] = BLACK  # Fully explored
        return False

    for v in graph.vertices():
        if color[v] == WHITE:
            if dfs_visit(v):
                return True
    return False
```

## Connected Components: "Can We Even Get There?"

Before planning a route, check if the destination is reachable:

```python
def is_reachable(graph, start, target):
    """Can we reach target from start? BFS-based."""
    visited = set()
    queue = deque([start])
    visited.add(start)

    while queue:
        current = queue.popleft()
        if current == target:
            return True
        for neighbor, _ in graph.neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return False

# "Can we deliver to the new housing development?"
if not is_reachable(city, "Warehouse", "New Development"):
    print("No route exists — check for missing road data")
```

## RouteMaster's Route Finder

```python
class RouteFinder:
    def __init__(self, city_graph):
        self.graph = city_graph

    def find_route(self, start, end):
        """Find a route between two intersections."""
        path = bfs(self.graph, start, end)
        if not path:
            return {"error": "No route found", "reachable": False}
        return {
            "path": path,
            "hops": len(path) - 1,
            "intersections": path
        }

    def find_all_within_hops(self, start, max_hops):
        """Find all reachable intersections within N hops (for delivery radius)."""
        visited = {start: 0}
        queue = deque([(start, 0)])

        while queue:
            current, distance = queue.popleft()
            if distance >= max_hops:
                continue
            for neighbor, _ in self.graph.neighbors(current):
                if neighbor not in visited:
                    visited[neighbor] = distance + 1
                    queue.append((neighbor, distance + 1))

        return visited
```

## Complexity

| Algorithm | Time | Space |
|---|---|---|
| BFS | O(V + E) | O(V) |
| DFS | O(V + E) | O(V) |
| Cycle detection | O(V + E) | O(V) |

For RouteMaster's city: V = 50,000 intersections, E = 120,000 roads. BFS: ~170,000 operations. Under 50ms.

## What You Learned

- **Graphs** — vertices + edges, directed/undirected, weighted/unweighted
- **Adjacency list** — efficient representation for sparse graphs
- **BFS** — level-by-level exploration, shortest path (unweighted)
- **DFS** — deep exploration, cycle detection, backtracking
- **Reachability** — can we get from A to B?
- **Connected components** — groups of mutually reachable nodes

Marcus no longer drives in circles. The app finds paths to any address in the city graph.

But BFS finds the path with fewest intersections — not the fastest or shortest by distance. A path through 3 highway intersections (30km) beats a path through 10 residential intersections (5km) in BFS. You need to account for edge weights.

That's Dijkstra's algorithm. Chapter 11.

---

[← Chapter 9: Binary Search Trees](chapter-09-bst.md) | [Chapter 11: Fastest Route →](chapter-11-dijkstra.md)

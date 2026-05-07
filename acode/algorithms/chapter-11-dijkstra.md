# Chapter 11: The Fastest Route — Dijkstra's Algorithm

[← Chapter 10: Graphs, BFS, DFS](chapter-10-graphs-bfs-dfs.md) | [Chapter 12: The Traveling Driver →](chapter-12-greedy.md)

---

## The Problem

BFS found a route from the warehouse to the hospital: Warehouse → Main & 1st → Main & 2nd → Main & 3rd → Hospital. Four hops. But the total distance is 5 + 2 + 2 + 1 = 10km.

There's another route: Warehouse → Highway Ramp → Hospital Exit → Hospital. Three hops, but 3 + 15 + 2 = 20km. BFS would prefer the highway route (fewer hops) even though it's twice as far.

Marcus: "Your app sent me on the highway for a delivery 2km away. I drove 20km."

You need shortest path by **weight** (distance, time, or cost), not by hop count.

## Dijkstra's Algorithm

Dijkstra's finds the shortest weighted path from a source to all other vertices. It works by greedily expanding the closest unvisited vertex.

The intuition: imagine pouring water from the source. It flows outward at constant speed along all edges simultaneously. The first time water reaches a vertex, that's the shortest path to it.

```python
import heapq

def dijkstra(graph, start):
    """
    Find shortest paths from start to all reachable vertices.
    Returns: {vertex: (distance, path)}
    O((V + E) log V) with a binary heap.
    """
    distances = {start: 0}
    previous = {start: None}
    priority_queue = [(0, start)]  # (distance, vertex)
    visited = set()

    while priority_queue:
        current_dist, current = heapq.heappop(priority_queue)

        if current in visited:
            continue
        visited.add(current)

        for neighbor, weight in graph.neighbors(current):
            if neighbor in visited:
                continue

            new_dist = current_dist + weight
            if new_dist < distances.get(neighbor, float('inf')):
                distances[neighbor] = new_dist
                previous[neighbor] = current
                heapq.heappush(priority_queue, (new_dist, neighbor))

    return distances, previous

def shortest_path(graph, start, end):
    """Find the shortest weighted path between two vertices."""
    distances, previous = dijkstra(graph, start)

    if end not in distances:
        return None, float('inf')

    # Reconstruct path
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse()

    return path, distances[end]
```

### Trace

```
Graph:
  Warehouse --5-- Main & 1st --2-- Main & 2nd --2-- Main & 3rd --1-- Hospital
  Warehouse --3-- Highway Ramp --15-- Hospital Exit --2-- Hospital

Start: Warehouse, Target: Hospital

Priority Queue: [(0, Warehouse)]
Distances: {Warehouse: 0}

Step 1: Pop (0, Warehouse)
  Visit Warehouse
  Neighbors: Main & 1st (5), Highway Ramp (3)
  Update: Main & 1st = 5, Highway Ramp = 3
  PQ: [(3, Highway Ramp), (5, Main & 1st)]

Step 2: Pop (3, Highway Ramp)
  Visit Highway Ramp
  Neighbors: Hospital Exit (15)
  Update: Hospital Exit = 3 + 15 = 18
  PQ: [(5, Main & 1st), (18, Hospital Exit)]

Step 3: Pop (5, Main & 1st)
  Visit Main & 1st
  Neighbors: Main & 2nd (2)
  Update: Main & 2nd = 5 + 2 = 7
  PQ: [(7, Main & 2nd), (18, Hospital Exit)]

Step 4: Pop (7, Main & 2nd)
  Visit Main & 2nd
  Neighbors: Main & 3rd (2)
  Update: Main & 3rd = 7 + 2 = 9
  PQ: [(9, Main & 3rd), (18, Hospital Exit)]

Step 5: Pop (9, Main & 3rd)
  Visit Main & 3rd
  Neighbors: Hospital (1)
  Update: Hospital = 9 + 1 = 10
  PQ: [(10, Hospital), (18, Hospital Exit)]

Step 6: Pop (10, Hospital)
  Visit Hospital → TARGET REACHED!
  Shortest distance: 10
  Path: Warehouse → Main & 1st → Main & 2nd → Main & 3rd → Hospital
```

The local streets (10km) beat the highway (20km). Dijkstra found the optimal route.

## Why It Works: The Greedy Choice

Dijkstra always processes the vertex with the smallest known distance. Once a vertex is visited, its distance is final — no shorter path can exist (because all remaining paths go through vertices with equal or greater distance).

**Critical requirement:** all edge weights must be non-negative. If a negative edge exists, a "longer" path through it could actually be shorter, breaking the greedy assumption.

## Complexity

| Implementation | Time |
|---|---|
| Array (scan for minimum) | O(V²) |
| Binary heap (heapq) | O((V + E) log V) |
| Fibonacci heap | O(V log V + E) |

For RouteMaster's city (V=50,000, E=120,000):
- Array: 2.5 billion operations (too slow)
- Binary heap: ~170,000 × 17 ≈ 2.9 million operations (fast)

## RouteMaster's Route Planner

```python
class RoutePlanner:
    def __init__(self, city_graph):
        self.graph = city_graph

    def plan_route(self, start, end, metric="distance"):
        """
        Find optimal route.
        metric: "distance" (km), "time" (minutes), "cost" (fuel)
        """
        # Use different edge weights based on metric
        path, total = shortest_path(self.graph, start, end)
        if path is None:
            return {"error": "No route found"}

        return {
            "path": path,
            "total_distance": total,
            "segments": len(path) - 1,
            "estimated_time": total / 30 * 60  # Assume 30km/h average
        }

    def plan_route_avoiding(self, start, end, avoid_vertices):
        """Route that avoids certain intersections (road closures)."""
        # Create a filtered graph
        filtered = Graph(directed=self.graph.directed)
        for v in self.graph.vertices():
            if v in avoid_vertices:
                continue
            for neighbor, weight in self.graph.neighbors(v):
                if neighbor not in avoid_vertices:
                    filtered.add_edge(v, neighbor, weight)

        return shortest_path(filtered, start, end)
```

## A* Search: Dijkstra with a Hint

Dijkstra explores in all directions equally. If you know the target's location, you can guide the search toward it using a **heuristic** (estimated distance to target).

```python
def a_star(graph, start, end, heuristic):
    """
    A* search — Dijkstra guided by a heuristic.
    heuristic(vertex) → estimated distance from vertex to end.
    O((V + E) log V) but explores fewer vertices in practice.
    """
    g_score = {start: 0}  # Actual distance from start
    f_score = {start: heuristic(start)}  # g + estimated remaining
    previous = {start: None}
    open_set = [(f_score[start], start)]
    closed_set = set()

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == end:
            # Reconstruct path
            path = []
            while current:
                path.append(current)
                current = previous[current]
            return path[::-1], g_score[end]

        if current in closed_set:
            continue
        closed_set.add(current)

        for neighbor, weight in graph.neighbors(current):
            if neighbor in closed_set:
                continue

            tentative_g = g_score[current] + weight
            if tentative_g < g_score.get(neighbor, float('inf')):
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor)
                previous[neighbor] = current
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return None, float('inf')
```

### Heuristic: Straight-Line Distance

```python
import math

# Each intersection has coordinates
coordinates = {
    "Warehouse": (0, 0),
    "Main & 1st": (3, 4),
    "Hospital": (8, 6),
    # ...
}

def euclidean_heuristic(vertex):
    """Straight-line distance to target (never overestimates)."""
    x1, y1 = coordinates[vertex]
    x2, y2 = coordinates["Hospital"]  # Target
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
```

A* with a good heuristic explores 60-80% fewer vertices than Dijkstra while finding the same optimal path. It's what Google Maps uses (with more sophisticated heuristics).

## Dijkstra vs BFS vs A*

| Algorithm | Edge weights | Optimal? | Speed |
|---|---|---|---|
| BFS | Unweighted only | Yes (hop count) | O(V + E) |
| Dijkstra | Non-negative | Yes (weighted) | O((V+E) log V) |
| A* | Non-negative | Yes (with admissible heuristic) | Faster than Dijkstra in practice |
| Bellman-Ford | Any (including negative) | Yes | O(V × E) — slower |

## What You Learned

- **Dijkstra's algorithm** — greedy shortest path for weighted graphs
- **Priority queue** — always process the closest unvisited vertex
- **Non-negative weights** — required for correctness
- **Path reconstruction** — track predecessors, walk backward
- **A* search** — Dijkstra + heuristic for faster targeted search
- **Practical routing** — avoid vertices, multiple metrics

Marcus gets optimal routes. The hospital delivery goes through local streets (10km) instead of the highway (20km). Fuel costs drop 15%.

But Priya has a harder problem: "Marcus has 20 deliveries today. What ORDER should he visit them in to minimize total driving distance?" That's not finding one shortest path — it's finding the best sequence of 20 stops. The Traveling Salesman Problem.

That's Chapter 12.

---

[← Chapter 10: Graphs, BFS, DFS](chapter-10-graphs-bfs-dfs.md) | [Chapter 12: The Traveling Driver →](chapter-12-greedy.md)

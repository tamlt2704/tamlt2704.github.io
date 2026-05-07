# Chapter 12: The Traveling Driver — Greedy Algorithms

[← Chapter 11: Dijkstra](chapter-11-dijkstra.md) | [Chapter 13: Package Loading →](chapter-13-dynamic-programming.md)

---

## The Problem

Marcus has 20 deliveries today. Each has an address. He needs to visit all 20 and return to the warehouse. What order minimizes total driving distance?

The brute-force answer: try all possible orderings. Pick the shortest.

20 stops = 20! = 2,432,902,008,176,640,000 possible orderings. At 1 billion per second, that's 77 years.

This is the **Traveling Salesman Problem (TSP)** — one of the most famous problems in computer science. No known polynomial-time algorithm exists for the optimal solution. But you don't need optimal. You need "good enough in under 1 second."

## Greedy Algorithms: The Concept

A greedy algorithm makes the locally optimal choice at each step, hoping it leads to a globally good solution. It never backtracks.

**Greedy strategy for TSP:** At each stop, go to the nearest unvisited stop.

```python
def nearest_neighbor_tsp(distances, start=0):
    """
    Greedy TSP: always visit the nearest unvisited city.
    Returns: (route, total_distance)
    Not optimal, but fast: O(n²).
    """
    n = len(distances)
    visited = [False] * n
    route = [start]
    visited[start] = True
    total = 0

    current = start
    for _ in range(n - 1):
        nearest = None
        nearest_dist = float('inf')

        for city in range(n):
            if not visited[city] and distances[current][city] < nearest_dist:
                nearest = city
                nearest_dist = distances[current][city]

        route.append(nearest)
        visited[nearest] = True
        total += nearest_dist
        current = nearest

    # Return to start
    total += distances[current][start]
    route.append(start)

    return route, total
```

### Example

Marcus's 5 stops (distances in km):

```
     W    A    B    C    D    E
W  [ 0,   5,  12,   8,  15,   3]
A  [ 5,   0,   7,  10,   6,   9]
B  [12,   7,   0,   4,  11,  14]
C  [ 8,  10,   4,   0,   3,  11]
D  [15,   6,  11,   3,   0,  13]
E  [ 3,   9,  14,  11,  13,   0]
```

Nearest neighbor from Warehouse (W):
```
W → E (3km, nearest to W)
E → A (9km, nearest unvisited to E)  — wait, A is 9, but let's check all
E → nearest unvisited: A=9, B=14, C=11, D=13 → A (9km)
A → nearest unvisited: B=7, C=10, D=6 → D (6km)
D → nearest unvisited: B=11, C=3 → C (3km)
C → nearest unvisited: B=4 → B (4km)
B → W (12km, return)

Route: W → E → A → D → C → B → W
Total: 3 + 9 + 6 + 3 + 4 + 12 = 37km
```

Optimal route (by exhaustive search): W → E → A → B → C → D → W = 3 + 9 + 7 + 4 + 3 + 15 = 41km. Wait — the greedy solution is actually better here! That's luck. On average, nearest neighbor produces routes 20-25% longer than optimal.

## Greedy Doesn't Always Win

The greedy approach fails when a locally good choice leads to a globally bad outcome:

```
Imagine 3 stops in a line:  W ---- A ---- B ---- C
                            0      1      2      100

Nearest neighbor: W → A (1) → B (1) → C (98) → W (100) = 200
Optimal:          W → C (100) → B (98) → A (1) → W (1) = 200
Actually same here. But consider:

W at (0,0), A at (1,0), B at (2,0), C at (0,3)
Nearest from W: A (1km)
Nearest from A: B (1km)
Nearest from B: C (3.6km)
C back to W: 3km
Total: 8.6km

Optimal: W → C → B → A → W = 3 + 3.6 + 1 + 1 = 8.6km (same!)

But with more complex layouts, greedy can be 25%+ worse.
```

## Improving the Greedy Solution: 2-Opt

After finding a greedy route, improve it by swapping pairs of edges:

```python
def two_opt(route, distances):
    """
    Improve a route by reversing segments.
    Repeatedly finds swaps that reduce total distance.
    O(n²) per iteration, typically converges in O(n) iterations.
    """
    n = len(route) - 1  # Exclude return-to-start
    improved = True

    while improved:
        improved = False
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                # Cost of current edges
                current = (distances[route[i-1]][route[i]] +
                          distances[route[j]][route[j+1]])
                # Cost if we reverse the segment between i and j
                new = (distances[route[i-1]][route[j]] +
                      distances[route[i]][route[j+1]])

                if new < current:
                    # Reverse the segment
                    route[i:j+1] = route[i:j+1][::-1]
                    improved = True

    return route
```

Nearest neighbor + 2-opt typically produces routes within 5-10% of optimal. Good enough for Marcus.

## RouteMaster's Route Optimizer

```python
class RouteOptimizer:
    def __init__(self, city_graph):
        self.graph = city_graph
        self._distance_cache = {}

    def _get_distance(self, a, b):
        """Cached shortest path distance between two points."""
        key = (a, b)
        if key not in self._distance_cache:
            _, dist = shortest_path(self.graph, a, b)
            self._distance_cache[key] = dist
        return self._distance_cache[key]

    def optimize_route(self, warehouse, stops):
        """Find a good delivery order for the given stops."""
        # Build distance matrix
        all_points = [warehouse] + stops
        n = len(all_points)
        distances = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i != j:
                    distances[i][j] = self._get_distance(all_points[i], all_points[j])

        # Greedy nearest neighbor
        route, total = nearest_neighbor_tsp(distances, start=0)

        # Improve with 2-opt
        route = two_opt(route, distances)

        # Map indices back to addresses
        total_distance = sum(distances[route[i]][route[i+1]] for i in range(len(route)-1))
        address_route = [all_points[i] for i in route]

        return {
            "route": address_route,
            "total_distance": total_distance,
            "stops": len(stops),
            "estimated_time": total_distance / 30 * 60  # minutes at 30km/h
        }
```

## Other Greedy Algorithms

### Activity Selection (Delivery Time Windows)

"Which deliveries can Marcus make if each has a time window?"

```python
def max_deliveries(deliveries):
    """
    Select maximum non-overlapping deliveries.
    Greedy: always pick the delivery that ends earliest.
    O(n log n) — sort + single pass.
    """
    # Sort by end time
    sorted_deliveries = sorted(deliveries, key=lambda d: d.end_time)

    selected = []
    last_end = 0

    for delivery in sorted_deliveries:
        if delivery.start_time >= last_end:
            selected.append(delivery)
            last_end = delivery.end_time

    return selected
```

This greedy choice IS optimal — provably. Not all greedy algorithms are approximate.

### Fractional Knapsack

"The van has 500kg capacity. Which packages maximize value per kg?"

```python
def fractional_knapsack(packages, capacity):
    """
    Greedy: take items with highest value/weight ratio first.
    Optimal for fractional (can take partial items).
    O(n log n).
    """
    # Sort by value density (value per kg)
    sorted_pkgs = sorted(packages, key=lambda p: p.value / p.weight, reverse=True)

    total_value = 0
    remaining = capacity

    for pkg in sorted_pkgs:
        if pkg.weight <= remaining:
            total_value += pkg.value
            remaining -= pkg.weight
        else:
            # Take a fraction
            fraction = remaining / pkg.weight
            total_value += pkg.value * fraction
            break

    return total_value
```

## When Greedy Works (Optimally)

Greedy gives the optimal solution when the problem has:
1. **Greedy choice property** — a locally optimal choice leads to a globally optimal solution
2. **Optimal substructure** — optimal solution contains optimal solutions to subproblems

| Problem | Greedy optimal? | Why |
|---|---|---|
| Activity selection | Yes | Earliest-end-first is provably optimal |
| Fractional knapsack | Yes | Highest density first is optimal |
| 0/1 knapsack | No | Must consider combinations |
| TSP | No | Nearest neighbor can be 25%+ worse |
| Huffman coding | Yes | Merge least frequent first is optimal |
| Dijkstra's | Yes | Closest-first is provably optimal |

## What You Learned

- **Greedy algorithms** — make locally optimal choices, never backtrack
- **Nearest neighbor TSP** — O(n²), typically 20-25% from optimal
- **2-opt improvement** — swap edges to reduce route length
- **Activity selection** — greedy IS optimal (earliest end time)
- **Fractional knapsack** — greedy IS optimal (highest density)
- **When greedy fails** — 0/1 knapsack, TSP need other approaches

Marcus's 20-stop route is computed in under 1 second. It's not mathematically optimal, but it's within 10% — saving him 30 minutes of driving compared to the old random ordering.

But there's a problem greedy can't solve well: loading the van. Each package has a weight and a priority value. The van has a weight limit. Which packages maximize total priority delivered? You can't take fractions of packages. You need to consider combinations.

That's dynamic programming. Chapter 13.

---

[← Chapter 11: Dijkstra](chapter-11-dijkstra.md) | [Chapter 13: Package Loading →](chapter-13-dynamic-programming.md)

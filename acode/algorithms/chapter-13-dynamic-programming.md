# Chapter 13: Package Loading — Dynamic Programming

[← Chapter 12: Greedy Algorithms](chapter-12-greedy.md) | [Chapter 14: Delivery Zones →](chapter-14-backtracking.md)

---

## The Problem

Marcus's van holds 500kg. He has 30 packages to deliver, each with a weight and a priority score. He can't take all of them — total weight exceeds capacity. Which subset maximizes total priority while staying under 500kg?

The greedy approach (highest priority-per-kg first) doesn't work for whole packages. Taking a 200kg high-value package might prevent you from taking three 100kg packages that together are worth more.

You need to consider combinations. But 2³⁰ = 1 billion subsets. Brute force is out.

## The Knapsack Problem

Given:
- Items with weights and values
- A capacity limit
- Choose items to maximize total value without exceeding capacity

This is the **0/1 Knapsack Problem** — each item is either taken (1) or left (0). No fractions.

## The Key Insight: Overlapping Subproblems

Consider: "What's the best value achievable with items 1..n and capacity W?"

This breaks into: "Take item n (value + best of items 1..n-1 with capacity W - weight_n)" vs "Skip item n (best of items 1..n-1 with capacity W)."

Both sub-choices ask about "best of items 1..n-1" — the same subproblem appears multiple times. Instead of recomputing, **store the result**.

That's dynamic programming: solve subproblems once, store results, build up to the full solution.

## Recursive Solution (Slow)

```python
def knapsack_recursive(weights, values, capacity, n):
    """
    Brute force with recursion. O(2^n) — exponential.
    """
    if n == 0 or capacity == 0:
        return 0

    # If current item is too heavy, skip it
    if weights[n-1] > capacity:
        return knapsack_recursive(weights, values, capacity, n-1)

    # Max of: take it vs skip it
    take = values[n-1] + knapsack_recursive(weights, values, capacity - weights[n-1], n-1)
    skip = knapsack_recursive(weights, values, capacity, n-1)

    return max(take, skip)
```

For 30 items: 2³⁰ ≈ 1 billion calls. Way too slow.

## Memoization (Top-Down DP)

Same recursion, but cache results:

```python
def knapsack_memo(weights, values, capacity, n, memo=None):
    """
    Top-down DP with memoization. O(n × capacity).
    """
    if memo is None:
        memo = {}

    if n == 0 or capacity == 0:
        return 0

    key = (n, capacity)
    if key in memo:
        return memo[key]

    if weights[n-1] > capacity:
        result = knapsack_memo(weights, values, capacity, n-1, memo)
    else:
        take = values[n-1] + knapsack_memo(weights, values, capacity - weights[n-1], n-1, memo)
        skip = knapsack_memo(weights, values, capacity, n-1, memo)
        result = max(take, skip)

    memo[key] = result
    return result
```

For 30 items, capacity 500: at most 30 × 500 = 15,000 subproblems. Each solved once. Instant.

## Tabulation (Bottom-Up DP)

Build a table from small subproblems to large:

```python
def knapsack_dp(weights, values, capacity):
    """
    Bottom-up DP. O(n × capacity) time and space.
    """
    n = len(weights)
    # dp[i][w] = max value using items 0..i-1 with capacity w
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(capacity + 1):
            # Option 1: skip item i
            dp[i][w] = dp[i-1][w]

            # Option 2: take item i (if it fits)
            if weights[i-1] <= w:
                take = values[i-1] + dp[i-1][w - weights[i-1]]
                dp[i][w] = max(dp[i][w], take)

    return dp[n][capacity]
```

### Trace

Items: [(weight=2, value=3), (weight=3, value=4), (weight=4, value=5)], capacity=5

```
dp table (rows = items considered, cols = capacity):

     w=0  w=1  w=2  w=3  w=4  w=5
i=0:  0    0    0    0    0    0     (no items)
i=1:  0    0    3    3    3    3     (item 1: w=2, v=3)
i=2:  0    0    3    4    4    7     (items 1-2: w=3, v=4)
i=3:  0    0    3    4    5    7     (items 1-3: w=4, v=5)

Answer: dp[3][5] = 7 (take items 1 and 2: weight=5, value=7)
```

### Reconstructing the Solution

Which items did we take?

```python
def knapsack_with_items(weights, values, capacity):
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(capacity + 1):
            dp[i][w] = dp[i-1][w]
            if weights[i-1] <= w:
                dp[i][w] = max(dp[i][w], values[i-1] + dp[i-1][w - weights[i-1]])

    # Backtrack to find which items were selected
    selected = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            selected.append(i - 1)  # Item i was taken
            w -= weights[i - 1]

    return dp[n][capacity], selected
```

## RouteMaster's Van Loading

```python
class VanLoader:
    def __init__(self, capacity_kg):
        self.capacity = capacity_kg

    def optimize_load(self, packages):
        """Select packages that maximize priority within weight limit."""
        weights = [int(p.weight) for p in packages]  # Must be integers for DP
        values = [p.priority_score for p in packages]

        max_value, selected_indices = knapsack_with_items(weights, values, self.capacity)

        selected_packages = [packages[i] for i in selected_indices]
        total_weight = sum(packages[i].weight for i in selected_indices)

        return {
            "packages": selected_packages,
            "total_priority": max_value,
            "total_weight": total_weight,
            "capacity_used": f"{total_weight}/{self.capacity}kg",
            "packages_loaded": len(selected_packages),
            "packages_left": len(packages) - len(selected_packages)
        }
```

```python
loader = VanLoader(capacity_kg=500)
result = loader.optimize_load(today_packages)
# {
#   "total_priority": 847,
#   "total_weight": 493,
#   "capacity_used": "493/500kg",
#   "packages_loaded": 22,
#   "packages_left": 8
# }
```

## Other DP Problems at RouteMaster

### Minimum Delivery Cost (Coin Change Variant)

"What's the minimum number of vans needed to deliver all packages?"

```python
def min_vans(package_weights, van_capacity):
    """
    Bin packing approximation using DP.
    (True bin packing is NP-hard; this is a simplified version)
    """
    # First-fit decreasing heuristic
    sorted_weights = sorted(package_weights, reverse=True)
    vans = []  # Each van's remaining capacity

    for weight in sorted_weights:
        placed = False
        for i, remaining in enumerate(vans):
            if remaining >= weight:
                vans[i] -= weight
                placed = True
                break
        if not placed:
            vans.append(van_capacity - weight)

    return len(vans)
```

### Longest Increasing Subsequence (Route Efficiency)

"What's the longest sequence of deliveries where each is further from the warehouse than the last?" (Useful for one-way routes)

```python
def longest_increasing_subsequence(distances):
    """O(n²) DP for LIS."""
    n = len(distances)
    dp = [1] * n  # dp[i] = length of LIS ending at i

    for i in range(1, n):
        for j in range(i):
            if distances[j] < distances[i]:
                dp[i] = max(dp[i], dp[j] + 1)

    return max(dp)
```

## When to Use Dynamic Programming

DP works when a problem has:
1. **Optimal substructure** — optimal solution built from optimal sub-solutions
2. **Overlapping subproblems** — same subproblems solved repeatedly

| Signal | Likely DP |
|---|---|
| "Find the minimum/maximum..." | Yes |
| "Count the number of ways..." | Yes |
| "Is it possible to..." | Yes |
| "Find the longest/shortest..." | Yes |
| Choices at each step affect future options | Yes |
| Can define state as (index, remaining_capacity) | Yes |

## DP vs Greedy

| Aspect | Greedy | Dynamic Programming |
|---|---|---|
| Approach | Local best choice | Consider all sub-choices |
| Backtracking | Never | Implicit (via table) |
| Optimality | Sometimes | Always (for DP-solvable problems) |
| Speed | Usually O(n log n) | Usually O(n × state_space) |
| When to use | Greedy choice property holds | Overlapping subproblems exist |

## What You Learned

- **Dynamic programming** — solve subproblems once, store results, build up
- **Memoization** — top-down (recursive + cache)
- **Tabulation** — bottom-up (iterative table filling)
- **0/1 Knapsack** — select items to maximize value within capacity
- **Solution reconstruction** — backtrack through the DP table
- **Recognizing DP** — optimal substructure + overlapping subproblems

Marcus's van is loaded optimally. 22 packages, 493/500kg, maximum priority score. The 8 packages left behind are the lowest priority — they'll go on the next run.

But there's one more class of problems: "assign drivers to delivery zones such that every zone is covered and no driver is overloaded." This requires exploring combinations systematically — trying assignments, checking constraints, and backtracking when stuck.

That's Chapter 14.

---

[← Chapter 12: Greedy Algorithms](chapter-12-greedy.md) | [Chapter 14: Delivery Zones →](chapter-14-backtracking.md)

# Chapter 15: Staying Fast — Amortized Analysis and System Design

[← Chapter 14: Backtracking](chapter-14-backtracking.md)

---

## The Problem

RouteMaster doubles every 6 months. 100K packages today. 200K in June. 400K by December. CEO Lena's Q4 target: 1 million packages per day.

Priya: "Which of our algorithms will break first? Where do we invest engineering time?"

You need to think about scaling — not just "what's the Big-O?" but "what's the actual cost as we grow, and when do we need to rebuild?"

## Amortized Analysis: The Real Cost

Some operations are expensive occasionally but cheap most of the time. Amortized analysis gives the average cost per operation over a sequence.

### Example: Dynamic Array (Python's list.append)

```python
# Python's list doubles its capacity when full
items = []
for i in range(1_000_000):
    items.append(i)  # Usually O(1), occasionally O(n) when resizing
```

Most appends: O(1) — just write to the next slot.
Occasional append: O(n) — allocate new array, copy everything.

But the expensive copies happen at sizes 1, 2, 4, 8, 16, ... n. Total copy cost: 1 + 2 + 4 + ... + n = 2n. Spread over n operations: **O(1) amortized**.

### The Accounting Method

Think of it like a bank account. Each O(1) append "deposits" a small extra cost. When the expensive O(n) resize happens, the accumulated deposits "pay" for it.

```
Operation 1: append (cost 1) + deposit 1 = pay 2
Operation 2: append (cost 1) + deposit 1 = pay 2
Operation 3: append (cost 1) + deposit 1 = pay 2
Operation 4: RESIZE (cost 4) — paid by 4 deposits from operations 1-4
Operation 5: append (cost 1) + deposit 1 = pay 2
...
```

Each operation pays O(1). The expensive operations are pre-funded.

## RouteMaster's Scaling Analysis

### Package Registry (Hash Table)

Current: 100K packages, load factor 0.6.
At 200K: load factor 1.2 → resize triggered → O(n) rehash.

```python
# Resize happens at 70% load factor
# Current capacity: 150K slots
# At 100K packages: load = 0.67 (fine)
# At 105K packages: load = 0.70 → RESIZE to 300K slots
# Cost: rehash 105K entries (one-time, ~50ms)
# Then fine until 210K packages
```

Amortized cost per insert: O(1). The occasional resize is expensive but rare. At RouteMaster's growth rate, resizes happen every 3-4 months. Acceptable.

**Verdict: No action needed.** Hash table scaling is self-managing.

### Sorted Package Array (for Binary Search)

Current: sorted array of 100K packages. Insertions require shifting.

```python
# Insert into sorted array: O(n) — shift everything after insertion point
# 100K packages, 1000 new packages/hour
# Cost: 1000 × 100K shifts/hour = 100M operations/hour

# At 400K packages:
# Cost: 1000 × 400K = 400M operations/hour — getting slow
```

**Verdict: Replace with a balanced BST or skip list at 200K.** Insertions become O(log n) instead of O(n).

### Priority Queue (Heap)

Current: binary heap with 50K active packages.

```python
# Push: O(log 50K) = O(16) — fine
# Pop: O(log 50K) = O(16) — fine
# At 1M packages: O(log 1M) = O(20) — still fine
```

**Verdict: No action needed.** Heaps scale gracefully. log(1M) = 20 operations. Negligible.

### Route Planner (Dijkstra)

Current: 50K intersections, 120K edges. Dijkstra: O((V+E) log V) ≈ 2.9M operations.

```python
# At 200K intersections (city expansion):
# O((200K + 480K) × 18) ≈ 12M operations
# Still under 100ms

# At 1M intersections (national scale):
# O((1M + 2.4M) × 20) ≈ 68M operations
# ~500ms — getting slow for real-time routing
```

**Verdict: Switch to A* with landmarks at 500K intersections.** Pre-compute distances from ~20 landmark nodes. Use as heuristic. 10x fewer nodes explored.

### Morning Sort (Quicksort)

Current: 50K packages sorted in 0.14s.

```python
# At 200K: O(200K × log 200K) = O(200K × 18) ≈ 3.6M operations → ~0.5s
# At 1M: O(1M × 20) = 20M operations → ~3s
```

**Verdict: Fine until 500K.** At 1M, consider:
- Partial sorting (only sort today's deliveries, not the full history)
- Incremental sorting (maintain sorted order as packages arrive)
- Parallel sort (split across cores)

## Rebuild vs Patch: The Decision Framework

| Situation | Patch | Rebuild |
|---|---|---|
| Occasional slowness (amortized O(1)) | ✓ | |
| Linear degradation with growth | | ✓ |
| One-time migration cost < 1 week | | ✓ |
| Current solution works for 6+ months | ✓ | |
| Complexity class changes (O(n) → O(log n)) | | ✓ |
| Only affects batch jobs (not real-time) | ✓ | |

## Lazy vs Eager: When to Defer Work

### Lazy Deletion

Instead of removing items from a sorted array (O(n) shift), mark them as deleted:

```python
class LazyPackageRegistry:
    def __init__(self):
        self.packages = []  # Sorted
        self.deleted = set()  # Tracking numbers marked for deletion
        self.delete_count = 0

    def delete(self, tracking):
        """O(1) — just mark it."""
        self.deleted.add(tracking)
        self.delete_count += 1

        # Rebuild when 30% of entries are deleted (amortized)
        if self.delete_count > len(self.packages) * 0.3:
            self._compact()

    def _compact(self):
        """O(n) — but happens rarely."""
        self.packages = [p for p in self.packages if p.tracking not in self.deleted]
        self.deleted.clear()
        self.delete_count = 0

    def search(self, tracking):
        """Binary search, skip deleted entries."""
        idx = binary_search(self.packages, tracking)
        if idx != -1 and tracking not in self.deleted:
            return self.packages[idx]
        return None
```

Amortized delete: O(1). The compaction is O(n) but happens every n/3 deletes.

### Lazy Index Rebuilding

The sorted index doesn't need to be perfectly up-to-date for every query:

```python
class BatchedIndex:
    def __init__(self):
        self.sorted_packages = []
        self.pending_inserts = []  # Buffer of unsorted new packages
        self.BUFFER_THRESHOLD = 1000

    def insert(self, package):
        """O(1) — buffer it."""
        self.pending_inserts.append(package)
        if len(self.pending_inserts) >= self.BUFFER_THRESHOLD:
            self._merge_pending()

    def _merge_pending(self):
        """O(n + k log k) — sort buffer, merge with main list."""
        self.pending_inserts.sort(key=lambda p: p.tracking)
        self.sorted_packages = merge(self.sorted_packages, self.pending_inserts)
        self.pending_inserts = []

    def search(self, tracking):
        """Check buffer (linear) then main index (binary)."""
        # Check small buffer first — O(k) where k < 1000
        for p in self.pending_inserts:
            if p.tracking == tracking:
                return p
        # Then binary search the main index — O(log n)
        return binary_search_packages(self.sorted_packages, tracking)
```

Amortized insert: O(1). Search: O(k + log n) where k is small. Rebuild happens every 1000 inserts.

## The Scaling Playbook

| Scale | Strategy |
|---|---|
| < 10K items | Anything works. Don't optimize. |
| 10K - 100K | Choose the right algorithm. O(n²) starts hurting. |
| 100K - 1M | Choose the right data structure. Amortized costs matter. |
| 1M - 10M | Partition data. Parallel processing. Caching layers. |
| > 10M | Distributed systems. Sharding. Approximate algorithms. |

## RouteMaster's 12-Month Plan

| Month | Scale | Action |
|---|---|---|
| Now | 100K/day | Current algorithms are fine |
| +3 | 200K/day | Replace sorted array with BST for package index |
| +6 | 400K/day | Add A* with landmarks for routing |
| +9 | 700K/day | Parallel morning sort, batched index updates |
| +12 | 1M/day | Shard by zone, distributed priority queues |

## What You Learned

- **Amortized analysis** — average cost over many operations (not worst case)
- **Dynamic arrays** — O(1) amortized append despite O(n) resizes
- **Scaling analysis** — predict when algorithms break at future scale
- **Rebuild vs patch** — when to change complexity class vs optimize constants
- **Lazy operations** — defer expensive work, batch it, amortize the cost
- **The scaling playbook** — different strategies for different magnitudes

## The Complete Algorithm Toolkit

| Problem | Algorithm | Complexity | Chapter |
|---|---|---|---|
| Find one item | Linear search | O(n) | 1 |
| Find in sorted data | Binary search | O(log n) | 2 |
| Sort (simple) | Insertion sort | O(n²) / O(n) best | 3 |
| Sort (fast) | Merge sort | O(n log n) | 4 |
| Sort (in-place) | Quicksort | O(n log n) avg | 5 |
| Find min/max dynamically | Heap / Priority queue | O(log n) | 6 |
| Exact lookup | Hash table | O(1) avg | 7 |
| Prefix matching | Trie | O(m) | 8 |
| Ordered operations | BST / AVL tree | O(log n) | 9 |
| Shortest path (unweighted) | BFS | O(V + E) | 10 |
| Shortest path (weighted) | Dijkstra / A* | O((V+E) log V) | 11 |
| Optimization (approximate) | Greedy | O(n log n) | 12 |
| Optimization (exact) | Dynamic programming | O(n × state) | 13 |
| Constraint satisfaction | Backtracking | Exponential (pruned) | 14 |
| Scaling decisions | Amortized analysis | — | 15 |

Every algorithm was introduced because something was too slow, too wrong, or about to break. The problems came first. The solutions followed.

RouteMaster delivers 1 million packages a day. Routes are optimal. Lookups are instant. The priority queue never drops an urgent delivery. Marcus hasn't driven through a lake in months.

Now go build something fast.

---

[← Chapter 14: Backtracking](chapter-14-backtracking.md)

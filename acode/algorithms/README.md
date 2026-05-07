# Algorithms — From Linear Search to Production Systems

A narrative-driven algorithms and data structures course. You're a software engineer at RouteMaster, a logistics startup drowning in brute-force code. Over 15 chapters, you'll rebuild every system — one disaster at a time.

## Episodes

| # | Title | The Problem | What You Learn |
|---|---|---|---|
| 00 | [Before You Start](chapter-00-overview.md) | — | Setup, Big-O intuition, the cast |
| 01 | [Finding a Package](chapter-01-linear-search.md) | 100K lookups are slow | Linear search, O(n), when it's fine |
| 02 | [The Sorted Shortcut](chapter-02-binary-search.md) | 50K lookups × 100K packages | Binary search, O(log n), sorted invariants |
| 03 | [Sorting by Deadline](chapter-03-basic-sorting.md) | Drivers pick up packages in wrong order | Selection sort, insertion sort, O(n²) wall |
| 04 | [Morning Dispatch](chapter-04-merge-sort.md) | 50K packages need sorting in < 1s | Merge sort, divide and conquer, O(n log n) |
| 05 | [Sorting In-Place](chapter-05-quicksort.md) | Merge sort uses too much memory | Quicksort, partitioning, pivot selection |
| 06 | [What's Most Urgent?](chapter-06-heaps.md) | Need dynamic "find minimum" | Heaps, priority queues, heapsort |
| 07 | [Instant Lookup](chapter-07-hash-tables.md) | Lookup by any field must be O(1) | Hash tables, collisions, load factor |
| 08 | [Autocomplete](chapter-08-tries.md) | Address prefix matching | Tries, prefix trees |
| 09 | [Ordered Data](chapter-09-bst.md) | Range queries on deadlines | BSTs, AVL trees, balancing |
| 10 | [Finding Routes](chapter-10-graphs-bfs-dfs.md) | "Can we get there?" | Graphs, BFS, DFS, cycle detection |
| 11 | [Fastest Route](chapter-11-dijkstra.md) | Shortest path by distance, not hops | Dijkstra, A*, weighted graphs |
| 12 | [The Traveling Driver](chapter-12-greedy.md) | Optimal order for 20 stops | Greedy algorithms, TSP, 2-opt |
| 13 | [Package Loading](chapter-13-dynamic-programming.md) | Maximize priority within weight limit | Dynamic programming, knapsack |
| 14 | [Delivery Zones](chapter-14-backtracking.md) | Assign drivers to zones with constraints | Recursion, backtracking, pruning |
| 15 | [Staying Fast](chapter-15-amortized.md) | System doubles every 6 months | Amortized analysis, scaling decisions |

## Prerequisites

- Python 3.10+
- No external libraries (we build everything from scratch)

## Philosophy

Every algorithm is introduced because something is too slow, too wrong, or about to break. No theory without a problem to solve first. The slow code comes first. The fast code follows.

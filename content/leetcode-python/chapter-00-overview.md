# LeetCode Mastery with Python: From Beginner to Professional

## The Path

This guide takes you from zero to contest-ready through structured pattern recognition. Each chapter builds on the previous, introducing data structures and algorithms in order of dependency.

## Chapters

| #                                         | Topic               | Key Patterns                     |
| ----------------------------------------- | ------------------- | -------------------------------- |
| [01](./chapter-01-arrays-strings.md)      | Arrays & Strings    | Two pointers, sliding window     |
| [02](./chapter-02-hashmaps.md)            | HashMaps & Sets     | Frequency counting, two sum      |
| [03](./chapter-03-linked-lists.md)        | Linked Lists        | Reversal, fast/slow pointers     |
| [04](./chapter-04-stacks-queues.md)       | Stacks & Queues     | Monotonic stack, BFS             |
| [05](./chapter-05-trees.md)               | Binary Trees        | DFS, BFS, traversals             |
| [06](./chapter-06-graphs.md)              | Graphs              | DFS, BFS, topological sort       |
| [07](./chapter-07-dynamic-programming.md) | Dynamic Programming | 1D, 2D, knapsack                 |
| [08](./chapter-08-binary-search.md)       | Binary Search       | On arrays, on answer             |
| [09](./chapter-09-greedy.md)              | Greedy & Intervals  | Scheduling, merge intervals      |
| [10](./chapter-10-advanced.md)            | Advanced            | Tries, Union-Find, Segment Trees |

## How to Use This Guide

1. **Read the pattern** — understand the template before solving problems
2. **Solve the Easy** — build confidence with the basic application
3. **Solve the Medium** — handle edge cases and combine patterns
4. **Attempt the Hard** — optimize and handle constraints
5. **Time yourself** — simulate contest conditions (20 min Easy, 30 min Medium, 45 min Hard)

## Python Tips for Competitive Programming

```python
# Fast I/O
import sys
input = sys.stdin.readline

# Common imports
from collections import defaultdict, Counter, deque
from heapq import heappush, heappop
from itertools import accumulate
from functools import lru_cache
from bisect import bisect_left, bisect_right

# Useful shortcuts
float('inf')   # infinity
float('-inf')  # negative infinity
```

## Complexity Cheat Sheet

| Operation | List | Dict | Set  | Deque | Heap     |
| --------- | ---- | ---- | ---- | ----- | -------- |
| Access    | O(1) | O(1) | —    | O(1)  | —        |
| Search    | O(n) | O(1) | O(1) | O(n)  | O(n)     |
| Insert    | O(n) | O(1) | O(1) | O(1)  | O(log n) |
| Delete    | O(n) | O(1) | O(1) | O(1)  | O(log n) |

---

[next →](./chapter-01-arrays-strings.md)

# Chapter 0: Before You Start

[Chapter 1: Linear Search →](chapter-01-linear-search.md)

---

## The Story

This is a series about algorithms and data structures — but not the kind where you memorize "merge sort is O(n log n)" and move on.

You're a software engineer at **RouteMaster**, a logistics startup that delivers packages across a city of 3 million people. The company grew from 50 deliveries a day to 50,000 in eighteen months. The code didn't keep up. Routes are planned by brute force. Package lookups scan the entire database. The dispatch system assigns drivers by whoever's name comes first alphabetically.

Your engineering manager, **Priya**, drops by your desk:

"The route planner takes 45 minutes to compute morning routes. Drivers are sitting in their vans waiting. Customer lookup crashes when we hit 100,000 packages. The priority system doesn't exist — a hospital waiting for medical supplies gets the same treatment as someone ordering a phone case. Fix it. All of it."

You nod. You took an algorithms class in college. How hard can it be?

Over the next 15 chapters, you'll rebuild RouteMaster's systems from the ground up. Every algorithm you implement solves a real problem — finding packages faster, sorting deliveries by urgency, planning optimal routes, handling real-time priority changes. And every naive solution will break in a way that teaches you why the textbook algorithm exists.

The route planner will time out. The priority queue will starve low-priority packages. The graph algorithm will loop forever on a one-way street cycle. The hash table will degenerate to O(n) during the holiday rush. Each failure teaches you something about computational thinking that no LeetCode problem could.

By the end, you'll have working implementations of searching, sorting, trees, graphs, dynamic programming, and greedy algorithms — and you'll understand *when* and *why* to reach for each one.

## How to Read This

Every chapter is the same loop:

1. Something is too slow, wrong, or impossible with the current approach
2. You measure the problem — how slow? How wrong? At what scale?
3. You learn the algorithm that solves it
4. You implement it, step by step
5. You analyze why it works — and where it breaks next

No algorithm shows up before you need it. You won't hear about binary search until linear search chokes on 100,000 packages. You won't touch Dijkstra until the BFS route planner sends a driver 30km out of the way because it counts intersections, not distance.

The slow code comes first. The fast code follows.

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Software Engineer | Resourceful, hates waiting |
| **Priya** | Engineering Manager | Data-driven. "Show me the benchmarks." |
| **Marcus** | Senior Driver | "Your app told me to drive through a lake." |
| **Dispatch Dan** | Operations Lead | Stares at dashboards. Panics at red numbers. |
| **CEO Lena** | Founder | "We're doing 200,000 deliveries by Q4." |
| **The Intern** | Summer hire | Wrote the original brute-force route planner. Proud of it. |

## The Roadmap

| Ch | The Problem | What You Learn |
|---|---|---|
| 1 | Finding a package in 100K records | Linear search, when it's fine, when it's not |
| 2 | Finding a package in 100K sorted records | Binary search, O(log n), sorted invariants |
| 3 | Sorting deliveries by deadline | Selection sort, insertion sort, why O(n²) hurts |
| 4 | Sorting 50,000 packages for morning dispatch | Merge sort, divide and conquer, O(n log n) |
| 5 | Sorting in-place with limited memory | Quicksort, partitioning, pivot selection |
| 6 | "Which delivery is most urgent RIGHT NOW?" | Heaps, priority queues, heapsort |
| 7 | Customer lookup must be instant | Hash tables, collisions, load factor |
| 8 | Autocomplete for address search | Tries, prefix trees |
| 9 | Package tracking with hierarchy | Binary search trees, AVL trees, balancing |
| 10 | Finding the shortest route between two points | Graphs, BFS, DFS |
| 11 | Finding the fastest route (weighted roads) | Dijkstra's algorithm, priority queue + graph |
| 12 | Planning a route through 20 stops | Greedy algorithms, nearest neighbor, TSP |
| 13 | Optimal package loading (weight limits) | Dynamic programming, knapsack |
| 14 | Delivery zone coverage | Recursion, backtracking |
| 15 | Real-time route updates | Amortized analysis, when to rebuild vs patch |

## Prerequisites

Two things: Python 3 and a willingness to draw things on paper.

### Python 3.10+

Every algorithm is implemented in Python. Not because it's the fastest language — because it reads like pseudocode. You can port to any language after you understand the logic.

```bash
python3 --version
# Python 3.10.x or higher
```

### No Libraries (On Purpose)

We won't use `sorted()`, `heapq`, `collections.deque`, or any built-in that hides the algorithm. You'll build everything from scratch. Once you understand how a heap works, you'll appreciate `heapq`. But not before.

The only imports: `time` (for benchmarking) and `random` (for generating test data).

### A Way to Run Code

Any of these work:
- A Python file and terminal (`python3 chapter_01.py`)
- A Jupyter notebook
- An online REPL (replit.com, pythontutor.com)

### Optional: Visualization

[Python Tutor](https://pythontutor.com) lets you step through code and see memory state. Extremely useful for understanding recursion and tree operations.

### Quick Check

```bash
python3 -c "print('Ready to optimize some routes')"
```

If that prints, you're good.

## Complexity Notation (The Only Theory Upfront)

You need one concept before Chapter 1: Big-O notation. Not the formal math — the intuition.

Big-O answers: "If I double the input size, how much slower does this get?"

| Notation | Name | Doubling input means... | Example |
|---|---|---|---|
| O(1) | Constant | Same time | Hash table lookup |
| O(log n) | Logarithmic | One extra step | Binary search |
| O(n) | Linear | 2x slower | Scanning a list |
| O(n log n) | Linearithmic | ~2.2x slower | Merge sort |
| O(n²) | Quadratic | 4x slower | Nested loops |
| O(2ⁿ) | Exponential | Impossibly slower | Brute-force TSP |

When RouteMaster had 1,000 packages, O(n²) took 1 second. At 50,000 packages, it takes 2,500 seconds (41 minutes). That's why Priya is at your desk.

We'll revisit Big-O in every chapter with concrete measurements. For now, just remember: the exponent in the Big-O is the difference between "runs instantly" and "runs until the heat death of the universe."

Let's find some packages.

---

[Chapter 1: Linear Search →](chapter-01-linear-search.md)

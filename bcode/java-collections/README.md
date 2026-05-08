# Java Collections — From ArrayList to ConcurrentSkipListMap

A narrative-driven course on the Java Collections Framework. You're a backend engineer at **ShipStream**, a real-time order processing platform. The system handles millions of orders, and every data structure choice matters — wrong container, wrong performance, angry customers.

## Episodes

| # | Title | The Problem | What You Learn |
|---|---|---|---|
| 00 | [Before You Start](chapter-00-overview.md) | — | Setup, the Collections hierarchy, the cast |
| 01 | [The Order Queue](chapter-01-arraylist.md) | Orders pile up in a raw array that can't grow | ArrayList, dynamic arrays, amortized O(1) add |
| 02 | [Undo History](chapter-02-linkedlist.md) | Frequent insertions/removals in the middle | LinkedList, doubly-linked nodes, iterator |
| 03 | [No Duplicates Allowed](chapter-03-hashset.md) | Duplicate order IDs slip through | HashSet, hashing, equals/hashCode contract |
| 04 | [Sorted Leaderboard](chapter-04-treeset.md) | Top sellers need sorted order | TreeSet, red-black trees, Comparable |
| 05 | [The Lookup Table](chapter-05-hashmap.md) | Customer lookup by ID must be O(1) | HashMap, buckets, load factor, rehashing |
| 06 | [Ordered Config](chapter-06-linkedhashmap.md) | Insertion order matters for config replay | LinkedHashMap, access-order mode, LRU cache |
| 07 | [Price Ranges](chapter-07-treemap.md) | Range queries on prices | TreeMap, NavigableMap, subMap/headMap/tailMap |
| 08 | [Task Scheduling](chapter-08-priorityqueue.md) | Process high-priority orders first | PriorityQueue, binary heap, Comparator |
| 09 | [FIFO Processing](chapter-09-deque.md) | Work-stealing, double-ended access | ArrayDeque, Deque interface, stack vs queue |
| 10 | [Immutable Snapshots](chapter-10-unmodifiable.md) | Shared state mutated by accident | Collections.unmodifiableX, List.of(), defensive copies |
| 11 | [Bulk Operations](chapter-11-streams-collections.md) | Filter/map/reduce over millions of orders | Streams + Collections, toList, groupingBy |
| 12 | [Choosing the Right Tool](chapter-12-tradeoffs.md) | Performance regressions from wrong choices | Time complexity cheat sheet, memory overhead, when to use what |

## Prerequisites

- Java 17+ (LTS)
- Any IDE or `javac` + terminal

## Philosophy

Every collection is introduced because the current data structure fails under load. You'll feel the pain of O(n) lookups before you reach for a HashMap. The wrong choice comes first. The right choice follows.

# Chapter 0: Before You Start

[Chapter 1: ArrayList →](chapter-01-arraylist.md)

---

## The Story

You're a backend engineer at **ShipStream**, an order processing platform that handles 4 million orders per day across 12 warehouses. The system was built fast — arrays everywhere, linear scans for lookups, duplicates slipping through because nobody checks.

Your tech lead, **Raj**, pulls you into a meeting room:

"The order lookup endpoint is at 800ms p99. The leaderboard page takes 6 seconds. The deduplication job runs for 3 hours every night. We're hemorrhaging money on compute because the data structures are wrong. I need you to fix the collections layer."

You open the codebase. It's `ArrayList` everywhere. Lookups loop through millions of entries. Sorted views re-sort on every request. The priority system uses `Collections.sort()` on every insert.

Every chapter in this course fixes one of these problems by choosing the right collection.

## The Java Collections Hierarchy

```
Iterable
└── Collection
    ├── List          (ordered, indexed, duplicates OK)
    │   ├── ArrayList
    │   ├── LinkedList
    │   └── Vector (legacy)
    ├── Set           (no duplicates)
    │   ├── HashSet
    │   ├── LinkedHashSet
    │   └── TreeSet (sorted)
    └── Queue         (FIFO / priority)
        ├── PriorityQueue
        ├── ArrayDeque
        └── LinkedList

Map (not a Collection, but part of the framework)
├── HashMap
├── LinkedHashMap
├── TreeMap
├── Hashtable (legacy)
└── ConcurrentHashMap
```

You don't need to memorize this. By the end of the course, you'll have used every one of these in a real scenario and you'll know exactly when to reach for each.

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Backend Engineer | Pragmatic, hates unnecessary complexity |
| **Raj** | Tech Lead | "Show me the flamegraph." |
| **Priya** | SRE | Gets paged at 3 AM when your code is slow |
| **Marcus** | Product Manager | "The leaderboard needs to update in real-time" |
| **The Intern** | Summer hire | Wrote `for (int i = 0; i < list.size(); i++)` everywhere |

## Prerequisites

### Java 17+

```bash
java --version
# java 17.0.x or higher
```

We use modern Java features: records, sealed interfaces, pattern matching where helpful. The collections themselves work on Java 8+, but our examples use modern idioms.

### Running Code

Any of these work:
- IntelliJ IDEA (recommended — great debugger for inspecting collection internals)
- VS Code with Java extension
- `javac` + `java` in a terminal
- JShell for quick experiments

### JShell for Exploration

```bash
jshell
|  Welcome to JShell
jshell> var list = new ArrayList<>(List.of(1, 2, 3));
jshell> list.add(4);
jshell> list
list ==> [1, 2, 3, 4]
```

JShell is perfect for testing collection behavior interactively.

## The Performance Mental Model

Every collection operation has a time complexity. The wrong choice means:

| Operation | ArrayList | LinkedList | HashSet | TreeSet |
|---|---|---|---|---|
| Get by index | O(1) | O(n) | — | — |
| Add to end | O(1)* | O(1) | O(1)* | O(log n) |
| Add to middle | O(n) | O(1)† | — | — |
| Contains | O(n) | O(n) | O(1)* | O(log n) |
| Remove | O(n) | O(1)† | O(1)* | O(log n) |

*amortized  †if you have the node/iterator

ShipStream has 4 million orders. The difference between O(1) and O(n) for a lookup is the difference between 1 microsecond and 4 seconds.

## The Rules

1. **See the pain first** — every chapter starts with code that's too slow
2. **Measure before switching** — we benchmark before and after
3. **Understand the tradeoff** — every collection trades something for something else
4. **Use the simplest collection that works** — don't use TreeMap when HashMap suffices

Let's start with the most common collection in Java — and the one ShipStream overuses.

---

[Chapter 1: ArrayList →](chapter-01-arraylist.md)

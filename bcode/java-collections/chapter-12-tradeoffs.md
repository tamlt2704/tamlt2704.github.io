# Chapter 12: Choosing the Right Tool — Tradeoffs

[← Chapter 11: Streams](chapter-11-streams-collections.md)

---

## The Decision Matrix

| I need... | Use | Why |
|---|---|---|
| Indexed access, mostly append | **ArrayList** | O(1) get, O(1) amortized add |
| Frequent insert/remove during iteration | **LinkedList** (via Iterator) | O(1) at iterator position |
| No duplicates, fast contains | **HashSet** | O(1) contains |
| No duplicates, sorted | **TreeSet** | O(log n), range queries |
| No duplicates, insertion order | **LinkedHashSet** | O(1) + order |
| Key-value lookup | **HashMap** | O(1) get/put |
| Key-value, insertion order | **LinkedHashMap** | O(1) + order, LRU cache |
| Key-value, sorted keys | **TreeMap** | O(log n), range queries |
| Priority processing | **PriorityQueue** | O(log n) insert, O(1) peek |
| Queue/Stack | **ArrayDeque** | O(1) both ends, cache-friendly |
| Thread-safe map | **ConcurrentHashMap** | Lock striping, no full lock |
| Thread-safe list (read-heavy) | **CopyOnWriteArrayList** | Snapshot reads, expensive writes |

## Memory Overhead Per Element

| Collection | Overhead per element |
|---|---|
| `int[]` | 0 bytes (just the value) |
| `ArrayList<Integer>` | ~16 bytes (Integer object + reference) |
| `LinkedList<Integer>` | ~48 bytes (Node + Integer + pointers) |
| `HashSet<Integer>` | ~48 bytes (HashMap.Entry + Integer) |
| `TreeSet<Integer>` | ~56 bytes (TreeMap.Entry + Integer + color) |

## The ShipStream Cheat Sheet

After 12 chapters, Raj's team uses this decision process:

1. **Do I need key-value?** → HashMap family
2. **Do I need sorted order?** → TreeSet/TreeMap
3. **Do I need no duplicates?** → Set family
4. **Do I need a queue?** → ArrayDeque or PriorityQueue
5. **Otherwise** → ArrayList (the default)

Then ask: **Is this concurrent?** If yes, use `java.util.concurrent` versions.

## Performance Traps

1. **ArrayList.contains() in a loop** → Use HashSet
2. **Sorting on every access** → Use TreeSet/TreeMap
3. **LinkedList for random access** → Use ArrayList
4. **HashMap with bad hashCode** → Fix hashCode or use TreeMap
5. **Synchronizing everything** → Use concurrent collections

## What You Learned (The Whole Course)

- Collections are tools — pick the right one for the job
- O(1) vs O(n) is the difference between milliseconds and minutes at scale
- Memory overhead matters at millions of elements
- Immutability prevents bugs; defensive copies protect internal state
- Streams provide declarative bulk operations
- When in doubt, start with ArrayList and HashMap — upgrade when you measure a problem

---

[← Chapter 11: Streams](chapter-11-streams-collections.md)

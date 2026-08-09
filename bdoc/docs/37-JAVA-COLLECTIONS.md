# Chapter 37: Java Collections — Complete Guide with Examples

## What you'll learn

- The Collections Framework hierarchy (interfaces + implementations)
- List: ArrayList, LinkedList, CopyOnWriteArrayList
- Set: HashSet, LinkedHashSet, TreeSet
- Map: HashMap, LinkedHashMap, TreeMap, ConcurrentHashMap
- Queue/Deque: ArrayDeque, PriorityQueue, BlockingQueue
- How each works internally (data structure, hashing, trees)
- Stream Collectors: groupingBy, partitioning, toMap, joining, reducing
- Choosing the right collection for every situation

---

## PART 1: The Framework

## 37.1 Hierarchy overview

```
                        Iterable
                           │
                      Collection
                     ╱     │      ╲
                  List    Set     Queue
                  │        │        │
            ┌─────┼────┐   │    ┌───┼────┐
            │     │    │   │    │   │    │
      ArrayList  │  Vector │  ArrayDeque │
                 │         │        PriorityQueue
           LinkedList   ┌──┼──┐
                        │  │  │
                   HashSet │ TreeSet
                           │
                     LinkedHashSet


                       Map (separate hierarchy)
                     ╱     │      ╲
              HashMap  TreeMap  LinkedHashMap
                 │
         ConcurrentHashMap
```

## 37.2 Key interfaces

| Interface | Contract | Allows duplicates? | Ordered? |
|-----------|----------|-------------------|----------|
| `List` | Indexed, sequential | Yes | Insertion order |
| `Set` | Unique elements | No | Depends on implementation |
| `Queue` | FIFO (or priority) | Yes | FIFO or priority |
| `Deque` | Double-ended queue | Yes | Insertion order |
| `Map` | Key→Value pairs | Keys: No, Values: Yes | Depends on implementation |

---

## PART 2: List Implementations

## 37.3 ArrayList — the default choice

Backed by a dynamic array. Fast random access, slow middle insert/remove.

```java
// Creation
List<String> names = new ArrayList<>();
List<String> names = new ArrayList<>(1000);  // pre-sized (avoid resizes)
List<String> names = List.of("Alice", "Bob", "Carol");  // immutable
List<String> names = new ArrayList<>(List.of("Alice", "Bob"));  // mutable copy

// Basic operations
names.add("Dave");              // append — O(1) amortized
names.add(1, "Eve");           // insert at index — O(n) (shifts elements)
names.get(2);                   // access by index — O(1)
names.set(0, "Zara");          // replace at index — O(1)
names.remove(0);               // remove by index — O(n) (shifts)
names.remove("Bob");           // remove by value — O(n) (search + shift)
names.size();                   // length
names.isEmpty();
names.contains("Alice");       // O(n) linear scan
names.indexOf("Bob");          // first occurrence, -1 if absent

// Iteration
for (String name : names) { }                          // enhanced for
names.forEach(System.out::println);                    // forEach
for (int i = 0; i < names.size(); i++) names.get(i);  // indexed (fastest for ArrayList)

// Sorting
names.sort(Comparator.naturalOrder());               // A-Z
names.sort(Comparator.reverseOrder());               // Z-A
names.sort(Comparator.comparing(String::length));    // by length

// Filtering (creates new list)
List<String> filtered = names.stream()
    .filter(n -> n.startsWith("A"))
    .toList();  // Java 16+ (immutable result)

// Sublist (view — changes reflect in original!)
List<String> sub = names.subList(1, 3); // index 1 and 2
```

**Internal mechanics:**
```
Initial: [_, _, _, _, _, _, _, _, _, _]  capacity=10, size=0
add("A"): [A, _, _, _, _, _, _, _, _, _]  size=1
add("B"): [A, B, _, _, _, _, _, _, _, _]  size=2
...
add(11th): capacity doubled → new array of 15, copy all elements, then add
```

## 37.4 LinkedList — when you need it (rarely)

Doubly-linked list. Fast insert/remove at known positions, slow random access.

```java
LinkedList<String> list = new LinkedList<>();

// Same List API as ArrayList, PLUS:
list.addFirst("head");        // O(1)
list.addLast("tail");         // O(1)
list.getFirst();              // O(1)
list.getLast();               // O(1)
list.removeFirst();           // O(1)
list.removeLast();            // O(1)

// Also implements Deque (double-ended queue)
list.push("stack-top");      // addFirst
list.pop();                  // removeFirst
list.offer("queue-end");     // addLast
list.poll();                 // removeFirst
```

**When to use LinkedList:**
- You need O(1) removal during iteration (with `ListIterator`)
- You use it exclusively as a Deque (but `ArrayDeque` is faster for this too)

**When NOT to use:**
- Random access by index (`get(500)` is O(n) — traverses from head)
- You're just appending and reading sequentially (ArrayList is faster due to cache)

---

## PART 3: Set Implementations

## 37.5 HashSet — unique elements, O(1) lookup

Backed by a HashMap (keys only, values are dummy objects).

```java
Set<String> fruits = new HashSet<>();
fruits.add("Apple");           // O(1)
fruits.add("Banana");
fruits.add("Apple");           // duplicate — ignored, returns false
fruits.contains("Banana");     // O(1)
fruits.remove("Apple");        // O(1)
fruits.size();                 // 1

// From a list (deduplication)
List<String> withDupes = List.of("a", "b", "a", "c", "b");
Set<String> unique = new HashSet<>(withDupes);  // {"a", "b", "c"}

// Set operations
Set<Integer> a = Set.of(1, 2, 3, 4);
Set<Integer> b = Set.of(3, 4, 5, 6);

// Union
Set<Integer> union = new HashSet<>(a);
union.addAll(b);  // {1, 2, 3, 4, 5, 6}

// Intersection
Set<Integer> intersection = new HashSet<>(a);
intersection.retainAll(b);  // {3, 4}

// Difference
Set<Integer> diff = new HashSet<>(a);
diff.removeAll(b);  // {1, 2}
```

**No ordering guarantee.** Iteration order is unpredictable.

## 37.6 LinkedHashSet — unique + insertion order

```java
Set<String> ordered = new LinkedHashSet<>();
ordered.add("Banana");
ordered.add("Apple");
ordered.add("Cherry");

// Iteration: Banana, Apple, Cherry (insertion order preserved)
for (String fruit : ordered) System.out.println(fruit);
```

Uses extra linked list to maintain insertion order. Slightly more memory than HashSet.

## 37.7 TreeSet — unique + sorted

Backed by a Red-Black Tree. All operations O(log n).

```java
Set<Integer> sorted = new TreeSet<>();
sorted.add(5);
sorted.add(2);
sorted.add(8);
sorted.add(1);

// Iteration: 1, 2, 5, 8 (always sorted!)
for (int n : sorted) System.out.println(n);

// NavigableSet methods
TreeSet<Integer> tree = new TreeSet<>(sorted);
tree.first();          // 1 (smallest)
tree.last();           // 8 (largest)
tree.lower(5);         // 2 (largest element < 5)
tree.higher(5);        // 8 (smallest element > 5)
tree.floor(5);         // 5 (largest element ≤ 5)
tree.ceiling(3);       // 5 (smallest element ≥ 3)
tree.headSet(5);       // {1, 2} (elements < 5)
tree.tailSet(5);       // {5, 8} (elements ≥ 5)
tree.subSet(2, 8);     // {2, 5} (elements in [2, 8))

// Custom comparator
Set<String> byLength = new TreeSet<>(Comparator.comparingInt(String::length));
byLength.add("Banana");  // length 6
byLength.add("Fig");     // length 3
byLength.add("Apple");   // length 5
// Iteration: Fig, Apple, Banana (sorted by length)
```

| | HashSet | LinkedHashSet | TreeSet |
|---|---|---|---|
| Order | None | Insertion order | Sorted (natural or Comparator) |
| add/remove/contains | O(1) | O(1) | O(log n) |
| Use when | Just need uniqueness | Unique + predictable order | Unique + sorted + range queries |

---

## PART 4: Map Implementations

## 37.8 HashMap — the workhorse

```java
Map<String, Integer> scores = new HashMap<>();
scores.put("Alice", 95);        // O(1)
scores.put("Bob", 87);
scores.put("Alice", 98);        // replaces previous value, returns 95

scores.get("Alice");             // 98 — O(1)
scores.get("Unknown");           // null
scores.getOrDefault("Unknown", 0);  // 0

scores.containsKey("Bob");       // true — O(1)
scores.containsValue(87);        // true — O(n) (scans all values!)
scores.remove("Bob");            // removes entry, returns 87
scores.size();                   // 1

// Iteration
for (Map.Entry<String, Integer> entry : scores.entrySet()) {
    System.out.println(entry.getKey() + ": " + entry.getValue());
}
scores.forEach((name, score) -> System.out.println(name + ": " + score));

// Keys and values separately
Set<String> keys = scores.keySet();
Collection<Integer> values = scores.values();
```

### Advanced HashMap operations

```java
// computeIfAbsent — create value on first access (lazy init)
Map<String, List<String>> groups = new HashMap<>();
groups.computeIfAbsent("fruits", k -> new ArrayList<>()).add("Apple");
groups.computeIfAbsent("fruits", k -> new ArrayList<>()).add("Banana");
// {"fruits": ["Apple", "Banana"]}

// merge — accumulate values
Map<String, Integer> wordCount = new HashMap<>();
for (String word : words) {
    wordCount.merge(word, 1, Integer::sum);  // increment or start at 1
}

// compute — transform existing value
scores.compute("Alice", (key, val) -> val == null ? 0 : val + 10);

// replaceAll — transform all values
scores.replaceAll((name, score) -> score + 5);  // everyone gets +5

// putIfAbsent — only insert if key doesn't exist
scores.putIfAbsent("Carol", 75);  // won't overwrite if Carol already exists
```

### How HashMap works internally

```
Bucket array (initial size 16):

Index:  [0]  [1]  [2]  [3]  [4]  [5]  [6]  [7]  ...
         │         │
         ▼         ▼
       Alice     Bob → Carol (collision: linked list, or tree if > 8)
       
hash("Alice") % 16 = 0  → bucket[0]
hash("Bob")   % 16 = 2  → bucket[2]
hash("Carol") % 16 = 2  → bucket[2] (collision! chain after Bob)

Load factor (default 0.75):
  When 12 of 16 buckets are used → resize to 32 (rehash everything)

Java 8+: when a bucket has > 8 entries → convert chain to Red-Black Tree (O(log n) instead of O(n))
```

## 37.9 LinkedHashMap — HashMap + insertion order

```java
Map<String, Integer> ordered = new LinkedHashMap<>();
ordered.put("Banana", 3);
ordered.put("Apple", 5);
ordered.put("Cherry", 2);

// Iteration: Banana→3, Apple→5, Cherry→2 (insertion order!)

// Access-order mode (LRU cache!)
Map<String, Integer> lru = new LinkedHashMap<>(16, 0.75f, true); // true = access order
lru.put("A", 1);
lru.put("B", 2);
lru.put("C", 3);
lru.get("A");  // moves A to end (most recently accessed)
// Order now: B, C, A

// LRU cache with automatic eviction
Map<String, Integer> cache = new LinkedHashMap<>(100, 0.75f, true) {
    @Override
    protected boolean removeEldestEntry(Map.Entry<String, Integer> eldest) {
        return size() > 100;  // evict oldest when over 100 entries
    }
};
```

## 37.10 TreeMap — sorted by keys

Backed by Red-Black Tree. All operations O(log n).

```java
Map<String, Integer> sorted = new TreeMap<>();
sorted.put("Charlie", 70);
sorted.put("Alice", 95);
sorted.put("Bob", 87);

// Iteration: Alice→95, Bob→87, Charlie→70 (alphabetical order!)

// NavigableMap methods
TreeMap<Integer, String> tree = new TreeMap<>();
tree.put(10, "ten");
tree.put(20, "twenty");
tree.put(30, "thirty");
tree.put(40, "forty");

tree.firstKey();              // 10
tree.lastKey();               // 40
tree.lowerKey(25);            // 20 (largest key < 25)
tree.higherKey(25);           // 30 (smallest key > 25)
tree.floorKey(20);            // 20 (largest key ≤ 20)
tree.ceilingKey(25);          // 30 (smallest key ≥ 25)
tree.headMap(30);             // {10=ten, 20=twenty} (keys < 30)
tree.tailMap(20);             // {20=twenty, 30=thirty, 40=forty} (keys ≥ 20)
tree.subMap(10, 30);          // {10=ten, 20=twenty} (keys in [10, 30))

// Custom comparator (sort by value instead of key)
Map<String, Integer> scores = Map.of("Alice", 95, "Bob", 87, "Carol", 92);
TreeMap<String, Integer> byScore = new TreeMap<>(
    Comparator.comparingInt(scores::get).reversed()  // highest score first
);
byScore.putAll(scores);
```

## 37.11 ConcurrentHashMap — thread-safe

```java
ConcurrentMap<String, AtomicInteger> counters = new ConcurrentHashMap<>();

// Thread-safe operations (no external synchronization needed)
counters.putIfAbsent("pageViews", new AtomicInteger(0));
counters.get("pageViews").incrementAndGet();

// Atomic compute (whole operation is atomic)
counters.compute("pageViews", (key, val) -> {
    val.incrementAndGet();
    return val;
});

// Parallel bulk operations (Java 8+)
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
// ... populate ...

// Search in parallel
String result = map.search(4, (key, value) -> value > 100 ? key : null);

// Reduce in parallel
int total = map.reduceValues(4, Integer::sum);  // 4 = parallelism threshold

// forEach in parallel
map.forEach(4, (key, value) -> System.out.println(key + "=" + value));
```

| | HashMap | LinkedHashMap | TreeMap | ConcurrentHashMap |
|---|---|---|---|---|
| Order | None | Insertion (or access) | Sorted by key | None |
| get/put | O(1) | O(1) | O(log n) | O(1) |
| Thread-safe | No | No | No | Yes |
| Null keys | 1 allowed | 1 allowed | No (needs comparison) | No |
| Use when | General purpose | LRU cache, predictable iteration | Sorted keys, range queries | Multi-threaded access |

---

## PART 5: Queue and Deque

## 37.12 ArrayDeque — stack AND queue (use this by default)

```java
// As a Queue (FIFO)
Deque<String> queue = new ArrayDeque<>();
queue.offer("first");       // add to tail
queue.offer("second");
queue.offer("third");
queue.poll();               // remove from head → "first"
queue.peek();               // look at head without removing → "second"

// As a Stack (LIFO)
Deque<Integer> stack = new ArrayDeque<>();
stack.push(1);              // add to head
stack.push(2);
stack.push(3);
stack.pop();                // remove from head → 3
stack.peek();               // → 2

// Deque operations (both ends)
Deque<String> deque = new ArrayDeque<>();
deque.offerFirst("A");     // add to front
deque.offerLast("B");      // add to back
deque.peekFirst();         // "A"
deque.peekLast();          // "B"
deque.pollFirst();         // remove from front
deque.pollLast();          // remove from back
```

> **Never use `java.util.Stack`** (it extends Vector — synchronized everywhere, slow). Use `ArrayDeque` for stack operations.

## 37.13 PriorityQueue — sorted automatically

Min-heap by default (smallest element first).

```java
// Natural ordering (min-heap)
PriorityQueue<Integer> minHeap = new PriorityQueue<>();
minHeap.offer(5);
minHeap.offer(2);
minHeap.offer(8);
minHeap.offer(1);
minHeap.poll();  // → 1 (smallest)
minHeap.poll();  // → 2
minHeap.poll();  // → 5

// Max-heap (reversed)
PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Comparator.reverseOrder());
maxHeap.offer(5);
maxHeap.offer(2);
maxHeap.offer(8);
maxHeap.poll();  // → 8 (largest)

// Custom objects
PriorityQueue<Task> taskQueue = new PriorityQueue<>(
    Comparator.comparingInt(Task::getPriority)
              .thenComparing(Task::getCreatedAt)
);

// Top-K pattern: keep K largest elements using min-heap of size K
PriorityQueue<Integer> topK = new PriorityQueue<>(); // min-heap
for (int num : numbers) {
    topK.offer(num);
    if (topK.size() > k) topK.poll(); // remove smallest (keep K largest)
}
// topK now contains the K largest elements
```

---

## PART 6: Stream Collectors

## 37.14 Collecting to different structures

```java
List<Person> people = List.of(
    new Person("Alice", 30, "Engineering"),
    new Person("Bob", 25, "Marketing"),
    new Person("Carol", 35, "Engineering"),
    new Person("Dave", 28, "Marketing"),
    new Person("Eve", 32, "Engineering")
);

// Collect to List
List<String> names = people.stream()
    .map(Person::getName)
    .collect(Collectors.toList());       // mutable list
    // or .toList();                     // immutable (Java 16+)

// Collect to Set (deduplicated)
Set<String> departments = people.stream()
    .map(Person::getDepartment)
    .collect(Collectors.toSet());        // {"Engineering", "Marketing"}

// Collect to specific collection type
TreeSet<String> sortedNames = people.stream()
    .map(Person::getName)
    .collect(Collectors.toCollection(TreeSet::new));
```

## 37.15 Collectors.toMap

```java
// Simple: name → age
Map<String, Integer> nameToAge = people.stream()
    .collect(Collectors.toMap(Person::getName, Person::getAge));
// {"Alice": 30, "Bob": 25, ...}

// Handle duplicate keys (merge function)
Map<String, Integer> deptCount = people.stream()
    .collect(Collectors.toMap(
        Person::getDepartment,
        p -> 1,
        Integer::sum  // if key exists, sum the values
    ));
// {"Engineering": 3, "Marketing": 2}

// Collect to specific map type
TreeMap<String, Integer> sorted = people.stream()
    .collect(Collectors.toMap(
        Person::getName,
        Person::getAge,
        (a, b) -> a,   // merge function (never called if keys unique)
        TreeMap::new    // map factory
    ));
```

## 37.16 Collectors.groupingBy — the powerful one

```java
// Group by department
Map<String, List<Person>> byDept = people.stream()
    .collect(Collectors.groupingBy(Person::getDepartment));
// {"Engineering": [Alice, Carol, Eve], "Marketing": [Bob, Dave]}

// Group by department, collect names only
Map<String, List<String>> namesByDept = people.stream()
    .collect(Collectors.groupingBy(
        Person::getDepartment,
        Collectors.mapping(Person::getName, Collectors.toList())
    ));
// {"Engineering": ["Alice", "Carol", "Eve"], "Marketing": ["Bob", "Dave"]}

// Group and count
Map<String, Long> countByDept = people.stream()
    .collect(Collectors.groupingBy(
        Person::getDepartment,
        Collectors.counting()
    ));
// {"Engineering": 3, "Marketing": 2}

// Group and sum
Map<String, Integer> totalAgeByDept = people.stream()
    .collect(Collectors.groupingBy(
        Person::getDepartment,
        Collectors.summingInt(Person::getAge)
    ));

// Group and find max
Map<String, Optional<Person>> oldestByDept = people.stream()
    .collect(Collectors.groupingBy(
        Person::getDepartment,
        Collectors.maxBy(Comparator.comparingInt(Person::getAge))
    ));

// Group and join strings
Map<String, String> nameListByDept = people.stream()
    .collect(Collectors.groupingBy(
        Person::getDepartment,
        Collectors.mapping(Person::getName, Collectors.joining(", "))
    ));
// {"Engineering": "Alice, Carol, Eve", "Marketing": "Bob, Dave"}

// Multi-level grouping
Map<String, Map<Integer, List<Person>>> byDeptAndAge = people.stream()
    .collect(Collectors.groupingBy(
        Person::getDepartment,
        Collectors.groupingBy(p -> p.getAge() / 10 * 10) // decade bucket
    ));

// Use TreeMap for sorted groups
Map<String, List<Person>> sortedByDept = people.stream()
    .collect(Collectors.groupingBy(
        Person::getDepartment,
        TreeMap::new,  // sorted map factory
        Collectors.toList()
    ));
```

## 37.17 Collectors.partitioningBy — split into two groups

```java
// Boolean split: true/false
Map<Boolean, List<Person>> seniorSplit = people.stream()
    .collect(Collectors.partitioningBy(p -> p.getAge() >= 30));
// {true: [Alice, Carol, Eve], false: [Bob, Dave]}

// Partition + downstream collector
Map<Boolean, Long> seniorCount = people.stream()
    .collect(Collectors.partitioningBy(
        p -> p.getAge() >= 30,
        Collectors.counting()
    ));
// {true: 3, false: 2}
```

## 37.18 Other useful Collectors

```java
// joining — concatenate strings
String allNames = people.stream()
    .map(Person::getName)
    .collect(Collectors.joining(", ", "[", "]"));
// "[Alice, Bob, Carol, Dave, Eve]"

// summarizingInt — all stats at once
IntSummaryStatistics stats = people.stream()
    .collect(Collectors.summarizingInt(Person::getAge));
stats.getCount();    // 5
stats.getSum();      // 150
stats.getMin();      // 25
stats.getMax();      // 35
stats.getAverage();  // 30.0

// reducing — custom reduction
Optional<Person> oldest = people.stream()
    .collect(Collectors.reducing(
        BinaryOperator.maxBy(Comparator.comparingInt(Person::getAge))
    ));

// collectingAndThen — transform the final result
List<Person> unmodifiable = people.stream()
    .filter(p -> p.getAge() > 25)
    .collect(Collectors.collectingAndThen(
        Collectors.toList(),
        Collections::unmodifiableList  // wrap result as immutable
    ));

// teeing — two collectors at once (Java 12+)
Map.Entry<Long, Double> countAndAvg = people.stream()
    .collect(Collectors.teeing(
        Collectors.counting(),
        Collectors.averagingInt(Person::getAge),
        Map::entry
    ));
// Entry{5, 30.0}
```

---

## PART 7: Choosing the Right Collection

## 37.19 Decision flowchart

```
Need key→value pairs?
├── YES → Need sorted keys?
│         ├── YES → TreeMap
│         └── NO → Need thread-safe?
│                   ├── YES → ConcurrentHashMap
│                   └── NO → Need insertion order?
│                             ├── YES → LinkedHashMap
│                             └── NO → HashMap
└── NO → Need unique elements?
          ├── YES → Need sorted?
          │         ├── YES → TreeSet
          │         └── NO → Need insertion order?
          │                   ├── YES → LinkedHashSet
          │                   └── NO → HashSet
          └── NO → Need FIFO/LIFO?
                    ├── FIFO (queue) → ArrayDeque
                    ├── LIFO (stack) → ArrayDeque
                    ├── Priority → PriorityQueue
                    └── Just a list → Need random access?
                                      ├── YES → ArrayList
                                      └── NO (only sequential + ends) → ArrayDeque
```

## 37.20 Performance comparison

| Operation | ArrayList | LinkedList | HashSet | TreeSet | HashMap | TreeMap |
|-----------|-----------|-----------|---------|---------|---------|---------|
| get(index) | **O(1)** | O(n) | — | — | — | — |
| add (end) | **O(1)** amortized | O(1) | — | — | — | — |
| add (middle) | O(n) | **O(1)*** | — | — | — | — |
| contains | O(n) | O(n) | **O(1)** | O(log n) | — | — |
| put/get | — | — | — | — | **O(1)** | O(log n) |
| Sorted iteration | O(n log n) | O(n log n) | O(n log n) | **O(n)** | O(n log n) | **O(n)** |
| Memory/element | 4-8 bytes | 24+ bytes | 32+ bytes | 48+ bytes | 32+ bytes | 48+ bytes |

*LinkedList O(1) insert only with an iterator at the position — finding the position is still O(n).

---

## Summary

✅ List: ArrayList (default), LinkedList (rare — deque use only)
✅ Set: HashSet (uniqueness), LinkedHashSet (+ order), TreeSet (+ sorted)
✅ Map: HashMap (default), LinkedHashMap (+ order / LRU), TreeMap (+ sorted + range queries)
✅ Queue: ArrayDeque (stack/queue), PriorityQueue (sorted/top-K)
✅ ConcurrentHashMap for multi-threaded access
✅ Stream Collectors: toMap, groupingBy, partitioningBy, joining, summarizing, teeing
✅ Internal mechanics: HashMap bucket array + Red-Black tree, TreeMap Red-Black tree, ArrayList dynamic array

## Key takeaways

**HashMap + ArrayList cover 80% of use cases.** Start here, switch only when you need ordering (LinkedHash/Tree variants) or concurrency (Concurrent variants).

**`groupingBy` is the most powerful Collector.** It replaces manual loop-based grouping with a single declarative call. Combine with downstream collectors (counting, mapping, joining) for complex aggregations.

**TreeMap/TreeSet give you range queries for free.** `headMap`, `tailMap`, `subMap`, `floor`, `ceiling` — problems that require sorted access are trivial with tree collections.

**Pre-size collections when you know the size.** `new ArrayList<>(10000)` and `new HashMap<>(capacity)` avoid expensive resize operations.

---

→ [Back to Chapter 36: Java Performance](./36-JAVA-PERFORMANCE.md)

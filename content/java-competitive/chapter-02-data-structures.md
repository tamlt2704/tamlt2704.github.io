# Chapter 2: Data Structures for Speed

[prev: Fast I/O](chapter-01-fast-io.md) | [next: Algorithms](chapter-03-algorithms.md)

## The Boxing Problem

The single biggest performance trap in Java CP: **object overhead**.

- `int`: 4 bytes, stored on stack/inline
- `Integer`: 16+ bytes (object header) + heap allocation + GC pressure

**Rule: Use primitive arrays (`int[]`, `long[]`) whenever possible.**

In C++, `vector<int>` stores primitives directly. Java's `ArrayList<Integer>` stores boxed objects with pointer indirection.

## ArrayList vs LinkedList

**Always use ArrayList.** There is no CP scenario where LinkedList wins.

| Operation         | ArrayList      | LinkedList |
| ----------------- | -------------- | ---------- |
| get(i)            | O(1)           | O(n)       |
| add (end)         | O(1) amortized | O(1)       |
| Cache performance | Excellent      | Terrible   |

LinkedList has ~6x more memory overhead per element and destroys cache locality.

## HashMap vs TreeMap

|          | HashMap      | TreeMap                          |
| -------- | ------------ | -------------------------------- |
| get/put  | O(1) average | O(log n)                         |
| Ordered  | No           | Yes (sorted keys)                |
| Use when | Need speed   | Need sorted order, floor/ceiling |

```java
// Frequency counting - use HashMap
Map<Integer, Integer> freq = new HashMap<>();
for (int x : arr) freq.merge(x, 1, Integer::sum);

// Need sorted keys or range queries - use TreeMap
TreeMap<Integer, Integer> tm = new TreeMap<>();
tm.floorKey(x);   // largest key <= x
tm.ceilingKey(x); // smallest key >= x
```

**Pre-size HashMap** if you know the count:

```java
Map<Integer, Integer> map = new HashMap<>(n * 4 / 3 + 1);
```

**Warning:** Java's HashMap has O(n) worst case due to hash collisions. On Codeforces, adversarial tests exploit this. Custom hash or shuffle:

```java
// Custom hash to avoid collision attacks
static long customHash(long x) {
    x ^= x >>> 33;
    x *= 0xff51afd7ed558ccdL;
    x ^= x >>> 33;
    x *= 0xc4ceb9fe1a85ec53L;
    x ^= x >>> 33;
    return x;
}
```

## PriorityQueue

Min-heap by default. O(log n) insert and extract-min.

```java
// Min-heap (default)
PriorityQueue<Integer> pq = new PriorityQueue<>();

// Max-heap
PriorityQueue<Integer> pq = new PriorityQueue<>(Collections.reverseOrder());

// Custom comparator
PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[1] - b[1]);
```

**Performance trick:** Encode (dist, node) as a single long to avoid boxing:

```java
PriorityQueue<Long> pq = new PriorityQueue<>();
pq.add((long) dist << 32 | node);
long top = pq.poll();
int d = (int)(top >>> 32);
int u = (int)(top & 0xFFFFFFFFL);
```

## ArrayDeque — The Universal Container

**Use ArrayDeque instead of Stack, Queue, or LinkedList.**

|          | ArrayDeque    | Stack                 | LinkedList       |
| -------- | ------------- | --------------------- | ---------------- |
| Push/Pop | O(1)          | O(1)                  | O(1)             |
| Memory   | Compact array | Vector (synchronized) | Nodes + pointers |
| Cache    | Excellent     | Good                  | Terrible         |

```java
// As stack
Deque<Integer> stack = new ArrayDeque<>();
stack.push(x); stack.pop(); stack.peek();

// As queue
Deque<Integer> queue = new ArrayDeque<>();
queue.offer(x); queue.poll(); queue.peek();
```

## BitSet

For boolean arrays or set operations on integers in range [0, n):

```java
BitSet bs = new BitSet(n);
bs.set(i);          // set bit i
bs.get(i);          // check bit i
bs.cardinality();   // count set bits - O(n/64)
bs.and(other);      // intersection
bs.or(other);       // union
bs.nextSetBit(0);   // first set bit
```

**64x more memory efficient** than `boolean[]`. Set operations are O(n/64) using word-level ops.

**Use cases:** Sieve of Eratosthenes, subset DP, reachability in graphs.

## int[] vs Integer[]

```java
// Good: 4 bytes per element, cache-friendly
int[] arr = new int[n];
Arrays.sort(arr); // dual-pivot quicksort

// Bad: 16+ bytes per element, pointer chasing
Integer[] arr = new Integer[n];
Arrays.sort(arr); // TimSort (stable but slower for primitives)
```

**When you must use Integer[]:** Custom comparator with Arrays.sort. Workaround — sort an index array:

```java
Integer[] idx = new Integer[n];
for (int i = 0; i < n; i++) idx[i] = i;
Arrays.sort(idx, (a, b) -> arr[a] - arr[b]);
```

## Summary: When to Use What

| Need                | Use           | Avoid                         |
| ------------------- | ------------- | ----------------------------- |
| Dynamic array       | ArrayList     | LinkedList                    |
| Stack/Queue         | ArrayDeque    | Stack, LinkedList             |
| Key-value (fast)    | HashMap       | TreeMap (unless need order)   |
| Key-value (ordered) | TreeMap       | -                             |
| Priority queue      | PriorityQueue | -                             |
| Boolean flags       | BitSet        | boolean[] (if memory matters) |
| Number array        | int[]/long[]  | Integer[]/Long[]              |

## Relevant Problems

- **Codeforces 702C** — TreeMap for efficient range queries
- **LeetCode 239** — Sliding Window Maximum (ArrayDeque as monotonic deque)
- **Codeforces 1702G** — BitSet for subset operations

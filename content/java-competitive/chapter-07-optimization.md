# Chapter 7: JVM Optimization Tricks

[prev: Strings](chapter-06-strings.md) | [next: Contest Templates](chapter-08-templates.md)

## Avoid Autoboxing

Every time you put an `int` into a `List<Integer>`, Java creates an `Integer` object (16 bytes + GC pressure).

```java
// BAD: creates 10^6 Integer objects
List<Integer> list = new ArrayList<>();
for (int i = 0; i < 1000000; i++) list.add(i);

// GOOD: primitive array, zero overhead
int[] arr = new int[1000000];
```

**Where boxing hides:**

- `HashMap<Integer, Integer>` — both key and value are boxed
- `PriorityQueue<Integer>` — every element boxed
- `List<Integer>` — every element boxed
- `Collections.sort()` — requires `List<T>`

**Mitigation:** Use primitive arrays wherever possible. When you must use collections, minimize insertions in hot loops.

## Pre-allocate Arrays

Never grow arrays dynamically in performance-critical code:

```java
// BAD: ArrayList resizes multiple times
List<Integer> result = new ArrayList<>();

// GOOD: know the size upfront
int[] result = new int[n];
int size = 0;
result[size++] = value;
```

For adjacency lists, pre-compute sizes:

```java
int[] degree = new int[n];
for (int[] edge : edges) { degree[edge[0]]++; degree[edge[1]]++; }
int[][] adj = new int[n][];
for (int i = 0; i < n; i++) adj[i] = new int[degree[i]];
```

## Avoid GC Pressure

Garbage collection pauses can cause TLE. Strategies:

1. **Reuse objects** — don't create new arrays in loops
2. **Use static arrays** — allocate once at class level
3. **Avoid String creation** — use char[] and StringBuilder
4. **Pool small arrays** — reuse int[2] pairs

```java
// BAD: creates n new arrays
for (int i = 0; i < n; i++) pq.offer(new int[]{dist, i});

// BETTER: encode into long
for (int i = 0; i < n; i++) pq.offer((long)dist << 32 | i);
```

## Static vs Instance

In competitive programming, use `static` for everything. Avoids implicit `this` reference and allows direct access:

```java
public class Main {
    static int[] arr;
    static int n;

    static void solve() {
        // direct access to static fields, no 'this' overhead
    }

    public static void main(String[] args) {
        solve();
    }
}
```

## The final Keyword

`final` on local variables helps the JIT compiler optimize:

```java
final int n = arr.length; // JIT can inline this
for (int i = 0; i < n; i++) { ... }
```

In practice, the JIT usually figures this out, but `final` on fields prevents accidental reassignment and can enable constant folding.

## Bit Manipulation Tricks

```java
// Count set bits - O(1) with hardware intrinsic
Integer.bitCount(x);
Long.bitCount(x);

// Lowest set bit
int lowest = x & (-x);

// Remove lowest set bit
x &= (x - 1);

// Check if power of 2
boolean isPow2 = (x & (x - 1)) == 0 && x > 0;

// Next power of 2 >= x
int next = Integer.highestOneBit(x - 1) << 1;

// Floor log2
int log2 = 31 - Integer.numberOfLeadingZeros(x);

// Iterate over all submasks of mask
for (int sub = mask; sub > 0; sub = (sub - 1) & mask) {
    // process submask
}

// Swap without temp
a ^= b; b ^= a; a ^= b;

// Absolute value without branch
int abs = (x ^ (x >> 31)) - (x >> 31);

// Max/min without branch
int max = a ^ ((a ^ b) & -(a < b ? 1 : 0)); // not always faster in Java
```

**C++ comparison:** C++ has `__builtin_popcount`, `__builtin_ctz`, `__builtin_clz`. Java equivalents are `Integer.bitCount()`, `Integer.numberOfTrailingZeros()`, `Integer.numberOfLeadingZeros()`.

## Loop Optimization

```java
// Cache array length
for (int i = 0, n = arr.length; i < n; i++) { ... }

// Avoid method calls in loop condition
int size = list.size();
for (int i = 0; i < size; i++) { ... }

// Prefer ++i style (no difference in Java, but good habit)
// Use enhanced for-loop only when you don't need index
for (int x : arr) sum += x;
```

## Memory Layout Awareness

Java arrays are contiguous in memory. 2D arrays are arrays of pointers to arrays (not contiguous):

```java
// int[][] grid = new int[n][m];
// grid[i] and grid[i+1] may not be adjacent in memory

// For cache-friendly access, iterate row by row:
for (int i = 0; i < n; i++)
    for (int j = 0; j < m; j++)
        process(grid[i][j]); // good: sequential access

// BAD: column-major access (cache misses)
for (int j = 0; j < m; j++)
    for (int i = 0; i < n; i++)
        process(grid[i][j]); // bad: jumping between rows
```

**Flatten 2D to 1D** for maximum cache performance:

```java
int[] grid = new int[n * m];
// Access (i, j) as grid[i * m + j]
```

## Common Pitfalls Summary

| Pitfall                               | Fix                                      |
| ------------------------------------- | ---------------------------------------- |
| Scanner                               | BufferedReader + StringTokenizer         |
| String += in loop                     | StringBuilder                            |
| Integer[]                             | int[]                                    |
| LinkedList                            | ArrayList or ArrayDeque                  |
| Stack class                           | ArrayDeque                               |
| Recursive DFS (deep)                  | Iterative or new Thread with large stack |
| HashMap collision attack              | Custom hash or shuffle keys              |
| Arrays.sort on primitives (anti-hack) | Shuffle before sort                      |
| 2D array column access                | Row-major or flatten                     |

## Relevant Problems

- **Codeforces 1097F** — Bitmask DP (submask enumeration)
- **AtCoder ABC 187E** — Careful with GC in large inputs
- **Codeforces 1195C** — Needs fast I/O + avoid boxing to pass in Java

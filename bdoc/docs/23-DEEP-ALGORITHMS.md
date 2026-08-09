# Chapter 23: Deep Algorithms — Mastering the Fundamentals

## What you'll learn

- How each data structure works internally (not just the API)
- Amortized analysis and when average-case matters
- Sorting: the maths behind divide-and-conquer, why comparison sorts can't beat O(n log n)
- Searching: binary search variations, interpolation search, exponential search
- Recursion: how the call stack works, tail recursion, memoization mechanics
- Dynamic programming: state design, space optimisation, bitmask DP
- Graphs: advanced traversals, shortest paths, minimum spanning trees, strongly connected components
- String algorithms: KMP, Rabin-Karp, suffix arrays

---

## PART 1: Data Structures — Under the Hood

## 23.1 Arrays and dynamic arrays

**Static array:** Fixed-size contiguous memory. Access is O(1) because: `address = base + index × elementSize`.

**Dynamic array (ArrayList / Vector):** Starts with capacity N. When full:
1. Allocate new array of size 2N
2. Copy all elements to new array
3. Free old array

```
Appending N elements:
  Most appends: O(1) — just put it at the end
  Occasional resize: O(n) — copy everything

Amortized cost: O(1) per append
  Proof: N appends trigger log₂(N) resizes
  Total copy work: 1 + 2 + 4 + 8 + ... + N = 2N - 1
  Average per element: (2N - 1) / N ≈ 2 = O(1)
```

> **Why double, not grow by 1?** Growing by 1 means N copies for N appends = O(n²) total. Doubling means 2N total copies for N appends = O(n) total = O(1) amortized.

## 23.2 Hash tables — how they really work

A HashMap stores key-value pairs in an array of "buckets":

```
hash("alice") → 7    bucket[7] = ("alice", 100)
hash("bob")   → 3    bucket[3] = ("bob", 200)
hash("carol") → 7    COLLISION! bucket[7] already taken
```

**Collision resolution:**

1. **Chaining** (Java HashMap): Each bucket is a linked list. Collisions just append.
   - Average: O(1) if load factor < 0.75
   - Worst: O(n) if all keys hash to same bucket

2. **Open addressing** (Python dict): Probe next empty slot (linear/quadratic/double hashing)
   - Better cache performance (contiguous memory)
   - Degrades as table fills up

**Load factor** = numEntries / numBuckets. When it exceeds threshold (0.75 in Java):
- Allocate 2× larger table
- Rehash every entry into new table
- O(n) operation, but amortized O(1) per insert

```java
// Why HashMap is O(1) average but O(n) worst case:
// Good hash function → even distribution → short chains → O(1)
// Bad hash function → all keys in one bucket → O(n) linked list scan

// Java 8+ optimisation: when a bucket exceeds 8 entries,
// convert linked list to red-black tree → O(log n) worst case
```

## 23.3 Trees — BST, AVL, Red-Black

**Binary Search Tree (BST):**
- Left child < parent < right child
- Search/Insert/Delete: O(h) where h = height
- Balanced: h = log n → O(log n)
- Degenerate (sorted insert): h = n → O(n) ← same as linked list!

**Self-balancing trees fix this:**

| Tree | Balance rule | Rotation cost | Use case |
|------|-------------|---------------|----------|
| AVL | Height difference ≤ 1 | O(log n) rotations per insert | Lookup-heavy (more strictly balanced) |
| Red-Black | No path is 2× longer than another | O(1) rotations per insert | Insert-heavy (Java TreeMap, C++ map) |
| B-Tree | Multi-way balanced, minimise disk reads | O(log n) | Databases, filesystems |

**Rotations (the key operation):**

```
Right rotation (fix left-heavy):        Left rotation (fix right-heavy):

      Y                X                    X                Y
     / \              / \                  / \              / \
    X   C    →      A    Y                A   Y    →      X   C
   / \                  / \                  / \          / \
  A   B                B   C                B   C        A   B
```

## 23.4 Heaps — the priority queue engine

A **binary heap** is a complete binary tree stored in an array:

```
Array:  [_, 10, 20, 30, 25, 35, 40, 50]  (index 0 unused)

Tree:
           10          index 1
         /    \
       20      30      index 2, 3
      /  \    /  \
    25   35  40   50   index 4, 5, 6, 7

Parent of i:     i / 2
Left child of i: 2 * i
Right child of i: 2 * i + 1
```

**Operations:**

```java
// Insert: add at end, bubble UP
void insert(int val) {
  heap[++size] = val;
  int i = size;
  while (i > 1 && heap[i] < heap[i/2]) {
    swap(heap, i, i/2);
    i = i / 2;
  }
}

// Extract min: remove root, put last at root, bubble DOWN
int extractMin() {
  int min = heap[1];
  heap[1] = heap[size--];
  int i = 1;
  while (2*i <= size) {
    int child = 2*i;
    if (child+1 <= size && heap[child+1] < heap[child]) child++;
    if (heap[i] <= heap[child]) break;
    swap(heap, i, child);
    i = child;
  }
  return min;
}
```

**Build heap from array — O(n) not O(n log n):**
```java
// Heapify from bottom up — leaf nodes are already heaps
for (int i = size/2; i >= 1; i--) {
  siftDown(i);  // O(1) for bottom, O(log n) for top — total is O(n)
}
```

## 23.5 Tries — prefix trees

```
Insert: "cat", "car", "card", "dog"

        (root)
       /      \
      c        d
      |        |
      a        o
     / \       |
    t   r      g
        |
        d

Lookup "car":  root → c → a → r (found, 3 steps = O(word length))
Prefix "ca":   root → c → a (2 matches below: "cat", "car", "card")
```

```java
class TrieNode {
  TrieNode[] children = new TrieNode[26]; // a-z
  boolean isEndOfWord;
}

class Trie {
  TrieNode root = new TrieNode();

  void insert(String word) {
    TrieNode node = root;
    for (char c : word.toCharArray()) {
      int idx = c - 'a';
      if (node.children[idx] == null) node.children[idx] = new TrieNode();
      node = node.children[idx];
    }
    node.isEndOfWord = true;
  }

  boolean search(String word) {
    TrieNode node = traverse(word);
    return node != null && node.isEndOfWord;
  }

  boolean startsWith(String prefix) {
    return traverse(prefix) != null;
  }

  private TrieNode traverse(String s) {
    TrieNode node = root;
    for (char c : s.toCharArray()) {
      node = node.children[c - 'a'];
      if (node == null) return null;
    }
    return node;
  }
}
```

## 23.6 Union-Find (Disjoint Set Union)

Tracks connected components. Two operations:
- `find(x)` — which component is x in?
- `union(x, y)` — merge x's and y's components

```java
class UnionFind {
  int[] parent, rank;

  UnionFind(int n) {
    parent = new int[n];
    rank = new int[n];
    for (int i = 0; i < n; i++) parent[i] = i;
  }

  int find(int x) {
    if (parent[x] != x) {
      parent[x] = find(parent[x]); // path compression
    }
    return parent[x];
  }

  void union(int x, int y) {
    int px = find(x), py = find(y);
    if (px == py) return;
    if (rank[px] < rank[py]) { parent[px] = py; }
    else if (rank[px] > rank[py]) { parent[py] = px; }
    else { parent[py] = px; rank[px]++; }
  }

  boolean connected(int x, int y) {
    return find(x) == find(y);
  }
}
```

With path compression + union by rank: O(α(n)) per operation ≈ O(1) in practice.

---

## PART 2: Advanced Sorting & Searching

## 23.7 Why comparison sorts can't beat O(n log n)

Any comparison-based sort makes binary decisions (a < b?). With n elements, there are n! possible orderings. A decision tree needs at least log₂(n!) leaves:

```
log₂(n!) ≈ n log₂(n) — by Stirling's approximation
```

Therefore any comparison sort needs Ω(n log n) comparisons in the worst case. This is a mathematical lower bound — no algorithm can beat it.

**Non-comparison sorts CAN beat O(n log n):**
- Counting Sort — O(n + k) where k = range of values
- Radix Sort — O(d × (n + b)) where d = digits, b = base
- Bucket Sort — O(n) average for uniformly distributed data

## 23.8 Quick Sort — deep dive

```java
void quickSort(int[] arr, int lo, int hi) {
  if (lo >= hi) return;
  int pivotIdx = partition(arr, lo, hi);
  quickSort(arr, lo, pivotIdx - 1);
  quickSort(arr, pivotIdx + 1, hi);
}

int partition(int[] arr, int lo, int hi) {
  int pivot = arr[hi]; // last element as pivot
  int i = lo - 1;      // boundary of "less than pivot" section

  for (int j = lo; j < hi; j++) {
    if (arr[j] <= pivot) {
      i++;
      swap(arr, i, j);
    }
  }
  swap(arr, i + 1, hi); // put pivot in correct position
  return i + 1;
}
```

**Why O(n²) worst case?** If pivot is always the smallest or largest element (sorted input + last-element pivot), one partition has n-1 elements → n + (n-1) + (n-2) + ... = O(n²).

**Fixes:**
- Random pivot: `swap(arr, lo + random.nextInt(hi-lo+1), hi)` before partition
- Median-of-three: pick median of first, middle, last element
- Three-way partition (Dutch National Flag): handles many duplicates efficiently

## 23.9 Merge Sort — guaranteed O(n log n)

```java
void mergeSort(int[] arr, int lo, int hi) {
  if (lo >= hi) return;
  int mid = lo + (hi - lo) / 2;
  mergeSort(arr, lo, mid);
  mergeSort(arr, mid + 1, hi);
  merge(arr, lo, mid, hi);
}

void merge(int[] arr, int lo, int mid, int hi) {
  int[] temp = new int[hi - lo + 1];
  int i = lo, j = mid + 1, k = 0;

  while (i <= mid && j <= hi) {
    if (arr[i] <= arr[j]) temp[k++] = arr[i++];
    else temp[k++] = arr[j++];
  }
  while (i <= mid) temp[k++] = arr[i++];
  while (j <= hi) temp[k++] = arr[j++];

  System.arraycopy(temp, 0, arr, lo, temp.length);
}
```

**Recurrence:** T(n) = 2T(n/2) + O(n) → O(n log n) by Master Theorem.

**Applications beyond sorting:**
- Count inversions (how "unsorted" is an array)
- External sorting (sort data too large for RAM)
- Finding closest pair of points

## 23.10 Binary search variations

```java
// Standard: find exact target
int binarySearch(int[] arr, int target) { ... }

// Find leftmost (first occurrence)
int leftmost(int[] arr, int target) {
  int lo = 0, hi = arr.length - 1, result = -1;
  while (lo <= hi) {
    int mid = lo + (hi - lo) / 2;
    if (arr[mid] >= target) { result = mid; hi = mid - 1; }
    else lo = mid + 1;
  }
  return (result != -1 && arr[result] == target) ? result : -1;
}

// Find rightmost (last occurrence)
int rightmost(int[] arr, int target) {
  int lo = 0, hi = arr.length - 1, result = -1;
  while (lo <= hi) {
    int mid = lo + (hi - lo) / 2;
    if (arr[mid] <= target) { result = mid; lo = mid + 1; }
    else hi = mid - 1;
  }
  return (result != -1 && arr[result] == target) ? result : -1;
}

// Find insertion point (where target would go)
int lowerBound(int[] arr, int target) {
  int lo = 0, hi = arr.length;
  while (lo < hi) {
    int mid = lo + (hi - lo) / 2;
    if (arr[mid] < target) lo = mid + 1;
    else hi = mid;
  }
  return lo;
}
```

---

## PART 3: Dynamic Programming — Deep Dive

## 23.11 DP state design

The hardest part of DP is defining `dp[i]`. Common patterns:

| State definition | Example problems |
|-----------------|-----------------|
| `dp[i]` = answer using first i elements | House Robber, Climbing Stairs |
| `dp[i][j]` = answer using elements i..j | Burst Balloons, Matrix Chain |
| `dp[i][j]` = answer for string1[0..i] vs string2[0..j] | Edit Distance, LCS |
| `dp[i][w]` = answer using first i items with capacity w | Knapsack |
| `dp[mask]` = answer for subset represented by bitmask | TSP, Assign Tasks |
| `dp[i][k]` = answer at position i with k transactions | Buy/Sell Stock with K transactions |

## 23.12 Space optimisation

Many 2D DP problems only look at the previous row:

```java
// Edit distance — full 2D: O(m×n) space
int[][] dp = new int[m+1][n+1];
for (int i = 1; i <= m; i++)
  for (int j = 1; j <= n; j++)
    dp[i][j] = /* uses dp[i-1][j], dp[i][j-1], dp[i-1][j-1] */

// Optimised — only 2 rows: O(n) space
int[] prev = new int[n+1], curr = new int[n+1];
for (int i = 1; i <= m; i++) {
  for (int j = 1; j <= n; j++)
    curr[j] = /* uses prev[j], curr[j-1], prev[j-1] */
  int[] temp = prev; prev = curr; curr = temp; // swap rows
}
```

**Even 1 row** (when only dp[j-1] and dp[j] needed):
```java
// Knapsack 0/1 — iterate capacity BACKWARDS to avoid using updated values
int[] dp = new int[capacity + 1];
for (int i = 0; i < n; i++)
  for (int w = capacity; w >= weights[i]; w--)  // backwards!
    dp[w] = Math.max(dp[w], dp[w - weights[i]] + values[i]);
```

## 23.13 Bitmask DP

When n is small (≤ 20), represent subsets as integers:

```java
// Travelling Salesman Problem — visit all cities, minimise distance
// dp[mask][i] = minimum cost to visit cities in `mask`, ending at city i
int n = cities.length;
int[][] dp = new int[1 << n][n];
Arrays.fill(dp, Integer.MAX_VALUE);
dp[1][0] = 0; // start at city 0

for (int mask = 1; mask < (1 << n); mask++) {
  for (int last = 0; last < n; last++) {
    if (dp[mask][last] == Integer.MAX_VALUE) continue;
    if ((mask & (1 << last)) == 0) continue; // last must be in mask

    for (int next = 0; next < n; next++) {
      if ((mask & (1 << next)) != 0) continue; // next not yet visited
      int newMask = mask | (1 << next);
      dp[newMask][next] = Math.min(
        dp[newMask][next],
        dp[mask][last] + dist[last][next]
      );
    }
  }
}
```

---

## PART 4: Advanced Graph Algorithms

## 23.14 Dijkstra's algorithm (weighted shortest path)

```java
int[] dijkstra(List<int[]>[] graph, int source) {
  int n = graph.length;
  int[] dist = new int[n];
  Arrays.fill(dist, Integer.MAX_VALUE);
  dist[source] = 0;

  // min-heap: (distance, node)
  PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[0] - b[0]);
  pq.add(new int[]{0, source});

  while (!pq.isEmpty()) {
    int[] curr = pq.poll();
    int d = curr[0], u = curr[1];

    if (d > dist[u]) continue; // stale entry

    for (int[] edge : graph[u]) {
      int v = edge[0], weight = edge[1];
      if (dist[u] + weight < dist[v]) {
        dist[v] = dist[u] + weight;
        pq.add(new int[]{dist[v], v});
      }
    }
  }
  return dist;
}
```

**Doesn't work with negative edges** — use Bellman-Ford instead.

## 23.15 Topological sort (dependency ordering)

```java
// Kahn's algorithm (BFS-based)
List<Integer> topologicalSort(int n, List<int[]> edges) {
  List<List<Integer>> graph = new ArrayList<>();
  int[] inDegree = new int[n];
  for (int i = 0; i < n; i++) graph.add(new ArrayList<>());

  for (int[] e : edges) {
    graph.get(e[0]).add(e[1]);
    inDegree[e[1]]++;
  }

  Queue<Integer> queue = new LinkedList<>();
  for (int i = 0; i < n; i++)
    if (inDegree[i] == 0) queue.add(i);

  List<Integer> order = new ArrayList<>();
  while (!queue.isEmpty()) {
    int node = queue.poll();
    order.add(node);
    for (int neighbor : graph.get(node)) {
      if (--inDegree[neighbor] == 0) queue.add(neighbor);
    }
  }

  return order.size() == n ? order : List.of(); // empty if cycle exists
}
```

## 23.16 Minimum Spanning Tree

```java
// Kruskal's — sort edges, add if no cycle (Union-Find)
int kruskal(int n, int[][] edges) {
  Arrays.sort(edges, (a, b) -> a[2] - b[2]); // sort by weight
  UnionFind uf = new UnionFind(n);
  int totalWeight = 0, edgesUsed = 0;

  for (int[] edge : edges) {
    int u = edge[0], v = edge[1], w = edge[2];
    if (!uf.connected(u, v)) {
      uf.union(u, v);
      totalWeight += w;
      if (++edgesUsed == n - 1) break;
    }
  }
  return totalWeight;
}
```

## 23.17 String algorithms

**KMP (Knuth-Morris-Pratt)** — find pattern in text in O(n + m):

```java
int[] buildKMPTable(String pattern) {
  int[] lps = new int[pattern.length()]; // longest proper prefix-suffix
  int len = 0, i = 1;

  while (i < pattern.length()) {
    if (pattern.charAt(i) == pattern.charAt(len)) {
      lps[i++] = ++len;
    } else if (len > 0) {
      len = lps[len - 1]; // don't increment i
    } else {
      lps[i++] = 0;
    }
  }
  return lps;
}

int kmpSearch(String text, String pattern) {
  int[] lps = buildKMPTable(pattern);
  int i = 0, j = 0;

  while (i < text.length()) {
    if (text.charAt(i) == pattern.charAt(j)) {
      i++; j++;
      if (j == pattern.length()) return i - j; // found
    } else if (j > 0) {
      j = lps[j - 1]; // partial match — don't restart
    } else {
      i++;
    }
  }
  return -1;
}
```

---

## Summary

✅ Data structures internals: dynamic array amortization, hash table collision resolution, heap array representation, trie structure, union-find with path compression
✅ Sorting theory: comparison sort lower bound O(n log n), quicksort pivot strategies, merge sort applications
✅ Binary search variations: leftmost, rightmost, insertion point, search on answer
✅ DP mastery: state design patterns, space optimisation (2-row, 1-row, backwards), bitmask DP
✅ Graph algorithms: Dijkstra, topological sort, Kruskal's MST
✅ String matching: KMP with failure function

## Key takeaway

**Algorithms are about invariants.** Binary search maintains "answer is in [lo, hi]". Dijkstra maintains "shortest distance to visited nodes is final". DP fills a table such that "dp[i] is optimal for subproblem i". Once you identify the invariant, the code follows naturally.

---

→ [Chapter 24: Deep LeetCode Patterns](./24-DEEP-LEETCODE-PATTERNS.md)

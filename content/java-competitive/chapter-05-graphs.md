# Chapter 5: Graph Algorithms

[prev: Math](chapter-04-math.md) | [next: Strings](chapter-06-strings.md)

## Adjacency List Representations

### ArrayList of ArrayList — Easy to use

```java
int n = 100000;
List<List<Integer>> adj = new ArrayList<>();
for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
adj.get(u).add(v);
adj.get(v).add(u);
```

### int[] arrays — Fastest (CSR-style)

For maximum speed, use a compressed sparse row format. Avoids all object overhead:

```java
// Build phase: count degrees, then fill
int[] head = new int[n + 1]; // head[i] = start index of node i's edges
int[] to = new int[2 * m];   // edge targets
int[] nxt = new int[2 * m];  // next edge in list
int edgeCnt = 0;

static void addEdge(int u, int v) {
    to[edgeCnt] = v;
    nxt[edgeCnt] = head[u];
    head[u] = edgeCnt++;
}

// Traverse edges of node u
for (int e = head[u]; e != -1; e = nxt[e]) {
    int v = to[e];
}
```

Initialize `head` with `-1` (Arrays.fill(head, -1)).

**C++ comparison:** C++ `vector<vector<int>>` is already fast due to no boxing. Java needs this trick for tight TLEs.

## BFS — O(V + E)

Always use iterative BFS (ArrayDeque):

```java
static int[] bfs(List<List<Integer>> adj, int src, int n) {
    int[] dist = new int[n];
    Arrays.fill(dist, -1);
    dist[src] = 0;
    Deque<Integer> q = new ArrayDeque<>();
    q.offer(src);
    while (!q.isEmpty()) {
        int u = q.poll();
        for (int v : adj.get(u)) {
            if (dist[v] == -1) {
                dist[v] = dist[u] + 1;
                q.offer(v);
            }
        }
    }
    return dist;
}
```

## DFS — Iterative (Avoid Stack Overflow)

Java's default stack size is ~512KB. For n = 10^5+, recursive DFS causes StackOverflowError. Always use iterative:

```java
static void dfs(List<List<Integer>> adj, int src, int n) {
    boolean[] visited = new boolean[n];
    Deque<Integer> stack = new ArrayDeque<>();
    stack.push(src);
    while (!stack.isEmpty()) {
        int u = stack.pop();
        if (visited[u]) continue;
        visited[u] = true;
        for (int v : adj.get(u)) {
            if (!visited[v]) stack.push(v);
        }
    }
}
```

**Alternative:** Increase stack size with a new Thread:

```java
public static void main(String[] args) {
    new Thread(null, () -> {
        // your solution with recursive DFS
    }, "main", 1 << 26).start(); // 64MB stack
}
```

## Dijkstra — O((V + E) log V)

```java
static long[] dijkstra(List<List<int[]>> adj, int src, int n) {
    long[] dist = new long[n];
    Arrays.fill(dist, Long.MAX_VALUE);
    dist[src] = 0;
    // PriorityQueue of {distance, node}
    PriorityQueue<long[]> pq = new PriorityQueue<>((a, b) -> Long.compare(a[0], b[0]));
    pq.offer(new long[]{0, src});
    while (!pq.isEmpty()) {
        long[] cur = pq.poll();
        long d = cur[0];
        int u = (int) cur[1];
        if (d > dist[u]) continue;
        for (int[] edge : adj.get(u)) {
            int v = edge[0];
            long w = edge[1];
            if (dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
                pq.offer(new long[]{dist[v], v});
            }
        }
    }
    return dist;
}
```

**Performance trick:** Encode (dist, node) as single long to avoid array allocation:

```java
PriorityQueue<Long> pq = new PriorityQueue<>();
pq.offer(0L << 20 | src); // works if node < 2^20
```

## Union-Find (DSU) — O(alpha(n)) per operation

```java
static int[] parent, rank;

static void init(int n) {
    parent = new int[n];
    rank = new int[n];
    for (int i = 0; i < n; i++) parent[i] = i;
}

static int find(int x) {
    while (parent[x] != x) {
        parent[x] = parent[parent[x]]; // path compression (two-pass)
        x = parent[x];
    }
    return x;
}

static boolean union(int a, int b) {
    a = find(a); b = find(b);
    if (a == b) return false;
    if (rank[a] < rank[b]) { int t = a; a = b; b = t; }
    parent[b] = a;
    if (rank[a] == rank[b]) rank[a]++;
    return true;
}
```

## Topological Sort — O(V + E)

Kahn's algorithm (BFS-based):

```java
static int[] topoSort(List<List<Integer>> adj, int n) {
    int[] indegree = new int[n];
    for (int u = 0; u < n; u++)
        for (int v : adj.get(u)) indegree[v]++;

    Deque<Integer> q = new ArrayDeque<>();
    for (int i = 0; i < n; i++)
        if (indegree[i] == 0) q.offer(i);

    int[] order = new int[n];
    int idx = 0;
    while (!q.isEmpty()) {
        int u = q.poll();
        order[idx++] = u;
        for (int v : adj.get(u))
            if (--indegree[v] == 0) q.offer(v);
    }
    return idx == n ? order : null; // null if cycle exists
}
```

## Fenwick Tree (BIT) — O(log n) update and query

```java
static int[] bit;
static int n;

static void update(int i, int delta) {
    for (i++; i <= n; i += i & (-i)) bit[i] += delta;
}

static int query(int i) { // prefix sum [0, i]
    int sum = 0;
    for (i++; i > 0; i -= i & (-i)) sum += bit[i];
    return sum;
}

static int query(int l, int r) { // range sum [l, r]
    return query(r) - (l > 0 ? query(l - 1) : 0);
}
```

## Segment Tree — O(log n) update and query

```java
static int[] tree;
static int n;

static void build(int[] arr) {
    n = arr.length;
    tree = new int[2 * n];
    System.arraycopy(arr, 0, tree, n, n);
    for (int i = n - 1; i > 0; i--) tree[i] = tree[2*i] + tree[2*i+1];
}

static void update(int i, int val) {
    tree[i += n] = val;
    for (i /= 2; i > 0; i /= 2) tree[i] = tree[2*i] + tree[2*i+1];
}

static int query(int l, int r) { // sum [l, r)
    int res = 0;
    for (l += n, r += n; l < r; l /= 2, r /= 2) {
        if ((l & 1) == 1) res += tree[l++];
        if ((r & 1) == 1) res += tree[--r];
    }
    return res;
}
```

This is the iterative bottom-up segment tree — faster than recursive due to no function call overhead.

## Relevant Problems

- **Codeforces 20C** — Dijkstra (path reconstruction)
- **LeetCode 200** — Number of Islands (BFS/DFS)
- **Codeforces 1559D2** — DSU
- **LeetCode 307** — Range Sum Query (BIT or Segment Tree)
- **Codeforces 1354D** — Segment Tree
- **AtCoder ABC 138D** — Topological sort on tree

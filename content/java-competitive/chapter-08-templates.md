# Chapter 8: Contest Templates

[prev: JVM Optimization](chapter-07-optimization.md) | [next: Overview](chapter-00-overview.md)

## Complete Java Contest Template

Copy-paste this at the start of every contest:

```java
import java.io.*;
import java.util.*;

public class Main {
    static BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
    static PrintWriter out = new PrintWriter(new BufferedOutputStream(System.out));
    static StringTokenizer st;

    static String next() throws IOException {
        while (st == null || !st.hasMoreTokens())
            st = new StringTokenizer(br.readLine());
        return st.nextToken();
    }
    static int ni() throws IOException { return Integer.parseInt(next()); }
    static long nl() throws IOException { return Long.parseLong(next()); }
    static int[] nia(int n) throws IOException {
        int[] a = new int[n];
        for (int i = 0; i < n; i++) a[i] = ni();
        return a;
    }

    static final int MOD = 1_000_000_007;

    public static void main(String[] args) throws IOException {
        int t = ni();
        while (t-- > 0) solve();
        out.flush();
    }

    static void solve() throws IOException {
        int n = ni();
        int[] a = nia(n);
        // solution here
    }
}
```

## Utility Methods

```java
static long gcd(long a, long b) {
    while (b != 0) { long t = b; b = a % b; a = t; }
    return a;
}

static long lcm(long a, long b) { return a / gcd(a, b) * b; }

static long modpow(long base, long exp, long mod) {
    long res = 1;
    base %= mod;
    while (exp > 0) {
        if ((exp & 1) == 1) res = res * base % mod;
        base = base * base % mod;
        exp >>= 1;
    }
    return res;
}

static long modinv(long a, long mod) { return modpow(a, mod - 2, mod); }

static long[] fact, invFact;
static void precomputeFactorials(int n) {
    fact = new long[n + 1];
    invFact = new long[n + 1];
    fact[0] = 1;
    for (int i = 1; i <= n; i++) fact[i] = fact[i - 1] * i % MOD;
    invFact[n] = modpow(fact[n], MOD - 2, MOD);
    for (int i = n - 1; i >= 0; i--) invFact[i] = invFact[i + 1] * (i + 1) % MOD;
}

static long nCr(int n, int r) {
    if (r < 0 || r > n) return 0;
    return fact[n] % MOD * invFact[r] % MOD * invFact[n - r] % MOD;
}
```

## DSU (Disjoint Set Union) Template

```java
static int[] par, rnk, sz;

static void dsuInit(int n) {
    par = new int[n]; rnk = new int[n]; sz = new int[n];
    for (int i = 0; i < n; i++) { par[i] = i; sz[i] = 1; }
}

static int find(int x) {
    while (par[x] != x) { par[x] = par[par[x]]; x = par[x]; }
    return x;
}

static boolean unite(int a, int b) {
    a = find(a); b = find(b);
    if (a == b) return false;
    if (rnk[a] < rnk[b]) { int t = a; a = b; b = t; }
    par[b] = a; sz[a] += sz[b];
    if (rnk[a] == rnk[b]) rnk[a]++;
    return true;
}
```

## Segment Tree Template

```java
static int[] seg;
static int segN;

static void segBuild(int[] arr) {
    segN = arr.length;
    seg = new int[2 * segN];
    System.arraycopy(arr, 0, seg, segN, segN);
    for (int i = segN - 1; i > 0; i--) seg[i] = seg[2*i] + seg[2*i+1];
}

static void segUpdate(int i, int val) {
    seg[i += segN] = val;
    for (i /= 2; i > 0; i /= 2) seg[i] = seg[2*i] + seg[2*i+1];
}

static int segQuery(int l, int r) { // [l, r)
    int res = 0;
    for (l += segN, r += segN; l < r; l /= 2, r /= 2) {
        if ((l & 1) == 1) res += seg[l++];
        if ((r & 1) == 1) res += seg[--r];
    }
    return res;
}
```

**Lazy propagation** (range update, range query):

```java
static long[] seg2, lazy;
static int segN2;

static void seg2Build(int n) {
    segN2 = n;
    seg2 = new long[4 * n];
    lazy = new long[4 * n];
}

static void push(int v) {
    if (lazy[v] != 0) {
        seg2[2*v] += lazy[v]; lazy[2*v] += lazy[v];
        seg2[2*v+1] += lazy[v]; lazy[2*v+1] += lazy[v];
        lazy[v] = 0;
    }
}

static void seg2Update(int v, int tl, int tr, int l, int r, long val) {
    if (l > tr || r < tl) return;
    if (l <= tl && tr <= r) { seg2[v] += val; lazy[v] += val; return; }
    push(v);
    int tm = (tl + tr) / 2;
    seg2Update(2*v, tl, tm, l, r, val);
    seg2Update(2*v+1, tm+1, tr, l, r, val);
    seg2[v] = Math.max(seg2[2*v], seg2[2*v+1]);
}

static long seg2Query(int v, int tl, int tr, int l, int r) {
    if (l > tr || r < tl) return Long.MIN_VALUE;
    if (l <= tl && tr <= r) return seg2[v];
    push(v);
    int tm = (tl + tr) / 2;
    return Math.max(seg2Query(2*v, tl, tm, l, r), seg2Query(2*v+1, tm+1, tr, l, r));
}
```

## Graph Template

```java
// Adjacency list with edge weights
static int[] head, to, nxt, wt;
static int edgeCnt;

static void graphInit(int n, int m) {
    head = new int[n]; Arrays.fill(head, -1);
    to = new int[2 * m]; nxt = new int[2 * m]; wt = new int[2 * m];
    edgeCnt = 0;
}

static void addEdge(int u, int v, int w) {
    to[edgeCnt] = v; wt[edgeCnt] = w; nxt[edgeCnt] = head[u]; head[u] = edgeCnt++;
    to[edgeCnt] = u; wt[edgeCnt] = w; nxt[edgeCnt] = head[v]; head[v] = edgeCnt++;
}

// Dijkstra using the graph template
static long[] dijkstra(int src, int n) {
    long[] dist = new long[n];
    Arrays.fill(dist, Long.MAX_VALUE);
    dist[src] = 0;
    PriorityQueue<long[]> pq = new PriorityQueue<>((a, b) -> Long.compare(a[0], b[0]));
    pq.offer(new long[]{0, src});
    while (!pq.isEmpty()) {
        long[] cur = pq.poll();
        int u = (int) cur[1];
        if (cur[0] > dist[u]) continue;
        for (int e = head[u]; e != -1; e = nxt[e]) {
            int v = to[e];
            long nd = dist[u] + wt[e];
            if (nd < dist[v]) { dist[v] = nd; pq.offer(new long[]{nd, v}); }
        }
    }
    return dist;
}
```

## Geometry Template

```java
static final double EPS = 1e-9;

static double cross(double x1, double y1, double x2, double y2) {
    return x1 * y2 - x2 * y1;
}

static double dist(double x1, double y1, double x2, double y2) {
    double dx = x1 - x2, dy = y1 - y2;
    return Math.sqrt(dx * dx + dy * dy);
}

// Convex hull (Andrew's monotone chain) - O(n log n)
static int[][] convexHull(int[][] pts) {
    int n = pts.length;
    Arrays.sort(pts, (a, b) -> a[0] != b[0] ? a[0] - b[0] : a[1] - b[1]);
    int[][] hull = new int[2 * n][2];
    int k = 0;
    for (int i = 0; i < n; i++) {
        while (k >= 2 && cross(hull[k-1][0]-hull[k-2][0], hull[k-1][1]-hull[k-2][1],
                               pts[i][0]-hull[k-2][0], pts[i][1]-hull[k-2][1]) <= 0) k--;
        hull[k++] = pts[i];
    }
    int lower = k + 1;
    for (int i = n - 2; i >= 0; i--) {
        while (k >= lower && cross(hull[k-1][0]-hull[k-2][0], hull[k-1][1]-hull[k-2][1],
                                   pts[i][0]-hull[k-2][0], pts[i][1]-hull[k-2][1]) <= 0) k--;
        hull[k++] = pts[i];
    }
    return Arrays.copyOf(hull, k - 1);
}
```

## Tips for Contest Day

1. **Pre-write your template** — have it ready before the contest starts
2. **Test locally** — compile with `javac Main.java`, run with `java -Xss64m Main`
3. **Use `-Xss64m`** for deep recursion problems
4. **Submit as Java 17** on Codeforces (better JIT than Java 8)
5. **If TLE in Java**, try these in order:
   - Fast I/O (most common fix)
   - Replace HashMap with array-based solution
   - Replace ArrayList with int[][]
   - Encode pairs as long instead of int[]
   - Shuffle before Arrays.sort on primitives

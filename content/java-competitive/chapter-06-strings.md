# Chapter 6: String Performance

[prev: Graphs](chapter-05-graphs.md) | [next: JVM Optimization](chapter-07-optimization.md)

## StringBuilder — Never Concatenate in Loops

String concatenation in a loop creates a new String object each iteration: O(n^2) total.

```java
// BAD - O(n^2) time and memory
String s = "";
for (int i = 0; i < n; i++) s += arr[i] + " ";

// GOOD - O(n)
StringBuilder sb = new StringBuilder();
for (int i = 0; i < n; i++) sb.append(arr[i]).append(' ');
String s = sb.toString();
```

**Pre-size** if you know the approximate length:

```java
StringBuilder sb = new StringBuilder(n * 10);
```

## char[] Manipulation

For character-level operations, `char[]` is faster than String methods:

```java
char[] cs = s.toCharArray();
// Direct manipulation
for (int i = 0; i < cs.length; i++) {
    if (cs[i] >= 'A' && cs[i] <= 'Z') cs[i] += 32; // toLower
}
String result = new String(cs);

// Frequency counting
int[] freq = new int[26];
for (char c : cs) freq[c - 'a']++;
```

**C++ comparison:** C++ strings are mutable. Java strings are immutable — always convert to `char[]` for in-place work.

## Polynomial Rolling Hash — O(n) build, O(1) substring hash

```java
static final long MOD1 = 1_000_000_007L;
static final long BASE1 = 131;

static long[] hash, pw;

static void buildHash(char[] s) {
    int n = s.length;
    hash = new long[n + 1];
    pw = new long[n + 1];
    pw[0] = 1;
    for (int i = 0; i < n; i++) {
        hash[i + 1] = (hash[i] * BASE1 + s[i]) % MOD1;
        pw[i + 1] = pw[i] * BASE1 % MOD1;
    }
}

// Hash of s[l..r] (0-indexed, inclusive)
static long getHash(int l, int r) {
    return (hash[r + 1] - hash[l] * pw[r - l + 1] % MOD1 + MOD1 * MOD1) % MOD1;
}
```

**Double hash** to reduce collision probability:

```java
static final long MOD2 = 998_244_353L;
static final long BASE2 = 137;
// Build second hash array similarly, compare both
```

Use double hashing when n is large (10^5+) or adversarial tests are possible.

## KMP (Knuth-Morris-Pratt) — O(n + m)

Pattern matching without backtracking:

```java
// Build failure function
static int[] kmpFailure(char[] pattern) {
    int m = pattern.length;
    int[] fail = new int[m];
    for (int i = 1, j = 0; i < m; i++) {
        while (j > 0 && pattern[i] != pattern[j]) j = fail[j - 1];
        if (pattern[i] == pattern[j]) j++;
        fail[i] = j;
    }
    return fail;
}

// Find all occurrences of pattern in text
static List<Integer> kmpSearch(char[] text, char[] pattern) {
    int[] fail = kmpFailure(pattern);
    List<Integer> matches = new ArrayList<>();
    for (int i = 0, j = 0; i < text.length; i++) {
        while (j > 0 && text[i] != pattern[j]) j = fail[j - 1];
        if (text[i] == pattern[j]) j++;
        if (j == pattern.length) {
            matches.add(i - j + 1);
            j = fail[j - 1];
        }
    }
    return matches;
}
```

## Z-Algorithm — O(n)

Z[i] = length of longest substring starting at i that matches a prefix of the string.

```java
static int[] zFunction(char[] s) {
    int n = s.length;
    int[] z = new int[n];
    int l = 0, r = 0;
    for (int i = 1; i < n; i++) {
        if (i < r) z[i] = Math.min(r - i, z[i - l]);
        while (i + z[i] < n && s[z[i]] == s[i + z[i]]) z[i]++;
        if (i + z[i] > r) { l = i; r = i + z[i]; }
    }
    return z;
}

// Pattern matching: concatenate pattern + "$" + text, find z[i] == m
```

## Trie — O(L) per operation

```java
static int[][] trie = new int[MAX_NODES][26];
static boolean[] isEnd = new boolean[MAX_NODES];
static int trieSize = 1; // root = 0

static void insert(char[] s) {
    int cur = 0;
    for (char c : s) {
        int idx = c - 'a';
        if (trie[cur][idx] == 0) trie[cur][idx] = trieSize++;
        cur = trie[cur][idx];
    }
    isEnd[cur] = true;
}

static boolean search(char[] s) {
    int cur = 0;
    for (char c : s) {
        int idx = c - 'a';
        if (trie[cur][idx] == 0) return false;
        cur = trie[cur][idx];
    }
    return isEnd[cur];
}
```

**Performance:** Array-based trie is much faster than HashMap-based (no boxing, cache-friendly). Pre-allocate MAX_NODES based on total character count.

## Suffix Array Basics — O(n log n)

```java
static int[] suffixArray(char[] s) {
    int n = s.length;
    Integer[] order = new Integer[n];
    for (int i = 0; i < n; i++) order[i] = i;
    int[] rank = new int[n], tmp = new int[n];
    for (int i = 0; i < n; i++) rank[i] = s[i];

    for (int k = 1; k < n; k <<= 1) {
        final int kk = k;
        final int[] r = rank;
        Arrays.sort(order, (a, b) -> r[a] != r[b] ? r[a] - r[b]
            : (a + kk < n && b + kk < n ? r[a + kk] - r[b + kk]
            : (a + kk >= n ? -1 : 1)));
        tmp[order[0]] = 0;
        for (int i = 1; i < n; i++) {
            tmp[order[i]] = tmp[order[i-1]];
            if (r[order[i]] != r[order[i-1]] ||
                (order[i]+kk < n && order[i-1]+kk < n ? r[order[i]+kk] != r[order[i-1]+kk] : true))
                tmp[order[i]]++;
        }
        System.arraycopy(tmp, 0, rank, 0, n);
    }
    int[] sa = new int[n];
    for (int i = 0; i < n; i++) sa[i] = order[i];
    return sa;
}
```

For competitive programming, suffix array + LCP array solves many string problems efficiently.

## Relevant Problems

- **LeetCode 28** — Find the Index (KMP)
- **Codeforces 126B** — Z-function (longest prefix-suffix)
- **LeetCode 208** — Implement Trie
- **Codeforces 271D** — String hashing
- **AtCoder ABC 141E** — Suffix array / hashing

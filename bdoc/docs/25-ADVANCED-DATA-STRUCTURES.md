# Chapter 25: Advanced Data Structures — Beyond the Basics

## What you'll learn

- Segment trees (range queries + point updates in O(log n))
- Fenwick trees / Binary Indexed Trees (simpler range-sum)
- LRU Cache (HashMap + Doubly Linked List)
- Skip Lists (probabilistic balanced structure)
- Bloom Filters (probabilistic membership testing)
- Persistent data structures (immutable with history)
- Disjoint sparse tables, suffix arrays
- When to use each — real-world applications

---

## 25.1 Segment Tree — range queries + point updates

**Problem:** Given an array, support:
- `query(l, r)` — sum/min/max of elements in range [l, r]
- `update(i, val)` — change element at index i

**Naive:** query O(n), update O(1). Can we do O(log n) for both?

```
Array: [1, 3, 5, 7, 2, 4, 6, 8]

Segment tree (stores range sums):

                    [36]              sum(0..7)
                /          \
           [16]              [20]     sum(0..3), sum(4..7)
          /    \            /    \
       [4]     [12]     [6]     [14]  sum(0..1), sum(2..3), etc.
      /  \    /   \    /  \    /  \
    [1] [3] [5]  [7] [2] [4] [6] [8]  leaves = original array
```

**Implementation:**

```java
class SegmentTree {
    int[] tree;
    int n;

    SegmentTree(int[] arr) {
        n = arr.length;
        tree = new int[4 * n]; // safe upper bound
        build(arr, 1, 0, n - 1);
    }

    void build(int[] arr, int node, int start, int end) {
        if (start == end) {
            tree[node] = arr[start];
            return;
        }
        int mid = (start + end) / 2;
        build(arr, 2 * node, start, mid);
        build(arr, 2 * node + 1, mid + 1, end);
        tree[node] = tree[2 * node] + tree[2 * node + 1]; // merge
    }

    // Point update: set arr[idx] = val
    void update(int node, int start, int end, int idx, int val) {
        if (start == end) {
            tree[node] = val;
            return;
        }
        int mid = (start + end) / 2;
        if (idx <= mid) update(2 * node, start, mid, idx, val);
        else update(2 * node + 1, mid + 1, end, idx, val);
        tree[node] = tree[2 * node] + tree[2 * node + 1]; // recompute
    }

    // Range query: sum of arr[l..r]
    int query(int node, int start, int end, int l, int r) {
        if (r < start || end < l) return 0;           // no overlap
        if (l <= start && end <= r) return tree[node]; // full overlap
        int mid = (start + end) / 2;
        return query(2 * node, start, mid, l, r) +
               query(2 * node + 1, mid + 1, end, l, r);
    }

    // Public API
    void update(int idx, int val) { update(1, 0, n - 1, idx, val); }
    int query(int l, int r) { return query(1, 0, n - 1, l, r); }
}
```

**Lazy propagation** (range updates in O(log n)):
- Problem: update ALL elements in [l, r] by +val
- Solution: mark nodes as "pending update", push down lazily when queried

```java
void updateRange(int node, int start, int end, int l, int r, int val) {
    if (lazy[node] != 0) pushDown(node, start, end);
    if (r < start || end < l) return;
    if (l <= start && end <= r) {
        tree[node] += (end - start + 1) * val;
        if (start != end) { lazy[2*node] += val; lazy[2*node+1] += val; }
        return;
    }
    int mid = (start + end) / 2;
    updateRange(2*node, start, mid, l, r, val);
    updateRange(2*node+1, mid+1, end, l, r, val);
    tree[node] = tree[2*node] + tree[2*node+1];
}
```

**Use cases:**
- Range sum/min/max queries with updates
- Count of elements in a range
- Interval scheduling
- 2D segment trees for matrix queries

## 25.2 Fenwick Tree (Binary Indexed Tree)

Simpler than segment tree, handles prefix sums + point updates:

```java
class FenwickTree {
    int[] bit;
    int n;

    FenwickTree(int n) {
        this.n = n;
        bit = new int[n + 1]; // 1-indexed
    }

    // Add val to index i
    void update(int i, int val) {
        for (i++; i <= n; i += i & (-i))
            bit[i] += val;
    }

    // Prefix sum [0, i]
    int query(int i) {
        int sum = 0;
        for (i++; i > 0; i -= i & (-i))
            sum += bit[i];
        return sum;
    }

    // Range sum [l, r]
    int query(int l, int r) {
        return query(r) - (l > 0 ? query(l - 1) : 0);
    }
}
```

**How `i & (-i)` works:** extracts the lowest set bit.
- `i = 12 (1100)` → `i & (-i) = 4 (0100)`
- This determines the "responsibility range" of each index

| | Segment Tree | Fenwick Tree |
|---|---|---|
| Range query | ✅ Any associative op | ✅ Prefix-based only (sum, XOR) |
| Point update | ✅ | ✅ |
| Range update | ✅ (lazy) | Limited (with tricks) |
| Code complexity | Higher | Lower |
| Constant factor | Larger | Smaller (2-5× faster) |

## 25.3 LRU Cache — HashMap + Doubly Linked List

LeetCode #146 — one of the most asked design problems.

```java
class LRUCache {
    private final int capacity;
    private final Map<Integer, Node> map;
    private final Node head, tail; // dummy sentinels

    static class Node {
        int key, value;
        Node prev, next;
        Node(int k, int v) { key = k; value = v; }
    }

    public LRUCache(int capacity) {
        this.capacity = capacity;
        map = new HashMap<>();
        head = new Node(0, 0);
        tail = new Node(0, 0);
        head.next = tail;
        tail.prev = head;
    }

    public int get(int key) {
        if (!map.containsKey(key)) return -1;
        Node node = map.get(key);
        moveToFront(node); // recently used → front
        return node.value;
    }

    public void put(int key, int value) {
        if (map.containsKey(key)) {
            Node node = map.get(key);
            node.value = value;
            moveToFront(node);
        } else {
            if (map.size() == capacity) {
                // Evict least recently used (tail)
                Node lru = tail.prev;
                remove(lru);
                map.remove(lru.key);
            }
            Node node = new Node(key, value);
            map.put(key, node);
            addToFront(node);
        }
    }

    private void addToFront(Node node) {
        node.next = head.next;
        node.prev = head;
        head.next.prev = node;
        head.next = node;
    }

    private void remove(Node node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
    }

    private void moveToFront(Node node) {
        remove(node);
        addToFront(node);
    }
}
```

**Why this combination?**
- HashMap: O(1) lookup by key
- Doubly Linked List: O(1) insert/remove at any position + maintains order
- Together: O(1) get + O(1) put + LRU eviction

## 25.4 Skip List — probabilistic balanced structure

A skip list is a linked list with "express lanes":

```
Level 3:  HEAD ─────────────────────────────── 50 ───── TAIL
Level 2:  HEAD ────── 20 ────────────── 40 ── 50 ───── TAIL
Level 1:  HEAD ── 10 ─ 20 ── 30 ── 35 ─ 40 ── 50 ── 60 TAIL
Level 0:  HEAD ── 10 ─ 20 ── 30 ── 35 ─ 40 ── 50 ── 60 TAIL (all elements)
```

**Search "35":** Start at top-left, go right until overshoot, drop down, repeat.
- Level 3: HEAD → 50 (too far) → drop
- Level 2: HEAD → 20 → 40 (too far) → drop to 20
- Level 1: 20 → 30 → 35 ✓ Found!

**Expected O(log n)** for search, insert, delete — same as balanced BST, but simpler to implement.

**Used in:** Redis sorted sets, LevelDB/RocksDB, Lucene.

```java
class SkipList {
    private static final int MAX_LEVEL = 16;
    private static final double P = 0.5;
    private final Node head = new Node(Integer.MIN_VALUE, MAX_LEVEL);
    private int level = 0;

    static class Node {
        int val;
        Node[] next;
        Node(int val, int level) {
            this.val = val;
            next = new Node[level + 1];
        }
    }

    private int randomLevel() {
        int lvl = 0;
        while (Math.random() < P && lvl < MAX_LEVEL) lvl++;
        return lvl;
    }

    boolean search(int target) {
        Node curr = head;
        for (int i = level; i >= 0; i--)
            while (curr.next[i] != null && curr.next[i].val < target)
                curr = curr.next[i];
        curr = curr.next[0];
        return curr != null && curr.val == target;
    }

    void add(int val) {
        Node[] update = new Node[MAX_LEVEL + 1];
        Node curr = head;
        for (int i = level; i >= 0; i--) {
            while (curr.next[i] != null && curr.next[i].val < val)
                curr = curr.next[i];
            update[i] = curr;
        }

        int newLevel = randomLevel();
        if (newLevel > level) {
            for (int i = level + 1; i <= newLevel; i++) update[i] = head;
            level = newLevel;
        }

        Node newNode = new Node(val, newLevel);
        for (int i = 0; i <= newLevel; i++) {
            newNode.next[i] = update[i].next[i];
            update[i].next[i] = newNode;
        }
    }
}
```

## 25.5 Bloom Filter — probabilistic membership

"Is this element in the set?" — answers YES (maybe) or NO (definitely).

```
False positives possible: says "yes" but element isn't there
False negatives impossible: if it says "no", element definitely isn't there
```

**How it works:**
1. A bit array of size m, all zeros initially
2. k hash functions
3. Insert: compute k hashes, set those bits to 1
4. Query: compute k hashes, if ALL bits are 1 → "probably yes", if any bit is 0 → "definitely no"

```java
class BloomFilter {
    private final BitSet bits;
    private final int size;
    private final int numHashes;

    BloomFilter(int expectedElements, double falsePositiveRate) {
        // Optimal size and hash count
        size = (int) (-expectedElements * Math.log(falsePositiveRate) / (Math.log(2) * Math.log(2)));
        numHashes = (int) (size / expectedElements * Math.log(2));
        bits = new BitSet(size);
    }

    void add(String element) {
        for (int i = 0; i < numHashes; i++)
            bits.set(hash(element, i) % size);
    }

    boolean mightContain(String element) {
        for (int i = 0; i < numHashes; i++)
            if (!bits.get(hash(element, i) % size)) return false;
        return true; // probably contains
    }

    private int hash(String element, int seed) {
        return Math.abs((element.hashCode() * (seed + 1) * 31) + seed);
    }
}
```

**Use cases:**
- Database: check if key exists before expensive disk read (HBase, Cassandra)
- Web: is this URL in the crawled set? (Google crawler)
- Network: has this packet been seen before? (deduplication)
- Cache: avoid looking up keys that definitely don't exist

## 25.6 Interval Tree

Store intervals, query "which intervals overlap point X?" in O(log n + k):

```java
// Simplified — stores intervals sorted by start, BST on midpoint
class IntervalTree {
    // Used for: calendar conflicts, IP range lookup, genome range queries
    // LeetCode: My Calendar, Insert Interval, Meeting Rooms
}
```

**Real-world use:** Database indexing (PostgreSQL range types), network routing (IP ranges), computational geometry.

## 25.7 Comparison table

| Structure | Key operation | Time | Space | Use case |
|-----------|--------------|------|-------|----------|
| Segment Tree | Range query + point update | O(log n) | O(n) | Range min/max/sum with updates |
| Fenwick Tree | Prefix sum + point update | O(log n) | O(n) | Simpler range sums |
| LRU Cache | Get + Put with eviction | O(1) | O(n) | Caching, page replacement |
| Skip List | Search + Insert + Delete | O(log n) avg | O(n) | Concurrent sorted structures |
| Bloom Filter | Add + MightContain | O(k) | O(m) bits | Probabilistic membership |
| Trie | Prefix search | O(m) | O(ALPHABET × nodes) | Autocomplete, spell check |
| Interval Tree | Overlap query | O(log n + k) | O(n) | Calendar, IP ranges |

---

## Summary

✅ Segment Tree: range queries with lazy propagation for range updates
✅ Fenwick Tree: lighter alternative for prefix-based operations
✅ LRU Cache: HashMap + DoublyLinkedList for O(1) cache with eviction
✅ Skip List: probabilistic balanced structure (simpler than red-black trees)
✅ Bloom Filter: space-efficient probabilistic membership testing
✅ When to use each structure based on the problem's access pattern

## Key takeaway

**Advanced data structures exist because basic ones have specific weaknesses.** Arrays can't do fast range queries. HashMaps can't maintain order. BSTs are complex to balance. Each advanced structure solves a specific pain point — know the pain point, and the right structure becomes obvious.

---

→ [Chapter 26: Java Concurrency](./26-JAVA-CONCURRENCY.md)

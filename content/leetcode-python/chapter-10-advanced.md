# Chapter 10: Advanced Topics

[← Greedy & Intervals](./chapter-09-greedy.md) | [Overview →](./chapter-00-overview.md)

---

## Trie (Prefix Tree)

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for c in word:
            if c not in node.children:
                node.children[c] = TrieNode()
            node = node.children[c]
        node.is_end = True

    def search(self, word):
        node = self._find(word)
        return node is not None and node.is_end

    def startsWith(self, prefix):
        return self._find(prefix) is not None

    def _find(self, prefix):
        node = self.root
        for c in prefix:
            if c not in node.children:
                return None
            node = node.children[c]
        return node
```

---

## Union-Find (Disjoint Set)

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True
```

---

## Problem 1: Implement Trie (Medium) — LC 208

(See Trie implementation above)

**Complexity:** O(m) per operation where m = word length. O(total chars) space.

---

## Problem 2: Word Search II (Hard) — LC 212

**Given:** Board of chars and list of words, find all words on the board.

```python
def findWords(board, words):
    root = {}
    for word in words:
        node = root
        for c in word:
            node = node.setdefault(c, {})
        node['#'] = word

    rows, cols = len(board), len(board[0])
    res = []

    def dfs(r, c, node):
        c_char = board[r][c]
        if c_char not in node:
            return
        node = node[c_char]
        if '#' in node:
            res.append(node.pop('#'))
        board[r][c] = '.'
        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != '.':
                dfs(nr, nc, node)
        board[r][c] = c_char

    for r in range(rows):
        for c in range(cols):
            dfs(r, c, root)
    return res
```

**Complexity:** O(m·n · 4^L) time where L = max word length.

---

## Problem 3: Number of Connected Components (Medium) — LC 323

```python
def countComponents(n, edges):
    uf = UnionFind(n)
    components = n
    for u, v in edges:
        if uf.union(u, v):
            components -= 1
    return components
```

**Complexity:** O(E · α(n)) ≈ O(E) time, O(n) space.

---

## Problem 4: Accounts Merge (Medium) — LC 721

```python
from collections import defaultdict

def accountsMerge(accounts):
    uf = UnionFind(len(accounts))
    email_to_id = {}

    for i, acc in enumerate(accounts):
        for email in acc[1:]:
            if email in email_to_id:
                uf.union(i, email_to_id[email])
            email_to_id[email] = i

    groups = defaultdict(set)
    for email, i in email_to_id.items():
        groups[uf.find(i)].add(email)

    return [[accounts[i][0]] + sorted(emails) for i, emails in groups.items()]
```

**Complexity:** O(n · k · α(n·k)) time where k = max emails per account.

---

## Problem 5: Design a System for Contest Strategy

### Contest Time Management

```python
# Priority: Easy (0-10 min) → Medium (15-25 min) → Hard (30-45 min)
# Total: 90 minutes for 4 problems

# Strategy:
# 1. Read ALL problems first (2 min)
# 2. Solve Easy immediately
# 3. Identify which Medium/Hard you recognize patterns for
# 4. Skip if stuck > 5 min, come back later
```

### Common Contest Patterns

| Technique           | When to Use                        |
| ------------------- | ---------------------------------- |
| Trie                | Prefix matching, XOR maximization  |
| Union-Find          | Dynamic connectivity, grouping     |
| Segment Tree        | Range queries with updates         |
| Binary Indexed Tree | Prefix sums with point updates     |
| Bitmask DP          | Small n (≤ 20), subset enumeration |

### Segment Tree (Range Sum with Point Update)

```python
class SegTree:
    def __init__(self, n):
        self.n = n
        self.tree = [0] * (2 * n)

    def update(self, i, val):
        i += self.n
        self.tree[i] = val
        while i > 1:
            i //= 2
            self.tree[i] = self.tree[2*i] + self.tree[2*i+1]

    def query(self, l, r):  # [l, r)
        res = 0
        l += self.n
        r += self.n
        while l < r:
            if l & 1:
                res += self.tree[l]
                l += 1
            if r & 1:
                r -= 1
                res += self.tree[r]
            l //= 2
            r //= 2
        return res
```

---

## Pattern Recognition Tips

| Signal                                | Pattern            |
| ------------------------------------- | ------------------ |
| "Prefix search / autocomplete"        | Trie               |
| "Dynamic connectivity / merge groups" | Union-Find         |
| "Range query + point update"          | Segment Tree / BIT |
| "All subsets of size ≤ 20"            | Bitmask DP         |
| "Maximum XOR"                         | Trie on bits       |

---

[← Greedy & Intervals](./chapter-09-greedy.md) | [Overview →](./chapter-00-overview.md)

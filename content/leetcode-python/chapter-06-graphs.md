# Chapter 6: Graphs

[← Binary Trees](./chapter-05-trees.md) | [next →](./chapter-07-dynamic-programming.md)

---

## Patterns

### DFS on Graph

```python
def dfs(graph, node, visited):
    visited.add(node)
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited)
```

### BFS (Shortest Path in Unweighted Graph)

```python
from collections import deque

def bfs(graph, start):
    queue = deque([(start, 0)])
    visited = {start}
    while queue:
        node, dist = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))
```

### Topological Sort (Kahn's Algorithm)

```python
from collections import deque, defaultdict

def topo_sort(num_nodes, edges):
    graph = defaultdict(list)
    indegree = [0] * num_nodes
    for u, v in edges:
        graph[u].append(v)
        indegree[v] += 1
    queue = deque(i for i in range(num_nodes) if indegree[i] == 0)
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for nei in graph[node]:
            indegree[nei] -= 1
            if indegree[nei] == 0:
                queue.append(nei)
    return order if len(order) == num_nodes else []  # empty = cycle
```

---

## Problem 1: Number of Islands (Medium) — LC 200

```python
def numIslands(grid):
    rows, cols = len(grid), len(grid[0])
    count = 0

    def dfs(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] != '1':
            return
        grid[r][c] = '0'
        dfs(r+1, c); dfs(r-1, c); dfs(r, c+1); dfs(r, c-1)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                dfs(r, c)
                count += 1
    return count
```

**Complexity:** O(m·n) time, O(m·n) space (recursion stack worst case).

---

## Problem 2: Clone Graph (Medium) — LC 133

```python
def cloneGraph(node):
    if not node:
        return None
    clones = {}

    def dfs(n):
        if n in clones:
            return clones[n]
        clone = Node(n.val)
        clones[n] = clone
        for nei in n.neighbors:
            clone.neighbors.append(dfs(nei))
        return clone

    return dfs(node)
```

**Complexity:** O(V + E) time, O(V) space.

---

## Problem 3: Course Schedule (Medium) — LC 207

**Given:** numCourses and prerequisites, determine if all courses can be finished (cycle detection).

```python
from collections import deque, defaultdict

def canFinish(numCourses, prerequisites):
    graph = defaultdict(list)
    indegree = [0] * numCourses
    for a, b in prerequisites:
        graph[b].append(a)
        indegree[a] += 1
    queue = deque(i for i in range(numCourses) if indegree[i] == 0)
    count = 0
    while queue:
        node = queue.popleft()
        count += 1
        for nei in graph[node]:
            indegree[nei] -= 1
            if indegree[nei] == 0:
                queue.append(nei)
    return count == numCourses
```

**Complexity:** O(V + E) time, O(V + E) space.

---

## Problem 4: Word Ladder (Hard) — LC 127

**Given:** Transform beginWord to endWord, changing one letter at a time, using words from wordList.

```python
from collections import deque

def ladderLength(beginWord, endWord, wordList):
    word_set = set(wordList)
    if endWord not in word_set:
        return 0
    queue = deque([(beginWord, 1)])
    visited = {beginWord}
    while queue:
        word, steps = queue.popleft()
        for i in range(len(word)):
            for c in 'abcdefghijklmnopqrstuvwxyz':
                next_word = word[:i] + c + word[i+1:]
                if next_word == endWord:
                    return steps + 1
                if next_word in word_set and next_word not in visited:
                    visited.add(next_word)
                    queue.append((next_word, steps + 1))
    return 0
```

**Complexity:** O(n · m · 26) time, O(n · m) space, where n = words, m = word length.

---

## Problem 5: Alien Dictionary (Hard) — LC 269

**Given:** Sorted list of words in alien language, derive character order.

```python
from collections import defaultdict, deque

def alienOrder(words):
    graph = defaultdict(set)
    indegree = {c: 0 for w in words for c in w}

    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i+1]
        min_len = min(len(w1), len(w2))
        if len(w1) > len(w2) and w1[:min_len] == w2[:min_len]:
            return ""  # invalid
        for j in range(min_len):
            if w1[j] != w2[j]:
                if w2[j] not in graph[w1[j]]:
                    graph[w1[j]].add(w2[j])
                    indegree[w2[j]] += 1
                break

    queue = deque(c for c in indegree if indegree[c] == 0)
    result = []
    while queue:
        c = queue.popleft()
        result.append(c)
        for nei in graph[c]:
            indegree[nei] -= 1
            if indegree[nei] == 0:
                queue.append(nei)

    return "".join(result) if len(result) == len(indegree) else ""
```

**Complexity:** O(C) time where C = total chars across all words.

---

## Pattern Recognition Tips

| Signal                           | Pattern                       |
| -------------------------------- | ----------------------------- |
| "Connected components / islands" | DFS/BFS flood fill            |
| "Shortest path (unweighted)"     | BFS                           |
| "Ordering with dependencies"     | Topological sort              |
| "Cycle detection (directed)"     | Topo sort or DFS coloring     |
| "Cycle detection (undirected)"   | Union-Find or DFS with parent |

---

[← Binary Trees](./chapter-05-trees.md) | [next →](./chapter-07-dynamic-programming.md)

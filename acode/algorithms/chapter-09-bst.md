# Chapter 9: Ordered Data — Binary Search Trees

[← Chapter 8: Tries](chapter-08-tries.md) | [Chapter 10: Shortest Path →](chapter-10-graphs-bfs-dfs.md)

---

## The Problem

RouteMaster needs to answer range queries efficiently:
- "Show all packages with deadlines between 9 AM and 12 PM"
- "What's the next delivery after this one?"
- "How many packages have priority ≤ 2?"

Hash tables give O(1) exact lookup but can't answer range queries. Sorted arrays answer range queries but insertions are O(n). You need a structure that supports O(log n) insert, delete, search, AND range queries.

## Binary Search Tree: The Concept

A BST is a binary tree where for every node:
- All values in the left subtree are **smaller**
- All values in the right subtree are **larger**

```
         8
       /   \
      3     10
     / \      \
    1   6     14
       / \   /
      4   7 13
```

In-order traversal (left → root → right) gives sorted output: 1, 3, 4, 6, 7, 8, 10, 13, 14.

## Implementation

```python
class BSTNode:
    def __init__(self, key, value=None):
        self.key = key
        self.value = value
        self.left = None
        self.right = None

class BST:
    def __init__(self):
        self.root = None

    def insert(self, key, value=None):
        """Insert a key-value pair. O(h) where h = height."""
        if not self.root:
            self.root = BSTNode(key, value)
            return
        self._insert(self.root, key, value)

    def _insert(self, node, key, value):
        if key < node.key:
            if node.left is None:
                node.left = BSTNode(key, value)
            else:
                self._insert(node.left, key, value)
        elif key > node.key:
            if node.right is None:
                node.right = BSTNode(key, value)
            else:
                self._insert(node.right, key, value)
        else:
            node.value = value  # Update existing key

    def search(self, key):
        """Find a value by key. O(h)."""
        node = self.root
        while node:
            if key == node.key:
                return node.value
            elif key < node.key:
                node = node.left
            else:
                node = node.right
        return None

    def range_query(self, low, high):
        """Find all keys in [low, high]. O(h + k) where k = results."""
        results = []
        self._range(self.root, low, high, results)
        return results

    def _range(self, node, low, high, results):
        if not node:
            return
        if low < node.key:
            self._range(node.left, low, high, results)
        if low <= node.key <= high:
            results.append((node.key, node.value))
        if node.key < high:
            self._range(node.right, low, high, results)

    def successor(self, key):
        """Find the smallest key greater than the given key."""
        successor = None
        node = self.root
        while node:
            if node.key > key:
                successor = node
                node = node.left
            else:
                node = node.right
        return (successor.key, successor.value) if successor else None

    def in_order(self):
        """Return all elements in sorted order. O(n)."""
        results = []
        self._in_order(self.root, results)
        return results

    def _in_order(self, node, results):
        if node:
            self._in_order(node.left, results)
            results.append((node.key, node.value))
            self._in_order(node.right, results)
```

## The Balance Problem

If you insert sorted data into a BST, it degenerates into a linked list:

```
Insert 1, 2, 3, 4, 5:

1
 \
  2
   \
    3
     \
      4
       \
        5

Height = n. All operations become O(n). Useless.
```

## AVL Trees: Self-Balancing

An AVL tree maintains the invariant: for every node, the heights of left and right subtrees differ by at most 1. After each insert/delete, it **rotates** to restore balance.

```python
class AVLNode:
    def __init__(self, key, value=None):
        self.key = key
        self.value = value
        self.left = None
        self.right = None
        self.height = 1

class AVLTree:
    def __init__(self):
        self.root = None

    def _height(self, node):
        return node.height if node else 0

    def _balance_factor(self, node):
        return self._height(node.left) - self._height(node.right)

    def _update_height(self, node):
        node.height = 1 + max(self._height(node.left), self._height(node.right))

    def _rotate_right(self, y):
        x = y.left
        t = x.right
        x.right = y
        y.left = t
        self._update_height(y)
        self._update_height(x)
        return x

    def _rotate_left(self, x):
        y = x.right
        t = y.left
        y.left = x
        x.right = t
        self._update_height(x)
        self._update_height(y)
        return y

    def insert(self, key, value=None):
        self.root = self._insert(self.root, key, value)

    def _insert(self, node, key, value):
        if not node:
            return AVLNode(key, value)

        if key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            node.value = value
            return node

        self._update_height(node)
        balance = self._balance_factor(node)

        # Left-heavy
        if balance > 1:
            if key < node.left.key:
                return self._rotate_right(node)
            else:
                node.left = self._rotate_left(node.left)
                return self._rotate_right(node)

        # Right-heavy
        if balance < -1:
            if key > node.right.key:
                return self._rotate_left(node)
            else:
                node.right = self._rotate_right(node.right)
                return self._rotate_left(node)

        return node
```

With balancing, height is always O(log n). All operations guaranteed O(log n).

## RouteMaster's Deadline Index

```python
class DeadlineIndex:
    """AVL tree indexed by deadline for range queries."""

    def __init__(self):
        self.tree = AVLTree()

    def add_package(self, package):
        # Key = (deadline, tracking) for uniqueness
        key = (package.deadline, package.tracking)
        self.tree.insert(key, package)

    def packages_between(self, start_time, end_time):
        """All packages with deadlines in [start, end]. O(log n + k)."""
        return self.tree.range_query((start_time, ""), (end_time, "~"))

    def next_deadline_after(self, time):
        """What's the next delivery deadline after this time?"""
        return self.tree.successor((time, "~"))
```

```python
# "Show me all packages due between 9 AM and noon"
morning_packages = index.packages_between("2024-01-15 09:00", "2024-01-15 12:00")

# "What's the next delivery after the current one?"
next_delivery = index.next_deadline_after("2024-01-15 10:30")
```

## BST vs Hash Table vs Sorted Array

| Operation | Hash Table | Sorted Array | BST (balanced) |
|---|---|---|---|
| Search | O(1) avg | O(log n) | O(log n) |
| Insert | O(1) avg | O(n) | O(log n) |
| Delete | O(1) avg | O(n) | O(log n) |
| Range query | O(n) | O(log n + k) | O(log n + k) |
| Min/Max | O(n) | O(1) | O(log n) |
| Successor | O(n) | O(1) | O(log n) |
| Sorted traversal | O(n log n) | O(n) | O(n) |

**Use hash tables** when you only need exact lookups.
**Use BSTs** when you need ordered operations (ranges, successor, sorted traversal).
**Use sorted arrays** when data is static (no inserts/deletes).

## What You Learned

- **BST** — left < root < right, enables O(log n) ordered operations
- **Range queries** — find all elements in [low, high] efficiently
- **Successor/predecessor** — find the next/previous element
- **The balance problem** — unbalanced BSTs degrade to O(n)
- **AVL trees** — self-balancing via rotations, guaranteed O(log n) height
- **When to use** — ordered data with dynamic inserts and range queries

RouteMaster can now query packages by deadline ranges instantly. But there's a bigger problem: the route planner. It needs to find the shortest path between two addresses in a city with 50,000 intersections and 120,000 road segments.

That's graphs. Chapter 10.

---

[← Chapter 8: Tries](chapter-08-tries.md) | [Chapter 10: Shortest Path →](chapter-10-graphs-bfs-dfs.md)

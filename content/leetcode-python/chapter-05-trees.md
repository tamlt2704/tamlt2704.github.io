# Chapter 5: Binary Trees

[← Stacks & Queues](./chapter-04-stacks-queues.md) | [next →](./chapter-06-graphs.md)

---

## Patterns

### DFS (Recursive)

```python
def dfs(root):
    if not root:
        return base_case
    left = dfs(root.left)
    right = dfs(root.right)
    return combine(root.val, left, right)
```

### BFS (Level Order)

```python
from collections import deque

def bfs(root):
    if not root:
        return []
    queue = deque([root])
    result = []
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left: queue.append(node.left)
            if node.right: queue.append(node.right)
        result.append(level)
    return result
```

### Pass Info Down (Preorder) vs Collect Info Up (Postorder)

- **Preorder:** pass constraints/path down (e.g., validate BST)
- **Postorder:** collect results up (e.g., height, diameter)

---

## Problem 1: Maximum Depth of Binary Tree (Easy) — LC 104

```python
def maxDepth(root):
    if not root:
        return 0
    return 1 + max(maxDepth(root.left), maxDepth(root.right))
```

**Complexity:** O(n) time, O(h) space.

---

## Problem 2: Invert Binary Tree (Easy) — LC 226

```python
def invertTree(root):
    if not root:
        return None
    root.left, root.right = invertTree(root.right), invertTree(root.left)
    return root
```

**Complexity:** O(n) time, O(h) space.

---

## Problem 3: Lowest Common Ancestor (Medium) — LC 236

```python
def lowestCommonAncestor(root, p, q):
    if not root or root == p or root == q:
        return root
    left = lowestCommonAncestor(root.left, p, q)
    right = lowestCommonAncestor(root.right, p, q)
    if left and right:
        return root
    return left or right
```

**Complexity:** O(n) time, O(h) space.

**Key insight:** If both sides return non-null, current node is LCA.

---

## Problem 4: Binary Tree Right Side View (Medium) — LC 199

```python
from collections import deque

def rightSideView(root):
    if not root:
        return []
    res = []
    queue = deque([root])
    while queue:
        for i in range(len(queue)):
            node = queue.popleft()
            if node.left: queue.append(node.left)
            if node.right: queue.append(node.right)
        res.append(node.val)  # last node of each level
    return res
```

**Complexity:** O(n) time, O(w) space where w = max width.

---

## Problem 5: Binary Tree Maximum Path Sum (Hard) — LC 124

```python
def maxPathSum(root):
    res = [float('-inf')]

    def dfs(node):
        if not node:
            return 0
        left = max(0, dfs(node.left))
        right = max(0, dfs(node.right))
        res[0] = max(res[0], node.val + left + right)
        return node.val + max(left, right)

    dfs(root)
    return res[0]
```

**Complexity:** O(n) time, O(h) space.

**Key insight:** At each node, compute the "split path" (left + node + right) for the answer, but return the "single path" (node + best side) to the parent.

---

## Pattern Recognition Tips

| Signal                       | Pattern                          |
| ---------------------------- | -------------------------------- |
| "Height / depth / diameter"  | Postorder DFS                    |
| "Level order / zigzag"       | BFS with queue                   |
| "Validate BST / path sum"    | Preorder with constraints        |
| "Serialize / construct tree" | Preorder + inorder               |
| "Lowest common ancestor"     | Postorder, return found nodes up |

---

[← Stacks & Queues](./chapter-04-stacks-queues.md) | [next →](./chapter-06-graphs.md)

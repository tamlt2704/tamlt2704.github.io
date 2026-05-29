# Chapter 4: Stacks & Queues

[← Linked Lists](./chapter-03-linked-lists.md) | [next →](./chapter-05-trees.md)

---

## Patterns

### Monotonic Stack

Use when: finding next greater/smaller element, or maintaining a decreasing/increasing order.

```python
# Template: next greater element
def next_greater(nums):
    n = len(nums)
    res = [-1] * n
    stack = []  # indices
    for i in range(n):
        while stack and nums[i] > nums[stack[-1]]:
            res[stack.pop()] = nums[i]
        stack.append(i)
    return res
```

### Queue for BFS

```python
from collections import deque

def bfs_template(start):
    queue = deque([start])
    visited = {start}
    while queue:
        node = queue.popleft()
        for neighbor in get_neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
```

---

## Problem 1: Valid Parentheses (Easy) — LC 20

```python
def isValid(s):
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    for c in s:
        if c in pairs:
            if not stack or stack[-1] != pairs[c]:
                return False
            stack.pop()
        else:
            stack.append(c)
    return not stack
```

**Complexity:** O(n) time, O(n) space.

---

## Problem 2: Daily Temperatures (Medium) — LC 739

**Given:** Array of temperatures, find days until warmer temperature.

```python
def dailyTemperatures(temperatures):
    n = len(temperatures)
    res = [0] * n
    stack = []
    for i in range(n):
        while stack and temperatures[i] > temperatures[stack[-1]]:
            j = stack.pop()
            res[j] = i - j
        stack.append(i)
    return res
```

**Complexity:** O(n) time, O(n) space.

---

## Problem 3: Min Stack (Medium) — LC 155

```python
class MinStack:
    def __init__(self):
        self.stack = []
        self.min_stack = []

    def push(self, val):
        self.stack.append(val)
        self.min_stack.append(min(val, self.min_stack[-1] if self.min_stack else val))

    def pop(self):
        self.stack.pop()
        self.min_stack.pop()

    def top(self):
        return self.stack[-1]

    def getMin(self):
        return self.min_stack[-1]
```

**Complexity:** O(1) all operations, O(n) space.

---

## Problem 4: Largest Rectangle in Histogram (Hard) — LC 84

```python
def largestRectangleArea(heights):
    stack = []
    res = 0
    heights.append(0)  # sentinel
    for i, h in enumerate(heights):
        while stack and heights[stack[-1]] > h:
            height = heights[stack.pop()]
            width = i if not stack else i - stack[-1] - 1
            res = max(res, height * width)
        stack.append(i)
    return res
```

**Complexity:** O(n) time, O(n) space.

**Key insight:** Monotonic increasing stack; when we pop, we know the width extends from current index back to new stack top.

---

## Problem 5: Sliding Window Maximum (Hard) — LC 239

```python
from collections import deque

def maxSlidingWindow(nums, k):
    dq = deque()  # indices, decreasing values
    res = []
    for i, n in enumerate(nums):
        while dq and nums[dq[-1]] <= n:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            res.append(nums[dq[0]])
    return res
```

**Complexity:** O(n) time, O(k) space.

**Pattern:** Monotonic deque maintains candidates in decreasing order.

---

## Pattern Recognition Tips

| Signal                         | Pattern         |
| ------------------------------ | --------------- |
| "Next greater/smaller element" | Monotonic stack |
| "Valid brackets/nesting"       | Stack matching  |
| "Sliding window max/min"       | Monotonic deque |
| "Level-order / shortest path"  | BFS with queue  |
| "Undo / history"               | Stack           |

---

[← Linked Lists](./chapter-03-linked-lists.md) | [next →](./chapter-05-trees.md)

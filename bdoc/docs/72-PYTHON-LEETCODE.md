# Chapter 72: Python for LeetCode — The Competitive Edge

## What you'll learn

- Python tricks that make LeetCode solutions 2-3× shorter than Java/C++
- Built-in data structures: list, dict, set, deque, heapq, Counter, defaultdict
- One-liners and idioms that save time in interviews
- Common patterns implemented in Pythonic style
- Time complexity of Python operations (know what's O(1) vs O(n))
- Template solutions for every major pattern

---

## PART 1: Python Advantages for LeetCode

## 72.1 Why Python wins in interviews

```python
# Java: 15 lines
# Python: 1 line
# "Return the two numbers that sum to target"

# Java:
# Map<Integer, Integer> map = new HashMap<>();
# for (int i = 0; i < nums.length; i++) {
#     int complement = target - nums[i];
#     if (map.containsKey(complement)) {
#         return new int[]{map.get(complement), i};
#     }
#     map.put(nums[i], i);
# }

# Python (same logic, half the code):
def twoSum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        if target - n in seen:
            return [seen[target - n], i]
        seen[n] = i
```

**Python advantages:**
- No type declarations (less boilerplate)
- Built-in data structures are rich (Counter, defaultdict, heapq)
- Slicing, comprehensions, unpacking save lines
- Negative indexing (`arr[-1]` = last element)
- Multiple return values, tuple unpacking
- `in` operator works on lists, sets, dicts, strings

---

## PART 2: Essential Data Structures

## 72.2 List (dynamic array)

```python
# Creation
a = [1, 2, 3, 4, 5]
b = [0] * 10            # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
c = [[0] * 3 for _ in range(4)]  # 4×3 matrix (NOT [[0]*3]*4 ← shares references!)

# Access
a[0]      # first: 1
a[-1]     # last: 5
a[-2]     # second last: 4
a[1:4]    # slice [2, 3, 4] (index 1 to 3)
a[:3]     # first 3: [1, 2, 3]
a[2:]     # from index 2: [3, 4, 5]
a[::-1]   # reversed: [5, 4, 3, 2, 1]

# Operations
a.append(6)         # O(1) — add to end
a.pop()             # O(1) — remove from end, returns it
a.pop(0)            # O(n) — remove from front (use deque instead!)
a.insert(2, 99)     # O(n) — insert at index
len(a)              # O(1)
a.sort()            # O(n log n) — in-place
sorted(a)           # O(n log n) — returns new list
a.reverse()         # O(n) — in-place
a.index(3)          # O(n) — find index of value
3 in a              # O(n) — membership check (use set for O(1)!)

# Useful tricks
min(a), max(a), sum(a)    # built-in aggregates
list(zip(a, b))           # pair elements: [(1,'a'), (2,'b'), ...]
list(enumerate(a))        # [(0,1), (1,2), (2,3), ...]
```

## 72.3 Dictionary (HashMap)

```python
# Creation
d = {}
d = {"a": 1, "b": 2}
d = dict.fromkeys(["a", "b", "c"], 0)  # {"a": 0, "b": 0, "c": 0}

# Operations — ALL O(1) average
d["key"] = value       # set
d["key"]               # get (KeyError if missing)
d.get("key", default)  # get with default (no error)
"key" in d             # check existence
del d["key"]           # delete
len(d)                 # size

# Iteration
for key in d:              # keys
for key, val in d.items(): # key-value pairs
for val in d.values():     # values only

# defaultdict — auto-creates missing keys
from collections import defaultdict
graph = defaultdict(list)       # missing key → empty list
graph["a"].append("b")          # no KeyError!
count = defaultdict(int)        # missing key → 0
count["x"] += 1                 # no need to check if exists

# Counter — count frequencies instantly
from collections import Counter
freq = Counter("abracadabra")   # {'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1}
freq = Counter([1,1,2,3,3,3])   # {3: 3, 1: 2, 2: 1}
freq.most_common(2)             # [(3, 3), (1, 2)] — top 2 most frequent
freq["a"]                       # 5
freq["z"]                       # 0 (not KeyError!)
```

## 72.4 Set (HashSet)

```python
s = set()
s = {1, 2, 3}
s = set([1, 2, 2, 3])  # {1, 2, 3} — auto-deduplicates

# Operations — ALL O(1) average
s.add(4)           # add element
s.remove(4)        # remove (KeyError if missing)
s.discard(4)       # remove (no error if missing)
4 in s             # membership check — O(1)!
len(s)

# Set operations
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}
a | b              # union: {1,2,3,4,5,6}
a & b              # intersection: {3,4}
a - b              # difference: {1,2}
a ^ b              # symmetric difference: {1,2,5,6}
a.issubset(b)      # is a ⊆ b?

# CRITICAL: Use set for O(1) lookups instead of list
# ❌ O(n): if x in my_list
# ✅ O(1): if x in my_set
```

## 72.5 Deque (double-ended queue) — O(1) both ends

```python
from collections import deque

q = deque()
q = deque([1, 2, 3])

# O(1) operations on BOTH ends (list.pop(0) is O(n)!)
q.append(4)       # add right: [1,2,3,4]
q.appendleft(0)   # add left: [0,1,2,3,4]
q.pop()           # remove right: returns 4
q.popleft()       # remove left: returns 0

# USE FOR: BFS queue, sliding window
# ❌ queue = []  ... queue.pop(0)  ← O(n)!
# ✅ queue = deque()  ... queue.popleft()  ← O(1)!
```

## 72.6 Heap (Priority Queue) — heapq

```python
import heapq

# Python heapq is a MIN-HEAP (smallest element first)
h = []
heapq.heappush(h, 5)
heapq.heappush(h, 2)
heapq.heappush(h, 8)
heapq.heappush(h, 1)

heapq.heappop(h)    # 1 (smallest)
heapq.heappop(h)    # 2
h[0]                # peek at smallest without removing

# MAX-HEAP trick: negate values
heapq.heappush(h, -val)   # push negated
-heapq.heappop(h)          # pop and negate back

# Heapify existing list — O(n)
nums = [5, 2, 8, 1, 9]
heapq.heapify(nums)        # now nums[0] is the smallest

# Top-K pattern (K largest elements):
heapq.nlargest(3, nums)    # [9, 8, 5]
heapq.nsmallest(3, nums)   # [1, 2, 5]

# With custom key (tuples — sorted by first element):
h = []
heapq.heappush(h, (priority, item))
heapq.heappush(h, (1, "high priority"))
heapq.heappush(h, (5, "low priority"))
_, item = heapq.heappop(h)  # "high priority" (lowest number = highest priority)
```

## 72.7 String tricks

```python
s = "hello world"

# Checks
s.isalpha()        # all letters?
s.isdigit()        # all digits?
s.isalnum()        # letters or digits?
s.startswith("he") # prefix check
s.endswith("ld")   # suffix check

# Transform
s.lower()          # "hello world"
s.upper()          # "HELLO WORLD"
s.strip()          # remove whitespace from both ends
s.split()          # ["hello", "world"] (split by whitespace)
s.split(",")       # split by comma
",".join(["a","b","c"])  # "a,b,c"
s.replace("l", "L")     # "heLLo worLd"
s[::-1]            # "dlrow olleh" (reverse)

# Character operations
ord("a")           # 97 (ASCII value)
chr(97)            # "a"
ord(c) - ord("a") # 0-25 index for lowercase letters

# Count occurrences
s.count("l")       # 3

# IMMUTABLE: strings can't be modified in-place
# Convert to list for manipulation:
chars = list(s)
chars[0] = "H"
s = "".join(chars)  # "Hello world"
```

---

## PART 3: Python Patterns for LeetCode

## 72.8 Two pointers

```python
# Opposite direction (sorted array)
def two_sum_sorted(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        s = nums[left] + nums[right]
        if s == target: return [left, right]
        elif s < target: left += 1
        else: right -= 1

# Same direction (remove duplicates in-place)
def remove_duplicates(nums):
    if not nums: return 0
    slow = 0
    for fast in range(1, len(nums)):
        if nums[fast] != nums[slow]:
            slow += 1
            nums[slow] = nums[fast]
    return slow + 1
```

## 72.9 Sliding window

```python
# Longest substring without repeating characters
def lengthOfLongestSubstring(s):
    seen = {}
    left = 0
    result = 0
    for right, char in enumerate(s):
        if char in seen and seen[char] >= left:
            left = seen[char] + 1
        seen[char] = right
        result = max(result, right - left + 1)
    return result

# Maximum sum subarray of size k
def max_sum_k(nums, k):
    window = sum(nums[:k])
    best = window
    for i in range(k, len(nums)):
        window += nums[i] - nums[i - k]  # slide: add new, remove old
        best = max(best, window)
    return best
```

## 72.10 Binary search

```python
import bisect

# Manual binary search
def binary_search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target: return mid
        elif nums[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return -1

# Built-in bisect (insertion point)
bisect.bisect_left(nums, target)   # leftmost position where target can be inserted
bisect.bisect_right(nums, target)  # rightmost position
bisect.insort(nums, val)           # insert maintaining sorted order

# Binary search on answer
def min_capacity(weights, days):
    lo, hi = max(weights), sum(weights)
    while lo < hi:
        mid = (lo + hi) // 2
        if can_ship(weights, mid, days):
            hi = mid
        else:
            lo = mid + 1
    return lo
```

## 72.11 BFS (breadth-first search)

```python
from collections import deque

# Grid BFS (shortest path)
def shortest_path(grid):
    rows, cols = len(grid), len(grid[0])
    queue = deque([(0, 0, 0)])  # (row, col, distance)
    visited = {(0, 0)}
    directions = [(0,1), (0,-1), (1,0), (-1,0)]
    
    while queue:
        r, c, dist = queue.popleft()
        if r == rows-1 and c == cols-1:
            return dist
        for dr, dc in directions:
            nr, nc = r+dr, c+dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr,nc) not in visited and grid[nr][nc] == 0:
                visited.add((nr, nc))
                queue.append((nr, nc, dist+1))
    return -1

# Level-order tree traversal
def level_order(root):
    if not root: return []
    result = []
    queue = deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):  # process one level at a time
            node = queue.popleft()
            level.append(node.val)
            if node.left: queue.append(node.left)
            if node.right: queue.append(node.right)
        result.append(level)
    return result
```

## 72.12 DFS + Backtracking

```python
# Subsets (generate all subsets)
def subsets(nums):
    result = []
    def backtrack(start, current):
        result.append(current[:])  # copy current state
        for i in range(start, len(nums)):
            current.append(nums[i])
            backtrack(i + 1, current)
            current.pop()  # undo
    backtrack(0, [])
    return result

# Permutations
def permutations(nums):
    result = []
    def backtrack(remaining, current):
        if not remaining:
            result.append(current[:])
            return
        for i in range(len(remaining)):
            current.append(remaining[i])
            backtrack(remaining[:i] + remaining[i+1:], current)
            current.pop()
    backtrack(nums, [])
    return result

# Number of islands (DFS flood fill)
def numIslands(grid):
    def dfs(r, c):
        if r < 0 or r >= len(grid) or c < 0 or c >= len(grid[0]) or grid[r][c] != '1':
            return
        grid[r][c] = '0'  # mark visited
        dfs(r+1,c); dfs(r-1,c); dfs(r,c+1); dfs(r,c-1)
    
    count = 0
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == '1':
                count += 1
                dfs(r, c)
    return count
```

## 72.13 Dynamic Programming

```python
# Climbing stairs (1D DP)
def climbStairs(n):
    if n <= 2: return n
    prev2, prev1 = 1, 2
    for _ in range(3, n+1):
        prev2, prev1 = prev1, prev1 + prev2
    return prev1

# Coin change (minimum coins)
def coinChange(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for a in range(1, amount + 1):
        for coin in coins:
            if coin <= a:
                dp[a] = min(dp[a], dp[a - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1

# Longest common subsequence (2D DP)
def longestCommonSubsequence(text1, text2):
    m, n = len(text1), len(text2)
    dp = [[0] * (n+1) for _ in range(m+1)]
    for i in range(1, m+1):
        for j in range(1, n+1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[m][n]

# 0/1 Knapsack (1D space optimization)
def knapsack(weights, values, capacity):
    dp = [0] * (capacity + 1)
    for i in range(len(weights)):
        for w in range(capacity, weights[i]-1, -1):  # BACKWARDS!
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    return dp[capacity]
```

## 72.14 Graph (Dijkstra)

```python
import heapq
from collections import defaultdict

def dijkstra(graph, source, n):
    dist = [float('inf')] * n
    dist[source] = 0
    heap = [(0, source)]  # (distance, node)
    
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]: continue  # stale entry
        for v, weight in graph[u]:
            if dist[u] + weight < dist[v]:
                dist[v] = dist[u] + weight
                heapq.heappush(heap, (dist[v], v))
    return dist
```

## 72.15 Monotonic stack

```python
# Next greater element
def next_greater(nums):
    result = [-1] * len(nums)
    stack = []  # stores indices
    for i, num in enumerate(nums):
        while stack and nums[stack[-1]] < num:
            result[stack.pop()] = num
        stack.append(i)
    return result
```

---

## PART 4: Python Speed Tricks

## 72.16 One-liners and idioms

```python
# Swap without temp
a, b = b, a

# Multiple assignment
x = y = z = 0

# Ternary
result = "yes" if condition else "no"

# List comprehension (faster than loop + append)
squares = [x*x for x in range(10)]
evens = [x for x in nums if x % 2 == 0]
flat = [x for row in matrix for x in row]  # flatten 2D

# Dictionary comprehension
freq = {char: s.count(char) for char in set(s)}

# Unpack
first, *middle, last = [1, 2, 3, 4, 5]  # first=1, middle=[2,3,4], last=5
a, b = [1, 2]  # parallel assignment from list

# any() / all() — short-circuit
any(x > 5 for x in nums)   # True if ANY element > 5
all(x > 0 for x in nums)   # True if ALL elements > 0

# zip for parallel iteration
for a, b in zip(list1, list2):
    ...

# Infinity
float('inf')   # positive infinity
float('-inf')  # negative infinity

# Math
abs(-5)          # 5
divmod(17, 5)    # (3, 2) — quotient and remainder
pow(2, 10)       # 1024
pow(2, 10, MOD)  # modular exponentiation (fast!)

# Sorting with key
intervals.sort(key=lambda x: x[0])           # sort by first element
words.sort(key=len)                           # sort by length
items.sort(key=lambda x: (-x[1], x[0]))      # sort by value DESC, then key ASC
```

## 72.17 Time complexity cheat sheet

| Operation | list | dict/set | deque | heapq |
|-----------|------|----------|-------|-------|
| Access by index | O(1) | — | O(n) | — |
| Search (`in`) | O(n) | **O(1)** | O(n) | O(n) |
| Append/push | O(1) | O(1) | O(1) | O(log n) |
| Pop end | O(1) | — | O(1) | O(log n) |
| Pop front | **O(n)** | — | **O(1)** | — |
| Insert middle | O(n) | — | O(n) | — |
| Sort | O(n log n) | — | — | O(n) heapify |
| Min/Max | O(n) | O(n) | O(n) | **O(1)** peek |

**Critical rules:**
- Membership check: use `set` or `dict` (O(1)), never `list` (O(n))
- Queue (FIFO): use `deque` (O(1) popleft), never `list.pop(0)` (O(n))
- Priority queue: use `heapq` (O(log n) push/pop)
- Sorting: Python's Timsort is O(n log n) and stable

## 72.18 Common Python gotchas in LeetCode

```python
# ❌ WRONG: Mutable default argument (shared between calls!)
def foo(arr=[]):
    arr.append(1)  # modifies the SAME list every call!
# ✅ FIX:
def foo(arr=None):
    if arr is None: arr = []

# ❌ WRONG: 2D array creation
grid = [[0] * 3] * 4  # all rows are THE SAME list!
grid[0][0] = 1  # changes ALL rows!
# ✅ FIX:
grid = [[0] * 3 for _ in range(4)]  # independent rows

# ❌ WRONG: Integer division
-7 // 2  # = -4 in Python (floors toward -infinity)
# In LeetCode (C++ style): int(-7 / 2) = -3
# ✅ FIX:
int(-7 / 2)  # -3 (truncates toward zero)

# ❌ WRONG: Modifying list while iterating
for x in my_list:
    if x < 0: my_list.remove(x)  # skips elements!
# ✅ FIX:
my_list = [x for x in my_list if x >= 0]

# ❌ SLOW: String concatenation in loop
s = ""
for word in words: s += word  # O(n²) — creates new string each time
# ✅ FAST:
s = "".join(words)  # O(n)
```

---

## Summary

✅ Data structures: list, dict (defaultdict/Counter), set, deque, heapq — know when to use each
✅ O(1) lookups: always use set/dict for membership, never list
✅ O(1) queue: always use deque.popleft(), never list.pop(0)
✅ String tricks: slicing, join, split, ord/chr, reverse with [::-1]
✅ Patterns: two pointers, sliding window, binary search (bisect), BFS (deque), DFS, DP, heap, monotonic stack
✅ One-liners: comprehensions, unpacking, ternary, any/all, zip, enumerate
✅ Gotchas: mutable defaults, 2D arrays, integer division, string concat in loops

## Key takeaway

**Python lets you focus on the ALGORITHM, not the syntax.** In an interview, spending 30 seconds on `Counter(s).most_common(k)` instead of 5 minutes writing a manual frequency map means more time for edge cases, optimization discussion, and communication. Learn the standard library deeply — it's your competitive advantage.

---

→ [Back to Chapter 71: Kiro Productivity](./71-KIRO-PRODUCTIVITY.md)

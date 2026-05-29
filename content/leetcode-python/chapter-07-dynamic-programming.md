# Chapter 7: Dynamic Programming

[← Graphs](./chapter-06-graphs.md) | [next →](./chapter-08-binary-search.md)

---

## Patterns

### 1D DP

```python
# Template: dp[i] = answer for subproblem ending at i
def solve(nums):
    dp = [0] * len(nums)
    dp[0] = base_case
    for i in range(1, len(nums)):
        dp[i] = recurrence(dp, nums, i)
    return dp[-1]
```

### 2D DP

```python
# Template: dp[i][j] = answer for subproblem (i, j)
def solve(m, n):
    dp = [[0] * (n+1) for _ in range(m+1)]
    for i in range(1, m+1):
        for j in range(1, n+1):
            dp[i][j] = recurrence(dp, i, j)
    return dp[m][n]
```

### 0/1 Knapsack

```python
def knapsack(weights, values, capacity):
    dp = [0] * (capacity + 1)
    for w, v in zip(weights, values):
        for c in range(capacity, w - 1, -1):  # reverse!
            dp[c] = max(dp[c], dp[c - w] + v)
    return dp[capacity]
```

---

## Problem 1: Climbing Stairs (Easy) — LC 70

```python
def climbStairs(n):
    a, b = 1, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b
```

**Complexity:** O(n) time, O(1) space.

---

## Problem 2: Longest Increasing Subsequence (Medium) — LC 300

```python
from bisect import bisect_left

def lengthOfLIS(nums):
    tails = []
    for n in nums:
        i = bisect_left(tails, n)
        if i == len(tails):
            tails.append(n)
        else:
            tails[i] = n
    return len(tails)
```

**Complexity:** O(n log n) time, O(n) space.

**Key insight:** `tails[i]` = smallest tail element for increasing subsequence of length i+1.

---

## Problem 3: Coin Change (Medium) — LC 322

```python
def coinChange(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for c in coins:
        for a in range(c, amount + 1):
            dp[a] = min(dp[a], dp[a - c] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1
```

**Complexity:** O(amount · len(coins)) time, O(amount) space.

---

## Problem 4: Longest Common Subsequence (Medium) — LC 1143

```python
def longestCommonSubsequence(text1, text2):
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[m][n]
```

**Complexity:** O(m·n) time, O(m·n) space.

---

## Problem 5: Edit Distance (Hard) — LC 72

```python
def minDistance(word1, word2):
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i-1] == word2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
    return dp[m][n]
```

**Complexity:** O(m·n) time, O(m·n) space.

---

## DP Problem-Solving Framework

1. **Define state:** What does dp[i] (or dp[i][j]) represent?
2. **Base case:** What's the answer for the smallest subproblem?
3. **Transition:** How does dp[i] relate to smaller subproblems?
4. **Order:** Fill dp in an order where dependencies are already computed.
5. **Answer:** Where in the dp table is the final answer?

## Pattern Recognition Tips

| Signal                                           | Pattern                    |
| ------------------------------------------------ | -------------------------- |
| "Min/max ways to reach end"                      | 1D DP                      |
| "Two strings comparison"                         | 2D DP (LCS, edit distance) |
| "Select items with capacity"                     | Knapsack                   |
| "Count partitions / subsets"                     | Subset sum DP              |
| "Optimal substructure + overlapping subproblems" | DP (vs greedy)             |

---

[← Graphs](./chapter-06-graphs.md) | [next →](./chapter-08-binary-search.md)

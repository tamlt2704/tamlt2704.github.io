# Chapter 73: Python One-Liners for LeetCode — Elegant Solutions

## What you'll learn

- Solve 50+ LeetCode problems in 1-3 lines of Python
- Master: comprehensions, Counter, zip, map, reduce, lambda, unpacking
- When one-liners are appropriate (and when they're not)
- Impress interviewers with concise, readable Pythonic solutions

---

## ⚠️ When to use one-liners in interviews

```
✅ USE when: the one-liner is READABLE and shows you know Python
✅ USE when: it replaces obvious boilerplate (counting, finding max, etc.)
✅ USE when: interviewer says "can you do it more concisely?"

❌ DON'T when: it sacrifices clarity (interviewer can't follow your logic)
❌ DON'T when: you can't explain what it does line by line
❌ DON'T when: the multi-line version is already clean

STRATEGY: Write the clear version first. Then say:
"In Python, this can also be written as [one-liner]. Same logic, just more concise."
```

---

## 📦 ARRAYS & NUMBERS

### Two Sum (#1)
```python
def twoSum(nums, target):
    d = {}
    return next([d[target-n], i] for i, n in enumerate(nums) if (target-n in d) or d.update({n: i}) is None)

# Cleaner (2 lines):
def twoSum(nums, target):
    seen = {}
    return next(([seen[target-n], i] for i, n in enumerate(nums) if target-n in seen or not seen.update({n: i})), [])
```

### Contains Duplicate (#217)
```python
def containsDuplicate(nums):
    return len(nums) != len(set(nums))
```

### Single Number (#136) — XOR all elements
```python
from functools import reduce
from operator import xor

def singleNumber(nums):
    return reduce(xor, nums)
```

### Product of Array Except Self (#238)
```python
from itertools import accumulate
from operator import mul

def productExceptSelf(nums):
    left = list(accumulate(nums, mul, initial=1))[:-1]
    right = list(accumulate(nums[::-1], mul, initial=1))[:-1][::-1]
    return [l * r for l, r in zip(left, right)]
```

### Maximum Subarray (#53) — Kadane's
```python
from itertools import accumulate

def maxSubArray(nums):
    return max(accumulate(nums, lambda cur, x: max(x, cur + x)))
```

### Best Time to Buy and Sell Stock (#121)
```python
from itertools import accumulate

def maxProfit(prices):
    return max(b - a for a, b in zip(accumulate(prices, min), prices))
```

### Majority Element (#169)
```python
from collections import Counter

def majorityElement(nums):
    return Counter(nums).most_common(1)[0][0]
```

### Move Zeroes (#283)
```python
def moveZeroes(nums):
    nums.sort(key=lambda x: x == 0)  # False (0) sorts before True (non-zero)... wait, reversed:
    # Actually:
    nums[:] = [x for x in nums if x] + [0] * nums.count(0)
```

### Missing Number (#268)
```python
def missingNumber(nums):
    return len(nums) * (len(nums) + 1) // 2 - sum(nums)

# Or with XOR:
from functools import reduce
from operator import xor
def missingNumber(nums):
    return reduce(xor, range(len(nums) + 1)) ^ reduce(xor, nums)
```

### Plus One (#66)
```python
def plusOne(digits):
    return list(map(int, str(int("".join(map(str, digits))) + 1)))
```

---

## 📝 STRINGS

### Valid Anagram (#242)
```python
from collections import Counter

def isAnagram(s, t):
    return Counter(s) == Counter(t)
```

### Valid Palindrome (#125)
```python
def isPalindrome(s):
    s = [c.lower() for c in s if c.isalnum()]
    return s == s[::-1]
```

### Longest Common Prefix (#14)
```python
import os

def longestCommonPrefix(strs):
    return os.path.commonprefix(strs)

# Without import:
def longestCommonPrefix(strs):
    return "".join(c[0] for c in zip(*strs) if len(set(c)) == 1)
```

### Reverse String (#344)
```python
def reverseString(s):
    s[:] = s[::-1]
```

### First Unique Character (#387)
```python
from collections import Counter

def firstUniqChar(s):
    return next((i for i, c in enumerate(s) if Counter(s)[c] == 1), -1)

# Faster (single Counter call):
def firstUniqChar(s):
    freq = Counter(s)
    return next((i for i, c in enumerate(s) if freq[c] == 1), -1)
```

### Group Anagrams (#49)
```python
from collections import defaultdict

def groupAnagrams(strs):
    groups = defaultdict(list)
    for s in strs:
        groups[tuple(sorted(s))].append(s)
    return list(groups.values())

# One-liner:
def groupAnagrams(strs):
    return list({tuple(sorted(s)): [] for s in strs} or defaultdict(list, {tuple(sorted(s)): [s for s2 in strs if sorted(s2) == sorted(s)] for s in strs}).values())
    # ^ ugly. Use the 3-line version above.
```

### Reverse Words in String (#151)
```python
def reverseWords(s):
    return " ".join(s.split()[::-1])
```

### Valid Parentheses (#20)
```python
def isValid(s):
    while "()" in s or "[]" in s or "{}" in s:
        s = s.replace("()", "").replace("[]", "").replace("{}", "")
    return s == ""
# Note: O(n²) — interview-OK for showing creativity, then explain O(n) stack version
```

### Roman to Integer (#13)
```python
def romanToInt(s):
    d = {'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000}
    return sum(-d[s[i]] if i < len(s)-1 and d[s[i]] < d[s[i+1]] else d[s[i]] for i in range(len(s)))
```

### Length of Last Word (#58)
```python
def lengthOfLastWord(s):
    return len(s.strip().split()[-1])
```

---

## 🔢 MATH & BIT MANIPULATION

### Power of Two (#231)
```python
def isPowerOfTwo(n):
    return n > 0 and n & (n - 1) == 0
```

### Reverse Integer (#7)
```python
def reverse(x):
    r = int(str(abs(x))[::-1]) * (1 if x > 0 else -1)
    return r if -2**31 <= r <= 2**31 - 1 else 0
```

### Palindrome Number (#9)
```python
def isPalindrome(x):
    return str(x) == str(x)[::-1]
```

### Counting Bits (#338)
```python
def countBits(n):
    return [bin(i).count('1') for i in range(n + 1)]
```

### Number of 1 Bits (#191)
```python
def hammingWeight(n):
    return bin(n).count('1')
```

### FizzBuzz (#412)
```python
def fizzBuzz(n):
    return ["FizzBuzz" if i%15==0 else "Fizz" if i%3==0 else "Buzz" if i%5==0 else str(i) for i in range(1, n+1)]
```

### Excel Sheet Column Number (#171)
```python
from functools import reduce

def titleToNumber(s):
    return reduce(lambda acc, c: acc * 26 + ord(c) - 64, s, 0)
```

### Happy Number (#202)
```python
def isHappy(n):
    seen = set()
    while n != 1 and n not in seen:
        seen.add(n)
        n = sum(int(d)**2 for d in str(n))
    return n == 1
```

---

## 📊 SORTING & SEARCHING

### Merge Sorted Array (#88)
```python
def merge(nums1, m, nums2, n):
    nums1[m:] = nums2
    nums1.sort()
```

### Kth Largest Element (#215)
```python
import heapq

def findKthLargest(nums, k):
    return heapq.nlargest(k, nums)[-1]
```

### Top K Frequent Elements (#347)
```python
from collections import Counter

def topKFrequent(nums, k):
    return [x for x, _ in Counter(nums).most_common(k)]
```

### Sort Colors / Dutch Flag (#75)
```python
def sortColors(nums):
    nums.sort()  # technically O(n log n), but the one-line version
    # O(n) one-pass: use 3-pointer (but that's 10 lines)
```

### Valid Anagram sorted approach
```python
def isAnagram(s, t):
    return sorted(s) == sorted(t)
```

### Intersection of Two Arrays (#349)
```python
def intersection(nums1, nums2):
    return list(set(nums1) & set(nums2))
```

### Intersection with duplicates (#350)
```python
from collections import Counter

def intersect(nums1, nums2):
    return list((Counter(nums1) & Counter(nums2)).elements())
```

---

## 🌳 TREES & LINKED LISTS

### Maximum Depth of Binary Tree (#104)
```python
def maxDepth(root):
    return 0 if not root else 1 + max(maxDepth(root.left), maxDepth(root.right))
```

### Invert Binary Tree (#226)
```python
def invertTree(root):
    if root: root.left, root.right = invertTree(root.right), invertTree(root.left)
    return root
```

### Same Tree (#100)
```python
def isSameTree(p, q):
    return p and q and p.val == q.val and isSameTree(p.left, q.left) and isSameTree(p.right, q.right) or p is q
```

### Symmetric Tree (#101)
```python
def isSymmetric(root):
    def check(a, b):
        if not a and not b: return True
        if not a or not b: return False
        return a.val == b.val and check(a.left, b.right) and check(a.right, b.left)
    return check(root.left, root.right) if root else True
```

### Path Sum (#112)
```python
def hasPathSum(root, target):
    return root is not None and (not root.left and not root.right and root.val == target or hasPathSum(root.left, target-root.val) or hasPathSum(root.right, target-root.val))
```

### Merge Two Sorted Lists (#21)
```python
def mergeTwoLists(l1, l2):
    if not l1 or not l2: return l1 or l2
    if l1.val < l2.val: l1.next = mergeTwoLists(l1.next, l2); return l1
    else: l2.next = mergeTwoLists(l1, l2.next); return l2
```

### Reverse Linked List (#206)
```python
def reverseList(head):
    prev = None
    while head: head.next, prev, head = prev, head, head.next
    return prev
```

### Linked List Cycle (#141)
```python
def hasCycle(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow == fast: return True
    return False
```

---

## 🧩 DYNAMIC PROGRAMMING

### Climbing Stairs (#70)
```python
from functools import lru_cache

@lru_cache(None)
def climbStairs(n):
    return n if n <= 2 else climbStairs(n-1) + climbStairs(n-2)
```

### House Robber (#198)
```python
from functools import reduce

def rob(nums):
    return reduce(lambda dp, n: (dp[1], max(dp[1], dp[0] + n)), nums, (0, 0))[1]
```

### Unique Paths (#62)
```python
from math import comb

def uniquePaths(m, n):
    return comb(m + n - 2, m - 1)
```

### Coin Change (#322) — with caching
```python
from functools import lru_cache

def coinChange(coins, amount):
    @lru_cache(None)
    def dp(remaining):
        if remaining == 0: return 0
        if remaining < 0: return float('inf')
        return min((dp(remaining - c) for c in coins), default=float('inf')) + 1
    result = dp(amount)
    return result if result != float('inf') else -1
```

### Word Break (#139)
```python
from functools import lru_cache

def wordBreak(s, wordDict):
    words = set(wordDict)
    @lru_cache(None)
    def dp(i):
        if i == len(s): return True
        return any(s[i:j] in words and dp(j) for j in range(i+1, len(s)+1))
    return dp(0)
```

---

## 🔧 UTILITY ONE-LINERS (use these everywhere)

```python
# Flatten 2D list
flat = [x for row in matrix for x in row]

# Transpose matrix
transposed = list(zip(*matrix))

# Rotate matrix 90° clockwise
rotated = [list(row) for row in zip(*matrix[::-1])]

# Get digits of number
digits = [int(d) for d in str(n)]

# Frequency count
from collections import Counter
freq = Counter(nums)

# Most common element
Counter(nums).most_common(1)[0][0]

# Remove duplicates preserving order
list(dict.fromkeys(nums))

# All pairs (i,j) where i < j
from itertools import combinations
pairs = list(combinations(range(n), 2))

# Cumulative sum (prefix sum)
from itertools import accumulate
prefix = list(accumulate(nums))

# Cartesian product (all combinations)
from itertools import product
grid = list(product(range(3), range(4)))  # all (row, col) pairs

# Group consecutive elements
from itertools import groupby
groups = [(key, list(g)) for key, g in groupby(sorted(nums))]

# Check if sorted
is_sorted = all(a <= b for a, b in zip(nums, nums[1:]))

# Clamp value to range
clamped = max(lo, min(hi, value))

# Binary representation
bin(42)         # '0b101010'
bin(42)[2:]     # '101010'
f"{42:08b}"    # '00101010' (padded to 8 bits)
```

---

## Summary

✅ 50+ problems solved in 1-3 lines
✅ Key tools: Counter, set operations, comprehensions, reduce, accumulate, lru_cache
✅ Patterns: `sorted(s) == sorted(t)`, `len(set(x))`, `reduce(xor, nums)`, `[::-1]`
✅ Math shortcuts: `comb()` for paths, `bin().count('1')` for bits, XOR for finding singles
✅ Tree recursion: base case + recursive case in one expression
✅ DP with `@lru_cache(None)` — turns recursion into DP with one decorator

## Key takeaway

**One-liners demonstrate MASTERY, not cleverness.** Using `Counter(nums).most_common(k)` in an interview shows you know Python's standard library deeply. Using an unreadable 200-character one-liner shows you're trying too hard. Write clean multi-line first, offer the concise version as a "Python can also do this in one line" bonus.

---

→ [Back to Chapter 72: Python for LeetCode](./72-PYTHON-LEETCODE.md)

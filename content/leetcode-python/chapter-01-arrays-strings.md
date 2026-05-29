# Chapter 1: Arrays & Strings

[← Overview](./chapter-00-overview.md) | [next →](./chapter-02-hashmaps.md)

---

## Patterns

### Two Pointers

Use when: sorted array, finding pairs, or partitioning.

```python
# Template: two pointers from both ends
def two_pointer(arr, target):
    left, right = 0, len(arr) - 1
    while left < right:
        curr = arr[left] + arr[right]
        if curr == target:
            return [left, right]
        elif curr < target:
            left += 1
        else:
            right -= 1
    return []
```

### Sliding Window

Use when: contiguous subarray/substring with a constraint.

```python
# Template: variable-size sliding window
def sliding_window(s, k):
    left = 0
    window = {}  # or counter
    result = 0
    for right in range(len(s)):
        # expand: add s[right] to window
        window[s[right]] = window.get(s[right], 0) + 1
        # shrink: while window is invalid
        while window_invalid(window):
            window[s[left]] -= 1
            if window[s[left]] == 0:
                del window[s[left]]
            left += 1
        result = max(result, right - left + 1)
    return result
```

---

## Problem 1: Two Sum II (Easy) — LC 167

**Given:** Sorted array, find two numbers that add to target.

```python
def twoSum(numbers, target):
    l, r = 0, len(numbers) - 1
    while l < r:
        s = numbers[l] + numbers[r]
        if s == target:
            return [l + 1, r + 1]
        elif s < target:
            l += 1
        else:
            r -= 1
```

**Complexity:** O(n) time, O(1) space.

---

## Problem 2: Container With Most Water (Medium) — LC 11

**Given:** Array of heights, find max area between two lines.

```python
def maxArea(height):
    l, r = 0, len(height) - 1
    res = 0
    while l < r:
        res = max(res, min(height[l], height[r]) * (r - l))
        if height[l] < height[r]:
            l += 1
        else:
            r -= 1
    return res
```

**Complexity:** O(n) time, O(1) space.

**Why it works:** Moving the shorter line inward is the only way to potentially increase area.

---

## Problem 3: Longest Substring Without Repeating Characters (Medium) — LC 3

**Given:** String, find length of longest substring without repeating chars.

```python
def lengthOfLongestSubstring(s):
    seen = {}
    l = res = 0
    for r, c in enumerate(s):
        if c in seen and seen[c] >= l:
            l = seen[c] + 1
        seen[c] = r
        res = max(res, r - l + 1)
    return res
```

**Complexity:** O(n) time, O(min(n, 26)) space.

---

## Problem 4: Minimum Window Substring (Hard) — LC 76

**Given:** Strings s and t, find minimum window in s containing all chars of t.

```python
from collections import Counter

def minWindow(s, t):
    need = Counter(t)
    missing = len(t)
    l = start = 0
    end = float('inf')
    for r, c in enumerate(s):
        if need[c] > 0:
            missing -= 1
        need[c] -= 1
        while missing == 0:
            if r - l < end - start:
                start, end = l, r
            need[s[l]] += 1
            if need[s[l]] > 0:
                missing += 1
            l += 1
    return s[start:end + 1] if end < float('inf') else ""
```

**Complexity:** O(n) time, O(k) space where k = unique chars in t.

---

## Problem 5: Trapping Rain Water (Hard) — LC 42

**Given:** Array of heights, compute trapped water.

```python
def trap(height):
    l, r = 0, len(height) - 1
    l_max = r_max = res = 0
    while l < r:
        if height[l] < height[r]:
            l_max = max(l_max, height[l])
            res += l_max - height[l]
            l += 1
        else:
            r_max = max(r_max, height[r])
            res += r_max - height[r]
            r -= 1
    return res
```

**Complexity:** O(n) time, O(1) space.

---

## Pattern Recognition Tips

| Signal                              | Pattern                                       |
| ----------------------------------- | --------------------------------------------- |
| Sorted array + pair                 | Two pointers (opposite ends)                  |
| Contiguous subarray with constraint | Sliding window                                |
| "Longest/shortest substring"        | Sliding window + hashmap                      |
| Palindrome check                    | Two pointers (center expand or opposite ends) |
| Remove duplicates in-place          | Two pointers (same direction)                 |

---

[← Overview](./chapter-00-overview.md) | [next →](./chapter-02-hashmaps.md)

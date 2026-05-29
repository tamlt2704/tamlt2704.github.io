# Chapter 8: Binary Search

[← Dynamic Programming](./chapter-07-dynamic-programming.md) | [next →](./chapter-09-greedy.md)

---

## Patterns

### Binary Search on Sorted Array

```python
def binary_search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

### Binary Search on Answer (Minimize/Maximize)

```python
def binary_search_on_answer(lo, hi):
    while lo < hi:
        mid = (lo + hi) // 2
        if feasible(mid):
            hi = mid       # minimize: shrink right
        else:
            lo = mid + 1
    return lo

# For maximize:
def binary_search_maximize(lo, hi):
    while lo < hi:
        mid = (lo + hi + 1) // 2  # round up to avoid infinite loop
        if feasible(mid):
            lo = mid
        else:
            hi = mid - 1
    return lo
```

---

## Problem 1: Binary Search (Easy) — LC 704

```python
def search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

**Complexity:** O(log n) time, O(1) space.

---

## Problem 2: Search in Rotated Sorted Array (Medium) — LC 33

```python
def search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:  # left half sorted
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:  # right half sorted
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1
```

**Complexity:** O(log n) time, O(1) space.

**Key insight:** One half is always sorted; check if target is in that half.

---

## Problem 3: Koko Eating Bananas (Medium) — LC 875

**Given:** Piles of bananas, find minimum eating speed to finish in h hours.

```python
import math

def minEatingSpeed(piles, h):
    lo, hi = 1, max(piles)
    while lo < hi:
        mid = (lo + hi) // 2
        if sum(math.ceil(p / mid) for p in piles) <= h:
            hi = mid
        else:
            lo = mid + 1
    return lo
```

**Complexity:** O(n · log(max(piles))) time, O(1) space.

**Pattern:** Binary search on answer — minimize speed where feasible(speed) = can finish in time.

---

## Problem 4: Find Minimum in Rotated Sorted Array (Medium) — LC 153

```python
def findMin(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        else:
            hi = mid
    return nums[lo]
```

**Complexity:** O(log n) time, O(1) space.

---

## Problem 5: Median of Two Sorted Arrays (Hard) — LC 4

```python
def findMedianSortedArrays(nums1, nums2):
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1
    m, n = len(nums1), len(nums2)
    lo, hi = 0, m
    while lo <= hi:
        i = (lo + hi) // 2
        j = (m + n + 1) // 2 - i
        left1 = nums1[i-1] if i > 0 else float('-inf')
        right1 = nums1[i] if i < m else float('inf')
        left2 = nums2[j-1] if j > 0 else float('-inf')
        right2 = nums2[j] if j < n else float('inf')
        if left1 <= right2 and left2 <= right1:
            if (m + n) % 2:
                return max(left1, left2)
            return (max(left1, left2) + min(right1, right2)) / 2
        elif left1 > right2:
            hi = i - 1
        else:
            lo = i + 1
```

**Complexity:** O(log(min(m, n))) time, O(1) space.

---

## Pattern Recognition Tips

| Signal                                | Pattern                              |
| ------------------------------------- | ------------------------------------ |
| Sorted array + search                 | Classic binary search                |
| "Minimum speed/capacity to achieve X" | Binary search on answer (minimize)   |
| "Maximum value where condition holds" | Binary search on answer (maximize)   |
| Rotated sorted array                  | Binary search with sorted-half check |
| "Find boundary / first true"          | bisect_left / lo < hi template       |

---

[← Dynamic Programming](./chapter-07-dynamic-programming.md) | [next →](./chapter-09-greedy.md)

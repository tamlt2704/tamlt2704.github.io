# Chapter 2: HashMaps & Sets

[← Arrays & Strings](./chapter-01-arrays-strings.md) | [next →](./chapter-03-linked-lists.md)

---

## Patterns

### Frequency Counting

```python
from collections import Counter

def frequency_pattern(arr):
    count = Counter(arr)
    # or manually:
    count = {}
    for x in arr:
        count[x] = count.get(x, 0) + 1
```

### Two Sum Pattern (Index Lookup)

```python
def two_sum_pattern(arr, target):
    seen = {}
    for i, x in enumerate(arr):
        complement = target - x
        if complement in seen:
            return [seen[complement], i]
        seen[x] = i
```

### Grouping Pattern

```python
from collections import defaultdict

def group_by_key(items):
    groups = defaultdict(list)
    for item in items:
        key = compute_key(item)
        groups[key].append(item)
    return list(groups.values())
```

---

## Problem 1: Two Sum (Easy) — LC 1

```python
def twoSum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        if target - n in seen:
            return [seen[target - n], i]
        seen[n] = i
```

**Complexity:** O(n) time, O(n) space.

---

## Problem 2: Group Anagrams (Medium) — LC 49

```python
from collections import defaultdict

def groupAnagrams(strs):
    groups = defaultdict(list)
    for s in strs:
        groups[tuple(sorted(s))].append(s)
    return list(groups.values())
```

**Complexity:** O(n · k log k) time, O(n · k) space, where k = max string length.

**Optimization:** Use character count tuple as key for O(n · k) time:

```python
def groupAnagrams(strs):
    groups = defaultdict(list)
    for s in strs:
        key = [0] * 26
        for c in s:
            key[ord(c) - ord('a')] += 1
        groups[tuple(key)].append(s)
    return list(groups.values())
```

---

## Problem 3: Longest Consecutive Sequence (Medium) — LC 128

**Given:** Unsorted array, find length of longest consecutive sequence in O(n).

```python
def longestConsecutive(nums):
    num_set = set(nums)
    res = 0
    for n in num_set:
        if n - 1 not in num_set:  # start of sequence
            length = 1
            while n + length in num_set:
                length += 1
            res = max(res, length)
    return res
```

**Complexity:** O(n) time, O(n) space.

**Key insight:** Only start counting from sequence beginnings (no predecessor).

---

## Problem 4: Subarray Sum Equals K (Medium) — LC 560

**Given:** Array, count subarrays with sum = k.

```python
def subarraySum(nums, k):
    prefix = {0: 1}
    curr = res = 0
    for n in nums:
        curr += n
        res += prefix.get(curr - k, 0)
        prefix[curr] = prefix.get(curr, 0) + 1
    return res
```

**Complexity:** O(n) time, O(n) space.

**Pattern:** Prefix sum + hashmap = count subarrays with target sum.

---

## Problem 5: First Missing Positive (Hard) — LC 41

**Given:** Unsorted array, find smallest missing positive integer in O(n) time, O(1) space.

```python
def firstMissingPositive(nums):
    n = len(nums)
    for i in range(n):
        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
            nums[nums[i] - 1], nums[i] = nums[i], nums[nums[i] - 1]
    for i in range(n):
        if nums[i] != i + 1:
            return i + 1
    return n + 1
```

**Complexity:** O(n) time, O(1) space.

**Trick:** Use the array itself as a hashmap — place each number at its "correct" index.

---

## Pattern Recognition Tips

| Signal                        | Pattern                   |
| ----------------------------- | ------------------------- |
| "Find pair/complement"        | HashMap index lookup      |
| "Count subarrays with sum X"  | Prefix sum + HashMap      |
| "Group by property"           | HashMap with computed key |
| "Find duplicates / frequency" | Counter / Set             |
| "O(1) lookup needed"          | HashSet                   |

---

[← Arrays & Strings](./chapter-01-arrays-strings.md) | [next →](./chapter-03-linked-lists.md)

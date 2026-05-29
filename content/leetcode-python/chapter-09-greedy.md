# Chapter 9: Greedy & Intervals

[← Binary Search](./chapter-08-binary-search.md) | [next →](./chapter-10-advanced.md)

---

## Patterns

### Greedy Choice Property

Make the locally optimal choice at each step. Works when:

- Local optimum leads to global optimum
- No need to reconsider past choices

### Interval Scheduling

```python
# Template: sort by end time, greedily pick non-overlapping
def max_non_overlapping(intervals):
    intervals.sort(key=lambda x: x[1])
    count = 0
    end = float('-inf')
    for s, e in intervals:
        if s >= end:
            count += 1
            end = e
    return count
```

### Merge Intervals

```python
def merge(intervals):
    intervals.sort()
    merged = [intervals[0]]
    for s, e in intervals[1:]:
        if s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    return merged
```

---

## Problem 1: Maximum Subarray (Medium) — LC 53

```python
def maxSubArray(nums):
    curr = res = nums[0]
    for n in nums[1:]:
        curr = max(n, curr + n)
        res = max(res, curr)
    return res
```

**Complexity:** O(n) time, O(1) space.

**Greedy insight:** Reset running sum when it becomes negative.

---

## Problem 2: Jump Game (Medium) — LC 55

```python
def canJump(nums):
    reach = 0
    for i, n in enumerate(nums):
        if i > reach:
            return False
        reach = max(reach, i + n)
    return True
```

**Complexity:** O(n) time, O(1) space.

---

## Problem 3: Merge Intervals (Medium) — LC 56

```python
def merge(intervals):
    intervals.sort()
    merged = [intervals[0]]
    for s, e in intervals[1:]:
        if s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    return merged
```

**Complexity:** O(n log n) time, O(n) space.

---

## Problem 4: Non-overlapping Intervals (Medium) — LC 435

**Given:** Find minimum number of intervals to remove for no overlap.

```python
def eraseOverlapIntervals(intervals):
    intervals.sort(key=lambda x: x[1])
    count = 0
    end = float('-inf')
    for s, e in intervals:
        if s >= end:
            end = e
        else:
            count += 1
    return count
```

**Complexity:** O(n log n) time, O(1) space.

**Key insight:** Sort by end time. Keep intervals that end earliest to leave room for more.

---

## Problem 5: Meeting Rooms II (Medium) — LC 253

**Given:** Find minimum number of conference rooms needed.

```python
import heapq

def minMeetingRooms(intervals):
    intervals.sort()
    heap = []  # end times of active meetings
    for s, e in intervals:
        if heap and heap[0] <= s:
            heapq.heappop(heap)
        heapq.heappush(heap, e)
    return len(heap)
```

**Complexity:** O(n log n) time, O(n) space.

**Alternative (sweep line):**

```python
def minMeetingRooms(intervals):
    events = []
    for s, e in intervals:
        events.append((s, 1))
        events.append((e, -1))
    events.sort()
    curr = res = 0
    for _, delta in events:
        curr += delta
        res = max(res, curr)
    return res
```

---

## Pattern Recognition Tips

| Signal                            | Pattern                      |
| --------------------------------- | ---------------------------- |
| "Maximum non-overlapping"         | Sort by end, greedy pick     |
| "Merge overlapping intervals"     | Sort by start, merge         |
| "Minimum rooms / resources"       | Sweep line or min-heap       |
| "Can reach end / jump game"       | Track farthest reachable     |
| "Minimum removals for no overlap" | Sort by end, count conflicts |

---

[← Binary Search](./chapter-08-binary-search.md) | [next →](./chapter-10-advanced.md)

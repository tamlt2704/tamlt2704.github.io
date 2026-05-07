# Chapter 2: The Sorted Shortcut — Binary Search

[← Chapter 1: Linear Search](chapter-01-linear-search.md) | [Chapter 3: Sorting Basics →](chapter-03-basic-sorting.md)

---

## The Problem

The dispatch system makes 50,000 lookups against 100,000 packages every morning. Linear search: 45 minutes. Priya wants it under 1 second.

You know the trick: if the data is sorted, you can eliminate half the remaining options with each comparison. Like guessing a number between 1 and 100 — you don't start at 1 and count up. You start at 50 and ask "higher or lower?"

But RouteMaster's packages aren't sorted. They're appended in arrival order. Step one: sort them by tracking number. Step two: binary search.

## The Intuition

You're looking for tracking number `RM-058291` in a sorted list of 100,000 packages.

```
Step 1: Check the middle (index 50,000) → RM-050000
        058291 > 050000 → target is in the RIGHT half

Step 2: Check the middle of the right half (index 75,000) → RM-075000
        058291 < 075000 → target is in the LEFT half (of this section)

Step 3: Check the middle (index 62,500) → RM-062500
        058291 < 062500 → LEFT half

Step 4: Check the middle (index 56,250) → RM-056250
        058291 > 056250 → RIGHT half

Step 5: Check the middle (index 59,375) → RM-059375
        058291 < 059375 → LEFT half

... (a few more steps)

Step 17: Check index 58,291 → RM-058291
         FOUND!
```

17 comparisons instead of 100,000. That's the power of halving.

## The Algorithm

```python
def binary_search(sorted_items, target):
    """
    Search a sorted list by repeatedly halving the search space.
    Returns the index if found, -1 if not.
    """
    left = 0
    right = len(sorted_items) - 1

    while left <= right:
        mid = (left + right) // 2
        current = sorted_items[mid]

        if current == target:
            return mid
        elif current < target:
            left = mid + 1   # Target is in the right half
        else:
            right = mid - 1  # Target is in the left half

    return -1  # Not found
```

### Step-by-Step Trace

Searching for `42` in `[3, 8, 17, 42, 55, 91]`:

```
Initial: left=0, right=5

Step 1: mid = (0+5)//2 = 2
        items[2] = 17
        17 < 42 → left = 3

Step 2: mid = (3+5)//2 = 4
        items[4] = 55
        55 > 42 → right = 3

Step 3: mid = (3+3)//2 = 3
        items[3] = 42
        42 == 42 → FOUND! Return 3
```

3 comparisons for 6 elements. log₂(6) ≈ 2.6, rounded up = 3. ✓

### Not Found Case

Searching for `20` in `[3, 8, 17, 42, 55, 91]`:

```
Initial: left=0, right=5

Step 1: mid=2, items[2]=17, 17 < 20 → left=3
Step 2: mid=4, items[4]=55, 55 > 20 → right=3
Step 3: mid=3, items[3]=42, 42 > 20 → right=2

left=3 > right=2 → STOP. Not found. Return -1.
```

The search space collapsed to nothing. The target doesn't exist.

## Complexity Analysis

Each step halves the search space:
- Start: n elements
- After step 1: n/2 elements
- After step 2: n/4 elements
- After step k: n/2ᵏ elements

We stop when n/2ᵏ = 1, which means k = log₂(n).

| n | Max comparisons (log₂ n) |
|---|---|
| 100 | 7 |
| 1,000 | 10 |
| 10,000 | 14 |
| 100,000 | 17 |
| 1,000,000 | 20 |
| 1,000,000,000 | 30 |

A billion elements: 30 comparisons. That's O(log n).

## Benchmarking: Linear vs Binary

```python
import time
import random

def benchmark_comparison(sizes):
    for n in sizes:
        # Sorted list of tracking numbers
        packages = [f"RM-{i:06d}" for i in range(n)]
        target = f"RM-{n-1:06d}"  # Worst case for linear (last element)

        # Linear search
        start = time.time()
        for _ in range(1000):
            linear_search(packages, target)
        linear_time = (time.time() - start) / 1000

        # Binary search
        start = time.time()
        for _ in range(1000):
            binary_search(packages, target)
        binary_time = (time.time() - start) / 1000

        speedup = linear_time / binary_time
        print(f"n={n:>10,} | Linear: {linear_time*1000:.3f}ms | Binary: {binary_time*1000:.3f}ms | Speedup: {speedup:.0f}x")

benchmark_comparison([1_000, 10_000, 100_000, 1_000_000])
```

Output:
```
n=     1,000 | Linear: 0.045ms | Binary: 0.003ms | Speedup: 15x
n=    10,000 | Linear: 0.450ms | Binary: 0.004ms | Speedup: 112x
n=   100,000 | Linear: 4.500ms | Binary: 0.005ms | Speedup: 900x
n= 1,000,000 | Linear: 45.00ms | Binary: 0.006ms | Speedup: 7,500x
```

At 100,000 packages: 900x faster. The dispatch system goes from 45 minutes to 3 seconds.

## The Requirement: Sorted Data

Binary search only works on sorted data. If the list isn't sorted, the "go left/go right" decision is meaningless.

```python
# This DOES NOT WORK:
unsorted = [42, 3, 91, 17, 8, 55]
binary_search(unsorted, 17)  # Might return -1 (wrong!) because it goes right at 91
```

RouteMaster's packages arrive in random order. You need to sort them first. Sorting costs O(n log n) — but you sort once and search many times. The amortized cost is:

```
Sort once:     O(n log n)  = 100,000 × 17 = 1,700,000 operations
Search 50,000: O(m × log n) = 50,000 × 17 = 850,000 operations
Total:         2,550,000 operations

vs. Linear search 50,000 times:
               O(m × n) = 50,000 × 100,000 = 5,000,000,000 operations
```

Sort + binary search: 2.5 million operations.
Linear search: 5 billion operations.

2,000x fewer operations. Sort once, search many.

## RouteMaster's Sorted Registry

```python
class SortedPackageRegistry:
    def __init__(self):
        self.packages = []  # Kept sorted by tracking number
        self._is_sorted = True

    def add(self, package):
        """Add package — marks list as needing re-sort."""
        self.packages.append(package)
        self._is_sorted = False

    def _ensure_sorted(self):
        if not self._is_sorted:
            self.packages.sort(key=lambda p: p.tracking)
            self._is_sorted = True

    def find_by_tracking(self, tracking_number):
        """Binary search — O(log n) after sorting."""
        self._ensure_sorted()

        left, right = 0, len(self.packages) - 1
        while left <= right:
            mid = (left + right) // 2
            current = self.packages[mid].tracking

            if current == tracking_number:
                return self.packages[mid]
            elif current < tracking_number:
                left = mid + 1
            else:
                right = mid - 1

        return None

    def find_insertion_point(self, tracking_number):
        """Where would this tracking number go? (for sorted insert)"""
        self._ensure_sorted()
        left, right = 0, len(self.packages)
        while left < right:
            mid = (left + right) // 2
            if self.packages[mid].tracking < tracking_number:
                left = mid + 1
            else:
                right = mid
        return left
```

## Variations: Finding More Than Exact Matches

### Find First Occurrence (Lower Bound)

Multiple packages might share a property. Find the first one:

```python
def lower_bound(sorted_items, target):
    """
    Find the leftmost position where target could be inserted
    to maintain sorted order. (First element >= target)
    """
    left, right = 0, len(sorted_items)
    while left < right:
        mid = (left + right) // 2
        if sorted_items[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left
```

### Find Last Occurrence (Upper Bound)

```python
def upper_bound(sorted_items, target):
    """
    Find the rightmost position where target could be inserted.
    (First element > target)
    """
    left, right = 0, len(sorted_items)
    while left < right:
        mid = (left + right) // 2
        if sorted_items[mid] <= target:
            left = mid + 1
        else:
            right = mid
    return left
```

### Range Query: All Packages in a Tracking Number Range

```python
def find_range(sorted_packages, start_tracking, end_tracking):
    """Find all packages with tracking numbers in [start, end]."""
    left_idx = lower_bound([p.tracking for p in sorted_packages], start_tracking)
    right_idx = upper_bound([p.tracking for p in sorted_packages], end_tracking)
    return sorted_packages[left_idx:right_idx]

# "Show me all packages RM-050000 through RM-060000"
results = find_range(registry.packages, "RM-050000", "RM-060000")
# Returns ~10,000 packages in O(log n + k) where k is result count
```

## Common Bug: Off-by-One Errors

Binary search is notoriously tricky to implement correctly. The most common bugs:

### Bug 1: Infinite Loop

```python
# WRONG: mid never changes when left == right - 1
mid = (left + right) // 2  # If left=3, right=4: mid=3 forever
# Fix: ensure left or right always moves PAST mid
left = mid + 1   # Not mid
right = mid - 1  # Not mid
```

### Bug 2: Integer Overflow (in other languages)

```python
# In Java/C++, this overflows for large arrays:
mid = (left + right) / 2  # left + right might exceed INT_MAX

# Fix:
mid = left + (right - left) // 2
```

Python handles big integers natively, so this isn't an issue in Python. But know it for interviews and other languages.

### Bug 3: Wrong Boundary Condition

```python
# WRONG: misses the last element
while left < right:  # Should be left <= right for exact match
    ...

# left < right: for lower_bound/upper_bound (insertion point)
# left <= right: for exact match search
```

## Binary Search on Answers

Binary search isn't just for sorted arrays. It works on any monotonic function — any situation where "too small" transitions to "just right" transitions to "too big."

### Example: Maximum Packages Per Van

"What's the minimum van capacity needed to deliver all packages in 8 hours?"

```python
def can_deliver_all(packages, van_capacity, max_hours):
    """Can we deliver all packages with vans of this capacity in max_hours?"""
    hours_needed = 0
    current_load = 0
    for package in packages:
        if current_load + package.weight > van_capacity:
            hours_needed += 1  # Need a new trip
            current_load = 0
        current_load += package.weight
    hours_needed += 1  # Last trip
    return hours_needed <= max_hours

def minimum_van_capacity(packages, max_hours):
    """Binary search on the answer."""
    left = max(p.weight for p in packages)  # At minimum, fit the heaviest package
    right = sum(p.weight for p in packages)  # At maximum, one trip carries everything

    while left < right:
        mid = (left + right) // 2
        if can_deliver_all(packages, mid, max_hours):
            right = mid  # This capacity works — try smaller
        else:
            left = mid + 1  # Too small — need bigger

    return left
```

The "sorted array" here is the range of possible capacities. Below some threshold, delivery is impossible. Above it, it's possible. Binary search finds the exact threshold.

## What You Learned

- **Binary search** — halve the search space each step, O(log n)
- **Requirement** — data must be sorted
- **Amortized cost** — sort once O(n log n), search many times O(log n) each
- **Lower/upper bound** — find insertion points and ranges
- **Binary search on answers** — works on any monotonic condition
- **Common bugs** — off-by-one, infinite loops, overflow

The dispatch system now runs in 3 seconds instead of 45 minutes. Priya is satisfied.

But there's a prerequisite you glossed over: "sort the packages first." You used Python's built-in `sort()`. What does it actually do? How fast is it? And what happens when you need to sort 50,000 packages by delivery deadline every morning — is there a faster way than what you're using?

Time to understand sorting from the ground up.

That's Chapter 3.

---

[← Chapter 1: Linear Search](chapter-01-linear-search.md) | [Chapter 3: Sorting Basics →](chapter-03-basic-sorting.md)

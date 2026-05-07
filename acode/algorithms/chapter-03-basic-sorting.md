# Chapter 3: Sorting by Deadline — Selection Sort and Insertion Sort

[← Chapter 2: Binary Search](chapter-02-binary-search.md) | [Chapter 4: Merge Sort →](chapter-04-merge-sort.md)

---

## The Problem

Every morning at 6 AM, Dispatch Dan needs the day's packages sorted by delivery deadline. Hospitals and pharmacies get "before 9 AM" deadlines. Regular deliveries get "before 6 PM." Low-priority gets "before end of day."

The current system doesn't sort at all — drivers pick up packages in whatever order they were loaded. Marcus (senior driver) has been manually reorganizing his van every morning. "Your system gave me a 6 PM package on top of a 9 AM package. I had to dig through 40 boxes."

You need to sort 50,000 packages by deadline. Let's start with the simplest approaches and see where they break.

## Selection Sort: Find the Minimum, Repeat

The most intuitive sorting algorithm: scan the entire list, find the smallest element, put it first. Then find the second smallest, put it second. Repeat.

```python
def selection_sort(items, key=lambda x: x):
    """
    Repeatedly find the minimum and place it at the front.
    """
    n = len(items)
    for i in range(n):
        # Find the index of the minimum element in items[i:]
        min_idx = i
        for j in range(i + 1, n):
            if key(items[j]) < key(items[min_idx]):
                min_idx = j
        # Swap it into position i
        items[i], items[min_idx] = items[min_idx], items[i]
    return items
```

### Step-by-Step

Sorting `[64, 25, 12, 22, 11]`:

```
Pass 1: Find min in [64, 25, 12, 22, 11] → 11 at index 4
         Swap items[0] and items[4]
         → [11, 25, 12, 22, 64]

Pass 2: Find min in [25, 12, 22, 64] → 12 at index 2
         Swap items[1] and items[2]
         → [11, 12, 25, 22, 64]

Pass 3: Find min in [25, 22, 64] → 22 at index 3
         Swap items[2] and items[3]
         → [11, 12, 22, 25, 64]

Pass 4: Find min in [25, 64] → 25 at index 3
         No swap needed
         → [11, 12, 22, 25, 64]

Done! 4 passes for 5 elements.
```

### Complexity

- Outer loop: n iterations
- Inner loop: n-1, n-2, n-3, ... 1 comparisons
- Total: n(n-1)/2 = **O(n²)**

| n | Comparisons | Time (approx) |
|---|---|---|
| 100 | 4,950 | instant |
| 1,000 | 499,500 | 0.05s |
| 10,000 | 49,995,000 | 5s |
| 50,000 | 1,249,975,000 | 125s |

50,000 packages: over 2 minutes. Dispatch Dan is not waiting 2 minutes at 6 AM.

### Properties

| Property | Value |
|---|---|
| Time complexity | O(n²) always |
| Space complexity | O(1) — in-place |
| Stable? | No (swaps can change relative order of equal elements) |
| Adaptive? | No (same time whether sorted or not) |

Selection sort always does n² comparisons regardless of input. Even if the list is already sorted, it still scans everything.

## Insertion Sort: Build the Sorted Portion

Think of sorting a hand of cards. You pick up cards one at a time and insert each into its correct position among the cards you've already sorted.

```python
def insertion_sort(items, key=lambda x: x):
    """
    Build a sorted portion from left to right.
    Each new element is inserted into its correct position.
    """
    n = len(items)
    for i in range(1, n):
        current = items[i]
        current_key = key(current)
        j = i - 1

        # Shift elements right until we find the correct position
        while j >= 0 and key(items[j]) > current_key:
            items[j + 1] = items[j]
            j -= 1

        items[j + 1] = current
    return items
```

### Step-by-Step

Sorting `[64, 25, 12, 22, 11]`:

```
Start: [64 | 25, 12, 22, 11]  (left of | is "sorted")

Pass 1: Insert 25 into [64]
         25 < 64 → shift 64 right
         → [25, 64 | 12, 22, 11]

Pass 2: Insert 12 into [25, 64]
         12 < 64 → shift 64 right
         12 < 25 → shift 25 right
         → [12, 25, 64 | 22, 11]

Pass 3: Insert 22 into [12, 25, 64]
         22 < 64 → shift 64 right
         22 < 25 → shift 25 right
         22 > 12 → stop
         → [12, 22, 25, 64 | 11]

Pass 4: Insert 11 into [12, 22, 25, 64]
         11 < 64 → shift
         11 < 25 → shift
         11 < 22 → shift
         11 < 12 → shift
         → [11, 12, 22, 25, 64]

Done!
```

### Complexity

| Case | Comparisons | When |
|---|---|---|
| Best case | O(n) | Already sorted (inner loop never executes) |
| Average case | O(n²) | Random order |
| Worst case | O(n²) | Reverse sorted |

### The Key Insight: Insertion Sort Is Adaptive

If the data is *almost* sorted, insertion sort is nearly O(n). Each element only shifts a few positions.

```python
# Nearly sorted: each element is at most 3 positions from its correct spot
nearly_sorted = [1, 3, 2, 5, 4, 7, 6, 9, 8, 10]
# Insertion sort: ~20 comparisons (nearly linear)

# Random order: elements are far from their correct positions
random_order = [7, 3, 9, 1, 5, 10, 2, 8, 4, 6]
# Insertion sort: ~45 comparisons (quadratic)
```

### Properties

| Property | Value |
|---|---|
| Time complexity | O(n²) worst/average, O(n) best |
| Space complexity | O(1) — in-place |
| Stable? | Yes (equal elements maintain relative order) |
| Adaptive? | Yes (fast on nearly-sorted data) |

## Sorting RouteMaster's Packages

```python
class Package:
    def __init__(self, tracking, deadline, priority, weight):
        self.tracking = tracking
        self.deadline = deadline  # datetime
        self.priority = priority  # 1=urgent, 2=normal, 3=low
        self.weight = weight

# Sort by deadline (earliest first)
packages = [
    Package("RM-001", "2024-01-15 09:00", 1, 2.5),
    Package("RM-002", "2024-01-15 18:00", 3, 1.0),
    Package("RM-003", "2024-01-15 09:00", 1, 5.0),
    Package("RM-004", "2024-01-15 12:00", 2, 3.0),
    Package("RM-005", "2024-01-15 18:00", 2, 0.5),
]

# Using insertion sort with a custom key
insertion_sort(packages, key=lambda p: (p.deadline, p.priority))
# Sorts by deadline first, then by priority within the same deadline
```

## Stability: Why It Matters

A **stable** sort preserves the relative order of equal elements.

RouteMaster sorts packages first by priority, then by deadline:

```python
# Step 1: Sort by priority (secondary key)
packages.sort(key=lambda p: p.priority)  # Must be stable!

# Step 2: Sort by deadline (primary key)
packages.sort(key=lambda p: p.deadline)  # Must be stable!

# Result: sorted by deadline, with ties broken by priority
```

If the sort is unstable, step 2 might scramble the priority ordering within the same deadline. Insertion sort is stable. Selection sort is not.

## Benchmarking: When O(n²) Hurts

```python
import time
import random

def benchmark_sorts(sizes):
    for n in sizes:
        data = list(range(n))
        random.shuffle(data)

        # Selection sort
        copy1 = data.copy()
        start = time.time()
        selection_sort(copy1)
        sel_time = time.time() - start

        # Insertion sort
        copy2 = data.copy()
        start = time.time()
        insertion_sort(copy2)
        ins_time = time.time() - start

        print(f"n={n:>6,} | Selection: {sel_time:.3f}s | Insertion: {ins_time:.3f}s")

benchmark_sorts([100, 1_000, 5_000, 10_000, 50_000])
```

Output:
```
n=   100 | Selection: 0.000s | Insertion: 0.000s
n= 1,000 | Selection: 0.030s | Insertion: 0.025s
n= 5,000 | Selection: 0.750s | Insertion: 0.600s
n=10,000 | Selection: 3.000s | Insertion: 2.400s
n=50,000 | Selection: 75.00s | Insertion: 60.00s
```

50,000 packages: over a minute. Both are O(n²). Both are unacceptable for the morning dispatch.

### But What About Nearly-Sorted Data?

```python
def benchmark_nearly_sorted(n=50_000):
    # Nearly sorted: swap 1% of adjacent elements
    data = list(range(n))
    for _ in range(n // 100):
        i = random.randint(0, n - 2)
        data[i], data[i + 1] = data[i + 1], data[i]

    copy = data.copy()
    start = time.time()
    insertion_sort(copy)
    print(f"Insertion sort (nearly sorted, n={n:,}): {time.time() - start:.3f}s")
    # ~0.5s instead of 60s!
```

Insertion sort on nearly-sorted data: 0.5 seconds. That's 120x faster than random data. This is why real-world sorting algorithms (like Timsort, Python's built-in) use insertion sort for small or nearly-sorted runs.

## When to Use Each

| Algorithm | Use When |
|---|---|
| Selection sort | Never in production. Educational only. |
| Insertion sort | Small arrays (n < 50), nearly-sorted data, online sorting (data arrives one at a time) |
| Neither | n > 1,000 with random data |

### Insertion Sort in Practice

Python's `sorted()` uses Timsort, which internally uses insertion sort for small runs (< 64 elements). Java's `Arrays.sort()` uses insertion sort for arrays smaller than 47 elements. They're not useless — they're building blocks.

## The Wall: O(n²) Can't Scale

Both algorithms hit the same wall: nested loops. For every element, they potentially examine every other element. n × n = n².

To break through O(n²), you need a fundamentally different strategy. You can't just optimize the inner loop — you need to reduce the number of comparisons from n² to n log n.

The key insight: **divide and conquer**. Instead of sorting the whole list at once, split it in half, sort each half, and merge the results. Sorting two halves of size n/2 is much cheaper than sorting one list of size n.

That's merge sort. That's Chapter 4.

## What You Learned

- **Selection sort** — find minimum, place it, repeat. O(n²) always.
- **Insertion sort** — insert each element into its sorted position. O(n²) worst, O(n) best.
- **Stability** — preserving relative order of equal elements
- **Adaptivity** — insertion sort is fast on nearly-sorted data
- **The O(n²) wall** — nested loops can't scale past ~10,000 elements
- **Practical use** — insertion sort is used inside faster algorithms for small subarrays

Dispatch Dan can't wait 60 seconds. He needs 50,000 packages sorted in under a second. You need to break through the quadratic barrier.

---

[← Chapter 2: Binary Search](chapter-02-binary-search.md) | [Chapter 4: Merge Sort →](chapter-04-merge-sort.md)

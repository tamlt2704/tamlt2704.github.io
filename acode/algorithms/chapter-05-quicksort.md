# Chapter 5: Sorting In-Place — Quicksort

[← Chapter 4: Merge Sort](chapter-04-merge-sort.md) | [Chapter 6: Priority Queues →](chapter-06-heaps.md)

---

## The Problem

Merge sort works. 50,000 packages in 0.2 seconds. But it allocates 50,000 extra slots — doubling memory usage during the sort. The route planner runs simultaneously and needs that memory.

Priya: "Can you sort without the extra allocation?"

You need an in-place O(n log n) sort. Quicksort: same divide-and-conquer idea, but instead of splitting arbitrarily and merging, you **partition** around a pivot and recurse on the pieces.

## The Idea

1. Pick a **pivot** element
2. **Partition**: rearrange so everything < pivot is left, everything > pivot is right
3. The pivot is now in its final position
4. Recursively sort the left and right portions

No merging needed — after partitioning, elements are already on the correct side.

## Partitioning

The core operation. Given a pivot, rearrange the array in-place:

```python
def partition(items, low, high):
    """
    Lomuto partition scheme.
    Pivot = last element. Returns pivot's final index.
    """
    pivot = items[high]
    i = low - 1  # Boundary of "less than pivot" region

    for j in range(low, high):
        if items[j] <= pivot:
            i += 1
            items[i], items[j] = items[j], items[i]

    # Place pivot in its correct position
    items[i + 1], items[high] = items[high], items[i + 1]
    return i + 1
```

### Trace

Partitioning `[8, 3, 7, 1, 5, 2, 6, 4]` with pivot = 4 (last element):

```
pivot = 4, i = -1

j=0: items[0]=8, 8 > 4 → skip
j=1: items[1]=3, 3 ≤ 4 → i=0, swap items[0]↔items[1] → [3, 8, 7, 1, 5, 2, 6, 4]
j=2: items[2]=7, 7 > 4 → skip
j=3: items[3]=1, 1 ≤ 4 → i=1, swap items[1]↔items[3] → [3, 1, 7, 8, 5, 2, 6, 4]
j=4: items[4]=5, 5 > 4 → skip
j=5: items[5]=2, 2 ≤ 4 → i=2, swap items[2]↔items[5] → [3, 1, 2, 8, 5, 7, 6, 4]
j=6: items[6]=6, 6 > 4 → skip

Place pivot: swap items[3]↔items[7] → [3, 1, 2, 4, 5, 7, 6, 8]
                                              ↑ pivot at index 3

Return 3
```

After partition: `[3, 1, 2]` are left of pivot, `[5, 7, 6, 8]` are right. Pivot (4) is in its final sorted position.

## The Full Algorithm

```python
def quicksort(items, low=0, high=None):
    """
    In-place divide and conquer. O(n log n) average.
    """
    if high is None:
        high = len(items) - 1

    if low < high:
        # Partition and get pivot's final position
        pivot_idx = partition(items, low, high)

        # Recursively sort left and right of pivot
        quicksort(items, low, pivot_idx - 1)
        quicksort(items, pivot_idx + 1, high)

    return items
```

### Why It's In-Place

No new lists created. All swaps happen within the original array. Space complexity: O(log n) for the recursion stack (the call frames), but O(1) extra data space.

## The Pivot Problem

Quicksort's performance depends entirely on pivot choice.

### Best Case: Pivot Splits Evenly

If the pivot is always the median, each partition splits the array in half. Like merge sort: log n levels, n work per level = O(n log n).

### Worst Case: Pivot Is Always the Extreme

If the pivot is always the smallest (or largest) element, one partition has n-1 elements and the other has 0. That's n levels of n work = **O(n²)**.

```python
# Worst case for "last element" pivot: already sorted data!
sorted_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# Pivot = 10 → partition: [1,2,3,4,5,6,7,8,9] and []
# Pivot = 9  → partition: [1,2,3,4,5,6,7,8] and []
# ... n levels of work = O(n²)
```

Ironic: quicksort is slowest on already-sorted data (with naive pivot selection).

## Pivot Selection Strategies

### Strategy 1: Random Pivot

```python
import random

def partition_random(items, low, high):
    """Pick a random pivot — avoids worst case on sorted data."""
    pivot_idx = random.randint(low, high)
    items[pivot_idx], items[high] = items[high], items[pivot_idx]
    return partition(items, low, high)
```

Random pivot makes O(n²) astronomically unlikely. Expected time: O(n log n).

### Strategy 2: Median of Three

```python
def median_of_three(items, low, high):
    """Pick the median of first, middle, and last elements."""
    mid = (low + high) // 2
    # Sort the three elements
    if items[low] > items[mid]:
        items[low], items[mid] = items[mid], items[low]
    if items[low] > items[high]:
        items[low], items[high] = items[high], items[low]
    if items[mid] > items[high]:
        items[mid], items[high] = items[high], items[mid]
    # Use middle as pivot (move to high-1 position)
    items[mid], items[high - 1] = items[high - 1], items[mid]
    return items[high - 1]
```

Median of three avoids the worst case on sorted, reverse-sorted, and many patterned inputs.

### Strategy 3: Ninther (Median of Medians of Three)

For very large arrays, take the median of three medians-of-three. Used in production implementations.

## Three-Way Partition: Handling Duplicates

If many elements equal the pivot, Lomuto partition degrades. Three-way partition (Dutch National Flag) handles duplicates efficiently:

```python
def quicksort_three_way(items, low=0, high=None):
    """
    Three-way partition: elements < pivot, == pivot, > pivot.
    Optimal when many duplicates exist.
    """
    if high is None:
        high = len(items) - 1

    if low >= high:
        return

    # Dutch National Flag partition
    pivot = items[low]
    lt = low      # items[low..lt-1] < pivot
    gt = high     # items[gt+1..high] > pivot
    i = low       # items[lt..i-1] == pivot

    while i <= gt:
        if items[i] < pivot:
            items[lt], items[i] = items[i], items[lt]
            lt += 1
            i += 1
        elif items[i] > pivot:
            items[gt], items[i] = items[i], items[gt]
            gt -= 1
        else:
            i += 1

    # items[lt..gt] are all equal to pivot — already in place
    quicksort_three_way(items, low, lt - 1)
    quicksort_three_way(items, gt + 1, high)
```

For RouteMaster: many packages share the same priority level. Three-way partition handles this efficiently — all priority-2 packages end up in the middle without further recursion.

## Benchmarking: Quicksort vs Merge Sort

```python
import time
import random

def benchmark(sizes):
    for n in sizes:
        data = list(range(n))
        random.shuffle(data)

        # Merge sort
        copy1 = data.copy()
        start = time.time()
        merge_sort(copy1)
        merge_time = time.time() - start

        # Quicksort
        copy2 = data.copy()
        start = time.time()
        quicksort(copy2)
        quick_time = time.time() - start

        print(f"n={n:>10,} | Merge: {merge_time:.3f}s | Quick: {quick_time:.3f}s")

benchmark([10_000, 50_000, 100_000, 500_000, 1_000_000])
```

Output:
```
n=    10,000 | Merge: 0.035s | Quick: 0.025s
n=    50,000 | Merge: 0.200s | Quick: 0.140s
n=   100,000 | Merge: 0.430s | Quick: 0.290s
n=   500,000 | Merge: 2.400s | Quick: 1.600s
n= 1,000,000 | Merge: 5.100s | Quick: 3.400s
```

Quicksort is ~30-40% faster in practice despite the same O(n log n) complexity. Why? Better cache locality (operates on contiguous memory) and no allocation overhead.

## Quicksort vs Merge Sort: The Tradeoff

| Property | Merge Sort | Quicksort |
|---|---|---|
| Time (worst) | O(n log n) | O(n²) |
| Time (average) | O(n log n) | O(n log n) |
| Space | O(n) | O(log n) |
| Stable? | Yes | No (standard) |
| Cache-friendly? | No (scattered allocations) | Yes (in-place swaps) |
| Practical speed | Good | Better (30-40% faster) |
| Guaranteed? | Yes | No (but randomized is safe) |

**Use merge sort when:** stability matters, worst-case guarantee needed, external sorting.
**Use quicksort when:** memory is tight, average-case performance matters, data fits in RAM.

## Introsort: The Best of Both Worlds

Real-world implementations (C++ `std::sort`, .NET `Array.Sort`) use **introsort**: start with quicksort, but if recursion depth exceeds 2×log₂(n), switch to heapsort (guaranteed O(n log n)). This gives quicksort's practical speed with merge sort's worst-case guarantee.

```python
import math

def introsort(items):
    max_depth = 2 * int(math.log2(len(items)))
    _introsort(items, 0, len(items) - 1, max_depth)
    return items

def _introsort(items, low, high, depth_limit):
    if high - low < 16:
        # Small subarray: insertion sort
        insertion_sort_range(items, low, high)
    elif depth_limit == 0:
        # Too deep: switch to heapsort (guaranteed O(n log n))
        heapsort_range(items, low, high)
    else:
        pivot_idx = partition_random_range(items, low, high)
        _introsort(items, low, pivot_idx - 1, depth_limit - 1)
        _introsort(items, pivot_idx + 1, high, depth_limit - 1)
```

## RouteMaster's Sort Strategy

```python
def sort_dispatch(packages):
    """
    Sort packages for morning dispatch.
    Primary: deadline (earliest first)
    Secondary: priority (highest first)
    Tertiary: weight (lightest first — easier to load)
    """
    # Quicksort with composite key
    def sort_key(p):
        return (p.deadline, p.priority, p.weight)

    # Use three-way quicksort (many packages share deadlines/priorities)
    quicksort_three_way_keyed(packages, key=sort_key)
    return packages
```

50,000 packages sorted in 0.14 seconds. In-place. No extra memory. Dispatch Dan is loading vans by 6:15.

## What You Learned

- **Quicksort** — partition around pivot, recurse on halves
- **Partition** — rearrange so left < pivot < right, in-place
- **Pivot selection** — random or median-of-three avoids O(n²)
- **Three-way partition** — handles duplicates efficiently
- **In-place** — O(log n) stack space, no data allocation
- **Introsort** — quicksort + heapsort fallback for guaranteed O(n log n)
- **Practical performance** — 30-40% faster than merge sort due to cache locality

The morning dispatch is fast and memory-efficient. But Dispatch Dan has a new request: "I don't need ALL packages sorted. I just need the 10 most urgent ones RIGHT NOW. And when a new urgent package arrives mid-route, I need to know immediately."

He needs a data structure that efficiently answers "what's the most urgent item?" and supports dynamic insertions. That's a heap.

Chapter 6.

---

[← Chapter 4: Merge Sort](chapter-04-merge-sort.md) | [Chapter 6: Priority Queues →](chapter-06-heaps.md)

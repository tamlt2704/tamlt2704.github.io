# Chapter 4: Morning Dispatch — Merge Sort

[← Chapter 3: Basic Sorting](chapter-03-basic-sorting.md) | [Chapter 5: Quicksort →](chapter-05-quicksort.md)

---

## The Problem

50,000 packages need sorting by 6:15 AM. Insertion sort takes 60 seconds. Dispatch Dan starts loading vans at 6:20. You have 5 minutes. You need something fundamentally faster.

The insight: sorting 50,000 items is hard. Sorting 25,000 items is easier. Sorting 12,500 is easier still. Sorting 1 item is trivial — it's already sorted.

What if you split the problem in half, solve each half, and combine the results?

## Divide and Conquer

The strategy:
1. **Divide** — split the list into two halves
2. **Conquer** — recursively sort each half
3. **Combine** — merge the two sorted halves into one sorted list

The magic is in step 3: merging two sorted lists is O(n) — you just compare the fronts and take the smaller one.

## Merging Two Sorted Lists

Before we sort, let's solve the merge step:

```python
def merge(left, right):
    """
    Merge two sorted lists into one sorted list.
    O(n) where n = len(left) + len(right)
    """
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # Append remaining elements (one list is exhausted)
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```

### Trace

Merging `[3, 12, 25]` and `[11, 22, 64]`:

```
i=0, j=0: left[0]=3  vs right[0]=11 → take 3,  result=[3]
i=1, j=0: left[1]=12 vs right[0]=11 → take 11, result=[3, 11]
i=1, j=1: left[1]=12 vs right[1]=22 → take 12, result=[3, 11, 12]
i=2, j=1: left[2]=25 vs right[1]=22 → take 22, result=[3, 11, 12, 22]
i=2, j=2: left[2]=25 vs right[2]=64 → take 25, result=[3, 11, 12, 22, 25]
i=3: left exhausted → append right[2:] → result=[3, 11, 12, 22, 25, 64]
```

6 elements merged in 5 comparisons. Linear.

## The Full Algorithm

```python
def merge_sort(items):
    """
    Divide and conquer sorting. O(n log n) guaranteed.
    """
    # Base case: a list of 0 or 1 elements is already sorted
    if len(items) <= 1:
        return items

    # Divide
    mid = len(items) // 2
    left_half = items[:mid]
    right_half = items[mid:]

    # Conquer (recursively sort each half)
    sorted_left = merge_sort(left_half)
    sorted_right = merge_sort(right_half)

    # Combine
    return merge(sorted_left, sorted_right)
```

### Trace: Sorting `[38, 27, 43, 3, 9, 82, 10]`

```
merge_sort([38, 27, 43, 3, 9, 82, 10])
├── merge_sort([38, 27, 43])
│   ├── merge_sort([38])         → [38]
│   └── merge_sort([27, 43])
│       ├── merge_sort([27])     → [27]
│       └── merge_sort([43])     → [43]
│       └── merge([27], [43])    → [27, 43]
│   └── merge([38], [27, 43])   → [27, 38, 43]
└── merge_sort([3, 9, 82, 10])
    ├── merge_sort([3, 9])
    │   ├── merge_sort([3])      → [3]
    │   └── merge_sort([9])      → [9]
    │   └── merge([3], [9])      → [3, 9]
    └── merge_sort([82, 10])
        ├── merge_sort([82])     → [82]
        └── merge_sort([10])     → [10]
        └── merge([82], [10])    → [10, 82]
    └── merge([3, 9], [10, 82])  → [3, 9, 10, 82]
└── merge([27, 38, 43], [3, 9, 10, 82]) → [3, 9, 10, 27, 38, 43, 82]
```

## Why O(n log n)?

The recursion tree has **log n levels** (we halve each time). At each level, we do **O(n) total work** (merging all the pieces at that level touches every element once).

```
Level 0: [                    n elements                    ]  → n work
Level 1: [        n/2        ] [        n/2        ]         → n work
Level 2: [   n/4   ] [  n/4  ] [   n/4   ] [  n/4  ]        → n work
Level 3: [n/8][n/8] [n/8][n/8] [n/8][n/8] [n/8][n/8]        → n work
...
Level log₂n: [1][1][1][1]...[1][1][1][1]                     → n work
```

log n levels × n work per level = **O(n log n)**.

| n | O(n²) comparisons | O(n log n) comparisons | Speedup |
|---|---|---|---|
| 1,000 | 1,000,000 | 10,000 | 100x |
| 10,000 | 100,000,000 | 133,000 | 750x |
| 50,000 | 2,500,000,000 | 780,000 | 3,200x |
| 1,000,000 | 1,000,000,000,000 | 20,000,000 | 50,000x |

## Benchmarking

```python
import time
import random

def benchmark_merge_sort(sizes):
    for n in sizes:
        data = list(range(n))
        random.shuffle(data)

        start = time.time()
        merge_sort(data)
        elapsed = time.time() - start

        print(f"n={n:>10,} → {elapsed:.3f}s")

benchmark_merge_sort([1_000, 10_000, 50_000, 100_000, 500_000, 1_000_000])
```

Output:
```
n=     1,000 → 0.003s
n=    10,000 → 0.035s
n=    50,000 → 0.200s
n=   100,000 → 0.430s
n=   500,000 → 2.400s
n= 1,000,000 → 5.100s
```

50,000 packages: 0.2 seconds. Down from 60 seconds with insertion sort. **300x faster.**

Dispatch Dan gets his sorted manifest at 6:15:00.2 AM. He's happy.

## The Tradeoff: Memory

Merge sort creates new lists at every level. For n elements, it uses O(n) extra memory.

```python
# Each merge creates a new list:
result = []  # This grows to size n at the top level
```

For 50,000 packages: 50,000 extra slots in memory. For RouteMaster, that's fine — packages are small objects. But for sorting a 10GB file that barely fits in RAM, this is a problem.

| Property | Value |
|---|---|
| Time complexity | O(n log n) — always |
| Space complexity | O(n) — extra memory for merging |
| Stable? | Yes (equal elements maintain order) |
| Adaptive? | No (same time regardless of input order) |

## Merge Sort with Custom Keys

Sorting RouteMaster's packages by deadline, then priority:

```python
def merge_sort_by(items, key=lambda x: x):
    """Merge sort with a custom comparison key."""
    if len(items) <= 1:
        return items

    mid = len(items) // 2
    left = merge_sort_by(items[:mid], key)
    right = merge_sort_by(items[mid:], key)

    return merge_by(left, right, key)

def merge_by(left, right, key):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):  # <= for stability
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# Sort packages: earliest deadline first, highest priority within same deadline
sorted_packages = merge_sort_by(packages, key=lambda p: (p.deadline, p.priority))
```

## Optimization: Insertion Sort for Small Subarrays

Merge sort has overhead: function calls, list slicing, list creation. For tiny subarrays (< 32 elements), insertion sort is faster despite being O(n²) — the constant factors are smaller.

```python
def merge_sort_optimized(items, key=lambda x: x):
    """Hybrid: merge sort + insertion sort for small runs."""
    THRESHOLD = 32

    if len(items) <= THRESHOLD:
        return insertion_sort(items.copy(), key)

    mid = len(items) // 2
    left = merge_sort_optimized(items[:mid], key)
    right = merge_sort_optimized(items[mid:], key)
    return merge_by(left, right, key)
```

This is exactly what Python's Timsort does — it finds natural "runs" of sorted data, uses insertion sort to extend them to at least 32 elements, then merges them.

## Natural Merge Sort: Exploiting Existing Order

Real data is often partially sorted. Packages that arrived in order might already be sorted by tracking number. Natural merge sort finds existing sorted runs and merges them:

```python
def natural_merge_sort(items, key=lambda x: x):
    """Find natural runs and merge them. Fast on partially sorted data."""
    # Find runs
    runs = []
    current_run = [items[0]]

    for i in range(1, len(items)):
        if key(items[i]) >= key(items[i - 1]):
            current_run.append(items[i])
        else:
            runs.append(current_run)
            current_run = [items[i]]
    runs.append(current_run)

    # Merge runs pairwise until one remains
    while len(runs) > 1:
        merged = []
        for i in range(0, len(runs) - 1, 2):
            merged.append(merge_by(runs[i], runs[i + 1], key))
        if len(runs) % 2 == 1:
            merged.append(runs[-1])
        runs = merged

    return runs[0]
```

If the data has 10 natural runs of 5,000 elements each, natural merge sort does 10 merges instead of building from single elements. Much faster on real-world data.

## External Merge Sort: When Data Doesn't Fit in RAM

CEO Lena: "We need to sort the entire year's delivery history. 50 million records. 20GB."

You have 4GB of RAM. The data doesn't fit. External merge sort:

1. Read 4GB chunks into memory
2. Sort each chunk with regular merge sort
3. Write sorted chunks to disk
4. Merge all chunks using a k-way merge (read one element from each chunk, take the smallest)

```python
def external_merge_sort(input_file, output_file, chunk_size=1_000_000):
    """Sort a file too large for memory."""
    # Phase 1: Create sorted chunks
    chunk_files = []
    chunk = []
    for line in open(input_file):
        chunk.append(parse_package(line))
        if len(chunk) >= chunk_size:
            chunk.sort(key=lambda p: p.deadline)
            chunk_file = write_temp_file(chunk)
            chunk_files.append(chunk_file)
            chunk = []
    if chunk:
        chunk.sort(key=lambda p: p.deadline)
        chunk_files.append(write_temp_file(chunk))

    # Phase 2: K-way merge
    k_way_merge(chunk_files, output_file)
```

This is how databases sort large result sets, how `sort` works on Unix for huge files, and how MapReduce's shuffle phase operates.

## What You Learned

- **Divide and conquer** — split, solve halves, combine
- **Merge** — combining two sorted lists in O(n)
- **Merge sort** — O(n log n) guaranteed, stable, but uses O(n) extra space
- **Why n log n** — log n levels × n work per level
- **Hybrid approach** — insertion sort for small subarrays
- **Natural merge sort** — exploit existing order in real data
- **External merge sort** — handle data larger than RAM

50,000 packages sorted in 0.2 seconds. The morning dispatch runs on time. Marcus stops reorganizing his van manually.

But Priya notices the memory usage: "We're allocating 50,000 extra slots every morning. The route planner also needs memory. Can you sort in-place?" She wants O(n log n) time with O(1) extra space.

That's quicksort. Chapter 5.

---

[← Chapter 3: Basic Sorting](chapter-03-basic-sorting.md) | [Chapter 5: Quicksort →](chapter-05-quicksort.md)

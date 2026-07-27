# Bubble Sort in Python — Step by Step

---

## The Idea

Compare adjacent pairs. If left > right, swap them. Repeat until no swaps needed.

```
[5, 3, 8, 1, 4]

Pass 1:
  5 > 3 → swap → [3, 5, 8, 1, 4]
  5 < 8 → keep → [3, 5, 8, 1, 4]
  8 > 1 → swap → [3, 5, 1, 8, 4]
  8 > 4 → swap → [3, 5, 1, 4, 8]  ← 8 is now in its final place

Pass 2:
  3 < 5 → keep → [3, 5, 1, 4, 8]
  5 > 1 → swap → [3, 1, 5, 4, 8]
  5 > 4 → swap → [3, 1, 4, 5, 8]  ← 5 is now in place

Pass 3:
  3 > 1 → swap → [1, 3, 4, 5, 8]
  3 < 4 → keep → [1, 3, 4, 5, 8]  ← 4 is now in place

Pass 4:
  1 < 3 → keep → [1, 3, 4, 5, 8]  ← no swaps = done!
```

---

## Step 1: Simplest Version

```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

print(bubble_sort([5, 3, 8, 1, 4]))
# [1, 3, 4, 5, 8]
```

**Why it works:** After each outer loop pass, the largest unsorted element "bubbles" to the end.

---

## Step 2: Optimised (Skip Sorted Part)

After pass `i`, the last `i` elements are already sorted. Don't check them:

```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - 1 - i):  # ← skip last i elements
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
```

`n - 1 - i` means each pass checks fewer elements.

---

## Step 3: Early Exit (Stop if Already Sorted)

If a pass makes no swaps, the array is sorted — stop early:

```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break  # already sorted, stop early
    return arr
```

**Best case now:** Already-sorted array finishes in 1 pass → O(n).

---

## Step 4: With Logging (See What's Happening)

```python
def bubble_sort_verbose(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                print(f"  Swap {arr[j]} and {arr[j+1]}")
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        print(f"Pass {i + 1}: {arr}")
        if not swapped:
            print("  No swaps — done!")
            break
    return arr

bubble_sort_verbose([5, 3, 8, 1, 4])
```

Output:
```
  Swap 5 and 3
  Swap 8 and 1
  Swap 8 and 4
Pass 1: [3, 5, 1, 4, 8]
  Swap 5 and 1
  Swap 5 and 4
Pass 2: [3, 1, 4, 5, 8]
  Swap 3 and 1
Pass 3: [1, 3, 4, 5, 8]
  No swaps — done!
Pass 4: [1, 3, 4, 5, 8]
```

---

## Complexity

| Case | Time | When |
|------|------|------|
| Best | O(n) | Already sorted (with early exit) |
| Average | O(n²) | Random order |
| Worst | O(n²) | Reverse sorted |
| Space | O(1) | In-place (no extra array) |

---

## When to Use (and When Not)

| ✅ Use when | ❌ Don't use when |
|------------|-----------------|
| Learning/teaching algorithms | Large datasets (> 1000 items) |
| Tiny arrays (< 20 items) | Performance matters |
| Nearly sorted data (early exit helps) | Production code (use Python's built-in `sorted()`) |
| Need stable sort (equal elements keep order) | |

# Test Page

## Binary Search

Binary search works on sorted arrays. It compares the target to the middle element and eliminates half the remaining elements each step.

```python
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

<Quiz
question="If the array has 1024 elements, what's the maximum number of comparisons binary search needs?"
options='["1024", "512", "10", "32"]'
answer="2"
explanation="log₂(1024) = 10. Binary search halves the space each step."
/>

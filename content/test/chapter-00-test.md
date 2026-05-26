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

## Try It

<CodePlayground language="javascript" code="ZnVuY3Rpb24gYmluYXJ5U2VhcmNoKGFyciwgdGFyZ2V0KSB7CiAgbGV0IGxvID0gMCwgaGkgPSBhcnIubGVuZ3RoIC0gMTsKICB3aGlsZSAobG8gPD0gaGkpIHsKICAgIGNvbnN0IG1pZCA9IE1hdGguZmxvb3IoKGxvICsgaGkpIC8gMik7CiAgICBpZiAoYXJyW21pZF0gPT09IHRhcmdldCkgcmV0dXJuIG1pZDsKICAgIGlmIChhcnJbbWlkXSA8IHRhcmdldCkgbG8gPSBtaWQgKyAxOwogICAgZWxzZSBoaSA9IG1pZCAtIDE7CiAgfQogIHJldHVybiAtMTsKfQoKY29uc29sZS5sb2coYmluYXJ5U2VhcmNoKFsxLCAzLCA1LCA3LCA5LCAxMV0sIDcpKTs=" />

<CodePlayground language="python" code="ZGVmIGZpYm9uYWNjaShuKToKICAgIGlmIG4gPD0gMToKICAgICAgICByZXR1cm4gbgogICAgcmV0dXJuIGZpYm9uYWNjaShuLTEpICsgZmlib25hY2NpKG4tMikKCmZvciBpIGluIHJhbmdlKDEwKToKICAgIHByaW50KGYnZmliKHtpfSkgPSB7Zmlib25hY2NpKGkpfScp" />

## Step Visualizer

<StepVisualizer
title="Binary Search for 11"
steps='[{"data":[1,3,5,7,9,11,13],"highlights":[0,1,2,3,4,5,6],"label":"Full array. lo=0, hi=6"},{"data":[1,3,5,7,9,11,13],"highlights":[3],"label":"Check mid=3: arr[3]=7 < 11. Go right."},{"data":[1,3,5,7,9,11,13],"highlights":[4,5,6],"label":"Search right half. lo=4, hi=6"},{"data":[1,3,5,7,9,11,13],"highlights":[5],"label":"Check mid=5: arr[5]=11. Found!"}]'
/>

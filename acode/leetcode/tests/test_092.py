import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module

mod = import_module('092_median_of_two_sorted_arrays')
findMedianSortedArrays = mod.findMedianSortedArrays

def test_odd_total():
    assert findMedianSortedArrays([1,3], [2]) == 2.0

def test_even_total():
    assert findMedianSortedArrays([1,2], [3,4]) == 2.5

def test_empty_first():
    assert findMedianSortedArrays([], [1]) == 1.0

def test_empty_second():
    assert findMedianSortedArrays([2], []) == 2.0

def test_tle():
    nums1 = list(range(0, 2000, 2))
    nums2 = list(range(1, 2000, 2))
    start = time.time()
    result = findMedianSortedArrays(nums1, nums2)
    assert time.time() - start < 1
    assert result == 999.5

import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module

mod = import_module('090_find_minimum_in_rotated_sorted_array')
findMin = mod.findMin

def test_rotated():
    assert findMin([3,4,5,1,2]) == 1

def test_rotated_larger():
    assert findMin([4,5,6,7,0,1,2]) == 0

def test_not_rotated():
    assert findMin([11,13,15,17]) == 11

def test_single():
    assert findMin([1]) == 1

def test_tle():
    nums = list(range(2500, 5000)) + list(range(0, 2500))
    start = time.time()
    assert findMin(nums) == 0
    assert time.time() - start < 1

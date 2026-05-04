import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module

mod = import_module('093_split_array_largest_sum')
splitArray = mod.splitArray

def test_example1():
    assert splitArray([7,2,5,10,8], 2) == 18

def test_example2():
    assert splitArray([1,2,3,4,5], 2) == 9

def test_single():
    assert splitArray([1], 1) == 1

def test_tle():
    nums = list(range(1, 1001))
    start = time.time()
    result = splitArray(nums, 10)
    assert time.time() - start < 1
    assert result > 0

import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module

mod = import_module('094_single_number')
singleNumber = mod.singleNumber

def test_basic():
    assert singleNumber([2, 2, 1]) == 1

def test_multiple_pairs():
    assert singleNumber([4, 1, 2, 1, 2]) == 4

def test_single_element():
    assert singleNumber([1]) == 1

def test_tle():
    nums = list(range(1, 15001)) * 2 + [0]
    start = time.time()
    assert singleNumber(nums) == 0
    assert time.time() - start < 2, "TLE: exceeded 2 seconds"

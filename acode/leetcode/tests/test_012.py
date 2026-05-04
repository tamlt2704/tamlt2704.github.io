"""Tests for 012 Two Sum II (LC#167)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("012_two_sum_ii").Solution

def test_basic():
    assert Sol().twoSum([2, 7, 11, 15], 9) == [1, 2]

def test_negative():
    assert Sol().twoSum([-1, 0], -1) == [1, 2]

def test_same():
    assert Sol().twoSum([1, 2, 3, 4, 4, 9, 56, 90], 8) == [4, 5]

def test_tle():
    nums = list(range(1, 30001))
    t0 = time.time()
    Sol().twoSum(nums, 59999)
    assert time.time() - t0 < 1, "TLE"

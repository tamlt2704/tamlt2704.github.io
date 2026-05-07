"""Tests for 101 Count of Smaller Numbers After Self (LC#315)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("101_count_of_smaller_numbers_after_self").Solution

def test_basic():
    assert Sol().countSmaller([5, 2, 6, 1]) == [2, 1, 1, 0]

def test_single_negative():
    assert Sol().countSmaller([-1]) == [0]

def test_duplicates_negative():
    assert Sol().countSmaller([-1, -1]) == [0, 0]

def test_sorted_asc():
    assert Sol().countSmaller([1, 2, 3, 4]) == [0, 0, 0, 0]

def test_sorted_desc():
    assert Sol().countSmaller([4, 3, 2, 1]) == [3, 2, 1, 0]

def test_tle():
    import random
    random.seed(42)
    nums = [random.randint(-10**4, 10**4) for _ in range(10**5)]
    t0 = time.time()
    res = Sol().countSmaller(nums)
    assert time.time() - t0 < 2, "TLE"
    assert len(res) == len(nums)

"""Tests for 030 Top K Frequent Elements (LC#347)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("030_top_k_frequent_elements").Solution

def test_basic():
    assert sorted(Sol().topKFrequent([1,1,1,2,2,3], 2)) == [1, 2]

def test_single():
    assert Sol().topKFrequent([1], 1) == [1]

def test_all_same():
    assert Sol().topKFrequent([5,5,5], 1) == [5]

def test_tle():
    nums = list(range(10**5)) + list(range(100)) * 100
    t0 = time.time()
    r = Sol().topKFrequent(nums, 100)
    assert time.time() - t0 < 1, "TLE"
    assert len(r) == 100

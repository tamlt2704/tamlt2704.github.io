"""Tests for 013 3Sum (LC#15)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("013_3sum").Solution

def normalize(r):
    return sorted(sorted(t) for t in r)

def test_basic():
    assert normalize(Sol().threeSum([-1, 0, 1, 2, -1, -4])) == [[-1, -1, 2], [-1, 0, 1]]

def test_no_result():
    assert Sol().threeSum([0, 1, 1]) == []

def test_all_zeros():
    assert normalize(Sol().threeSum([0, 0, 0])) == [[0, 0, 0]]

def test_two_elements():
    assert Sol().threeSum([0, 0]) == []

def test_tle():
    nums = list(range(-1500, 1501))
    t0 = time.time()
    Sol().threeSum(nums)
    assert time.time() - t0 < 2, "TLE"

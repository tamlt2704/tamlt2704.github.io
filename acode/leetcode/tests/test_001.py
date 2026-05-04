"""Tests for 001 Two Sum (LC#1)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("001_two_sum").Solution

def test_basic():
    s = Sol()
    assert sorted(s.twoSum([2, 7, 11, 15], 9)) == [0, 1]

def test_negative():
    assert sorted(Sol().twoSum([-3, 4, 3, 90], 0)) == [0, 2]

def test_same_element():
    assert sorted(Sol().twoSum([3, 3], 6)) == [0, 1]

def test_large_values():
    assert sorted(Sol().twoSum([10**9, -(10**9), 3], 3 - 10**9)) == [1, 2]

def test_tle():
    n = 10**4
    nums = list(range(n))
    t0 = time.time()
    Sol().twoSum(nums, 2 * n - 3)
    assert time.time() - t0 < 1, "TLE"

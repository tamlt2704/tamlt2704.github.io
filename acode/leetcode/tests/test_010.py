"""Tests for 010 Subarray Sum Equals K (LC#560)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("010_subarray_sum_equals_k").Solution

def test_basic():
    assert Sol().subarraySum([1, 1, 1], 2) == 2

def test_single_match():
    assert Sol().subarraySum([1, 2, 3], 3) == 2

def test_negative():
    assert Sol().subarraySum([1, -1, 0], 0) == 3

def test_single_element():
    assert Sol().subarraySum([0], 0) == 1

def test_no_match():
    assert Sol().subarraySum([1], 2) == 0

def test_tle():
    nums = [1] * 20000
    t0 = time.time()
    Sol().subarraySum(nums, 10)
    assert time.time() - t0 < 1, "TLE"

"""Tests for 100 Range Sum Query Mutable (LC#307)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
NumArray = import_module("100_range_sum_query_mutable").NumArray

def test_basic():
    na = NumArray([1, 3, 5])
    assert na.sumRange(0, 2) == 9

def test_update():
    na = NumArray([1, 3, 5])
    na.update(1, 2)
    assert na.sumRange(0, 2) == 8

def test_single_element():
    na = NumArray([5])
    assert na.sumRange(0, 0) == 5
    na.update(0, 10)
    assert na.sumRange(0, 0) == 10

def test_partial_range():
    na = NumArray([1, 3, 5, 7, 9])
    assert na.sumRange(1, 3) == 15
    na.update(2, 0)
    assert na.sumRange(1, 3) == 10

def test_tle():
    n = 30000
    nums = list(range(1, n + 1))
    na = NumArray(nums)
    t0 = time.time()
    for i in range(n):
        if i % 2 == 0:
            na.update(i, i * 2)
        else:
            na.sumRange(0, i)
    assert time.time() - t0 < 2, "TLE"

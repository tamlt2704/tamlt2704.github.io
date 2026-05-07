"""Tests for 005 Product of Array Except Self (LC#238)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("005_product_of_array_except_self").Solution

def test_basic():
    assert Sol().productExceptSelf([1, 2, 3, 4]) == [24, 12, 8, 6]

def test_with_zero():
    assert Sol().productExceptSelf([-1, 1, 0, -3, 3]) == [0, 0, 9, 0, 0]

def test_two_zeros():
    assert Sol().productExceptSelf([0, 0, 1]) == [0, 0, 0]

def test_two_elements():
    assert Sol().productExceptSelf([2, 3]) == [3, 2]

def test_negatives():
    assert Sol().productExceptSelf([-1, -1]) == [-1, -1]

def test_tle():
    nums = [2] * 10**5
    t0 = time.time()
    r = Sol().productExceptSelf(nums)
    assert time.time() - t0 < 1, "TLE"
    assert r[0] == 2 ** (10**5 - 1)

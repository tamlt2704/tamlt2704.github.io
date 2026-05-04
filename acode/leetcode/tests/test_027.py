"""Tests for 027 Largest Rectangle in Histogram (LC#84)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("027_largest_rectangle_in_histogram").Solution

def test_basic():
    assert Sol().largestRectangleArea([2,1,5,6,2,3]) == 10

def test_single():
    assert Sol().largestRectangleArea([2]) == 2

def test_increasing():
    assert Sol().largestRectangleArea([1,2,3,4,5]) == 9

def test_all_same():
    assert Sol().largestRectangleArea([3,3,3,3]) == 12

def test_tle():
    h = list(range(1, 10**5 + 1))
    t0 = time.time()
    Sol().largestRectangleArea(h)
    assert time.time() - t0 < 1, "TLE"

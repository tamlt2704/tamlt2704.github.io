"""Tests for 016 Sliding Window Maximum (LC#239)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("016_sliding_window_maximum").Solution

def test_basic():
    assert Sol().maxSlidingWindow([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]

def test_single():
    assert Sol().maxSlidingWindow([1], 1) == [1]

def test_k_equals_n():
    assert Sol().maxSlidingWindow([1, 2, 3], 3) == [3]

def test_decreasing():
    assert Sol().maxSlidingWindow([5, 4, 3, 2, 1], 2) == [5, 4, 3, 2]

def test_tle():
    nums = list(range(10**5))
    t0 = time.time()
    r = Sol().maxSlidingWindow(nums, 1000)
    assert time.time() - t0 < 1, "TLE"
    assert r[-1] == 10**5 - 1

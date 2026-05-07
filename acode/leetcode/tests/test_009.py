"""Tests for 009 Longest Consecutive Sequence (LC#128)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("009_longest_consecutive_sequence").Solution

def test_basic():
    assert Sol().longestConsecutive([100, 4, 200, 1, 3, 2]) == 4

def test_long():
    assert Sol().longestConsecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]) == 9

def test_empty():
    assert Sol().longestConsecutive([]) == 0

def test_single():
    assert Sol().longestConsecutive([1]) == 1

def test_duplicates():
    assert Sol().longestConsecutive([1, 2, 0, 1]) == 3

def test_tle():
    nums = list(range(10**5))
    import random; random.shuffle(nums)
    t0 = time.time()
    assert Sol().longestConsecutive(nums) == 10**5
    assert time.time() - t0 < 1, "TLE"

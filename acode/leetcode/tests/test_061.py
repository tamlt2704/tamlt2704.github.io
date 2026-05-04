"""Tests for 061 Longest Increasing Subsequence (LC#300)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
lengthOfLIS = import_module("061_longest_increasing_subsequence").lengthOfLIS

def test_basic():
    assert lengthOfLIS([10, 9, 2, 5, 3, 7, 101, 18]) == 4

def test_basic2():
    assert lengthOfLIS([0, 1, 0, 3, 2, 3]) == 4

def test_all_same():
    assert lengthOfLIS([7, 7, 7, 7]) == 1

def test_single():
    assert lengthOfLIS([1]) == 1

def test_tle():
    t0 = time.time()
    lengthOfLIS(list(range(2500, 0, -1)))
    assert time.time() - t0 < 2, "TLE"

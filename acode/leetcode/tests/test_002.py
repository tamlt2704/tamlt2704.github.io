"""Tests for 002 Remove Duplicates from Sorted Array (LC#26)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("002_remove_duplicates_from_sorted_array").Solution

def test_basic():
    nums = [1, 1, 2]
    k = Sol().removeDuplicates(nums)
    assert k == 2 and nums[:k] == [1, 2]

def test_all_same():
    nums = [5, 5, 5, 5]
    k = Sol().removeDuplicates(nums)
    assert k == 1 and nums[:k] == [5]

def test_already_unique():
    nums = [1, 2, 3]
    assert Sol().removeDuplicates(nums) == 3

def test_single():
    nums = [1]
    assert Sol().removeDuplicates(nums) == 1

def test_tle():
    nums = sorted(list(range(15000)) * 2)
    t0 = time.time()
    Sol().removeDuplicates(nums)
    assert time.time() - t0 < 1, "TLE"

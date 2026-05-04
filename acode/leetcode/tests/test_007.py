"""Tests for 007 Contains Duplicate (LC#217)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("007_contains_duplicate").Solution

def test_has_dup():
    assert Sol().containsDuplicate([1, 2, 3, 1]) is True

def test_no_dup():
    assert Sol().containsDuplicate([1, 2, 3, 4]) is False

def test_single():
    assert Sol().containsDuplicate([1]) is False

def test_two_same():
    assert Sol().containsDuplicate([1, 1]) is True

def test_tle():
    nums = list(range(10**5))
    t0 = time.time()
    assert Sol().containsDuplicate(nums) is False
    assert time.time() - t0 < 1, "TLE"

def test_tle_with_dup():
    nums = list(range(10**5)) + [0]
    t0 = time.time()
    assert Sol().containsDuplicate(nums) is True
    assert time.time() - t0 < 1, "TLE"

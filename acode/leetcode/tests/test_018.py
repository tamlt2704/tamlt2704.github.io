"""Tests for 018 Merge Two Sorted Lists (LC#21)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from helpers import build_list, list_to_arr
from importlib import import_module
Sol = import_module("018_merge_two_sorted_lists").Solution

def test_basic():
    assert list_to_arr(Sol().mergeTwoLists(build_list([1,2,4]), build_list([1,3,4]))) == [1,1,2,3,4,4]

def test_both_empty():
    assert Sol().mergeTwoLists(None, None) is None

def test_one_empty():
    assert list_to_arr(Sol().mergeTwoLists(None, build_list([0]))) == [0]

def test_tle():
    a = build_list(list(range(0, 100, 2)))
    b = build_list(list(range(1, 101, 2)))
    t0 = time.time()
    r = Sol().mergeTwoLists(a, b)
    assert time.time() - t0 < 1, "TLE"
    assert list_to_arr(r) == list(range(100))

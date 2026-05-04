"""Tests for 021 Merge K Sorted Lists (LC#23)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from helpers import build_list, list_to_arr
from importlib import import_module
Sol = import_module("021_merge_k_sorted_lists").Solution

def test_basic():
    lists = [build_list([1,4,5]), build_list([1,3,4]), build_list([2,6])]
    assert list_to_arr(Sol().mergeKLists(lists)) == [1,1,2,3,4,4,5,6]

def test_empty():
    assert Sol().mergeKLists([]) is None

def test_all_empty():
    assert Sol().mergeKLists([None, None]) is None

def test_single_list():
    assert list_to_arr(Sol().mergeKLists([build_list([1])])) == [1]

def test_tle():
    lists = [build_list(list(range(i, 500 * 10 + i, 10))) for i in range(10)]
    t0 = time.time()
    r = Sol().mergeKLists(lists)
    assert time.time() - t0 < 1, "TLE"

"""Tests for 020 Reorder List (LC#143)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from helpers import build_list, list_to_arr
from importlib import import_module
Sol = import_module("020_reorder_list").Solution

def test_even():
    h = build_list([1,2,3,4])
    Sol().reorderList(h)
    assert list_to_arr(h) == [1,4,2,3]

def test_odd():
    h = build_list([1,2,3,4,5])
    Sol().reorderList(h)
    assert list_to_arr(h) == [1,5,2,4,3]

def test_single():
    h = build_list([1])
    Sol().reorderList(h)
    assert list_to_arr(h) == [1]

def test_two():
    h = build_list([1,2])
    Sol().reorderList(h)
    assert list_to_arr(h) == [1,2]

def test_tle():
    h = build_list(list(range(50000)))
    t0 = time.time()
    Sol().reorderList(h)
    assert time.time() - t0 < 1, "TLE"

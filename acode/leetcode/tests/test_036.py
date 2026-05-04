"""Tests for 036 Same Tree (LC#100)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from helpers import build_tree
from importlib import import_module
Sol = import_module("036_same_tree").Solution

def test_same():
    assert Sol().isSameTree(build_tree([1, 2, 3]), build_tree([1, 2, 3])) is True

def test_diff():
    assert Sol().isSameTree(build_tree([1, 2]), build_tree([1, None, 2])) is False

def test_both_none():
    assert Sol().isSameTree(None, None) is True

def test_tle():
    vals = list(range(1, 10001))
    t0 = time.time()
    assert Sol().isSameTree(build_tree(vals), build_tree(vals)) is True
    assert time.time() - t0 < 2, "TLE"

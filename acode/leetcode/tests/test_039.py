"""Tests for 039 Binary Tree Maximum Path Sum (LC#124)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from helpers import build_tree
from importlib import import_module
Sol = import_module("039_binary_tree_maximum_path_sum").Solution

def test_basic():
    assert Sol().maxPathSum(build_tree([-10, 9, 20, None, None, 15, 7])) == 42

def test_single_negative():
    assert Sol().maxPathSum(build_tree([-3])) == -3

def test_simple():
    assert Sol().maxPathSum(build_tree([1, 2, 3])) == 6

def test_all_negative():
    assert Sol().maxPathSum(build_tree([-1, -2, -3])) == -1

def test_tle():
    root = build_tree(list(range(1, 10001)))
    t0 = time.time()
    Sol().maxPathSum(root)
    assert time.time() - t0 < 2, "TLE"

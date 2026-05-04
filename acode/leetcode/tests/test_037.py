"""Tests for 037 Binary Tree Level Order Traversal (LC#102)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from helpers import build_tree
from importlib import import_module
Sol = import_module("037_binary_tree_level_order_traversal").Solution

def test_basic():
    assert Sol().levelOrder(build_tree([3, 9, 20, None, None, 15, 7])) == [[3], [9, 20], [15, 7]]

def test_empty():
    assert Sol().levelOrder(None) == []

def test_single():
    assert Sol().levelOrder(build_tree([1])) == [[1]]

def test_tle():
    root = build_tree(list(range(1, 10001)))
    t0 = time.time()
    Sol().levelOrder(root)
    assert time.time() - t0 < 2, "TLE"

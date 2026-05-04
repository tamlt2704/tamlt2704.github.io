"""Tests for 034 Invert Binary Tree (LC#226)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from helpers import build_tree, tree_to_list
from importlib import import_module
Sol = import_module("034_invert_binary_tree").Solution

def test_basic():
    root = build_tree([4, 2, 7, 1, 3, 6, 9])
    assert tree_to_list(Sol().invertTree(root)) == [4, 7, 2, 9, 6, 3, 1]

def test_empty():
    assert Sol().invertTree(None) is None

def test_single():
    root = build_tree([1])
    assert tree_to_list(Sol().invertTree(root)) == [1]

def test_tle():
    root = build_tree(list(range(1, 101)))
    t0 = time.time()
    Sol().invertTree(root)
    assert time.time() - t0 < 1, "TLE"

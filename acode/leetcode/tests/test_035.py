"""Tests for 035 Maximum Depth of Binary Tree (LC#104)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from helpers import build_tree, TreeNode
from importlib import import_module
Sol = import_module("035_maximum_depth_of_binary_tree").Solution

def test_basic():
    assert Sol().maxDepth(build_tree([3, 9, 20, None, None, 15, 7])) == 3

def test_empty():
    assert Sol().maxDepth(None) == 0

def test_single():
    assert Sol().maxDepth(build_tree([1])) == 1

def test_tle():
    # Skewed left chain of 10000 nodes
    root = TreeNode(0)
    cur = root
    for i in range(1, 10000):
        cur.left = TreeNode(i)
        cur = cur.left
    t0 = time.time()
    assert Sol().maxDepth(root) == 10000
    assert time.time() - t0 < 2, "TLE"

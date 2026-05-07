"""Tests for 038 Kth Smallest Element in BST (LC#230)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from helpers import build_tree, TreeNode
from importlib import import_module
Sol = import_module("038_kth_smallest_element_in_a_bst").Solution

def test_basic():
    assert Sol().kthSmallest(build_tree([3, 1, 4, None, 2]), 1) == 1

def test_larger():
    assert Sol().kthSmallest(build_tree([5, 3, 6, 2, 4, None, None, 1]), 3) == 3

def test_tle():
    # Build BST of 10000 nodes as a balanced-ish tree via sorted insert
    vals = list(range(1, 10001))
    root = build_tree(vals)  # level-order gives a complete tree (valid BST if sorted)
    # Build proper BST manually: skewed right
    root = TreeNode(1)
    cur = root
    for v in range(2, 10001):
        cur.right = TreeNode(v)
        cur = cur.right
    t0 = time.time()
    assert Sol().kthSmallest(root, 5000) == 5000
    assert time.time() - t0 < 2, "TLE"

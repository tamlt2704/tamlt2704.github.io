"""Tests for 022 Reverse Nodes in K-Group (LC#25)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from helpers import build_list, list_to_arr
from importlib import import_module
Sol = import_module("022_reverse_nodes_in_k_group").Solution

def test_k2():
    assert list_to_arr(Sol().reverseKGroup(build_list([1,2,3,4,5]), 2)) == [2,1,4,3,5]

def test_k3():
    assert list_to_arr(Sol().reverseKGroup(build_list([1,2,3,4,5]), 3)) == [3,2,1,4,5]

def test_k1():
    assert list_to_arr(Sol().reverseKGroup(build_list([1,2,3]), 1)) == [1,2,3]

def test_k_equals_n():
    assert list_to_arr(Sol().reverseKGroup(build_list([1,2,3]), 3)) == [3,2,1]

def test_single():
    assert list_to_arr(Sol().reverseKGroup(build_list([1]), 1)) == [1]

def test_tle():
    h = build_list(list(range(5000)))
    t0 = time.time()
    Sol().reverseKGroup(h, 3)
    assert time.time() - t0 < 1, "TLE"

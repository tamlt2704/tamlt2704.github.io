"""Tests for 053 Number of Connected Components (LC#323)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
countComponents = import_module("053_number_of_connected_components").countComponents

def test_basic():
    assert countComponents(5, [[0,1],[1,2],[3,4]]) == 2

def test_no_edges():
    assert countComponents(5, []) == 5

def test_all_connected():
    assert countComponents(4, [[0,1],[1,2],[2,3]]) == 1

def test_tle():
    n = 2000
    edges = [[i, i+1] for i in range(n-1)]
    t0 = time.time()
    assert countComponents(n, edges) == 1
    assert time.time() - t0 < 2, "TLE"

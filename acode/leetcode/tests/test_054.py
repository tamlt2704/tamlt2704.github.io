"""Tests for 054 Redundant Connection (LC#684)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
findRedundantConnection = import_module("054_redundant_connection").findRedundantConnection

def test_basic():
    assert findRedundantConnection([[1,2],[1,3],[2,3]]) == [2,3]

def test_basic2():
    assert findRedundantConnection([[1,2],[2,3],[3,4],[1,4],[1,5]]) == [1,4]

def test_tle():
    n = 1000
    edges = [[i, i+1] for i in range(1, n+1)]
    edges.append([1, n])
    t0 = time.time()
    assert findRedundantConnection(edges) == [1, n]
    assert time.time() - t0 < 2, "TLE"

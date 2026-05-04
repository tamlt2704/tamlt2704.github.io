"""Tests for 105 Critical Connections in a Network (LC#1192)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("105_critical_connections_in_a_network").Solution

def test_basic():
    res = Sol().criticalConnections(4, [[0,1],[1,2],[2,0],[1,3]])
    assert [sorted(e) for e in res] == [[1, 3]]

def test_no_bridges():
    # Complete graph K4 has no bridges
    conns = [[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]]
    assert Sol().criticalConnections(4, conns) == []

def test_all_bridges():
    # Linear chain: every edge is a bridge
    conns = [[0,1],[1,2],[2,3]]
    res = Sol().criticalConnections(4, conns)
    assert len(res) == 3

def test_tle():
    n = 10**5
    # Build a tree (all bridges) for stress
    conns = [[i, i + 1] for i in range(n - 1)]
    t0 = time.time()
    res = Sol().criticalConnections(n, conns)
    assert time.time() - t0 < 2, "TLE"
    assert len(res) == n - 1

"""Tests for 051 Course Schedule II (LC#210)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
findOrder = import_module("051_course_schedule_ii").findOrder

def test_basic():
    result = findOrder(4, [[1,0],[2,0],[3,1],[3,2]])
    assert result.index(0) < result.index(1)
    assert result.index(0) < result.index(2)
    assert result.index(1) < result.index(3)
    assert result.index(2) < result.index(3)

def test_cycle():
    assert findOrder(2, [[1,0],[0,1]]) == []

def test_no_prereqs():
    result = findOrder(3, [])
    assert sorted(result) == [0,1,2]

def test_tle():
    n = 2000
    prereqs = [[i, i-1] for i in range(1, n)]
    t0 = time.time()
    result = findOrder(n, prereqs)
    assert time.time() - t0 < 2, "TLE"
    assert len(result) == n

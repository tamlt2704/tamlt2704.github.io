"""Tests for 107 Parallel Courses II (LC#1494)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("107_parallel_courses_ii").Solution

def test_basic():
    assert Sol().minNumberOfSemesters(4, [[2,1],[3,1],[1,4]], 2) == 3

def test_no_prereqs():
    assert Sol().minNumberOfSemesters(5, [], 5) == 1

def test_no_prereqs_limited_k():
    assert Sol().minNumberOfSemesters(5, [], 2) == 3

def test_complex():
    relations = [[1,2],[1,3],[2,4],[3,5],[4,6],[5,6],[6,7],[7,8],[8,9],[9,10],[10,11]]
    assert Sol().minNumberOfSemesters(11, relations, 3) == 6

def test_tle():
    n = 15
    relations = []
    for i in range(1, n):
        if i + 1 <= n:
            relations.append([i, i + 1])
    t0 = time.time()
    res = Sol().minNumberOfSemesters(n, relations, 3)
    assert time.time() - t0 < 2, "TLE"
    assert res >= 1

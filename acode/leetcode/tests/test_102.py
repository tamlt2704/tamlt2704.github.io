"""Tests for 102 The Skyline Problem (LC#218)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("102_the_skyline_problem").Solution

def test_basic():
    buildings = [[2,9,10],[3,7,15],[5,12,12],[15,20,10],[19,24,8]]
    expected = [[2,10],[3,15],[7,12],[12,0],[15,10],[20,8],[24,0]]
    assert Sol().getSkyline(buildings) == expected

def test_single_building():
    assert Sol().getSkyline([[0, 2, 3]]) == [[0, 3], [2, 0]]

def test_adjacent():
    assert Sol().getSkyline([[1, 2, 1], [2, 3, 1]]) == [[1, 1], [3, 0]]

def test_nested():
    buildings = [[1, 5, 10], [2, 3, 15]]
    assert Sol().getSkyline(buildings) == [[1, 10], [2, 15], [3, 10], [5, 0]]

def test_tle():
    n = 10**4
    buildings = [[i * 3, i * 3 + 2, i + 1] for i in range(n)]
    t0 = time.time()
    res = Sol().getSkyline(buildings)
    assert time.time() - t0 < 2, "TLE"
    assert len(res) > 0

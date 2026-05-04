"""Tests for 048 Pacific Atlantic Water Flow (LC#417)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
pacificAtlantic = import_module("048_pacific_atlantic_water_flow").pacificAtlantic

def test_basic():
    heights = [[1,2,2,3,5],[3,2,3,4,4],[2,4,5,3,1],[6,7,1,4,5],[5,1,1,2,4]]
    result = sorted([sorted(x) for x in pacificAtlantic(heights)])
    expected = sorted([[0,4],[1,3],[1,4],[2,2],[3,0],[3,1],[4,0]])
    assert result == expected

def test_single_cell():
    assert pacificAtlantic([[1]]) == [[0,0]]

def test_tle():
    n = 200
    heights = [[i+j for j in range(n)] for i in range(n)]
    t0 = time.time()
    pacificAtlantic(heights)
    assert time.time() - t0 < 2, "TLE"

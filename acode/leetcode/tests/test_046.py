"""Tests for 046 Max Area of Island (LC#695)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
maxAreaOfIsland = import_module("046_max_area_of_island").maxAreaOfIsland

def test_basic():
    grid = [[0,0,1,0,0],[0,0,0,0,0],[0,1,1,0,0],[0,1,1,0,0],[0,0,0,0,0]]
    assert maxAreaOfIsland(grid) == 4

def test_no_island():
    assert maxAreaOfIsland([[0,0],[0,0]]) == 0

def test_single_one():
    assert maxAreaOfIsland([[0,0],[0,1]]) == 1

def test_tle():
    grid = [[1]*50 for _ in range(50)]
    t0 = time.time()
    assert maxAreaOfIsland(grid) == 2500
    assert time.time() - t0 < 2, "TLE"

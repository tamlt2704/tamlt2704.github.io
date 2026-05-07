"""Tests for 044 Number of Islands (LC#200)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
numIslands = import_module("044_number_of_islands").numIslands

def test_basic_two_islands():
    grid = [["1","1","0","0","0"],["1","1","0","0","0"],["0","0","1","0","0"],["0","0","0","1","1"]]
    assert numIslands(grid) == 3

def test_all_water():
    assert numIslands([["0","0"],["0","0"]]) == 0

def test_all_land():
    assert numIslands([["1","1"],["1","1"]]) == 1

def test_single_cell_land():
    assert numIslands([["1"]]) == 1

def test_single_cell_water():
    assert numIslands([["0"]]) == 0

def test_tle():
    n = 300
    grid = [["1" if (i+j) % 2 == 0 else "0" for j in range(n)] for i in range(n)]
    t0 = time.time()
    numIslands(grid)
    assert time.time() - t0 < 2, "TLE"

"""Tests for 106 Longest Increasing Path in a Matrix (LC#329)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("106_longest_increasing_path_in_a_matrix").Solution

def test_basic():
    assert Sol().longestIncreasingPath([[9,9,4],[6,6,8],[2,1,1]]) == 4

def test_single_cell():
    assert Sol().longestIncreasingPath([[1]]) == 1

def test_increasing_row():
    assert Sol().longestIncreasingPath([[1, 2, 3, 4, 5]]) == 5

def test_all_same():
    assert Sol().longestIncreasingPath([[7,7],[7,7]]) == 1

def test_tle():
    import random
    random.seed(42)
    m, n = 200, 200
    matrix = [[random.randint(0, 2**31 - 1) for _ in range(n)] for _ in range(m)]
    t0 = time.time()
    res = Sol().longestIncreasingPath(matrix)
    assert time.time() - t0 < 2, "TLE"
    assert res >= 1

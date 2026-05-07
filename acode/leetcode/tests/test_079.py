import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module

mod = import_module('079_n_queens')
solveNQueens = mod.solveNQueens


def test_n1():
    result = solveNQueens(1)
    assert len(result) == 1
    assert result == [["Q"]]


def test_n4():
    result = solveNQueens(4)
    assert len(result) == 2


def test_n8():
    result = solveNQueens(8)
    assert len(result) == 92


def test_tle_n9():
    start = time.time()
    result = solveNQueens(9)
    elapsed = time.time() - start
    assert len(result) == 352
    assert elapsed < 2, f"TLE: {elapsed:.2f}s"

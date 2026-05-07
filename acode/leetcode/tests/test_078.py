import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module

mod = import_module('078_word_search')
exist = mod.exist

BOARD = [
    ["A","B","C","E"],
    ["S","F","C","S"],
    ["A","D","E","E"]
]


def test_abcced():
    assert exist(BOARD, "ABCCED") is True


def test_see():
    assert exist(BOARD, "SEE") is True


def test_abcb():
    assert exist(BOARD, "ABCB") is False


def test_single_cell_match():
    assert exist([["A"]], "A") is True


def test_single_cell_no_match():
    assert exist([["A"]], "B") is False


def test_tle_large_board():
    start = time.time()
    board = [["A","B","C","D","E","F"],
             ["G","H","I","J","K","L"],
             ["M","N","O","P","Q","R"],
             ["S","T","U","V","W","X"],
             ["Y","Z","A","B","C","D"],
             ["E","F","G","H","I","J"]]
    result = exist(board, "ABCDEFKLQRWXDCBA")
    elapsed = time.time() - start
    assert isinstance(result, bool)
    assert elapsed < 2, f"TLE: {elapsed:.2f}s"

"""Tests for 043 Word Search II (LC#212)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("043_word_search_ii").Solution

def test_basic():
    board = [["o","a","a","n"],["e","t","a","e"],["i","h","k","r"],["i","f","l","v"]]
    result = sorted(Sol().findWords(board, ["oath","pea","eat","rain"]))
    assert result == ["eat", "oath"]

def test_no_match():
    board = [["a","b"],["c","d"]]
    assert Sol().findWords(board, ["xyz"]) == []

def test_single_cell():
    board = [["a"]]
    assert Sol().findWords(board, ["a"]) == ["a"]

def test_tle():
    import string, random
    random.seed(42)
    board = [[random.choice(string.ascii_lowercase) for _ in range(12)] for _ in range(12)]
    words = ["".join(random.choices(string.ascii_lowercase, k=5)) for _ in range(30000)]
    t0 = time.time()
    Sol().findWords(board, words)
    assert time.time() - t0 < 5, "TLE"

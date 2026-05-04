"""Tests for 073 Distinct Subsequences (LC#115)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
numDistinct = import_module("073_distinct_subsequences").numDistinct

def test_basic():
    assert numDistinct("rabbbit", "rabbit") == 3

def test_basic2():
    assert numDistinct("babgbag", "bag") == 5

def test_no_match():
    assert numDistinct("a", "b") == 0

def test_tle():
    t0 = time.time()
    numDistinct("a" * 1000, "a" * 500)
    assert time.time() - t0 < 2, "TLE"

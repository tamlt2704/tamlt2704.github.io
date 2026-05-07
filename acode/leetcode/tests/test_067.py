"""Tests for 067 Edit Distance (LC#72)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
minDistance = import_module("067_edit_distance").minDistance

def test_basic():
    assert minDistance("horse", "ros") == 3

def test_basic2():
    assert minDistance("intention", "execution") == 5

def test_both_empty():
    assert minDistance("", "") == 0

def test_one_empty():
    assert minDistance("a", "") == 1

def test_tle():
    t0 = time.time()
    minDistance("a" * 500, "b" * 500)
    assert time.time() - t0 < 2, "TLE"

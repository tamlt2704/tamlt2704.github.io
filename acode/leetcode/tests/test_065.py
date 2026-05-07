"""Tests for 065 Unique Paths (LC#62)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
uniquePaths = import_module("065_unique_paths").uniquePaths

def test_basic():
    assert uniquePaths(3, 7) == 28

def test_one_by_one():
    assert uniquePaths(1, 1) == 1

def test_large():
    r = uniquePaths(100, 100)
    assert r > 0

def test_tle():
    t0 = time.time()
    uniquePaths(100, 100)
    assert time.time() - t0 < 2, "TLE"

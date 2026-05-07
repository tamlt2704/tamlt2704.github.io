"""Tests for 069 Burst Balloons (LC#312)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
maxCoins = import_module("069_burst_balloons").maxCoins

def test_basic():
    assert maxCoins([3, 1, 5, 8]) == 167

def test_two():
    assert maxCoins([1, 5]) == 10

def test_single():
    assert maxCoins([5]) == 5

def test_tle():
    t0 = time.time()
    maxCoins(list(range(1, 301)))
    assert time.time() - t0 < 10, "TLE"

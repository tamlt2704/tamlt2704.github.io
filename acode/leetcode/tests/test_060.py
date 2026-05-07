"""Tests for 060 House Robber (LC#198)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
rob = import_module("060_house_robber").rob

def test_basic():
    assert rob([1, 2, 3, 1]) == 4

def test_basic2():
    assert rob([2, 7, 9, 3, 1]) == 12

def test_single():
    assert rob([5]) == 5

def test_single_zero():
    assert rob([0]) == 0

def test_tle():
    t0 = time.time()
    rob(list(range(100)))
    assert time.time() - t0 < 2, "TLE"

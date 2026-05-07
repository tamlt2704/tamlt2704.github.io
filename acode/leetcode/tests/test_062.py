"""Tests for 062 Coin Change (LC#322)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
coinChange = import_module("062_coin_change").coinChange

def test_basic():
    assert coinChange([1, 2, 5], 11) == 3

def test_impossible():
    assert coinChange([2], 3) == -1

def test_zero_amount():
    assert coinChange([1], 0) == 0

def test_tle():
    t0 = time.time()
    coinChange([1, 2, 5], 10000)
    assert time.time() - t0 < 2, "TLE"

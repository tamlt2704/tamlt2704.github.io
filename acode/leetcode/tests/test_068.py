"""Tests for 068 Coin Change II (LC#518)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
change = import_module("068_coin_change_ii").change

def test_basic():
    assert change(5, [1, 2, 5]) == 4

def test_impossible():
    assert change(3, [2]) == 0

def test_zero_amount():
    assert change(0, [7]) == 1

def test_tle():
    t0 = time.time()
    change(5000, [1, 2, 5])
    assert time.time() - t0 < 2, "TLE"

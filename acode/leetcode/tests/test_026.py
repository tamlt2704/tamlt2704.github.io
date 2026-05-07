"""Tests for 026 Daily Temperatures (LC#739)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("026_daily_temperatures").Solution

def test_basic():
    assert Sol().dailyTemperatures([73,74,75,71,69,72,76,73]) == [1,1,4,2,1,1,0,0]

def test_decreasing():
    assert Sol().dailyTemperatures([5,4,3,2,1]) == [0,0,0,0,0]

def test_increasing():
    assert Sol().dailyTemperatures([1,2,3,4,5]) == [1,1,1,1,0]

def test_single():
    assert Sol().dailyTemperatures([30]) == [0]

def test_tle():
    temps = list(range(10**5, 0, -1))
    t0 = time.time()
    r = Sol().dailyTemperatures(temps)
    assert time.time() - t0 < 1, "TLE"
    assert r == [0] * 10**5

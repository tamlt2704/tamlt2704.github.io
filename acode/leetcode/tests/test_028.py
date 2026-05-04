"""Tests for 028 Car Fleet (LC#853)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("028_car_fleet").Solution

def test_basic():
    assert Sol().carFleet(12, [10,8,0,5,3], [2,4,1,1,3]) == 3

def test_single():
    assert Sol().carFleet(10, [3], [3]) == 1

def test_all_same_speed():
    assert Sol().carFleet(100, [0,2,4], [2,2,2]) == 3

def test_tle():
    n = 10**5
    pos = list(range(n))
    speed = [1] * n
    t0 = time.time()
    Sol().carFleet(n, pos, speed)
    assert time.time() - t0 < 1, "TLE"

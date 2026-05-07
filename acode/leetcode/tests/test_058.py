"""Tests for 058 Swim in Rising Water (LC#778)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
swimInWater = import_module("058_swim_in_rising_water").swimInWater

def test_basic():
    assert swimInWater([[0,2],[1,3]]) == 3

def test_5x5():
    grid = [[0,1,2,3,4],[24,23,22,21,5],[12,13,14,15,16],[11,17,18,19,20],[10,9,8,7,6]]
    assert swimInWater(grid) == 16

def test_tle():
    import random
    n = 50
    vals = list(range(n*n))
    random.seed(42)
    random.shuffle(vals)
    grid = [vals[i*n:(i+1)*n] for i in range(n)]
    t0 = time.time()
    swimInWater(grid)
    assert time.time() - t0 < 2, "TLE"

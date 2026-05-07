"""Tests for 059 Climbing Stairs (LC#70)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
climbStairs = import_module("059_climbing_stairs").climbStairs

def test_one_step():
    assert climbStairs(1) == 1

def test_two_steps():
    assert climbStairs(2) == 2

def test_three_steps():
    assert climbStairs(3) == 3

def test_large():
    assert climbStairs(45) == 1836311903

def test_tle():
    t0 = time.time()
    climbStairs(45)
    assert time.time() - t0 < 2, "TLE"

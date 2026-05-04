"""Tests for 104 Min Cost to Connect All Points (LC#1584)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("104_min_cost_to_connect_all_points").Solution

def test_basic():
    assert Sol().minCostConnectPoints([[0,0],[2,2],[3,10],[5,2],[7,0]]) == 20

def test_single_point():
    assert Sol().minCostConnectPoints([[0, 0]]) == 0

def test_two_points():
    assert Sol().minCostConnectPoints([[0, 0], [1, 1]]) == 2

def test_collinear():
    assert Sol().minCostConnectPoints([[0,0],[1,0],[2,0],[3,0]]) == 3

def test_tle():
    import random
    random.seed(42)
    points = [[random.randint(-10**6, 10**6), random.randint(-10**6, 10**6)] for _ in range(1000)]
    t0 = time.time()
    res = Sol().minCostConnectPoints(points)
    assert time.time() - t0 < 2, "TLE"
    assert res > 0

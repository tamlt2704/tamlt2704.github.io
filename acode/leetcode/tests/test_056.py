"""Tests for 056 Network Delay Time (LC#743)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
networkDelayTime = import_module("056_network_delay_time").networkDelayTime

def test_basic():
    assert networkDelayTime([[2,1,1],[2,3,1],[3,4,1]], 4, 2) == 2

def test_unreachable():
    assert networkDelayTime([[1,2,1]], 3, 1) == -1

def test_single_node():
    assert networkDelayTime([], 1, 1) == 0

def test_tle():
    n = 100
    times = []
    for i in range(1, n+1):
        for j in range(1, min(n+1, i+61)):
            if i != j:
                times.append([i, j, i+j])
    t0 = time.time()
    networkDelayTime(times, n, 1)
    assert time.time() - t0 < 2, "TLE"

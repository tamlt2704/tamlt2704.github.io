"""Tests for 024 Min Stack (LC#155)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
MinStack = import_module("024_min_stack").MinStack

def test_basic():
    s = MinStack()
    s.push(-2); s.push(0); s.push(-3)
    assert s.getMin() == -3
    s.pop()
    assert s.top() == 0
    assert s.getMin() == -2

def test_single():
    s = MinStack()
    s.push(5)
    assert s.top() == 5
    assert s.getMin() == 5

def test_tle():
    s = MinStack()
    t0 = time.time()
    for i in range(30000):
        s.push(i)
    assert s.getMin() == 0
    for _ in range(30000):
        s.pop()
    assert time.time() - t0 < 1, "TLE"

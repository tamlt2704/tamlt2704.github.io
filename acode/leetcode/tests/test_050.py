"""Tests for 050 Course Schedule (LC#207)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
canFinish = import_module("050_course_schedule").canFinish

def test_basic():
    assert canFinish(2, [[1,0]]) == True

def test_cycle():
    assert canFinish(2, [[1,0],[0,1]]) == False

def test_no_prereqs():
    assert canFinish(3, []) == True

def test_tle():
    n = 2000
    prereqs = [[i, i-1] for i in range(1, n)]
    t0 = time.time()
    assert canFinish(n, prereqs) == True
    assert time.time() - t0 < 2, "TLE"

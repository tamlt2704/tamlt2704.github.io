"""Tests for 072 Maximum Profit in Job Scheduling (LC#1235)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
jobScheduling = import_module("072_maximum_profit_in_job_scheduling").jobScheduling

def test_basic():
    assert jobScheduling([1, 2, 3, 3], [3, 4, 5, 6], [50, 10, 40, 70]) == 120

def test_single_job():
    assert jobScheduling([1], [2], [50]) == 50

def test_tle():
    n = 50000
    t0 = time.time()
    jobScheduling(list(range(n)), list(range(1, n + 1)), [1] * n)
    assert time.time() - t0 < 2, "TLE"

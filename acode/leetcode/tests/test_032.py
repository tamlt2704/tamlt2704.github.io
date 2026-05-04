"""Tests for 032 Task Scheduler (LC#621)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("032_task_scheduler").Solution

def test_basic():
    assert Sol().leastInterval(["A","A","A","B","B","B"], 2) == 8

def test_no_cooldown():
    assert Sol().leastInterval(["A","A","A","B","B","B"], 0) == 6

def test_single_task():
    assert Sol().leastInterval(["A"], 2) == 1

def test_all_same():
    assert Sol().leastInterval(["A","A","A"], 2) == 7

def test_tle():
    tasks = ["A"] * 5000 + ["B"] * 5000
    t0 = time.time()
    Sol().leastInterval(tasks, 100)
    assert time.time() - t0 < 1, "TLE"

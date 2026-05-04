"""Tests for 019 Linked List Cycle (LC#141)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from helpers import build_list_cycle, build_list
from importlib import import_module
Sol = import_module("019_linked_list_cycle").Solution

def test_has_cycle():
    assert Sol().hasCycle(build_list_cycle([3,2,0,-4], 1)) is True

def test_no_cycle():
    assert Sol().hasCycle(build_list([1,2])) is False

def test_single_no_cycle():
    assert Sol().hasCycle(build_list([1])) is False

def test_empty():
    assert Sol().hasCycle(None) is False

def test_self_cycle():
    assert Sol().hasCycle(build_list_cycle([1], 0)) is True

def test_tle():
    head = build_list_cycle(list(range(10**4)), 0)
    t0 = time.time()
    assert Sol().hasCycle(head) is True
    assert time.time() - t0 < 1, "TLE"

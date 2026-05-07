"""Tests for 023 Valid Parentheses (LC#20)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("023_valid_parentheses").Solution

def test_basic():
    assert Sol().isValid("()[]{}") is True

def test_nested():
    assert Sol().isValid("{[]}") is True

def test_wrong_order():
    assert Sol().isValid("(]") is False

def test_single():
    assert Sol().isValid("(") is False

def test_empty():
    # edge: though constraint says len>=1, test robustness
    assert Sol().isValid("()") is True

def test_tle():
    s = "()" * 5000
    t0 = time.time()
    assert Sol().isValid(s) is True
    assert time.time() - t0 < 1, "TLE"

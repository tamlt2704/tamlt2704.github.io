"""Tests for 015 Minimum Window Substring (LC#76)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("015_minimum_window_substring").Solution

def test_basic():
    assert Sol().minWindow("ADOBECODEBANC", "ABC") == "BANC"

def test_exact():
    assert Sol().minWindow("a", "a") == "a"

def test_no_match():
    assert Sol().minWindow("a", "aa") == ""

def test_t_equals_s():
    assert Sol().minWindow("abc", "abc") == "abc"

def test_tle():
    s = "a" * 50000 + "b" + "a" * 49999
    t0 = time.time()
    assert Sol().minWindow(s, "b") == "b"
    assert time.time() - t0 < 1, "TLE"

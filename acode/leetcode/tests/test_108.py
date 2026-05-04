"""Tests for 108 Find the Shortest Superstring (LC#943)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("108_find_the_shortest_superstring").Solution

def test_basic():
    res = Sol().shortestSuperstring(["alex", "loves", "leetcode"])
    for w in ["alex", "loves", "leetcode"]:
        assert w in res

def test_overlap():
    res = Sol().shortestSuperstring(["catg", "ctaagt", "gcta", "ttca", "atgcatc"])
    for w in ["catg", "ctaagt", "gcta", "ttca", "atgcatc"]:
        assert w in res

def test_single():
    assert Sol().shortestSuperstring(["abc"]) == "abc"

def test_no_overlap():
    res = Sol().shortestSuperstring(["abc", "def"])
    assert "abc" in res and "def" in res
    assert len(res) == 6

def test_tle():
    words = [chr(ord('a') + i) * 5 + str(i) for i in range(12)]
    t0 = time.time()
    res = Sol().shortestSuperstring(words)
    assert time.time() - t0 < 2, "TLE"
    for w in words:
        assert w in res

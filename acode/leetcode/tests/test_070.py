"""Tests for 070 Regular Expression Matching (LC#10)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
isMatch = import_module("070_regular_expression_matching").isMatch

def test_no_match():
    assert isMatch("aa", "a") is False

def test_star():
    assert isMatch("aa", "a*") is True

def test_dot_star():
    assert isMatch("ab", ".*") is True

def test_complex():
    assert isMatch("mississippi", "mis*is*p*.") is False

def test_both_empty():
    assert isMatch("", "") is True

def test_empty_star():
    assert isMatch("", "a*") is True

def test_tle():
    t0 = time.time()
    isMatch("a" * 20, "a*" * 10 + "a" * 20)
    assert time.time() - t0 < 2, "TLE"

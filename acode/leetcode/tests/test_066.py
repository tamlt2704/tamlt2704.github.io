"""Tests for 066 Longest Common Subsequence (LC#1143)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
longestCommonSubsequence = import_module("066_longest_common_subsequence").longestCommonSubsequence

def test_basic():
    assert longestCommonSubsequence("abcde", "ace") == 3

def test_identical():
    assert longestCommonSubsequence("abc", "abc") == 3

def test_no_common():
    assert longestCommonSubsequence("abc", "def") == 0

def test_tle():
    t0 = time.time()
    longestCommonSubsequence("a" * 1000, "b" * 1000)
    assert time.time() - t0 < 2, "TLE"

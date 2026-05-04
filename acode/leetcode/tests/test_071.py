"""Tests for 071 Longest Palindromic Subsequence (LC#516)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
longestPalindromeSubseq = import_module("071_longest_palindromic_subsequence").longestPalindromeSubseq

def test_basic():
    assert longestPalindromeSubseq("bbbab") == 4

def test_basic2():
    assert longestPalindromeSubseq("cbbd") == 2

def test_single():
    assert longestPalindromeSubseq("a") == 1

def test_tle():
    t0 = time.time()
    longestPalindromeSubseq("ab" * 500)
    assert time.time() - t0 < 2, "TLE"

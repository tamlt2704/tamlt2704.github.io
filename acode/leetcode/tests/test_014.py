"""Tests for 014 Longest Substring Without Repeating Characters (LC#3)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("014_longest_substring_without_repeating_characters").Solution

def test_basic():
    assert Sol().lengthOfLongestSubstring("abcabcbb") == 3

def test_all_same():
    assert Sol().lengthOfLongestSubstring("bbbbb") == 1

def test_mixed():
    assert Sol().lengthOfLongestSubstring("pwwkew") == 3

def test_empty():
    assert Sol().lengthOfLongestSubstring("") == 0

def test_single():
    assert Sol().lengthOfLongestSubstring("a") == 1

def test_all_unique():
    assert Sol().lengthOfLongestSubstring("abcdef") == 6

def test_tle():
    s = "abcdefghij" * 5000
    t0 = time.time()
    assert Sol().lengthOfLongestSubstring(s) == 10
    assert time.time() - t0 < 1, "TLE"

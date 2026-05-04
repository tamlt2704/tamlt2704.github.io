"""Tests for 008 Valid Anagram (LC#242)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("008_valid_anagram").Solution

def test_true():
    assert Sol().isAnagram("anagram", "nagaram") is True

def test_false():
    assert Sol().isAnagram("rat", "car") is False

def test_diff_len():
    assert Sol().isAnagram("a", "ab") is False

def test_single_char():
    assert Sol().isAnagram("a", "a") is True

def test_empty():
    assert Sol().isAnagram("", "") is True

def test_tle():
    s = "a" * 25000 + "b" * 25000
    t = "b" * 25000 + "a" * 25000
    t0 = time.time()
    assert Sol().isAnagram(s, t) is True
    assert time.time() - t0 < 1, "TLE"

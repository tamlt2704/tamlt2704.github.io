"""Tests for 063 Word Break (LC#139)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
wordBreak = import_module("063_word_break").wordBreak

def test_leetcode():
    assert wordBreak("leetcode", ["leet", "code"]) is True

def test_applepenapple():
    assert wordBreak("applepenapple", ["apple", "pen"]) is True

def test_catsandog():
    assert wordBreak("catsandog", ["cats", "dog", "sand", "and", "cat"]) is False

def test_tle():
    t0 = time.time()
    s = 'a' * 300
    d = ['a' * i for i in range(1, 301)]
    wordBreak(s, d)
    assert time.time() - t0 < 2, "TLE"

"""Tests for 042 Design Add and Search Words (LC#211)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
WordDictionary = import_module("042_design_add_and_search_words").WordDictionary

def test_basic():
    wd = WordDictionary()
    wd.addWord("bad")
    assert wd.search("bad") is True
    assert wd.search("b..") is True
    assert wd.search("b.d") is True
    assert wd.search(".ad") is True
    assert wd.search("...") is True
    assert wd.search("....") is False

def test_tle():
    wd = WordDictionary()
    t0 = time.time()
    for i in range(10000):
        wd.addWord("word" + str(i))
    for i in range(1000):
        wd.search("w...")
        wd.search("wor." + str(i))
    assert time.time() - t0 < 2, "TLE"

"""Tests for 041 Implement Trie (LC#208)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Trie = import_module("041_implement_trie").Trie

def test_basic():
    t = Trie()
    t.insert("apple")
    assert t.search("apple") is True
    assert t.search("app") is False
    assert t.startsWith("app") is True
    t.insert("app")
    assert t.search("app") is True

def test_tle():
    t = Trie()
    t0 = time.time()
    for i in range(2000):
        t.insert("a" * 2000 + str(i))
    for i in range(2000):
        t.search("a" * 2000 + str(i))
    assert time.time() - t0 < 2, "TLE"

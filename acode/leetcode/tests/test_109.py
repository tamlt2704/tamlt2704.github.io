"""Tests for 109 LRU Cache (LC#146)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
LRUCache = import_module("109_lru_cache").LRUCache

def test_basic():
    c = LRUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    assert c.get(1) == 1
    c.put(3, 3)  # evicts key 2
    assert c.get(2) == -1
    c.put(4, 4)  # evicts key 1
    assert c.get(1) == -1
    assert c.get(3) == 3
    assert c.get(4) == 4

def test_update_existing():
    c = LRUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    c.put(1, 10)  # update, key 1 becomes most recent
    c.put(3, 3)   # evicts key 2
    assert c.get(2) == -1
    assert c.get(1) == 10

def test_get_refreshes():
    c = LRUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    c.get(1)      # refresh key 1
    c.put(3, 3)   # evicts key 2
    assert c.get(1) == 1
    assert c.get(2) == -1

def test_tle():
    c = LRUCache(1000)
    t0 = time.time()
    for i in range(10**4):
        c.put(i, i)
        c.get(i // 2)
    assert time.time() - t0 < 2, "TLE"

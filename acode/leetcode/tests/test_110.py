"""Tests for 110 LFU Cache (LC#460)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
LFUCache = import_module("110_lfu_cache").LFUCache

def test_basic():
    c = LFUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    assert c.get(1) == 1       # freq(1)=2
    c.put(3, 3)                 # evicts key 2 (least frequent)
    assert c.get(2) == -1
    assert c.get(3) == 3
    c.put(4, 4)                 # evicts key 3 (freq 1 vs key 1 freq 2)
    assert c.get(1) == 1
    assert c.get(3) == -1
    assert c.get(4) == 4

def test_tie_break_lru():
    c = LFUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    # Both freq=1, key 1 is older (LRU)
    c.put(3, 3)  # evicts key 1
    assert c.get(1) == -1
    assert c.get(2) == 2

def test_update_value():
    c = LFUCache(2)
    c.put(1, 10)
    c.put(1, 20)
    assert c.get(1) == 20

def test_zero_capacity():
    c = LFUCache(0)
    c.put(0, 0)
    assert c.get(0) == -1

def test_tle():
    c = LFUCache(1000)
    t0 = time.time()
    for i in range(10**4):
        c.put(i, i)
        c.get(i // 2)
    assert time.time() - t0 < 2, "TLE"

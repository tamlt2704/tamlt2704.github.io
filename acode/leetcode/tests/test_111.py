"""Tests for 111 Insert Delete GetRandom O(1) (LC#380)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
RandomizedSet = import_module("111_insert_delete_getrandom_o1").RandomizedSet

def test_basic():
    rs = RandomizedSet()
    assert rs.insert(1) == True
    assert rs.remove(2) == False
    assert rs.insert(2) == True
    assert rs.getRandom() in (1, 2)
    assert rs.remove(1) == True
    assert rs.insert(2) == False
    assert rs.getRandom() == 2

def test_duplicate_insert():
    rs = RandomizedSet()
    assert rs.insert(5) == True
    assert rs.insert(5) == False

def test_remove_and_reinsert():
    rs = RandomizedSet()
    rs.insert(1)
    rs.remove(1)
    assert rs.insert(1) == True

def test_tle():
    rs = RandomizedSet()
    t0 = time.time()
    for i in range(2 * 10**5):
        rs.insert(i)
    for i in range(0, 2 * 10**5, 2):
        rs.remove(i)
    for _ in range(10**5):
        rs.getRandom()
    assert time.time() - t0 < 2, "TLE"

"""Tests for 029 Kth Largest Element in a Stream (LC#703)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
KthLargest = import_module("029_kth_largest_element_in_a_stream").KthLargest

def test_basic():
    kl = KthLargest(3, [4, 5, 8, 2])
    assert kl.add(3) == 4
    assert kl.add(5) == 5
    assert kl.add(10) == 5
    assert kl.add(9) == 8
    assert kl.add(4) == 8

def test_k1():
    kl = KthLargest(1, [])
    assert kl.add(1) == 1
    assert kl.add(2) == 2

def test_tle():
    kl = KthLargest(5000, list(range(5000)))
    t0 = time.time()
    for i in range(5000, 10000):
        kl.add(i)
    assert time.time() - t0 < 1, "TLE"

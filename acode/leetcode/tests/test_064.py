"""Tests for 064 Maximum Product Subarray (LC#152)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
maxProduct = import_module("064_maximum_product_subarray").maxProduct

def test_basic():
    assert maxProduct([2, 3, -2, 4]) == 6

def test_with_zero():
    assert maxProduct([-2, 0, -1]) == 0

def test_single_negative():
    assert maxProduct([-2]) == -2

def test_two_negatives():
    assert maxProduct([-2, -3]) == 6

def test_tle():
    t0 = time.time()
    maxProduct([(-1) ** i * (i + 1) for i in range(20000)])
    assert time.time() - t0 < 2, "TLE"

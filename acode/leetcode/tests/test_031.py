"""Tests for 031 Find Median from Data Stream (LC#295)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
MedianFinder = import_module("031_find_median_from_data_stream").MedianFinder

def test_basic():
    mf = MedianFinder()
    mf.addNum(1); mf.addNum(2)
    assert mf.findMedian() == 1.5
    mf.addNum(3)
    assert mf.findMedian() == 2.0

def test_single():
    mf = MedianFinder()
    mf.addNum(5)
    assert mf.findMedian() == 5.0

def test_negative():
    mf = MedianFinder()
    mf.addNum(-1); mf.addNum(-2)
    assert mf.findMedian() == -1.5

def test_tle():
    mf = MedianFinder()
    t0 = time.time()
    for i in range(50000):
        mf.addNum(i)
    mf.findMedian()
    assert time.time() - t0 < 2, "TLE"

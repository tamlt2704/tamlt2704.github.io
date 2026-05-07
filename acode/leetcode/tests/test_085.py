import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module

mod = import_module('085_non_overlapping_intervals')
sol = mod.Solution()

def test_basic():
    assert sol.eraseOverlapIntervals([[1,2],[2,3],[3,4],[1,3]]) == 1

def test_all_same():
    assert sol.eraseOverlapIntervals([[1,2],[1,2],[1,2]]) == 2

def test_no_overlap():
    assert sol.eraseOverlapIntervals([[1,2],[2,3]]) == 0

def test_tle():
    intervals = [[i, i+1] for i in range(10**5)]
    start = time.time()
    sol.eraseOverlapIntervals(intervals)
    assert time.time() - start < 1.0

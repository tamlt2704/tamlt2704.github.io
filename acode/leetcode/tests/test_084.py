import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module

mod = import_module('084_merge_intervals')
sol = mod.Solution()

def test_basic():
    assert sol.merge([[1,3],[2,6],[8,10],[15,18]]) == [[1,6],[8,10],[15,18]]

def test_touching():
    assert sol.merge([[1,4],[4,5]]) == [[1,5]]

def test_single():
    assert sol.merge([[1,2]]) == [[1,2]]

def test_tle():
    intervals = [[i, i+2] for i in range(0, 2*10**4, 2)]
    start = time.time()
    sol.merge(intervals)
    assert time.time() - start < 1.0

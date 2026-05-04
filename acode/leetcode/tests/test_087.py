import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module

mod = import_module('087_minimum_interval_to_include_each_query')
sol = mod.Solution()

def test_basic():
    assert sol.minInterval([[1,4],[2,4],[3,6],[4,4]], [2,3,4,5]) == [3,3,1,4]

def test_basic2():
    assert sol.minInterval([[2,3],[2,5],[1,8],[20,25]], [2,19,5,22]) == [2,4,-1,6]

def test_tle():
    n = 10**5
    intervals = [[i, i+5] for i in range(n)]
    queries = list(range(n))
    start = time.time()
    sol.minInterval(intervals, queries)
    assert time.time() - start < 2.0

import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module

mod = import_module('074_subsets')
subsets = mod.subsets


def test_basic():
    result = subsets([1, 2, 3])
    assert len(result) == 8
    for s in [[], [1], [2], [3], [1,2], [1,3], [2,3], [1,2,3]]:
        assert sorted(s) in [sorted(r) for r in result]


def test_empty():
    assert subsets([]) == [[]]


def test_single():
    result = subsets([0])
    assert sorted([sorted(r) for r in result]) == [[], [0]]


def test_tle_10_elements():
    start = time.time()
    result = subsets(list(range(10)))
    elapsed = time.time() - start
    assert len(result) == 1024
    assert elapsed < 2, f"TLE: {elapsed:.2f}s"

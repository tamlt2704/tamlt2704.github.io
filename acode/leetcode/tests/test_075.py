import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module

mod = import_module('075_permutations')
permute = mod.permute


def test_basic():
    result = permute([1, 2, 3])
    assert len(result) == 6
    for p in [[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]:
        assert p in result


def test_two_elements():
    result = permute([0, 1])
    assert len(result) == 2
    assert sorted(result) == [[0,1],[1,0]]


def test_single():
    assert permute([1]) == [[1]]


def test_tle_6_elements():
    start = time.time()
    result = permute(list(range(6)))
    elapsed = time.time() - start
    assert len(result) == 720
    assert elapsed < 2, f"TLE: {elapsed:.2f}s"

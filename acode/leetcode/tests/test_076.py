import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module

mod = import_module('076_combination_sum')
combinationSum = mod.combinationSum


def test_basic():
    result = combinationSum([2, 3, 6, 7], 7)
    expected = [[2, 2, 3], [7]]
    assert sorted([sorted(r) for r in result]) == sorted([sorted(e) for e in expected])


def test_multiple_combos():
    result = combinationSum([2, 3, 5], 8)
    expected = [[2, 2, 2, 2], [2, 3, 3], [3, 5]]
    assert sorted([sorted(r) for r in result]) == sorted([sorted(e) for e in expected])


def test_no_solution():
    assert combinationSum([2], 1) == []


def test_tle_large_target():
    start = time.time()
    result = combinationSum([2, 3, 5, 7, 11, 13], 40)
    elapsed = time.time() - start
    assert len(result) > 0
    for combo in result:
        assert sum(combo) == 40
    assert elapsed < 2, f"TLE: {elapsed:.2f}s"

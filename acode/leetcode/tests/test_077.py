import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module

mod = import_module('077_combination_sum_ii')
combinationSum2 = mod.combinationSum2


def test_basic():
    result = combinationSum2([10, 1, 2, 7, 6, 1, 5], 8)
    expected = [[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]
    assert sorted([sorted(r) for r in result]) == sorted([sorted(e) for e in expected])


def test_duplicates():
    result = combinationSum2([2, 5, 2, 1, 2], 5)
    expected = [[1, 2, 2], [5]]
    assert sorted([sorted(r) for r in result]) == sorted([sorted(e) for e in expected])


def test_tle_100_candidates():
    start = time.time()
    candidates = [1] * 50 + [2] * 30 + [3] * 20
    result = combinationSum2(candidates, 10)
    elapsed = time.time() - start
    for combo in result:
        assert sum(combo) == 10
    # no duplicate combos
    seen = set()
    for combo in result:
        key = tuple(sorted(combo))
        assert key not in seen
        seen.add(key)
    assert elapsed < 2, f"TLE: {elapsed:.2f}s"

import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module

mod = import_module('080_palindrome_partitioning')
partition = mod.partition


def test_aab():
    result = partition("aab")
    expected = [["a", "a", "b"], ["aa", "b"]]
    assert sorted(result) == sorted(expected)


def test_single_char():
    assert partition("a") == [["a"]]


def test_tle_long_palindrome():
    start = time.time()
    result = partition("a" * 16)
    elapsed = time.time() - start
    assert len(result) > 0
    for parts in result:
        assert "".join(parts) == "a" * 16
        for p in parts:
            assert p == p[::-1]
    assert elapsed < 2, f"TLE: {elapsed:.2f}s"

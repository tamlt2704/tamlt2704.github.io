"""Tests for 004 Group Anagrams (LC#49)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("004_group_anagrams").Solution

def normalize(result):
    return sorted(sorted(g) for g in result)

def test_basic():
    r = Sol().groupAnagrams(["eat","tea","tan","ate","nat","bat"])
    assert normalize(r) == [["ate","eat","tea"],["bat"],["nat","tan"]]

def test_empty_string():
    assert normalize(Sol().groupAnagrams([""])) == [[""]]

def test_single():
    assert normalize(Sol().groupAnagrams(["a"])) == [["a"]]

def test_no_anagrams():
    r = Sol().groupAnagrams(["abc","def","ghi"])
    assert len(r) == 3

def test_tle():
    strs = ["".join(chr(97 + (i * j) % 26) for j in range(100)) for i in range(10**4)]
    t0 = time.time()
    Sol().groupAnagrams(strs)
    assert time.time() - t0 < 2, "TLE"

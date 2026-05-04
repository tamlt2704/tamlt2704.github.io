"""Tests for 006 Encode and Decode Strings (LC#271)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("006_encode_and_decode_strings").Solution

def test_basic():
    s = Sol()
    strs = ["lint", "code", "love", "you"]
    assert s.decode(s.encode(strs)) == strs

def test_empty_list():
    s = Sol()
    assert s.decode(s.encode([])) == []

def test_empty_strings():
    s = Sol()
    strs = ["", "", ""]
    assert s.decode(s.encode(strs)) == strs

def test_special_chars():
    s = Sol()
    strs = ["#", "4#abc", ":", ""]
    assert s.decode(s.encode(strs)) == strs

def test_tle():
    s = Sol()
    strs = ["a" * 200] * 200
    t0 = time.time()
    assert s.decode(s.encode(strs)) == strs
    assert time.time() - t0 < 1, "TLE"

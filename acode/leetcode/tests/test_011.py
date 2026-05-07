"""Tests for 011 Valid Palindrome (LC#125)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("011_valid_palindrome").Solution

def test_basic():
    assert Sol().isPalindrome("A man, a plan, a canal: Panama") is True

def test_false():
    assert Sol().isPalindrome("race a car") is False

def test_empty():
    assert Sol().isPalindrome(" ") is True

def test_only_special():
    assert Sol().isPalindrome(".,") is True

def test_single_char():
    assert Sol().isPalindrome("a") is True

def test_tle():
    s = "a" * 10**5
    t0 = time.time()
    assert Sol().isPalindrome(s) is True
    assert time.time() - t0 < 1, "TLE"

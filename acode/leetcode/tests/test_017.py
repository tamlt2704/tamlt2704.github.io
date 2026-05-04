"""Tests for 017 Reverse Linked List (LC#206)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from helpers import build_list, list_to_arr
from importlib import import_module
mod = import_module("017_reverse_linked_list")
Sol = mod.Solution; ListNode = mod.ListNode

def test_basic():
    assert list_to_arr(Sol().reverseList(build_list([1,2,3,4,5]))) == [5,4,3,2,1]

def test_single():
    assert list_to_arr(Sol().reverseList(build_list([1]))) == [1]

def test_empty():
    assert Sol().reverseList(None) is None

def test_two():
    assert list_to_arr(Sol().reverseList(build_list([1,2]))) == [2,1]

def test_tle():
    head = build_list(list(range(5000)))
    t0 = time.time()
    r = Sol().reverseList(head)
    assert time.time() - t0 < 1, "TLE"
    assert list_to_arr(r)[0] == 4999

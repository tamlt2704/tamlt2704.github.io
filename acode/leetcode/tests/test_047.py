"""Tests for 047 Rotting Oranges (LC#994)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
orangesRotting = import_module("047_rotting_oranges").orangesRotting

def test_basic():
    assert orangesRotting([[2,1,1],[1,1,0],[0,1,1]]) == 4

def test_already_rotten():
    assert orangesRotting([[2,2],[2,2]]) == 0

def test_impossible():
    assert orangesRotting([[2,1,1],[0,1,1],[1,0,1]]) == -1

def test_no_oranges():
    assert orangesRotting([[0,0],[0,0]]) == 0

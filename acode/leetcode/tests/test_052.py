"""Tests for 052 Alien Dictionary (LC#269)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
alienOrder = import_module("052_alien_dictionary").alienOrder

def test_basic():
    assert alienOrder(["wrt","wrf","er","ett","rftt"]) == "wertf"

def test_invalid():
    assert alienOrder(["z","x","z"]) == ""

def test_single_word():
    result = alienOrder(["abc"])
    assert set(result) == {"a","b","c"}

def test_single_char_words():
    assert alienOrder(["z","z"]) == "z"

"""Tests for 025 Evaluate Reverse Polish Notation (LC#150)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("025_evaluate_reverse_polish_notation").Solution

def test_basic():
    assert Sol().evalRPN(["2","1","+","3","*"]) == 9

def test_division():
    assert Sol().evalRPN(["10","6","9","3","+","-11","*","/","*","17","+","5","+"]) == 22

def test_negative_division():
    assert Sol().evalRPN(["4","13","5","/","+"]) == 6

def test_single():
    assert Sol().evalRPN(["18"]) == 18

def test_tle():
    # build a long expression: 1 + 1 + 1 + ... (5000 additions)
    tokens = ["1"] * 5001 + ["+"] * 5000
    t0 = time.time()
    assert Sol().evalRPN(tokens) == 5001
    assert time.time() - t0 < 1, "TLE"

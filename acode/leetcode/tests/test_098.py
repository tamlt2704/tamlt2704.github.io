import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module

mod = import_module('098_reverse_integer')
reverse = mod.reverse

def test_positive():
    assert reverse(123) == 321

def test_negative():
    assert reverse(-123) == -321

def test_trailing_zero():
    assert reverse(120) == 21

def test_zero():
    assert reverse(0) == 0

def test_overflow_positive():
    assert reverse(2**31) == 0

def test_overflow_edge():
    assert reverse(1534236469) == 0

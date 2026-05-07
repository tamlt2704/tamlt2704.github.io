import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module

mod = import_module('097_sum_of_two_integers')
getSum = mod.getSum

def test_positive():
    assert getSum(1, 2) == 3

def test_negative_positive():
    assert getSum(-1, 1) == 0

def test_both_negative():
    assert getSum(-2, -3) == -5

def test_zeros():
    assert getSum(0, 0) == 0

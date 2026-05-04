import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module

mod = import_module('099_pow_x_n')
myPow = mod.myPow

def test_basic():
    assert myPow(2.0, 10) == 1024.0

def test_decimal():
    assert abs(myPow(2.1, 3) - 9.261) < 1e-3

def test_negative_exponent():
    assert myPow(2.0, -2) == 0.25

def test_large_exponent_one():
    assert myPow(1.0, 2**31 - 1) == 1.0

def test_tle():
    start = time.time()
    result = myPow(1.00001, 2**31 - 1)
    assert result > 0
    assert time.time() - start < 2, "TLE: exceeded 2 seconds"

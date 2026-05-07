import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module

mod = import_module('096_counting_bits')
countBits = mod.countBits

def test_two():
    assert countBits(2) == [0, 1, 1]

def test_five():
    assert countBits(5) == [0, 1, 1, 2, 1, 2]

def test_zero():
    assert countBits(0) == [0]

def test_tle():
    start = time.time()
    result = countBits(10**5)
    assert len(result) == 10**5 + 1
    assert time.time() - start < 2, "TLE: exceeded 2 seconds"

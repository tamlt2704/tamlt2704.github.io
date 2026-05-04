import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module

mod = import_module('091_koko_eating_bananas')
minEatingSpeed = mod.minEatingSpeed

def test_example1():
    assert minEatingSpeed([3,6,7,11], 8) == 4

def test_example2():
    assert minEatingSpeed([30,11,23,4,20], 5) == 30

def test_example3():
    assert minEatingSpeed([30,11,23,4,20], 6) == 23

def test_tle():
    piles = [10**9] * (10**4)
    start = time.time()
    result = minEatingSpeed(piles, 10**4)
    assert time.time() - start < 2
    assert result == 10**9

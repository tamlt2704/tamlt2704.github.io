import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module

mod = import_module('095_number_of_1_bits')
hammingWeight = mod.hammingWeight

def test_eleven():
    assert hammingWeight(11) == 3

def test_power_of_two():
    assert hammingWeight(128) == 1

def test_all_ones():
    assert hammingWeight(2**31 - 1) == 31

def test_one():
    assert hammingWeight(1) == 1

def test_tle():
    start = time.time()
    for _ in range(10**5):
        hammingWeight(2**31 - 1)
    assert time.time() - start < 2, "TLE: exceeded 2 seconds"

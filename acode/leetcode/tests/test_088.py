import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module

mod = import_module('088_binary_search')
search = mod.search

def test_found():
    assert search([-1,0,3,5,9,12], 9) == 4

def test_not_found():
    assert search([-1,0,3,5,9,12], 2) == -1

def test_single_found():
    assert search([5], 5) == 0

def test_single_not_found():
    assert search([1], 2) == -1

def test_tle():
    nums = list(range(10**4))
    start = time.time()
    assert search(nums, 9999) == 9999
    assert time.time() - start < 1

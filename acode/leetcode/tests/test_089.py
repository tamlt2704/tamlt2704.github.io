import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module

mod = import_module('089_search_in_rotated_sorted_array')
search = mod.search

def test_found():
    assert search([4,5,6,7,0,1,2], 0) == 4

def test_not_found():
    assert search([4,5,6,7,0,1,2], 3) == -1

def test_single_not_found():
    assert search([1], 0) == -1

def test_single_found():
    assert search([1], 1) == 0

def test_tle():
    nums = list(range(2500, 5000)) + list(range(0, 2500))
    start = time.time()
    assert search(nums, 0) == 2500
    assert time.time() - start < 1

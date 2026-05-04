"""Tests for 003 Best Time to Buy and Sell Stock (LC#121)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("003_best_time_to_buy_and_sell_stock").Solution

def test_basic():
    assert Sol().maxProfit([7, 1, 5, 3, 6, 4]) == 5

def test_no_profit():
    assert Sol().maxProfit([7, 6, 4, 3, 1]) == 0

def test_single():
    assert Sol().maxProfit([5]) == 0

def test_two_elements():
    assert Sol().maxProfit([1, 2]) == 1

def test_all_same():
    assert Sol().maxProfit([3, 3, 3]) == 0

def test_tle():
    prices = list(range(10**5, 0, -1)) + [10**5 + 1]
    t0 = time.time()
    assert Sol().maxProfit(prices) == 10**5
    assert time.time() - t0 < 1, "TLE"

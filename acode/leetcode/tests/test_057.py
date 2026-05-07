"""Tests for 057 Cheapest Flights Within K Stops (LC#787)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
findCheapestPrice = import_module("057_cheapest_flights_within_k_stops").findCheapestPrice

def test_basic():
    assert findCheapestPrice(4, [[0,1,100],[1,2,100],[2,0,100],[1,3,600],[2,3,200]], 0, 3, 1) == 700

def test_no_route():
    assert findCheapestPrice(3, [[0,1,100],[1,2,100]], 0, 2, 0) == -1

def test_direct_flight():
    assert findCheapestPrice(2, [[0,1,500]], 0, 1, 0) == 500

def test_tle():
    n = 100
    flights = []
    for i in range(n):
        for j in range(n):
            if i != j:
                flights.append([i, j, (i+j) % 1000 + 1])
    t0 = time.time()
    findCheapestPrice(n, flights, 0, n-1, n-2)
    assert time.time() - t0 < 2, "TLE"

"""Tests for 103 Reconstruct Itinerary (LC#332)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Sol = import_module("103_reconstruct_itinerary").Solution

def test_basic():
    tickets = [["MUC","LHR"],["JFK","MUC"],["SFO","SJC"],["LHR","SFO"]]
    assert Sol().findItinerary(tickets) == ["JFK","MUC","LHR","SFO","SJC"]

def test_lexical_order():
    tickets = [["JFK","SFO"],["JFK","ATL"],["SFO","ATL"],["ATL","JFK"],["ATL","SFO"]]
    assert Sol().findItinerary(tickets) == ["JFK","ATL","JFK","SFO","ATL","SFO"]

def test_single_ticket():
    assert Sol().findItinerary([["JFK","AAA"]]) == ["JFK","AAA"]

def test_tle():
    import random, string
    random.seed(42)
    codes = ["JFK"] + ["".join(random.choices(string.ascii_uppercase, k=3)) for _ in range(30)]
    tickets = []
    for _ in range(300):
        a, b = random.sample(codes, 2)
        tickets.append([a, b])
    # Ensure starts from JFK
    tickets.append(["JFK", codes[1]])
    t0 = time.time()
    try:
        Sol().findItinerary(tickets)
    except Exception:
        pass
    assert time.time() - t0 < 2, "TLE"

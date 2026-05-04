import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module

mod = import_module('083_gas_station')
sol = mod.Solution()

def test_basic():
    assert sol.canCompleteCircuit([1,2,3,4,5], [3,4,5,1,2]) == 3

def test_impossible():
    assert sol.canCompleteCircuit([2,3,4], [3,4,3]) == -1

def test_single():
    assert sol.canCompleteCircuit([5], [4]) == 0

def test_tle():
    n = 10**5
    gas = [i % 10 + 1 for i in range(n)]
    cost = [1] * n
    start = time.time()
    sol.canCompleteCircuit(gas, cost)
    assert time.time() - start < 1.0

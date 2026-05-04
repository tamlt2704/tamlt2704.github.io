import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module

mod = import_module('081_jump_game')
sol = mod.Solution()

def test_reachable():
    assert sol.canJump([2,3,1,1,4]) == True

def test_not_reachable():
    assert sol.canJump([3,2,1,0,4]) == False

def test_single_zero():
    assert sol.canJump([0]) == True

def test_two_elements():
    assert sol.canJump([2,0]) == True

def test_tle():
    nums = [1] * 10**4
    start = time.time()
    sol.canJump(nums)
    assert time.time() - start < 1.0

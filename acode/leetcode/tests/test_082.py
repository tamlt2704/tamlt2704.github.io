import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module

mod = import_module('082_jump_game_ii')
sol = mod.Solution()

def test_basic():
    assert sol.jump([2,3,1,1,4]) == 2

def test_basic2():
    assert sol.jump([2,3,0,1,4]) == 2

def test_single():
    assert sol.jump([1]) == 0

def test_tle():
    nums = [1] * 10**4
    start = time.time()
    sol.jump(nums)
    assert time.time() - start < 1.0

import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module

mod = import_module('086_partition_labels')
sol = mod.Solution()

def test_basic():
    assert sol.partitionLabels("ababcbacadefegdehijhklij") == [9,7,8]

def test_single_partition():
    assert sol.partitionLabels("eccbbbbdec") == [10]

def test_single_char():
    assert sol.partitionLabels("a") == [1]

def test_tle():
    import string
    s = (string.ascii_lowercase * 20)[:500]
    start = time.time()
    sol.partitionLabels(s)
    assert time.time() - start < 1.0

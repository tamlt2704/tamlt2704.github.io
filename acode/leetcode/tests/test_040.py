"""Tests for 040 Serialize and Deserialize Binary Tree (LC#297)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from helpers import build_tree, tree_to_list
from importlib import import_module
Codec = import_module("040_serialize_and_deserialize_binary_tree").Codec

def test_roundtrip():
    c = Codec()
    root = build_tree([1, 2, 3, None, None, 4, 5])
    assert tree_to_list(c.deserialize(c.serialize(root))) == [1, 2, 3, None, None, 4, 5]

def test_empty():
    c = Codec()
    assert c.deserialize(c.serialize(None)) is None

def test_single():
    c = Codec()
    assert tree_to_list(c.deserialize(c.serialize(build_tree([1])))) == [1]

def test_tle():
    c = Codec()
    root = build_tree(list(range(1, 10001)))
    t0 = time.time()
    tree_to_list(c.deserialize(c.serialize(root)))
    assert time.time() - t0 < 2, "TLE"

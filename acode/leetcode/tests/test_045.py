"""Tests for 045 Clone Graph (LC#133)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
from helpers import build_graph, graph_to_adj, Node
cloneGraph = import_module("045_clone_graph").cloneGraph

def test_basic():
    adj = [[2,4],[1,3],[2,4],[1,3]]
    node = build_graph(adj)
    clone = cloneGraph(node)
    assert clone is not node
    assert graph_to_adj(clone, 4) == [[2,4],[1,3],[2,4],[1,3]]

def test_single_node():
    node = Node(1)
    clone = cloneGraph(node)
    assert clone is not node
    assert clone.val == 1
    assert clone.neighbors == []

def test_empty():
    assert cloneGraph(None) is None

def test_tle():
    n = 100
    nodes = [Node(i+1) for i in range(n)]
    for i in range(n):
        nodes[i].neighbors = [nodes[j] for j in range(n) if j != i]
    t0 = time.time()
    clone = cloneGraph(nodes[0])
    assert time.time() - t0 < 2, "TLE"
    assert graph_to_adj(clone, n) == [sorted(j+1 for j in range(n) if j != i) for i in range(n)]

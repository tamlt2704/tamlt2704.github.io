# 133. Clone Graph
# Difficulty: Medium | Topic: Graph Traversal (BFS/DFS)
#
# Given a reference of a node in a connected undirected graph, return a
# deep copy (clone) of the graph. Each node contains a val and a list
# of its neighbors.
#
# Example: adjList = [[2,4],[1,3],[2,4],[1,3]] -> same structure cloned
# Constraints: 1 <= number of nodes <= 100

from typing import Optional


class Node:
    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []


class Solution:
    def cloneGraph(self, node: Optional[Node]) -> Optional[Node]:
        pass

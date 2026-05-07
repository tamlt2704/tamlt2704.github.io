# 1192. Critical Connections in a Network
# Difficulty: Hard | Topic: Advanced Graph (Tarjan's)
#
# Given n servers and connections between them, find all critical
# connections. A critical connection is an edge whose removal disconnects
# some servers.
#
# Example: n = 4, connections = [[0,1],[1,2],[2,0],[1,3]] -> [[1,3]]
# Constraints: 2 <= n <= 10^5, n-1 <= connections.length <= 10^5

from collections import defaultdict


class Solution:
    def criticalConnections(self, n: int, connections: list[list[int]]) -> list[list[int]]:
        pass

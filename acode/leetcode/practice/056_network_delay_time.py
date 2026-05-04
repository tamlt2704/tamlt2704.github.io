# 743. Network Delay Time
# Difficulty: Medium | Topic: Shortest Path
#
# Given a network of n nodes and weighted directed edges times[i] =
# (ui, vi, wi), send a signal from node k. Return the minimum time for
# all n nodes to receive the signal, or -1 if impossible.
#
# Example: times = [[2,1,1],[2,3,1],[3,4,1]], n = 4, k = 2 -> 2
# Constraints: 1 <= n <= 100, 1 <= times.length <= 6000

import heapq
from collections import defaultdict


class Solution:
    def networkDelayTime(self, times: list[list[int]], n: int, k: int) -> int:
        pass

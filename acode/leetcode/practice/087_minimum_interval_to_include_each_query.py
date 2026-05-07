# 1851. Minimum Interval to Include Each Query
# Difficulty: Hard | Topic: Intervals
#
# Given a 2D array intervals where intervals[i] = [lefti, righti] and
# an array queries, for each query return the size of the smallest
# interval that contains it, or -1 if no interval contains it.
#
# Example: intervals = [[1,4],[2,4],[3,6],[4,4]], queries = [2,3,4,5]
#       -> [3,3,1,4]
# Constraints: 1 <= intervals.length, queries.length <= 10^5

import heapq


class Solution:
    def minInterval(self, intervals: list[list[int]], queries: list[int]) -> list[int]:
        pass

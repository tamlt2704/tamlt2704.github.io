# 778. Swim in Rising Water
# Difficulty: Hard | Topic: Shortest Path
#
# Given an n x n integer matrix grid where grid[i][j] represents the
# elevation at (i,j). At time t, the water depth everywhere is t. You
# can swim to adjacent cells if both cells have elevation <= t. Return
# the minimum time to reach from (0,0) to (n-1,n-1).
#
# Example: grid = [[0,2],[1,3]] -> 3
# Constraints: 1 <= n <= 50, 0 <= grid[i][j] < n^2, all values distinct

import heapq


class Solution:
    def swimInWater(self, grid: list[list[int]]) -> int:
        pass

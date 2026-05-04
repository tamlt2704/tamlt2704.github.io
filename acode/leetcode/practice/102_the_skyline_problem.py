# 218. The Skyline Problem
# Difficulty: Hard | Topic: Segment Trees / Sweep Line
#
# Given the locations and heights of buildings, return the skyline formed
# by these buildings collectively. A building is represented as
# [left, right, height]. The skyline is a list of key points [x, height]
# sorted by x-coordinate.
#
# Example: buildings = [[2,9,10],[3,7,15],[5,12,12],[15,20,10],[19,24,8]]
#       -> [[2,10],[3,15],[7,12],[12,0],[15,10],[20,8],[24,0]]
# Constraints: 1 <= buildings.length <= 10^4

import heapq


class Solution:
    def getSkyline(self, buildings: list[list[int]]) -> list[list[int]]:
        pass

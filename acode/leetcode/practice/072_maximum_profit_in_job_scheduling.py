# 1235. Maximum Profit in Job Scheduling
# Difficulty: Hard | Topic: DP on Sequences
#
# Given n jobs with startTime, endTime, and profit arrays, find the
# maximum profit such that no two selected jobs overlap. A job that
# ends at time X can start another job that begins at time X.
#
# Example: startTime=[1,2,3,3], endTime=[3,4,5,6], profit=[50,10,40,70] -> 120
# Constraints: 1 <= n <= 5 * 10^4

import bisect


class Solution:
    def jobScheduling(self, startTime: list[int], endTime: list[int], profit: list[int]) -> int:
        pass

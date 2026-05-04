# 312. Burst Balloons
# Difficulty: Hard | Topic: 2-D DP (Interval)
#
# Given n balloons with nums[i] painted on them. Burst all balloons to
# collect maximum coins. When you burst balloon i, you get
# nums[i-1] * nums[i] * nums[i+1] coins. After bursting, i-1 and i+1
# become adjacent. Assume nums[-1] = nums[n] = 1.
#
# Example: nums = [3,1,5,8] -> 167
# Constraints: 1 <= n <= 300, 0 <= nums[i] <= 100


class Solution:
    def maxCoins(self, nums: list[int]) -> int:
        pass

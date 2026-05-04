# 124. Binary Tree Maximum Path Sum
# Difficulty: Hard | Topic: Binary Trees
#
# A path in a binary tree is a sequence of nodes where each pair of
# adjacent nodes has an edge. The path sum is the sum of the node values.
# Given the root, return the maximum path sum of any non-empty path.
#
# Example: root = [-10,9,20,null,null,15,7] -> 42 (15+20+7)
# Constraints: 1 <= number of nodes <= 3 * 10^4

from typing import Optional


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def maxPathSum(self, root: Optional[TreeNode]) -> int:
        pass

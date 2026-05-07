# 100. Same Tree
# Difficulty: Easy | Topic: Binary Trees
#
# Given the roots of two binary trees p and q, check if they are the
# same or not. Two binary trees are the same if they are structurally
# identical and the nodes have the same value.
#
# Example: p = [1,2,3], q = [1,2,3] -> true
# Constraints: 0 <= number of nodes <= 100

from typing import Optional


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def isSameTree(self, p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
        pass

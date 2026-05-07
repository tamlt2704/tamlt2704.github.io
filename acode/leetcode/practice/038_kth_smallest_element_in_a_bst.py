# 230. Kth Smallest Element in a BST
# Difficulty: Medium | Topic: Binary Trees
#
# Given the root of a binary search tree and an integer k, return the
# kth smallest value (1-indexed) of all the values in the BST.
#
# Example: root = [3,1,4,null,2], k = 1 -> 1
# Constraints: 1 <= k <= n <= 10^4

from typing import Optional


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def kthSmallest(self, root: Optional[TreeNode], k: int) -> int:
        pass

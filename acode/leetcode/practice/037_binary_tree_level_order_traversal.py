# 102. Binary Tree Level Order Traversal
# Difficulty: Medium | Topic: Binary Trees
#
# Given the root of a binary tree, return the level order traversal of
# its nodes' values (i.e., from left to right, level by level).
#
# Example: root = [3,9,20,null,null,15,7] -> [[3],[9,20],[15,7]]
# Constraints: 0 <= number of nodes <= 2000

from typing import Optional
from collections import deque


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def levelOrder(self, root: Optional[TreeNode]) -> list[list[int]]:
        pass

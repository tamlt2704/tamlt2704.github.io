# 226. Invert Binary Tree
# Difficulty: Easy | Topic: Binary Trees
#
# Given the root of a binary tree, invert the tree, and return its root.
#
# Example: root = [4,2,7,1,3,6,9] -> [4,7,2,9,6,3,1]
# Constraints: 0 <= number of nodes <= 100

from typing import Optional


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def invertTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        pass

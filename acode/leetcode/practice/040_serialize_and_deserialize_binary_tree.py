# 297. Serialize and Deserialize Binary Tree
# Difficulty: Hard | Topic: Binary Trees
#
# Design an algorithm to serialize and deserialize a binary tree.
# Serialization is converting a tree to a string. Deserialization is
# reconstructing the tree from the string.
#
# Example: root = [1,2,3,null,null,4,5] -> "1,2,3,null,null,4,5"
# Constraints: 0 <= number of nodes <= 10^4

from typing import Optional


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Codec:
    def serialize(self, root: Optional[TreeNode]) -> str:
        pass

    def deserialize(self, data: str) -> Optional[TreeNode]:
        pass

# 143. Reorder List
# Difficulty: Medium | Topic: Linked Lists
#
# Given head of a singly linked list L0 -> L1 -> ... -> Ln-1 -> Ln,
# reorder it to: L0 -> Ln -> L1 -> Ln-1 -> L2 -> Ln-2 -> ...
# You may not modify the values, only the nodes themselves.
#
# Example: head = [1,2,3,4] -> [1,4,2,3]
# Constraints: 1 <= list length <= 5 * 10^4

from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def reorderList(self, head: Optional[ListNode]) -> None:
        pass

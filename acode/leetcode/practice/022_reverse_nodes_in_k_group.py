# 25. Reverse Nodes in K-Group
# Difficulty: Hard | Topic: Linked Lists
#
# Given the head of a linked list, reverse the nodes of the list k at a
# time, and return the modified list. If the number of nodes is not a
# multiple of k then left-out nodes at the end should remain as is.
#
# Example: head = [1,2,3,4,5], k = 2 -> [2,1,4,3,5]
# Constraints: 1 <= k <= n <= 5000

from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def reverseKGroup(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:
        pass

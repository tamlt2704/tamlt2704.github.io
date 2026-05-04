# 141. Linked List Cycle
# Difficulty: Easy | Topic: Linked Lists
#
# Given head, determine if the linked list has a cycle in it.
# A cycle exists if some node can be reached again by continuously
# following the next pointer.
#
# Example: head = [3,2,0,-4], pos = 1 -> true
# Constraints: 0 <= number of nodes <= 10^4

from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def hasCycle(self, head: Optional[ListNode]) -> bool:
        pass

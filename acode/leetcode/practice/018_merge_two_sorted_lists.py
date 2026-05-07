# 21. Merge Two Sorted Lists
# Difficulty: Easy | Topic: Linked Lists
#
# Merge two sorted linked lists and return it as a sorted list.
# The list should be made by splicing together the nodes of the two lists.
#
# Example: list1 = [1,2,4], list2 = [1,3,4] -> [1,1,2,3,4,4]
# Constraints: 0 <= list length <= 50

from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def mergeTwoLists(self, list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
        pass

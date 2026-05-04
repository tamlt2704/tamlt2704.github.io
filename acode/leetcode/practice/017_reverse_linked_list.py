# 206. Reverse Linked List
# Difficulty: Easy | Topic: Linked Lists
#
# Given the head of a singly linked list, reverse the list, and return
# the reversed list.
#
# Example: head = [1,2,3,4,5] -> [5,4,3,2,1]
# Constraints: 0 <= number of nodes <= 5000

from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        pass

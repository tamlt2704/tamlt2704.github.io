# 23. Merge K Sorted Lists
# Difficulty: Hard | Topic: Linked Lists
#
# You are given an array of k linked-lists, each sorted in ascending order.
# Merge all the linked-lists into one sorted linked-list and return it.
#
# Example: lists = [[1,4,5],[1,3,4],[2,6]] -> [1,1,2,3,4,4,5,6]
# Constraints: 0 <= k <= 10^4, 0 <= lists[i].length <= 500

from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def mergeKLists(self, lists: list[Optional[ListNode]]) -> Optional[ListNode]:
        pass

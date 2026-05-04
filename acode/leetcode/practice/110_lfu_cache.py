# 460. LFU Cache
# Difficulty: Hard | Topic: Design
#
# Design a data structure for a Least Frequently Used (LFU) cache.
# Implement get and put in O(1) time. When capacity is reached, evict
# the least frequently used key. If there is a tie, evict the least
# recently used key among them.
#
# Example: LFUCache(2) -> put(1,1) -> put(2,2) -> get(1)=1 -> put(3,3) -> get(2)=-1
# Constraints: 1 <= capacity <= 10^4, 0 <= key,value <= 10^5

from collections import defaultdict, OrderedDict


class LFUCache:
    def __init__(self, capacity: int):
        pass

    def get(self, key: int) -> int:
        pass

    def put(self, key: int, value: int) -> None:
        pass

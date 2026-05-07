# 355. Design Twitter
# Difficulty: Medium | Topic: Heaps / Priority Queues
#
# Design a simplified version of Twitter where users can post tweets,
# follow/unfollow another user, and see the 10 most recent tweets in
# their news feed.
#
# Constraints: 1 <= userId, followerId, followeeId <= 500, at most 3 * 10^4 calls

import heapq
from collections import defaultdict


class Twitter:
    def __init__(self):
        pass

    def postTweet(self, userId: int, tweetId: int) -> None:
        pass

    def getNewsFeed(self, userId: int) -> list[int]:
        pass

    def follow(self, followerId: int, followeeId: int) -> None:
        pass

    def unfollow(self, followerId: int, followeeId: int) -> None:
        pass

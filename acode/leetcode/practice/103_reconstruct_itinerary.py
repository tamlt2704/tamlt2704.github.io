# 332. Reconstruct Itinerary
# Difficulty: Hard | Topic: Advanced Graph
#
# Given a list of airline tickets [from, to], reconstruct the itinerary
# starting from "JFK". If multiple valid itineraries, return the one with
# the smallest lexical order. All tickets must be used exactly once.
#
# Example: tickets = [["MUC","LHR"],["JFK","MUC"],["SFO","SJC"],["LHR","SFO"]]
#       -> ["JFK","MUC","LHR","SFO","SJC"]
# Constraints: 1 <= tickets.length <= 300

from collections import defaultdict


class Solution:
    def findItinerary(self, tickets: list[list[str]]) -> list[str]:
        pass

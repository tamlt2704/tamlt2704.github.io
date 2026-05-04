"""Tests for 033 Design Twitter (LC#355)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
Twitter = import_module("033_design_twitter").Twitter

def test_basic():
    t = Twitter()
    t.postTweet(1, 5)
    assert t.getNewsFeed(1) == [5]
    t.follow(1, 2)
    t.postTweet(2, 6)
    assert t.getNewsFeed(1) == [6, 5]
    t.unfollow(1, 2)
    assert t.getNewsFeed(1) == [5]

def test_empty_feed():
    t = Twitter()
    assert t.getNewsFeed(1) == []

def test_max_10():
    t = Twitter()
    for i in range(15):
        t.postTweet(1, i)
    assert len(t.getNewsFeed(1)) == 10

def test_tle():
    t = Twitter()
    t0 = time.time()
    for i in range(500):
        t.postTweet(i % 50, i)
    for i in range(50):
        t.follow(0, i)
    for _ in range(1000):
        t.getNewsFeed(0)
    assert time.time() - t0 < 2, "TLE"

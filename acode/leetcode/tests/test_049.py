"""Tests for 049 Word Ladder (LC#127)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
ladderLength = import_module("049_word_ladder").ladderLength

def test_basic():
    assert ladderLength("hit", "cog", ["hot","dot","dog","lot","log","cog"]) == 5

def test_no_path():
    assert ladderLength("hit", "cog", ["hot","dot","dog","lot","log"]) == 0

def test_tle():
    import string
    words = []
    base = "aaaa"
    for i in range(26):
        for j in range(26):
            w = chr(ord('a')+i) + chr(ord('a')+j) + "aa"
            if w not in words:
                words.append(w)
            if len(words) >= 5000:
                break
        if len(words) >= 5000:
            break
    t0 = time.time()
    ladderLength("aaaa", "zzaa", words)
    assert time.time() - t0 < 2, "TLE"

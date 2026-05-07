"""Tests for 055 Accounts Merge (LC#721)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
accountsMerge = import_module("055_accounts_merge").accountsMerge

def test_basic():
    accounts = [["John","j1@x.com","j2@x.com"],["John","j3@x.com"],["John","j1@x.com","j3@x.com"],["Mary","m@x.com"]]
    result = sorted([sorted(a) for a in accountsMerge(accounts)])
    expected = sorted([sorted(["John","j1@x.com","j2@x.com","j3@x.com"]),sorted(["Mary","m@x.com"])])
    assert result == expected

def test_no_merge():
    accounts = [["A","a@x.com"],["B","b@x.com"]]
    result = sorted([sorted(a) for a in accountsMerge(accounts)])
    assert result == sorted([sorted(["A","a@x.com"]),sorted(["B","b@x.com"])])

def test_tle():
    accounts = [["User"+str(i), "e"+str(i)+"@x.com", "e"+str(i+1)+"@x.com"] for i in range(1000)]
    t0 = time.time()
    accountsMerge(accounts)
    assert time.time() - t0 < 2, "TLE"

"""Tests for 112 Design In-Memory File System (LC#588)"""
import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'practice'))
from importlib import import_module
FileSystem = import_module("112_design_in_memory_file_system").FileSystem

def test_basic():
    fs = FileSystem()
    assert fs.ls("/") == []
    fs.mkdir("/a/b/c")
    fs.addContentToFile("/a/b/c/d", "hello")
    assert fs.ls("/") == ["a"]
    assert fs.readContentFromFile("/a/b/c/d") == "hello"

def test_ls_file():
    fs = FileSystem()
    fs.addContentToFile("/a", "content")
    assert fs.ls("/a") == ["a"]

def test_nested_dirs():
    fs = FileSystem()
    fs.mkdir("/x/y/z")
    fs.mkdir("/x/a")
    assert sorted(fs.ls("/x")) == ["a", "y"]

def test_append_content():
    fs = FileSystem()
    fs.addContentToFile("/file", "hello")
    fs.addContentToFile("/file", " world")
    assert fs.readContentFromFile("/file") == "hello world"

def test_tle():
    fs = FileSystem()
    t0 = time.time()
    for i in range(10**4):
        path = f"/dir{i % 100}/sub{i % 50}/file{i}"
        fs.mkdir(f"/dir{i % 100}/sub{i % 50}")
        fs.addContentToFile(path, f"data{i}")
    for i in range(0, 10**4, 2):
        path = f"/dir{i % 100}/sub{i % 50}/file{i}"
        fs.readContentFromFile(path)
    assert time.time() - t0 < 2, "TLE"

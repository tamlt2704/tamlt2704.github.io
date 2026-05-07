# LeetCode Practice

A curated collection of 112 LeetCode problems with Python solution stubs and test cases, organized for structured interview preparation.

## Structure

```
leetcode/
├── practice/       # Solution stubs with problem descriptions
│   ├── 001_two_sum.py
│   ├── ...
│   └── 112_design_in_memory_file_system.py
└── tests/          # Test cases for each problem
    ├── helpers.py  # Shared utilities (ListNode, TreeNode, builders)
    └── test_001.py ... test_112.py
```

Each practice file contains the LeetCode problem number, difficulty, topic, description, examples, and constraints as comments, followed by a `Solution` class stub to implement.

## Topics Covered

| Category | Examples |
|---|---|
| Arrays & Strings | Two Sum, 3Sum, Product of Array Except Self |
| Sliding Window | Longest Substring Without Repeating, Minimum Window Substring |
| Stacks & Queues | Valid Parentheses, Min Stack, Daily Temperatures |
| Linked Lists | Reverse Linked List, Merge K Sorted Lists |
| Binary Trees | Invert Binary Tree, Max Depth, Level Order Traversal |
| Heaps / Priority Queues | Top K Frequent Elements, Find Median from Data Stream |
| Tries | Implement Trie, Word Search II |
| Graph Traversal (BFS/DFS) | Number of Islands, Clone Graph, Course Schedule |
| Dynamic Programming | Coin Change, Longest Increasing Subsequence, Word Break |
| Greedy | Jump Game, Gas Station, Merge Intervals |
| Binary Search | Binary Search, Koko Eating Bananas, Median of Two Sorted Arrays |
| Bit Manipulation | Single Number, Number of 1 Bits, Counting Bits |
| Segment Trees / BIT | Range Sum Query Mutable, Count of Smaller Numbers After Self |
| Design | LRU Cache, LFU Cache, Design Twitter |

## Running Tests

```bash
# All tests
pytest tests/

# Single problem
pytest tests/test_001.py -v
```

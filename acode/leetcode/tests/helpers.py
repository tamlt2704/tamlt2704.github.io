"""Shared helpers for test files."""
import sys
from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Node:
    """Graph node for Clone Graph."""
    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []


def build_list(vals: list) -> Optional[ListNode]:
    dummy = ListNode()
    cur = dummy
    for v in vals:
        cur.next = ListNode(v)
        cur = cur.next
    return dummy.next


def list_to_arr(head: Optional[ListNode]) -> list:
    arr = []
    while head:
        arr.append(head.val)
        head = head.next
    return arr


def build_list_cycle(vals: list, pos: int) -> Optional[ListNode]:
    nodes = [ListNode(v) for v in vals]
    for i in range(len(nodes) - 1):
        nodes[i].next = nodes[i + 1]
    if pos >= 0:
        nodes[-1].next = nodes[pos]
    return nodes[0] if nodes else None


def build_tree(vals: list) -> Optional[TreeNode]:
    """Build tree from level-order list (None = null)."""
    if not vals or vals[0] is None:
        return None
    root = TreeNode(vals[0])
    queue = [root]
    i = 1
    while i < len(vals):
        node = queue.pop(0)
        if i < len(vals) and vals[i] is not None:
            node.left = TreeNode(vals[i])
            queue.append(node.left)
        i += 1
        if i < len(vals) and vals[i] is not None:
            node.right = TreeNode(vals[i])
            queue.append(node.right)
        i += 1
    return root


def tree_to_list(root: Optional[TreeNode]) -> list:
    if not root:
        return []
    result, queue = [], [root]
    while queue:
        node = queue.pop(0)
        if node:
            result.append(node.val)
            queue.append(node.left)
            queue.append(node.right)
        else:
            result.append(None)
    while result and result[-1] is None:
        result.pop()
    return result


def build_graph(adj_list: list[list[int]]) -> Optional[Node]:
    """Build graph from adjacency list (1-indexed)."""
    if not adj_list:
        return None
    nodes = [Node(i + 1) for i in range(len(adj_list))]
    for i, neighbors in enumerate(adj_list):
        nodes[i].neighbors = [nodes[n - 1] for n in neighbors]
    return nodes[0]


def graph_to_adj(node: Optional[Node], n: int) -> list[list[int]]:
    if not node:
        return []
    visited = {}
    queue = [node]
    visited[node.val] = node
    while queue:
        cur = queue.pop(0)
        for nb in cur.neighbors:
            if nb.val not in visited:
                visited[nb.val] = nb
                queue.append(nb)
    return [sorted(nb.val for nb in visited[i].neighbors) for i in range(1, n + 1)]

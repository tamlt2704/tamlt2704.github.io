# Chapter 3: Linked Lists

[← HashMaps](./chapter-02-hashmaps.md) | [next →](./chapter-04-stacks-queues.md)

---

## Patterns

### Reversal

```python
def reverse(head):
    prev = None
    while head:
        nxt = head.next
        head.next = prev
        prev = head
        head = nxt
    return prev
```

### Fast/Slow Pointers (Floyd's)

```python
def find_middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow  # middle node
```

### Dummy Node

```python
def merge_pattern(list1, list2):
    dummy = ListNode(0)
    curr = dummy
    # build result by appending to curr
    return dummy.next
```

---

## Problem 1: Reverse Linked List (Easy) — LC 206

```python
def reverseList(head):
    prev = None
    while head:
        nxt = head.next
        head.next = prev
        prev = head
        head = nxt
    return prev
```

**Complexity:** O(n) time, O(1) space.

---

## Problem 2: Linked List Cycle (Easy) — LC 141

```python
def hasCycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False
```

**Complexity:** O(n) time, O(1) space.

---

## Problem 3: Merge Two Sorted Lists (Easy) — LC 21

```python
def mergeTwoLists(l1, l2):
    dummy = curr = ListNode(0)
    while l1 and l2:
        if l1.val <= l2.val:
            curr.next = l1
            l1 = l1.next
        else:
            curr.next = l2
            l2 = l2.next
        curr = curr.next
    curr.next = l1 or l2
    return dummy.next
```

**Complexity:** O(n + m) time, O(1) space.

---

## Problem 4: Reorder List (Medium) — LC 143

**Given:** L0→L1→...→Ln, reorder to L0→Ln→L1→Ln-1→...

**Strategy:** Find middle → reverse second half → merge alternating.

```python
def reorderList(head):
    # Find middle
    slow = fast = head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next

    # Reverse second half
    prev, curr = None, slow.next
    slow.next = None
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt

    # Merge alternating
    first, second = head, prev
    while second:
        tmp1, tmp2 = first.next, second.next
        first.next = second
        second.next = tmp1
        first, second = tmp1, tmp2
```

**Complexity:** O(n) time, O(1) space.

---

## Problem 5: Reverse Nodes in k-Group (Hard) — LC 25

```python
def reverseKGroup(head, k):
    # Check if k nodes available
    node = head
    for _ in range(k):
        if not node:
            return head
        node = node.next

    # Reverse k nodes
    prev, curr = None, head
    for _ in range(k):
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt

    # Recurse for remaining
    head.next = reverseKGroup(curr, k)
    return prev
```

**Complexity:** O(n) time, O(n/k) space (recursion stack).

---

## Pattern Recognition Tips

| Signal                       | Pattern                       |
| ---------------------------- | ----------------------------- |
| "Reverse a list"             | Iterative prev/curr/next      |
| "Find middle / cycle"        | Fast/slow pointers            |
| "Merge lists"                | Dummy node + comparison       |
| "Reorder / palindrome check" | Find middle + reverse + merge |
| "Remove nth from end"        | Two pointers with n gap       |

---

[← HashMaps](./chapter-02-hashmaps.md) | [next →](./chapter-04-stacks-queues.md)

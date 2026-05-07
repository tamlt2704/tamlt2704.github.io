# Chapter 6: What's Most Urgent? — Heaps and Priority Queues

[← Chapter 5: Quicksort](chapter-05-quicksort.md) | [Chapter 7: Instant Lookup →](chapter-07-hash-tables.md)

---

## The Problem

Dispatch Dan doesn't need all 50,000 packages sorted. He needs to answer one question repeatedly: **"What's the most urgent delivery right now?"**

New packages arrive throughout the day. Priorities change (a hospital calls — their package is now critical). Packages get delivered and removed from the queue. The system needs to:

1. Insert a new package: fast
2. Find the most urgent package: instant
3. Remove the most urgent package (it's been dispatched): fast
4. Change a package's priority: fast

A sorted array gives you #2 in O(1) but #1 costs O(n) (shift everything). An unsorted array gives you #1 in O(1) but #2 costs O(n) (scan everything).

You need a data structure that's good at all four. That's a **heap**.

## The Heap: A Partially Sorted Tree

A **min-heap** is a binary tree where every parent is smaller than (or equal to) its children. The root is always the minimum.

```
         1
       /   \
      3     5
     / \   / \
    7   4 8   6
```

- Root (1) is the smallest — instant access
- Not fully sorted — 7 is left of 4, that's fine
- Only guarantee: parent ≤ children

### Array Representation

A heap is stored as a flat array. For element at index `i`:
- Left child: `2*i + 1`
- Right child: `2*i + 2`
- Parent: `(i - 1) // 2`

```
Array: [1, 3, 5, 7, 4, 8, 6]
Index:  0  1  2  3  4  5  6

Tree:       1(0)
          /      \
       3(1)      5(2)
      /    \    /    \
   7(3)  4(4) 8(5)  6(6)
```

No pointers. No nodes. Just an array with a clever indexing scheme.

## Building a Heap from Scratch

```python
class MinHeap:
    def __init__(self):
        self.data = []

    def _parent(self, i):
        return (i - 1) // 2

    def _left(self, i):
        return 2 * i + 1

    def _right(self, i):
        return 2 * i + 2

    def _swap(self, i, j):
        self.data[i], self.data[j] = self.data[j], self.data[i]

    def peek(self):
        """Return the minimum element. O(1)."""
        if not self.data:
            return None
        return self.data[0]

    def push(self, item):
        """Insert an element. O(log n)."""
        self.data.append(item)
        self._sift_up(len(self.data) - 1)

    def pop(self):
        """Remove and return the minimum. O(log n)."""
        if not self.data:
            return None
        if len(self.data) == 1:
            return self.data.pop()

        minimum = self.data[0]
        self.data[0] = self.data.pop()  # Move last to root
        self._sift_down(0)
        return minimum

    def _sift_up(self, i):
        """Bubble element up until heap property is restored."""
        while i > 0:
            parent = self._parent(i)
            if self.data[i] < self.data[parent]:
                self._swap(i, parent)
                i = parent
            else:
                break

    def _sift_down(self, i):
        """Push element down until heap property is restored."""
        n = len(self.data)
        while True:
            smallest = i
            left = self._left(i)
            right = self._right(i)

            if left < n and self.data[left] < self.data[smallest]:
                smallest = left
            if right < n and self.data[right] < self.data[smallest]:
                smallest = right

            if smallest != i:
                self._swap(i, smallest)
                i = smallest
            else:
                break

    def __len__(self):
        return len(self.data)
```

## Operations Traced

### Push: Insert 2 into `[1, 3, 5, 7, 4, 8, 6]`

```
Step 1: Append 2 at the end
        [1, 3, 5, 7, 4, 8, 6, 2]
                                ↑ index 7

Step 2: Sift up — compare with parent
        parent(7) = 3, data[3] = 7
        2 < 7 → swap
        [1, 3, 5, 2, 4, 8, 6, 7]
                  ↑ index 3

Step 3: Continue sifting up
        parent(3) = 1, data[1] = 3
        2 < 3 → swap
        [1, 2, 5, 3, 4, 8, 6, 7]
            ↑ index 1

Step 4: Continue
        parent(1) = 0, data[0] = 1
        2 > 1 → STOP

Final: [1, 2, 5, 3, 4, 8, 6, 7]
```

O(log n) — at most the height of the tree.

### Pop: Remove minimum from `[1, 2, 5, 3, 4, 8, 6, 7]`

```
Step 1: Save root (1), move last element (7) to root
        [7, 2, 5, 3, 4, 8, 6]
         ↑

Step 2: Sift down — compare with children
        left(0) = 1 → data[1] = 2
        right(0) = 2 → data[2] = 5
        smallest child = 2 (index 1)
        7 > 2 → swap
        [2, 7, 5, 3, 4, 8, 6]
            ↑ index 1

Step 3: Continue sifting down
        left(1) = 3 → data[3] = 3
        right(1) = 4 → data[4] = 4
        smallest child = 3 (index 3)
        7 > 3 → swap
        [2, 3, 5, 7, 4, 8, 6]
                  ↑ index 3

Step 4: No children → STOP

Final: [2, 3, 5, 7, 4, 8, 6], returned 1
```

O(log n).

## Complexity Summary

| Operation | Time |
|---|---|
| peek (find min) | O(1) |
| push (insert) | O(log n) |
| pop (extract min) | O(log n) |
| build heap from array | O(n) |
| search (find arbitrary) | O(n) |

## RouteMaster's Priority Queue

```python
class DeliveryQueue:
    """Priority queue for package dispatch. Most urgent = lowest priority number."""

    def __init__(self):
        self.heap = MinHeap()

    def add_package(self, package):
        """Add a package to the dispatch queue."""
        # Priority tuple: (deadline, priority_level, tracking)
        # Tuples compare lexicographically — deadline first, then priority
        key = (package.deadline, package.priority, package.tracking)
        self.heap.push((key, package))

    def next_delivery(self):
        """Get the most urgent package."""
        result = self.heap.pop()
        if result:
            return result[1]  # Return the package, not the key
        return None

    def peek_next(self):
        """See the most urgent without removing it."""
        result = self.heap.peek()
        if result:
            return result[1]
        return None

    def size(self):
        return len(self.heap)
```

```python
# Usage
queue = DeliveryQueue()
queue.add_package(Package("RM-001", "2024-01-15 09:00", 1, 2.5))  # Hospital, urgent
queue.add_package(Package("RM-002", "2024-01-15 18:00", 3, 1.0))  # Regular
queue.add_package(Package("RM-003", "2024-01-15 09:00", 2, 5.0))  # Morning, normal
queue.add_package(Package("RM-004", "2024-01-15 12:00", 1, 3.0))  # Noon, urgent

# Dispatch in priority order
queue.next_delivery()  # RM-001 (9AM, priority 1)
queue.next_delivery()  # RM-003 (9AM, priority 2)
queue.next_delivery()  # RM-004 (12PM, priority 1)
queue.next_delivery()  # RM-002 (6PM, priority 3)
```

## Heapsort: Sorting with a Heap

Build a heap from the data, then extract elements one by one. They come out sorted.

```python
def heapsort(items):
    """Sort using a heap. O(n log n), in-place."""
    n = len(items)

    # Build max-heap (for ascending sort, use max-heap)
    for i in range(n // 2 - 1, -1, -1):
        sift_down_max(items, n, i)

    # Extract elements one by one
    for i in range(n - 1, 0, -1):
        items[0], items[i] = items[i], items[0]  # Move max to end
        sift_down_max(items, i, 0)  # Restore heap on reduced array

    return items

def sift_down_max(items, heap_size, i):
    """Max-heap sift down."""
    while True:
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2

        if left < heap_size and items[left] > items[largest]:
            largest = left
        if right < heap_size and items[right] > items[largest]:
            largest = right

        if largest != i:
            items[i], items[largest] = items[largest], items[i]
            i = largest
        else:
            break
```

| Property | Value |
|---|---|
| Time | O(n log n) — always |
| Space | O(1) — in-place |
| Stable? | No |
| Practical speed | Slower than quicksort (poor cache locality) |

Heapsort is the fallback in introsort — guaranteed O(n log n) when quicksort degrades.

## Building a Heap in O(n)

Inserting n elements one by one: O(n log n). But building a heap from an existing array is O(n) using bottom-up construction:

```python
def heapify(items):
    """Build a min-heap from an arbitrary array. O(n)."""
    n = len(items)
    # Start from the last non-leaf node and sift down
    for i in range(n // 2 - 1, -1, -1):
        sift_down(items, n, i)
    return items
```

Why O(n) and not O(n log n)? Most nodes are near the bottom and sift down very little. The math works out to O(n) total swaps.

## Top-K: "Give Me the 10 Most Urgent"

Dispatch Dan: "I don't need all 50,000 sorted. Just the top 10 most urgent."

Sorting everything is O(n log n). Finding top-K with a heap is O(n log k):

```python
def top_k_urgent(packages, k=10):
    """Find the k most urgent packages. O(n log k)."""
    # Use a MAX-heap of size k (keep the k smallest)
    import heapq

    # Negate priorities so heapq (min-heap) acts as max-heap
    top = []
    for package in packages:
        key = (package.deadline, package.priority)
        neg_key = (-key[0], -key[1])  # Negate for max-heap behavior

        if len(top) < k:
            heapq.heappush(top, (neg_key, package))
        elif neg_key > top[0][0]:
            heapq.heapreplace(top, (neg_key, package))

    # Extract in order
    result = []
    while top:
        result.append(heapq.heappop(top)[1])
    return result[::-1]
```

For 50,000 packages, finding top 10: O(50,000 × log 10) = O(50,000 × 3.3) ≈ 165,000 operations. Much faster than sorting all 50,000.

## What You Learned

- **Heap** — partially sorted binary tree (parent ≤ children)
- **Array representation** — no pointers, just index math
- **Push/Pop** — O(log n) via sift up/down
- **Peek** — O(1) access to the minimum
- **Priority queue** — the abstract data type that heaps implement
- **Heapsort** — O(n log n) in-place, guaranteed
- **Heapify** — build a heap in O(n) bottom-up
- **Top-K** — find K best elements in O(n log k)

Dispatch Dan gets his top 10 urgent deliveries instantly. New packages slot into the priority queue in O(log n). Priority changes are handled by removing and re-inserting.

But there's another lookup problem. The customer support tool needs to find packages by tracking number, by recipient name, by address. Binary search works for one key (tracking number) but not for arbitrary lookups. You need O(1) lookup by any field.

That's hash tables. Chapter 7.

---

[← Chapter 5: Quicksort](chapter-05-quicksort.md) | [Chapter 7: Instant Lookup →](chapter-07-hash-tables.md)

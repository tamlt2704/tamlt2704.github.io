# Chapter 2: Undo History — LinkedList

[← Chapter 1: ArrayList](chapter-01-arraylist.md) | [Chapter 3: HashSet →](chapter-03-hashset.md)

---

## The Problem

ShipStream's admin panel has an undo system. Every action (edit order, change status, reassign warehouse) gets pushed onto a history stack. Users can undo the last 50 actions.

The current implementation uses ArrayList:

```java
public class UndoHistory {
    private final List<Action> history = new ArrayList<>();
    private int cursor = 0;  // Points to current position

    public void perform(Action action) {
        // Remove any "future" actions (redo history) after cursor
        while (history.size() > cursor) {
            history.remove(history.size() - 1);  // O(1) — removing from end
        }
        history.add(action);  // O(1) amortized
        cursor++;
        action.execute();
    }

    public void undo() {
        if (cursor > 0) {
            cursor--;
            history.get(cursor).reverse();
        }
    }
}
```

This works fine. But then Product adds a feature: **"Insert a checkpoint at any position in the history."** And **"Remove actions from the middle when they're invalidated."**

```java
public void insertCheckpoint(int position, Action checkpoint) {
    history.add(position, checkpoint);  // O(n) — shifts everything after position
    cursor++;
}

public void invalidate(int position) {
    history.remove(position);  // O(n) — shifts everything after position
}
```

With 10,000 actions in history and frequent mid-list operations, the admin panel lags. Every insert or remove in the middle copies thousands of elements.

## LinkedList: O(1) Insert and Remove

A LinkedList stores elements as nodes connected by pointers:

```
┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐
│ Act1 │───→│ Act2 │───→│ Act3 │───→│ Act4 │
│      │←───│      │←───│      │←───│      │
└──────┘    └──────┘    └──────┘    └──────┘
  head                                 tail
```

Each node holds: the element, a pointer to the next node, and a pointer to the previous node (doubly-linked).

### Inserting in the Middle

To insert between Act2 and Act3, just rewire two pointers:

```
Before: Act2 ──→ Act3
After:  Act2 ──→ NEW ──→ Act3
```

No shifting. No copying. O(1) once you have the position.

### Removing from the Middle

To remove Act3:

```
Before: Act2 ──→ Act3 ──→ Act4
After:  Act2 ──────────→ Act4
```

Rewire pointers. O(1).

## LinkedList in Java

```java
import java.util.LinkedList;
import java.util.List;

public class UndoHistory {
    private final LinkedList<Action> history = new LinkedList<>();
    private int cursor = 0;

    public void perform(Action action) {
        // Remove future actions
        while (history.size() > cursor) {
            history.removeLast();  // O(1)
        }
        history.addLast(action);  // O(1)
        cursor++;
        action.execute();
    }

    public void undo() {
        if (cursor > 0) {
            cursor--;
            history.get(cursor).reverse();  // O(n) — this is the catch
        }
    }

    public void insertCheckpoint(int position, Action checkpoint) {
        history.add(position, checkpoint);  // O(n) to find position, O(1) to insert
        if (position <= cursor) cursor++;
    }

    public void removeInvalidated(int position) {
        history.remove(position);  // O(n) to find position, O(1) to remove
        if (position < cursor) cursor--;
    }
}
```

Wait — `history.get(cursor)` is O(n)? And `history.add(position, ...)` is also O(n)?

## The Catch: Finding vs Inserting

LinkedList's O(1) insert/remove only applies **if you already have a reference to the node**. Finding the node by index requires traversal:

| Operation | ArrayList | LinkedList |
|---|---|---|
| `get(index)` | O(1) | O(n) |
| `add(element)` (end) | O(1) amortized | O(1) |
| `add(index, element)` | O(n) shift | O(n) traverse + O(1) insert |
| `remove(index)` | O(n) shift | O(n) traverse + O(1) remove |
| `iterator.remove()` | O(n) shift | O(1) |

The key insight: **LinkedList is fast when you use iterators**, not indexes.

## Using Iterators: The Right Way

```java
public class UndoHistory {
    private final LinkedList<Action> history = new LinkedList<>();

    public void removeAllInvalidated() {
        // Using iterator — each remove is O(1)
        var it = history.listIterator();
        while (it.hasNext()) {
            Action action = it.next();
            if (action.isInvalidated()) {
                it.remove();  // O(1) — already at the node
            }
        }
    }

    public void insertAfterLastCheckpoint(Action action) {
        // Iterate backwards to find last checkpoint
        var it = history.listIterator(history.size());
        while (it.hasPrevious()) {
            if (it.previous().isCheckpoint()) {
                it.next();  // Move back forward past the checkpoint
                it.add(action);  // O(1) insert at current position
                return;
            }
        }
        history.addFirst(action);  // No checkpoint found, add to front
    }
}
```

With iterators, LinkedList shines. Without them, it's often slower than ArrayList.

## How LinkedList Works Internally

```java
// Simplified internal structure
public class MyLinkedList<E> {
    private static class Node<E> {
        E item;
        Node<E> next;
        Node<E> prev;

        Node(Node<E> prev, E element, Node<E> next) {
            this.item = element;
            this.prev = prev;
            this.next = next;
        }
    }

    private Node<E> first;
    private Node<E> last;
    private int size;

    public void addLast(E element) {
        Node<E> oldLast = last;
        Node<E> newNode = new Node<>(oldLast, element, null);
        last = newNode;
        if (oldLast == null) {
            first = newNode;
        } else {
            oldLast.next = newNode;
        }
        size++;
    }

    public E get(int index) {
        // Must traverse from start or end
        Node<E> node;
        if (index < size / 2) {
            node = first;
            for (int i = 0; i < index; i++) node = node.next;
        } else {
            node = last;
            for (int i = size - 1; i > index; i--) node = node.prev;
        }
        return node.item;
    }
}
```

Note: `get(index)` starts from whichever end is closer. Still O(n/2) = O(n).

## Memory Overhead

Each ArrayList element costs: the element reference (8 bytes on 64-bit).

Each LinkedList element costs: the element reference + next pointer + prev pointer + Node object header = ~40 bytes overhead per element.

For 1 million elements:
- ArrayList: ~8 MB (references) + backing array
- LinkedList: ~48 MB (nodes with pointers)

LinkedList uses **6x more memory** per element. This also hurts cache performance — nodes are scattered in memory, causing cache misses.

## When to Use LinkedList

✅ **Use LinkedList when:**
- You frequently insert/remove at both ends (use as Deque)
- You iterate and remove/insert during iteration
- You never access by index
- The list is used as a queue (FIFO)

❌ **Don't use LinkedList when:**
- You need random access (`get(i)`)
- You mostly add to the end and read sequentially (ArrayList is better)
- Memory is a concern
- You need cache-friendly iteration (ArrayList wins)

## The Honest Truth

In practice, **ArrayList beats LinkedList in almost every real-world scenario**. Modern CPUs are optimized for sequential memory access (cache lines). ArrayList's contiguous memory layout gives it a massive constant-factor advantage.

LinkedList's theoretical O(1) insert/remove rarely matters because:
1. You usually need to *find* the position first (O(n))
2. ArrayList's O(n) shift is a `System.arraycopy` — a single optimized memory operation
3. Cache misses in LinkedList traversal are expensive

Raj's rule: "If you're reaching for LinkedList, you probably want ArrayDeque (Chapter 9) or a different data structure entirely."

## Benchmark

```java
int n = 100_000;

// Insert at beginning: LinkedList wins
// ArrayList: 2,400 ms (shifts everything each time)
// LinkedList: 8 ms (just rewire pointers)

// Random access: ArrayList wins
// ArrayList: 2 ms (direct index)
// LinkedList: 4,200 ms (traverse from head/tail)

// Sequential iteration: ArrayList wins
// ArrayList: 3 ms (cache-friendly)
// LinkedList: 12 ms (pointer chasing, cache misses)
```

## What You Learned

- **LinkedList** — doubly-linked nodes, O(1) insert/remove at known positions
- **The catch** — finding a position is O(n), negating the O(1) insert
- **Use iterators** — that's where LinkedList actually shines
- **Memory overhead** — ~6x more per element than ArrayList
- **Cache unfriendly** — scattered memory, poor CPU cache utilization
- **Honest advice** — ArrayList is usually better; consider ArrayDeque for queue operations

The undo system works. But a new bug appeared: duplicate order IDs are slipping through the system. We need a collection that rejects duplicates automatically.

---

[← Chapter 1: ArrayList](chapter-01-arraylist.md) | [Chapter 3: HashSet →](chapter-03-hashset.md)

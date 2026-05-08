# Chapter 8: Task Scheduling — PriorityQueue

[← Chapter 7: TreeMap](chapter-07-treemap.md) | [Chapter 9: Deque →](chapter-09-deque.md)

---

## The Problem

ShipStream processes orders by priority: VIP customers first, then express, then standard. The current approach sorts the entire queue on every poll:

```java
List<Order> queue = new ArrayList<>();
queue.add(order);
Collections.sort(queue, Comparator.comparingInt(Order::priority));
Order next = queue.remove(0);  // O(n) shift after sort
```

## PriorityQueue: Always Know the Highest Priority

```java
PriorityQueue<Order> queue = new PriorityQueue<>(
    Comparator.comparingInt(Order::priority)  // Lower number = higher priority
);

queue.offer(new Order("std-1", 3));   // Standard
queue.offer(new Order("vip-1", 1));   // VIP
queue.offer(new Order("exp-1", 2));   // Express

queue.poll();  // vip-1 (priority 1 — highest)
queue.poll();  // exp-1 (priority 2)
queue.poll();  // std-1 (priority 3)
```

## How It Works: Binary Heap

PriorityQueue uses a binary min-heap — a complete binary tree where every parent is smaller than its children:

```
        [1: VIP]
       /        \
  [2: Express]  [3: Standard]
```

| Operation | Time |
|---|---|
| `offer(element)` | O(log n) |
| `poll()` | O(log n) |
| `peek()` | O(1) |
| `contains(element)` | O(n) |
| `remove(element)` | O(n) |

## ShipStream's Order Scheduler

```java
public class OrderScheduler {
    private final PriorityQueue<Order> queue = new PriorityQueue<>(
        Comparator.comparingInt(Order::priority)
            .thenComparing(Order::createdAt)  // FIFO within same priority
    );

    public void submit(Order order) {
        queue.offer(order);
    }

    public Order nextOrder() {
        return queue.poll();  // Highest priority, oldest first
    }

    public int pendingCount() {
        return queue.size();
    }
}
```

## Important: PriorityQueue Is NOT Sorted

Iterating a PriorityQueue does NOT give sorted order:

```java
// WRONG: iteration order is NOT sorted
for (Order o : queue) { ... }  // Arbitrary heap order

// RIGHT: poll repeatedly for sorted order
while (!queue.isEmpty()) {
    Order o = queue.poll();  // Sorted
}
```

## What You Learned

- **PriorityQueue** — binary heap, O(log n) insert/remove-min
- **peek()** — O(1) view of highest-priority element
- **Not sorted for iteration** — only poll() gives sorted order
- **Comparator** — defines priority (natural order or custom)

---

[← Chapter 7: TreeMap](chapter-07-treemap.md) | [Chapter 9: Deque →](chapter-09-deque.md)

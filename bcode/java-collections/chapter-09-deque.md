# Chapter 9: FIFO Processing — Deque

[← Chapter 8: PriorityQueue](chapter-08-priorityqueue.md) | [Chapter 10: Unmodifiable Collections →](chapter-10-unmodifiable.md)

---

## The Problem

ShipStream's work-stealing scheduler needs a double-ended queue: workers take from the front of their own queue, but steal from the back of other workers' queues.

## ArrayDeque: The Swiss Army Queue

```java
Deque<Task> workQueue = new ArrayDeque<>();

// Queue operations (FIFO)
workQueue.offerLast(task);    // Add to back
Task next = workQueue.pollFirst();  // Remove from front

// Stack operations (LIFO)
workQueue.offerFirst(task);   // Push to front
Task top = workQueue.pollFirst();   // Pop from front

// Peek without removing
workQueue.peekFirst();  // Front
workQueue.peekLast();   // Back
```

## ArrayDeque vs LinkedList as Queue

| Operation | ArrayDeque | LinkedList |
|---|---|---|
| Add to end | O(1) amortized | O(1) |
| Remove from front | O(1) | O(1) |
| Memory per element | ~8 bytes | ~48 bytes |
| Cache performance | Excellent | Poor |

**Always prefer ArrayDeque over LinkedList** for queue/stack operations. It's faster, uses less memory, and is more cache-friendly.

## Work-Stealing Pattern

```java
public class WorkStealingScheduler {
    private final Deque<Task>[] queues;

    public void submit(int workerId, Task task) {
        queues[workerId].offerLast(task);
    }

    public Task getWork(int workerId) {
        // Try own queue first
        Task task = queues[workerId].pollFirst();
        if (task != null) return task;

        // Steal from others' back
        for (int i = 0; i < queues.length; i++) {
            if (i != workerId) {
                task = queues[i].pollLast();  // Steal from back
                if (task != null) return task;
            }
        }
        return null;
    }
}
```

## What You Learned

- **ArrayDeque** — resizable circular array, O(1) both ends
- **Prefer over LinkedList** — faster, less memory, cache-friendly
- **Deque interface** — supports both queue (FIFO) and stack (LIFO)
- **Work-stealing** — take from front, steal from back

---

[← Chapter 8: PriorityQueue](chapter-08-priorityqueue.md) | [Chapter 10: Unmodifiable Collections →](chapter-10-unmodifiable.md)

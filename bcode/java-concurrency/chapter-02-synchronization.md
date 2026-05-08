# Chapter 2: Shared Counters — Synchronization

[← Chapter 1: Threads](chapter-01-threads.md) | [Chapter 3: Volatile →](chapter-03-volatile.md)

---

## The Problem

From Chapter 1, our event counter is broken:

```java
public class EventCounter {
    private int count = 0;

    public void increment() {
        count++;  // Race condition: read-modify-write is not atomic
    }

    public int getCount() {
        return count;
    }
}
```

Four ingestion threads, 500K increments each. Expected: 2,000,000. Actual: ~1,600,000. We're losing 400,000 events.

Omar at 3 AM: "The dashboard says we processed 1.6M events but the queue had 2M. Where did 400K events go?"

They didn't go anywhere. The counter is wrong. The events were processed — we just can't count them correctly.

## synchronized: The Mutual Exclusion Lock

The `synchronized` keyword ensures only one thread executes a block at a time:

```java
public class EventCounter {
    private int count = 0;

    public synchronized void increment() {
        count++;  // Only one thread at a time
    }

    public synchronized int getCount() {
        return count;
    }
}
```

Now:
```
Thread A: acquires lock → reads count (5) → adds 1 → writes count (6) → releases lock
Thread B: waits... waits... acquires lock → reads count (6) → adds 1 → writes count (7) → releases lock
```

No interleaving. No lost updates. The count is always correct.

## How synchronized Works

Every Java object has an intrinsic lock (also called a monitor). `synchronized` acquires this lock:

```java
// Method-level: locks on `this`
public synchronized void increment() {
    count++;
}

// Equivalent block-level:
public void increment() {
    synchronized (this) {
        count++;
    }
}

// Lock on a specific object:
private final Object lock = new Object();

public void increment() {
    synchronized (lock) {
        count++;
    }
}
```

### Why a Separate Lock Object?

```java
// RISKY: locking on `this` means external code can also lock on your object
synchronized (counter) {  // Someone else locks your counter
    Thread.sleep(10000);  // Blocks all your synchronized methods!
}

// SAFE: private lock — only you can acquire it
private final Object lock = new Object();
```

Use a private lock object when your class is part of a public API.

## The Happens-Before Guarantee

`synchronized` does more than mutual exclusion. It establishes a **happens-before** relationship:

```java
// Thread A:
synchronized (lock) {
    x = 42;           // Write inside synchronized
}

// Thread B:
synchronized (lock) {
    System.out.println(x);  // Guaranteed to see 42
}
```

When Thread B acquires the same lock that Thread A released, Thread B is guaranteed to see all writes Thread A made before releasing. This is the JMM's happens-before guarantee.

Without `synchronized`, Thread B might see `x = 0` (stale cached value) even after Thread A wrote 42.

## Critical Sections: Keep Them Small

```java
// BAD: holding the lock during I/O
public synchronized void processEvent(Event event) {
    count++;                    // Needs lock
    validate(event);           // CPU work — needs lock? Maybe.
    writeToDatabase(event);    // Network I/O — 5ms! Don't hold lock!
    log(event);                // I/O — don't hold lock!
}

// GOOD: lock only what needs locking
public void processEvent(Event event) {
    synchronized (lock) {
        count++;               // Protected
    }
    validate(event);           // No shared state — no lock needed
    writeToDatabase(event);    // I/O outside the lock
    log(event);
}
```

Rule: **hold locks for the shortest time possible.** Every millisecond you hold a lock, other threads are blocked.

## PulseMetrics: Thread-Safe Aggregator

```java
public class MetricsAggregator {
    private final Object lock = new Object();
    private long totalEvents = 0;
    private long totalBytes = 0;
    private final Map<String, Long> eventsByType = new HashMap<>();

    public void recordEvent(String type, int bytes) {
        synchronized (lock) {
            totalEvents++;
            totalBytes += bytes;
            eventsByType.merge(type, 1L, Long::sum);
        }
    }

    public Snapshot getSnapshot() {
        synchronized (lock) {
            // Return a copy — don't leak the mutable map
            return new Snapshot(totalEvents, totalBytes, Map.copyOf(eventsByType));
        }
    }

    public record Snapshot(long events, long bytes, Map<String, Long> byType) {}
}
```

Key points:
- Same lock for `recordEvent` and `getSnapshot` — ensures consistent reads
- `getSnapshot` returns an immutable copy — safe to use outside the lock
- `Map.copyOf` prevents the caller from seeing future mutations

## Deadlock Preview

What happens when two threads need two locks?

```java
// Thread A:
synchronized (lockA) {
    synchronized (lockB) {  // Waits for Thread B to release lockB
        // ...
    }
}

// Thread B:
synchronized (lockB) {
    synchronized (lockA) {  // Waits for Thread A to release lockA
        // ...
    }
}
```

Both threads wait forever. This is a **deadlock**. We'll cover detection and prevention in Chapter 13.

## wait() and notify(): Thread Coordination

Sometimes a thread needs to wait for a condition:

```java
public class BoundedBuffer<E> {
    private final Queue<E> queue = new LinkedList<>();
    private final int capacity;

    public BoundedBuffer(int capacity) {
        this.capacity = capacity;
    }

    public synchronized void put(E item) throws InterruptedException {
        while (queue.size() == capacity) {
            wait();  // Release lock, sleep until notified
        }
        queue.add(item);
        notifyAll();  // Wake up waiting consumers
    }

    public synchronized E take() throws InterruptedException {
        while (queue.isEmpty()) {
            wait();  // Release lock, sleep until notified
        }
        E item = queue.poll();
        notifyAll();  // Wake up waiting producers
        return item;
    }
}
```

- `wait()` — releases the lock and suspends the thread until `notify()`/`notifyAll()`
- `notifyAll()` — wakes all threads waiting on this lock
- Always use `while` (not `if`) around `wait()` — spurious wakeups can happen

## Benchmark: Synchronized vs Unsynchronized

```java
int threads = 4;
int incrementsPerThread = 10_000_000;

// Unsynchronized: ~120ms (wrong answer)
// Synchronized:   ~850ms (correct answer)
```

Synchronization has a cost: ~7x slower here. That's the price of correctness. In Chapter 5, we'll see `AtomicLong` which is ~3x faster than synchronized for simple counters.

## Common Mistakes

### 1. Synchronizing on the Wrong Object

```java
// WRONG: each thread creates a new lock!
public void increment() {
    synchronized (new Object()) {  // Useless — different object each time
        count++;
    }
}
```

### 2. Synchronizing on a Non-Final Reference

```java
private Object lock = new Object();

public void reset() {
    lock = new Object();  // Now threads use different locks!
}
```

Always make lock objects `final`.

### 3. Forgetting to Synchronize Reads

```java
public synchronized void increment() { count++; }
public int getCount() { return count; }  // WRONG: unsynchronized read
```

If writes are synchronized but reads aren't, the reader might see stale data. Both must synchronize on the same lock.

## What You Learned

- **synchronized** — mutual exclusion, only one thread in the block at a time
- **Intrinsic locks** — every object has one, acquired by synchronized
- **Happens-before** — synchronized establishes visibility guarantees
- **Keep critical sections small** — don't hold locks during I/O
- **Private lock objects** — prevent external code from interfering
- **wait/notify** — thread coordination within synchronized blocks
- **Always synchronize both reads and writes** on shared state

The counter is correct now. But Nadia notices a different bug: the shutdown flag isn't working. Thread A sets `running = false`, but Thread B keeps running. That's a visibility problem — and `volatile` is the fix.

---

[← Chapter 1: Threads](chapter-01-threads.md) | [Chapter 3: Volatile →](chapter-03-volatile.md)

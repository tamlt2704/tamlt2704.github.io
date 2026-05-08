# Chapter 4: Explicit Locks

[← Chapter 3: Volatile](chapter-03-volatile.md) | [Chapter 5: Atomics →](chapter-05-atomics.md)

---

## The Problem

PulseMetrics' metrics aggregator uses `synchronized` to protect shared state:

```java
public class MetricsAggregator {
    public synchronized void recordEvent(Event event) {
        // 200μs of CPU work
        updateCounters(event);
        updateHistogram(event);
        updateTopK(event);
    }

    public synchronized Snapshot getSnapshot() {
        // Reads all counters — takes 50μs
        return new Snapshot(counters, histogram, topK);
    }
}
```

The problem: `getSnapshot()` is called 500 times/second by dashboard connections. `recordEvent()` is called 2 million times/second by ingestion threads. Both acquire the same lock.

Dashboard reads block ingestion writes. Ingestion writes block dashboard reads. With `synchronized`, there's no way to say "multiple readers are fine, just block writers."

Nadia: "Why are dashboard reads blocking ingestion? Reads don't modify anything."

She's right. We need a lock that distinguishes readers from writers.

## ReentrantLock: The Explicit Lock

`ReentrantLock` gives you the same mutual exclusion as `synchronized`, but with more control:

```java
import java.util.concurrent.locks.ReentrantLock;

public class EventCounter {
    private final ReentrantLock lock = new ReentrantLock();
    private long count = 0;

    public void increment() {
        lock.lock();
        try {
            count++;
        } finally {
            lock.unlock();  // ALWAYS in finally
        }
    }

    public long getCount() {
        lock.lock();
        try {
            return count;
        } finally {
            lock.unlock();
        }
    }
}
```

Critical rule: **always unlock in a finally block.** If the code between lock/unlock throws an exception, the lock stays held forever. Deadlock.

## Why "Reentrant"?

A reentrant lock can be acquired multiple times by the same thread:

```java
public void outerMethod() {
    lock.lock();
    try {
        innerMethod();  // This also acquires the lock — same thread, OK
    } finally {
        lock.unlock();
    }
}

public void innerMethod() {
    lock.lock();  // Same thread already holds it — reentrant, no deadlock
    try {
        // ...
    } finally {
        lock.unlock();
    }
}
```

`synchronized` is also reentrant. Without reentrancy, calling a synchronized method from another synchronized method on the same object would deadlock.

## tryLock(): Non-Blocking Lock Acquisition

This is where `ReentrantLock` shines over `synchronized`. You can *try* to acquire the lock without blocking:

```java
public boolean tryRecordEvent(Event event) {
    if (lock.tryLock()) {
        try {
            updateCounters(event);
            return true;
        } finally {
            lock.unlock();
        }
    }
    // Lock not available — buffer the event instead of blocking
    return false;
}
```

With `synchronized`, if the lock is held, you block. Period. With `tryLock()`, you can do something else — buffer the event, try a different shard, skip the update.

### tryLock with Timeout

```java
if (lock.tryLock(100, TimeUnit.MILLISECONDS)) {
    try {
        processEvent(event);
    } finally {
        lock.unlock();
    }
} else {
    // Couldn't get lock in 100ms — log and move on
    metrics.recordDropped(event);
}
```

This prevents threads from waiting forever. Essential for meeting latency SLAs.

## ReadWriteLock: Multiple Readers, Single Writer

The real fix for PulseMetrics. `ReadWriteLock` allows concurrent reads but exclusive writes:

```java
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;

public class MetricsAggregator {
    private final ReadWriteLock rwLock = new ReentrantReadWriteLock();
    private long totalEvents = 0;
    private final Map<String, Long> counters = new HashMap<>();

    public void recordEvent(Event event) {
        rwLock.writeLock().lock();
        try {
            totalEvents++;
            counters.merge(event.type(), 1L, Long::sum);
        } finally {
            rwLock.writeLock().unlock();
        }
    }

    public Snapshot getSnapshot() {
        rwLock.readLock().lock();
        try {
            return new Snapshot(totalEvents, Map.copyOf(counters));
        } finally {
            rwLock.readLock().unlock();
        }
    }
}
```

Now:
- Multiple dashboard threads can call `getSnapshot()` simultaneously (read lock is shared)
- `recordEvent()` waits for all readers to finish, then gets exclusive access
- Readers wait only when a writer is active

## Lock Fairness

By default, `ReentrantLock` is **unfair** — when the lock is released, any waiting thread might get it, regardless of who waited longest. This is faster but can starve threads.

```java
// Fair lock: threads acquire in FIFO order
ReentrantLock fairLock = new ReentrantLock(true);

// Unfair lock (default): better throughput, possible starvation
ReentrantLock unfairLock = new ReentrantLock(false);
```

Fair locks have ~10-20% lower throughput because they must maintain a queue. Use fair locks only when starvation is a real problem (e.g., a low-priority thread never gets the lock).

```java
// Fair ReadWriteLock
ReadWriteLock rwLock = new ReentrantReadWriteLock(true);
```

With a fair `ReadWriteLock`, writers won't starve even under heavy read load.

## Condition Variables: Better wait/notify

`ReentrantLock` comes with `Condition` objects — a more flexible replacement for `wait()`/`notify()`:

```java
public class BoundedBuffer<E> {
    private final ReentrantLock lock = new ReentrantLock();
    private final Condition notFull = lock.newCondition();
    private final Condition notEmpty = lock.newCondition();
    private final Queue<E> queue = new LinkedList<>();
    private final int capacity;

    public BoundedBuffer(int capacity) {
        this.capacity = capacity;
    }

    public void put(E item) throws InterruptedException {
        lock.lock();
        try {
            while (queue.size() == capacity) {
                notFull.await();  // Wait until not full
            }
            queue.add(item);
            notEmpty.signal();  // Wake one consumer
        } finally {
            lock.unlock();
        }
    }

    public E take() throws InterruptedException {
        lock.lock();
        try {
            while (queue.isEmpty()) {
                notEmpty.await();  // Wait until not empty
            }
            E item = queue.poll();
            notFull.signal();  // Wake one producer
            return item;
        } finally {
            lock.unlock();
        }
    }
}
```

Advantage over `wait()`/`notify()`: you can have multiple conditions on the same lock. Producers wait on `notFull`, consumers wait on `notEmpty`. With `synchronized`, you'd have to `notifyAll()` and wake everyone.

## StampedLock: Optimistic Reading (Java 8+)

For read-heavy workloads, `StampedLock` offers optimistic reads that don't acquire any lock:

```java
import java.util.concurrent.locks.StampedLock;

public class MetricsAggregator {
    private final StampedLock sl = new StampedLock();
    private long totalEvents = 0;
    private double avgLatency = 0.0;

    public void recordEvent(long latency) {
        long stamp = sl.writeLock();
        try {
            totalEvents++;
            avgLatency = avgLatency * 0.99 + latency * 0.01;
        } finally {
            sl.unlockWrite(stamp);
        }
    }

    public double getAvgLatency() {
        // Optimistic read — no lock acquired!
        long stamp = sl.tryOptimisticRead();
        double latency = avgLatency;
        if (!sl.validate(stamp)) {
            // A write happened during our read — fall back to read lock
            stamp = sl.readLock();
            try {
                latency = avgLatency;
            } finally {
                sl.unlockRead(stamp);
            }
        }
        return latency;
    }
}
```

Optimistic reads are free when there's no contention. If a write happens during the read, you retry with a real lock. Perfect for dashboards that read far more than they write.

## PulseMetrics: The Fix

```java
public class PipelineMetrics {
    private final ReadWriteLock rwLock = new ReentrantReadWriteLock();
    private long totalEvents = 0;
    private long totalBytes = 0;
    private final Map<String, Long> eventsBySource = new HashMap<>();
    private final long[] latencyBuckets = new long[10];  // 0-10ms, 10-20ms, etc.

    // Called by 8 ingestion threads — 2M events/sec total
    public void record(String source, int bytes, long latencyMs) {
        rwLock.writeLock().lock();
        try {
            totalEvents++;
            totalBytes += bytes;
            eventsBySource.merge(source, 1L, Long::sum);
            int bucket = (int) Math.min(latencyMs / 10, 9);
            latencyBuckets[bucket]++;
        } finally {
            rwLock.writeLock().unlock();
        }
    }

    // Called by 500 dashboard connections — reads only
    public DashboardData getDashboardData() {
        rwLock.readLock().lock();
        try {
            return new DashboardData(
                totalEvents,
                totalBytes,
                Map.copyOf(eventsBySource),
                latencyBuckets.clone()
            );
        } finally {
            rwLock.readLock().unlock();
        }
    }

    public record DashboardData(
        long events, long bytes,
        Map<String, Long> bySource, long[] latencyBuckets
    ) {}
}
```

Dashboard reads no longer block each other. Ingestion throughput improved 3x because readers aren't holding the exclusive lock.

## synchronized vs ReentrantLock: When to Use Which

| Feature | synchronized | ReentrantLock |
|---|---|---|
| Syntax | Simple | Verbose (try/finally) |
| tryLock | No | Yes |
| Timeout | No | Yes |
| Fairness | No | Configurable |
| Multiple conditions | No | Yes |
| Read/write separation | No | Yes (ReadWriteLock) |
| Interruptible | No | lockInterruptibly() |

**Use synchronized** when: simple mutual exclusion, no timeout needed, code is short.

**Use ReentrantLock** when: you need tryLock, timeouts, fairness, conditions, or read/write separation.

## What You Learned

- **ReentrantLock** — explicit lock with try/finally pattern
- **tryLock()** — non-blocking lock acquisition, with optional timeout
- **ReadWriteLock** — concurrent readers, exclusive writers
- **Fairness** — FIFO ordering at the cost of throughput
- **Condition** — multiple wait sets on one lock (better than wait/notify)
- **StampedLock** — optimistic reads for read-heavy workloads
- **Always unlock in finally** — or you'll deadlock

Dashboard reads are fast now. But the write lock is still a bottleneck — 8 threads contending on one lock for every event. What if we could update counters without any lock at all? That's atomics.

---

[← Chapter 3: Volatile](chapter-03-volatile.md) | [Chapter 5: Atomics →](chapter-05-atomics.md)

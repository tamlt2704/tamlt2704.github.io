# Chapter 5: Atomics and CAS

[← Chapter 4: Locks](chapter-04-locks.md) | [Chapter 6: Executors →](chapter-06-executors.md)

---

## The Problem

PulseMetrics' ingestion counter uses a `ReentrantLock`:

```java
public class EventCounter {
    private final ReentrantLock lock = new ReentrantLock();
    private long count = 0;

    public void increment() {
        lock.lock();
        try {
            count++;
        } finally {
            lock.unlock();
        }
    }
}
```

Eight ingestion threads, each doing 250K increments/second. The lock works — the count is correct. But profiling shows 40% of CPU time is spent on lock acquisition and release. Threads are fighting over one lock for a single `count++`.

Kai: "We're spending more time locking than counting. There has to be a better way."

There is. Atomic variables use CPU-level instructions to update values without locks.

## AtomicInteger / AtomicLong

```java
import java.util.concurrent.atomic.AtomicLong;

public class EventCounter {
    private final AtomicLong count = new AtomicLong(0);

    public void increment() {
        count.incrementAndGet();  // Atomic — no lock needed
    }

    public long getCount() {
        return count.get();
    }
}
```

No lock. No `try/finally`. No blocking. `incrementAndGet()` is a single atomic operation at the hardware level.

## How It Works: Compare-And-Swap (CAS)

Under the hood, `incrementAndGet()` uses a CPU instruction called **CAS** (Compare-And-Swap):

```java
// Pseudocode for what incrementAndGet() does:
long incrementAndGet() {
    while (true) {
        long current = value;              // Read current value
        long next = current + 1;           // Compute new value
        if (compareAndSwap(current, next)) // Atomically: if value == current, set to next
            return next;                   // Success!
        // CAS failed — another thread changed value. Retry.
    }
}
```

CAS says: "Set the value to `next`, but only if it's still `current`." If another thread changed it between the read and the CAS, the CAS fails and we retry. This is called a **spin loop** or **optimistic concurrency**.

No thread ever blocks. No thread ever waits for a lock. They just retry until they succeed.

## CAS vs Locks: The Tradeoff

| | Locks | CAS |
|---|---|---|
| Contention behavior | Thread blocks (sleeps) | Thread retries (spins) |
| Low contention | Lock overhead wasted | CAS succeeds first try |
| High contention | Threads sleep, fair | Threads spin, waste CPU |
| Best for | Long critical sections | Short operations (increment, swap) |

CAS wins when the operation is fast (a few nanoseconds) and contention is moderate. Under extreme contention, CAS threads spin-wait and waste CPU.

## Atomic Operations

```java
AtomicLong counter = new AtomicLong(0);

counter.incrementAndGet();     // ++counter (returns new value)
counter.getAndIncrement();     // counter++ (returns old value)
counter.addAndGet(10);         // counter += 10
counter.getAndAdd(10);         // old = counter; counter += 10; return old

counter.compareAndSet(5, 10);  // if (counter == 5) { counter = 10; return true; }
                               // else return false;

counter.updateAndGet(x -> x * 2);  // Atomic: read, apply function, write
counter.accumulateAndGet(5, Long::max);  // Atomic: counter = max(counter, 5)
```

## AtomicReference: Atomic Object Swaps

For swapping object references atomically:

```java
import java.util.concurrent.atomic.AtomicReference;

public class ConfigManager {
    private final AtomicReference<Config> config = new AtomicReference<>(Config.defaults());

    // One thread reloads config
    public void reload() {
        Config newConfig = loadFromDisk();
        config.set(newConfig);  // Atomic reference swap
    }

    // Many threads read config
    public Config getConfig() {
        return config.get();
    }

    // Conditional update: only replace if still the old config
    public boolean updateIfCurrent(Config expected, Config newConfig) {
        return config.compareAndSet(expected, newConfig);
    }
}
```

`compareAndSet` on references compares by identity (`==`), not `equals()`.

## The ABA Problem

CAS has a subtle bug called ABA:

```
Thread A: reads value = A
Thread B: changes value to B
Thread B: changes value back to A
Thread A: CAS(A, C) succeeds — but the value was modified!
```

Thread A thinks nothing changed (it's still A), but it was actually modified and reverted. For simple counters this doesn't matter. For pointer-based data structures, it can corrupt state.

Solution: `AtomicStampedReference` adds a version number:

```java
AtomicStampedReference<Node> head = new AtomicStampedReference<>(null, 0);

int[] stampHolder = new int[1];
Node current = head.get(stampHolder);
int stamp = stampHolder[0];

// CAS checks both reference AND stamp
head.compareAndSet(current, newNode, stamp, stamp + 1);
```

## LongAdder: When CAS Isn't Enough

At 2M events/second across 8 threads, even `AtomicLong` shows contention — threads keep retrying CAS because others keep changing the value.

`LongAdder` solves this by **striping** — each thread updates its own cell, and you sum them when you need the total:

```java
import java.util.concurrent.atomic.LongAdder;

public class EventCounter {
    private final LongAdder count = new LongAdder();

    public void increment() {
        count.increment();  // Each thread hits its own cell — no contention
    }

    public long getCount() {
        return count.sum();  // Sums all cells — slightly stale but correct
    }
}
```

### Benchmark: 8 Threads, 10M Increments Each

```
synchronized:    1,200ms
AtomicLong:        380ms
LongAdder:          95ms
```

`LongAdder` is 12x faster than `synchronized` and 4x faster than `AtomicLong` under high contention.

The tradeoff: `sum()` is not an atomic snapshot. If threads are still incrementing while you call `sum()`, you get an approximate value. For metrics counters, that's fine.

## LongAccumulator: Custom Reduction

`LongAdder` only does addition. `LongAccumulator` lets you define any associative operation:

```java
import java.util.concurrent.atomic.LongAccumulator;

// Track maximum latency across all threads
LongAccumulator maxLatency = new LongAccumulator(Long::max, 0);

// In each thread:
maxLatency.accumulate(eventLatency);

// Read the max:
long max = maxLatency.get();
```

```java
// Track minimum (use Long.MAX_VALUE as identity)
LongAccumulator minLatency = new LongAccumulator(Long::min, Long.MAX_VALUE);
```

## PulseMetrics: Lock-Free Metrics

```java
public class PipelineMetrics {
    private final LongAdder totalEvents = new LongAdder();
    private final LongAdder totalBytes = new LongAdder();
    private final LongAccumulator maxLatency = new LongAccumulator(Long::max, 0);
    private final LongAdder[] latencyBuckets;

    // Per-source counters using ConcurrentHashMap + LongAdder
    private final ConcurrentHashMap<String, LongAdder> bySource = new ConcurrentHashMap<>();

    public PipelineMetrics() {
        latencyBuckets = new LongAdder[10];
        for (int i = 0; i < 10; i++) {
            latencyBuckets[i] = new LongAdder();
        }
    }

    // Called by 8 ingestion threads — NO LOCKS
    public void record(String source, int bytes, long latencyMs) {
        totalEvents.increment();
        totalBytes.add(bytes);
        maxLatency.accumulate(latencyMs);

        int bucket = (int) Math.min(latencyMs / 10, 9);
        latencyBuckets[bucket].increment();

        bySource.computeIfAbsent(source, k -> new LongAdder()).increment();
    }

    // Dashboard reads — no lock needed, slightly stale is OK
    public DashboardData snapshot() {
        return new DashboardData(
            totalEvents.sum(),
            totalBytes.sum(),
            maxLatency.get(),
            Arrays.stream(latencyBuckets).mapToLong(LongAdder::sum).toArray()
        );
    }

    public record DashboardData(long events, long bytes, long maxLatency, long[] buckets) {}
}
```

Zero locks. Zero blocking. Each ingestion thread updates its own striped cells. Dashboard reads sum the cells — slightly stale (by microseconds) but never blocks ingestion.

## Building a Lock-Free Stack (Advanced)

CAS enables lock-free data structures:

```java
public class LockFreeStack<E> {
    private final AtomicReference<Node<E>> top = new AtomicReference<>(null);

    public void push(E item) {
        Node<E> newNode = new Node<>(item);
        while (true) {
            Node<E> current = top.get();
            newNode.next = current;
            if (top.compareAndSet(current, newNode)) return;  // CAS loop
        }
    }

    public E pop() {
        while (true) {
            Node<E> current = top.get();
            if (current == null) return null;
            if (top.compareAndSet(current, current.next)) return current.item;
        }
    }

    private static class Node<E> {
        final E item;
        Node<E> next;
        Node(E item) { this.item = item; }
    }
}
```

No locks. Threads never block. Under contention, they retry CAS until they succeed.

## When to Use What

| Scenario | Tool |
|---|---|
| Simple counter, low contention | AtomicLong |
| Simple counter, high contention | LongAdder |
| Max/min tracking | LongAccumulator |
| Swap a reference atomically | AtomicReference |
| Compound operation (check-then-act) | Lock or synchronized |
| Multiple variables must update together | Lock or synchronized |

Atomics can't help when you need to update multiple variables atomically. `if (x > 0) { x--; y++; }` needs a lock — there's no CAS for two variables at once.

## What You Learned

- **AtomicLong/AtomicInteger** — lock-free counters using CAS
- **CAS (Compare-And-Swap)** — hardware instruction: "set if unchanged, else retry"
- **LongAdder** — striped counter for high-contention scenarios (4x faster than AtomicLong)
- **LongAccumulator** — custom reduction (max, min, etc.)
- **AtomicReference** — atomic object reference swaps
- **ABA problem** — CAS can miss intermediate changes (use AtomicStampedReference)
- **Lock-free ≠ wait-free** — threads don't block but may spin

The counters are fast. But we're still creating a new `Thread` for every task. At 2M events/second, that's catastrophic. We need thread pools.

---

[← Chapter 4: Locks](chapter-04-locks.md) | [Chapter 6: Executors →](chapter-06-executors.md)

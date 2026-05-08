# Chapter 13: Deadlocks and Debugging

[← Chapter 12: Virtual Threads](chapter-12-virtual-threads.md) | [Chapter 14: Patterns →](chapter-14-patterns.md)

---

## The Problem

3 AM. Omar's phone buzzes. PagerDuty alert: "PulseMetrics ingestion rate dropped to zero."

No exceptions in the logs. No OOM. CPU at 0%. The process is alive but doing nothing. Omar takes a thread dump:

```
"ingestion-0" #12 prio=5 BLOCKED
    waiting to lock <0x00000007c0a1b2c0> (MetricsStore)
    locked <0x00000007c0a1b3d0> (EventBuffer)

"ingestion-1" #13 prio=5 BLOCKED
    waiting to lock <0x00000007c0a1b3d0> (EventBuffer)
    locked <0x00000007c0a1b2c0> (MetricsStore)

Found 1 deadlock.
```

Thread 0 holds `EventBuffer`, wants `MetricsStore`.
Thread 1 holds `MetricsStore`, wants `EventBuffer`.
Neither can proceed. The system is frozen.

## What Is a Deadlock?

A deadlock occurs when two or more threads are each waiting for a resource held by another, forming a cycle:

```
Thread A: holds Lock 1, waiting for Lock 2
Thread B: holds Lock 2, waiting for Lock 1
```

Four conditions must ALL be true for deadlock (Coffman conditions):
1. **Mutual exclusion**: resources can't be shared
2. **Hold and wait**: thread holds one resource while waiting for another
3. **No preemption**: resources can't be forcibly taken
4. **Circular wait**: A waits for B, B waits for A (or longer cycle)

Break any one condition and deadlock is impossible.

## The Deadlocked Code

```java
public class Pipeline {
    private final Object bufferLock = new Object();
    private final Object metricsLock = new Object();

    // Called by ingestion threads
    public void processEvent(Event event) {
        synchronized (bufferLock) {          // Acquires bufferLock
            buffer.add(event);
            synchronized (metricsLock) {     // Then acquires metricsLock
                metrics.record(event);
            }
        }
    }

    // Called by dashboard threads
    public Snapshot getSnapshot() {
        synchronized (metricsLock) {         // Acquires metricsLock
            Snapshot snap = metrics.snapshot();
            synchronized (bufferLock) {      // Then acquires bufferLock
                snap.setPending(buffer.size());
            }
            return snap;
        }
    }
}
```

`processEvent`: bufferLock → metricsLock
`getSnapshot`: metricsLock → bufferLock

Opposite ordering. Deadlock waiting to happen.

## Fix 1: Consistent Lock Ordering

The simplest fix — always acquire locks in the same order:

```java
public class Pipeline {
    private final Object bufferLock = new Object();   // Always first
    private final Object metricsLock = new Object();  // Always second

    public void processEvent(Event event) {
        synchronized (bufferLock) {
            synchronized (metricsLock) {
                buffer.add(event);
                metrics.record(event);
            }
        }
    }

    public Snapshot getSnapshot() {
        synchronized (bufferLock) {       // Same order: buffer first
            synchronized (metricsLock) {  // Then metrics
                Snapshot snap = metrics.snapshot();
                snap.setPending(buffer.size());
                return snap;
            }
        }
    }
}
```

Rule: define a global ordering for all locks. Every thread acquires them in that order. No cycles possible.

### Ordering by Object Identity

When you can't define a static order (e.g., transferring between arbitrary accounts):

```java
public void transfer(Account from, Account to, long amount) {
    // Order by System.identityHashCode to prevent deadlock
    Account first = System.identityHashCode(from) < System.identityHashCode(to) ? from : to;
    Account second = first == from ? to : from;

    synchronized (first) {
        synchronized (second) {
            from.debit(amount);
            to.credit(amount);
        }
    }
}
```

## Fix 2: tryLock with Timeout

Use `ReentrantLock.tryLock()` to detect and recover from potential deadlocks:

```java
public class Pipeline {
    private final ReentrantLock bufferLock = new ReentrantLock();
    private final ReentrantLock metricsLock = new ReentrantLock();

    public boolean processEvent(Event event) {
        boolean gotBuffer = false;
        boolean gotMetrics = false;
        try {
            gotBuffer = bufferLock.tryLock(100, TimeUnit.MILLISECONDS);
            if (!gotBuffer) return false;  // Couldn't get lock — back off

            gotMetrics = metricsLock.tryLock(100, TimeUnit.MILLISECONDS);
            if (!gotMetrics) return false;  // Couldn't get lock — back off

            buffer.add(event);
            metrics.record(event);
            return true;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return false;
        } finally {
            if (gotMetrics) metricsLock.unlock();
            if (gotBuffer) bufferLock.unlock();
        }
    }
}
```

If a lock can't be acquired within the timeout, the thread backs off and retries. No indefinite waiting = no deadlock.

## Fix 3: Reduce Lock Scope

Often the best fix is to not hold multiple locks at all:

```java
public class Pipeline {
    private final ReentrantLock bufferLock = new ReentrantLock();
    private final ReentrantLock metricsLock = new ReentrantLock();

    public void processEvent(Event event) {
        // Acquire and release one at a time — never hold both
        bufferLock.lock();
        try {
            buffer.add(event);
        } finally {
            bufferLock.unlock();
        }

        metricsLock.lock();
        try {
            metrics.record(event);
        } finally {
            metricsLock.unlock();
        }
    }
}
```

No nested locks = no deadlock. The tradeoff: the two operations aren't atomic together. If that's acceptable, this is the safest approach.

## Detecting Deadlocks: jstack

```bash
# Get thread dump from running JVM
jstack <pid>

# Or trigger from within Java
kill -3 <pid>  # Sends SIGQUIT, JVM prints thread dump to stderr
```

jstack output for a deadlock:
```
Found one Java-level deadlock:
=============================
"ingestion-0":
  waiting to lock monitor 0x00007f8b3c003f08 (object 0x00000007c0a1b2c0, a MetricsStore),
  which is held by "ingestion-1"
"ingestion-1":
  waiting to lock monitor 0x00007f8b3c004a18 (object 0x00000007c0a1b3d0, a EventBuffer),
  which is held by "ingestion-0"

Java stack information for the threads listed above:
===================================================
"ingestion-0":
    at Pipeline.processEvent(Pipeline.java:15)
    - waiting to lock <0x00000007c0a1b2c0> (a MetricsStore)
    - locked <0x00000007c0a1b3d0> (a EventBuffer)
"ingestion-1":
    at Pipeline.getSnapshot(Pipeline.java:24)
    - waiting to lock <0x00000007c0a1b3d0> (a EventBuffer)
    - locked <0x00000007c0a1b2c0> (a MetricsStore)
```

## Programmatic Deadlock Detection

```java
import java.lang.management.ManagementFactory;
import java.lang.management.ThreadMXBean;

public class DeadlockDetector {
    private final ThreadMXBean threadBean = ManagementFactory.getThreadMXBean();

    public void startMonitoring() {
        ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();
        scheduler.scheduleAtFixedRate(this::checkForDeadlocks, 0, 10, TimeUnit.SECONDS);
    }

    private void checkForDeadlocks() {
        long[] deadlockedThreads = threadBean.findDeadlockedThreads();
        if (deadlockedThreads != null) {
            ThreadInfo[] infos = threadBean.getThreadInfo(deadlockedThreads, true, true);
            StringBuilder sb = new StringBuilder("DEADLOCK DETECTED!\n");
            for (ThreadInfo info : infos) {
                sb.append(info.getThreadName())
                  .append(" blocked on ").append(info.getLockName())
                  .append(" held by ").append(info.getLockOwnerName())
                  .append("\n");
            }
            logger.error(sb.toString());
            alerting.fire("deadlock_detected");
        }
    }
}
```

## Livelock: The Polite Deadlock

Two threads keep yielding to each other, making no progress:

```java
// Thread A and Thread B both try to acquire lock1 and lock2
// Both use tryLock, both back off at the same time, both retry at the same time...

while (true) {
    if (lock1.tryLock()) {
        try {
            if (lock2.tryLock()) {
                try { doWork(); return; }
                finally { lock2.unlock(); }
            }
        } finally { lock1.unlock(); }
    }
    // Both threads reach here at the same time, retry simultaneously → livelock
}
```

Fix: add random backoff:

```java
while (true) {
    if (lock1.tryLock()) {
        try {
            if (lock2.tryLock()) {
                try { doWork(); return; }
                finally { lock2.unlock(); }
            }
        } finally { lock1.unlock(); }
    }
    // Random backoff breaks the symmetry
    Thread.sleep(ThreadLocalRandom.current().nextInt(1, 10));
}
```

## Thread Starvation

Not a deadlock, but similar symptoms — a thread never gets CPU time:

```java
// Unfair lock: high-priority threads always win
ReentrantLock unfairLock = new ReentrantLock(false);

// Low-priority thread might never acquire the lock
// Fix: use fair lock
ReentrantLock fairLock = new ReentrantLock(true);
```

## PulseMetrics: Deadlock-Free Pipeline

```java
public class SafePipeline {
    // Single lock — simplest deadlock prevention
    private final ReentrantLock pipelineLock = new ReentrantLock();

    // Or: lock-free where possible
    private final LongAdder eventCount = new LongAdder();
    private final ConcurrentHashMap<String, LongAdder> metrics = new ConcurrentHashMap<>();
    private final ArrayBlockingQueue<Event> buffer = new ArrayBlockingQueue<>(100_000);

    // No locks needed for these operations!
    public void processEvent(Event event) {
        buffer.offer(event);  // Thread-safe queue, no lock
        eventCount.increment();  // Atomic, no lock
        metrics.computeIfAbsent(event.source(), k -> new LongAdder()).increment();  // CAS, no lock
    }

    // Only lock when you must coordinate multiple operations atomically
    public TransferResult transferBetweenBuffers(Buffer from, Buffer to, int count) {
        // Consistent ordering by identity hash
        Buffer first = System.identityHashCode(from) < System.identityHashCode(to) ? from : to;
        Buffer second = first == from ? to : from;

        first.lock();
        try {
            second.lock();
            try {
                return doTransfer(from, to, count);
            } finally {
                second.unlock();
            }
        } finally {
            first.unlock();
        }
    }
}
```

## Deadlock Prevention Checklist

1. **Avoid nested locks** — if you can, use one lock or lock-free structures
2. **Consistent ordering** — if you must nest, always acquire in the same order
3. **Use tryLock with timeout** — detect and recover instead of hanging
4. **Keep critical sections short** — less time holding locks = less chance of conflict
5. **Prefer concurrent collections** — ConcurrentHashMap, BlockingQueue need no external locks
6. **Monitor in production** — periodic deadlock detection with ThreadMXBean
7. **Name your threads** — makes thread dumps readable at 3 AM

## Debugging Thread Issues: The Toolkit

| Tool | Purpose |
|---|---|
| `jstack <pid>` | Thread dump — see what every thread is doing |
| `jcmd <pid> Thread.print` | Same as jstack, more options |
| `ThreadMXBean` | Programmatic deadlock detection |
| `JConsole` / `VisualVM` | GUI: thread count, deadlock detection, CPU per thread |
| `async-profiler` | Lock contention profiling (which locks are hot) |
| `-XX:+PrintConcurrentLocks` | Include ReentrantLock info in thread dumps |

## What You Learned

- **Deadlock** — threads waiting for each other in a cycle, system frozen
- **Four conditions** — mutual exclusion, hold-and-wait, no preemption, circular wait
- **Lock ordering** — always acquire locks in the same global order
- **tryLock with timeout** — detect potential deadlock and back off
- **Reduce lock scope** — don't hold multiple locks if you don't need atomicity
- **jstack** — your best friend at 3 AM
- **Livelock** — threads retry forever without progress (fix: random backoff)
- **Prevention > detection** — use lock-free structures where possible

The system is deadlock-free. For the final chapter, we'll put everything together — patterns, best practices, and the complete PulseMetrics architecture.

---

[← Chapter 12: Virtual Threads](chapter-12-virtual-threads.md) | [Chapter 14: Patterns →](chapter-14-patterns.md)

# Chapter 6: Thread Pools and Executors

[← Chapter 5: Atomics](chapter-05-atomics.md) | [Chapter 7: Futures →](chapter-07-futures.md)

---

## The Problem

The Intern's first contribution to PulseMetrics:

```java
public class EventProcessor {
    public void processEvents(List<Event> batch) {
        for (Event event : batch) {
            new Thread(() -> {
                aggregate(event);
                updateDashboard(event);
            }).start();
        }
    }
}
```

A batch of 10,000 events arrives. 10,000 threads are created. Each thread allocates ~1MB of stack space. That's 10GB of memory for thread stacks alone.

```
Exception in thread "main" java.lang.OutOfMemoryError: unable to create native thread
```

Omar at 4 AM: "The JVM crashed. Thread count hit 10,247 before OOM. Who's creating threads in a loop?"

Creating a thread is expensive: ~1ms and ~1MB of memory. At 2M events/second, you can't create a thread per event. You need a fixed pool of threads that process events from a queue.

## ExecutorService: The Thread Pool

```java
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class EventProcessor {
    // Fixed pool: 8 threads, reused for all tasks
    private final ExecutorService executor = Executors.newFixedThreadPool(8);

    public void processEvents(List<Event> batch) {
        for (Event event : batch) {
            executor.submit(() -> {
                aggregate(event);
                updateDashboard(event);
            });
        }
    }

    public void shutdown() {
        executor.shutdown();  // No new tasks; finish existing ones
    }
}
```

8 threads handle millions of events. Tasks queue up when all threads are busy. No OOM. No thread creation overhead.

## Thread Pool Types

```java
// Fixed: exactly N threads. Tasks queue when all busy.
ExecutorService fixed = Executors.newFixedThreadPool(8);

// Cached: creates threads as needed, reuses idle ones. Threads die after 60s idle.
ExecutorService cached = Executors.newCachedThreadPool();

// Single: one thread, tasks execute sequentially. Good for ordered processing.
ExecutorService single = Executors.newSingleThreadExecutor();

// Scheduled: for delayed/periodic tasks.
ScheduledExecutorService scheduled = Executors.newScheduledThreadPool(4);
```

### When to Use Which

| Pool Type | Use Case | Risk |
|---|---|---|
| Fixed | Known workload, bounded resources | Tasks queue up if pool too small |
| Cached | Bursty workloads, short tasks | Unbounded thread creation under load |
| Single | Sequential processing, event ordering | Bottleneck if tasks are slow |
| Scheduled | Periodic cleanup, heartbeats | Timer drift under heavy load |

## ThreadPoolExecutor: Full Control

`Executors.newFixedThreadPool()` is a convenience wrapper. For production, configure `ThreadPoolExecutor` directly:

```java
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;

ThreadPoolExecutor executor = new ThreadPoolExecutor(
    8,                          // corePoolSize: minimum threads kept alive
    16,                         // maximumPoolSize: max threads under load
    60, TimeUnit.SECONDS,       // keepAliveTime: idle threads above core die after this
    new LinkedBlockingQueue<>(10_000),  // work queue: bounded!
    new ThreadFactory() {       // custom thread names
        private int count = 0;
        public Thread newThread(Runnable r) {
            return new Thread(r, "ingestion-" + count++);
        }
    },
    new ThreadPoolExecutor.CallerRunsPolicy()  // rejection policy
);
```

### How ThreadPoolExecutor Decides

```
Task submitted:
  1. Threads < corePoolSize? → Create new thread
  2. Queue not full? → Add to queue
  3. Threads < maximumPoolSize? → Create new thread
  4. Queue full AND at max threads? → Rejection policy
```

## Thread Pool Sizing

### CPU-Bound Tasks (Computation)

```java
int cpuThreads = Runtime.getRuntime().availableProcessors();
// Use exactly CPU count — more threads just cause context switching
ExecutorService cpuPool = Executors.newFixedThreadPool(cpuThreads);
```

### I/O-Bound Tasks (Network, Disk)

```java
// Threads spend most time waiting. More threads = more concurrent I/O.
int ioThreads = Runtime.getRuntime().availableProcessors() * 2;
// Or use Little's Law: threads = throughput × latency
// 1000 req/sec × 0.1sec avg latency = 100 threads needed
ExecutorService ioPool = Executors.newFixedThreadPool(ioThreads);
```

### PulseMetrics Sizing

```java
// Ingestion: CPU-bound (aggregation math) — 8 cores = 8 threads
ExecutorService ingestionPool = Executors.newFixedThreadPool(8);

// Dashboard updates: I/O-bound (network writes) — 8 cores × 4 = 32 threads
ExecutorService dashboardPool = Executors.newFixedThreadPool(32);
```

Separate pools for separate workloads. A slow dashboard write shouldn't block event ingestion.

## Rejection Policies

When the queue is full and all threads are busy, what happens to new tasks?

```java
// AbortPolicy (default): throws RejectedExecutionException
new ThreadPoolExecutor.AbortPolicy()

// CallerRunsPolicy: the submitting thread runs the task itself (backpressure!)
new ThreadPoolExecutor.CallerRunsPolicy()

// DiscardPolicy: silently drops the task
new ThreadPoolExecutor.DiscardPolicy()

// DiscardOldestPolicy: drops the oldest queued task, then retries
new ThreadPoolExecutor.DiscardOldestPolicy()
```

For PulseMetrics, `CallerRunsPolicy` is ideal: if the pool is overwhelmed, the ingestion thread slows down (runs the task itself), which naturally applies backpressure to the event source.

```java
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    8, 8, 0, TimeUnit.SECONDS,
    new ArrayBlockingQueue<>(1000),  // Bounded queue!
    new ThreadPoolExecutor.CallerRunsPolicy()  // Backpressure
);
```

## Graceful Shutdown

```java
public void shutdownGracefully(ExecutorService executor) {
    executor.shutdown();  // Stop accepting new tasks

    try {
        // Wait for running tasks to finish
        if (!executor.awaitTermination(30, TimeUnit.SECONDS)) {
            executor.shutdownNow();  // Interrupt running tasks
            if (!executor.awaitTermination(10, TimeUnit.SECONDS)) {
                System.err.println("Pool did not terminate");
            }
        }
    } catch (InterruptedException e) {
        executor.shutdownNow();
        Thread.currentThread().interrupt();
    }
}
```

- `shutdown()` — no new tasks, finish what's running
- `shutdownNow()` — interrupt running tasks, return queued tasks
- `awaitTermination()` — block until all tasks finish or timeout

## Scheduled Tasks

```java
ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(2);

// Run once after 5 seconds
scheduler.schedule(() -> cleanupExpiredSessions(), 5, TimeUnit.SECONDS);

// Run every 10 seconds (fixed rate — next starts 10s after previous start)
scheduler.scheduleAtFixedRate(
    () -> publishMetrics(),
    0,    // initial delay
    10,   // period
    TimeUnit.SECONDS
);

// Run with 10s delay between end of one and start of next
scheduler.scheduleWithFixedDelay(
    () -> compactStorage(),
    0,    // initial delay
    10,   // delay after completion
    TimeUnit.SECONDS
);
```

`scheduleAtFixedRate`: if the task takes 3s, next run starts at 10s, 20s, 30s...
`scheduleWithFixedDelay`: if the task takes 3s, next run starts at 13s, 26s, 39s...

## PulseMetrics: Production Pipeline

```java
public class PipelineManager {
    private final ExecutorService ingestionPool;
    private final ExecutorService dashboardPool;
    private final ScheduledExecutorService scheduler;

    public PipelineManager() {
        int cores = Runtime.getRuntime().availableProcessors();

        ingestionPool = new ThreadPoolExecutor(
            cores, cores, 0, TimeUnit.SECONDS,
            new ArrayBlockingQueue<>(50_000),
            r -> new Thread(r, "ingest-" + Thread.currentThread().threadId()),
            new ThreadPoolExecutor.CallerRunsPolicy()
        );

        dashboardPool = new ThreadPoolExecutor(
            cores * 2, cores * 4, 60, TimeUnit.SECONDS,
            new LinkedBlockingQueue<>(1000),
            r -> new Thread(r, "dashboard-" + Thread.currentThread().threadId()),
            new ThreadPoolExecutor.AbortPolicy()
        );

        scheduler = Executors.newScheduledThreadPool(2);
        scheduler.scheduleAtFixedRate(this::reportPoolStats, 0, 5, TimeUnit.SECONDS);
    }

    public void ingest(Event event) {
        ingestionPool.submit(() -> {
            aggregate(event);
            metrics.record(event);
        });
    }

    public void updateDashboard(String dashboardId, Snapshot data) {
        dashboardPool.submit(() -> pushToDashboard(dashboardId, data));
    }

    private void reportPoolStats() {
        ThreadPoolExecutor pool = (ThreadPoolExecutor) ingestionPool;
        System.out.printf("Pool: active=%d, queued=%d, completed=%d%n",
            pool.getActiveCount(),
            pool.getQueue().size(),
            pool.getCompletedTaskCount()
        );
    }

    public void shutdown() {
        scheduler.shutdown();
        ingestionPool.shutdown();
        dashboardPool.shutdown();
    }
}
```

## Common Mistakes

### 1. Unbounded Queue with Fixed Pool

```java
// DANGEROUS: LinkedBlockingQueue is unbounded by default
Executors.newFixedThreadPool(8);  // Uses new LinkedBlockingQueue<>() — no limit!
```

If tasks arrive faster than 8 threads can process them, the queue grows forever → OOM. Always use a bounded queue in production.

### 2. Not Handling Exceptions

```java
executor.submit(() -> {
    throw new RuntimeException("oops");  // Silently swallowed!
});
```

Exceptions in submitted tasks are swallowed unless you check the `Future`. Use `execute()` instead of `submit()` if you don't need the Future, or wrap tasks:

```java
executor.submit(() -> {
    try {
        riskyWork();
    } catch (Exception e) {
        logger.error("Task failed", e);
    }
});
```

### 3. Using CachedThreadPool for Unbounded Work

```java
// DANGEROUS: creates unlimited threads under load
ExecutorService pool = Executors.newCachedThreadPool();
for (Event e : millionsOfEvents) {
    pool.submit(() -> process(e));  // Could create millions of threads
}
```

## What You Learned

- **ExecutorService** — submit tasks to a thread pool instead of creating threads
- **ThreadPoolExecutor** — full control over core/max size, queue, rejection
- **Pool sizing** — CPU-bound: core count. I/O-bound: core count × multiplier
- **Rejection policies** — CallerRunsPolicy for backpressure
- **Bounded queues** — prevent OOM from unbounded task accumulation
- **Graceful shutdown** — shutdown() → awaitTermination() → shutdownNow()
- **Separate pools** — isolate workloads so slow I/O doesn't block computation

The pool processes events efficiently. But how do we get results back from submitted tasks? We need Futures.

---

[← Chapter 5: Atomics](chapter-05-atomics.md) | [Chapter 7: Futures →](chapter-07-futures.md)

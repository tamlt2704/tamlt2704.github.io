# Chapter 14: Concurrency Patterns

[← Chapter 13: Deadlocks](chapter-13-deadlocks.md) | [Chapter 0: Overview →](chapter-00-overview.md)

---

## The Story So Far

Over 13 chapters, you rebuilt PulseMetrics from a single-threaded pipeline to a concurrent system handling 2M events/second. This final chapter covers the patterns that tie everything together — and the complete architecture.

Nadia: "Show me the architecture. How does it all fit?"

## Pattern 1: Double-Checked Locking

Lazy initialization that's both thread-safe and fast:

```java
public class ConnectionPool {
    private static volatile ConnectionPool instance;

    public static ConnectionPool getInstance() {
        if (instance == null) {                    // First check: no lock
            synchronized (ConnectionPool.class) {
                if (instance == null) {            // Second check: with lock
                    instance = new ConnectionPool();
                }
            }
        }
        return instance;
    }

    private ConnectionPool() {
        // Expensive initialization
    }
}
```

Why it works:
- First check avoids the lock in the common case (instance already exists)
- `synchronized` ensures only one thread creates the instance
- `volatile` prevents seeing a partially constructed object

Modern alternative — simpler and just as safe:

```java
public class ConnectionPool {
    private static class Holder {
        static final ConnectionPool INSTANCE = new ConnectionPool();
    }

    public static ConnectionPool getInstance() {
        return Holder.INSTANCE;  // Class loaded on first access — thread-safe by JLS
    }
}
```

The JVM guarantees class initialization is thread-safe. No volatile, no synchronized, no double-checking.

## Pattern 2: Thread-Local Storage

Give each thread its own copy of a resource — no sharing, no synchronization:

```java
public class EventParser {
    // SimpleDateFormat is NOT thread-safe. One per thread.
    private static final ThreadLocal<SimpleDateFormat> dateFormat =
        ThreadLocal.withInitial(() -> new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss"));

    public Event parse(String raw) {
        SimpleDateFormat fmt = dateFormat.get();  // Each thread gets its own instance
        Date timestamp = fmt.parse(raw.substring(0, 19));
        return new Event(timestamp, raw);
    }
}
```

### Thread-Local for Request Context

```java
public class RequestContext {
    private static final ThreadLocal<String> traceId = new ThreadLocal<>();
    private static final ThreadLocal<String> userId = new ThreadLocal<>();

    public static void set(String trace, String user) {
        traceId.set(trace);
        userId.set(user);
    }

    public static String getTraceId() { return traceId.get(); }
    public static String getUserId() { return userId.get(); }

    public static void clear() {
        traceId.remove();  // IMPORTANT: prevent memory leaks in thread pools
        userId.remove();
    }
}

// Usage in a thread pool
executor.submit(() -> {
    RequestContext.set(trace, user);
    try {
        processEvent();  // Any code can access RequestContext.getTraceId()
    } finally {
        RequestContext.clear();  // Always clean up in pooled threads!
    }
});
```

**Critical**: always call `remove()` when using ThreadLocal with thread pools. Pooled threads are reused — stale values leak between tasks.

### Scoped Values (Java 21 Preview) — ThreadLocal Replacement

```java
import jdk.incubator.concurrent.ScopedValue;

public class RequestContext {
    static final ScopedValue<String> TRACE_ID = ScopedValue.newInstance();

    public static void processRequest(String traceId, Event event) {
        ScopedValue.where(TRACE_ID, traceId).run(() -> {
            // TRACE_ID is available here and in all called methods
            enrich(event);
            aggregate(event);
            // Automatically cleaned up when scope exits — no leaks possible
        });
    }
}
```

Scoped values are immutable, automatically scoped, and work well with virtual threads.

## Pattern 3: Producer-Consumer with Batching

The core pattern of PulseMetrics — decouple ingestion from processing:

```java
public class BatchingPipeline {
    private final BlockingQueue<Event> queue = new ArrayBlockingQueue<>(100_000);
    private final int batchSize = 256;
    private final Duration maxWait = Duration.ofMillis(50);

    // Producers: many threads, non-blocking
    public boolean submit(Event event) {
        return queue.offer(event);  // Non-blocking, drops on overflow
    }

    // Consumer: batches events for efficient processing
    public void startConsumer() {
        Thread.startVirtualThread(() -> {
            List<Event> batch = new ArrayList<>(batchSize);
            while (!Thread.currentThread().isInterrupted()) {
                try {
                    batch.clear();
                    // Wait for first event (up to maxWait)
                    Event first = queue.poll(maxWait.toMillis(), TimeUnit.MILLISECONDS);
                    if (first == null) continue;  // Timeout — flush empty batch or skip

                    batch.add(first);
                    queue.drainTo(batch, batchSize - 1);  // Grab more without blocking

                    processBatch(batch);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
        });
    }
}
```

Batching amortizes per-event overhead (network calls, disk writes, lock acquisitions).

## Pattern 4: Stripe Locking

When one lock is too coarse but per-element locking is too expensive:

```java
public class StripedMap<K, V> {
    private static final int STRIPE_COUNT = 16;
    private final ReentrantLock[] locks = new ReentrantLock[STRIPE_COUNT];
    private final Map<K, V>[] buckets;

    @SuppressWarnings("unchecked")
    public StripedMap() {
        buckets = new HashMap[STRIPE_COUNT];
        for (int i = 0; i < STRIPE_COUNT; i++) {
            locks[i] = new ReentrantLock();
            buckets[i] = new HashMap<>();
        }
    }

    private int stripeFor(K key) {
        return Math.abs(key.hashCode() % STRIPE_COUNT);
    }

    public void put(K key, V value) {
        int stripe = stripeFor(key);
        locks[stripe].lock();
        try {
            buckets[stripe].put(key, value);
        } finally {
            locks[stripe].unlock();
        }
    }

    public V get(K key) {
        int stripe = stripeFor(key);
        locks[stripe].lock();
        try {
            return buckets[stripe].get(key);
        } finally {
            locks[stripe].unlock();
        }
    }
}
```

16 stripes = 16x less contention than a single lock. This is how `ConcurrentHashMap` works internally.

## Pattern 5: Event Loop (Single-Writer)

Eliminate synchronization by funneling all writes through one thread:

```java
public class MetricsAggregator {
    private final BlockingQueue<MetricEvent> inbox = new LinkedBlockingQueue<>();

    // State: only accessed by the event loop thread — no synchronization needed!
    private long totalEvents = 0;
    private final Map<String, Long> counters = new HashMap<>();

    public MetricsAggregator() {
        Thread.startVirtualThread(this::eventLoop);
    }

    // Called by many threads — just enqueue
    public void record(String source) {
        inbox.offer(new MetricEvent(source));
    }

    // Single thread processes all events — no locks needed
    private void eventLoop() {
        while (!Thread.currentThread().isInterrupted()) {
            try {
                MetricEvent event = inbox.take();
                totalEvents++;
                counters.merge(event.source(), 1L, Long::sum);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }

    // Snapshot: send a request through the event loop
    public CompletableFuture<Map<String, Long>> getSnapshot() {
        CompletableFuture<Map<String, Long>> future = new CompletableFuture<>();
        inbox.offer(new SnapshotRequest(future));
        return future;
    }

    private record MetricEvent(String source) {}
    private record SnapshotRequest(CompletableFuture<Map<String, Long>> future) {}
}
```

The single-writer pattern (also called the actor model) eliminates all synchronization on the mutable state. Reads go through the same queue to ensure consistency.

## Pattern 6: Circuit Breaker

Protect the system when a dependency fails:

```java
public class CircuitBreaker {
    private enum State { CLOSED, OPEN, HALF_OPEN }

    private final AtomicReference<State> state = new AtomicReference<>(State.CLOSED);
    private final AtomicInteger failureCount = new AtomicInteger(0);
    private final int threshold = 5;
    private volatile long lastFailureTime = 0;
    private final long resetTimeout = 30_000;  // 30 seconds

    public <T> T execute(Callable<T> action, Callable<T> fallback) throws Exception {
        if (state.get() == State.OPEN) {
            if (System.currentTimeMillis() - lastFailureTime > resetTimeout) {
                state.set(State.HALF_OPEN);  // Try one request
            } else {
                return fallback.call();  // Circuit open — use fallback
            }
        }

        try {
            T result = action.call();
            reset();
            return result;
        } catch (Exception e) {
            recordFailure();
            return fallback.call();
        }
    }

    private void recordFailure() {
        lastFailureTime = System.currentTimeMillis();
        if (failureCount.incrementAndGet() >= threshold) {
            state.set(State.OPEN);
        }
    }

    private void reset() {
        failureCount.set(0);
        state.set(State.CLOSED);
    }
}
```

## The Complete PulseMetrics Architecture

```java
public class PulseMetrics {
    // Layer 1: Ingestion (Virtual Threads)
    private final ExecutorService connectionPool = Executors.newVirtualThreadPerTaskExecutor();

    // Layer 2: Buffering (Blocking Queues)
    private final BlockingQueue<Event> rawEvents = new ArrayBlockingQueue<>(500_000);

    // Layer 3: Enrichment (Bounded Thread Pool + Semaphore)
    private final ExecutorService enrichmentPool = Executors.newFixedThreadPool(32);
    private final Semaphore enrichmentPermits = new Semaphore(100);
    private final BlockingQueue<EnrichedEvent> enrichedEvents = new ArrayBlockingQueue<>(200_000);

    // Layer 4: Aggregation (Lock-free)
    private final ConcurrentHashMap<String, LongAdder> counters = new ConcurrentHashMap<>();
    private final LongAdder totalEvents = new LongAdder();
    private final LongAccumulator maxLatency = new LongAccumulator(Long::max, 0);

    // Layer 5: Dashboard Push (Virtual Threads)
    private final CopyOnWriteArrayList<DashboardConnection> dashboards = new CopyOnWriteArrayList<>();

    // Coordination
    private final CountDownLatch systemReady = new CountDownLatch(3);
    private volatile boolean running = true;

    public void start() throws InterruptedException {
        // Phase 1: Initialize infrastructure
        CompletableFuture.runAsync(this::initDatabase).thenRun(systemReady::countDown);
        CompletableFuture.runAsync(this::initCache).thenRun(systemReady::countDown);
        CompletableFuture.runAsync(this::initGeoService).thenRun(systemReady::countDown);

        systemReady.await(30, TimeUnit.SECONDS);
        System.out.println("System ready. Starting pipeline.");

        // Phase 2: Start processing stages
        startIngestionConsumers(8);
        startEnrichmentConsumers(16);
        startDashboardPusher();
        startMetricsReporter();
    }

    // Ingestion: accept connections, buffer events
    public void acceptConnection(Socket client) {
        connectionPool.submit(() -> {
            try (client;
                 var reader = new BufferedReader(new InputStreamReader(client.getInputStream()))) {
                String line;
                while (running && (line = reader.readLine()) != null) {
                    Event event = Event.parse(line);
                    if (!rawEvents.offer(event)) {
                        // Backpressure: queue full, drop event
                        totalEvents.increment();  // Count it even if dropped
                    }
                }
            } catch (IOException e) { /* connection closed */ }
        });
    }

    // Enrichment: parallel with rate limiting
    private void startEnrichmentConsumers(int count) {
        for (int i = 0; i < count; i++) {
            enrichmentPool.submit(() -> {
                while (running) {
                    try {
                        Event raw = rawEvents.poll(1, TimeUnit.SECONDS);
                        if (raw == null) continue;

                        enrichmentPermits.acquire();
                        try {
                            EnrichedEvent enriched = enrich(raw);
                            enrichedEvents.put(enriched);
                        } finally {
                            enrichmentPermits.release();
                        }
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                        break;
                    }
                }
            });
        }
    }

    // Aggregation: lock-free, batched
    private void startIngestionConsumers(int count) {
        for (int i = 0; i < count; i++) {
            Thread.startVirtualThread(() -> {
                List<EnrichedEvent> batch = new ArrayList<>(256);
                while (running) {
                    try {
                        batch.clear();
                        EnrichedEvent first = enrichedEvents.poll(1, TimeUnit.SECONDS);
                        if (first == null) continue;
                        batch.add(first);
                        enrichedEvents.drainTo(batch, 255);

                        for (EnrichedEvent e : batch) {
                            totalEvents.increment();
                            maxLatency.accumulate(e.latency());
                            counters.computeIfAbsent(e.source(), k -> new LongAdder()).increment();
                        }
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                        break;
                    }
                }
            });
        }
    }

    // Dashboard: push snapshots every second
    private void startDashboardPusher() {
        Executors.newSingleThreadScheduledExecutor().scheduleAtFixedRate(() -> {
            Snapshot snap = new Snapshot(totalEvents.sum(), maxLatency.get(), snapshotCounters());
            for (DashboardConnection dc : dashboards) {
                Thread.startVirtualThread(() -> dc.push(snap));
            }
        }, 0, 1, TimeUnit.SECONDS);
    }

    private Map<String, Long> snapshotCounters() {
        Map<String, Long> result = new HashMap<>();
        counters.forEach((k, v) -> result.put(k, v.sum()));
        return result;
    }

    public void shutdown() {
        running = false;
        connectionPool.shutdown();
        enrichmentPool.shutdown();
    }
}
```

## The Concurrency Decision Tree

```
Need to share mutable state?
├── No → No synchronization needed (immutable objects, thread confinement)
├── Yes, simple counter → LongAdder (high contention) or AtomicLong (low contention)
├── Yes, key-value → ConcurrentHashMap
├── Yes, producer-consumer → BlockingQueue
├── Yes, compound operation → synchronized or ReentrantLock
│   ├── Read-heavy → ReadWriteLock or StampedLock
│   ├── Need timeout → ReentrantLock.tryLock()
│   └── Simple → synchronized
└── Yes, but can redesign → Single-writer pattern (event loop / actor)

Need to coordinate threads?
├── Wait for N tasks → CountDownLatch
├── Sync at barrier, repeat → CyclicBarrier
├── Limit concurrency → Semaphore
└── Multi-phase → Phaser

Need async results?
├── Simple → Future
├── Chaining/composition → CompletableFuture
└── Fan-out with cancellation → StructuredTaskScope

Thread model?
├── CPU-bound → Fixed platform thread pool (core count)
├── I/O-bound, moderate → Fixed platform thread pool (core count × N)
├── I/O-bound, massive → Virtual threads
└── Recursive divide-and-conquer → ForkJoinPool
```

## Rules of Thumb

1. **Immutability is the best synchronization** — if it can't change, it can't race
2. **Prefer higher-level abstractions** — BlockingQueue over wait/notify, CompletableFuture over raw threads
3. **Measure before optimizing** — profile lock contention before going lock-free
4. **One writer is simpler than many** — single-writer pattern eliminates most bugs
5. **Bound everything** — queues, thread pools, connection counts. Unbounded = OOM
6. **Name your threads** — you'll read thread dumps at 3 AM
7. **Test with more threads than cores** — forces context switches, exposes races
8. **volatile for flags, atomics for counters, locks for compound ops**

## What You Learned (The Whole Course)

| Chapter | Concept | When to Use |
|---|---|---|
| 1 | Threads | Independent tasks |
| 2 | synchronized | Simple mutual exclusion |
| 3 | volatile | Visibility flags, single-writer |
| 4 | ReentrantLock | tryLock, fairness, conditions |
| 5 | Atomics/CAS | Lock-free counters |
| 6 | Executors | Thread pool management |
| 7 | CompletableFuture | Async pipelines |
| 8 | BlockingQueue | Producer-consumer buffering |
| 9 | ConcurrentHashMap | Concurrent key-value |
| 10 | Latches/Barriers | Phase coordination |
| 11 | Fork/Join | Recursive parallelism |
| 12 | Virtual Threads | Massive I/O concurrency |
| 13 | Deadlocks | Prevention and detection |
| 14 | Patterns | Putting it all together |

PulseMetrics handles 2M events/second with 50ms latency. Dashboards update in real-time for 100K connections. The system is concurrent, correct, and debuggable.

Nadia: "Ship it."

---

[← Chapter 13: Deadlocks](chapter-13-deadlocks.md) | [Chapter 0: Overview →](chapter-00-overview.md)

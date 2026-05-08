# Chapter 8: Blocking Queues and Backpressure

[← Chapter 7: Futures](chapter-07-futures.md) | [Chapter 9: Concurrent Collections →](chapter-09-concurrent-maps.md)

---

## The Problem

PulseMetrics ingests 2M events/second. The enrichment pipeline (Chapter 7) processes events at 1.5M/second on a good day. During traffic spikes, ingestion outpaces processing:

```java
public class Pipeline {
    private final List<Event> buffer = new ArrayList<>();  // Shared buffer

    // Producer: ingestion thread
    public void ingest(Event event) {
        synchronized (buffer) {
            buffer.add(event);  // Grows without bound
        }
    }

    // Consumer: processing thread
    public void process() {
        synchronized (buffer) {
            if (!buffer.isEmpty()) {
                Event event = buffer.remove(0);  // O(n) removal!
                enrich(event);
            }
        }
    }
}
```

Problems:
1. `ArrayList` grows without bound → OOM during spikes
2. `remove(0)` is O(n) — shifts all elements
3. Producer and consumer fight over the same lock
4. Consumer busy-waits when buffer is empty

After a 30-minute traffic spike, the buffer holds 18 million events, consuming 4GB of heap. GC pauses spike to 2 seconds. Dashboards freeze.

Omar: "Heap usage hit 95%. Full GC every 3 seconds. The pipeline is drowning."

## BlockingQueue: The Producer-Consumer Bridge

`BlockingQueue` solves all four problems:

```java
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;

public class Pipeline {
    // Bounded: holds at most 10,000 events
    private final BlockingQueue<Event> queue = new ArrayBlockingQueue<>(10_000);

    // Producer: blocks if queue is full (backpressure!)
    public void ingest(Event event) throws InterruptedException {
        queue.put(event);  // Blocks until space available
    }

    // Consumer: blocks if queue is empty (no busy-waiting!)
    public void process() throws InterruptedException {
        Event event = queue.take();  // Blocks until event available
        enrich(event);
    }
}
```

- **Bounded**: can't grow past 10,000 → no OOM
- **Blocking**: producers wait when full, consumers wait when empty
- **Thread-safe**: no external synchronization needed
- **O(1)**: array-backed circular buffer

## BlockingQueue Operations

| | Throws | Returns Special Value | Blocks | Times Out |
|---|---|---|---|---|
| Insert | `add(e)` | `offer(e)` → false | `put(e)` | `offer(e, time, unit)` |
| Remove | `remove()` | `poll()` → null | `take()` | `poll(time, unit)` |
| Examine | `element()` | `peek()` → null | — | — |

Choose based on your backpressure strategy:
- `put()`/`take()` — block forever (simple producer-consumer)
- `offer(timeout)`/`poll(timeout)` — block with deadline (latency-sensitive)
- `offer()`/`poll()` — non-blocking (drop or buffer elsewhere)

## Backpressure Strategies

### Strategy 1: Block the Producer (put)

```java
queue.put(event);  // Producer slows down when queue is full
```

The producer thread blocks until space is available. This naturally slows ingestion to match processing speed. Simple and effective.

### Strategy 2: Drop on Overflow (offer)

```java
if (!queue.offer(event)) {
    metrics.recordDropped(event);
    // Event is lost — acceptable for metrics, not for billing
}
```

Never blocks. Events are dropped during overload. Good for best-effort metrics.

### Strategy 3: Timeout and Redirect (offer with timeout)

```java
if (!queue.offer(event, 50, TimeUnit.MILLISECONDS)) {
    // Couldn't enqueue in 50ms — send to overflow storage
    overflowStore.save(event);
}
```

Try the fast path; fall back to durable storage if the pipeline is backed up.

## BlockingQueue Implementations

### ArrayBlockingQueue

```java
// Fixed-size array, FIFO, optional fairness
BlockingQueue<Event> queue = new ArrayBlockingQueue<>(10_000);
BlockingQueue<Event> fair = new ArrayBlockingQueue<>(10_000, true);  // FIFO lock ordering
```

- Bounded (you specify capacity)
- Single lock for put and take (lower throughput under contention)
- Predictable memory usage

### LinkedBlockingQueue

```java
// Optionally bounded, separate locks for put/take
BlockingQueue<Event> queue = new LinkedBlockingQueue<>(10_000);  // Bounded
BlockingQueue<Event> unbounded = new LinkedBlockingQueue<>();     // DANGEROUS: no limit
```

- Separate locks for head and tail → higher throughput
- Each element allocates a Node object → more GC pressure
- **Always specify capacity** — unbounded = OOM risk

### PriorityBlockingQueue

```java
// Unbounded, elements ordered by priority
BlockingQueue<Event> queue = new PriorityBlockingQueue<>(100,
    Comparator.comparingInt(Event::priority).reversed()
);
```

- High-priority events processed first
- Unbounded (only blocks on take when empty, never on put)
- Not FIFO — ordering is by priority

### LinkedTransferQueue

```java
// Unbounded, optimized for handoff scenarios
TransferQueue<Event> queue = new LinkedTransferQueue<>();

// Producer can wait until a consumer takes the item
queue.transfer(event);  // Blocks until a consumer takes it

// Or try without blocking
queue.tryTransfer(event);  // Returns false if no consumer waiting
```

Direct handoff: the producer waits until a consumer is ready. Zero buffering.

## The Producer-Consumer Pattern

```java
public class EventPipeline {
    private final BlockingQueue<Event> queue = new ArrayBlockingQueue<>(50_000);
    private final int numConsumers = 8;
    private volatile boolean running = true;

    // Multiple producers
    public void startProducers(int count) {
        for (int i = 0; i < count; i++) {
            new Thread(() -> {
                while (running) {
                    Event event = receiveFromNetwork();
                    try {
                        if (!queue.offer(event, 100, TimeUnit.MILLISECONDS)) {
                            metrics.recordBackpressure();
                        }
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                        break;
                    }
                }
            }, "producer-" + i).start();
        }
    }

    // Multiple consumers
    public void startConsumers() {
        for (int i = 0; i < numConsumers; i++) {
            new Thread(() -> {
                while (running) {
                    try {
                        Event event = queue.poll(1, TimeUnit.SECONDS);
                        if (event != null) {
                            process(event);
                        }
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                        break;
                    }
                }
            }, "consumer-" + i).start();
        }
    }

    public void shutdown() {
        running = false;
    }
}
```

Using `poll(timeout)` instead of `take()` lets consumers check the `running` flag periodically for graceful shutdown.

## Poison Pill: Clean Shutdown

How do consumers know when to stop? Send a special "poison pill" message:

```java
private static final Event POISON_PILL = new Event("SHUTDOWN", null, -1);

public void shutdown() throws InterruptedException {
    // Send one poison pill per consumer
    for (int i = 0; i < numConsumers; i++) {
        queue.put(POISON_PILL);
    }
}

// Consumer loop
while (true) {
    Event event = queue.take();
    if (event == POISON_PILL) break;  // Clean exit
    process(event);
}
```

Each consumer takes one poison pill and exits. No `volatile` flag needed.

## Batch Draining for Throughput

Taking one event at a time has overhead. Drain multiple events in one call:

```java
public void consumeBatch() throws InterruptedException {
    List<Event> batch = new ArrayList<>(256);

    // Block until at least one event is available
    Event first = queue.take();
    batch.add(first);

    // Drain up to 255 more without blocking
    queue.drainTo(batch, 255);

    // Process entire batch — amortizes overhead
    processBatch(batch);
}
```

`drainTo()` is non-blocking — it takes whatever's available up to the limit. Combined with one blocking `take()`, you get efficient batching without busy-waiting.

## PulseMetrics: Multi-Stage Pipeline

```java
public class MultiStagePipeline {
    private final BlockingQueue<Event> rawQueue = new ArrayBlockingQueue<>(100_000);
    private final BlockingQueue<EnrichedEvent> enrichedQueue = new ArrayBlockingQueue<>(50_000);
    private final BlockingQueue<AggregatedResult> outputQueue = new ArrayBlockingQueue<>(10_000);

    // Stage 1: Ingestion → Raw Queue
    public void ingest(Event event) {
        if (!rawQueue.offer(event)) {
            metrics.recordDrop("ingestion_overflow");
        }
    }

    // Stage 2: Raw Queue → Enrichment → Enriched Queue
    public void startEnrichers(int count) {
        for (int i = 0; i < count; i++) {
            Thread t = new Thread(() -> {
                while (!Thread.currentThread().isInterrupted()) {
                    try {
                        Event raw = rawQueue.poll(1, TimeUnit.SECONDS);
                        if (raw != null) {
                            EnrichedEvent enriched = enrich(raw);
                            enrichedQueue.put(enriched);  // Backpressure to enrichers
                        }
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                }
            }, "enricher-" + i);
            t.start();
        }
    }

    // Stage 3: Enriched Queue → Aggregation → Output Queue
    public void startAggregators(int count) {
        for (int i = 0; i < count; i++) {
            Thread t = new Thread(() -> {
                List<EnrichedEvent> batch = new ArrayList<>(100);
                while (!Thread.currentThread().isInterrupted()) {
                    try {
                        batch.clear();
                        EnrichedEvent first = enrichedQueue.take();
                        batch.add(first);
                        enrichedQueue.drainTo(batch, 99);

                        AggregatedResult result = aggregate(batch);
                        outputQueue.put(result);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                }
            }, "aggregator-" + i);
            t.start();
        }
    }

    // Monitoring
    public void printQueueDepths() {
        System.out.printf("raw=%d enriched=%d output=%d%n",
            rawQueue.size(), enrichedQueue.size(), outputQueue.size());
    }
}
```

Three stages, each with its own queue and thread pool. Backpressure propagates naturally: if aggregation is slow, the enriched queue fills up, enrichers block on `put()`, raw queue fills up, ingestion starts dropping.

## Monitoring Queue Health

```java
ScheduledExecutorService monitor = Executors.newSingleThreadScheduledExecutor();
monitor.scheduleAtFixedRate(() -> {
    int size = queue.size();
    int capacity = 100_000;
    double utilization = (double) size / capacity;

    if (utilization > 0.8) {
        logger.warn("Queue at {}% capacity ({}/{})", 
            (int)(utilization * 100), size, capacity);
        alerting.fire("queue_near_full");
    }
}, 0, 1, TimeUnit.SECONDS);
```

## What You Learned

- **BlockingQueue** — thread-safe bounded buffer with blocking put/take
- **Backpressure** — bounded queues naturally slow producers when consumers can't keep up
- **put() vs offer()** — block forever vs fail fast (choose your strategy)
- **ArrayBlockingQueue** — fixed size, predictable memory
- **LinkedBlockingQueue** — higher throughput (separate locks), specify capacity!
- **drainTo()** — batch consumption for throughput
- **Poison pill** — clean shutdown signal through the queue
- **Multi-stage pipelines** — queues between stages decouple throughput

The pipeline handles backpressure. But we're using `HashMap` for aggregation state, and multiple threads are getting `ConcurrentModificationException`. We need concurrent collections.

---

[← Chapter 7: Futures](chapter-07-futures.md) | [Chapter 9: Concurrent Collections →](chapter-09-concurrent-maps.md)

# Chapter 10: Latches, Barriers, and Semaphores

[← Chapter 9: Concurrent Collections](chapter-09-concurrent-maps.md) | [Chapter 11: Fork/Join →](chapter-11-forkjoin.md)

---

## The Problem

PulseMetrics has a multi-phase startup sequence:

```java
public class PipelineStartup {
    public void start() {
        // Phase 1: Connect to databases (3 connections in parallel)
        connectToTimeSeries();   // 2 seconds
        connectToUserDB();       // 1.5 seconds
        connectToGeoCache();     // 800ms

        // Phase 2: Load reference data (only after ALL connections are up)
        loadGeoMappings();       // Needs geoCache connection
        loadUserSegments();      // Needs userDB connection

        // Phase 3: Start ingestion (only after reference data is loaded)
        startIngestionThreads();
    }
}
```

The Intern parallelized it:

```java
new Thread(() -> connectToTimeSeries()).start();
new Thread(() -> connectToUserDB()).start();
new Thread(() -> connectToGeoCache()).start();
// How do we wait for ALL THREE before starting Phase 2?
Thread.sleep(5000);  // "Should be enough time" — The Intern
```

It wasn't enough time. On a cold Monday morning, the geo cache took 6 seconds to connect. Phase 2 started before Phase 1 finished. `NullPointerException` everywhere.

Nadia: "We need a gate. Phase 2 doesn't start until all Phase 1 tasks signal completion. Not a sleep. A guarantee."

## CountDownLatch: One-Time Gate

A `CountDownLatch` starts at a count and blocks threads until the count reaches zero:

```java
import java.util.concurrent.CountDownLatch;

public class PipelineStartup {
    public void start() throws InterruptedException {
        CountDownLatch connectionsReady = new CountDownLatch(3);  // 3 connections

        // Phase 1: Connect in parallel
        new Thread(() -> {
            connectToTimeSeries();
            connectionsReady.countDown();  // 3 → 2
        }).start();

        new Thread(() -> {
            connectToUserDB();
            connectionsReady.countDown();  // 2 → 1
        }).start();

        new Thread(() -> {
            connectToGeoCache();
            connectionsReady.countDown();  // 1 → 0
        }).start();

        // Block until count reaches 0 (all 3 connected)
        connectionsReady.await();  // Blocks until count == 0

        // Phase 2: Safe to proceed — all connections are up
        loadGeoMappings();
        loadUserSegments();

        // Phase 3
        startIngestionThreads();
    }
}
```

`countDown()` decrements the count. `await()` blocks until count hits zero. Once zero, the latch is open forever — it can't be reset.

### With Timeout

```java
if (!connectionsReady.await(30, TimeUnit.SECONDS)) {
    throw new StartupException("Connections not ready after 30s");
}
```

## CountDownLatch: Starting Gun Pattern

A latch can also synchronize a start signal — all threads wait, then go simultaneously:

```java
public class LoadTest {
    public void runLoadTest(int numClients) throws InterruptedException {
        CountDownLatch startGun = new CountDownLatch(1);    // All wait for this
        CountDownLatch allDone = new CountDownLatch(numClients);  // Wait for all to finish

        for (int i = 0; i < numClients; i++) {
            new Thread(() -> {
                try {
                    startGun.await();  // All threads wait here
                    // Simulate client traffic
                    sendRequests();
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                } finally {
                    allDone.countDown();
                }
            }).start();
        }

        System.out.println("All threads ready. Starting load test...");
        startGun.countDown();  // Release all threads simultaneously

        allDone.await();  // Wait for all to finish
        System.out.println("Load test complete.");
    }
}
```

## CyclicBarrier: Reusable Synchronization Point

Unlike `CountDownLatch` (one-shot), `CyclicBarrier` resets after all threads arrive — useful for iterative algorithms:

```java
import java.util.concurrent.CyclicBarrier;

public class ParallelAggregation {
    private final int numWorkers = 4;
    private final CyclicBarrier barrier = new CyclicBarrier(numWorkers, () -> {
        // Runs when all threads arrive — merge partial results
        mergePartialResults();
    });

    public void process() {
        for (int i = 0; i < numWorkers; i++) {
            int workerId = i;
            new Thread(() -> {
                while (hasMoreData()) {
                    // Phase 1: Each worker processes its partition
                    processPartition(workerId);

                    try {
                        barrier.await();  // Wait for all workers
                        // Barrier action (mergePartialResults) runs here
                        // Then all threads continue
                    } catch (Exception e) {
                        Thread.currentThread().interrupt();
                        break;
                    }

                    // Phase 2: All workers see merged results
                    updateLocalState(workerId);

                    try {
                        barrier.await();  // Sync again before next iteration
                    } catch (Exception e) {
                        Thread.currentThread().interrupt();
                        break;
                    }
                }
            }).start();
        }
    }
}
```

Key differences from CountDownLatch:
- **Reusable**: resets automatically after all threads arrive
- **Barrier action**: optional Runnable that executes when all threads arrive
- **All threads wait**: every thread both counts down AND waits (latch separates counters from waiters)

## Phaser: Flexible Multi-Phase Coordination

`Phaser` is a more flexible barrier that supports dynamic registration and multiple phases:

```java
import java.util.concurrent.Phaser;

public class MultiPhaseStartup {
    public void start() {
        Phaser phaser = new Phaser(1);  // Register self (the coordinator)

        // Phase 0: Start connections
        for (int i = 0; i < 3; i++) {
            phaser.register();  // Register each worker
            new Thread(() -> {
                connectToDatabase();
                phaser.arriveAndAwaitAdvance();  // Signal done, wait for phase 1

                loadReferenceData();
                phaser.arriveAndAwaitAdvance();  // Signal done, wait for phase 2

                startProcessing();
                phaser.arriveAndDeregister();    // Done — leave the phaser
            }).start();
        }

        // Coordinator advances through phases
        phaser.arriveAndAwaitAdvance();  // Wait for Phase 0 (connections)
        System.out.println("All connections up");

        phaser.arriveAndAwaitAdvance();  // Wait for Phase 1 (reference data)
        System.out.println("Reference data loaded");

        phaser.arriveAndDeregister();    // Coordinator leaves
        System.out.println("Processing started");
    }
}
```

Phaser advantages:
- **Dynamic registration**: threads can join/leave at any phase
- **Phase numbering**: `phaser.getPhase()` tells you which phase you're in
- **Termination**: phaser terminates when all parties deregister

## Semaphore: Limiting Concurrency

A `Semaphore` controls how many threads can access a resource simultaneously:

```java
import java.util.concurrent.Semaphore;

public class RateLimitedClient {
    // Allow at most 10 concurrent connections to the external API
    private final Semaphore permits = new Semaphore(10);

    public Response query(Request request) throws InterruptedException {
        permits.acquire();  // Block if 10 threads already active
        try {
            return externalApi.call(request);  // At most 10 concurrent calls
        } finally {
            permits.release();  // Return permit
        }
    }
}
```

Unlike a lock (permits = 1), a semaphore allows N concurrent accesses.

### tryAcquire: Non-Blocking

```java
if (permits.tryAcquire(100, TimeUnit.MILLISECONDS)) {
    try {
        return externalApi.call(request);
    } finally {
        permits.release();
    }
} else {
    return Response.rateLimited();  // Couldn't get permit in time
}
```

### Fair Semaphore

```java
Semaphore fair = new Semaphore(10, true);  // FIFO ordering
```

## PulseMetrics: Coordinated Startup and Rate Limiting

```java
public class PulseMetricsPipeline {
    private final CountDownLatch systemReady = new CountDownLatch(1);
    private final Semaphore enrichmentPermits = new Semaphore(50);  // Max 50 concurrent enrichments

    public void start() throws InterruptedException {
        Phaser startupPhaser = new Phaser(1);

        // Phase 1: Infrastructure
        startupPhaser.register();
        CompletableFuture.runAsync(() -> {
            connectDatabases();
            startupPhaser.arriveAndDeregister();
        });

        startupPhaser.register();
        CompletableFuture.runAsync(() -> {
            warmCaches();
            startupPhaser.arriveAndDeregister();
        });

        startupPhaser.arriveAndAwaitAdvance();
        System.out.println("Infrastructure ready");

        // Phase 2: Load data
        CountDownLatch dataLoaded = new CountDownLatch(2);
        CompletableFuture.runAsync(() -> { loadGeoData(); dataLoaded.countDown(); });
        CompletableFuture.runAsync(() -> { loadSegments(); dataLoaded.countDown(); });
        dataLoaded.await();
        System.out.println("Data loaded");

        // Signal: system is ready for traffic
        systemReady.countDown();
    }

    // Ingestion threads wait for system to be ready
    public void ingest(Event event) throws InterruptedException {
        systemReady.await();  // No-op after first countDown (latch is open)

        // Rate-limit enrichment calls to external services
        enrichmentPermits.acquire();
        try {
            EnrichedEvent enriched = enrichmentService.enrich(event);
            aggregate(enriched);
        } finally {
            enrichmentPermits.release();
        }
    }

    // Graceful degradation: reduce permits under load
    public void reduceEnrichmentCapacity() {
        enrichmentPermits.drainPermits();  // Take all permits
        // Release fewer back
        enrichmentPermits.release(20);  // Now only 20 concurrent enrichments
    }
}
```

## Choosing the Right Coordinator

| Need | Tool | Reusable? |
|---|---|---|
| Wait for N tasks to complete | CountDownLatch | No (one-shot) |
| All threads sync at a point, repeat | CyclicBarrier | Yes (auto-reset) |
| Multi-phase with dynamic parties | Phaser | Yes (flexible) |
| Limit concurrent access to N | Semaphore | Yes |
| One thread signals, many wait | CountDownLatch(1) | No |

## Common Mistakes

### 1. Forgetting to countDown in Error Cases

```java
// WRONG: if connect() throws, countDown never happens → await() blocks forever
new Thread(() -> {
    connect();
    latch.countDown();
}).start();

// RIGHT: countDown in finally
new Thread(() -> {
    try {
        connect();
    } finally {
        latch.countDown();  // Always count down, even on failure
    }
}).start();
```

### 2. CyclicBarrier with Wrong Party Count

```java
// WRONG: barrier expects 4 but only 3 threads call await() → hangs forever
CyclicBarrier barrier = new CyclicBarrier(4);
for (int i = 0; i < 3; i++) {  // Only 3 threads!
    new Thread(() -> barrier.await()).start();
}
```

### 3. Semaphore Leak

```java
// WRONG: if process() throws, permit is never released
permits.acquire();
process();  // Throws exception!
permits.release();  // Never reached

// RIGHT: try/finally
permits.acquire();
try {
    process();
} finally {
    permits.release();
}
```

## What You Learned

- **CountDownLatch** — one-shot gate: N threads count down, waiters proceed at zero
- **CyclicBarrier** — reusable sync point: all threads wait, then proceed together
- **Phaser** — flexible multi-phase coordination with dynamic registration
- **Semaphore** — limit concurrent access to N (rate limiting, connection pools)
- **Starting gun pattern** — latch(1) to release all threads simultaneously
- **Always countDown/release in finally** — or you'll hang forever

Startup is coordinated. Rate limiting works. But Kai's aggregation algorithm is recursive — it splits data, processes halves, and merges results. Sequential recursion is too slow. We need Fork/Join.

---

[← Chapter 9: Concurrent Collections](chapter-09-concurrent-maps.md) | [Chapter 11: Fork/Join →](chapter-11-forkjoin.md)

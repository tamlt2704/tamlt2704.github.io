# Chapter 7: Futures and CompletableFuture

[← Chapter 6: Executors](chapter-06-executors.md) | [Chapter 8: Blocking Queues →](chapter-08-blocking-queues.md)

---

## The Problem

PulseMetrics needs to enrich events before aggregation. Each event requires three lookups:

```java
public Event enrich(Event raw) {
    GeoData geo = geoService.lookup(raw.ip());         // 20ms network call
    UserProfile user = userService.fetch(raw.userId()); // 15ms network call
    RiskScore risk = fraudService.score(raw);           // 30ms network call

    return raw.withGeo(geo).withUser(user).withRisk(risk);
}
```

Sequential: 20 + 15 + 30 = **65ms per event**. These calls are independent — they don't depend on each other. Running them in parallel should take only 30ms (the slowest one).

But `executor.submit()` returns... what? How do you get the result back?

Kai: "I submitted the tasks but I have no way to get the answers. Do I use a shared variable? A callback? A queue?"

You use a `Future`.

## Future: A Promise of a Result

```java
ExecutorService executor = Executors.newFixedThreadPool(3);

Future<GeoData> geoFuture = executor.submit(() -> geoService.lookup(ip));
Future<UserProfile> userFuture = executor.submit(() -> userService.fetch(userId));
Future<RiskScore> riskFuture = executor.submit(() -> fraudService.score(event));

// All three are running in parallel now

GeoData geo = geoFuture.get();       // Blocks until geo lookup completes
UserProfile user = userFuture.get(); // Blocks until user fetch completes
RiskScore risk = riskFuture.get();   // Blocks until risk score completes
```

Three calls in parallel: total time ≈ 30ms (the slowest), not 65ms.

### Future API

```java
Future<String> future = executor.submit(() -> "hello");

future.get();                          // Block until result (or exception)
future.get(5, TimeUnit.SECONDS);       // Block with timeout
future.isDone();                       // Check without blocking
future.cancel(true);                   // Cancel (interrupt if running)
future.isCancelled();                  // Was it cancelled?
```

## The Limitations of Future

`Future.get()` blocks. That's the problem. You can't compose futures, chain them, or react when they complete:

```java
// UGLY: polling loop
while (!future.isDone()) {
    Thread.sleep(10);  // Waste
}

// UGLY: blocking get in a callback-style world
Future<GeoData> geo = executor.submit(() -> geoLookup(ip));
// Can't say: "when geo completes, THEN do this"
// You have to block: geo.get()
```

You can't say "when A finishes, start B with A's result" without blocking a thread. Enter `CompletableFuture`.

## CompletableFuture: Async Pipelines

`CompletableFuture` is a `Future` you can chain, compose, and react to:

```java
import java.util.concurrent.CompletableFuture;

CompletableFuture<GeoData> geoFuture = CompletableFuture.supplyAsync(
    () -> geoService.lookup(ip)
);

// When geo completes, enrich the event — no blocking!
CompletableFuture<Event> enrichedFuture = geoFuture.thenApply(
    geo -> event.withGeo(geo)
);
```

`thenApply` runs when the previous stage completes. No thread is blocked waiting.

## Chaining Operations

```java
CompletableFuture<DashboardUpdate> pipeline = CompletableFuture
    .supplyAsync(() -> receiveEvent())           // Step 1: receive
    .thenApply(event -> validate(event))         // Step 2: validate
    .thenApply(event -> enrich(event))           // Step 3: enrich
    .thenApply(event -> aggregate(event))        // Step 4: aggregate
    .thenAccept(result -> pushToDashboard(result)); // Step 5: push (no return)
```

Each `thenApply` runs after the previous completes. The thread is free between stages.

## Combining Multiple Futures

### thenCombine: Merge Two Results

```java
CompletableFuture<GeoData> geo = CompletableFuture.supplyAsync(() -> geoLookup(ip));
CompletableFuture<UserProfile> user = CompletableFuture.supplyAsync(() -> userFetch(id));

// When BOTH complete, combine results
CompletableFuture<EnrichedEvent> enriched = geo.thenCombine(user,
    (g, u) -> new EnrichedEvent(event, g, u)
);
```

### allOf: Wait for All

```java
CompletableFuture<GeoData> geo = CompletableFuture.supplyAsync(() -> geoLookup(ip));
CompletableFuture<UserProfile> user = CompletableFuture.supplyAsync(() -> userFetch(id));
CompletableFuture<RiskScore> risk = CompletableFuture.supplyAsync(() -> riskScore(event));

// Wait for all three
CompletableFuture<Void> all = CompletableFuture.allOf(geo, user, risk);

// When all complete, build the enriched event
CompletableFuture<EnrichedEvent> enriched = all.thenApply(v ->
    new EnrichedEvent(event, geo.join(), user.join(), risk.join())
);
```

### anyOf: First to Complete Wins

```java
// Query three replicas, use whichever responds first
CompletableFuture<Data> replica1 = CompletableFuture.supplyAsync(() -> queryReplica(1));
CompletableFuture<Data> replica2 = CompletableFuture.supplyAsync(() -> queryReplica(2));
CompletableFuture<Data> replica3 = CompletableFuture.supplyAsync(() -> queryReplica(3));

CompletableFuture<Object> fastest = CompletableFuture.anyOf(replica1, replica2, replica3);
Data result = (Data) fastest.join();
```

## Error Handling

### exceptionally: Recover from Failure

```java
CompletableFuture<GeoData> geo = CompletableFuture
    .supplyAsync(() -> geoService.lookup(ip))
    .exceptionally(ex -> {
        logger.warn("Geo lookup failed: {}", ex.getMessage());
        return GeoData.UNKNOWN;  // Fallback value
    });
```

### handle: Process Result or Error

```java
CompletableFuture<GeoData> geo = CompletableFuture
    .supplyAsync(() -> geoService.lookup(ip))
    .handle((result, ex) -> {
        if (ex != null) {
            metrics.recordFailure("geo");
            return GeoData.UNKNOWN;
        }
        return result;
    });
```

### whenComplete: Side Effects Without Changing Result

```java
CompletableFuture<GeoData> geo = CompletableFuture
    .supplyAsync(() -> geoService.lookup(ip))
    .whenComplete((result, ex) -> {
        if (ex != null) logger.error("Geo failed", ex);
        else logger.debug("Geo resolved: {}", result.country());
    });
```

## Controlling the Executor

By default, `supplyAsync` uses the common `ForkJoinPool`. For I/O tasks, use your own pool:

```java
ExecutorService ioPool = Executors.newFixedThreadPool(32);

CompletableFuture<GeoData> geo = CompletableFuture.supplyAsync(
    () -> geoService.lookup(ip),
    ioPool  // Use our I/O pool, not ForkJoinPool
);

// Async variants run the callback on the pool too
geo.thenApplyAsync(g -> enrich(event, g), ioPool);
```

Rule: **never do blocking I/O on the common ForkJoinPool.** It has limited threads (CPU count). Blocking I/O starves CPU-bound tasks.

## Timeouts (Java 9+)

```java
CompletableFuture<GeoData> geo = CompletableFuture
    .supplyAsync(() -> geoService.lookup(ip))
    .orTimeout(2, TimeUnit.SECONDS)           // Fails with TimeoutException
    .exceptionally(ex -> GeoData.UNKNOWN);    // Fallback on timeout

// Or complete with a default value on timeout
CompletableFuture<GeoData> geo = CompletableFuture
    .supplyAsync(() -> geoService.lookup(ip))
    .completeOnTimeout(GeoData.UNKNOWN, 2, TimeUnit.SECONDS);
```

## PulseMetrics: Async Enrichment Pipeline

```java
public class EnrichmentPipeline {
    private final ExecutorService ioPool = Executors.newFixedThreadPool(64);
    private final GeoService geoService;
    private final UserService userService;
    private final FraudService fraudService;

    public CompletableFuture<EnrichedEvent> enrich(Event raw) {
        CompletableFuture<GeoData> geo = CompletableFuture
            .supplyAsync(() -> geoService.lookup(raw.ip()), ioPool)
            .completeOnTimeout(GeoData.UNKNOWN, 100, TimeUnit.MILLISECONDS);

        CompletableFuture<UserProfile> user = CompletableFuture
            .supplyAsync(() -> userService.fetch(raw.userId()), ioPool)
            .completeOnTimeout(UserProfile.ANONYMOUS, 100, TimeUnit.MILLISECONDS);

        CompletableFuture<RiskScore> risk = CompletableFuture
            .supplyAsync(() -> fraudService.score(raw), ioPool)
            .completeOnTimeout(RiskScore.UNKNOWN, 200, TimeUnit.MILLISECONDS);

        return CompletableFuture.allOf(geo, user, risk)
            .thenApply(v -> new EnrichedEvent(
                raw,
                geo.join(),
                user.join(),
                risk.join()
            ));
    }

    // Process a batch of events concurrently
    public CompletableFuture<List<EnrichedEvent>> enrichBatch(List<Event> batch) {
        List<CompletableFuture<EnrichedEvent>> futures = batch.stream()
            .map(this::enrich)
            .toList();

        return CompletableFuture.allOf(futures.toArray(CompletableFuture[]::new))
            .thenApply(v -> futures.stream()
                .map(CompletableFuture::join)
                .toList()
            );
    }
}
```

Three enrichment calls run in parallel per event. Timeout after 100-200ms with fallback values. Batch processing enriches hundreds of events concurrently. Total latency per event: ~200ms worst case (timeout), ~30ms typical.

## Common Mistakes

### 1. Blocking in thenApply

```java
// WRONG: blocking call in thenApply runs on common pool
future.thenApply(data -> {
    return httpClient.post(data);  // Blocks a ForkJoinPool thread!
});

// RIGHT: use thenApplyAsync with an I/O pool
future.thenApplyAsync(data -> httpClient.post(data), ioPool);
```

### 2. Ignoring Exceptions

```java
// Exceptions are swallowed if you never call get()/join()
CompletableFuture.supplyAsync(() -> riskyOperation());
// If this fails, you'll never know

// Always handle errors
CompletableFuture.supplyAsync(() -> riskyOperation())
    .exceptionally(ex -> { logger.error("Failed", ex); return fallback; });
```

### 3. join() vs get()

```java
future.get();   // Throws checked ExecutionException — must handle
future.join();  // Throws unchecked CompletionException — cleaner in lambdas
```

Use `join()` inside lambda chains. Use `get()` when you want explicit timeout handling.

## What You Learned

- **Future** — a handle to an async result, blocks on `get()`
- **CompletableFuture** — chainable, composable async pipelines
- **thenApply/thenAccept** — transform or consume results without blocking
- **allOf/anyOf** — wait for all or race for first
- **exceptionally/handle** — error recovery in async chains
- **orTimeout/completeOnTimeout** — deadline enforcement
- **Use a dedicated I/O pool** — never block on the common ForkJoinPool

Enrichment is fast. But events are arriving faster than we can process them. We need a buffer between producers and consumers — with backpressure. That's blocking queues.

---

[← Chapter 6: Executors](chapter-06-executors.md) | [Chapter 8: Blocking Queues →](chapter-08-blocking-queues.md)

# Chapter 12: Production Readiness

[← Chapter 11: Migration Patterns](chapter-11-migration.md)

---

## The Problem

VaultPay's virtual thread migration is complete in staging. Throughput is up 15x. Latency is down. The team is excited. Nadia has one question before the production deploy:

"What's going to break at 3 AM on a Saturday that we haven't seen in our load tests?"

This chapter is the checklist. Everything you need to verify, monitor, and plan for before virtual threads hit production traffic.

## When NOT to Use Virtual Threads

Virtual threads are not universally better. They hurt in these cases:

### CPU-Bound Workloads

```java
// DON'T use virtual threads for this
executor.submit(() -> {
    // Pure computation — never blocks, never yields
    return computeHash(largePayload);  // 50ms of CPU work
});
```

Virtual threads add scheduling overhead without benefit. The carrier thread is occupied the entire time. Use a platform thread pool sized to CPU cores.

### Very Short Tasks

```java
// DON'T use virtual threads for this
executor.submit(() -> {
    return cache.get(key);  // 0.01ms — in-memory lookup
});
```

If the task completes in microseconds, the overhead of creating and scheduling a virtual thread exceeds the work itself. Use direct method calls or a platform thread pool.

### Thread-Per-Core Architectures

If your system is designed around thread-per-core (like LMAX Disruptor or single-threaded event loops), virtual threads don't fit. These architectures avoid context switching entirely — virtual threads reintroduce it.

## Production Monitoring

### Essential Metrics

```java
@Component
public class VirtualThreadHealthIndicator implements HealthIndicator {

    @Override
    public Health health() {
        Set<Thread> threads = Thread.getAllStackTraces().keySet();

        long virtualActive = threads.stream().filter(Thread::isVirtual).count();
        long virtualBlocked = threads.stream()
            .filter(Thread::isVirtual)
            .filter(t -> t.getState() == Thread.State.BLOCKED)
            .count();

        double blockedRatio = virtualActive > 0
            ? (double) virtualBlocked / virtualActive : 0;

        Health.Builder builder = blockedRatio > 0.5
            ? Health.down() : Health.up();

        return builder
            .withDetail("virtualThreads.active", virtualActive)
            .withDetail("virtualThreads.blocked", virtualBlocked)
            .withDetail("virtualThreads.blockedRatio", blockedRatio)
            .build();
    }
}
```

### Alert Thresholds

| Metric | Warning | Critical | Likely Cause |
|---|---|---|---|
| Virtual threads active | > 50,000 | > 200,000 | Thread leak or unbounded concurrency |
| Virtual threads BLOCKED | > 1,000 | > 5,000 | Pinning or resource starvation |
| Blocked ratio | > 20% | > 50% | Systemic pinning issue |
| Carrier thread utilization | > 90% | > 98% | CPU-bound work on virtual threads |
| Connection pool wait time | > 1s | > 5s | Pool too small for concurrency |

### JFR in Production

Run JFR continuously with low overhead:

```bash
java -XX:StartFlightRecording=disk=true,maxsize=500m,maxage=24h,\
settings=profile,name=continuous \
-jar vaultpay.jar
```

Dump on demand when issues occur:

```bash
jcmd <pid> JFR.dump name=continuous filename=incident.jfr
```

## Known Pitfalls

### 1. ThreadLocal Memory Leaks

```java
// DANGEROUS with virtual threads
private static final ThreadLocal<byte[]> BUFFER =
    ThreadLocal.withInitial(() -> new byte[64 * 1024]);
```

With 100K virtual threads: 100,000 × 64KB = 6.4GB of buffers. Use `ScopedValue` or pass buffers explicitly.

### 2. Object Pooling Becomes Counterproductive

```java
// UNNECESSARY with virtual threads — don't pool cheap objects
private static final ThreadLocal<SimpleDateFormat> FORMAT =
    ThreadLocal.withInitial(() -> new SimpleDateFormat("yyyy-MM-dd"));
```

ThreadLocal-based object pools were designed for reuse across a small number of threads. With virtual threads, you get one instance per thread — defeating the purpose. Use `DateTimeFormatter` (thread-safe) or create instances locally.

### 3. Carrier Thread Starvation

If all carrier threads are pinned or doing CPU work, no virtual thread can make progress:

```java
// DANGEROUS: CPU-bound work on all carriers
IntStream.range(0, 1000).forEach(i ->
    Thread.startVirtualThread(() -> {
        while (true) { computeIntensive(); } // never yields
    })
);
```

Monitor carrier utilization. If it's consistently > 95%, you have CPU-bound work that should be on platform threads.

### 4. Unbounded Thread Creation Under Load

```java
// DANGEROUS: no limit on concurrent operations
@PostMapping("/process")
public Result process(@RequestBody Request req) {
    // Each request spawns 10 virtual threads
    // 10K requests = 100K virtual threads = overwhelm downstream
    try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
        for (int i = 0; i < 10; i++) {
            scope.fork(() -> callDownstream(req));
        }
        scope.join();
    }
}
```

Always add semaphores for downstream calls (Chapter 9).

### 5. Logging Overhead

```java
// CAREFUL: logging in tight loops with 100K threads
Thread.startVirtualThread(() -> {
    for (int i = 0; i < 1000; i++) {
        log.debug("Processing item {}", i); // 100K threads × 1000 logs = 100M log lines
    }
});
```

Virtual threads amplify logging volume. Ensure async appenders and appropriate log levels.

## Pre-Deploy Checklist

Before deploying virtual threads to production:

### Code Audit
- [ ] All `synchronized` blocks with I/O inside → migrated to `ReentrantLock`
- [ ] All `ThreadLocal` usage reviewed → migrated to `ScopedValue` or removed
- [ ] No thread pools used for virtual threads (don't pool them)
- [ ] CPU-bound work remains on platform thread pools

### Backpressure
- [ ] Semaphores on all downstream service calls
- [ ] Database access limited by semaphore matching pool size
- [ ] HTTP client connections bounded
- [ ] Load shedding configured (timed permits, circuit breakers)

### Monitoring
- [ ] Virtual thread count metric exported
- [ ] Blocked thread count metric with alerting
- [ ] JFR running continuously in production
- [ ] Thread dump automation for incident response
- [ ] Connection pool metrics (wait time, active connections)

### Testing
- [ ] Load test at 2x expected peak traffic
- [ ] Soak test for 24+ hours (detect memory leaks)
- [ ] Chaos test: kill downstream services, verify graceful degradation
- [ ] Pinning test: run with `-Djdk.tracePinnedThreads=full` under load

### Rollback
- [ ] Feature flag to switch between virtual and platform thread executors
- [ ] Runbook for reverting if throughput degrades
- [ ] Canary deployment: route 5% of traffic first

## VaultPay: The Final Configuration

```yaml
# application.yml — production
spring:
  threads:
    virtual:
      enabled: true
  datasource:
    hikari:
      maximum-pool-size: 50
      connection-timeout: 5000

server:
  tomcat:
    max-connections: 20000
    connection-timeout: 20000

management:
  endpoints:
    web:
      exposure:
        include: health,metrics,threaddump
```

```bash
# JVM flags
java \
  -XX:StartFlightRecording=disk=true,maxsize=500m,maxage=24h \
  -Djdk.virtualThreadScheduler.parallelism=16 \
  -Djdk.tracePinnedThreads=short \
  -jar vaultpay.jar
```

## The Results

VaultPay after the full virtual thread migration:

| Metric | Before (Platform Threads) | After (Virtual Threads) |
|---|---|---|
| Max concurrent requests | 200 | 20,000 |
| P95 latency at peak | 8,100ms | 280ms |
| Thread memory overhead | 2GB | 20MB |
| Throughput | 625 req/s | 9,400 req/s |
| Code changes | — | ~50 lines of config |
| Reactive rewrite needed | — | No |

Same blocking code. Same sequential logic. Same readability. 15x more throughput.

## What You Learned

- **When NOT to use virtual threads** — CPU-bound work, microsecond tasks, thread-per-core designs
- **Production monitoring** — active count, blocked count, carrier utilization, JFR
- **Known pitfalls** — ThreadLocal leaks, object pooling waste, carrier starvation, unbounded creation
- **Pre-deploy checklist** — code audit, backpressure, monitoring, testing, rollback plan
- **The payoff** — 15x throughput, 30x latency reduction, minimal code changes

## The Journey

You started with 200 platform threads and a Black Friday outage. You ended with 20,000 concurrent requests on a single JVM.

Along the way, you learned that virtual threads aren't magic — they're a tool with specific tradeoffs. They eliminate the thread pool bottleneck but expose every other bottleneck: connection pools, downstream service capacity, synchronized blocks, ThreadLocal memory.

The thread-per-request model works again. Not because threads got faster — because they got cheaper. Cheap enough that blocking is no longer a sin. Cheap enough that you don't need reactive frameworks to handle concurrency. Cheap enough that the simple, readable, sequential code you wrote on day one scales to production traffic.

That's the promise of virtual threads. Not "faster threads." Cheaper threads that let you write simple code at scale.

---

[← Chapter 11: Migration Patterns](chapter-11-migration.md)

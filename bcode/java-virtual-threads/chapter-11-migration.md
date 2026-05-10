# Chapter 11: Migration Patterns

[← Chapter 10: Debugging & Profiling](chapter-10-debugging.md) | [Chapter 12: Production Readiness →](chapter-12-production.md)

---

## The Problem

VaultPay has 200K lines of Java. Thread pools are everywhere:

```java
// In PaymentProcessor.java
private final ExecutorService executor = Executors.newFixedThreadPool(50);

// In NotificationService.java
private final ExecutorService notifier = Executors.newCachedThreadPool();

// In ReportGenerator.java
private final ScheduledExecutorService scheduler =
    Executors.newScheduledThreadPool(10);

// In BatchSettlement.java
private final ExecutorService batchPool =
    new ThreadPoolExecutor(20, 100, 60L, TimeUnit.SECONDS, new LinkedBlockingQueue<>());
```

You can't rewrite everything at once. You need a strategy: which pools to migrate first, which to leave alone, and how to do it without breaking production.

Nadia: "Give me a migration plan. Lowest risk first. I want to see throughput improvements within a sprint, not a quarter."

## The Drop-In Replacement

The simplest migration: replace `newFixedThreadPool` with `newVirtualThreadPerTaskExecutor`:

```java
// BEFORE
private final ExecutorService executor = Executors.newFixedThreadPool(50);

// AFTER
private final ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();
```

Same `ExecutorService` interface. Same `submit()`, `invokeAll()`, `invokeAny()`. Same `Future<T>` return type. Your calling code doesn't change.

```java
// This code works identically with both executors
Future<PaymentResult> future = executor.submit(() -> {
    FraudResult fraud = fraudService.check(request);
    BankResult bank = bankService.authorize(request);
    return new PaymentResult(fraud, bank);
});

PaymentResult result = future.get(5, TimeUnit.SECONDS);
```

## Migration Decision Tree

For each thread pool in your codebase, ask:

```
Is the work I/O-bound (HTTP calls, DB queries, file I/O)?
├── YES → Migrate to virtual threads
│         └── Does it use synchronized with I/O inside?
│             ├── YES → Fix pinning first (Chapter 7), then migrate
│             └── NO → Safe to migrate
└── NO (CPU-bound: computation, hashing, encryption)
    └── Keep the platform thread pool (sized to CPU cores)
```

## VaultPay: Service-by-Service Migration

### Phase 1: HTTP Client Pools (Week 1)

The notification service sends webhooks to merchants. Currently pooled at 50 threads:

```java
// BEFORE
@Service
public class NotificationService {
    private final ExecutorService pool = Executors.newFixedThreadPool(50);

    public void notifyMerchant(String merchantId, Event event) {
        pool.submit(() -> {
            // HTTP call — blocks for 100-500ms
            webhookClient.send(merchantId, event);
        });
    }
}

// AFTER
@Service
public class NotificationService {
    private final ExecutorService pool = Executors.newVirtualThreadPerTaskExecutor();
    private final Semaphore permits = new Semaphore(200); // backpressure

    public void notifyMerchant(String merchantId, Event event) {
        pool.submit(() -> {
            permits.acquire();
            try {
                webhookClient.send(merchantId, event);
            } finally {
                permits.release();
            }
        });
    }
}
```

Result: notification throughput went from 50/s to 800/s. Merchants get webhooks in seconds instead of minutes during peak.

### Phase 2: Database-Heavy Services (Week 2)

The report generator queries the database with 10 concurrent threads:

```java
// BEFORE
@Service
public class ReportGenerator {
    private final ExecutorService pool = Executors.newFixedThreadPool(10);

    public Report generate(ReportRequest request) throws Exception {
        List<Future<ReportSection>> sections = new ArrayList<>();
        for (String query : request.getQueries()) {
            sections.add(pool.submit(() -> runQuery(query)));
        }
        return assemble(sections);
    }
}

// AFTER — with connection pool awareness
@Service
public class ReportGenerator {
    private final ExecutorService pool = Executors.newVirtualThreadPerTaskExecutor();
    private final Semaphore dbPermits = new Semaphore(20); // match pool size

    public Report generate(ReportRequest request) throws Exception {
        List<Future<ReportSection>> sections = new ArrayList<>();
        for (String query : request.getQueries()) {
            sections.add(pool.submit(() -> {
                dbPermits.acquire();
                try { return runQuery(query); }
                finally { dbPermits.release(); }
            }));
        }
        return assemble(sections);
    }
}
```

### Phase 3: Batch Processing (Week 3)

The settlement batch processor — this one has `synchronized`:

```java
// BEFORE — has pinning risk
@Service
public class BatchSettlement {
    private final ExecutorService pool = Executors.newFixedThreadPool(20);
    private final Object lock = new Object();

    public void processBatch(List<Settlement> settlements) {
        List<Future<?>> futures = settlements.stream()
            .map(s -> pool.submit(() -> processOne(s)))
            .toList();
        futures.forEach(f -> { try { f.get(); } catch (Exception e) { /*...*/ } });
    }

    private void processOne(Settlement s) {
        synchronized (lock) {  // PINNING RISK
            cache.update(s);
            bankApi.submit(s); // I/O inside synchronized!
        }
    }
}

// AFTER — fixed pinning, then migrated
@Service
public class BatchSettlement {
    private final ExecutorService pool = Executors.newVirtualThreadPerTaskExecutor();
    private final ReentrantLock lock = new ReentrantLock();

    public void processBatch(List<Settlement> settlements) {
        List<Future<?>> futures = settlements.stream()
            .map(s -> pool.submit(() -> processOne(s)))
            .toList();
        futures.forEach(f -> { try { f.get(); } catch (Exception e) { /*...*/ } });
    }

    private void processOne(Settlement s) {
        lock.lock();
        try {
            cache.update(s);
            bankApi.submit(s); // I/O — unmounts cleanly with ReentrantLock
        } finally {
            lock.unlock();
        }
    }
}
```

## What NOT to Migrate

### CPU-Bound Work

```java
// KEEP as platform thread pool — CPU-bound, no I/O
@Service
public class CryptoService {
    // Sized to CPU cores — virtual threads add no benefit here
    private final ExecutorService pool =
        Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors());

    public byte[] encrypt(byte[] data) throws Exception {
        return pool.submit(() -> {
            // Pure computation — never blocks, never unmounts
            return cipher.doFinal(data);
        }).get();
    }
}
```

### ScheduledExecutorService

Virtual threads don't have a scheduled variant. Keep `ScheduledExecutorService` for periodic tasks:

```java
// KEEP — no virtual thread equivalent for scheduling
private final ScheduledExecutorService scheduler =
    Executors.newScheduledThreadPool(2);

scheduler.scheduleAtFixedRate(() -> {
    // Periodic cleanup — runs every 5 minutes
    cache.evictExpired();
}, 0, 5, TimeUnit.MINUTES);
```

If the scheduled task does I/O, launch a virtual thread from within:

```java
scheduler.scheduleAtFixedRate(() -> {
    Thread.startVirtualThread(() -> {
        // I/O-heavy periodic task runs on a virtual thread
        reportService.generateDailyReport();
    });
}, 0, 1, TimeUnit.HOURS);
```

## The try-with-resources Pattern

Java 21's `ExecutorService` implements `AutoCloseable`. Use try-with-resources for scoped executors:

```java
public List<PaymentResult> processAll(List<AuthRequest> requests) throws Exception {
    List<PaymentResult> results = new ArrayList<>();

    try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
        List<Future<PaymentResult>> futures = requests.stream()
            .map(req -> executor.submit(() -> processOne(req)))
            .toList();

        for (Future<PaymentResult> f : futures) {
            results.add(f.get());
        }
    } // executor shuts down here — waits for all tasks to complete

    return results;
}
```

No manual `shutdown()` + `awaitTermination()` dance. The try block handles it.

## Migration Checklist

For each thread pool you migrate:

- [ ] Identify: is the work I/O-bound or CPU-bound?
- [ ] Check: any `synchronized` blocks with I/O inside? Fix pinning first.
- [ ] Check: any `ThreadLocal` usage? Consider `ScopedValue` migration.
- [ ] Add backpressure: semaphore matching downstream capacity.
- [ ] Test: run load tests comparing before/after throughput.
- [ ] Monitor: add virtual thread metrics (count, blocked state).
- [ ] Rollback plan: keep old config behind a feature flag.

## What You Learned

- **Drop-in replacement** — `newVirtualThreadPerTaskExecutor()` replaces `newFixedThreadPool()`
- **Same interface** — `ExecutorService` API unchanged, calling code stays the same
- **Decision tree** — I/O-bound → migrate; CPU-bound → keep platform threads
- **Phased migration** — HTTP clients first, then DB services, then batch (fix pinning)
- **Don't migrate scheduled tasks** — no virtual thread equivalent for `ScheduledExecutorService`
- **try-with-resources** — `ExecutorService` is `AutoCloseable` in Java 21
- **Always add backpressure** — semaphore when removing the implicit throttle of a thread pool

The migration is underway. Services are moving to virtual threads one by one. But before you deploy to production, you need to answer Nadia's final question: "What can go wrong that we haven't seen in staging?"

---

[← Chapter 10: Debugging & Profiling](chapter-10-debugging.md) | [Chapter 12: Production Readiness →](chapter-12-production.md)

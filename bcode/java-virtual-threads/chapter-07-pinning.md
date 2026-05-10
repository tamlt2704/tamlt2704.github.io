# Chapter 7: Pinning

[← Chapter 6: Database Access](chapter-06-database.md) | [Chapter 8: HTTP Servers →](chapter-08-http-servers.md)

---

## The Problem

VaultPay's throughput dropped 80% after deploying virtual threads to the settlement service. The service processes batch payments — reads from a queue, validates, writes to the ledger. It should be I/O-bound. Virtual threads should fly.

Raj pulls up the metrics: "8 carrier threads. All 8 are blocked. Nothing is making progress. But the CPU is at 2%."

You dig into the code. The settlement service uses a shared cache with `synchronized`:

```java
public class SettlementCache {
    private final Map<String, Settlement> cache = new HashMap<>();

    public synchronized Settlement getOrFetch(String id) {
        Settlement cached = cache.get(id);
        if (cached != null) return cached;

        // This blocks for 50ms — and the carrier is PINNED
        Settlement fresh = settlementApi.fetch(id);
        cache.put(id, fresh);
        return fresh;
    }
}
```

The `synchronized` keyword **pins** the virtual thread to its carrier. While pinned, the carrier cannot run other virtual threads. If the code inside `synchronized` blocks on I/O, the carrier is stuck — waiting for I/O, unable to serve anyone else.

8 carrier threads. 8 pinned virtual threads doing I/O inside `synchronized`. Every other virtual thread is parked, waiting for a carrier that will never come.

## What Is Pinning?

Normally, when a virtual thread blocks:
```
VT blocks → unmounts from carrier → carrier runs another VT
```

When a virtual thread blocks **inside a synchronized block**:
```
VT blocks → STAYS mounted on carrier → carrier is stuck → deadlock-like behavior
```

The JVM cannot unmount a virtual thread that holds a monitor (the lock behind `synchronized`). The monitor is tied to the OS thread. If the virtual thread unmounted, the monitor would be in an inconsistent state.

## Detecting Pinned Threads

Java provides a system property to log pinning events:

```bash
java -Djdk.tracePinnedThreads=full com.vaultpay.SettlementService
```

Output when pinning occurs:
```
Thread[#28,ForkJoinPool-1-worker-1,5,CarrierThreads]
    com.vaultpay.SettlementCache.getOrFetch(SettlementCache.java:12) <== monitors:1
    com.vaultpay.SettlementService.process(SettlementService.java:45)
    java.lang.VirtualThread.run(VirtualThread.java:309)
```

The `<== monitors:1` tells you: this virtual thread is pinned because it holds a monitor lock.

Short form (just a warning):
```bash
java -Djdk.tracePinnedThreads=short com.vaultpay.SettlementService
```

## The Fix: ReentrantLock

Replace `synchronized` with `ReentrantLock`. ReentrantLock uses `LockSupport.park()` internally, which allows virtual threads to unmount:

```java
public class SettlementCache {
    private final Map<String, Settlement> cache = new HashMap<>();
    private final ReentrantLock lock = new ReentrantLock();

    public Settlement getOrFetch(String id) {
        lock.lock();  // virtual thread can unmount while waiting for this lock
        try {
            Settlement cached = cache.get(id);
            if (cached != null) return cached;

            // I/O inside lock — virtual thread unmounts, carrier is FREE
            Settlement fresh = settlementApi.fetch(id);
            cache.put(id, fresh);
            return fresh;
        } finally {
            lock.unlock();
        }
    }
}
```

With `ReentrantLock`:
- Waiting to acquire the lock → virtual thread unmounts (carrier is free)
- Blocking on I/O while holding the lock → virtual thread unmounts (carrier is free)
- No pinning. Carriers stay productive.

## Before and After

```java
// BEFORE: pins carrier thread
public synchronized void processPayment(Payment payment) {
    validate(payment);                    // CPU work — fine
    bankApi.submit(payment);             // I/O — PINS carrier!
    ledger.record(payment);              // I/O — PINS carrier!
}

// AFTER: no pinning
private final ReentrantLock lock = new ReentrantLock();

public void processPayment(Payment payment) {
    lock.lock();
    try {
        validate(payment);                // CPU work — fine
        bankApi.submit(payment);         // I/O — unmounts cleanly
        ledger.record(payment);          // I/O — unmounts cleanly
    } finally {
        lock.unlock();
    }
}
```

## When Pinning Is Acceptable

Not all `synchronized` blocks need migration. Pinning only matters when:

1. The synchronized block contains **blocking I/O**
2. The synchronized block is **held for a long time**
3. The code runs on **virtual threads** (platform threads don't care)

Short, CPU-only synchronized blocks are fine:

```java
// This is FINE — no I/O, executes in microseconds
private int counter = 0;
public synchronized void increment() {
    counter++;  // CPU-only, no blocking, pinning lasts microseconds
}
```

## Finding Pinning in Your Codebase

A systematic approach for VaultPay's 200K-line codebase:

```bash
# Find synchronized methods
grep -rn "synchronized" src/ --include="*.java"

# Find synchronized blocks
grep -rn "synchronized\s*(" src/ --include="*.java"
```

Then check each one: does it contain I/O? Network calls? Database queries? File operations? If yes, migrate to `ReentrantLock`.

Common offenders in Java libraries:
- `java.io.PrintStream` (System.out.println is synchronized)
- `java.util.Hashtable` (all methods synchronized)
- `java.util.Vector` (all methods synchronized)
- Some JDBC drivers use synchronized internally
- Older logging frameworks

## VaultPay: The Migration

The settlement service after fixing pinning:

```java
@Service
public class SettlementService {

    private final ReentrantLock cacheLock = new ReentrantLock();
    private final Map<String, Settlement> cache = new ConcurrentHashMap<>();

    public void processSettlement(String settlementId) throws Exception {
        Settlement settlement = getOrFetch(settlementId);

        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            scope.fork(() -> bankApi.submit(settlement));
            scope.fork(() -> ledger.record(settlement));
            scope.fork(() -> notificationService.notify(settlement));

            scope.join();
            scope.throwIfFailed();
        }
    }

    private Settlement getOrFetch(String id) {
        // Fast path: no lock needed for reads on ConcurrentHashMap
        Settlement cached = cache.get(id);
        if (cached != null) return cached;

        // Slow path: lock only for cache population
        cacheLock.lock();
        try {
            // Double-check after acquiring lock
            cached = cache.get(id);
            if (cached != null) return cached;

            Settlement fresh = settlementApi.fetch(id);
            cache.put(id, fresh);
            return fresh;
        } finally {
            cacheLock.unlock();
        }
    }
}
```

Results after the fix:
```
Before (with pinning):   800 settlements/second, 8 carriers blocked
After (ReentrantLock):  12,000 settlements/second, carriers fully utilized
```

15x throughput improvement from removing pinning.

## What You Learned

- **Pinning** — `synchronized` blocks prevent virtual threads from unmounting
- **The symptom** — all carrier threads blocked, CPU idle, no progress
- **Detection** — `-Djdk.tracePinnedThreads=full` logs pinning events
- **The fix** — replace `synchronized` with `ReentrantLock`
- **When it matters** — only when synchronized blocks contain blocking I/O
- **When it's fine** — short, CPU-only synchronized blocks don't need migration
- **Library pinning** — watch for synchronized in JDBC drivers, logging, legacy collections

Pinning is fixed. The settlement service is fast. Now let's zoom out — VaultPay's HTTP server is still using a platform thread pool to accept requests. Even with virtual threads doing the work, Tomcat's thread pool is the front door. Time to replace it.

---

[← Chapter 6: Database Access](chapter-06-database.md) | [Chapter 8: HTTP Servers →](chapter-08-http-servers.md)

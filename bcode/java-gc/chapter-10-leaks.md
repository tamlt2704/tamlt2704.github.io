# Chapter 10: Memory Leaks

[← Chapter 9: GC Logging & Analysis](chapter-09-logging.md) | [Chapter 11: Off-Heap & Direct Memory →](chapter-11-off-heap.md)

---

## The Problem

Thursday, 3:47 AM. The pager fires:

```
CRITICAL: BidServer-05 OOMKilled
java.lang.OutOfMemoryError: Java heap space
  at com.bidstream.targeting.RuleEngine.evaluate(RuleEngine.java:142)
```

Sasha checks the timeline: "Server was fine for 72 hours. Heap usage grew linearly — about 1MB per hour. After 3 days, it hit the 4GB limit and OOM'd."

The GC log confirms it. Live data after each collection grew steadily:

```
[Day 1, 00:00] GC(100)  Used after GC: 1247MB
[Day 1, 12:00] GC(500)  Used after GC: 1259MB   (+12MB in 12 hours)
[Day 2, 00:00] GC(900)  Used after GC: 1271MB   (+24MB in 24 hours)
[Day 2, 12:00] GC(1300) Used after GC: 1283MB
[Day 3, 00:00] GC(1700) Used after GC: 1295MB
[Day 3, 03:47] GC(1850) Pause Full → OOM        (heap exhausted)
```

1MB/hour. Invisible in dashboards (noise hides it). Fatal after 72 hours.

Viktor: "We restarted the server and it's fine. But this will happen again in 3 days. Find the leak."

## What Is a Memory Leak in Java?

Java has garbage collection — so how can memory leak? A leak happens when objects are **reachable but unused**. The GC can't collect them because something still holds a reference, even though the application will never use them again.

Common patterns:

```java
// 1. Growing collection with no eviction
private static final Map<String, Session> sessions = new HashMap<>();
// Sessions added but never removed when user disconnects

// 2. Listener registration without deregistration
eventBus.register(new BidListener());  // Never unregistered

// 3. ClassLoader leak (common in app servers)
// Old classloader retained by a static reference after redeploy

// 4. ThreadLocal not cleaned up
threadLocal.set(largeObject);
// Thread returns to pool without threadLocal.remove()
```

## Capturing a Heap Dump

### On OOM (Automatic)

Always enable this in production:

```bash
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/dumps/bidserver-heap.hprof
```

### On Demand (Live Server)

```bash
# Full heap dump (pauses the JVM for seconds — use carefully in production)
jcmd <pid> GC.heap_dump /tmp/heap.hprof

# Or with jmap
jmap -dump:live,format=b,file=/tmp/heap.hprof <pid>
```

The `live` option forces a GC first — the dump only contains reachable objects. This makes the dump smaller and easier to analyze.

### Comparing Two Dumps

The key technique for leak detection: take two dumps separated by time and compare:

```bash
# Dump 1: after server has been running 1 hour
jcmd <pid> GC.heap_dump /tmp/heap-1h.hprof

# Dump 2: after server has been running 24 hours
jcmd <pid> GC.heap_dump /tmp/heap-24h.hprof
```

The difference between them is the leak.

## Analyzing with Eclipse MAT

Open the heap dump in [Eclipse Memory Analyzer](https://eclipse.dev/mat/):

### Step 1: Leak Suspects Report

MAT's automatic analysis identifies the largest retained objects:

```
Problem Suspect 1:
  Thread "bid-worker-pool" retains 847MB
  └─ com.bidstream.targeting.RuleEngine
     └─ java.util.HashMap (entries: 2,847,000)
        └─ com.bidstream.targeting.CompiledRule[] (avg 300 bytes each)

  Keywords: RuleEngine, HashMap, CompiledRule
```

847MB in a HashMap with 2.8 million entries. That's the leak.

### Step 2: Dominator Tree

The dominator tree shows which objects "own" the most memory:

```
Retained Heap    | Class
─────────────────┼──────────────────────────────────
847,234,112      | java.util.HashMap (RuleEngine.compiledRules)
  412,891,200    |   └─ HashMap$Node[] (table)
  434,342,912    |   └─ CompiledRule instances (2.8M entries)
```

### Step 3: Path to GC Roots

Right-click the HashMap → "Path to GC Roots" → "exclude weak references":

```
GC Root: Static field
  └─ com.bidstream.targeting.RuleEngine.compiledRules (static HashMap)
     └─ HashMap$Node[4194304]
        └─ 2,847,000 CompiledRule entries
```

A **static HashMap** that grows without bound. Found it.

## The Leak: Compiled Rules Cache

```java
public class RuleEngine {
    // The leak: rules are compiled and cached, but never evicted
    private static final Map<String, CompiledRule> compiledRules = new HashMap<>();

    public BidDecision evaluate(Campaign campaign, BidRequest request) {
        String ruleKey = campaign.getId() + ":" + campaign.getVersion();
        CompiledRule rule = compiledRules.computeIfAbsent(ruleKey, k ->
            compileRule(campaign.getTargetingRules())
        );
        return rule.apply(request);
    }
}
```

The problem: campaign rules are versioned. Every time a campaign is updated, a new version key is created. The old version's compiled rule stays in the map forever. With 60K campaigns updated daily, that's 60K new entries per day × 300 bytes = 18MB/day ≈ 0.75MB/hour.

Close to the observed 1MB/hour leak rate.

## The Fix

```java
public class RuleEngine {
    // Fixed: bounded cache with LRU eviction
    private static final Cache<String, CompiledRule> compiledRules =
        Caffeine.newBuilder()
            .maximumSize(100_000)        // Cap at 100K entries
            .expireAfterAccess(1, TimeUnit.HOURS)  // Evict unused rules
            .build();

    public BidDecision evaluate(Campaign campaign, BidRequest request) {
        String ruleKey = campaign.getId() + ":" + campaign.getVersion();
        CompiledRule rule = compiledRules.get(ruleKey, k ->
            compileRule(campaign.getTargetingRules())
        );
        return rule.apply(request);
    }
}
```

After deploying the fix, live data after GC stabilizes:

```
[Hour 0]  Used after GC: 1247MB
[Hour 24] Used after GC: 1249MB  (stable, ±2MB noise)
[Hour 72] Used after GC: 1251MB  (no growth trend)
```

## Other Common Leak Patterns

### Listener Leak

```java
// Leak: listener registered but never removed
public class BidProcessor implements Closeable {
    public BidProcessor(EventBus bus) {
        bus.register(this);  // Leak if close() is never called
    }

    @Override
    public void close() {
        bus.unregister(this);  // Must be called!
    }
}
```

### ThreadLocal Leak

```java
// Leak: ThreadLocal set in thread pool, never cleaned
private static final ThreadLocal<LargeContext> CTX = new ThreadLocal<>();

executor.submit(() -> {
    CTX.set(new LargeContext());  // Set
    process();
    // Missing: CTX.remove()  ← LEAK
    // Thread returns to pool with CTX still set
});

// Fix: always clean up in finally
executor.submit(() -> {
    try {
        CTX.set(new LargeContext());
        process();
    } finally {
        CTX.remove();  // Always clean up
    }
});
```

### ClassLoader Leak

Common in application servers during hot redeploy:

```java
// A static field in a library holds a reference to a class
// That class holds a reference to its ClassLoader
// The ClassLoader holds ALL classes it loaded
// Result: entire old application stays in memory after redeploy
```

Detect with MAT: look for duplicate ClassLoader instances in the dominator tree.

## Monitoring for Leaks

Don't wait for OOM. Monitor live data growth:

```java
// After each GC, record the "used after GC" metric
for (GarbageCollectorMXBean gc : ManagementFactory.getGarbageCollectorMXBeans()) {
    NotificationEmitter emitter = (NotificationEmitter) gc;
    emitter.addNotificationListener((notification, handback) -> {
        GcInfo info = ((GarbageCollectionNotificationInfo)
            notification.getUserData()).getGcInfo();
        long usedAfterGc = info.getMemoryUsageAfterGc().values().stream()
            .mapToLong(MemoryUsage::getUsed).sum();
        metrics.gauge("jvm.heap.used_after_gc", usedAfterGc);
    }, null, null);
}
```

Alert if `used_after_gc` shows a positive trend over 24 hours:

```yaml
- alert: PossibleMemoryLeak
  expr: deriv(jvm_heap_used_after_gc_bytes[24h]) > 500000  # >500KB/hour growth
  for: 6h
  annotations:
    summary: "Heap growing {{ $value | humanize }}/hour after GC"
```

## What You Learned

- **Memory leak in Java** — reachable but unused objects that accumulate
- **Heap dumps** — capture with `jcmd`, enable auto-dump on OOM
- **Eclipse MAT** — leak suspects, dominator tree, path to GC roots
- **Comparison technique** — two dumps separated by time reveals the leak
- **Common patterns** — unbounded maps, unregistered listeners, ThreadLocal, ClassLoader
- **Monitoring** — track "used after GC" trend to detect leaks before OOM
- **Bounded caches** — always set maximumSize and expiration on caches

The heap leak is fixed. But a week later, Sasha notices something else: the container's RSS (resident set size) is growing even though heap usage is stable. The GC manages the heap — but there's memory outside the heap that it can't touch.

Chapter 11: off-heap memory and why RSS grows when the heap looks fine.

---

[← Chapter 9: GC Logging & Analysis](chapter-09-logging.md) | [Chapter 11: Off-Heap & Direct Memory →](chapter-11-off-heap.md)

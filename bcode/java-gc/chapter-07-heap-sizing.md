# Chapter 7: Tuning Heap Size

[← Chapter 6: ZGC: Sub-Millisecond Pauses](chapter-06-zgc.md) | [Chapter 8: Allocation Pressure →](chapter-08-allocation.md)

---

## The Problem

ZGC is deployed. Pauses are gone. Then the Intern joins for the summer.

"I noticed BidServer-04 has 4GB heap but only uses 1.5GB of live data. That's wasteful. I'll set it to 2GB to save memory — we can fit more containers on the same host."

Monday morning:

```
[08:14:22.100] Allocation Stall (bid-worker-47) 84.2ms
[08:14:22.184] Allocation Stall (bid-worker-112) 91.7ms
[08:14:22.276] Allocation Stall (bid-worker-83) 67.4ms
```

Allocation stalls. ZGC can't collect fast enough because the heap is too small. The application allocates 500MB/sec, and with only 500MB of headroom (2GB heap - 1.5GB live), ZGC has less than a second to complete a collection cycle.

Sasha reverts to 4GB. Stalls disappear.

Viktor: "The Intern cost us $400 in lost bids. Teach them why heap sizing matters."

## The Sizing Dilemma

```
Too small:
  → Frequent GC (G1) or allocation stalls (ZGC)
  → High CPU spent on GC
  → Application throughput drops

Too large:
  → Longer GC pauses (G1 — more memory to scan)
  → Wasted memory (fewer containers per host)
  → Longer startup time (OS must allocate pages)
  → Higher cloud costs ($$$)

Just right:
  → GC has enough headroom to work efficiently
  → No wasted memory
  → Predictable performance
```

## Step 1: Measure Live Data

Live data is the memory occupied by objects that survive a Full GC — the irreducible minimum your application needs.

Force a Full GC and measure:

```bash
# Trigger a Full GC (only in testing/staging!)
jcmd <pid> GC.run

# Or check GC logs after a natural Full GC:
grep "Pause Full" gc.log
```

```
GC(4012) Pause Full 3891M->1247M(4096M) 339.6ms
                            ^^^^
                     Live data: 1247MB
```

For ZGC, check the "Used" after a collection:

```
GC(12) Mark: 4096M(100%) 2841M(69%) 1247M(30%)
                                     ^^^^
                              Live data: ~1247MB
```

BidStream's live data breakdown:

```
Campaign cache:     240MB  (60K entries × 4KB)
Connection pools:   120MB  (200 threads × 5 connections × 120KB buffers)
Thread stacks:       80MB  (200 threads × 400KB)
Class metadata:      60MB  (loaded classes, JIT compiled code)
JVM internals:       50MB  (GC structures, code cache)
Misc long-lived:    100MB  (config, routing tables, metrics)
─────────────────────────
Total live data:   ~650MB  (after cache reduction from Chapter 3)
```

Wait — the GC log said 1247MB. The difference is objects that are alive *at the moment of GC* but will die soon (in-flight requests, temporary buffers). Under load, "effective live data" is higher than the structural minimum.

## Step 2: Measure Under Load

Live data at rest ≠ live data under load. With 50K requests in flight:

```java
// Each in-flight request holds ~10KB of live objects
// 50K concurrent × 10KB = 500MB of "transient live" data
```

So under peak load:
- Structural live data: 650MB
- Transient live data: 500MB
- **Total live data under load: ~1.15GB**

This matches the GC log (1247MB ≈ 1.15GB + some variance).

## Step 3: Apply the Multiplier

The heap sizing formula:

```
Heap size = Live data × Multiplier

Multiplier depends on collector:
  G1:    3-4× live data (needs room for Eden, survivors, old gen headroom)
  ZGC:   2.5-3× live data (needs concurrent collection headroom)
  Parallel: 3-5× live data (needs room between Full GCs)
```

For BidStream with ZGC:

```
Live data: 1.15GB
Multiplier: 3×
Recommended heap: 3.45GB → round to 4GB
```

The Intern's 2GB was only 1.7× live data — not enough headroom for ZGC's concurrent collection.

## Step 4: Set -Xms Equal to -Xmx

Always. No exceptions for production servers.

```bash
# Good: heap is pre-allocated, no resizing overhead
-Xms4g -Xmx4g

# Bad: JVM starts small and grows, causing GC pressure during warmup
-Xms512m -Xmx4g
```

Why equal?
- **No resize pauses** — heap resizing triggers Full GC
- **Predictable memory** — container memory limits need a fixed target
- **No GC thrashing at startup** — small initial heap fills instantly

```bash
# The BidStream production configuration
java -XX:+UseZGC \
     -Xms4g -Xmx4g \
     -XX:+AlwaysPreTouch \
     BidServer
```

`-XX:+AlwaysPreTouch` forces the OS to allocate physical pages at startup. Without it, the first access to each page triggers a page fault (adds latency during warmup).

## Sizing Strategies by Workload

### Strategy 1: Fixed Workload (BidStream bidding)

Workload is predictable. Measure live data under peak load, apply multiplier, done.

```bash
-Xms4g -Xmx4g  # 1.15GB live × 3.5 ≈ 4GB
```

### Strategy 2: Variable Workload (BidStream analytics)

Batch jobs process different-sized datasets. Size for the largest expected job:

```bash
# Largest daily log: 2GB of live data during processing
# Parallel GC, 4× multiplier
-Xms8g -Xmx8g
```

### Strategy 3: Container-Constrained

When running in Kubernetes with memory limits:

```bash
# Container limit: 6GB
# Reserve for non-heap: ~1.5GB (metaspace, threads, native, buffers)
# Available for heap: 4.5GB → round down to 4GB for safety
-Xms4g -Xmx4g
```

```yaml
# kubernetes deployment
resources:
  limits:
    memory: "6Gi"
  requests:
    memory: "6Gi"
```

Critical: if heap + non-heap exceeds the container limit, the OOM killer terminates the process with no heap dump, no graceful shutdown.

## Monitoring Heap Usage

Track these metrics in production:

```java
// Expose via JMX or Prometheus
MemoryMXBean memory = ManagementFactory.getMemoryMXBean();
MemoryUsage heap = memory.getHeapMemoryUsage();

long used = heap.getUsed();       // Current usage
long committed = heap.getCommitted(); // Allocated by OS
long max = heap.getMax();         // -Xmx value

double utilization = (double) used / max;
// Alert if utilization > 80% sustained (heap too small)
// Investigate if utilization < 30% sustained (heap too large)
```

BidStream's Prometheus alerts:

```yaml
# Alert: heap consistently over 80% → risk of allocation stalls
- alert: HeapUtilizationHigh
  expr: jvm_memory_used_bytes{area="heap"} / jvm_memory_max_bytes{area="heap"} > 0.8
  for: 5m

# Alert: heap consistently under 30% → wasting memory
- alert: HeapUtilizationLow
  expr: jvm_memory_used_bytes{area="heap"} / jvm_memory_max_bytes{area="heap"} < 0.3
  for: 30m
```

## The Intern's Lesson

The Intern's mistake was reasonable — 1.5GB used out of 4GB looks wasteful. But "used" at any instant isn't the right metric. What matters:

1. **Live data after GC** — the irreducible minimum
2. **Allocation rate** — how fast new objects are created
3. **Collection time** — how long the GC needs to reclaim garbage
4. **Headroom** — space for the GC to work while the app allocates

With ZGC allocating 500MB/sec and needing ~20ms to complete a collection cycle, the GC needs at least 10MB of headroom just for one cycle. In practice, you need much more because collection cycles overlap with allocation bursts.

## What You Learned

- **Live data measurement** — force GC, measure what survives
- **Load vs rest** — live data is higher under peak traffic
- **Sizing multiplier** — 2.5-3× for ZGC, 3-4× for G1, 3-5× for Parallel
- **-Xms = -Xmx** — always, in production
- **AlwaysPreTouch** — pre-fault pages to avoid latency spikes at startup
- **Container sizing** — reserve 1-2GB for non-heap memory
- **Monitoring** — alert on sustained high utilization, not instantaneous spikes

The heap is sized correctly. ZGC has headroom. But there's another dimension: BidStream allocates 500MB/sec of garbage. That's the *allocation rate* — and it determines how hard the GC has to work regardless of heap size.

Chapter 8: reducing allocation pressure.

---

[← Chapter 6: ZGC: Sub-Millisecond Pauses](chapter-06-zgc.md) | [Chapter 8: Allocation Pressure →](chapter-08-allocation.md)

# Chapter 6: ZGC: Sub-Millisecond Pauses

[← Chapter 5: G1 Deep Dive](chapter-05-g1.md) | [Chapter 7: Tuning Heap Size →](chapter-07-heap-sizing.md)

---

## The Problem

G1 is tuned. Pauses are 10-16ms. But Viktor has the competitor dashboard open:

"AdPulse published their latency numbers. p99: 2.1ms. p999: 3.4ms. They're winning auctions we lose because our p99 is 18ms. Every millisecond of latency advantage means they bid later with more data and still respond in time."

You've squeezed G1 as far as it goes. The 10ms young GC pauses are fundamental — G1 must stop the world to evacuate Eden. No amount of tuning eliminates that.

Time for ZGC.

## What Makes ZGC Different

G1 stops the world to move objects. ZGC moves objects **while the application is running**. The only stop-the-world phases are tiny coordination points:

```
G1 collection:
  [APP RUNNING] → [STOP 10ms: evacuate] → [APP RUNNING]

ZGC collection:
  [APP RUNNING] → [STOP 0.02ms: start mark] → [APP + GC RUNNING]
  → [STOP 0.03ms: end mark] → [APP + GC RUNNING: relocate]
  → [STOP 0.02ms: start relocate] → [APP + GC RUNNING]
```

ZGC's pauses are **constant** — they don't grow with heap size. A 4GB heap and a 4TB heap have the same pause time: <1ms.

## Enabling ZGC

```bash
java -XX:+UseZGC -Xms4g -Xmx4g \
     -Xlog:gc*:file=gc.log:time,level,tags \
     BidServer
```

First GC log with ZGC:

```
[10:00:01.000] GC(1) Garbage Collection (Proactive)
[10:00:01.000] GC(1) Pause Mark Start 0.021ms
[10:00:01.008] GC(1) Concurrent Mark 8.124ms
[10:00:01.008] GC(1) Pause Mark End 0.028ms
[10:00:01.009] GC(1) Concurrent Mark Free 0.891ms
[10:00:01.010] GC(1) Concurrent Process Non-Strong References 1.412ms
[10:00:01.012] GC(1) Concurrent Reset Relocation Set 0.204ms
[10:00:01.014] GC(1) Concurrent Select Relocation Set 2.104ms
[10:00:01.014] GC(1) Pause Relocate Start 0.019ms
[10:00:01.020] GC(1) Concurrent Relocate 5.891ms
[10:00:01.020] GC(1) Load: 1.24/1.18/0.97
[10:00:01.020] GC(1) MMU: 2ms/99.2%, 5ms/99.6%, 10ms/99.9%, 20ms/99.9%
[10:00:01.020] GC(1) Mark: 4096M(100%) 2841M(69%) 1255M(31%)
[10:00:01.020] GC(1)                    Used: 2841M  Reclaimed: 1586M
```

Three pauses: 0.021ms + 0.028ms + 0.019ms = **0.068ms total**. Compare to G1's 10-16ms.

## How ZGC Works: Colored Pointers

ZGC's magic is **colored pointers**. On 64-bit systems, object pointers are 64 bits but only 48 bits are needed for the address. ZGC uses the extra bits as metadata:

```
64-bit pointer layout (ZGC):
┌────────────────────────────────────────────────────────────────┐
│ [unused] [Finalizable] [Remapped] [Marked1] [Marked0] [Address (44 bits)] │
└────────────────────────────────────────────────────────────────┘
```

The color bits tell the GC the state of the object:
- **Marked0/Marked1**: Object is reachable (alive)
- **Remapped**: Object's pointer has been updated after relocation
- **Finalizable**: Object is only reachable through a finalizer

This means ZGC can determine an object's GC state just by looking at the pointer — no side tables, no card marking.

## Load Barriers: The Key Mechanism

When the application loads a reference from the heap, ZGC inserts a **load barrier** — a small check:

```java
// What you write:
Object obj = someField;

// What the JVM actually executes (simplified):
Object obj = someField;
if (obj.colorBits != EXPECTED) {
    obj = zgc_slow_path(obj);  // Fix the pointer
}
```

The load barrier ensures that every pointer the application sees is valid and up-to-date. If an object was relocated during concurrent collection, the barrier transparently updates the pointer. The application never sees a stale reference.

Cost: ~4% throughput overhead from barrier checks. But no stop-the-world pauses.

## ZGC Collection Phases

### Phase 1: Pause Mark Start (0.02ms)

Scan GC roots (thread stacks, static fields). This is the only part that requires stopping threads, and it's tiny — just the roots, not the full object graph.

### Phase 2: Concurrent Mark (runs alongside application)

Trace the entire object graph, marking live objects via colored pointers. The application continues running. If the app modifies references during marking, the load barrier ensures consistency.

### Phase 3: Pause Mark End (0.03ms)

Finalize marking. Handle any references that changed during concurrent mark. Tiny pause.

### Phase 4: Concurrent Relocate (runs alongside application)

Move live objects to compact memory. The application keeps running. When a thread accesses a relocated object, the load barrier fixes the pointer on the fly.

### Phase 5: Pause Relocate Start (0.02ms)

Update root references to point to new locations. Another tiny pause.

**Total pause time: <0.1ms.** Everything else is concurrent.

## BidStream on ZGC: The Results

After switching the 10 bidding servers to ZGC:

```bash
java -XX:+UseZGC \
     -Xms4g -Xmx4g \
     -Xlog:gc*:file=gc.log:time,level,tags \
     BidServer
```

One hour of production traffic:

```
Metric              G1 (before)    ZGC (after)
─────────────────────────────────────────────────
Avg latency         4.1ms          3.9ms
p95 latency         8.2ms          4.1ms
p99 latency         18ms           4.3ms
p999 latency        42ms           4.8ms
Max pause           48ms           0.08ms
GC CPU overhead     3%             8%
Throughput          49K req/s      47K req/s
Lost auctions/hr   ~2,400         0
```

The p99 dropped from 18ms to 4.3ms. The tail latency (p999) went from 42ms to 4.8ms. No more GC-induced auction losses.

Viktor: "Zero lost auctions. The 5% throughput reduction is nothing — we'll add one more server to compensate. Ship it."

## ZGC Tuning (There Isn't Much)

ZGC is designed to need minimal tuning. The main knobs:

```bash
# Heap size (most important — ZGC needs headroom for concurrent collection)
-Xms4g -Xmx4g

# Number of concurrent GC threads (default: auto-detected)
-XX:ConcGCThreads=4

# Proactive collection (collect before heap is full)
-XX:+ZProactive  # default: true
```

That's it. No pause time targets, no region sizes, no survivor ratios. ZGC figures it out.

### The One Thing You Must Get Right: Heap Headroom

ZGC collects concurrently. While it's collecting, the application is still allocating. If the application allocates faster than ZGC can collect, you get an **allocation stall** — the application thread blocks waiting for memory.

```
[WARN] Allocation Stall (main) 12.4ms
```

This is ZGC's equivalent of a GC pause — and it means your heap is too small. The fix:

```bash
# Give ZGC enough headroom (rule of thumb: 2-3x live data)
# BidStream live data: ~1.5GB → heap should be 3-4.5GB
-Xms4g -Xmx4g  # Good: 2.7x live data
```

## ZGC vs Shenandoah

Both achieve sub-millisecond pauses. The differences:

| Feature | ZGC | Shenandoah |
|---------|-----|------------|
| Pointer metadata | Colored pointers (extra bits) | Brooks pointers (forwarding pointer per object) |
| Memory overhead | ~3% (pointer metadata) | ~5% (extra word per object) |
| Barrier type | Load barrier | Load + store barrier |
| Availability | All OpenJDK, Oracle JDK | OpenJDK only (not Oracle) |
| Maturity (Java 21) | Production-ready | Production-ready |

For BidStream, ZGC wins on memory overhead and availability (we use Oracle JDK on some servers).

## When NOT to Use ZGC

ZGC isn't always the answer:

- **Small heaps (<256MB)**: ZGC's overhead isn't worth it. Use Serial or G1.
- **Batch processing**: You don't care about pauses. Parallel GC gives better throughput.
- **Memory-constrained**: ZGC needs headroom. If you can't spare 2-3x live data, G1 is more memory-efficient.
- **Single-core machines**: ZGC's concurrent threads compete with application threads.

## What You Learned

- **Colored pointers** — metadata bits in the pointer itself encode GC state
- **Load barriers** — transparent pointer fixup when accessing relocated objects
- **Concurrent collection** — marking and relocation happen while app runs
- **Sub-millisecond pauses** — only root scanning requires stop-the-world
- **Heap headroom** — ZGC needs room to collect while app allocates
- **Allocation stalls** — ZGC's failure mode when heap is too small
- **Throughput tradeoff** — 5-8% CPU overhead for concurrent GC work

ZGC eliminated GC pauses from BidStream's latency profile. But the heap size matters more than ever — too small and you get allocation stalls, too large and you waste memory across 10 servers.

Chapter 7: how to size the heap correctly.

---

[← Chapter 5: G1 Deep Dive](chapter-05-g1.md) | [Chapter 7: Tuning Heap Size →](chapter-07-heap-sizing.md)

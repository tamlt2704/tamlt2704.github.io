# Chapter 4: Choosing a Collector

[← Chapter 3: Old Generation](chapter-03-old-gen.md) | [Chapter 5: G1 Deep Dive →](chapter-05-g1.md)

---

## The Problem

Viktor pulls up the quarterly review:

"We reduced GC pauses from 200ms to 15ms. Good. But our competitor AdPulse claims sub-millisecond pauses. Their p99 is 2ms. Ours is still 18ms. What are they using?"

You check AdPulse's tech blog. They migrated to ZGC last quarter. But before jumping to ZGC, you need to understand what you're trading off. Every collector makes a different bet.

Sasha: "The batch analytics pipeline on BidServer-Analytics is different. It doesn't care about latency — it processes yesterday's bid logs. It just needs to finish fast. Should that use the same GC as the real-time bidding servers?"

No. Different workloads need different collectors.

## The Five Collectors

### Serial GC (`-XX:+UseSerialGC`)

Single-threaded. Stops the world for everything. The simplest possible GC.

```bash
java -XX:+UseSerialGC -Xmx512m SmallApp
```

**When to use:** Containers with 1 CPU core and <256MB heap. Lambda functions. CLI tools.

**BidStream verdict:** Absolutely not. Single-threaded GC on a 200-thread bid server would be catastrophic.

### Parallel GC (`-XX:+UseParallelGC`)

Multi-threaded stop-the-world. Maximizes throughput — the GC uses all cores to finish as fast as possible, but still freezes the application.

```bash
java -XX:+UseParallelGC -XX:ParallelGCThreads=8 -Xmx8g BatchProcessor
```

```
GC(1) Pause Young (Allocation Failure) 2048M->124M(8192M) 45.2ms
GC(2) Pause Young (Allocation Failure) 2048M->118M(8192M) 42.8ms
```

**When to use:** Batch processing, data pipelines, anything where total runtime matters more than individual pause times.

**BidStream verdict:** Perfect for BidServer-Analytics (the batch pipeline). Terrible for real-time bidding.

### G1 GC (`-XX:+UseG1GC`) — Default since Java 9

Divides heap into regions. Collects the most garbage-filled regions first ("Garbage First"). Targets a configurable pause time.

```bash
java -XX:+UseG1GC -XX:MaxGCPauseMillis=20 -Xmx4g BidServer
```

```
GC(912) Pause Young (Normal) 2048M->84M(4096M) 8.1ms
GC(950) Pause Mixed 2560M->1840M(4096M) 14.7ms
```

**When to use:** General-purpose. Good balance of throughput and latency. Heaps from 2GB to 64GB.

**BidStream verdict:** Current choice. Works well but pauses are still 8-15ms.

### ZGC (`-XX:+UseZGC`)

Concurrent. Almost everything happens while the application runs. Pauses are <1ms regardless of heap size.

```bash
java -XX:+UseZGC -Xmx4g BidServer
```

```
GC(12) Pause Mark Start 0.024ms
GC(12) Concurrent Mark 8.412ms
GC(12) Pause Mark End 0.031ms
GC(12) Concurrent Process Non-Strong References 1.204ms
GC(12) Concurrent Relocate 3.891ms
GC(12) Pause Relocate Start 0.019ms
```

**When to use:** Latency-critical applications. Large heaps (up to 16TB). When you can't tolerate >1ms pauses.

**BidStream verdict:** The endgame for real-time bidding. Sub-millisecond pauses.

### Shenandoah (`-XX:+UseShenandoahGC`)

Similar goals to ZGC — concurrent, low-pause. Different implementation (uses Brooks pointers instead of colored pointers). Available in OpenJDK but not Oracle JDK.

```bash
java -XX:+UseShenandoahGC -Xmx4g BidServer
```

```
GC(8) Pause Init Mark 0.041ms
GC(8) Concurrent marking 12.7ms
GC(8) Pause Final Mark 0.089ms
GC(8) Concurrent evacuation 4.2ms
```

**When to use:** Same use cases as ZGC. Choose based on your JDK distribution and benchmarks.

**BidStream verdict:** Viable alternative to ZGC. We'll benchmark both.

## The Decision Matrix

```
                    Throughput    Latency    Footprint    Heap Size
Serial              ★★☆☆☆       ★☆☆☆☆     ★★★★★       < 512MB
Parallel            ★★★★★       ★★☆☆☆     ★★★★☆       Any
G1                  ★★★★☆       ★★★★☆     ★★★☆☆       2GB - 64GB
ZGC                 ★★★☆☆       ★★★★★     ★★☆☆☆       Any (up to 16TB)
Shenandoah          ★★★☆☆       ★★★★★     ★★☆☆☆       Any
```

The tradeoffs:

- **Throughput vs Latency**: Parallel GC maximizes throughput (total work done) but has long pauses. ZGC minimizes pauses but uses CPU for concurrent GC work, reducing throughput by 5-15%.
- **Latency vs Footprint**: ZGC and Shenandoah use more memory for their concurrent bookkeeping (colored pointers, forwarding tables). Expect 5-10% memory overhead.
- **Simplicity vs Control**: G1 has dozens of tuning knobs. ZGC has almost none — it's designed to "just work."

## Benchmarking for BidStream

You run the same workload with each collector:

```bash
# G1 (current)
java -XX:+UseG1GC -XX:MaxGCPauseMillis=20 -Xms4g -Xmx4g \
     -Xlog:gc*:file=gc-g1.log BidServer

# ZGC
java -XX:+UseZGC -Xms4g -Xmx4g \
     -Xlog:gc*:file=gc-zgc.log BidServer

# Parallel (for comparison)
java -XX:+UseParallelGC -Xms4g -Xmx4g \
     -Xlog:gc*:file=gc-parallel.log BidServer
```

Results after 10 minutes under load (50K req/sec):

```
Collector    Avg Latency    p99 Latency    Max Pause    Throughput
Parallel     3.2ms          85ms           312ms        52K req/s
G1           4.1ms          18ms           42ms         49K req/s
ZGC          3.8ms          4.2ms          0.8ms        47K req/s
```

Analysis:
- **Parallel**: Best throughput and average latency, but p99 is terrible (GC pauses)
- **G1**: Good balance, p99 is acceptable, no catastrophic pauses
- **ZGC**: Slightly lower throughput (concurrent GC uses CPU), but p99 is excellent

For BidStream's real-time bidding: **ZGC wins**. The 5% throughput reduction is worth eliminating tail latency.

For BidStream's batch analytics: **Parallel wins**. It processes the daily log 15% faster than G1.

## The Migration Plan

You propose to Viktor:

```
Real-time bidding servers (10 JVMs):  G1 → ZGC
Batch analytics pipeline (2 JVMs):    G1 → Parallel
Campaign management API (3 JVMs):     Stay on G1 (latency-tolerant, moderate load)
```

Viktor: "Do the bidding servers first. That's where the money is."

But before switching to ZGC, you want to squeeze everything out of G1. ZGC has less tuning surface — if something goes wrong, you have fewer knobs. Understanding G1 deeply gives you a fallback.

## Quick Reference: Choosing Your Collector

```
Is your heap < 512MB and single-core?
  → Serial

Is this a batch job where total runtime matters?
  → Parallel

Do you need pauses < 1ms regardless of heap size?
  → ZGC or Shenandoah

Do you need predictable pauses with good throughput?
  → G1

Not sure?
  → Start with G1 (default). Measure. Switch if needed.
```

## What You Learned

- **Five collectors** — Serial, Parallel, G1, ZGC, Shenandoah
- **Throughput vs latency** — fundamental tradeoff in GC design
- **Concurrent collectors** — ZGC/Shenandoah do work while app runs, trading CPU for low pauses
- **Workload matching** — different services in the same system may need different collectors
- **Benchmarking** — always measure with your actual workload, not synthetic benchmarks
- **ZGC overhead** — 5-15% throughput cost for sub-millisecond pauses

G1 is the current collector and the default for good reason — it's the best general-purpose choice. Before jumping to ZGC, let's understand G1 deeply. Its region-based design, mixed collections, and pause time targeting are elegant — and knowing them helps you understand when G1 is enough and when you truly need ZGC.

Chapter 5: G1 internals.

---

[← Chapter 3: Old Generation](chapter-03-old-gen.md) | [Chapter 5: G1 Deep Dive →](chapter-05-g1.md)

# Java Garbage Collection — From GC Pauses to GC Mastery

A narrative-driven course on Java garbage collection. You're a performance engineer at an ad-tech company where GC pauses are losing auctions. Over 12 chapters, you'll tame the garbage collector — one stop-the-world pause at a time.

## Episodes

| # | Title | The Problem | What You Learn |
|---|---|---|---|
| 00 | [Before You Start](chapter-00-overview.md) | — | Setup, memory model, the cast |
| 01 | [The Pause That Lost Money](chapter-01-the-pause.md) | 200ms GC pause loses bid auction | GC basics, heap layout, generations |
| 02 | [Young Generation](chapter-02-young-gen.md) | Short-lived objects fill memory | Eden, survivors, minor GC, promotion |
| 03 | [Old Generation](chapter-03-old-gen.md) | Long-lived objects accumulate | Major GC, compaction, fragmentation |
| 04 | [Choosing a Collector](chapter-04-collectors.md) | Default GC isn't optimal | Serial, Parallel, G1, ZGC, Shenandoah |
| 05 | [G1 Deep Dive](chapter-05-g1.md) | Need predictable pause times | Regions, mixed collections, humongous objects |
| 06 | [ZGC: Sub-Millisecond](chapter-06-zgc.md) | Even G1 pauses are too long | Colored pointers, load barriers, concurrent |
| 07 | [Tuning Heap Size](chapter-07-heap-sizing.md) | Too small = frequent GC, too large = long pauses | -Xmx, -Xms, sizing strategies |
| 08 | [Allocation Pressure](chapter-08-allocation.md) | Creating too much garbage | Object pooling, escape analysis, TLAB |
| 09 | [GC Logging & Analysis](chapter-09-logging.md) | "Why did GC just take 3 seconds?" | -Xlog:gc*, GCViewer, GCEasy |
| 10 | [Memory Leaks](chapter-10-leaks.md) | Heap grows forever, OOM at 3 AM | Heap dumps, MAT, leak patterns |
| 11 | [Off-Heap & Direct Memory](chapter-11-off-heap.md) | GC can't help with native memory | ByteBuffer, Unsafe, memory tracking |
| 12 | [Production GC Strategy](chapter-12-production.md) | Putting it all together | Monitoring, alerting, tuning workflow |

## Prerequisites

- Java 21+ (for ZGC and latest G1 improvements)
- VisualVM or JDK Mission Control
- Basic understanding of JVM memory

## Philosophy

Every tuning decision is introduced because a GC pause hurt the business. No flags without a measurable problem first. The pause comes first. The fix follows.

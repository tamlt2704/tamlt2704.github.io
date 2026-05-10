# Chapter 0: Before You Start

[Chapter 1: The Pause That Lost Money →](chapter-01-the-pause.md)

---

## The Story

This is a series about Java garbage collection — but not the kind where you memorize "G1 uses regions" and move on.

You're a performance engineer at **BidStream**, an ad-tech company that runs real-time bidding (RTB) auctions. When a user loads a webpage, BidStream has **100 milliseconds** to receive the bid request, evaluate 50 ad campaigns, compute a bid price, and respond. If the response arrives after 100ms, the auction is lost. The ad doesn't show. The revenue is zero.

BidStream processes 500,000 bid requests per second across a fleet of JVMs. Each JVM handles 50,000 requests/second. The system works beautifully — until it doesn't.

Every few minutes, a JVM pauses. The garbage collector runs. For 200 milliseconds, nothing happens. No requests are processed. No bids are sent. 10,000 auctions are lost in a single pause. At $0.002 per auction, that's $20 per pause. With pauses every 3 minutes across 10 JVMs, that's **$100,000/month in lost revenue** from GC pauses alone.

Your CTO, **Viktor**, shows you the dashboard:

"See these red spikes? Every spike is money we didn't make. The business logic takes 5ms. The GC takes 200ms. We're spending 40x more time collecting garbage than doing actual work. Fix it."

You nod. You know what a garbage collector is. It frees memory. How hard can it be to tune?

Over the next 12 chapters, you'll take BidStream's GC from "200ms pauses every 3 minutes" to "sub-millisecond pauses, always." Every tuning decision solves a real problem — reducing pause times, preventing memory leaks, choosing the right collector, sizing the heap. And every naive fix will break in a way that teaches you why GC tuning is an art.

The heap will fill up faster than expected. The promotion rate will overwhelm old gen. The humongous allocation will bypass your carefully tuned regions. The memory leak will grow so slowly it takes 3 days to OOM. The off-heap memory will grow while the heap looks fine.

Each failure teaches you something about memory management that no JVM flag reference could.

By the end, you'll have a production-tuned GC configuration that handles 50K requests/second with sub-millisecond pauses — and you'll understand *why* every flag is set the way it is.

## How to Read This

Every chapter is the same loop:

1. A GC pause (or OOM, or memory leak) hurts the business
2. You measure the problem — how long? How often? What triggered it?
3. You learn the GC concept that explains it
4. You apply the fix, measure the improvement
5. You discover the next problem

No concept shows up before you need it. You won't hear about ZGC until G1's pauses are still too long. You won't touch heap dumps until a memory leak crashes production at 3 AM.

The pause comes first. The understanding follows.

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Performance Engineer | Reads GC logs like poetry. |
| **Viktor** | CTO | "Every millisecond is money. Show me the numbers." |
| **Sasha** | SRE | "The JVM OOM'd again. Page 3 of the runbook." |
| **The JVM** | Your patient | Healthy until it isn't. Communicates through logs. |
| **The GC** | The janitor | Tries its best. Sometimes stops the world. |
| **The Intern** | Summer hire | Set -Xmx to 128GB. "More heap = fewer GCs, right?" |

## The Roadmap

| Ch | The Problem | What You Learn |
|---|---|---|
| 1 | 200ms pause loses 10K auctions | GC fundamentals, stop-the-world, heap layout |
| 2 | Short-lived bid objects fill Eden | Young generation, minor GC, survivor spaces |
| 3 | Campaign cache grows in old gen | Major GC, compaction, promotion |
| 4 | Default collector isn't optimal for latency | Collector comparison, selection criteria |
| 5 | G1 pauses are predictable but still 50ms | G1 internals, mixed collections, tuning |
| 6 | Need pauses under 1ms | ZGC, concurrent collection, colored pointers |
| 7 | Heap too small = thrashing, too large = long pauses | Sizing strategies, live data measurement |
| 8 | Allocating 2GB/sec of garbage | Allocation rate, TLAB, escape analysis |
| 9 | "Why did that pause happen?" | GC logging, analysis tools, reading logs |
| 10 | Heap grows 1MB/hour, OOM after 3 days | Leak detection, heap dumps, MAT |
| 11 | Native memory grows while heap is stable | Direct buffers, off-heap tracking, NMT |
| 12 | Putting it all together for production | Monitoring, alerting, tuning workflow |

## Prerequisites

Two things: Java 21 and a profiling tool.

### Java 21+

We use Java 21 for the latest GC improvements (G1 and ZGC both received significant updates):

```bash
java --version
# openjdk 21.0.x or higher
```

### JVM Flags We'll Use

Don't set these yet — each chapter introduces them when needed:

```bash
# GC logging (Chapter 9)
-Xlog:gc*:file=gc.log:time,level,tags

# Heap sizing (Chapter 7)
-Xms4g -Xmx4g

# Collector selection (Chapter 4-6)
-XX:+UseG1GC
-XX:+UseZGC

# Diagnostics
-XX:+HeapDumpOnOutOfMemoryError
-XX:NativeMemoryTracking=summary
```

### Profiling Tools

Install at least one:

```bash
# VisualVM (free, good for basics)
# Download from https://visualvm.github.io/

# JDK Mission Control (free, more powerful)
# Bundled with some JDK distributions, or download separately

# GCEasy (online, paste GC logs)
# https://gceasy.io/
```

### The Test Application

We'll use a simulated bid server throughout the course:

```java
public class BidServer {
    public static void main(String[] args) {
        // Simulates 50K requests/second
        // Each request: parse JSON, evaluate campaigns, compute bid
        // Generates ~1GB/sec of short-lived garbage
        System.out.println("BidServer starting...");
        System.out.println("JVM: " + System.getProperty("java.version"));
        System.out.println("Max heap: " + Runtime.getRuntime().maxMemory() / 1024 / 1024 + "MB");
        System.out.println("Processors: " + Runtime.getRuntime().availableProcessors());
    }
}
```

### Quick Check

```bash
java -XX:+PrintFlagsFinal -version 2>&1 | grep -i "UseG1GC\|UseZGC"
```

You should see `UseG1GC` as `true` (default in Java 21). If that works, you're ready.

## The Memory Model (The Only Theory Upfront)

Every Java object lives on the **heap** — a region of memory managed by the garbage collector. When you write `new Object()`, the JVM allocates space on the heap. When nothing references that object anymore, the GC reclaims the space.

### The Generational Hypothesis

Most objects die young. A bid request object lives for 5ms — created, processed, discarded. A campaign cache entry lives for hours. The GC exploits this:

```
┌─────────────────────────────────────────────────────┐
│                      HEAP                            │
├──────────────────────┬──────────────────────────────┤
│    Young Generation  │       Old Generation         │
├────────┬─────────────┤                              │
│  Eden  │  Survivors  │                              │
│        │  S0  │  S1  │                              │
└────────┴──────┴──────┴──────────────────────────────┘
  (new objects)          (objects that survived many GCs)
```

- **Eden**: Where new objects are born. Collected frequently (minor GC). Fast.
- **Survivors**: Objects that survived one minor GC. Collected with Eden.
- **Old Generation**: Objects that survived many minor GCs. Collected rarely (major GC). Slow.

The insight: if 95% of objects die in Eden, you only need to scan 5% of the heap most of the time. Minor GCs are fast because they only look at the young generation.

### Stop-the-World

When the GC runs, it must ensure no thread is modifying objects while it's scanning them. The simplest way: **stop all application threads**. This is a "stop-the-world" (STW) pause.

- Minor GC STW: 5–20ms (small heap region, few survivors)
- Major GC STW: 50–500ms (entire old generation)
- Full GC STW: 200ms–10s (everything, compaction)

BidStream's 200ms pauses are major GCs. The old generation fills up, the GC stops the world, scans everything, compacts memory, and resumes. During those 200ms, 10,000 bid requests go unanswered.

### The Goal

We want to go from:

```
Pause time: 200ms every 3 minutes
Lost auctions: 10,000 per pause
Monthly cost: $100,000
```

To:

```
Pause time: <1ms (ZGC) or <10ms (tuned G1)
Lost auctions: 0
Monthly cost: $0
```

Same hardware. Same code. Different GC configuration.

Let's see the first pause.

---

[Chapter 1: The Pause That Lost Money →](chapter-01-the-pause.md)

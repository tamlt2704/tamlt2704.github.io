# Chapter 1: The Pause That Lost Money

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Young Generation →](chapter-02-young-gen.md)

---

## The Problem

Monday morning. Sasha pings you:

"BidServer-07 dropped 12,000 requests between 09:14:22.100 and 09:14:22.312. No errors. No exceptions. The process was alive. It just... stopped responding for 212ms."

You check the application logs. Nothing at that timestamp. The server was healthy before and after. But for 212 milliseconds, it was dead to the world.

You check the GC log:

```
[2024-01-15T09:14:22.100+0000] GC(847) Pause Full (Allocation Failure)
[2024-01-15T09:14:22.100+0000] GC(847) Phase 1: Mark live objects
[2024-01-15T09:14:22.178+0000] GC(847) Phase 2: Compute new addresses
[2024-01-15T09:14:22.201+0000] GC(847) Phase 3: Adjust pointers
[2024-01-15T09:14:22.267+0000] GC(847) Phase 4: Move objects
[2024-01-15T09:14:22.312+0000] GC(847) Pause Full 3842M->1247M(4096M) 212.456ms
```

A **Full GC**. The heap was 3842MB out of 4096MB. The GC stopped everything, found 2595MB of garbage, compacted the remaining 1247MB of live data, and resumed. 212 milliseconds of silence.

Viktor: "That's $24 we just lost. And it happens every 3 minutes. Do the math."

## Understanding the GC Log

Let's break down what happened:

```
Pause Full (Allocation Failure)
```

- **Pause**: Stop-the-world — all application threads frozen
- **Full**: Entire heap collected (young + old generation)
- **Allocation Failure**: A thread tried to allocate an object and there was no space

```
3842M->1247M(4096M) 212.456ms
```

- **3842M**: Heap usage before GC
- **1247M**: Heap usage after GC (live data)
- **4096M**: Total heap size (-Xmx4g)
- **212.456ms**: Pause duration

So: 4GB heap, 3.8GB used, 1.2GB actually alive, 2.6GB was garbage. The GC reclaimed 68% of the heap. But it took 212ms to figure that out.

## Why a Full GC?

Full GCs are the nuclear option. They happen when:

1. **Old generation is full** — no room for promoted objects
2. **Allocation failure** — can't allocate even after a minor GC
3. **Explicit call** — someone called `System.gc()` (never do this in production)
4. **Metadata space full** — class metadata exhausted (rare)

In BidStream's case: the old generation filled up with long-lived objects (campaign cache, connection pools, compiled bid strategies). When a minor GC tried to promote objects from young to old, there was no room. Fallback: Full GC.

## Reproducing the Problem

Let's build a minimal BidServer that exhibits the same behavior:

```java
import java.util.*;
import java.util.concurrent.*;

public class BidServer {

    // Simulates campaign cache (long-lived, stays in old gen)
    private static final Map<String, byte[]> campaignCache = new ConcurrentHashMap<>();

    // Simulates bid processing (short-lived garbage)
    private static final ExecutorService executor = Executors.newFixedThreadPool(200);

    public static void main(String[] args) throws Exception {
        System.out.println("BidServer starting...");
        System.out.println("Max heap: " + Runtime.getRuntime().maxMemory() / 1024 / 1024 + "MB");

        // Load campaign cache (fills old gen over time)
        loadCampaigns();

        // Process bids (generates young gen garbage)
        processBids();
    }

    private static void loadCampaigns() {
        // 1000 campaigns, each ~1MB of targeting data
        for (int i = 0; i < 1000; i++) {
            campaignCache.put("campaign-" + i, new byte[1024 * 1024]);
        }
        System.out.println("Loaded " + campaignCache.size() + " campaigns (~1GB)");
    }

    private static void processBids() {
        // Simulate 50K bids/second
        ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
        scheduler.scheduleAtFixedRate(() -> {
            for (int i = 0; i < 1000; i++) {
                executor.submit(() -> processSingleBid());
            }
        }, 0, 20, TimeUnit.MILLISECONDS); // 1000 bids every 20ms = 50K/sec
    }

    private static void processSingleBid() {
        // Each bid creates ~10KB of short-lived garbage
        // Parse request
        byte[] request = new byte[2048];

        // Evaluate campaigns (creates intermediate objects)
        List<String> eligible = new ArrayList<>();
        for (int i = 0; i < 50; i++) {
            eligible.add("campaign-" + ThreadLocalRandom.current().nextInt(1000));
        }

        // Compute bid (more allocations)
        Map<String, Double> scores = new HashMap<>();
        for (String campaign : eligible) {
            scores.put(campaign, ThreadLocalRandom.current().nextDouble() * 10.0);
        }

        // Response (serialization garbage)
        byte[] response = new byte[512];
    }
}
```

Run with GC logging:

```bash
java -Xms4g -Xmx4g \
     -Xlog:gc*:file=gc.log:time,level,tags \
     -XX:+UseG1GC \
     BidServer
```

After a few minutes, check the log:

```bash
grep "Pause Full" gc.log
```

You'll see Full GC pauses. The campaign cache (1GB) lives in old gen. Bid processing generates ~500MB/sec of young gen garbage. Eventually, promoted objects plus the cache fill old gen, triggering a Full GC.

## Measuring GC Impact

Add a latency tracker to see the effect on request processing:

```java
private static void processSingleBid() {
    long start = System.nanoTime();

    // ... bid processing ...

    long elapsed = System.nanoTime() - start;
    if (elapsed > 10_000_000) { // > 10ms
        System.out.printf("SLOW BID: %dms (likely GC pause)%n", elapsed / 1_000_000);
    }
}
```

During a Full GC, every in-flight bid shows 200ms+ latency. Not because the bid logic is slow — because the thread was frozen.

## The GC Phases

What happens during those 212ms:

### Phase 1: Mark Live Objects (78ms)

The GC starts from "GC roots" (stack variables, static fields, JNI references) and traces every reachable object. Anything not reachable is garbage.

```
GC Roots → campaignCache → 1000 byte arrays (live)
GC Roots → executor → thread stacks → in-flight bids (live)
Everything else → GARBAGE
```

With 1.2GB of live data spread across millions of objects, marking takes time.

### Phase 2: Compute New Addresses (23ms)

After marking, live objects are scattered across the heap with gaps (where garbage was). The GC computes where each live object will move to eliminate gaps.

### Phase 3: Adjust Pointers (66ms)

Every reference to a moved object must be updated. If object A points to object B, and B is moving from address 0x1000 to 0x2000, the pointer in A must change.

### Phase 4: Move Objects (45ms)

Physically copy live objects to their new locations. This is the compaction step — it eliminates fragmentation.

**Total: 212ms of frozen application.**

## Why This Matters for BidStream

The RTB protocol gives you 100ms to respond. A 212ms GC pause means:

- Every bid request that arrived during the pause → **lost** (timed out)
- At 50K requests/second, 212ms = **10,600 lost bids**
- At $0.002/bid average revenue = **$21.20 per pause**
- Pauses every ~3 minutes = **$10,176/day = $305,280/month**

Viktor: "That's a senior engineer's salary. In GC pauses."

## Quick Wins (That Don't Actually Fix It)

### Increase heap size?

```bash
java -Xmx8g ...
```

Fewer GCs (more room before filling up), but each GC takes **longer** (more memory to scan). You trade frequency for duration. The pauses go from 200ms every 3 minutes to 400ms every 6 minutes. Same total impact.

### Reduce live data?

If the campaign cache were smaller, GC would be faster. But the cache exists for a reason — without it, every bid requires a database lookup (5ms), which is worse than the GC pause amortized.

### The real fix?

A different garbage collector. One that doesn't stop the world for 200ms. One that collects concurrently while the application runs. That's G1 (tuned) or ZGC.

But first, you need to understand *what* the GC is collecting and *why*. That starts with the young generation.

## What You Learned

- **Stop-the-world** — all threads freeze during GC
- **Full GC** — collects entire heap, longest pause type
- **GC log reading** — heap before/after, pause duration, trigger reason
- **Allocation failure** — triggered when no space for new objects
- **The four phases** — mark, compute addresses, adjust pointers, move
- **Business impact** — GC pauses have measurable cost in latency-sensitive systems
- **Heap size tradeoff** — bigger heap = fewer but longer pauses

The Full GC is the symptom. The disease is: too much garbage being promoted to old gen, filling it up, forcing a full collection. To fix it, we need to understand how objects move through the generational system.

That's Chapter 2.

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Young Generation →](chapter-02-young-gen.md)

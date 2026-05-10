# Chapter 8: Allocation Pressure

[← Chapter 7: Tuning Heap Size](chapter-07-heap-sizing.md) | [Chapter 9: GC Logging & Analysis →](chapter-09-logging.md)

---

## The Problem

ZGC is running smoothly. Then traffic doubles — Black Friday for ad-tech. BidStream goes from 50K to 100K requests/second.

```
[11:00:01] GC(412) Concurrent Relocate 14.2ms
[11:00:01] GC(412) Used: 3841M  Reclaimed: 2104M
[11:00:02] GC(413) Concurrent Relocate 16.8ms
[11:00:02] GC(413) Used: 3912M  Reclaimed: 2201M
[11:00:02] GC(414) Garbage Collection (Allocation Rate)
[11:00:03] Allocation Stall (bid-worker-88) 4.2ms
```

ZGC is collecting every second. The allocation rate doubled from 500MB/sec to **1GB/sec**. Even with 4GB heap, ZGC can barely keep up. The GC is spending 15% of CPU on concurrent collection.

Sasha: "We could double the heap to 8GB. But that means bigger containers, fewer per host, more cloud spend."

Viktor: "Or we could allocate less garbage. How much of that 1GB/sec is actually necessary?"

## Measuring Allocation Rate

### From GC Logs

```bash
# ZGC logs show allocation rate directly
grep "Allocation Rate" gc.log
```

```
[11:00:01] GC(412) Allocation Rate: 1024MB/s
[11:00:02] GC(413) Allocation Rate: 1089MB/s
[11:00:03] GC(414) Allocation Rate: 1156MB/s  ← climbing
```

### From JMX

```java
// Sample allocation rate programmatically
long before = getEdenUsed();
Thread.sleep(1000);
long after = getEdenUsed();
long allocationRate = after - before;  // bytes/second

private static long getEdenUsed() {
    for (MemoryPoolMXBean pool : ManagementFactory.getMemoryPoolMXBeans()) {
        if (pool.getName().contains("Eden") || pool.getName().contains("ZHeap")) {
            return pool.getUsage().getUsed();
        }
    }
    return 0;
}
```

### From JFR (Java Flight Recorder)

```bash
jcmd <pid> JFR.start duration=60s filename=alloc.jfr settings=profile
```

JFR captures allocation by call site — the most actionable data. Open in JDK Mission Control and sort by "TLAB Allocations" to find the hottest allocators.

## Where BidStream's Garbage Comes From

JFR profiling reveals the top allocators:

```
Allocation Site                          Rate        % of Total
─────────────────────────────────────────────────────────────────
BidServer.processSingleBid()             420MB/s     42%
  └─ new byte[2048] (request parsing)   200MB/s
  └─ new ArrayList<>() + strings         120MB/s
  └─ new HashMap<>() + entries           100MB/s
JsonSerializer.serialize()               310MB/s     31%
  └─ StringBuilder.toString()            180MB/s
  └─ byte[] (UTF-8 encoding)            130MB/s
MetricsCollector.record()                150MB/s     15%
  └─ new MetricEvent() per request       150MB/s
Other                                    120MB/s     12%
```

## TLAB: Thread-Local Allocation Buffers

Before optimizing, understand how allocation works. Each thread has a **TLAB** — a private chunk of Eden:

```
Thread-1 TLAB: [████████░░░░░░░░] 8KB used of 64KB
Thread-2 TLAB: [██████████████░░] 56KB used of 64KB  ← almost full
Thread-3 TLAB: [██░░░░░░░░░░░░░░] 4KB used of 64KB
```

Allocation within a TLAB is a simple pointer bump — no synchronization, no locks. It's essentially free. The cost comes when:
1. TLAB is full → request new TLAB from Eden (minor contention)
2. Eden is full → trigger GC

TLAB sizing:

```bash
# Let JVM auto-size TLABs (default, usually best)
-XX:+UseTLAB  # default: true

# Or set minimum size (rarely needed)
-XX:TLABSize=256k
```

## Optimization 1: Escape Analysis

The JIT compiler can detect objects that never escape a method and allocate them on the **stack** instead of the heap. Stack allocation is free — no GC needed.

```java
// Before: allocates on heap (GC must collect it)
private double computeBidScore(Campaign campaign, BidRequest request) {
    // This Point object never leaves the method
    Point userLocation = new Point(request.getLat(), request.getLon());
    double distance = campaign.getCenter().distanceTo(userLocation);
    return campaign.getBaseScore() * (1.0 / (1.0 + distance));
}
```

The JIT sees that `userLocation` never escapes `computeBidScore()` — it's not stored in a field, not passed to another thread, not returned. It can be **scalar replaced**: the fields are placed directly in local variables.

```java
// What the JIT effectively does (scalar replacement):
private double computeBidScore(Campaign campaign, BidRequest request) {
    double userLat = request.getLat();  // No object allocated
    double userLon = request.getLon();  // Just stack variables
    double distance = campaign.getCenter().distanceTo(userLat, userLon);
    return campaign.getBaseScore() * (1.0 / (1.0 + distance));
}
```

Verify escape analysis is working:

```bash
-XX:+PrintEscapeAnalysis       # Shows which allocations are eliminated
-XX:+PrintEliminateAllocations # Shows scalar replacements
```

**Caveat:** Escape analysis fails if the object is too complex (>64 fields), stored in an array, or passed to a non-inlined method. Don't rely on it — design for it.

## Optimization 2: Object Reuse

The biggest win for BidStream — reuse objects instead of creating new ones:

```java
// Before: 420MB/s of garbage from processSingleBid()
private static void processSingleBid() {
    byte[] request = new byte[2048];
    List<String> eligible = new ArrayList<>();
    Map<String, Double> scores = new HashMap<>();
    // ... process ...
}

// After: thread-local reusable objects
private static final ThreadLocal<BidContext> CONTEXT =
    ThreadLocal.withInitial(BidContext::new);

private static void processSingleBid() {
    BidContext ctx = CONTEXT.get();
    ctx.reset();  // Clear previous state, reuse buffers
    ctx.parseRequest(inputStream);
    ctx.evaluateCampaigns();
    ctx.computeScores();
}

static class BidContext {
    final byte[] requestBuffer = new byte[2048];  // Reused
    final List<String> eligible = new ArrayList<>(64);  // Reused
    final Map<String, Double> scores = new HashMap<>(64);  // Reused

    void reset() {
        eligible.clear();
        scores.clear();
    }
}
```

Result: `processSingleBid()` drops from 420MB/s to ~5MB/s (only truly temporary objects remain).

## Optimization 3: Avoid Intermediate Strings

```java
// Before: StringBuilder.toString() creates a new String + char[] copy
String json = new StringBuilder()
    .append("{\"bid\":\"").append(bidId)
    .append("\",\"price\":").append(price)
    .append("}").toString();  // Allocates final String
byte[] payload = json.getBytes(UTF_8);  // Another allocation

// After: write directly to output buffer
private static final ThreadLocal<ByteArrayOutputStream> BAOS =
    ThreadLocal.withInitial(() -> new ByteArrayOutputStream(4096));

byte[] payload = serializeDirect(bidId, price);

private static byte[] serializeDirect(String bidId, double price) {
    ByteArrayOutputStream out = BAOS.get();
    out.reset();
    // Write JSON bytes directly — no intermediate String
    out.write('{'); out.write('"'); out.write('b');
    // ... or use a streaming JSON writer like Jackson's JsonGenerator
    return out.toByteArray();
}
```

Better yet, use Jackson's streaming API:

```java
// Zero intermediate strings — writes directly to output
JsonGenerator gen = jsonFactory.createGenerator(outputStream);
gen.writeStartObject();
gen.writeStringField("bid", bidId);
gen.writeNumberField("price", price);
gen.writeEndObject();
gen.flush();
```

## Optimization 4: Eliminate Per-Request Metrics Objects

```java
// Before: new object per request (150MB/s)
metricsCollector.record(new MetricEvent(
    "bid.processed", System.nanoTime(), tags));

// After: ring buffer with pre-allocated events
private static final MetricEvent[] RING = new MetricEvent[8192];
static { for (int i = 0; i < RING.length; i++) RING[i] = new MetricEvent(); }
private static final AtomicInteger INDEX = new AtomicInteger(0);

MetricEvent event = RING[INDEX.getAndIncrement() & 8191];
event.set("bid.processed", System.nanoTime(), tags);
metricsPublisher.submit(event);
```

## Results After Optimization

```
Allocation Rate:
  Before: 1000MB/s (100K req/s × 10KB/req)
  After:   180MB/s (100K req/s × 1.8KB/req)

GC Frequency:
  Before: ZGC collecting every 1 second
  After:  ZGC collecting every 6 seconds

GC CPU Overhead:
  Before: 15%
  After:  3%

Freed CPU for application:
  +12% → can handle 112K req/s on same hardware
```

## What You Learned

- **Allocation rate** — the speed at which garbage is created, drives GC frequency
- **TLAB** — thread-local allocation buffers make allocation fast but don't reduce GC work
- **Escape analysis** — JIT eliminates heap allocations for non-escaping objects
- **Object reuse** — ThreadLocal pools eliminate per-request allocations
- **Streaming serialization** — avoid intermediate String/byte[] copies
- **Ring buffers** — pre-allocated arrays for high-frequency events
- **Measurement** — JFR shows allocation by call site, enabling targeted optimization

Allocation pressure is under control. But when something goes wrong — an unexpected 3-second pause, a sudden spike in GC frequency — you need to diagnose it from logs. The GC log is your primary diagnostic tool, and reading it fluently is a core skill.

Chapter 9: reading GC logs like a pro.

---

[← Chapter 7: Tuning Heap Size](chapter-07-heap-sizing.md) | [Chapter 9: GC Logging & Analysis →](chapter-09-logging.md)

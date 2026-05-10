# Chapter 5: G1 Deep Dive

[← Chapter 4: Choosing a Collector](chapter-04-collectors.md) | [Chapter 6: ZGC: Sub-Millisecond Pauses →](chapter-06-zgc.md)

---

## The Problem

You've tuned G1 to 15ms pauses. Viktor is satisfied — for now. But the SRE dashboard shows occasional spikes:

```
[14:22:01.100] GC(5012) Pause Young (Normal) 1840M->92M(4096M) 9.2ms
[14:22:01.900] GC(5013) Pause Young (Normal) 1840M->88M(4096M) 8.7ms
[14:22:02.700] GC(5014) Pause Young (Concurrent Start) 1840M->94M(4096M) 11.4ms
[14:22:03.500] GC(5015) Pause Young (Normal) 1840M->91M(4096M) 9.1ms
[14:22:04.300] GC(5016) Pause Mixed 2240M->1680M(4096M) 48.2ms  ← SPIKE
```

48ms. Three times the target. During a mixed collection, G1 tried to evacuate old gen regions that had too many live objects. The copy took longer than expected.

Sasha: "It's always the mixed collections. Young GCs are fine. But every few minutes, a mixed collection blows past our 20ms target."

To fix this, you need to understand how G1 actually works — regions, remembered sets, and the mixed collection algorithm.

## G1's Region-Based Design

G1 doesn't use contiguous young/old generations. It divides the heap into equal-sized **regions** (default: 2048 regions):

```
┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
│ E  │ E  │ E  │ S  │ O  │ O  │ O  │ H  │ H  │ F  │
├────┼────┼────┼────┼────┼────┼────┼────┼────┼────┤
│ E  │ E  │ O  │ O  │ O  │ F  │ F  │ O  │ E  │ E  │
├────┼────┼────┼────┼────┼────┼────┼────┼────┼────┤
│ O  │ O  │ F  │ F  │ E  │ E  │ O  │ O  │ S  │ F  │
└────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘

E = Eden    S = Survivor    O = Old    H = Humongous    F = Free
```

With a 4GB heap and 2048 regions: each region is **2MB**. Regions can change role — a free region becomes Eden, then after collection becomes free again.

Check your region size:

```bash
java -XX:+UseG1GC -Xmx4g -Xlog:gc+heap=info -version
```

```
Heap region size: 2097152 (2MB)
```

Or set it explicitly:

```bash
-XX:G1HeapRegionSize=4m  # Must be power of 2, between 1MB and 32MB
```

## Mixed Collections: The Heart of G1

G1's key innovation: it doesn't collect all of old gen at once. It picks the regions with the most garbage and collects them alongside young gen. This is a **mixed collection**.

The process:

```
1. Concurrent Marking (runs while app works)
   → Identifies which old gen regions have the most garbage

2. Mixed Collection (stop-the-world, but short)
   → Evacuates young gen + selected old gen regions
   → Picks regions with highest garbage ratio first ("Garbage First")
```

The GC log shows the selection:

```
[14:22:04.300] GC(5016) Pause Mixed
[14:22:04.300] GC(5016)   Collected regions: 180 young + 42 old
[14:22:04.300] GC(5016)   Old regions selected: 42 of 312 candidates
[14:22:04.300] GC(5016)   Predicted pause: 18.4ms
[14:22:04.348] GC(5016)   Actual pause: 48.2ms  ← prediction was wrong
```

G1 predicted 18ms but took 48ms. Why? The selected old regions had more live objects than expected. Copying live objects is the expensive part.

## The Pause Time Target

`-XX:MaxGCPauseMillis` is a **target**, not a guarantee:

```bash
-XX:MaxGCPauseMillis=20  # "Try to keep pauses under 20ms"
```

G1 uses historical data to predict how long evacuating each region will take. It selects regions until the predicted time approaches the target. But predictions can be wrong:

- A region's liveness changed since marking
- Object graphs are deeper than expected (more pointer chasing)
- OS scheduling delays

Tuning the target:

```bash
# Aggressive (fewer old regions per mixed GC, more mixed GCs needed)
-XX:MaxGCPauseMillis=10

# Relaxed (more old regions per mixed GC, fewer total mixed GCs)
-XX:MaxGCPauseMillis=50
```

Lower target = more predictable but slower old gen reclamation. If you set it too low, G1 can't collect old gen fast enough and falls back to a Full GC.

## Humongous Objects

Any object larger than **half a region** is "humongous." It gets special treatment:

```java
// With 2MB regions, anything > 1MB is humongous
byte[] largeBuffer = new byte[1_500_000];  // 1.5MB → humongous
```

Humongous objects:
- Allocated directly in old gen (skip Eden entirely)
- Occupy one or more contiguous regions
- Not moved during collection (too expensive to copy)
- Can cause fragmentation

BidStream's problem: serializing bid responses to JSON sometimes creates large byte arrays:

```java
// Bid response with 200 campaign scores — can exceed 1MB when serialized
String json = objectMapper.writeValueAsString(bidResponse);
byte[] payload = json.getBytes(StandardCharsets.UTF_8);
// If payload > 1MB → humongous allocation
```

Detect humongous allocations in GC logs:

```
[14:22:05.100] GC(5017) Humongous regions: 24
[14:22:05.100] GC(5017) Humongous reclaimed: 8
```

### Fixing Humongous Allocations

**Option 1:** Increase region size so fewer objects qualify as humongous:

```bash
-XX:G1HeapRegionSize=8m  # Now objects must be >4MB to be humongous
```

**Option 2:** Reduce object sizes:

```java
// Stream the response instead of buffering the entire JSON
try (OutputStream out = response.getOutputStream()) {
    objectMapper.writeValue(out, bidResponse);  // No intermediate byte[]
}
```

**Option 3:** Use G1's eager reclamation (Java 8u60+, improved in later versions):

```bash
-XX:+G1EagerReclaimHumongousObjects  # Default: true in Java 12+
```

## Tuning Mixed Collections

The 48ms spike happened because G1 selected too many old regions with high liveness. Tune the selection:

```bash
# How many old regions to include per mixed GC (default: 10% of old regions)
-XX:G1MixedGCCountTarget=8  # Spread old gen collection over 8 mixed GCs

# Only collect regions with < 85% live data (default: 85%)
-XX:G1MixedGCLiveThresholdPercent=65  # Skip regions that are mostly live

# Stop mixed GCs when this much old gen is reclaimable (default: 5%)
-XX:G1HeapWastePercent=10  # Stop earlier, accept some waste
```

The BidStream fix:

```bash
java -Xms4g -Xmx4g \
     -XX:+UseG1GC \
     -XX:MaxGCPauseMillis=15 \
     -XX:G1HeapRegionSize=4m \
     -XX:G1MixedGCLiveThresholdPercent=65 \
     -XX:G1MixedGCCountTarget=12 \
     -XX:InitiatingHeapOccupancyPercent=30 \
     -Xlog:gc*:file=gc.log:time,level,tags \
     BidServer
```

Results:

```
Before: Mixed collections occasionally spike to 48ms
After:  Mixed collections consistently 10-16ms
         (more mixed GCs, but each is shorter and predictable)
```

## G1 Summary: The Complete Picture

```
Normal operation:
  Eden fills → Young GC (8-12ms) → survivors age → some promote to old

Old gen filling:
  IHOP reached → Concurrent Marking starts (no pause)
  Marking completes → identifies garbage-heavy old regions

Mixed collections:
  Young GC + selected old regions → reclaims old gen incrementally (10-16ms)
  Repeats until old gen is healthy

Emergency:
  Old gen fills faster than mixed GCs reclaim → Full GC (200ms+)
  This should NEVER happen with proper tuning
```

## When G1 Isn't Enough

G1's pauses are bounded but not eliminated. Even a well-tuned G1:

- Young GC: 5-15ms (proportional to survivor count)
- Mixed GC: 10-20ms (proportional to selected regions' live data)
- Rare spikes: 30-50ms (prediction errors)

For BidStream, 15ms pauses mean 750 bids stalled per pause. At one pause per second, that's 750 bids/second experiencing elevated latency. The p99 stays at 18ms.

AdPulse's ZGC achieves <1ms pauses. Zero bids stalled. Their p99 is 2ms.

Viktor: "G1 got us from $100K/month to $8K/month in lost revenue. ZGC gets us to zero. Make it happen."

## What You Learned

- **Regions** — G1 divides heap into equal-sized regions that change roles dynamically
- **Mixed collections** — collect young gen + selected old gen regions together
- **Pause time target** — MaxGCPauseMillis is a goal, not a guarantee
- **Humongous objects** — objects > half a region get special (worse) treatment
- **Region size** — affects humongous threshold and collection granularity
- **Prediction errors** — G1 estimates pause time from history, can be wrong
- **Tuning knobs** — MixedGCLiveThresholdPercent, MixedGCCountTarget, IHOP

G1 is excellent for most workloads. But when you need pauses measured in microseconds, not milliseconds, you need a fundamentally different approach. ZGC doesn't just tune the pause — it eliminates it.

Chapter 6: how ZGC achieves sub-millisecond pauses.

---

[← Chapter 4: Choosing a Collector](chapter-04-collectors.md) | [Chapter 6: ZGC: Sub-Millisecond Pauses →](chapter-06-zgc.md)

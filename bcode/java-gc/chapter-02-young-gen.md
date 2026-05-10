# Chapter 2: Young Generation

[← Chapter 1: The Pause That Lost Money](chapter-01-the-pause.md) | [Chapter 3: Old Generation →](chapter-03-old-gen.md)

---

## The Problem

After the Full GC incident, you enable detailed GC logging and watch the pattern:

```
[09:20:01.044] GC(912) Pause Young (Normal) (G1 Evacuation Pause)
[09:20:01.052] GC(912) Pause Young 2048M->84M(4096M) 8.112ms
[09:20:01.103] GC(913) Pause Young (Normal) (G1 Evacuation Pause)
[09:20:01.110] GC(913) Pause Young 2048M->81M(4096M) 7.845ms
[09:20:01.162] GC(914) Pause Young (Normal) (G1 Evacuation Pause)
[09:20:01.170] GC(914) Pause Young 2048M->86M(4096M) 7.923ms
```

Minor GCs every **60 milliseconds**. Each one pauses for ~8ms. That's 8ms of frozen threads, 16 times per second. At 50K requests/second, each 8ms pause stalls 400 bids.

Sasha: "The Full GCs are gone since we tuned old gen. But now we're getting 8ms hiccups constantly. The p99 latency is 12ms instead of 5ms."

Viktor: "8ms is better than 200ms. But our competitors respond in 3ms. We're losing auctions we should win."

The young generation is collecting too often. You need to understand why.

## How Eden Works

Every `new` keyword allocates in **Eden**. Eden is the nursery — objects are born here and most die here.

```
┌─────────────────── Young Generation ───────────────────┐
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │                    EDEN                          │   │
│  │  [bid-req] [scores] [list] [map] [response]     │   │
│  │  [bid-req] [scores] [list] [map] [response]     │   │
│  │  ... 50,000 bids/sec worth of objects ...        │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────────┐         ┌──────────────┐             │
│  │  Survivor 0  │         │  Survivor 1  │             │
│  │  (from-space)│         │  (to-space)  │             │
│  │  age=1: 12MB │         │   (empty)    │             │
│  └──────────────┘         └──────────────┘             │
└─────────────────────────────────────────────────────────┘
```

BidStream's bid processing creates ~10KB per request:

```java
private static void processSingleBid() {
    byte[] request = new byte[2048];           // 2KB - dies immediately
    List<String> eligible = new ArrayList<>();  // 200B - dies immediately
    for (int i = 0; i < 50; i++) {
        eligible.add("campaign-" + i);         // 50 strings - die immediately
    }
    Map<String, Double> scores = new HashMap<>(); // 2KB - dies immediately
    byte[] response = new byte[512];           // 512B - dies immediately
}
```

At 50K requests/second × 10KB = **500MB/second** of Eden allocations. With a 2GB Eden, it fills in 4 seconds. But our logs show minor GC every 60ms — Eden is only ~30MB.

Why so small? The default young generation ratio. Let's check:

```bash
java -XX:+PrintFlagsFinal -version 2>&1 | grep -i "NewRatio\|NewSize\|MaxNewSize"
```

```
uintx NewRatio = 2
uintx NewSize = 1363144
uintx MaxNewSize = 1431699456
```

`NewRatio=2` means old gen is 2× young gen. With 4GB heap: ~1.3GB young, ~2.7GB old. But G1 dynamically adjusts — under heavy allocation, it shrinks Eden to keep pause times short.

## Minor GC: What Actually Happens

When Eden fills up:

1. **Stop the world** (all threads pause)
2. **Scan GC roots** — find live objects referenced from stacks, statics
3. **Copy live objects** to a Survivor space
4. **Everything else in Eden is garbage** — the space is simply reclaimed (no scanning needed)
5. **Resume threads**

The key insight: minor GC time is proportional to **live objects**, not total Eden size. If 99% of Eden is garbage, the GC only copies the 1% that's alive.

```
Before Minor GC:
Eden: [████████████████████████████] 30MB used (29.7MB garbage, 0.3MB live)
S0:   [███] 3MB (survivors from last GC)
S1:   [   ] empty

After Minor GC:
Eden: [                            ] 0MB (reclaimed instantly)
S0:   [   ] empty (was from-space, now cleared)
S1:   [███] 3.3MB (0.3MB from Eden + survivors aged from S0)
```

## Survivor Spaces and Object Aging

Objects don't go directly from Eden to old gen. They pass through Survivor spaces, aging with each GC:

```java
// This object survives because it's referenced by a thread-local cache
ThreadLocal<BidContext> context = ThreadLocal.withInitial(BidContext::new);
```

Each time an object survives a minor GC, its **age** increments:

```
Age 0: Born in Eden
Age 1: Survived 1 minor GC → in Survivor
Age 2: Survived 2 minor GCs → still in Survivor
...
Age 15: Survived 15 minor GCs → PROMOTED to Old Gen
```

The threshold is controlled by `-XX:MaxTenuringThreshold` (default: 15 for G1).

Check the age distribution in GC logs:

```
[09:20:01.052] GC(912) Age table with threshold 15 (max threshold 15)
[09:20:01.052] GC(912) - age   1:    2841600 bytes,    2841600 total
[09:20:01.052] GC(912) - age   2:    1245184 bytes,    4086784 total
[09:20:01.052] GC(912) - age   3:     892416 bytes,    4979200 total
[09:20:01.052] GC(912) - age   4:     892416 bytes,    5871616 total
```

Most objects die at age 0 (never leave Eden). A few survive to age 1. Even fewer reach age 4+. Those are your long-lived objects heading for old gen.

## The Promotion Problem

BidStream has a thread-local connection pool that survives many GCs:

```java
private static final ThreadLocal<List<Connection>> connPool =
    ThreadLocal.withInitial(() -> {
        List<Connection> pool = new ArrayList<>();
        for (int i = 0; i < 5; i++) {
            pool.add(createConnection());
        }
        return pool;  // This list survives forever → promoted to old gen
    });
```

With 200 threads × 5 connections × ~2KB each = 2MB promoted per thread initialization. That's fine — it happens once. The problem is objects that survive *just long enough* to get promoted but then die:

```java
// A bid response cache — holds results for 30 seconds for deduplication
private static final Cache<String, BidResponse> recentBids =
    Caffeine.newBuilder()
        .expireAfterWrite(30, TimeUnit.SECONDS)
        .maximumSize(100_000)
        .build();
```

These entries survive 15+ minor GCs (at one GC per 60ms, that's only 900ms — well within the 30-second TTL). They get promoted to old gen, then die 29 seconds later. This is **premature promotion** — objects that belong in young gen but live just long enough to escape.

## Tuning Young Generation

### Option 1: Increase Eden Size

More Eden = less frequent minor GC = fewer pauses:

```bash
java -Xms4g -Xmx4g -XX:NewSize=2g -XX:MaxNewSize=2g ...
```

Result: minor GC every 4 seconds instead of 60ms. But each pause is longer (more live objects to copy). Tradeoff.

### Option 2: Increase Tenuring Threshold

Keep objects in Survivor longer before promoting:

```bash
java -XX:MaxTenuringThreshold=31 ...  # Max is 15 for G1, 15 for most collectors
```

G1 caps at 15. If objects survive 15 GCs in 900ms, they'll still get promoted before their 30-second TTL expires.

### Option 3: Increase Survivor Space

Larger survivors can hold more aging objects:

```bash
java -XX:SurvivorRatio=4 ...  # Eden:Survivor = 4:1 (default is 8:1)
```

More survivor space means objects can age longer without overflowing into old gen.

### The BidStream Fix

For BidStream, the right answer is a larger Eden with appropriately sized survivors:

```bash
java -Xms4g -Xmx4g \
     -XX:+UseG1GC \
     -XX:G1NewSizePercent=40 \
     -XX:G1MaxNewSizePercent=60 \
     -XX:MaxTenuringThreshold=15 \
     -XX:SurvivorRatio=6 \
     -Xlog:gc*,gc+age=debug:file=gc.log:time,level,tags \
     BidServer
```

Results:

```
Before: Minor GC every 60ms, 8ms pause, p99 latency 12ms
After:  Minor GC every 800ms, 12ms pause, p99 latency 6ms
```

Fewer pauses, slightly longer each, but the overall throughput and latency improve because threads spend less total time frozen.

## What You Learned

- **Eden** — where all new objects are allocated, collected by minor GC
- **Survivor spaces** — S0/S1 ping-pong, objects age here before promotion
- **Object aging** — each surviving GC increments age, promotion at threshold
- **Minor GC cost** — proportional to live objects, not Eden size
- **Premature promotion** — objects that survive just long enough to escape young gen
- **Tuning levers** — Eden size, survivor ratio, tenuring threshold
- **Allocation rate** — BidStream's 500MB/sec drives minor GC frequency

The young generation is under control. But those promoted objects — the campaign cache, the connection pools, the response cache entries — they're accumulating in old gen. When old gen fills up, you're back to the 200ms Full GC.

Chapter 3: what happens when old gen gets full.

---

[← Chapter 1: The Pause That Lost Money](chapter-01-the-pause.md) | [Chapter 3: Old Generation →](chapter-03-old-gen.md)

# Chapter 3: Old Generation

[← Chapter 2: Young Generation](chapter-02-young-gen.md) | [Chapter 4: Choosing a Collector →](chapter-04-collectors.md)

---

## The Problem

Two weeks after tuning young gen, Sasha messages at 2 AM:

"BidServer-03 just had a 340ms pause. First one in 14 days. But now they're happening every 45 minutes and getting longer. Last one was 380ms."

The GC log tells the story:

```
[02:14:07.881] GC(4012) Pause Full (G1 Compaction Pause)
[02:14:07.881] GC(4012) Phase 1: Mark live objects      112.4ms
[02:14:07.994] GC(4012) Phase 2: Prepare for compaction  18.2ms
[02:14:08.012] GC(4012) Phase 3: Adjust pointers         89.7ms
[02:14:08.102] GC(4012) Phase 4: Compact heap           119.3ms
[02:14:08.221] GC(4012) Pause Full 3891M->2104M(4096M) 339.6ms
```

Before: 3891MB used. After: 2104MB. The heap reclaimed 1787MB — but 2104MB is still alive. That's **2.1GB of live data** in old gen.

Two weeks ago, live data after Full GC was 1247MB. It's growing. Something is accumulating.

You check the campaign service: a new feature launched last week. Campaign targeting rules are now cached with a 6-hour TTL instead of being reloaded every request. The cache is growing.

```java
// The new campaign cache — seemed like a good idea
private static final LoadingCache<String, CampaignRules> rulesCache =
    Caffeine.newBuilder()
        .expireAfterWrite(6, TimeUnit.HOURS)
        .maximumSize(500_000)  // 500K entries × ~4KB each = 2GB
        .build(key -> loadRulesFromDB(key));
```

The cache promotes to old gen (entries live for hours), fills it up, and eventually triggers a Full GC to reclaim expired entries.

## How Old Generation Works

Old gen holds objects that survived enough minor GCs to be promoted. It's collected differently than young gen:

```
┌──────────────────── Old Generation ────────────────────┐
│                                                         │
│  [campaign-A][    ][campaign-B][conn-pool][    ][cache] │
│  [    ][campaign-C][    ][    ][thread-local][    ]     │
│  [cache][cache][    ][campaign-D][    ][cache][    ]    │
│                                                         │
│  [    ] = freed space (fragmentation)                   │
│  [xxxx] = live objects                                  │
└─────────────────────────────────────────────────────────┘
```

Unlike Eden (which is simply wiped clean), old gen accumulates objects over time. Dead objects leave gaps. Live objects are scattered. This is **fragmentation**.

## Major GC vs Full GC

These are different things:

| Type | What it collects | When it happens | Pause |
|------|-----------------|-----------------|-------|
| Minor GC | Young gen only | Eden full | 5-20ms |
| Major GC | Old gen (concurrent marking + mixed collection) | Old gen filling up | 10-50ms |
| Full GC | Everything + compaction | Old gen completely full, or major GC can't keep up | 100-500ms |

G1's **major GC** is actually a series of steps:
1. **Concurrent marking** — finds garbage in old gen while app runs (no pause)
2. **Mixed collections** — collects some old gen regions alongside young gen (short pauses)

A **Full GC** only happens when G1 falls behind — old gen fills faster than mixed collections can reclaim it.

## The Compaction Problem

After many cycles of promotion and collection, old gen looks like Swiss cheese:

```
Before compaction:
[LIVE][    ][LIVE][    ][    ][LIVE][    ][LIVE][    ]

After compaction:
[LIVE][LIVE][LIVE][LIVE][                              ]
                        ↑ contiguous free space
```

Compaction eliminates fragmentation but requires moving objects and updating all references. With 2GB of live data, that means copying 2GB and updating millions of pointers. Hence the 340ms pause.

## Watching Old Gen Fill Up

Enable old gen occupancy tracking:

```bash
java -Xms4g -Xmx4g \
     -XX:+UseG1GC \
     -Xlog:gc*,gc+heap=debug:file=gc.log:time,level,tags \
     BidServer
```

The log shows old gen growing over time:

```
[00:00:00] GC(1)    Old: 0MB
[00:15:00] GC(200)  Old: 412MB
[00:30:00] GC(400)  Old: 847MB
[01:00:00] GC(800)  Old: 1203MB
[02:00:00] GC(1600) Old: 1891MB   ← concurrent marking triggered
[02:05:00] GC(1620) Old: 1650MB   ← mixed collections reclaimed some
[02:30:00] GC(1800) Old: 2100MB   ← growing faster than reclaiming
[02:45:00] GC(1900) Old: 3891MB   ← FULL GC triggered
```

The **Initiating Heap Occupancy Percent** (IHOP) controls when concurrent marking starts:

```bash
-XX:InitiatingHeapOccupancyPercent=45  # default: 45% of heap
```

When old gen reaches 45% of total heap, G1 starts concurrent marking. If the promotion rate exceeds the reclamation rate, old gen still fills up and you get a Full GC.

## Promotion Rate

The rate at which objects move from young to old gen determines how fast old gen fills:

```
Promotion rate = (objects surviving MaxTenuringThreshold) per second
```

For BidStream, the promotion sources are:

```java
// 1. Campaign cache entries (intentional, long-lived)
rulesCache.get(campaignId);  // ~4KB per entry, lives 6 hours

// 2. Thread-local buffers (survive many GCs)
private static final ThreadLocal<ByteBuffer> buffer =
    ThreadLocal.withInitial(() -> ByteBuffer.allocate(8192));

// 3. Premature promotion (bid responses surviving 15 GCs)
recentBids.put(bidId, response);  // lives 30 seconds, but promoted after 900ms
```

Measure promotion rate from GC logs:

```bash
grep "promoted" gc.log | tail -5
```

```
[02:00:01] GC(1601) Promoted: 12.4MB
[02:00:02] GC(1602) Promoted: 11.8MB
[02:00:03] GC(1603) Promoted: 13.1MB
[02:00:04] GC(1604) Promoted: 12.9MB
[02:00:05] GC(1605) Promoted: 14.2MB
```

~13MB/second promoted to old gen. At that rate, 2.7GB of old gen free space fills in ~3.5 minutes. But concurrent marking and mixed collections reclaim some, extending the time to ~45 minutes before a Full GC.

## Fixing the Old Gen Problem

### Strategy 1: Reduce Promotion Rate

The 30-second bid response cache is the biggest offender — entries get promoted after 900ms but live for 30 seconds:

```java
// Before: entries promoted to old gen, die there
Cache<String, BidResponse> recentBids = Caffeine.newBuilder()
    .expireAfterWrite(30, TimeUnit.SECONDS)
    .build();

// After: shorter TTL keeps entries in young gen
Cache<String, BidResponse> recentBids = Caffeine.newBuilder()
    .expireAfterWrite(5, TimeUnit.SECONDS)  // dies before promotion
    .build();
```

5 seconds ÷ 60ms per GC = ~83 GCs. Still promoted. The math doesn't work with 60ms GC intervals.

With the tuned Eden from Chapter 2 (800ms between GCs): 5 seconds ÷ 800ms = ~6 GCs. Objects die at age 6, well before the threshold of 15. **No promotion.**

### Strategy 2: Trigger Concurrent Marking Earlier

Start reclaiming old gen before it's critical:

```bash
-XX:InitiatingHeapOccupancyPercent=30  # Start marking at 30% instead of 45%
```

This gives G1 more runway to reclaim old gen before it fills up.

### Strategy 3: Size the Cache Appropriately

The campaign cache was set to 500K entries without measuring actual usage:

```java
// Check actual cache stats
System.out.println("Cache size: " + rulesCache.estimatedSize());
System.out.println("Hit rate: " + rulesCache.stats().hitRate());
```

Output: only 50K entries are ever active. The 500K limit was 10× too high. Reducing it caps old gen growth:

```java
Cache<String, CampaignRules> rulesCache = Caffeine.newBuilder()
    .expireAfterWrite(6, TimeUnit.HOURS)
    .maximumSize(60_000)  // 60K × 4KB = 240MB (manageable)
    .build(key -> loadRulesFromDB(key));
```

### The Combined Fix

```bash
java -Xms4g -Xmx4g \
     -XX:+UseG1GC \
     -XX:InitiatingHeapOccupancyPercent=30 \
     -XX:G1NewSizePercent=40 \
     -XX:G1MaxNewSizePercent=60 \
     -Xlog:gc*:file=gc.log:time,level,tags \
     BidServer
```

Plus the code changes (smaller cache, shorter TTL on bid responses).

Results after 48 hours:

```
Before: Full GC every 45 minutes, 340ms pause
After:  No Full GCs. Mixed collections every 5 minutes, 15ms pause.
Old gen stable at ~800MB (campaign cache + connection pools + thread locals)
```

## What You Learned

- **Old generation** — holds promoted objects, collected by major/full GC
- **Fragmentation** — dead objects leave gaps, compaction fixes it but is expensive
- **Major vs Full GC** — major is incremental (mixed collections), full is stop-the-world
- **IHOP** — controls when concurrent marking starts (tune lower for safety margin)
- **Promotion rate** — the speed at which objects flow into old gen
- **Premature promotion** — objects that get promoted but die shortly after
- **Cache sizing** — unbounded caches are the #1 cause of old gen pressure

Old gen is stable now. Minor GCs are infrequent. But you're still using G1 with default settings. Is G1 even the right collector for BidStream's workload? Maybe Parallel GC would give better throughput. Maybe ZGC would eliminate pauses entirely.

Chapter 4: choosing the right collector.

---

[← Chapter 2: Young Generation](chapter-02-young-gen.md) | [Chapter 4: Choosing a Collector →](chapter-04-collectors.md)

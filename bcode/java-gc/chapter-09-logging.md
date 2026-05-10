# Chapter 9: GC Logging & Analysis

[← Chapter 8: Allocation Pressure](chapter-08-allocation.md) | [Chapter 10: Memory Leaks →](chapter-10-leaks.md)

---

## The Problem

3 AM. Sasha's pager fires:

"BidServer-02 had a 3.2-second pause. One pause. Then it recovered. No OOM, no crash. Just 3.2 seconds of silence. 160,000 lost bids."

By the time you wake up, the server is healthy. No reproduction steps. The only evidence is the GC log. If you can't read it, you can't diagnose it.

You open the 400MB gc.log file. Thousands of entries. Somewhere in there is the story of what happened at 3:14 AM.

## Unified Logging (Java 9+)

Java 9 replaced the old `-XX:+PrintGCDetails` with a unified logging framework. The flag:

```bash
-Xlog:gc*:file=gc.log:time,level,tags:filecount=10,filesize=100m
```

Breaking it down:

```
-Xlog:                          # Unified logging prefix
  gc*                           # What: all GC-related tags
  :file=gc.log                  # Where: write to file
  :time,level,tags              # Decorators: timestamp, log level, tag names
  :filecount=10,filesize=100m   # Rotation: 10 files × 100MB = 1GB max
```

### Tag Selection

```bash
# Everything GC-related (verbose, good for debugging)
-Xlog:gc*:file=gc.log:time,level,tags

# Just pause events (minimal, good for production monitoring)
-Xlog:gc:file=gc.log:time

# Specific subsystems
-Xlog:gc+heap=debug,gc+age=debug,gc+phases=info:file=gc.log:time,level,tags
```

### Log Levels

```
trace  → extremely verbose (allocation events)
debug  → detailed (age tables, region details)
info   → standard (pause times, heap sizes)
warning → problems (allocation stalls, to-space exhaustion)
error  → failures (OOM)
```

## Reading a G1 GC Log Line by Line

Here's a complete young GC entry:

```
[2024-01-15T09:14:22.100+0000][info][gc,start    ] GC(5012) Pause Young (Normal) (G1 Evacuation Pause)
[2024-01-15T09:14:22.100+0000][info][gc,task     ] GC(5012) Using 8 workers of 8 for evacuation
[2024-01-15T09:14:22.108+0000][info][gc,phases   ] GC(5012)   Pre Evacuate Collection Set: 0.2ms
[2024-01-15T09:14:22.108+0000][info][gc,phases   ] GC(5012)   Merge Heap Roots: 0.4ms
[2024-01-15T09:14:22.108+0000][info][gc,phases   ] GC(5012)   Evacuate Collection Set: 6.8ms
[2024-01-15T09:14:22.108+0000][info][gc,phases   ] GC(5012)   Post Evacuate Collection Set: 0.9ms
[2024-01-15T09:14:22.108+0000][info][gc,phases   ] GC(5012)   Other: 0.3ms
[2024-01-15T09:14:22.108+0000][info][gc,heap     ] GC(5012) Eden regions: 180->0(180)
[2024-01-15T09:14:22.108+0000][info][gc,heap     ] GC(5012) Survivor regions: 12->14(24)
[2024-01-15T09:14:22.108+0000][info][gc,heap     ] GC(5012) Old regions: 412->414
[2024-01-15T09:14:22.108+0000][info][gc,heap     ] GC(5012) Humongous regions: 4->2
[2024-01-15T09:14:22.108+0000][info][gc          ] GC(5012) Pause Young (Normal) 1840M->92M(4096M) 8.6ms
```

Reading it:

| Line | Meaning |
|------|---------|
| `Pause Young (Normal)` | Minor GC, not triggered by emergency |
| `Using 8 workers` | Parallel GC threads |
| `Evacuate Collection Set: 6.8ms` | The expensive part — copying live objects |
| `Eden regions: 180->0` | All 180 Eden regions collected |
| `Survivor regions: 12->14` | 12 survivor regions before, 14 after (2 promoted from Eden) |
| `Old regions: 412->414` | 2 objects promoted to old gen |
| `Humongous regions: 4->2` | 2 humongous objects reclaimed |
| `1840M->92M(4096M) 8.6ms` | 1840MB used → 92MB after, 4GB heap, 8.6ms pause |

## Reading a ZGC Log

```
[09:14:22.100] GC(412) Garbage Collection (Proactive)
[09:14:22.100] GC(412) Using 4 workers
[09:14:22.100] GC(412) Pause Mark Start 0.019ms
[09:14:22.108] GC(412) Concurrent Mark 8.412ms
[09:14:22.108] GC(412) Pause Mark End 0.024ms
[09:14:22.110] GC(412) Concurrent Mark Free 1.204ms
[09:14:22.112] GC(412) Concurrent Process Non-Strong References 2.104ms
[09:14:22.114] GC(412) Concurrent Reset Relocation Set 0.412ms
[09:14:22.116] GC(412) Concurrent Select Relocation Set 1.891ms
[09:14:22.116] GC(412) Pause Relocate Start 0.017ms
[09:14:22.122] GC(412) Concurrent Relocate 5.891ms
[09:14:22.122] GC(412) Load: 2.14/1.89/1.42
[09:14:22.122] GC(412) MMU: 2ms/99.4%, 5ms/99.7%, 10ms/99.9%, 20ms/100.0%
[09:14:22.122] GC(412) Mark: 4096M(100%) 2841M(69%) 1247M(30%)
[09:14:22.122] GC(412)       Used: 2841M  Reclaimed: 1594M  Garbage: 1594M(39%)
```

Key lines:

| Line | Meaning |
|------|---------|
| `Proactive` | ZGC decided to collect before heap was full |
| `Pause Mark Start 0.019ms` | STW pause — 19 microseconds |
| `Concurrent Mark 8.412ms` | Marking happened while app ran |
| `MMU: 2ms/99.4%` | Minimum Mutator Utilization — app got 99.4% of CPU in any 2ms window |
| `Reclaimed: 1594M` | Freed 1.5GB |

## Diagnosing the 3 AM Incident

Back to Sasha's 3.2-second pause. You search the log:

```bash
grep -A 20 "3[0-9][0-9][0-9]\." gc.log | head -40
# Looking for any pause > 3000ms
```

Found it:

```
[2024-01-15T03:14:18.100] GC(8847) Pause Full (System.gc()) 
[2024-01-15T03:14:21.312] GC(8847) Pause Full 3412M->891M(4096M) 3212.4ms
```

**`System.gc()`**. Someone called `System.gc()` explicitly. A Full GC was forced.

```bash
grep -r "System.gc" src/
```

```
src/main/java/com/bidstream/cache/CacheWarmer.java:42:  System.gc(); // "clean up before warming"
```

The cache warming job runs at 3 AM. A developer added `System.gc()` thinking it would "clean up" before loading fresh data. Instead, it triggered a 3.2-second Full GC on a production server.

Fix: remove the call and add `-XX:+DisableExplicitGC`:

```bash
-XX:+DisableExplicitGC  # Ignores System.gc() calls
```

## Analysis Tools

### GCEasy (Online)

Upload your gc.log to [gceasy.io](https://gceasy.io). It produces:
- Pause time distribution (histogram)
- Heap usage over time (graph)
- Allocation rate and promotion rate
- Recommendations

### GCViewer (Desktop)

```bash
java -jar gcviewer.jar gc.log
```

Shows pause times as a timeline — spikes are immediately visible.

### JDK Mission Control (JFR)

```bash
# Start recording
jcmd <pid> JFR.start duration=300s filename=gc-analysis.jfr

# Open in JMC
jmc gc-analysis.jfr
```

JFR correlates GC events with application behavior — you can see which threads were allocating most before a GC triggered.

## Essential Log Patterns to Recognize

### Pattern: Allocation Failure (heap too small)

```
GC(100) Pause Young (Allocation Failure)
```

Eden is full, can't allocate. Normal for G1 — this triggers minor GC.

### Pattern: Concurrent Mode Failure (G1 falling behind)

```
GC(200) To-space exhausted
GC(201) Pause Full (G1 Evacuation Pause)
```

G1 couldn't find free regions during evacuation. Emergency Full GC. Fix: lower IHOP, increase heap.

### Pattern: Allocation Stall (ZGC can't keep up)

```
Allocation Stall (bid-worker-47) 84.2ms
```

ZGC is collecting but the app is allocating faster. Fix: increase heap or reduce allocation rate.

### Pattern: Humongous Allocation

```
GC(300) Pause Young (Concurrent Start) (G1 Humongous Allocation)
```

A large object triggered a GC. Fix: increase region size or reduce object size.

### Pattern: Metadata GC Threshold

```
GC(400) Pause Full (Metadata GC Threshold)
```

Metaspace is full (too many loaded classes). Common with frameworks that generate classes dynamically. Fix: `-XX:MaxMetaspaceSize=512m`.

## Production Logging Configuration

BidStream's production GC logging:

```bash
java -XX:+UseZGC \
     -Xms4g -Xmx4g \
     -Xlog:gc*:file=/var/log/bidserver/gc.log:time,level,tags:filecount=10,filesize=100m \
     -Xlog:gc:stdout:time \
     -XX:+DisableExplicitGC \
     BidServer
```

- Detailed logs to file (for post-mortem analysis)
- Summary to stdout (for container log aggregation)
- 10 rotated files × 100MB = 1GB max disk usage
- Explicit GC disabled

## What You Learned

- **Unified logging** — `-Xlog:gc*` replaces old `-XX:+PrintGCDetails`
- **Log decorators** — time, level, tags for structured parsing
- **Reading G1 logs** — phases, region counts, pause breakdown
- **Reading ZGC logs** — concurrent phases, MMU, pause durations
- **Diagnosis workflow** — grep for anomalies, correlate with timestamps
- **Common patterns** — allocation failure, to-space exhaustion, stalls
- **Tools** — GCEasy, GCViewer, JFR/JMC for visual analysis
- **DisableExplicitGC** — prevent rogue `System.gc()` calls

GC logs tell you what the collector is doing. But sometimes the problem isn't the collector — it's a memory leak. The heap grows slowly, GC reclaims less each cycle, and after 3 days the JVM OOMs at 3 AM.

Chapter 10: finding and fixing memory leaks.

---

[← Chapter 8: Allocation Pressure](chapter-08-allocation.md) | [Chapter 10: Memory Leaks →](chapter-10-leaks.md)

# Chapter 12: Production GC Strategy

[← Chapter 11: Off-Heap & Direct Memory](chapter-11-off-heap.md)

---

## The Problem (Solved)

It's been three months since you started tuning BidStream's GC. Viktor pulls up the before/after:

```
                        Before          After
─────────────────────────────────────────────────────
GC Pauses (max)         212ms           0.08ms
p99 Latency             42ms            4.3ms
Lost Auctions/month     ~3,000,000      0
Revenue Impact          -$100K/month    $0
OOM Incidents           2/month         0
Container Restarts      8/month         0
```

"Zero lost auctions. Zero OOMs. Same hardware. You just changed how we talk to the garbage collector."

This chapter is the reference — the complete production configuration, monitoring setup, and tuning workflow that got BidStream here.

## The Complete JVM Configuration

### BidStream Real-Time Bidding Servers (10 JVMs)

```bash
#!/bin/bash
# bidserver-start.sh — Production JVM configuration

exec java \
    # Collector: ZGC for sub-millisecond pauses
    -XX:+UseZGC \
    -XX:+ZProactive \
    \
    # Heap: 3× live data (1.15GB live → 4GB heap)
    -Xms4g -Xmx4g \
    -XX:+AlwaysPreTouch \
    \
    # Direct memory: capped for predictable container sizing
    -XX:MaxDirectMemorySize=512m \
    \
    # Metaspace: bounded to prevent classloader leaks
    -XX:MaxMetaspaceSize=300m \
    \
    # Threads: reduced stack size (default 1MB is excessive)
    -Xss512k \
    \
    # GC Logging: detailed to file, summary to stdout
    -Xlog:gc*:file=/var/log/bidserver/gc.log:time,level,tags:filecount=10,filesize=100m \
    -Xlog:gc:stdout:time \
    \
    # Diagnostics: heap dump on OOM, NMT for native memory tracking
    -XX:+HeapDumpOnOutOfMemoryError \
    -XX:HeapDumpPath=/var/dumps/bidserver-$(date +%Y%m%d-%H%M%S).hprof \
    -XX:NativeMemoryTracking=summary \
    \
    # Safety: disable explicit GC, enable error file
    -XX:+DisableExplicitGC \
    -XX:ErrorFile=/var/log/bidserver/hs_err_%p.log \
    \
    # JFR: always-on with low overhead
    -XX:StartFlightRecording=disk=true,maxsize=500m,maxage=24h,dumponexit=true,filename=/var/log/bidserver/flight.jfr \
    \
    # Application
    -jar /opt/bidserver/bidserver.jar
```

### BidStream Batch Analytics (2 JVMs)

```bash
exec java \
    # Collector: Parallel for maximum throughput
    -XX:+UseParallelGC \
    -XX:ParallelGCThreads=8 \
    \
    # Heap: large for batch processing
    -Xms8g -Xmx8g \
    -XX:+AlwaysPreTouch \
    \
    # GC Logging
    -Xlog:gc*:file=/var/log/analytics/gc.log:time,level,tags:filecount=5,filesize=50m \
    \
    # Diagnostics
    -XX:+HeapDumpOnOutOfMemoryError \
    -XX:HeapDumpPath=/var/dumps/ \
    \
    -jar /opt/analytics/analytics.jar
```

### BidStream Campaign API (3 JVMs)

```bash
exec java \
    # Collector: G1 for balanced latency/throughput
    -XX:+UseG1GC \
    -XX:MaxGCPauseMillis=50 \
    -XX:InitiatingHeapOccupancyPercent=35 \
    \
    # Heap
    -Xms2g -Xmx2g \
    \
    # GC Logging
    -Xlog:gc*:file=/var/log/campaign-api/gc.log:time,level,tags:filecount=5,filesize=50m \
    \
    -jar /opt/campaign-api/campaign-api.jar
```

## Monitoring with Prometheus + Grafana

### Key Metrics to Export

```java
// GC pause duration (histogram)
GarbageCollectorMXBean gc = ...;
metrics.timer("jvm.gc.pause", Tags.of("collector", gc.getName()))
    .record(pauseDuration, TimeUnit.MILLISECONDS);

// Heap usage after GC (gauge — for leak detection)
metrics.gauge("jvm.heap.used_after_gc", usedAfterGc);

// Allocation rate (counter)
metrics.counter("jvm.gc.allocation.rate").increment(bytesAllocated);

// Direct buffer usage (gauge)
metrics.gauge("jvm.direct.memory.used", directPool.getMemoryUsed());

// Thread count (gauge)
metrics.gauge("jvm.threads.live", threadMXBean.getThreadCount());
```

### Grafana Dashboard Panels

```
Row 1: GC Health
  - Panel: GC Pause Duration (p50, p95, p99) — line chart
  - Panel: GC Frequency (collections/minute) — line chart
  - Panel: GC CPU Time (%) — gauge

Row 2: Memory
  - Panel: Heap Used vs Max — area chart
  - Panel: Used After GC (trend line) — line chart with linear regression
  - Panel: Direct Buffer Usage — line chart
  - Panel: Container RSS vs Limit — area chart

Row 3: Application Impact
  - Panel: Request Latency (p50, p99) — line chart
  - Panel: Allocation Rate (MB/s) — line chart
  - Panel: Promotion Rate (MB/s) — line chart
```

### Alerting Rules

```yaml
groups:
  - name: jvm-gc-alerts
    rules:
      # ZGC allocation stall (immediate impact)
      - alert: ZGCAllocationStall
        expr: increase(jvm_gc_stall_total[5m]) > 0
        for: 0m
        labels:
          severity: critical
        annotations:
          summary: "ZGC allocation stall detected on {{ $labels.instance }}"

      # GC pause exceeds threshold
      - alert: GCPauseTooLong
        expr: jvm_gc_pause_seconds_max > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "GC pauses exceeding 50ms on {{ $labels.instance }}"

      # Memory leak detection (heap growing after GC)
      - alert: PossibleMemoryLeak
        expr: deriv(jvm_heap_used_after_gc_bytes[24h]) > 500000
        for: 6h
        labels:
          severity: warning
        annotations:
          summary: "Heap growing {{ $value | humanize }}/hour after GC"

      # Container approaching memory limit
      - alert: ContainerMemoryHigh
        expr: container_memory_rss / container_spec_memory_limit > 0.85
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "Container RSS at {{ $value | humanizePercentage }} of limit"

      # GC overhead too high (spending too much time in GC)
      - alert: GCOverheadHigh
        expr: rate(jvm_gc_time_seconds_total[5m]) > 0.15
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "GC consuming >15% CPU on {{ $labels.instance }}"
```

## The Tuning Workflow

When a GC problem appears in production, follow this workflow:

```
1. DETECT
   └─ Alert fires (pause too long, stall, memory growing)

2. MEASURE
   └─ Check GC logs: what type of GC? How long? What triggered it?
   └─ Check metrics: allocation rate, promotion rate, heap usage trend

3. DIAGNOSE
   └─ Pause too long?
   │   └─ G1: check mixed collection regions, humongous objects
   │   └─ ZGC: check allocation stalls (heap too small)
   │   └─ Full GC: check trigger (System.gc? Allocation failure? Metadata?)
   └─ Memory growing?
   │   └─ Heap growing after GC → memory leak (Chapter 10)
   │   └─ RSS growing, heap stable → off-heap leak (Chapter 11)
   └─ GC too frequent?
       └─ High allocation rate → reduce garbage (Chapter 8)
       └─ Eden too small → increase young gen (Chapter 2)

4. FIX
   └─ Code change (reduce allocations, fix leak, bound cache)
   └─ JVM flag change (heap size, IHOP, region size)
   └─ Architecture change (different collector, off-heap storage)

5. VERIFY
   └─ Deploy to canary
   └─ Compare metrics: before vs after
   └─ Confirm fix holds for 48+ hours
   └─ Roll out to fleet
```

## Java Flight Recorder: Always-On Profiling

JFR runs continuously with <2% overhead. When something goes wrong, you have the recording:

```bash
# Always-on recording (configured in startup script above)
-XX:StartFlightRecording=disk=true,maxsize=500m,maxage=24h,dumponexit=true

# Dump the current recording on demand
jcmd <pid> JFR.dump filename=/tmp/incident.jfr

# Start a focused recording for investigation
jcmd <pid> JFR.start duration=300s filename=/tmp/focused.jfr settings=profile
```

JFR captures:
- GC events (pauses, phases, heap sizes)
- Allocation profiling (which methods allocate most)
- Thread states (blocked, waiting, running)
- Lock contention
- I/O operations

Open in JDK Mission Control for visual analysis.

## Runbook: GC Incident Response

```markdown
## GC Incident Runbook

### Symptoms: High latency spike (p99 > 50ms)
1. Check GC log: `grep "Pause" /var/log/bidserver/gc.log | tail -20`
2. If Full GC: check trigger reason
   - System.gc() → find and remove the call
   - Allocation Failure → heap too small or leak
   - Metadata GC → increase MaxMetaspaceSize
3. If ZGC stall: `grep "Allocation Stall" gc.log`
   - Increase heap or reduce allocation rate
4. Dump JFR: `jcmd <pid> JFR.dump filename=/tmp/incident.jfr`

### Symptoms: OOM Kill (container restarted)
1. Check for heap dump: `ls /var/dumps/`
2. If heap dump exists: analyze with MAT
3. If no heap dump: likely native memory
   - Check NMT: `jcmd <pid> VM.native_memory summary`
   - Check direct buffers: look at BufferPool MXBean metrics
4. Check container RSS history in Prometheus

### Symptoms: Gradual performance degradation
1. Check "used after GC" trend in Grafana
2. If growing: memory leak → take heap dumps 24h apart, compare in MAT
3. If stable: check allocation rate trend
   - Growing allocation rate → new code path creating more garbage
   - Stable allocation rate → check for CPU throttling or noisy neighbor
```

## What Changed: The Journey

| Chapter | Problem | Fix | Impact |
|---------|---------|-----|--------|
| 1 | 212ms Full GC | Understood the problem | — |
| 2 | Minor GC every 60ms | Tuned Eden size | p99: 12ms → 6ms |
| 3 | Full GC every 45min | Reduced promotion, lowered IHOP | No more Full GCs |
| 4 | Wrong collector | Chose ZGC for bidding, Parallel for batch | Right tool for job |
| 5 | G1 mixed GC spikes | Tuned region selection | Consistent 15ms |
| 6 | Need <1ms pauses | Switched to ZGC | p99: 18ms → 4.3ms |
| 7 | Intern shrunk heap | Sized correctly (3× live data) | No allocation stalls |
| 8 | 1GB/s allocation | Object reuse, streaming | 82% less garbage |
| 9 | Mystery 3s pause | Read GC log, found System.gc() | Eliminated |
| 10 | OOM after 3 days | Found unbounded cache | Stable heap |
| 11 | RSS growing | Fixed direct buffer leak | Stable containers |
| 12 | — | Production monitoring | Proactive detection |

## The Final Numbers

```
BidStream Production Fleet (after tuning):
  10 bidding servers:  ZGC, 4GB heap, <0.1ms pauses, 47K req/s each
  2 analytics servers: Parallel GC, 8GB heap, batch throughput optimized
  3 API servers:       G1, 2GB heap, 50ms pause target

  Total throughput:    470K bids/second
  p99 latency:        4.3ms
  GC-related revenue loss: $0/month
  OOM incidents:      0 in 90 days
  Container restarts: 0 in 90 days
```

Viktor: "Same hardware. Same code. Different relationship with the garbage collector. That's engineering."

## What You Learned

- **Production configuration** — complete JVM flags for different workload types
- **Monitoring** — Prometheus metrics, Grafana dashboards, alerting rules
- **Tuning workflow** — detect → measure → diagnose → fix → verify
- **JFR** — always-on profiling with minimal overhead
- **Runbook** — incident response procedures for GC problems
- **The journey** — from 212ms pauses to sub-millisecond, one problem at a time

---

## Course Complete

You started with a 212ms GC pause that lost 10,000 bid auctions. You ended with sub-millisecond pauses and zero lost revenue.

Along the way, you learned that GC tuning isn't about memorizing flags — it's about understanding the system. Every flag exists because of a tradeoff. Every tradeoff exists because of physics: memory is finite, scanning takes time, moving objects requires coordination.

The garbage collector isn't your enemy. It's a collaborator. Speak its language — allocation rates, promotion rates, live data ratios — and it'll work with you. Ignore it, and it'll stop the world at the worst possible moment.

The pause comes first. The understanding follows. Now you have both.

---

[← Chapter 11: Off-Heap & Direct Memory](chapter-11-off-heap.md)

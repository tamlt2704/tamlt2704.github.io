# Chapter 9: Concurrent Collections

[← Chapter 8: Blocking Queues](chapter-08-blocking-queues.md) | [Chapter 10: Latches and Barriers →](chapter-10-latches-barriers.md)

---

## The Problem

PulseMetrics aggregates events by source. Kai wrote the aggregation logic:

```java
public class SourceAggregator {
    private final Map<String, Long> countsBySource = new HashMap<>();

    public void record(String source) {
        Long current = countsBySource.getOrDefault(source, 0L);
        countsBySource.put(source, current + 1);
    }

    public Map<String, Long> getCounts() {
        return new HashMap<>(countsBySource);  // Defensive copy
    }
}
```

Single-threaded, this works fine. With 8 ingestion threads calling `record()` concurrently:

```
Exception in thread "ingestion-3" java.util.ConcurrentModificationException
    at java.util.HashMap$HashIterator.nextNode(HashMap.java:1597)
    at java.util.HashMap$EntryIterator.next(HashMap.java:1631)
```

Even wrapping it with `synchronized` doesn't help the dashboard thread that iterates the map while ingestion threads modify it:

```java
// Thread A: iterating for dashboard
for (Map.Entry<String, Long> entry : countsBySource.entrySet()) {
    // Thread B calls record() here → ConcurrentModificationException
    dashboard.update(entry.getKey(), entry.getValue());
}
```

## Collections.synchronizedMap: The Wrong Fix

```java
Map<String, Long> counts = Collections.synchronizedMap(new HashMap<>());
```

This wraps every method in `synchronized`. But compound operations are still broken:

```java
// STILL BROKEN: two separate synchronized calls, not atomic together
Long current = counts.getOrDefault(source, 0L);  // Lock, read, unlock
counts.put(source, current + 1);                  // Lock, write, unlock
// Another thread can modify between these two calls!
```

And iteration still throws `ConcurrentModificationException` unless you manually synchronize:

```java
synchronized (counts) {  // Must lock the wrapper
    for (var entry : counts.entrySet()) { ... }
}
```

## ConcurrentHashMap: The Real Solution

```java
import java.util.concurrent.ConcurrentHashMap;

public class SourceAggregator {
    private final ConcurrentHashMap<String, LongAdder> countsBySource = new ConcurrentHashMap<>();

    public void record(String source) {
        countsBySource.computeIfAbsent(source, k -> new LongAdder()).increment();
    }

    public Map<String, Long> getCounts() {
        Map<String, Long> snapshot = new HashMap<>();
        countsBySource.forEach((k, v) -> snapshot.put(k, v.sum()));
        return snapshot;
    }
}
```

No locks. No exceptions. `computeIfAbsent` is atomic — it creates the `LongAdder` only if the key doesn't exist, and the operation is thread-safe.

## How ConcurrentHashMap Works

Unlike `synchronizedMap` (one lock for the entire map), `ConcurrentHashMap` uses **lock striping**: the map is divided into segments, each with its own lock.

```
synchronizedMap:  [  entire map locked  ]
ConcurrentHashMap: [seg0][seg1][seg2][seg3][seg4][seg5]...
                    lock0 lock1 lock2 lock3 lock4 lock5
```

Threads accessing different segments don't contend. In Java 8+, it uses even finer-grained locking (per-bin CAS for most operations).

### Key Properties

- **Reads never block** — no lock for `get()`
- **Writes lock only the affected bin** — other bins are unaffected
- **Iteration is weakly consistent** — sees elements as they were at some point, no `ConcurrentModificationException`
- **null keys/values not allowed** — unlike HashMap

## Atomic Compound Operations

`ConcurrentHashMap` provides atomic compound operations that `synchronizedMap` can't:

```java
ConcurrentHashMap<String, Long> map = new ConcurrentHashMap<>();

// Atomic: create if absent
map.putIfAbsent("clicks", 0L);

// Atomic: compute new value from old
map.compute("clicks", (key, val) -> val == null ? 1L : val + 1);

// Atomic: compute only if key exists
map.computeIfPresent("clicks", (key, val) -> val + 1);

// Atomic: compute only if key absent
map.computeIfAbsent("clicks", key -> 0L);

// Atomic: merge with existing value
map.merge("clicks", 1L, Long::sum);  // If exists: old + 1. If absent: set to 1.
```

### The merge() Pattern for Counters

```java
// Increment counter atomically
map.merge(source, 1L, Long::sum);

// This is equivalent to:
// if (map.containsKey(source))
//     map.put(source, map.get(source) + 1);
// else
//     map.put(source, 1);
// But atomic!
```

## Bulk Operations (Java 8+)

`ConcurrentHashMap` has parallel bulk operations:

```java
ConcurrentHashMap<String, Long> counts = new ConcurrentHashMap<>();

// forEach with parallelism threshold
// If map has > 1000 entries, operations run in parallel
counts.forEach(1000, (source, count) -> {
    System.out.println(source + ": " + count);
});

// search: find first match (parallel)
String bigSource = counts.search(1000, (source, count) -> {
    return count > 1_000_000 ? source : null;
});

// reduce: aggregate all values (parallel)
long total = counts.reduceValues(1000, Long::sum);

// Parallel transform + reduce
long totalAbove1K = counts.reduceValues(1000,
    count -> count > 1000 ? count : 0L,  // Transform
    Long::sum                              // Reduce
);
```

The first argument is the parallelism threshold: if the map has more entries than this, the operation runs in parallel using the ForkJoinPool.

## CopyOnWriteArrayList: Read-Heavy Lists

For lists that are read far more than written:

```java
import java.util.concurrent.CopyOnWriteArrayList;

public class DashboardRegistry {
    // 500 dashboards read every second, new ones added rarely
    private final CopyOnWriteArrayList<Dashboard> dashboards = new CopyOnWriteArrayList<>();

    public void register(Dashboard d) {
        dashboards.add(d);  // Copies entire array — expensive!
    }

    public void notifyAll(Snapshot data) {
        // Iteration is safe — uses a snapshot of the array
        for (Dashboard d : dashboards) {
            d.update(data);  // No ConcurrentModificationException, ever
        }
    }
}
```

How it works: every write (`add`, `set`, `remove`) creates a new copy of the internal array. Reads see the old array until the write completes.

- **Reads**: zero overhead, no locking, no copying
- **Writes**: O(n) — copies the entire array
- **Use when**: reads vastly outnumber writes (config lists, listener lists)
- **Don't use when**: frequent writes (use `ConcurrentHashMap` or synchronized list)

## ConcurrentSkipListMap: Sorted Concurrent Map

When you need a sorted concurrent map (like `TreeMap` but thread-safe):

```java
import java.util.concurrent.ConcurrentSkipListMap;

// Time-series data: events sorted by timestamp
ConcurrentSkipListMap<Long, Event> timeline = new ConcurrentSkipListMap<>();

timeline.put(System.nanoTime(), event);

// Range queries are thread-safe
NavigableMap<Long, Event> lastMinute = timeline.tailMap(oneMinuteAgo);

// Remove old entries
timeline.headMap(fiveMinutesAgo).clear();
```

O(log n) for all operations. Lock-free reads. Good for time-series and range queries.

## PulseMetrics: Concurrent Aggregation

```java
public class RealTimeAggregator {
    // Per-source event counts
    private final ConcurrentHashMap<String, LongAdder> eventCounts = new ConcurrentHashMap<>();

    // Per-source byte totals
    private final ConcurrentHashMap<String, LongAdder> byteCounts = new ConcurrentHashMap<>();

    // Top-K sources (updated periodically, read frequently)
    private final CopyOnWriteArrayList<SourceRank> topSources = new CopyOnWriteArrayList<>();

    // Time-series: per-second aggregates
    private final ConcurrentSkipListMap<Long, SecondAggregate> timeSeries =
        new ConcurrentSkipListMap<>();

    // Called by 8 ingestion threads
    public void record(Event event) {
        eventCounts.computeIfAbsent(event.source(), k -> new LongAdder()).increment();
        byteCounts.computeIfAbsent(event.source(), k -> new LongAdder()).add(event.bytes());

        long second = event.timestamp() / 1000;
        timeSeries.computeIfAbsent(second, k -> new SecondAggregate()).record(event);
    }

    // Called by dashboard threads — no locking needed
    public DashboardData snapshot() {
        Map<String, Long> events = new HashMap<>();
        eventCounts.forEach((k, v) -> events.put(k, v.sum()));

        // Last 60 seconds of time-series
        long sixtySecondsAgo = System.currentTimeMillis() / 1000 - 60;
        var recentSeries = timeSeries.tailMap(sixtySecondsAgo);

        return new DashboardData(events, List.copyOf(topSources), recentSeries);
    }

    // Periodic: compute top-K (runs every 5 seconds)
    public void refreshTopSources() {
        List<SourceRank> top = eventCounts.entrySet().stream()
            .map(e -> new SourceRank(e.getKey(), e.getValue().sum()))
            .sorted(Comparator.comparingLong(SourceRank::count).reversed())
            .limit(10)
            .toList();

        topSources.clear();
        topSources.addAll(top);  // CopyOnWrite: safe for concurrent readers
    }

    // Periodic: evict old time-series data
    public void evictOldData() {
        long fiveMinutesAgo = System.currentTimeMillis() / 1000 - 300;
        timeSeries.headMap(fiveMinutesAgo).clear();
    }

    public record SourceRank(String source, long count) {}
}
```

## Choosing the Right Collection

| Need | Collection | Notes |
|---|---|---|
| Key-value, high concurrency | ConcurrentHashMap | Lock striping, atomic compute |
| Sorted key-value | ConcurrentSkipListMap | O(log n), range queries |
| Queue (producer-consumer) | BlockingQueue | See Chapter 8 |
| List, read-heavy | CopyOnWriteArrayList | Writes copy entire array |
| Set, high concurrency | ConcurrentHashMap.newKeySet() | Backed by CHM |
| Deque, concurrent | ConcurrentLinkedDeque | Lock-free, unbounded |

## Common Mistakes

### 1. Check-Then-Act on ConcurrentHashMap

```java
// WRONG: not atomic
if (!map.containsKey(key)) {
    map.put(key, new Value());  // Another thread might put between check and put
}

// RIGHT: atomic
map.computeIfAbsent(key, k -> new Value());
```

### 2. Iterating and Modifying

```java
// SAFE with ConcurrentHashMap (weakly consistent iterator)
for (var entry : concurrentMap.entrySet()) {
    if (entry.getValue() == 0) {
        concurrentMap.remove(entry.getKey());  // OK!
    }
}

// UNSAFE with HashMap — throws ConcurrentModificationException
```

### 3. Using size() for Logic

```java
// WRONG: size() is an estimate under concurrency
if (map.size() == 0) {  // Another thread might add between check and action
    initialize();
}

// Use isEmpty() or atomic operations instead
map.computeIfAbsent(key, k -> expensiveInit());
```

## What You Learned

- **ConcurrentHashMap** — lock-striped map, atomic compound operations, weakly consistent iteration
- **computeIfAbsent/merge** — atomic check-and-modify in one call
- **CopyOnWriteArrayList** — snapshot-on-write for read-heavy lists
- **ConcurrentSkipListMap** — sorted concurrent map for range queries
- **Bulk operations** — parallel forEach, search, reduce on ConcurrentHashMap
- **Never use HashMap with multiple threads** — use ConcurrentHashMap
- **synchronizedMap is rarely what you want** — compound operations still need external sync

The collections are concurrent. But PulseMetrics has a startup problem: the system has multiple initialization phases that must complete in order. We need coordination primitives.

---

[← Chapter 8: Blocking Queues](chapter-08-blocking-queues.md) | [Chapter 10: Latches and Barriers →](chapter-10-latches-barriers.md)

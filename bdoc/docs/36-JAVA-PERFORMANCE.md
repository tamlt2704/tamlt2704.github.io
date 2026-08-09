# Chapter 36: Java Performance Tricks — Write Faster Code

## What you'll learn

- JVM internals: how memory, GC, and JIT compilation affect performance
- String performance: concatenation traps, interning, compact strings
- Collections: choosing the right one, sizing, iteration performance
- Primitives vs wrappers: autoboxing costs, primitive collections
- Memory layout: cache-friendly data structures, false sharing
- Concurrency performance: lock contention, CAS, virtual threads
- I/O performance: buffering, NIO, zero-copy
- JVM tuning: GC selection, heap sizing, flags
- Profiling: finding bottlenecks before optimising blindly

---

## PART 1: Strings

## 36.1 String concatenation in loops — the classic trap

```java
// ❌ O(n²) — creates a new String object on EVERY iteration
String result = "";
for (int i = 0; i < 100_000; i++) {
    result += i + ",";  // allocates new char[], copies everything, discards old
}

// ✅ O(n) — StringBuilder mutates in place
StringBuilder sb = new StringBuilder(1_000_000); // pre-size if you know approximate length
for (int i = 0; i < 100_000; i++) {
    sb.append(i).append(',');
}
String result = sb.toString();

// Benchmark: 100K iterations
// String +=:     ~4,200 ms
// StringBuilder: ~3 ms
// Factor: 1400× faster
```

**Why `+=` is O(n²):** Each concatenation creates a new `char[]` of length (old + new), copies the old string into it, then appends new characters. After N iterations, you've copied 1 + 2 + 3 + ... + N = N²/2 characters total.

> **Note:** The compiler optimises `"a" + "b" + "c"` in a SINGLE expression (not a loop) into a StringBuilder automatically (or `invokedynamic` in Java 9+). The trap is only in **loops**.

## 36.2 String.intern() — deduplication

```java
// 1 million strings with the same value — 1 million objects in memory
List<String> names = new ArrayList<>();
for (record : database) {
    names.add(record.getCountry()); // "USA", "USA", "USA"... each is a new String object
}

// With interning — share one instance
for (record : database) {
    names.add(record.getCountry().intern()); // returns canonical instance from String pool
}

// Result: 1 million references pointing to ~200 unique String objects (one per country)
// Memory savings: massive when many duplicates
```

**When to use:** High-cardinality deduplication (country codes, status values, repeated field values from DB/CSV). Don't intern arbitrary user input (bloats the pool).

## 36.3 char[] vs String for sensitive data

```java
// ❌ String: immutable, stays in memory until GC (visible in heap dumps)
String password = "secret123";

// ✅ char[]: you can zero it out immediately after use
char[] password = "secret123".toCharArray();
try {
    authenticate(password);
} finally {
    Arrays.fill(password, '\0'); // wipe from memory
}
```

---

## PART 2: Collections

## 36.4 Choose the right collection

| Need | Use | NOT |
|------|-----|-----|
| Indexed access (get by position) | `ArrayList` | `LinkedList` (O(n) access) |
| Frequent insert/remove in middle | `LinkedList` or `ArrayDeque` | `ArrayList` (O(n) shift) |
| Key-value lookup | `HashMap` | `TreeMap` (unless you need sorted keys) |
| Ordered iteration + fast lookup | `LinkedHashMap` | `HashMap` (random order) |
| Sorted keys | `TreeMap` | `HashMap` + sort later |
| Uniqueness | `HashSet` | `ArrayList` + `.contains()` (O(n) per check) |
| FIFO queue | `ArrayDeque` | `LinkedList` (more GC, worse cache) |
| Stack (LIFO) | `ArrayDeque` | `Stack` (synchronized — slow) |
| Thread-safe map | `ConcurrentHashMap` | `Collections.synchronizedMap` (global lock) |
| Thread-safe queue | `ConcurrentLinkedQueue` or `ArrayBlockingQueue` | Synchronized wrapper |

> **Never use `LinkedList`** in modern Java unless you specifically need O(1) removal by iterator. `ArrayDeque` is faster for both stack and queue operations due to cache locality.

## 36.5 Pre-size collections

```java
// ❌ Default size (10) → resizes at 10, 15, 22, 33, 49... (copies array each time)
List<User> users = new ArrayList<>();
for (int i = 0; i < 10_000; i++) users.add(fetchUser(i));

// ✅ Pre-sized — zero resizes
List<User> users = new ArrayList<>(10_000);

// Same for HashMap (default capacity 16, load factor 0.75)
// If you know you'll have 1000 entries: capacity = 1000 / 0.75 ≈ 1334
Map<String, User> map = new HashMap<>(1334);

// Or simpler: just overestimate
Map<String, User> map = new HashMap<>(2000);
```

## 36.6 Iteration performance

```java
// For ArrayList — indexed loop is fastest (sequential memory access)
for (int i = 0; i < list.size(); i++) {
    process(list.get(i));
}

// Enhanced for-loop — almost identical for ArrayList (iterator overhead is tiny)
for (User user : users) {
    process(user);
}

// Stream — adds overhead for simple operations, but enables parallelism
users.stream().filter(u -> u.isActive()).forEach(this::process);

// ❌ Stream for trivial operations on small collections (overhead > benefit)
list.stream().collect(Collectors.toList()); // just copy: new ArrayList<>(list) is faster

// ✅ Stream for complex pipelines or parallel processing
users.parallelStream()
    .filter(User::isActive)
    .map(this::enrichProfile)   // expensive per-element
    .collect(Collectors.toList());
```

## 36.7 Map tricks

```java
// computeIfAbsent — avoid double lookup
// ❌ Two lookups: containsKey + put
if (!map.containsKey(key)) {
    map.put(key, new ArrayList<>());
}
map.get(key).add(value);

// ✅ Single atomic operation
map.computeIfAbsent(key, k -> new ArrayList<>()).add(value);

// getOrDefault — avoid null checks
int count = map.getOrDefault(key, 0);

// merge — counting pattern
map.merge(word, 1, Integer::sum); // increment count, start at 1 if absent

// replaceAll — transform all values
map.replaceAll((k, v) -> v.toUpperCase());
```

---

## PART 3: Primitives vs Wrappers

## 36.8 Autoboxing costs

```java
// ❌ Every iteration boxes int → Integer (object allocation + GC pressure)
Long sum = 0L;
for (int i = 0; i < 1_000_000; i++) {
    sum += i;  // autoboxes i to Integer, unboxes sum, adds, reboxes to Long
}
// ~6,000 ms, millions of garbage Integer/Long objects created

// ✅ Use primitive
long sum = 0L;
for (int i = 0; i < 1_000_000; i++) {
    sum += i;
}
// ~2 ms — 3000× faster, zero allocations
```

**Memory difference:**
```
int:      4 bytes
Integer:  16 bytes (object header) + 4 bytes (value) = ~16-20 bytes (4-5× more)

int[1000]:        4 KB (contiguous, cache-friendly)
Integer[1000]:    ~20 KB + 1000 object headers (scattered in heap, cache-hostile)
```

## 36.9 Primitive-specialised collections

```java
// Standard Java: List<Integer> — every element is a boxed object
List<Integer> ids = new ArrayList<>(); // 20 bytes per element

// Eclipse Collections (or similar): IntArrayList — primitive int[]
IntArrayList ids = new IntArrayList(); // 4 bytes per element, 5× less memory

// For maps with int/long keys:
// ❌ HashMap<Integer, User> — boxes every key
// ✅ IntObjectHashMap<User> (Eclipse Collections) — no boxing

// Dependencies:
// implementation 'org.eclipse.collections:eclipse-collections:11.1.0'
```

| Library | Primitive collections? | Notes |
|---------|----------------------|-------|
| Eclipse Collections | Yes (Int/Long/Double lists, maps, sets) | Most complete |
| HPPC | Yes | Fastest for pure primitive ops |
| Koloboke | Yes | Best HashMap performance |
| fastutil | Yes | Widely used, good general purpose |

---

## PART 4: Memory & GC

## 36.10 Object allocation and GC pressure

```java
// ❌ Allocates millions of short-lived objects (stresses GC)
for (Request request : requests) {
    String key = request.getType() + ":" + request.getId(); // new String every time
    Result result = new Result(process(request));             // new Result every time
    cache.put(key, result);
}

// ✅ Reduce allocations
StringBuilder keyBuilder = new StringBuilder(64); // reuse across iterations
for (Request request : requests) {
    keyBuilder.setLength(0); // reset without reallocating
    keyBuilder.append(request.getType()).append(':').append(request.getId());
    String key = keyBuilder.toString();
    // Or better: use a pre-sized cache key object
}
```

**GC-friendly patterns:**
- Reuse objects (object pools for expensive objects)
- Pre-size collections (avoid resize copies)
- Prefer primitives over wrappers
- Avoid creating objects in hot loops
- Short-lived objects are cheap (young gen GC is fast) — don't over-optimize

## 36.11 Object pooling (when it helps)

```java
// For expensive-to-create objects (DB connections, threads, byte buffers)
// Use built-in pools:
ExecutorService pool = Executors.newFixedThreadPool(8);       // thread pool
DataSource ds = HikariDataSource(config);                     // connection pool
ByteBuffer buffer = ByteBuffer.allocateDirect(8192);         // reuse direct buffers

// For cheap objects (String, Integer, small DTOs) — DON'T pool
// Object creation is ~10ns. Pool synchronization overhead is worse.
```

**Rule:** Pool if object creation > 1μs (connections, threads, large buffers). Don't pool if creation < 100ns (most objects).

## 36.12 Memory layout and cache lines

```java
// CPU caches work in 64-byte cache lines
// Adjacent memory is loaded together → sequential access is fast

// ✅ Array of primitives: sequential, cache-friendly
int[] values = new int[1000]; // 4000 bytes contiguous
for (int v : values) sum += v; // CPU prefetcher loves this

// ❌ Array of objects: pointers scatter across heap
Object[] objects = new Object[1000]; // 1000 pointers, objects scattered
for (Object o : objects) sum += o.hashCode(); // random memory access, cache misses

// ❌ LinkedList: every node is a separate heap object (worst case for cache)
// Traversal = pointer chase = cache miss per element
```

**False sharing (concurrency):**
```java
// ❌ Two threads updating adjacent fields — share a cache line
class Counters {
    volatile long counter1; // Thread 1 writes
    volatile long counter2; // Thread 2 writes
    // Both in same 64-byte cache line → constant invalidation!
}

// ✅ Pad to separate cache lines
class Counters {
    volatile long counter1;
    long p1, p2, p3, p4, p5, p6, p7; // padding (7 × 8 = 56 bytes)
    volatile long counter2;            // now in a different cache line
}

// Or use @Contended (Java 8+, JVM flag required)
@sun.misc.Contended
volatile long counter1;
```

---

## PART 5: Concurrency Performance

## 36.13 Lock contention — the scalability killer

```java
// ❌ Global lock: only 1 thread works at a time (no parallelism)
synchronized (this) {
    map.put(key, value);
}

// ✅ ConcurrentHashMap: lock striping (locks per segment, not whole map)
ConcurrentHashMap<String, Value> map = new ConcurrentHashMap<>();
map.put(key, value); // fine-grained locking internally

// ✅ Lock-free: CAS (Compare-And-Swap)
AtomicLong counter = new AtomicLong(0);
counter.incrementAndGet(); // no lock needed — CPU-level atomic instruction

// ✅ ReadWriteLock: when reads vastly outnumber writes
ReadWriteLock lock = new ReentrantReadWriteLock();
// Multiple readers simultaneously OR one writer exclusively
```

## 36.14 Virtual threads (Java 21+) — I/O performance

```java
// ❌ Platform threads: 1 thread per request, limited by OS threads (~2000-10000)
ExecutorService executor = Executors.newFixedThreadPool(200);
// 200 threads, each blocking on I/O (DB, HTTP calls)
// 201st request must wait!

// ✅ Virtual threads: millions of concurrent I/O operations
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();
// Each request gets a virtual thread (costs ~1KB, not ~1MB)
// 100,000 concurrent blocking calls? No problem.

// Perfect for:
// - REST APIs with database calls
// - Microservices calling other services
// - Any I/O-bound workload

// NOT helpful for:
// - CPU-bound work (still limited by cores)
// - Already async code (CompletableFuture)
```

## 36.15 Batch processing

```java
// ❌ One DB call per item (1000 items = 1000 round trips × 1ms each = 1 second)
for (User user : users) {
    userRepository.save(user);
}

// ✅ Batch insert (1 round trip, ~5ms)
userRepository.saveAll(users); // Spring Data batches this

// ✅ JDBC batch explicitly
PreparedStatement ps = conn.prepareStatement("INSERT INTO users VALUES (?,?,?)");
for (User user : users) {
    ps.setString(1, user.getName());
    ps.setString(2, user.getEmail());
    ps.addBatch();
    if (batchCount % 1000 == 0) ps.executeBatch(); // flush every 1000
}
ps.executeBatch(); // flush remaining
```

---

## PART 6: I/O Performance

## 36.16 Buffered I/O

```java
// ❌ Unbuffered: 1 system call per byte (catastrophically slow)
FileInputStream fis = new FileInputStream("data.bin");
int b;
while ((b = fis.read()) != -1) { process(b); }

// ✅ Buffered: reads 8KB chunks, serves bytes from memory
BufferedInputStream bis = new BufferedInputStream(new FileInputStream("data.bin"), 65536);
int b;
while ((b = bis.read()) != -1) { process(b); }

// ✅ Even better: read into byte array
byte[] buffer = new byte[65536];
int bytesRead;
while ((bytesRead = fis.read(buffer)) != -1) {
    processChunk(buffer, bytesRead);
}

// Benchmark (reading 100MB file):
// Unbuffered byte-by-byte: ~60 seconds
// BufferedInputStream:     ~0.5 seconds
// Byte array reads:        ~0.2 seconds
```

## 36.17 NIO (Non-blocking I/O)

```java
// Memory-mapped files — OS handles caching, zero-copy for reads
FileChannel channel = FileChannel.open(Path.of("large-file.dat"), StandardOpenOption.READ);
MappedByteBuffer buffer = channel.map(FileChannel.MapMode.READ_ONLY, 0, channel.size());
// Access data directly from OS page cache — no copy to JVM heap

// NIO for network — handle 10,000+ connections with few threads
Selector selector = Selector.open();
ServerSocketChannel server = ServerSocketChannel.open();
server.configureBlocking(false);
server.register(selector, SelectionKey.OP_ACCEPT);

while (true) {
    selector.select(); // blocks until events are ready
    for (SelectionKey key : selector.selectedKeys()) {
        if (key.isAcceptable()) handleAccept(key);
        if (key.isReadable()) handleRead(key);
    }
}
```

---

## PART 7: JVM Tuning

## 36.18 GC selection

| GC | Best for | Flags |
|---|---------|-------|
| **G1GC** | General purpose (default since Java 9) | `-XX:+UseG1GC` |
| **ZGC** | Ultra-low latency (< 1ms pauses) | `-XX:+UseZGC` |
| **Shenandoah** | Low latency (alternative to ZGC) | `-XX:+UseShenandoahGC` |
| **Parallel GC** | Maximum throughput (batch jobs) | `-XX:+UseParallelGC` |

```bash
# Web API (low latency, moderate throughput):
java -XX:+UseZGC -Xmx4g -Xms4g -jar app.jar

# Batch processing (throughput > latency):
java -XX:+UseParallelGC -Xmx8g -jar app.jar

# General purpose (good default):
java -XX:+UseG1GC -Xmx4g -Xms4g -XX:MaxGCPauseMillis=200 -jar app.jar
```

## 36.19 Key JVM flags

```bash
# Heap size (ALWAYS set both equal — avoid resize pauses)
-Xms4g -Xmx4g

# GC logging (diagnose GC issues)
-Xlog:gc*:file=gc.log:time,level,tags

# Metaspace (class metadata — increase if "Metaspace OOM")
-XX:MaxMetaspaceSize=512m

# Thread stack size (reduce if many threads, increase if StackOverflow)
-Xss512k

# Enable string deduplication (G1GC only — auto-deduplicate identical strings)
-XX:+UseStringDeduplication

# Print compilation (see what JIT compiles)
-XX:+PrintCompilation

# Escape analysis (default on — allows stack allocation of non-escaping objects)
-XX:+DoEscapeAnalysis
```

## 36.20 Profiling — find bottlenecks first

**NEVER optimise without profiling.** Your intuition about what's slow is usually wrong.

```bash
# 1. JFR (Java Flight Recorder) — low overhead, production-safe
java -XX:+FlightRecorder -XX:StartFlightRecording=duration=60s,filename=recording.jfr -jar app.jar
# Open .jfr file in JDK Mission Control (jmc)

# 2. async-profiler — find hot methods with flame graphs
./profiler.sh -d 30 -f flamegraph.html <pid>

# 3. jstat — GC statistics
jstat -gc <pid> 1000  # print GC stats every 1 second

# 4. jmap — heap dump (find memory leaks)
jmap -dump:format=b,file=heap.hprof <pid>
# Open with Eclipse MAT or VisualVM
```

**Flame graph reading:**
```
Wide bar = method that uses lots of CPU time (or its children do)
Tall stack = deep call chain
Look for: surprisingly wide bars (unexpected hotspots)
```

---

## Quick Reference: Performance Rules

| Area | Rule | Impact |
|------|------|--------|
| Strings | Use StringBuilder in loops | 100-1000× for large loops |
| Collections | Pre-size ArrayList/HashMap | 2-5× fewer allocations |
| Collections | Use ArrayDeque, not LinkedList | 2-3× cache locality |
| Primitives | Avoid autoboxing in hot paths | 5-20× for numeric loops |
| Memory | Prefer arrays over object graphs | Better cache utilisation |
| Concurrency | ConcurrentHashMap over synchronized map | 10-50× under contention |
| Concurrency | Virtual threads for I/O-bound | 10-100× concurrent connections |
| I/O | Always buffer file/network I/O | 100× for unbuffered reads |
| I/O | Batch DB operations | 50-200× fewer round trips |
| JVM | Set -Xms = -Xmx | Avoid heap resize pauses |
| JVM | Use ZGC for low latency | < 1ms GC pauses |
| General | Profile before optimising | Don't waste time on cold paths |

---

## Summary

✅ String traps: `+=` in loops is O(n²), StringBuilder is O(n)
✅ Collections: right choice + pre-sizing + proper iteration
✅ Autoboxing: use primitives in hot paths, primitive collections for large datasets
✅ Memory: cache-friendly layout, object pooling for expensive resources, false sharing avoidance
✅ Concurrency: ConcurrentHashMap, Atomics/CAS, virtual threads for I/O
✅ I/O: always buffer, batch DB calls, NIO for high-connection servers
✅ JVM: GC choice by workload, heap sizing, JVM flags
✅ Profiling: JFR + flame graphs before any optimisation

## Key takeaways

**Profile first, optimise second.** Most code doesn't matter for performance (Amdahl's Law). Find the 5% of code that takes 95% of the time — optimise THAT.

**The JVM is already fast.** JIT compilation, escape analysis, and modern GCs mean most "optimisations" are premature. Only optimise when you've measured a bottleneck.

**Memory access pattern > algorithm complexity** at modern hardware speeds. An O(n) algorithm on contiguous memory often beats O(log n) on scattered pointers due to cache effects. `ArrayList` beats `TreeMap` for small N.

**The biggest wins are architectural**, not micro: batching I/O, choosing the right data structure, reducing allocations in hot loops, and using concurrent data structures instead of global locks.

---

→ [Back to Chapter 35: System Design Interview](./35-SYSTEM-DESIGN-INTERVIEW.md)

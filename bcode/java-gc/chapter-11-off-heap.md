# Chapter 11: Off-Heap & Direct Memory

[← Chapter 10: Memory Leaks](chapter-10-leaks.md) | [Chapter 12: Production GC Strategy →](chapter-12-production.md)

---

## The Problem

Sasha's monitoring dashboard shows something strange:

```
BidServer-09 container metrics:
  Heap used:     1.8GB (stable)
  Heap max:      4.0GB
  Container RSS: 7.2GB (growing 50MB/hour)
  Container limit: 8.0GB
```

The heap is fine — 1.8GB used, 4GB max, no leak. But the container's total memory (RSS) is 7.2GB and climbing. At 50MB/hour, it'll hit the 8GB container limit in 16 hours and get OOM-killed.

The GC manages the heap. But 3.2GB of memory is **outside the heap** — and growing.

Sasha: "The GC logs look perfect. No pauses, no pressure. But the container is going to die."

Viktor: "Where is the memory going?"

## JVM Memory Beyond the Heap

The heap is just one piece of JVM memory:

```
┌─────────────────────────────────────────────────────────┐
│                    Container RSS (7.2GB)                  │
├──────────────────────────────────────────────────────────┤
│  Heap (4GB max)           │  Non-Heap                    │
│  ┌──────────────────┐     │  ┌────────────────────────┐  │
│  │ Young + Old Gen  │     │  │ Metaspace:     180MB   │  │
│  │ Used: 1.8GB      │     │  │ Code Cache:    120MB   │  │
│  │ Max:  4.0GB      │     │  │ Thread Stacks: 400MB   │  │
│  └──────────────────┘     │  │ Direct Buffers: ???    │  │
│                           │  │ Native (JNI):  ???     │  │
│                           │  │ GC Structures: 200MB   │  │
│                           │  └────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

The GC only manages the heap. Everything else is "native memory" — allocated by the JVM or application code directly from the OS.

## Native Memory Tracking (NMT)

Enable NMT to see where native memory goes:

```bash
java -XX:NativeMemoryTracking=summary \
     -XX:+UseZGC -Xms4g -Xmx4g \
     BidServer
```

Query at runtime:

```bash
jcmd <pid> VM.native_memory summary
```

```
Native Memory Tracking:

Total: reserved=9841MB, committed=7234MB

-                 Java Heap (reserved=4096MB, committed=4096MB)
                            (mmap: reserved=4096MB, committed=4096MB)

-                     Class (reserved=180MB, committed=180MB)
                            (classes #24891)

-                    Thread (reserved=412MB, committed=412MB)
                            (thread #206)
                            (stack: reserved=410MB, committed=410MB)

-                      Code (reserved=248MB, committed=122MB)
                            (mmap: reserved=248MB, committed=122MB)

-                        GC (reserved=198MB, committed=198MB)

-                  Internal (reserved=1842MB, committed=1842MB)  ← SUSPICIOUS
                            (malloc=1842MB #48291)

-                    Symbol (reserved=24MB, committed=24MB)

-    Native Memory Tracking (reserved=8MB, committed=8MB)

-                     Other (reserved=833MB, committed=380MB)
```

**Internal: 1842MB.** That's the culprit. "Internal" includes direct ByteBuffers and other native allocations made through the JVM.

## Direct ByteBuffers

`ByteBuffer.allocateDirect()` allocates memory outside the heap. It's used for I/O because the OS can read/write directly to it without copying through the heap:

```java
// Heap buffer: data lives on the Java heap
ByteBuffer heapBuf = ByteBuffer.allocate(4096);  // GC manages this

// Direct buffer: data lives in native memory
ByteBuffer directBuf = ByteBuffer.allocateDirect(4096);  // GC does NOT manage this
```

Direct buffers are freed when their Java wrapper object is garbage collected — but the GC doesn't know how much native memory they hold. It might not collect them urgently enough.

### BidStream's Direct Buffer Leak

The network layer uses Netty, which allocates direct buffers for I/O:

```java
// Netty allocates direct buffers for each connection
ByteBuf buf = ctx.alloc().directBuffer(65536);
// ... write response ...
buf.release();  // Must be called! Reference counting.
```

A code path was missing `release()`:

```java
public void handleBidResponse(ChannelHandlerContext ctx, BidResponse response) {
    ByteBuf buf = ctx.alloc().directBuffer(65536);
    try {
        serialize(response, buf);
        ctx.writeAndFlush(buf);
        // Bug: writeAndFlush takes ownership, but only if successful
    } catch (Exception e) {
        // buf.release() missing here!  ← LEAK
        log.error("Serialization failed", e);
    }
}
```

When serialization fails (rare — maybe 10 times/hour), the direct buffer leaks. At 64KB per leak, that's 640KB/hour. But Netty's allocator rounds up and pools buffers, so the actual growth is ~50MB/hour. Matches the observed leak rate.

### The Fix

```java
public void handleBidResponse(ChannelHandlerContext ctx, BidResponse response) {
    ByteBuf buf = ctx.alloc().directBuffer(65536);
    try {
        serialize(response, buf);
        ctx.writeAndFlush(buf);  // Netty releases on success
    } catch (Exception e) {
        buf.release();  // Release on failure
        log.error("Serialization failed", e);
    }
}
```

Or better — use Netty's `ReferenceCountUtil`:

```java
ByteBuf buf = ctx.alloc().directBuffer(65536);
boolean success = false;
try {
    serialize(response, buf);
    ctx.writeAndFlush(buf);
    success = true;
} finally {
    if (!success) {
        ReferenceCountUtil.release(buf);
    }
}
```

## Monitoring Direct Memory

### JMX

```java
// Track direct buffer usage
BufferPoolMXBean directPool = ManagementFactory.getPlatformMXBeans(BufferPoolMXBean.class)
    .stream()
    .filter(p -> p.getName().equals("direct"))
    .findFirst().orElseThrow();

long directUsed = directPool.getMemoryUsed();    // Bytes in use
long directCount = directPool.getCount();         // Number of buffers
long directCapacity = directPool.getTotalCapacity();
```

### Limiting Direct Memory

```bash
# Cap direct memory (default: same as -Xmx)
-XX:MaxDirectMemorySize=512m
```

If direct memory exceeds this limit, `allocateDirect()` triggers a GC to try to free phantom-reachable direct buffers. If that fails, it throws `OutOfMemoryError: Direct buffer memory`.

## Unsafe and Manual Memory

Some libraries use `sun.misc.Unsafe` or `java.lang.foreign` (Panama) for manual memory management:

```java
// Unsafe allocation (no GC involvement at all)
Unsafe unsafe = getUnsafe();
long address = unsafe.allocateMemory(1024 * 1024);  // 1MB native
// ... use memory ...
unsafe.freeMemory(address);  // Must free manually!

// Java 21+ Foreign Memory API (safer)
try (Arena arena = Arena.ofConfined()) {
    MemorySegment segment = arena.allocate(1024 * 1024);
    // ... use segment ...
}  // Automatically freed when arena closes
```

If `freeMemory()` is never called, the memory leaks permanently. NMT won't even track it (it's below the JVM's awareness).

## NMT Baseline and Diff

Track native memory growth over time:

```bash
# Set baseline
jcmd <pid> VM.native_memory baseline

# Wait 24 hours, then compare
jcmd <pid> VM.native_memory summary.diff
```

```
Total: reserved=9841MB +1204MB, committed=7234MB +1198MB

-                  Internal (reserved=1842MB +1180MB, committed=1842MB +1180MB)
                            (malloc=1842MB +1180MB #48291 +12400)
```

+1180MB in "Internal" over 24 hours. 12,400 new allocations. That's the direct buffer leak — each leaked buffer is a separate malloc.

## Container Memory Budget

For Kubernetes deployments, budget all JVM memory:

```
Container limit:     8GB
─────────────────────────
Java Heap (-Xmx):   4.0GB
Metaspace:           0.3GB
Thread stacks:       0.4GB  (200 threads × 2MB)
Code cache:          0.2GB
GC overhead:         0.2GB
Direct buffers:      0.5GB  (-XX:MaxDirectMemorySize)
JVM internals:       0.2GB
Safety margin:       0.2GB
─────────────────────────
Total:               6.0GB  (leaves 2GB headroom)
```

```bash
java -XX:+UseZGC \
     -Xms4g -Xmx4g \
     -XX:MaxDirectMemorySize=512m \
     -XX:MaxMetaspaceSize=300m \
     -XX:ReservedCodeCacheSize=256m \
     -Xss512k \
     -XX:NativeMemoryTracking=summary \
     BidServer
```

## What You Learned

- **Off-heap memory** — native memory not managed by the GC
- **RSS vs heap** — container RSS includes heap + metaspace + threads + direct buffers + GC structures
- **NMT** — Native Memory Tracking shows where native memory is allocated
- **Direct ByteBuffers** — allocated outside heap, freed when wrapper is GC'd
- **Reference counting** — Netty buffers must be explicitly released
- **MaxDirectMemorySize** — caps direct buffer allocation
- **NMT diff** — baseline + diff to track native memory growth over time
- **Container budgeting** — account for all memory sources when setting limits

The memory model is complete. You understand heap (young + old), off-heap (direct buffers, metaspace, threads), and how to monitor both. Now it's time to put everything together into a production-ready GC strategy.

Chapter 12: the complete production configuration for BidStream.

---

[← Chapter 10: Memory Leaks](chapter-10-leaks.md) | [Chapter 12: Production GC Strategy →](chapter-12-production.md)

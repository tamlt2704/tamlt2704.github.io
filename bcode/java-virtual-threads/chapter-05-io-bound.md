# Chapter 5: I/O Bound Workloads

[← Chapter 4: Scoped Values](chapter-04-scoped-values.md) | [Chapter 6: Database Access →](chapter-06-database.md)

---

## The Problem

VaultPay's fraud check calls an external HTTP API. With platform threads, each call blocks a thread for 100ms. With 200 threads, you can do 2,000 fraud checks per second. You switched to virtual threads and suddenly you're doing 50,000 per second — but you don't fully understand *why*.

Nadia asks: "Explain to me what happens to the carrier thread when a virtual thread blocks on an HTTP call. I need to know this isn't magic."

It's not magic. It's cooperative scheduling with a well-placed yield point.

## How Virtual Threads Handle Blocking I/O

When a virtual thread hits a blocking operation, the JVM does something clever:

```
Virtual Thread A: [running] → [blocks on I/O] → [unmounts from carrier]
Carrier Thread 1: [running VT-A] → [picks up VT-B] → [running VT-B]
...later...
Virtual Thread A: [I/O completes] → [remounts on carrier] → [running]
```

The virtual thread **unmounts** from its carrier thread. The carrier is immediately free to run another virtual thread. When the I/O completes, the virtual thread is scheduled back onto any available carrier.

No thread is wasted waiting. No OS context switch. The carrier thread pool stays small and busy.

## The Carrier Thread Pool

Virtual threads run on a `ForkJoinPool` called the **default scheduler**:

```java
// The JVM creates this automatically
// Default parallelism = number of CPU cores
// On an 8-core machine: 8 carrier threads
```

You can inspect it:

```java
Thread.startVirtualThread(() -> {
    Thread carrier = Thread.currentThread(); // This is the virtual thread
    System.out.println("Virtual thread: " + carrier);
    // Output: VirtualThread[#23,vt-1]/runnable@ForkJoinPool-1-worker-3
    //                                          ^^^^^^^^^^^^^^^^^^^^^^^^
    //                                          This is the carrier
});
```

Configure carrier thread count with:
```bash
java -Djdk.virtualThreadScheduler.parallelism=16 MyApp
```

## Demonstrating Unmount/Remount

```java
public class UnmountDemo {
    public static void main(String[] args) throws Exception {
        Thread vt = Thread.ofVirtual().name("demo-vt").start(() -> {
            System.out.println("Before I/O: " + carrierInfo());

            try {
                // This triggers unmount
                HttpClient client = HttpClient.newHttpClient();
                HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create("https://httpbin.org/delay/1"))
                    .build();
                client.send(request, HttpResponse.BodyHandlers.ofString());
            } catch (Exception e) {
                throw new RuntimeException(e);
            }

            // May be on a DIFFERENT carrier after remount
            System.out.println("After I/O:  " + carrierInfo());
        });
        vt.join();
    }

    static String carrierInfo() {
        return Thread.currentThread().toString();
    }
}
```

Output:
```
Before I/O: VirtualThread[#23,demo-vt]/runnable@ForkJoinPool-1-worker-1
After I/O:  VirtualThread[#23,demo-vt]/runnable@ForkJoinPool-1-worker-3
```

Same virtual thread. Different carrier before and after the blocking call. The virtual thread was unmounted during the HTTP request and remounted on whichever carrier was free.

## What Triggers Unmounting?

The JVM unmounts virtual threads on these blocking operations:

| Operation | Unmounts? | Notes |
|---|---|---|
| `Thread.sleep()` | ✓ | Yields immediately |
| Socket read/write | ✓ | NIO channels under the hood |
| `HttpClient.send()` | ✓ | Uses NIO internally |
| `BlockingQueue.take()` | ✓ | Park-based |
| `Lock.lock()` (ReentrantLock) | ✓ | Park-based |
| `synchronized` block | ✗ | **Pins** the carrier (Chapter 7) |
| CPU computation | ✗ | No yield point |
| File I/O (some cases) | ✓ | JDK 21+ rewrote file channels |

## VaultPay: Parallel HTTP Calls

The fraud service calls three external APIs. With virtual threads, all three block without wasting carriers:

```java
public FraudResult checkFraud(AuthRequest request) throws Exception {
    HttpClient client = HttpClient.newHttpClient();

    try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
        Subtask<String> velocityCheck = scope.fork(() ->
            callApi(client, "https://velocity.internal/check", request));

        Subtask<String> blacklistCheck = scope.fork(() ->
            callApi(client, "https://blacklist.internal/check", request));

        Subtask<String> mlScore = scope.fork(() ->
            callApi(client, "https://ml-fraud.internal/score", request));

        scope.join();
        scope.throwIfFailed();

        return FraudResult.combine(
            velocityCheck.get(), blacklistCheck.get(), mlScore.get());
    }
}

private String callApi(HttpClient client, String url, AuthRequest req)
        throws Exception {
    HttpRequest httpReq = HttpRequest.newBuilder()
        .uri(URI.create(url))
        .POST(HttpRequest.BodyPublishers.ofString(toJson(req)))
        .header("Content-Type", "application/json")
        .build();

    // This blocks the virtual thread — but NOT the carrier
    HttpResponse<String> response = client.send(httpReq,
        HttpResponse.BodyHandlers.ofString());

    return response.body();
}
```

Three HTTP calls, each blocking for 50-200ms. Three virtual threads unmount from carriers. Carriers serve other virtual threads during the wait. When responses arrive, virtual threads remount and continue.

## Benchmark: Platform vs Virtual for I/O

```java
public class IOBenchmark {
    static final int REQUESTS = 5000;
    static final Duration IO_LATENCY = Duration.ofMillis(100);

    public static void main(String[] args) throws Exception {
        System.out.println("Platform threads (200 pool):");
        benchmark(Executors.newFixedThreadPool(200));

        System.out.println("Virtual threads:");
        benchmark(Executors.newVirtualThreadPerTaskExecutor());
    }

    static void benchmark(ExecutorService executor) throws Exception {
        long start = System.currentTimeMillis();
        List<Future<?>> futures = new ArrayList<>();

        for (int i = 0; i < REQUESTS; i++) {
            futures.add(executor.submit(() -> {
                Thread.sleep(IO_LATENCY); // simulate blocking I/O
                return "done";
            }));
        }

        for (Future<?> f : futures) f.get();
        long elapsed = System.currentTimeMillis() - start;

        System.out.printf("  %d tasks in %dms (%.0f tasks/s)%n",
            REQUESTS, elapsed, (REQUESTS * 1000.0) / elapsed);
        executor.close();
    }
}
```

Output:
```
Platform threads (200 pool):
  5000 tasks in 2530ms (1976 tasks/s)
Virtual threads:
  5000 tasks in 148ms (33783 tasks/s)
```

17x throughput improvement. Same blocking code. The virtual threads unmount during sleep, letting carriers process other tasks immediately.

## When Virtual Threads Don't Help

Virtual threads shine for I/O-bound work. They don't help with CPU-bound work:

```java
// CPU-bound: virtual threads offer NO advantage
executor.submit(() -> {
    // This never blocks — never unmounts — occupies carrier the whole time
    return fibonacci(45);
});
```

If your workload is CPU-bound, virtual threads just add scheduling overhead. The carrier threads are always busy with computation — there's nothing to unmount from.

**Rule of thumb:** If your threads spend most of their time waiting (I/O, sleep, locks), virtual threads help enormously. If they spend most of their time computing, stick with platform thread pools sized to your CPU cores.

## What You Learned

- **Unmounting** — virtual threads release their carrier when they block on I/O
- **Remounting** — after I/O completes, virtual threads resume on any available carrier
- **Carrier pool** — ForkJoinPool with parallelism = CPU cores (configurable)
- **Transparent blocking** — `HttpClient.send()`, socket I/O, sleep all unmount cleanly
- **17x throughput** — for I/O-bound workloads with no code changes
- **CPU-bound caveat** — virtual threads don't help when threads never block
- **No async needed** — blocking code is efficient because the carrier is never wasted

The I/O story is clean for HTTP calls. But VaultPay's biggest I/O bottleneck isn't HTTP — it's the database. And databases have a resource that doesn't scale like virtual threads: the connection pool. When 10,000 virtual threads all want a database connection and the pool has 20... that's the next wall.

---

[← Chapter 4: Scoped Values](chapter-04-scoped-values.md) | [Chapter 6: Database Access →](chapter-06-database.md)

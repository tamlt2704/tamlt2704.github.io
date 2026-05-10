# Chapter 2: Your First Virtual Thread

[← Chapter 1: The Thread Pool Wall](chapter-01-thread-pool-wall.md) | [Chapter 3: Structured Concurrency →](chapter-03-structured-concurrency.md)

---

## The Problem

After the Black Friday post-mortem, Nadia gives you a spike: "Prove that virtual threads can handle 10K concurrent operations without blowing up memory. I want numbers."

You open a blank file. You know `new Thread(() -> ...)`. You know `ExecutorService`. But virtual threads are new. How do you create one? How do you create a million? And what actually happens to memory when you do?

The intern already tried: "I just set the thread pool to 10,000." That crashed with `OutOfMemoryError`. You need a different approach.

## Creating Virtual Threads

### The Builder API

```java
// Platform thread (the old way)
Thread platform = Thread.ofPlatform()
    .name("worker-1")
    .start(() -> System.out.println("Platform: " + Thread.currentThread()));

// Virtual thread (the new way)
Thread virtual = Thread.ofVirtual()
    .name("vt-1")
    .start(() -> System.out.println("Virtual: " + Thread.currentThread()));

virtual.join();
```

Output:
```
Platform: Thread[#21,worker-1,5,main]
Virtual: VirtualThread[#23,vt-1]/runnable@ForkJoinPool-1-worker-1
```

Notice the virtual thread runs *on* a ForkJoinPool worker — that's the carrier thread.

### The Convenience Method

```java
Thread vt = Thread.startVirtualThread(() -> {
    System.out.println("Quick virtual thread");
});
vt.join();
```

No builder needed. One line. This is what you'll use for quick tasks.

### Checking Thread Type

```java
Thread current = Thread.currentThread();
if (current.isVirtual()) {
    System.out.println("Running on a virtual thread");
} else {
    System.out.println("Running on a platform thread");
}
```

## The Million-Thread Test

Here's the spike Nadia asked for. Create 1,000,000 threads that each sleep for 1 second (simulating I/O wait):

```java
public class MillionThreads {
    public static void main(String[] args) throws Exception {
        long start = System.currentTimeMillis();

        List<Thread> threads = new ArrayList<>();
        for (int i = 0; i < 1_000_000; i++) {
            Thread vt = Thread.ofVirtual().name("vt-" + i).start(() -> {
                try {
                    Thread.sleep(Duration.ofSeconds(1)); // simulate I/O
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            });
            threads.add(vt);
        }

        for (Thread t : threads) {
            t.join();
        }

        long elapsed = System.currentTimeMillis() - start;
        System.out.printf("1M virtual threads completed in %dms%n", elapsed);
    }
}
```

Output:
```
1M virtual threads completed in 1,823ms
```

1 million threads. All sleeping for 1 second. Completed in under 2 seconds. Memory usage: ~600MB.

Now try the same with platform threads:

```java
public class MillionPlatformThreads {
    public static void main(String[] args) throws Exception {
        for (int i = 0; i < 1_000_000; i++) {
            Thread t = Thread.ofPlatform().start(() -> {
                try {
                    Thread.sleep(Duration.ofSeconds(1));
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            });
        }
    }
}
```

Output:
```
[After ~4,000 threads]
java.lang.OutOfMemoryError: unable to create native thread
```

Dead at 4,000. Virtual threads made it to 1,000,000.

## Memory Comparison

| Metric | 10K Platform Threads | 10K Virtual Threads |
|---|---|---|
| Stack memory | 10GB | ~10MB |
| Creation time | ~10s | ~50ms |
| OS threads used | 10,000 | 8 (carrier threads) |
| Feasible? | No (OOM) | Yes |

## ExecutorService with Virtual Threads

You don't pool virtual threads — you create a new one per task. Java 21 provides an executor that does exactly this:

```java
try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {
    List<Future<String>> futures = new ArrayList<>();

    for (int i = 0; i < 10_000; i++) {
        final int taskId = i;
        futures.add(executor.submit(() -> {
            Thread.sleep(Duration.ofMillis(100)); // simulate I/O
            return "Result-" + taskId;
        }));
    }

    for (Future<String> future : futures) {
        String result = future.get();
        // process result
    }
}
```

Key insight: `newVirtualThreadPerTaskExecutor()` creates a **new virtual thread for every submitted task**. No pool. No queue. No limit. Each task gets its own thread immediately.

Compare with the old pattern:

```java
// OLD: pool of 200 platform threads, tasks queue when pool is full
ExecutorService old = Executors.newFixedThreadPool(200);

// NEW: unlimited virtual threads, no queuing
ExecutorService modern = Executors.newVirtualThreadPerTaskExecutor();
```

## VaultPay: The Proof of Concept

You wire it into a simple benchmark simulating VaultPay's authorization flow:

```java
public class VaultPayBenchmark {
    public static void main(String[] args) throws Exception {
        int requests = 10_000;

        try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {
            long start = System.currentTimeMillis();

            List<Future<String>> futures = new ArrayList<>();
            for (int i = 0; i < requests; i++) {
                futures.add(executor.submit(() -> {
                    // Simulate: fraud check (100ms) + bank call (200ms) + ledger (20ms)
                    Thread.sleep(100);
                    Thread.sleep(200);
                    Thread.sleep(20);
                    return "authorized";
                }));
            }

            int success = 0;
            for (Future<String> f : futures) {
                f.get();
                success++;
            }

            long elapsed = System.currentTimeMillis() - start;
            System.out.printf("%d requests in %dms (%.0f req/s)%n",
                success, elapsed, (success * 1000.0) / elapsed);
        }
    }
}
```

Output:
```
10000 requests in 1,340ms (7462 req/s)
```

10,000 concurrent requests. 320ms of simulated I/O each. Completed in 1.3 seconds. On 8 carrier threads.

With a 200-thread pool, the same workload takes: 10,000 / 200 × 320ms = **16 seconds**.

You show Nadia the numbers. She nods. "Good. Now what happens when one of those 10,000 threads fails and the others keep running with stale data?"

You don't have an answer yet.

## What You Learned

- **Thread.ofVirtual()** — builder API for creating virtual threads with names and options
- **Thread.startVirtualThread()** — convenience method for quick fire-and-forget threads
- **Thread.isVirtual()** — runtime check for thread type
- **1M virtual threads** — feasible in ~600MB; platform threads die at ~4K
- **newVirtualThreadPerTaskExecutor()** — one virtual thread per task, no pooling
- **Don't pool virtual threads** — they're cheap to create, expensive to reuse incorrectly
- **Carrier threads** — the small platform thread pool that actually runs virtual threads

Virtual threads are cheap. Dangerously cheap. You can spawn 10,000 of them to handle concurrent requests — but what happens when one fails? The others keep running. They might use partial results. They might hold resources. They might complete work that should have been cancelled.

Unstructured concurrency is a resource leak waiting to happen.

---

[← Chapter 1: The Thread Pool Wall](chapter-01-thread-pool-wall.md) | [Chapter 3: Structured Concurrency →](chapter-03-structured-concurrency.md)

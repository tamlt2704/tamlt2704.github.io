# Java Concurrency — Step by Step

---

## Why Concurrency?

Your computer has multiple CPU cores. By default, Java runs on ONE core. Concurrency lets you:
- Use all cores (faster processing)
- Handle multiple users at once (web servers)
- Do background tasks without blocking the UI
- Process large datasets in parallel

---

## The Big Picture

```
Level 1: Threads (low-level, manual)
    ↓
Level 2: Executors (managed thread pools)
    ↓
Level 3: Concurrent Collections (thread-safe data)
    ↓
Level 4: CompletableFuture (async pipelines)
    ↓
Level 5: Virtual Threads (Java 21+ — lightweight)
    ↓
Level 6: Patterns (producer-consumer, fork-join, reactive)
```

---

## Level 1: Threads — The Foundation

### What Is a Thread?

A thread is an independent path of execution. Your `main()` method runs on the "main thread." You can create more.

```java
// Way 1: Extend Thread
class MyThread extends Thread {
    @Override
    public void run() {
        System.out.println("Running on: " + Thread.currentThread().getName());
    }
}

new MyThread().start();  // start() creates a new thread. run() would just call it on the current thread.
```

```java
// Way 2: Implement Runnable (preferred — separates task from thread)
Runnable task = () -> {
    System.out.println("Running on: " + Thread.currentThread().getName());
};

new Thread(task).start();
```

### The Problem: Shared State

Two threads accessing the same variable = disaster:

```java
class Counter {
    int count = 0;  // shared state

    void increment() {
        count++;  // NOT atomic — read, add, write (3 steps)
    }
}

// Two threads incrementing 1000 times each:
// Expected: 2000
// Actual: sometimes 1500, 1800, 1997... (race condition)
```

**Why?** `count++` is actually three operations:
1. Read current value
2. Add 1
3. Write new value

Two threads can read the same value, both add 1, both write — one increment is lost.

### synchronized — The Lock

```java
class Counter {
    private int count = 0;

    synchronized void increment() {  // only one thread at a time
        count++;
    }

    synchronized int getCount() {
        return count;
    }
}
```

`synchronized` means: "Only one thread can be inside this method at a time. Others wait."

**Visualised:**

```
Thread A → increment() → [LOCKED] → count=1 → [UNLOCKED]
Thread B → ........waiting......... → increment() → [LOCKED] → count=2 → [UNLOCKED]
```

### volatile — Visibility Guarantee

Without `volatile`, threads may cache variables locally and not see each other's changes:

```java
class Flag {
    volatile boolean running = true;  // all threads see the latest value

    void stop() {
        running = false;  // other threads will see this immediately
    }

    void run() {
        while (running) {  // without volatile, might loop forever
            // do work
        }
    }
}
```

**`synchronized` vs `volatile`:**

| | `synchronized` | `volatile` |
|-|---------------|-----------|
| Prevents race conditions | ✅ | ❌ (no atomicity) |
| Guarantees visibility | ✅ | ✅ |
| Blocks other threads | ✅ (waiting) | ❌ (non-blocking) |
| Use for | Multi-step operations | Simple flags, status checks |

---

## Level 2: Executors — Don't Manage Threads Yourself

Creating threads manually is expensive and error-prone. Use thread pools:

```java
import java.util.concurrent.*;

// Fixed pool: 4 threads handle all submitted tasks
ExecutorService executor = Executors.newFixedThreadPool(4);

// Submit tasks
executor.submit(() -> processFile("data1.csv"));
executor.submit(() -> processFile("data2.csv"));
executor.submit(() -> processFile("data3.csv"));
executor.submit(() -> processFile("data4.csv"));
executor.submit(() -> processFile("data5.csv"));  // waits for a free thread

// Shutdown when done
executor.shutdown();
executor.awaitTermination(1, TimeUnit.MINUTES);
```

### Thread Pool Types

| Factory Method | Threads | Use Case |
|---------------|---------|----------|
| `newFixedThreadPool(n)` | Fixed N | Known workload, CPU-bound tasks |
| `newCachedThreadPool()` | Grows/shrinks | Many short-lived tasks |
| `newSingleThreadExecutor()` | 1 | Sequential background tasks |
| `newScheduledThreadPool(n)` | Fixed N, timed | Periodic tasks (every 5 min) |
| `newVirtualThreadPerTaskExecutor()` | Unlimited virtual | I/O-heavy tasks (Java 21+) |

### Callable + Future — Get Results Back

`Runnable` returns nothing. `Callable` returns a value:

```java
ExecutorService executor = Executors.newFixedThreadPool(4);

Future<Integer> future = executor.submit(() -> {
    Thread.sleep(1000);  // simulate work
    return 42;
});

// Do other stuff while it computes...

Integer result = future.get();  // blocks until result is ready
System.out.println(result);     // 42
```

**Future methods:**

| Method | What it does |
|--------|-------------|
| `get()` | Block and wait for result |
| `get(timeout, unit)` | Wait with timeout |
| `isDone()` | Check if complete (non-blocking) |
| `cancel(mayInterrupt)` | Cancel the task |

---

## Level 3: Concurrent Collections

Normal collections (`ArrayList`, `HashMap`) are NOT thread-safe. Use concurrent versions:

| Instead of | Use | Difference |
|-----------|-----|-----------|
| `HashMap` | `ConcurrentHashMap` | Lock-free reads, segmented writes |
| `ArrayList` | `CopyOnWriteArrayList` | Copies array on write (good for read-heavy) |
| `LinkedList` as queue | `ConcurrentLinkedQueue` | Non-blocking queue |
| `ArrayDeque` | `LinkedBlockingQueue` | Blocks when empty (producer-consumer) |

### ConcurrentHashMap

```java
ConcurrentHashMap<String, Integer> scores = new ConcurrentHashMap<>();

// Thread-safe atomic operations
scores.put("Alice", 100);
scores.computeIfAbsent("Bob", key -> 0);
scores.merge("Alice", 10, Integer::sum);  // atomic add
```

### BlockingQueue — Producer-Consumer

```java
BlockingQueue<String> queue = new LinkedBlockingQueue<>(100);  // max 100 items

// Producer thread
executor.submit(() -> {
    while (true) {
        String data = fetchData();
        queue.put(data);  // blocks if queue is full
    }
});

// Consumer thread
executor.submit(() -> {
    while (true) {
        String data = queue.take();  // blocks if queue is empty
        process(data);
    }
});
```

**This pattern is everywhere:** web servers, message queues, data pipelines.

---

## Level 4: CompletableFuture — Async Pipelines

Chain async operations without blocking:

```java
CompletableFuture
    .supplyAsync(() -> fetchUser(userId))           // run on thread pool
    .thenApply(user -> user.getEmail())             // transform result
    .thenCompose(email -> sendEmailAsync(email))    // chain another async call
    .thenAccept(result -> log("Email sent"))        // consume final result
    .exceptionally(ex -> {                          // handle any error
        log("Failed: " + ex.getMessage());
        return null;
    });
```

### Combining Multiple Futures

```java
CompletableFuture<User> userFuture = fetchUserAsync(id);
CompletableFuture<List<Order>> ordersFuture = fetchOrdersAsync(id);

// Wait for both, then combine
CompletableFuture<ProfileDTO> profile = userFuture
    .thenCombine(ordersFuture, (user, orders) -> new ProfileDTO(user, orders));
```

### allOf — Wait for Many

```java
List<CompletableFuture<Result>> futures = urls.stream()
    .map(url -> CompletableFuture.supplyAsync(() -> fetch(url)))
    .toList();

CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
    .thenRun(() -> System.out.println("All done!"));
```

### CompletableFuture vs Future

| | `Future` | `CompletableFuture` |
|-|---------|-------------------|
| Get result | `.get()` (blocking) | `.thenApply()` (non-blocking) |
| Chain operations | ❌ Manual | ✅ `.thenCompose()`, `.thenCombine()` |
| Error handling | Try/catch around `.get()` | `.exceptionally()`, `.handle()` |
| Combine multiple | Manual | `.allOf()`, `.anyOf()` |

---

## Level 5: Virtual Threads (Java 21+)

Traditional threads are expensive (~1MB stack each). Virtual threads are lightweight (~few KB):

```java
// Old way: limited by OS thread count
ExecutorService executor = Executors.newFixedThreadPool(200);

// New way: millions of virtual threads
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();

// Or create directly
Thread.startVirtualThread(() -> {
    var result = httpClient.send(request, bodyHandler);  // blocks, but cheaply
    process(result);
});
```

**When to use virtual threads:**
- I/O-bound tasks (HTTP calls, database queries, file reads)
- High concurrency (10,000+ simultaneous connections)
- Blocking code that you want to scale without rewriting as async

**When NOT to use:**
- CPU-bound computation (use fixed thread pool matching CPU cores)
- Synchronized blocks holding locks for a long time (pin the carrier thread)

```java
// Process 100,000 HTTP requests concurrently
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    List<Future<Response>> futures = urls.stream()
        .map(url -> executor.submit(() -> httpClient.send(buildRequest(url), ofString())))
        .toList();

    List<Response> responses = futures.stream()
        .map(f -> f.get())
        .toList();
}
```

This would need 100,000 OS threads before. Now it uses a handful of carrier threads.

---

## Level 6: Patterns

### Producer-Consumer

```
[Producer] → [BlockingQueue] → [Consumer]
   writes          buffer          reads
```

Already covered with `BlockingQueue`. The core pattern for decoupling work generation from work processing.

### Fork-Join (Divide and Conquer)

Split a big task into smaller pieces, process in parallel, combine results:

```java
class SumTask extends RecursiveTask<Long> {
    private final int[] array;
    private final int start, end;
    private static final int THRESHOLD = 1000;

    @Override
    protected Long compute() {
        if (end - start <= THRESHOLD) {
            // Small enough — compute directly
            long sum = 0;
            for (int i = start; i < end; i++) sum += array[i];
            return sum;
        }

        // Split in half
        int mid = (start + end) / 2;
        SumTask left = new SumTask(array, start, mid);
        SumTask right = new SumTask(array, mid, end);

        left.fork();           // run left on another thread
        long rightResult = right.compute();  // compute right here
        long leftResult = left.join();       // wait for left

        return leftResult + rightResult;
    }
}

// Usage
ForkJoinPool pool = new ForkJoinPool();
long total = pool.invoke(new SumTask(bigArray, 0, bigArray.length));
```

### Parallel Streams (Simplest Parallelism)

```java
long sum = list.parallelStream()
    .filter(x -> x > 0)
    .mapToLong(x -> expensiveComputation(x))
    .sum();
```

**Use when:**
- Large dataset (10,000+ items)
- Each item is independent (no shared state)
- Work per item is significant (not just adding numbers)

**Don't use when:**
- Small collections (overhead > benefit)
- Order matters
- Side effects (writing to shared variables)

---

## Common Concurrency Bugs

| Bug | What happens | Prevention |
|-----|-------------|-----------|
| **Race condition** | Two threads modify same data, result is unpredictable | `synchronized`, atomic classes, concurrent collections |
| **Deadlock** | Thread A waits for B's lock, B waits for A's lock — both stuck forever | Always lock in the same order, use timeouts |
| **Starvation** | A thread never gets CPU time (others always take priority) | Fair locks (`new ReentrantLock(true)`) |
| **Memory visibility** | Thread doesn't see other thread's changes | `volatile`, `synchronized`, happens-before |
| **Thread leak** | Threads created but never shut down | Always call `executor.shutdown()` |

### Deadlock Example

```java
// DEADLOCK — don't do this
Object lockA = new Object();
Object lockB = new Object();

// Thread 1
synchronized (lockA) {
    synchronized (lockB) { ... }  // waits for lockB
}

// Thread 2
synchronized (lockB) {
    synchronized (lockA) { ... }  // waits for lockA — DEADLOCK
}

// FIX: Always lock in the same order (A before B)
```

---

## Atomic Classes — Lock-Free Thread Safety

For simple counters/flags, avoid `synchronized` overhead:

```java
import java.util.concurrent.atomic.*;

AtomicInteger counter = new AtomicInteger(0);
counter.incrementAndGet();       // thread-safe ++
counter.addAndGet(5);            // thread-safe += 5
counter.compareAndSet(5, 10);    // if value is 5, set to 10

AtomicReference<String> ref = new AtomicReference<>("initial");
ref.compareAndSet("initial", "updated");
```

---

## Cheat Sheet — What to Use When

| Situation | Tool |
|-----------|------|
| Simple shared counter | `AtomicInteger` |
| Shared flag (stop signal) | `volatile boolean` |
| Protect multi-step operations | `synchronized` or `ReentrantLock` |
| Run tasks in background | `ExecutorService` |
| Get result from async task | `CompletableFuture` |
| Multiple producers/consumers | `BlockingQueue` |
| Thread-safe map | `ConcurrentHashMap` |
| Parallel data processing | `parallelStream()` or Fork-Join |
| 10,000+ concurrent I/O tasks | Virtual Threads (Java 21+) |
| Schedule periodic tasks | `ScheduledExecutorService` |

---

## Practice Exercises

| Exercise | Concepts |
|----------|---------|
| Multi-threaded web scraper | ExecutorService, Future, rate limiting |
| Chat server | Virtual threads, BlockingQueue, ConcurrentHashMap |
| Parallel file processor | Fork-Join, parallel streams |
| Rate limiter | AtomicInteger, ScheduledExecutor, sliding window |
| Thread-safe cache (LRU) | ConcurrentHashMap, ReentrantReadWriteLock |
| Producer-consumer pipeline | BlockingQueue, multiple stages |

---

## Resources

| Resource | What | Free? |
|----------|------|-------|
| [Java Concurrency in Practice (book)](https://jcip.net) | The definitive book | 💰 |
| [Baeldung Concurrency](https://baeldung.com/java-concurrency) | Practical tutorials | ✅ |
| [JEP 444 — Virtual Threads](https://openjdk.org/jeps/444) | Official spec | ✅ |
| [Jakob Jenkov's tutorials](https://jenkov.com/tutorials/java-concurrency/) | Clear explanations | ✅ |
| [Heinz Kabutz's newsletter](https://javaspecialists.eu) | Advanced deep dives | ✅ (some) |

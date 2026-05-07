# Chapter 6: The Thread Avalanche

[← Chapter 5: The Null Minefield](chapter-05-null-safety.md) | [Chapter 7: The Collection Ceremony →](chapter-07-collections.md)

---

## The Incident

Black Friday. 2:14 PM. The payment notification service goes down.

```
java.lang.OutOfMemoryError: unable to create native thread
Active threads: 12,847
```

The service spawns one platform thread per incoming request to send email/SMS notifications. Each thread costs ~1MB of stack memory. 10,000 concurrent requests = 10GB of thread stacks alone. The JVM dies.

```
Platform threads:

Request 1  → Thread 1  (~1MB)     ┐
Request 2  → Thread 2  (~1MB)     │
Request 3  → Thread 3  (~1MB)     │  10,000 threads
...                                │  = ~10 GB stack memory
Request 10K → Thread 10K (~1MB)   ┘  = OOM 💀
```

The Architect: "Use a thread pool. Cap it at 200."

Priya: "Then 9,800 requests queue up and timeout. Virtual threads."

---

## What Are Virtual Threads?

Virtual threads (Java 21, Project Loom) are lightweight threads managed by the JVM, not the OS. They cost ~1KB each instead of ~1MB.

```
Platform threads:                    Virtual threads:

OS Thread 1 ← 1 task                OS Thread 1 ← many tasks
OS Thread 2 ← 1 task                OS Thread 2 ← many tasks
OS Thread 3 ← 1 task                (JVM schedules virtual threads
...                                   onto a small pool of OS threads)
OS Thread 10K ← 1 task

Memory: ~10 GB                       Memory: ~10 MB
OS limit: ~10K threads               JVM limit: millions
```

When a virtual thread blocks on I/O (HTTP call, DB query, file read), the JVM **unmounts** it from the carrier thread and mounts another virtual thread. No OS thread is wasted waiting.

---

## Creating Virtual Threads

Three ways:

```java
// 1. Thread.ofVirtual()
Thread vt = Thread.ofVirtual().start(() -> {
    System.out.println("Hello from virtual thread: " + Thread.currentThread());
});

// 2. Executor (most common in production)
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    executor.submit(() -> sendEmail(notification));
    executor.submit(() -> sendSms(notification));
}

// 3. Thread.startVirtualThread() — shorthand
Thread.startVirtualThread(() -> doWork());
```

### The Test

```java
@Test
void virtualThread_shouldBeVirtual() throws Exception {
    var thread = Thread.ofVirtual().start(() -> {});
    thread.join();

    assertTrue(thread.isVirtual());
}

@Test
void virtualThreadExecutor_shouldHandleThousandsOfTasks() throws Exception {
    AtomicInteger counter = new AtomicInteger(0);

    try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
        IntStream.range(0, 10_000).forEach(i ->
            executor.submit(() -> {
                Thread.sleep(Duration.ofMillis(100)); // simulate I/O
                counter.incrementAndGet();
            }));
    } // auto-closes, waits for all tasks

    assertEquals(10_000, counter.get());
}
```

10,000 tasks, each sleeping 100ms. With platform threads, you'd need 10,000 threads or wait sequentially. With virtual threads, the JVM handles it with a handful of carrier threads.

---

## The Notification Service Fix

Before (platform threads, OOM on Black Friday):

```java
ExecutorService pool = Executors.newFixedThreadPool(200);

for (Notification n : notifications) {
    pool.submit(() -> {
        sendEmail(n);   // blocks ~500ms on SMTP
        sendSms(n);     // blocks ~300ms on SMS API
    });
}
```

After (virtual threads, handles 100K concurrent):

```java
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (Notification n : notifications) {
        executor.submit(() -> {
            sendEmail(n);
            sendSms(n);
        });
    }
}
```

One line changed. The executor creates a virtual thread per task instead of queuing onto a fixed pool. Each virtual thread blocks on I/O, yields its carrier thread, and resumes when the I/O completes.

### The Test

```java
@Test
void notificationService_shouldSend10kNotificationsUnder5Seconds() {
    List<Notification> notifications = IntStream.range(0, 10_000)
        .mapToObj(i -> new Notification("user-" + i, "Payment processed"))
        .toList();

    long start = System.currentTimeMillis();

    try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
        notifications.forEach(n ->
            executor.submit(() -> {
                simulateEmailSend(n);  // 100ms I/O
            }));
    }

    long elapsed = System.currentTimeMillis() - start;
    assertTrue(elapsed < 5000, "Took " + elapsed + "ms");
}
```

---

## When NOT to Use Virtual Threads

The Architect raises a finger. "Virtual threads aren't magic."

| Use Virtual Threads For | Don't Use Virtual Threads For |
|---|---|
| I/O-bound work (HTTP, DB, file) | CPU-bound work (image resize, crypto) |
| High-concurrency servers | Tasks that hold locks for a long time |
| Fan-out API calls | Code using `synchronized` on hot paths |

### CPU-Bound Work

Virtual threads yield when they block on I/O. CPU-bound work never blocks — the virtual thread monopolizes the carrier thread:

```java
// ❌ Bad: CPU-bound work on virtual threads
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    executor.submit(() -> {
        // This never yields — hogs the carrier thread
        BigInteger result = factorial(100_000);
    });
}

// ✓ Good: Use platform threads for CPU work
ExecutorService cpuPool = Executors.newFixedThreadPool(
    Runtime.getRuntime().availableProcessors());
cpuPool.submit(() -> factorial(100_000));
```

### Pinning

Virtual threads get **pinned** to their carrier thread when inside a `synchronized` block or a native method. Pinned = can't yield = defeats the purpose.

```java
// ❌ Pinning: synchronized blocks pin the virtual thread
synchronized (lock) {
    httpClient.send(request, bodyHandler); // blocks, but can't yield
}

// ✓ Use ReentrantLock instead — virtual threads can yield while waiting
ReentrantLock lock = new ReentrantLock();
lock.lock();
try {
    httpClient.send(request, bodyHandler);
} finally {
    lock.unlock();
}
```

Detect pinning with: `-Djdk.tracePinnedThreads=short`

---

## Structured Concurrency (Preview)

Java 21 introduced **structured concurrency** as a preview feature. The idea: when you fan out to multiple tasks, their lifetimes are bounded by a scope. If one fails, the others are cancelled.

```java
// Preview feature — requires --enable-preview
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Subtask<String> email = scope.fork(() -> sendEmail(notification));
    Subtask<String> sms   = scope.fork(() -> sendSms(notification));

    scope.join();           // wait for both
    scope.throwIfFailed();  // propagate first failure

    return new NotificationResult(email.get(), sms.get());
}
```

If `sendEmail` throws, `sendSms` is cancelled automatically. No orphaned threads. No leaked resources.

```
Traditional:                         Structured:

  main thread                          main thread
      │                                    │
      ├── spawn email thread               ├── scope {
      ├── spawn sms thread                 │     fork email
      │                                    │     fork sms
      │   (email fails)                    │     (email fails)
      │   sms keeps running...             │     sms auto-cancelled ✓
      │   sms finishes (wasted work)       │   }
      │                                    │
      └── now what?                        └── exception propagated
```

---

## Virtual Threads with Spring Boot

Spring Boot 3.2+ supports virtual threads with one property:

```properties
# application.properties
spring.threads.virtual.enabled=true
```

Every incoming HTTP request is handled on a virtual thread. No code changes. Your existing `@RestController` methods just work — but now the server can handle thousands of concurrent requests without a massive thread pool.

### The Test

```java
@SpringBootTest(properties = "spring.threads.virtual.enabled=true")
@AutoConfigureMockMvc
class VirtualThreadControllerTest {

    @Autowired MockMvc mockMvc;

    @Test
    void requestHandler_shouldRunOnVirtualThread() throws Exception {
        mockMvc.perform(get("/thread-info"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.virtual").value(true));
    }
}

@RestController
class ThreadInfoController {
    @GetMapping("/thread-info")
    Map<String, Object> info() {
        return Map.of(
            "virtual", Thread.currentThread().isVirtual(),
            "name", Thread.currentThread().toString()
        );
    }
}
```

---

## Platform vs Virtual: The Cheat Sheet

```
┌──────────────────┬──────────────────────┬──────────────────────┐
│                  │ Platform Thread      │ Virtual Thread       │
├──────────────────┼──────────────────────┼──────────────────────┤
│ Managed by       │ OS                   │ JVM                  │
│ Stack size       │ ~1 MB                │ ~1 KB (grows)        │
│ Creation cost    │ Expensive            │ Cheap                │
│ Max count        │ ~10K (OS limit)      │ Millions             │
│ Blocks on I/O    │ Wastes OS thread     │ Yields carrier       │
│ CPU-bound work   │ ✓ Good               │ ✗ Monopolizes carrier│
│ synchronized     │ Fine                 │ Pins (avoid)         │
│ ReentrantLock    │ Fine                 │ ✓ Yields properly    │
│ Thread-local     │ Fine                 │ Expensive at scale   │
│ Best for         │ CPU work, legacy     │ I/O, high concurrency│
└──────────────────┴──────────────────────┴──────────────────────┘
```

---

## What You Learned

| Concept | One-liner |
|---|---|
| Virtual threads | Lightweight JVM-managed threads, ~1KB each |
| `Executors.newVirtualThreadPerTaskExecutor()` | One virtual thread per task — the go-to executor |
| `Thread.ofVirtual()` | Create a virtual thread manually |
| Carrier thread | The OS thread a virtual thread runs on |
| Mounting/unmounting | JVM swaps virtual threads on/off carriers at I/O points |
| Pinning | `synchronized` blocks prevent unmounting — use `ReentrantLock` |
| Structured concurrency | Scoped fan-out — if one fails, cancel the rest (preview) |
| Spring Boot integration | `spring.threads.virtual.enabled=true` — one line |
| When NOT to use | CPU-bound work, `synchronized` hot paths, thread-local heavy code |

---

## The Foreshadow

The notification service survives Black Friday. But Marcus opens `ReportGenerator.java`:

```java
List<String> currencies = new ArrayList<>();
currencies.add("USD");
currencies.add("EUR");
currencies.add("GBP");
currencies = Collections.unmodifiableList(currencies);

Map<String, BigDecimal> rates = new HashMap<>();
rates.put("USD", BigDecimal.ONE);
rates.put("EUR", new BigDecimal("0.92"));
rates.put("GBP", new BigDecimal("0.79"));
rates = Collections.unmodifiableMap(rates);

// And later...
String last = currencies.get(currencies.size() - 1); // no getLast()
```

Six lines to create an immutable list. Four lines for a map. And getting the last element requires `size() - 1`.

Priya: "Java 9 gave us factory methods. Java 21 gave us sequenced collections. Use them."

---

[← Chapter 5: The Null Minefield](chapter-05-null-safety.md) | [Chapter 7: The Collection Ceremony →](chapter-07-collections.md)

# Chapter 12: Virtual Threads

[← Chapter 11: Fork/Join](chapter-11-forkjoin.md) | [Chapter 13: Deadlocks →](chapter-13-deadlocks.md)

---

## The Problem

PulseMetrics has 100,000 concurrent WebSocket connections for real-time dashboards. Each connection needs a thread to handle incoming messages and push updates:

```java
public class DashboardServer {
    private final ExecutorService pool = Executors.newFixedThreadPool(200);

    public void handleConnection(WebSocket ws) {
        pool.submit(() -> {
            while (ws.isOpen()) {
                Message msg = ws.receive();  // Blocks waiting for client message
                Snapshot data = computeSnapshot(msg.getDashboardId());
                ws.send(data);               // Blocks on network write
            }
        });
    }
}
```

200 threads for 100,000 connections. Each thread handles one connection at a time, blocking on I/O. At any moment, 199 threads are blocked waiting for network I/O while 99,800 connections are unserved.

Increasing the pool to 100,000 threads? Each platform thread uses ~1MB of stack:

```
100,000 threads × 1MB = 100GB of memory just for stacks
```

```
Exception in thread "main" java.lang.OutOfMemoryError: unable to create native thread
```

Omar: "We can't scale to 100K connections with platform threads. We'd need 100GB of RAM just for thread stacks."

Nadia: "What about async/reactive? NIO?"

You could rewrite everything with callbacks and event loops. But that means rewriting the entire codebase into callback hell. There's a better way in Java 21.

## Virtual Threads (Project Loom)

Virtual threads are lightweight threads managed by the JVM, not the OS:

```java
// Platform thread: ~1MB stack, OS-scheduled, expensive
Thread platform = new Thread(() -> doWork());

// Virtual thread: ~1KB initial stack, JVM-scheduled, cheap
Thread virtual = Thread.startVirtualThread(() -> doWork());
```

| | Platform Thread | Virtual Thread |
|---|---|---|
| Stack size | ~1MB (fixed) | ~1KB (grows as needed) |
| Creation cost | ~1ms | ~1μs |
| Max count | ~10K (memory limited) | Millions |
| Scheduled by | OS kernel | JVM (on carrier threads) |
| Blocking cost | Expensive (thread is idle) | Cheap (carrier is freed) |

## Creating Virtual Threads

```java
// Way 1: Thread.startVirtualThread
Thread vt = Thread.startVirtualThread(() -> {
    System.out.println("Running on: " + Thread.currentThread());
});

// Way 2: Thread.ofVirtual()
Thread vt = Thread.ofVirtual()
    .name("dashboard-handler-", 0)  // dashboard-handler-0, dashboard-handler-1, ...
    .start(() -> handleConnection());

// Way 3: ExecutorService (preferred for production)
try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (int i = 0; i < 100_000; i++) {
        executor.submit(() -> handleConnection());
    }
}  // Auto-closes, waits for all tasks
```

## How Virtual Threads Work

Virtual threads run on a small pool of **carrier threads** (platform threads). When a virtual thread blocks on I/O, the JVM **unmounts** it from the carrier and mounts another virtual thread:

```
Carrier Thread 1: [VT-1 running] → [VT-1 blocks on I/O] → [VT-2 mounted, running]
Carrier Thread 2: [VT-3 running] → [VT-3 blocks on I/O] → [VT-4 mounted, running]

VT-1: running → blocked (unmounted, waiting for I/O) → I/O ready → remounted → running
```

The carrier pool has ~CPU-count threads. Millions of virtual threads multiplex onto these few carriers. When a virtual thread blocks, it costs almost nothing — just a few KB of stack stored on the heap.

## The Fix: One Virtual Thread Per Connection

```java
public class DashboardServer {
    public void start() {
        try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
            ServerSocket server = new ServerSocket(8080);
            while (true) {
                Socket client = server.accept();
                executor.submit(() -> handleConnection(client));
            }
        }
    }

    private void handleConnection(Socket client) {
        // Simple blocking code — but on a virtual thread!
        try (client;
             var in = new BufferedReader(new InputStreamReader(client.getInputStream()));
             var out = new PrintWriter(client.getOutputStream(), true)) {

            String line;
            while ((line = in.readLine()) != null) {  // Blocks — virtual thread unmounts
                String response = processRequest(line);
                out.println(response);                 // Blocks — virtual thread unmounts
            }
        } catch (IOException e) {
            // Connection closed
        }
    }
}
```

100,000 connections, each with its own virtual thread. Simple blocking I/O code. No callbacks. No reactive streams. The JVM handles the multiplexing.

## What NOT to Do with Virtual Threads

### Don't Pool Virtual Threads

```java
// WRONG: pooling virtual threads defeats the purpose
ExecutorService pool = Executors.newFixedThreadPool(200);  // Platform threads, limited

// RIGHT: one virtual thread per task, no pooling
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();
```

Virtual threads are cheap. Create millions. Don't pool them.

### Don't Hold Locks During I/O

```java
// BAD: pins the virtual thread to its carrier
synchronized (lock) {
    httpClient.send(request);  // Blocks while holding monitor → carrier is pinned!
}

// GOOD: use ReentrantLock (doesn't pin)
lock.lock();
try {
    httpClient.send(request);  // Virtual thread unmounts cleanly
} finally {
    lock.unlock();
}
```

`synchronized` blocks **pin** the virtual thread to its carrier — the carrier can't run other virtual threads. Use `ReentrantLock` instead for code that blocks while holding a lock.

### Don't Use for CPU-Bound Work

```java
// WRONG: CPU-bound work on virtual threads — no benefit
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (int i = 0; i < 1000; i++) {
        executor.submit(() -> computeHash(data));  // CPU-bound, never blocks
    }
}

// RIGHT: use a fixed platform thread pool for CPU work
ExecutorService cpuPool = Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors());
```

Virtual threads shine when tasks block on I/O. For CPU-bound work, platform threads with a fixed pool are better.

## Structured Concurrency (Preview in Java 21)

Structured concurrency ensures that child tasks don't outlive their parent scope:

```java
import java.util.concurrent.StructuredTaskScope;

public EnrichedEvent enrich(Event raw) throws Exception {
    try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
        // Fork subtasks — each runs on its own virtual thread
        Subtask<GeoData> geo = scope.fork(() -> geoService.lookup(raw.ip()));
        Subtask<UserProfile> user = scope.fork(() -> userService.fetch(raw.userId()));
        Subtask<RiskScore> risk = scope.fork(() -> fraudService.score(raw));

        scope.join();            // Wait for all subtasks
        scope.throwIfFailed();   // Propagate any exception

        return new EnrichedEvent(raw, geo.get(), user.get(), risk.get());
    }
    // Scope closes: if any subtask is still running, it's cancelled
}
```

Benefits:
- **Lifetime bound**: subtasks can't outlive the scope
- **Error propagation**: if one fails, others are cancelled
- **Observability**: thread dumps show the parent-child relationship

### ShutdownOnSuccess: First Result Wins

```java
try (var scope = new StructuredTaskScope.ShutdownOnSuccess<Data>()) {
    scope.fork(() -> queryReplica1());
    scope.fork(() -> queryReplica2());
    scope.fork(() -> queryReplica3());

    scope.join();
    Data fastest = scope.result();  // First successful result
    // Other subtasks are cancelled automatically
}
```

## PulseMetrics: Virtual Thread Architecture

```java
public class PulseMetricsServer {
    private final ExecutorService connectionHandler = Executors.newVirtualThreadPerTaskExecutor();
    private final ExecutorService cpuPool = Executors.newFixedThreadPool(
        Runtime.getRuntime().availableProcessors()
    );

    public void start() throws IOException {
        var server = new ServerSocket(9090);
        System.out.println("Accepting connections on :9090");

        while (true) {
            Socket client = server.accept();
            connectionHandler.submit(() -> handleDashboard(client));
        }
    }

    private void handleDashboard(Socket client) {
        try (client) {
            var reader = new BufferedReader(new InputStreamReader(client.getInputStream()));
            var writer = new PrintWriter(client.getOutputStream(), true);

            String dashboardId = reader.readLine();

            // Enrich with structured concurrency
            while (true) {
                Snapshot snapshot = fetchSnapshot(dashboardId);
                writer.println(serialize(snapshot));
                Thread.sleep(1000);  // Push every second — virtual thread sleeps cheaply
            }
        } catch (Exception e) {
            // Connection closed
        }
    }

    private Snapshot fetchSnapshot(String dashboardId) throws Exception {
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            var events = scope.fork(() -> eventStore.getRecent(dashboardId));
            var metrics = scope.fork(() -> metricsStore.getAggregates(dashboardId));
            var alerts = scope.fork(() -> alertStore.getActive(dashboardId));

            scope.join();
            scope.throwIfFailed();

            return new Snapshot(events.get(), metrics.get(), alerts.get());
        }
    }
}
```

100K dashboard connections, each on a virtual thread. Each snapshot fetch fans out to three services using structured concurrency. Simple, readable, blocking code — but scales to millions of concurrent operations.

## Migrating from Platform Threads

The migration is often a one-line change:

```java
// Before: limited to 200 concurrent connections
ExecutorService pool = Executors.newFixedThreadPool(200);

// After: unlimited concurrent connections
ExecutorService pool = Executors.newVirtualThreadPerTaskExecutor();
```

But check for:
1. **synchronized + I/O** → replace with `ReentrantLock`
2. **ThreadLocal abuse** → virtual threads are cheap, don't cache expensive objects in ThreadLocal
3. **Thread pool sizing assumptions** → virtual threads don't need sizing

## What You Learned

- **Virtual threads** — lightweight (KB not MB), millions possible, JVM-scheduled
- **newVirtualThreadPerTaskExecutor()** — one virtual thread per task, no pooling
- **Blocking is cheap** — virtual thread unmounts from carrier, carrier runs other work
- **Pinning** — `synchronized` + blocking pins the carrier; use `ReentrantLock` instead
- **Structured concurrency** — child tasks bound to parent scope, automatic cancellation
- **Use for I/O-bound work** — not CPU-bound (use platform thread pools for CPU)
- **Don't pool virtual threads** — they're cheap to create, expensive to pool

100K connections handled. But at 3 AM, the system freezes. No errors. No exceptions. Just... nothing. Thread dump shows two threads waiting for each other. Deadlock.

---

[← Chapter 11: Fork/Join](chapter-11-forkjoin.md) | [Chapter 13: Deadlocks →](chapter-13-deadlocks.md)

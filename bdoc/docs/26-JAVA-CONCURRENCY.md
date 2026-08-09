# Chapter 26: Java Concurrency — Build a Thread-Safe Order Processing System

## What you'll learn

- Thread lifecycle, creation, and the Java Memory Model
- `synchronized`, `volatile`, and intrinsic locks
- `java.util.concurrent` — the modern concurrency toolkit
- ExecutorService, CompletableFuture, and structured concurrency
- Concurrent collections (ConcurrentHashMap, BlockingQueue)
- Lock-free programming (AtomicInteger, CAS)
- Common pitfalls: deadlocks, race conditions, visibility
- Build: a multi-threaded order processing pipeline

---

## PART 1: Foundations

## 26.1 Threads — the mental model

```
Process (your JVM):
┌─────────────────────────────────────────────────┐
│  Shared Heap Memory                              │
│  (objects, static fields)                        │
│                                                  │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │ Thread 1│  │ Thread 2│  │ Thread 3│        │
│  │ Stack   │  │ Stack   │  │ Stack   │        │
│  │ (local  │  │ (local  │  │ (local  │        │
│  │  vars)  │  │  vars)  │  │  vars)  │        │
│  └─────────┘  └─────────┘  └─────────┘        │
└─────────────────────────────────────────────────┘
```

- Each thread has its own **stack** (local variables, method calls)
- All threads share the **heap** (objects, fields)
- Problems happen when threads access shared heap data concurrently

## 26.2 Creating threads

```java
// Way 1: Extend Thread (legacy — don't use)
class MyThread extends Thread {
    public void run() { System.out.println("Running"); }
}
new MyThread().start();

// Way 2: Runnable (functional, preferred)
Thread t = new Thread(() -> System.out.println("Running"));
t.start();

// Way 3: ExecutorService (production code — ALWAYS use this)
ExecutorService executor = Executors.newFixedThreadPool(4);
executor.submit(() -> processOrder(order));
executor.shutdown();
```

## 26.3 Race conditions — the core problem

```java
class Counter {
    private int count = 0;

    void increment() {
        count++;  // NOT atomic! Read → Modify → Write (3 steps)
    }
}

// Two threads calling increment() 1000 times each:
// Expected: 2000. Actual: could be 1500-2000 (race condition)
//
// Thread A reads count=5
// Thread B reads count=5        ← sees stale value!
// Thread A writes count=6
// Thread B writes count=6       ← overwrites A's increment!
```

## 26.4 synchronized — the basic lock

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

**How it works:**
- Every object has an intrinsic lock (monitor)
- `synchronized` method acquires lock on `this`
- Other threads trying to enter any `synchronized` method on SAME object must wait
- Lock released when method returns (even on exception)

**Synchronized block (finer granularity):**
```java
class OrderService {
    private final Object lock = new Object();
    private final Map<String, Order> orders = new HashMap<>();

    void addOrder(Order order) {
        synchronized (lock) {  // lock only what's needed
            orders.put(order.getId(), order);
        }
        // Code outside the block runs concurrently
        notifyExternalSystem(order);
    }
}
```

## 26.5 volatile — visibility guarantee

```java
class StopFlag {
    private volatile boolean running = true;  // volatile = always read from main memory

    void stop() { running = false; }

    void run() {
        while (running) {  // without volatile, thread might cache `running = true` forever
            doWork();
        }
    }
}
```

`volatile` guarantees:
- Reads always see the latest write (no CPU cache staleness)
- Does NOT provide atomicity (count++ is still broken with volatile)

**Use `volatile` for:** flags, status fields, singleton double-checked locking.
**Don't use for:** compound operations (check-then-act, read-modify-write).

## 26.6 Java Memory Model (JMM) — the rules

```
Thread 1 CPU Cache              Main Memory              Thread 2 CPU Cache
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ count = 5       │     │ count = 5       │     │ count = 5       │
│ (cached copy)   │     │ (truth)         │     │ (cached copy)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

Without synchronization, threads may see stale data. The JMM defines **happens-before** relationships that guarantee visibility:

- Unlock → subsequent Lock on same monitor
- Write to volatile → subsequent Read of same volatile
- Thread.start() → first action in started thread
- Thread termination → Thread.join() return

---

## PART 2: java.util.concurrent

## 26.7 ExecutorService — thread pool management

```java
// Fixed thread pool (production default)
ExecutorService executor = Executors.newFixedThreadPool(
    Runtime.getRuntime().availableProcessors()
);

// Submit tasks
Future<OrderResult> future = executor.submit(() -> processOrder(order));

// Get result (blocks until done)
OrderResult result = future.get(5, TimeUnit.SECONDS); // with timeout

// Shutdown gracefully
executor.shutdown();                           // no new tasks, finish existing
executor.awaitTermination(30, TimeUnit.SECONDS); // wait for completion
executor.shutdownNow();                        // interrupt if still running
```

**Thread pool types:**
| Type | Threads | Use case |
|------|---------|----------|
| `newFixedThreadPool(n)` | Fixed n | CPU-bound work |
| `newCachedThreadPool()` | 0..∞ (reuses idle) | Many short I/O tasks |
| `newSingleThreadExecutor()` | 1 | Sequential task queue |
| `newScheduledThreadPool(n)` | Fixed n | Periodic/delayed tasks |
| `newVirtualThreadPerTaskExecutor()` | Virtual threads (Java 21+) | Massive I/O concurrency |

## 26.8 CompletableFuture — async pipelines

```java
CompletableFuture<OrderResult> pipeline =
    CompletableFuture
        .supplyAsync(() -> validateOrder(order), executor)        // Step 1: validate
        .thenApplyAsync(validated -> calculatePrice(validated), executor)  // Step 2: price
        .thenApplyAsync(priced -> reserveInventory(priced), executor)      // Step 3: reserve
        .thenApplyAsync(reserved -> chargePayment(reserved), executor)     // Step 4: payment
        .exceptionally(ex -> {
            log.error("Order failed: {}", ex.getMessage());
            return OrderResult.failed(ex.getMessage());
        });

// Combine multiple independent futures
CompletableFuture<Void> allDone = CompletableFuture.allOf(
    fetchUserProfile(userId),
    fetchOrderHistory(userId),
    fetchRecommendations(userId)
);

// Race: first to complete wins
CompletableFuture<String> fastest = CompletableFuture.anyOf(
    callServiceA(), callServiceB(), callServiceC()
).thenApply(Object::toString);
```

**Key methods:**
| Method | Purpose |
|--------|---------|
| `supplyAsync(supplier)` | Start async computation returning a value |
| `thenApply(fn)` | Transform result (like .map) |
| `thenCompose(fn)` | Chain another CompletableFuture (like .flatMap) |
| `thenAccept(consumer)` | Consume result, return void |
| `exceptionally(fn)` | Handle errors |
| `allOf(futures)` | Wait for ALL to complete |
| `anyOf(futures)` | Wait for FIRST to complete |

## 26.9 Concurrent Collections

```java
// ConcurrentHashMap — thread-safe, lock-free reads, segmented writes
ConcurrentMap<String, Order> orders = new ConcurrentHashMap<>();
orders.put("ORD-001", order);
orders.computeIfAbsent("ORD-001", id -> createNewOrder(id)); // atomic

// CopyOnWriteArrayList — reads never lock, writes copy entire array
// Perfect for: read-heavy, rarely-modified lists (listeners, config)
List<OrderListener> listeners = new CopyOnWriteArrayList<>();

// BlockingQueue — producer/consumer pattern
BlockingQueue<Order> orderQueue = new LinkedBlockingQueue<>(1000);
orderQueue.put(order);           // blocks if full
Order next = orderQueue.take();  // blocks if empty

// ConcurrentLinkedQueue — non-blocking, lock-free
Queue<Task> taskQueue = new ConcurrentLinkedQueue<>();
```

## 26.10 Locks — more control than synchronized

```java
// ReentrantLock — same as synchronized but with tryLock, timeout, interruptible
private final ReentrantLock lock = new ReentrantLock();

void processOrder(Order order) {
    lock.lock();
    try {
        // critical section
    } finally {
        lock.unlock(); // ALWAYS in finally
    }
}

// TryLock — non-blocking attempt
if (lock.tryLock(100, TimeUnit.MILLISECONDS)) {
    try { /* got the lock */ }
    finally { lock.unlock(); }
} else {
    // couldn't get lock — do something else
}

// ReadWriteLock — multiple readers OR one writer
private final ReadWriteLock rwLock = new ReentrantReadWriteLock();

Order getOrder(String id) {
    rwLock.readLock().lock();  // multiple threads can read simultaneously
    try { return orders.get(id); }
    finally { rwLock.readLock().unlock(); }
}

void updateOrder(Order order) {
    rwLock.writeLock().lock(); // exclusive — blocks all readers and writers
    try { orders.put(order.getId(), order); }
    finally { rwLock.writeLock().unlock(); }
}
```

## 26.11 Atomic variables — lock-free operations

```java
private final AtomicInteger orderCount = new AtomicInteger(0);
private final AtomicLong totalRevenue = new AtomicLong(0);
private final AtomicReference<OrderStatus> status = new AtomicReference<>(PENDING);

// Atomic increment (uses CPU CAS instruction — no lock needed)
int newCount = orderCount.incrementAndGet();

// Compare-And-Swap (CAS) — the foundation of lock-free programming
boolean success = status.compareAndSet(PENDING, PROCESSING);
// Only succeeds if current value is PENDING → sets to PROCESSING atomically

// Atomic update with function
totalRevenue.updateAndGet(current -> current + order.getAmount());
```

**CAS loop pattern:**
```java
// Retry until CAS succeeds (optimistic locking)
int expected, updated;
do {
    expected = counter.get();
    updated = expected + 1;
} while (!counter.compareAndSet(expected, updated));
```

---

## PART 3: Build — Order Processing Pipeline

## 26.12 Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ HTTP API    │────►│ Order Queue      │────►│ Order Processor  │
│ (receives   │     │ (BlockingQueue)  │     │ (thread pool)    │
│  orders)    │     └──────────────────┘     └────────┬─────────┘
└─────────────┘                                       │
                                                      ├── Validate
                                                      ├── Price
                                                      ├── Reserve Inventory
                                                      ├── Charge Payment
                                                      └── Notify
                                                            │
                                              ┌─────────────▼─────────────┐
                                              │ Result Queue              │
                                              │ (completed/failed orders) │
                                              └───────────────────────────┘
```

## 26.13 Implementation

```java
public class OrderProcessingSystem {
    private final BlockingQueue<Order> incomingOrders = new LinkedBlockingQueue<>(10_000);
    private final BlockingQueue<OrderResult> results = new LinkedBlockingQueue<>();
    private final ExecutorService processorPool = Executors.newFixedThreadPool(8);
    private final ConcurrentMap<String, OrderStatus> statusMap = new ConcurrentHashMap<>();
    private final AtomicLong processedCount = new AtomicLong(0);
    private volatile boolean running = true;

    // Producer: submit an order
    public boolean submitOrder(Order order) {
        statusMap.put(order.getId(), OrderStatus.QUEUED);
        return incomingOrders.offer(order); // non-blocking, returns false if full
    }

    // Consumer: process orders from queue
    public void startProcessing() {
        // Start multiple consumer threads
        for (int i = 0; i < 4; i++) {
            processorPool.submit(this::consumerLoop);
        }
    }

    private void consumerLoop() {
        while (running) {
            try {
                Order order = incomingOrders.poll(1, TimeUnit.SECONDS);
                if (order == null) continue; // timeout, check if still running

                processOrder(order);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }

    private void processOrder(Order order) {
        statusMap.put(order.getId(), OrderStatus.PROCESSING);

        CompletableFuture
            .supplyAsync(() -> validate(order), processorPool)
            .thenApply(this::calculatePrice)
            .thenApply(this::reserveInventory)
            .thenApply(this::chargePayment)
            .thenAccept(result -> {
                statusMap.put(order.getId(), OrderStatus.COMPLETED);
                results.add(OrderResult.success(order));
                processedCount.incrementAndGet();
            })
            .exceptionally(ex -> {
                statusMap.put(order.getId(), OrderStatus.FAILED);
                results.add(OrderResult.failed(order, ex.getMessage()));
                return null;
            });
    }

    // Status check (thread-safe — ConcurrentHashMap)
    public OrderStatus getStatus(String orderId) {
        return statusMap.getOrDefault(orderId, OrderStatus.UNKNOWN);
    }

    // Metrics (thread-safe — AtomicLong)
    public long getProcessedCount() {
        return processedCount.get();
    }

    // Graceful shutdown
    public void shutdown() {
        running = false;
        processorPool.shutdown();
        try {
            processorPool.awaitTermination(30, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            processorPool.shutdownNow();
        }
    }
}
```

## 26.14 Common concurrency pitfalls

### Deadlock

```java
// Thread 1: lock A → try lock B
// Thread 2: lock B → try lock A
// Both wait forever!

// Prevention:
// 1. Always acquire locks in the same order
// 2. Use tryLock with timeout
// 3. Use a single coarse lock (simpler but less concurrent)
```

### Lost update (check-then-act)

```java
// ❌ Race condition:
if (!orders.containsKey(id)) {     // Thread A and B both check
    orders.put(id, new Order());   // Both insert!
}

// ✅ Atomic:
orders.computeIfAbsent(id, k -> new Order()); // single atomic operation
```

### Thread starvation

```java
// ❌ Thread pool too small for blocking tasks:
ExecutorService pool = Executors.newFixedThreadPool(2);
// If 2 tasks are blocking on I/O, no threads available for new work

// ✅ Use separate pools for CPU and I/O:
ExecutorService cpuPool = Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors());
ExecutorService ioPool = Executors.newCachedThreadPool(); // scales with demand
```

---

## Summary

✅ Thread fundamentals: shared heap, thread-local stack, happens-before
✅ synchronized and volatile — when to use each
✅ ExecutorService — thread pools for production code
✅ CompletableFuture — async pipelines with error handling
✅ Concurrent collections — ConcurrentHashMap, BlockingQueue, CopyOnWriteArrayList
✅ Locks and Atomics — ReentrantLock, ReadWriteLock, AtomicInteger/CAS
✅ Built: a thread-safe order processing system with queues, pools, and metrics
✅ Common pitfalls: deadlocks, race conditions, lost updates, starvation

## Key takeaway

**Concurrency is about safely sharing mutable state.** The best solution (in order of preference):
1. Don't share state (message passing, immutable objects)
2. Share immutable state (final fields, unmodifiable collections)
3. Share mutable state with synchronization (locks, atomics, concurrent collections)

---

→ [Chapter 27: Kafka Messaging Patterns](./27-KAFKA-MESSAGING-PATTERNS.md)

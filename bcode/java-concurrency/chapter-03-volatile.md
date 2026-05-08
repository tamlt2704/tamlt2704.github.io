# Chapter 3: Volatile Signals

[← Chapter 2: Synchronization](chapter-02-synchronization.md) | [Chapter 4: Locks →](chapter-04-locks.md)

---

## The Problem

PulseMetrics has a graceful shutdown mechanism. When the system receives a shutdown signal, all ingestion threads should stop:

```java
public class IngestionWorker implements Runnable {
    private boolean running = true;

    public void shutdown() {
        running = false;  // Signal the thread to stop
    }

    @Override
    public void run() {
        while (running) {  // Check the flag every iteration
            Event event = receiveEvent();
            process(event);
        }
        System.out.println("Worker stopped gracefully");
    }
}
```

The main thread calls `shutdown()`. The worker thread keeps running. Forever.

Omar: "I called shutdown 10 minutes ago. The thread is still processing events. I had to kill -9 the process."

## Why It Doesn't Work

The JVM is allowed to **cache** `running` in the worker thread's CPU register. The worker thread never re-reads from main memory — it sees its cached copy (`true`) forever.

```
Main thread:     running = false  (writes to main memory)
Worker thread:   while (running)  (reads from CPU cache — still true!)
```

This isn't a bug in your code's logic. It's the Java Memory Model allowing optimizations that break cross-thread visibility.

## volatile: Visibility Guarantee

The `volatile` keyword forces every read to go to main memory and every write to flush to main memory:

```java
public class IngestionWorker implements Runnable {
    private volatile boolean running = true;  // volatile!

    public void shutdown() {
        running = false;  // Write goes directly to main memory
    }

    @Override
    public void run() {
        while (running) {  // Read comes directly from main memory
            Event event = receiveEvent();
            process(event);
        }
        System.out.println("Worker stopped gracefully");
    }
}
```

Now when the main thread writes `false`, the worker thread sees it on the next loop iteration.

## What volatile Guarantees

1. **Visibility**: writes to a volatile variable are immediately visible to all threads
2. **Ordering**: reads/writes of volatile variables cannot be reordered by the compiler or CPU

What volatile does NOT guarantee:
- **Atomicity**: `count++` on a volatile int is still a race condition (read-modify-write)

```java
private volatile int count = 0;

// STILL BROKEN — volatile doesn't make ++ atomic
public void increment() {
    count++;  // Read count, add 1, write count — three operations
}
```

## volatile vs synchronized

| Feature | volatile | synchronized |
|---|---|---|
| Visibility | ✓ | ✓ |
| Atomicity | ✗ | ✓ |
| Mutual exclusion | ✗ | ✓ |
| Performance | Fast (no lock) | Slower (lock acquisition) |
| Use case | Flags, single-writer | Compound operations |

Use `volatile` when:
- One thread writes, others only read
- The operation is a single read or write (not read-modify-write)
- You need a lightweight visibility guarantee

Use `synchronized` when:
- Multiple threads write
- Operations are compound (check-then-act, read-modify-write)
- You need mutual exclusion

## Common volatile Patterns

### Pattern 1: Shutdown Flag (Most Common)

```java
private volatile boolean shutdownRequested = false;

public void requestShutdown() { shutdownRequested = true; }

public void run() {
    while (!shutdownRequested) {
        doWork();
    }
}
```

### Pattern 2: Published Configuration

```java
// One thread updates config, many threads read it
private volatile Config currentConfig = Config.defaults();

// Writer thread (only one)
public void reloadConfig() {
    Config newConfig = loadFromDisk();  // Create new immutable config
    currentConfig = newConfig;          // Atomic reference assignment
}

// Reader threads (many)
public void processEvent(Event e) {
    Config config = currentConfig;  // Read once per event
    // Use config...
}
```

This works because:
- Reference assignment is atomic (writing a pointer is one operation)
- `volatile` ensures the new reference is visible to readers
- The Config object itself is immutable (no partial reads)

### Pattern 3: Completion Status

```java
public class AsyncTask {
    private volatile boolean completed = false;
    private volatile Throwable error = null;
    private Object result;  // Safe: only read after completed = true

    public void execute() {
        try {
            result = doExpensiveWork();
        } catch (Throwable t) {
            error = t;
        } finally {
            completed = true;  // Publish: all writes before this are visible
        }
    }

    public boolean isCompleted() { return completed; }
    public Object getResult() { return result; }  // Safe after isCompleted() returns true
}
```

The volatile write to `completed` establishes a happens-before relationship: all writes before `completed = true` (including `result = ...`) are visible to any thread that reads `completed == true`.

## The Double-Checked Locking Pattern (Revisited)

From Chapter 1's Singleton discussion:

```java
public class Singleton {
    private static volatile Singleton instance;  // Must be volatile!

    public static Singleton getInstance() {
        if (instance == null) {                    // First check (no lock)
            synchronized (Singleton.class) {
                if (instance == null) {            // Second check (with lock)
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

Without `volatile`, Thread B might see a non-null `instance` that's not fully constructed (constructor hasn't finished). `volatile` prevents this reordering.

## PulseMetrics: Graceful Shutdown

```java
public class PipelineManager {
    private final List<IngestionWorker> workers = new ArrayList<>();
    private volatile boolean systemRunning = true;

    public void start(int numWorkers) {
        for (int i = 0; i < numWorkers; i++) {
            IngestionWorker worker = new IngestionWorker(i, this::isRunning);
            workers.add(worker);
            new Thread(worker, "ingestion-" + i).start();
        }
    }

    public boolean isRunning() {
        return systemRunning;
    }

    public void shutdown() {
        System.out.println("Shutdown requested...");
        systemRunning = false;

        // Wait for workers to finish current event
        for (IngestionWorker w : workers) {
            w.awaitTermination(5, TimeUnit.SECONDS);
        }
        System.out.println("All workers stopped.");
    }
}

public class IngestionWorker implements Runnable {
    private final int id;
    private final BooleanSupplier runningCheck;
    private volatile boolean terminated = false;

    public IngestionWorker(int id, BooleanSupplier runningCheck) {
        this.id = id;
        this.runningCheck = runningCheck;
    }

    @Override
    public void run() {
        while (runningCheck.getAsBoolean()) {
            Event event = receiveEvent();
            if (event != null) {
                process(event);
            }
        }
        terminated = true;
        System.out.println("Worker " + id + " terminated");
    }

    public void awaitTermination(long timeout, TimeUnit unit) {
        long deadline = System.nanoTime() + unit.toNanos(timeout);
        while (!terminated && System.nanoTime() < deadline) {
            Thread.onSpinWait();  // Hint to CPU: we're spin-waiting
        }
    }
}
```

## When volatile Is NOT Enough

```java
// BROKEN: check-then-act is not atomic
private volatile boolean initialized = false;

public void initialize() {
    if (!initialized) {        // Thread A reads false
        // Thread B also reads false — both enter!
        doExpensiveInit();
        initialized = true;
    }
}
```

This needs `synchronized` (or `AtomicBoolean.compareAndSet`) because the check-then-act is a compound operation.

## What You Learned

- **volatile** — forces reads/writes through main memory (visibility)
- **Does NOT provide atomicity** — `count++` is still broken with volatile
- **Use for flags** — shutdown signals, completion status, config publishing
- **Happens-before** — volatile write → subsequent volatile read sees all prior writes
- **Cheaper than synchronized** — no lock acquisition, just memory barriers
- **Not enough for compound operations** — check-then-act needs synchronized or atomics

The shutdown flag works. But `synchronized` is too coarse for PulseMetrics' hot path — it locks the entire object. We need finer-grained control: explicit locks with `ReentrantLock`.

---

[← Chapter 2: Synchronization](chapter-02-synchronization.md) | [Chapter 4: Locks →](chapter-04-locks.md)

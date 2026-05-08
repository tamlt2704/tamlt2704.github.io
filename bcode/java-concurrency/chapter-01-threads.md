# Chapter 1: The First Thread

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Synchronization →](chapter-02-synchronization.md)

---

## The Problem

PulseMetrics' ingestion pipeline is single-threaded:

```java
public class Pipeline {
    public void run() {
        while (true) {
            Event event = receiveEvent();    // Blocks until event arrives
            aggregate(event);                 // CPU work: ~200μs
            updateDashboard();               // Network I/O: ~5ms
        }
    }
}
```

The problem: `updateDashboard()` takes 5ms (network round-trip). During those 5ms, no events are being received or aggregated. At 2 million events/second, that's 10,000 events backed up every time we update a dashboard.

Nadia: "Why is ingestion blocking on dashboard updates? Those are independent operations."

She's right. Receiving events and updating dashboards don't depend on each other. They should run concurrently.

## Creating a Thread

A thread is an independent path of execution within your program. Java gives you two ways to create one:

### Way 1: Extend Thread (don't do this)

```java
class DashboardUpdater extends Thread {
    @Override
    public void run() {
        System.out.println("Updating dashboard on: " + Thread.currentThread().getName());
        updateDashboard();
    }
}

// Usage
DashboardUpdater updater = new DashboardUpdater();
updater.start();  // Starts a new thread, calls run()
```

### Way 2: Implement Runnable (do this)

```java
Runnable dashboardTask = () -> {
    System.out.println("Updating on: " + Thread.currentThread().getName());
    updateDashboard();
};

Thread thread = new Thread(dashboardTask);
thread.start();
```

Why Runnable? Because Java has single inheritance. If you extend `Thread`, you can't extend anything else. `Runnable` is a functional interface — use a lambda.

## Thread Lifecycle

```
NEW → RUNNABLE → RUNNING → (BLOCKED/WAITING) → TERMINATED
 │        │                        │
 │        └── start() called       └── waiting for lock/IO
 └── Thread created but not started
```

```java
Thread t = new Thread(() -> doWork());  // NEW
t.start();                              // RUNNABLE (scheduled by OS)
// ... thread runs ...                  // RUNNING
// ... thread finishes run() ...        // TERMINATED

System.out.println(t.getState());       // TERMINATED
```

Key rule: **you cannot restart a terminated thread.** Once `run()` completes, that Thread object is done.

## The Fix: Separate Ingestion from Dashboard Updates

```java
public class Pipeline {
    public void run() {
        // Dashboard updates run on a separate thread
        Thread dashboardThread = new Thread(() -> {
            while (true) {
                try {
                    Thread.sleep(1000);  // Update every second
                    updateDashboard();
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }
        });
        dashboardThread.setDaemon(true);  // Dies when main thread exits
        dashboardThread.start();

        // Main thread: pure ingestion, no blocking on dashboard
        while (true) {
            Event event = receiveEvent();
            aggregate(event);
            // No updateDashboard() here — it's running separately
        }
    }
}
```

Now ingestion never blocks on dashboard updates. Two threads, two independent tasks.

## join() — Waiting for a Thread to Finish

Sometimes you need to wait for a thread to complete:

```java
public class BatchProcessor {
    public void processInParallel(List<Event> events) throws InterruptedException {
        int mid = events.size() / 2;

        Thread t1 = new Thread(() -> process(events.subList(0, mid)));
        Thread t2 = new Thread(() -> process(events.subList(mid, events.size())));

        t1.start();
        t2.start();

        // Wait for both to finish
        t1.join();  // Blocks until t1 completes
        t2.join();  // Blocks until t2 completes

        System.out.println("Both halves processed");
    }
}
```

`join()` blocks the calling thread until the target thread terminates. You can also pass a timeout: `t1.join(5000)` waits at most 5 seconds.

## Daemon vs Non-Daemon Threads

```java
Thread worker = new Thread(() -> infiniteLoop());
worker.setDaemon(true);   // JVM exits even if this thread is running
worker.start();
```

- **Non-daemon** (default): JVM waits for all non-daemon threads to finish before exiting
- **Daemon**: JVM kills daemon threads when all non-daemon threads are done

Use daemon threads for background tasks (monitoring, cleanup) that shouldn't prevent shutdown.

## Thread Naming (You'll Thank Yourself at 3 AM)

```java
Thread t = new Thread(task, "pulse-ingestion-1");
// or
t.setName("pulse-dashboard-updater");
```

When Omar sends you a thread dump at 3 AM, you'll see:
```
"pulse-ingestion-1" #12 prio=5 RUNNABLE
"pulse-dashboard-updater" #13 prio=5 TIMED_WAITING
```

Named threads make debugging possible. `Thread-0`, `Thread-1` tells you nothing.

## The Danger: Shared State

Here's where things get dangerous. Two threads accessing the same variable:

```java
public class EventCounter {
    private int count = 0;  // Shared between threads

    public void increment() {
        count++;  // NOT ATOMIC — read, add, write
    }

    public int getCount() {
        return count;
    }
}
```

```java
EventCounter counter = new EventCounter();

Thread t1 = new Thread(() -> {
    for (int i = 0; i < 1_000_000; i++) counter.increment();
});
Thread t2 = new Thread(() -> {
    for (int i = 0; i < 1_000_000; i++) counter.increment();
});

t1.start(); t2.start();
t1.join(); t2.join();

System.out.println(counter.getCount());
// Expected: 2,000,000
// Actual:   1,573,284 (or some other wrong number)
```

The count is wrong. Every time. This is a **race condition** — two threads reading and writing the same variable without synchronization. Chapter 2 fixes this.

## Why count++ Isn't Atomic

`count++` looks like one operation but is actually three:

```
1. READ count from memory → register (value: 5)
2. ADD 1 to register (value: 6)
3. WRITE register back to memory (count = 6)
```

If two threads interleave:
```
Thread A: READ count → 5
Thread B: READ count → 5      (same value!)
Thread A: ADD → 6
Thread B: ADD → 6             (same result!)
Thread A: WRITE → count = 6
Thread B: WRITE → count = 6   (overwrites A's write!)
```

Two increments, but count only went from 5 to 6. One increment was lost.

## PulseMetrics After Chapter 1

```java
public class PulseMetrics {
    public static void main(String[] args) throws InterruptedException {
        EventCounter counter = new EventCounter();  // BROKEN — we'll fix in Ch 2

        // Simulate 4 ingestion threads
        List<Thread> threads = new ArrayList<>();
        for (int i = 0; i < 4; i++) {
            Thread t = new Thread(() -> {
                for (int j = 0; j < 500_000; j++) {
                    counter.increment();
                }
            }, "ingestion-" + i);
            threads.add(t);
            t.start();
        }

        for (Thread t : threads) t.join();

        System.out.println("Expected: 2,000,000");
        System.out.println("Actual:   " + counter.getCount());
        // Actual will be less than 2,000,000 — race condition
    }
}
```

We've separated concerns into threads. But shared state is corrupted. That's the next chapter.

## What You Learned

- **Thread** — an independent path of execution
- **Runnable** — preferred over extending Thread (use lambdas)
- **start() vs run()** — start() creates a new thread; run() executes on current thread
- **join()** — wait for a thread to finish
- **Daemon threads** — don't prevent JVM shutdown
- **Name your threads** — essential for debugging
- **Shared mutable state is dangerous** — race conditions corrupt data

The pipeline no longer blocks on dashboard updates. But the event counter is wrong. We need synchronization.

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Synchronization →](chapter-02-synchronization.md)

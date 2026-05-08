# Chapter 0: Before You Start

[Chapter 1: The First Thread →](chapter-01-threads.md)

---

## The Story

You're a systems engineer at **PulseMetrics**, a real-time analytics platform. Companies send you events — page views, clicks, purchases — and you aggregate them into dashboards that update every second.

The numbers: 2 million events per second. 500 concurrent dashboard connections. 50ms latency budget from event ingestion to dashboard update.

The problem: the ingestion pipeline is single-threaded. It processes events one at a time. At 2 million events/second, each event gets 500 nanoseconds of processing time. A single slow event blocks everything behind it.

Your CTO, **Nadia**, sends a Slack message at 11 PM:

"Dashboard latency hit 30 seconds during the Black Friday spike. We lost three enterprise customers. The pipeline needs to be concurrent. You have two weeks."

You've written multi-threaded code before. A thread here, a synchronized block there. But 2 million events per second with 50ms latency? That's a different game. Race conditions corrupt data. Deadlocks freeze the system. Thread creation overhead kills throughput.

Over 14 chapters, you'll rebuild PulseMetrics' pipeline from single-threaded to a fully concurrent system using modern Java concurrency primitives — from raw threads to virtual threads.

## The Java Memory Model (The One Thing You Must Know)

Before writing any concurrent code, you need to understand one thing: **threads don't see each other's writes immediately.**

```java
// Thread A
running = true;
count = 42;

// Thread B (running concurrently)
System.out.println(running); // might print false
System.out.println(count);   // might print 0
```

This isn't a bug. It's the Java Memory Model (JMM). Each thread can cache variables in CPU registers or L1 cache. Without explicit synchronization, there's no guarantee that Thread B sees Thread A's writes.

The JMM defines **happens-before** relationships — guarantees about when one thread's writes become visible to another. Every synchronization mechanism in this course (synchronized, volatile, locks, atomics) establishes happens-before relationships.

You don't need to memorize the JMM spec. But you need to internalize this: **if two threads access the same variable and at least one writes, you need synchronization.** No exceptions. No "it works on my machine."

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Systems Engineer | Paranoid about race conditions (rightly so) |
| **Nadia** | CTO | "If it's not lock-free, explain why." |
| **Omar** | SRE | "Your thread leak crashed prod at 4 AM." |
| **Kai** | Data Engineer | Writes the aggregation logic you must parallelize |
| **The Intern** | Summer hire | Added `Thread.sleep(100)` to "fix" a race condition |

## Prerequisites

### Java 21+

Virtual threads (Chapter 12) require Java 21. Earlier chapters work on Java 17+, but we'll use 21 throughout for consistency.

```bash
java --version
# java 21.0.x or higher
```

### Tooling

- **JConsole** or **VisualVM** — for monitoring thread count, deadlock detection
- **jstack** — for thread dumps (built into JDK)
- **async-profiler** — for finding lock contention (optional but recommended)

### Running Examples

```bash
javac Chapter01.java
java Chapter01
```

Or use your IDE's run button. For concurrency, the debugger is less useful than you'd think — breakpoints change timing and hide race conditions. We'll rely on logging and assertions.

## The Concurrency Toolbox

Java's concurrency primitives, from low-level to high-level:

```
Low-level (you rarely use directly)
├── Thread, Runnable
├── synchronized, wait/notify
└── volatile

Mid-level (your daily tools)
├── ReentrantLock, ReadWriteLock
├── AtomicInteger, AtomicReference
├── BlockingQueue, ConcurrentHashMap
└── CountDownLatch, Semaphore

High-level (where you should start)
├── ExecutorService, ThreadPoolExecutor
├── CompletableFuture
├── ForkJoinPool
└── Virtual Threads (Project Loom)
```

We start at the bottom and work up. Not because you should use raw threads in production — but because understanding the low-level mechanics makes the high-level tools predictable.

## The Rules

1. **See the bug first** — every chapter starts with broken concurrent code
2. **Never trust "it works on my machine"** — race conditions are probabilistic
3. **Measure contention** — the fastest lock is the one you don't take
4. **Prefer higher-level abstractions** — but know what's underneath

Let's create our first thread.

---

[Chapter 1: The First Thread →](chapter-01-threads.md)

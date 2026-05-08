# Java Concurrency — From Threads to Virtual Threads

A narrative-driven course on Java concurrency. You're a systems engineer at **PulseMetrics**, a real-time analytics platform ingesting 2 million events per second. Single-threaded code can't keep up. Multi-threaded code keeps corrupting data. You'll fix both.

## Episodes

| # | Title | The Problem | What You Learn |
|---|---|---|---|
| 00 | [Before You Start](chapter-00-overview.md) | — | Setup, the Java Memory Model primer, the cast |
| 01 | [The First Thread](chapter-01-threads.md) | Ingestion blocks the API | Thread, Runnable, start/join, thread lifecycle |
| 02 | [Shared Counters](chapter-02-synchronization.md) | Event count is wrong under load | synchronized, monitors, happens-before |
| 03 | [Volatile Signals](chapter-03-volatile.md) | Shutdown flag not visible across threads | volatile, visibility vs atomicity |
| 04 | [Lock It Down](chapter-04-locks.md) | synchronized is too coarse | ReentrantLock, ReadWriteLock, tryLock, fairness |
| 05 | [Atomic Operations](chapter-05-atomics.md) | Lock contention kills throughput | AtomicInteger, CAS, LongAdder, AtomicReference |
| 06 | [Thread Pools](chapter-06-executors.md) | Creating 10K threads crashes the JVM | ExecutorService, thread pool sizing, rejection policies |
| 07 | [Futures and Promises](chapter-07-futures.md) | Need results from async work | Future, CompletableFuture, thenApply, exceptionally |
| 08 | [Producer-Consumer](chapter-08-blocking-queues.md) | Ingestion overwhelms processing | BlockingQueue, ArrayBlockingQueue, backpressure |
| 09 | [Concurrent Collections](chapter-09-concurrent-maps.md) | ConcurrentModificationException everywhere | ConcurrentHashMap, CopyOnWriteArrayList, segments |
| 10 | [Coordination](chapter-10-latches-barriers.md) | Phases must complete before next starts | CountDownLatch, CyclicBarrier, Phaser, Semaphore |
| 11 | [Fork/Join](chapter-11-forkjoin.md) | Recursive aggregation is too slow | ForkJoinPool, RecursiveTask, work-stealing |
| 12 | [Virtual Threads](chapter-12-virtual-threads.md) | 100K concurrent connections need 100K threads | Virtual threads (Project Loom), structured concurrency |
| 13 | [Deadlocks and Debugging](chapter-13-deadlocks.md) | System freezes at 3 AM | Deadlock detection, jstack, thread dumps, ordering |
| 14 | [Patterns in Production](chapter-14-patterns.md) | Putting it all together | Double-checked locking, thread-local, actor model |

## Prerequisites

- Java 21+ (for virtual threads)
- Any IDE or `javac` + terminal

## Philosophy

Every concurrency primitive is introduced because something broke in production. You'll see the race condition before you see the fix. The broken code comes first. The correct code follows.

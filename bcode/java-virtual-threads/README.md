# Java Virtual Threads — Concurrency Without the Pain

A narrative-driven course on Java's virtual threads (Project Loom). You're a backend engineer at a fintech company where thread pools are the bottleneck. Over 12 chapters, you'll migrate from thread-per-request to million-thread concurrency — one production incident at a time.

## Episodes

| # | Title | The Problem | What You Learn |
|---|---|---|---|
| 00 | [Before You Start](chapter-00-overview.md) | — | Setup, threading model, the cast |
| 01 | [The Thread Pool Wall](chapter-01-thread-pool-wall.md) | 200 threads, 10K requests queued | Platform threads, OS limits, thread cost |
| 02 | [Your First Virtual Thread](chapter-02-first-virtual-thread.md) | Need more concurrency without more RAM | Thread.ofVirtual(), startVirtualThread() |
| 03 | [Structured Concurrency](chapter-03-structured-concurrency.md) | Threads leak, errors get lost | StructuredTaskScope, ShutdownOnFailure |
| 04 | [Scoped Values](chapter-04-scoped-values.md) | ThreadLocal breaks with virtual threads | ScopedValue, immutable context |
| 05 | [I/O Bound Workloads](chapter-05-io-bound.md) | HTTP calls block platform threads | Virtual threads + blocking I/O, carrier threads |
| 06 | [Database Access](chapter-06-database.md) | Connection pool is the new bottleneck | JDBC + virtual threads, pool sizing |
| 07 | [Pinning](chapter-07-pinning.md) | synchronized blocks pin carrier threads | Pinning detection, ReentrantLock migration |
| 08 | [HTTP Servers](chapter-08-http-servers.md) | Tomcat thread pool limits throughput | Virtual thread executors, Spring Boot config |
| 09 | [Backpressure](chapter-09-backpressure.md) | Unlimited threads overwhelm downstream | Semaphores, bulkheads, rate limiting |
| 10 | [Debugging & Profiling](chapter-10-debugging.md) | "Where are my million threads?" | JFR, thread dumps, jcmd |
| 11 | [Migration Patterns](chapter-11-migration.md) | Legacy code uses ExecutorService everywhere | Drop-in replacement, gradual migration |
| 12 | [Production Readiness](chapter-12-production.md) | Virtual threads in prod: what could go wrong? | Monitoring, pitfalls, real-world patterns |

## Prerequisites

- Java 21+ (LTS with virtual threads GA)
- Gradle or Maven
- Basic understanding of Java threading

## Philosophy

Every concept is introduced because a thread pool hit a wall. No theory without a production bottleneck to solve first. The blocked thread comes first. The virtual thread follows.

# Chapter 0: Before You Start

[Chapter 1: The Thread Pool Wall →](chapter-01-thread-pool-wall.md)

---

## The Story

This is a series about Java virtual threads — but not the kind where you read "virtual threads are lightweight" and move on.

You're a backend engineer at **VaultPay**, a fintech company that processes payment transactions. The system handles card authorizations, fraud checks, balance updates, and settlement — all through a Java monolith running on Spring Boot. It works. Until it doesn't.

The architecture is simple: Tomcat receives HTTP requests, each request gets a platform thread, the thread calls downstream services (fraud API, bank API, ledger database), waits for responses, and returns. Thread-per-request. The model that's powered Java servers for 25 years.

The problem: VaultPay is growing. Black Friday last year, the system hit 10,000 concurrent requests. Tomcat's thread pool maxes out at 200 threads. The other 9,800 requests queued. Response times went from 50ms to 12 seconds. Transactions timed out. Merchants lost sales. The CEO lost sleep.

Your tech lead, **Nadia**, drops a post-mortem on your desk:

"We can't add more platform threads — each one costs 1MB of stack space. 200 threads = 200MB just for stacks. 10,000 threads = 10GB. That's our entire heap. We need a different model. Java 21 has virtual threads. Figure out if they actually work for us."

You nod. You've read the JEP. "Lightweight threads, millions of them, no code changes." How hard can it be?

Over the next 12 chapters, you'll migrate VaultPay from platform threads to virtual threads. Every change solves a real problem — handling more concurrent requests, eliminating thread pool bottlenecks, structuring concurrent operations safely. And every naive migration will break in a way that teaches you why virtual threads aren't just "faster threads."

The synchronized block will pin a carrier thread. The connection pool will become the new bottleneck. The ThreadLocal will leak memory across millions of virtual threads. The unbounded concurrency will DDoS your own database.

Each failure teaches you something about concurrent systems that no blog post could.

By the end, you'll have a production-ready system handling 100K concurrent requests on a single JVM — and you'll understand *when* virtual threads help, *when* they don't, and *what* changes when you adopt them.

## How to Read This

Every chapter is the same loop:

1. The system hits a concurrency limit
2. You identify the bottleneck
3. You learn the virtual thread concept that addresses it
4. You implement it, measure the improvement
5. You discover the next bottleneck

No concept shows up before you need it. You won't hear about pinning until a synchronized block tanks your throughput. You won't touch structured concurrency until a leaked thread causes a resource leak in production.

The bottleneck comes first. The solution follows.

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Backend Engineer | Knows Java threading. Skeptical of magic. |
| **Nadia** | Tech Lead | "Show me the benchmarks. Then show me the failure modes." |
| **Raj** | SRE | "Your thread dump has 500,000 entries. My tooling is crying." |
| **The Monolith** | VaultPay's codebase | 200K lines of Java. Lots of synchronized blocks. |
| **The Load Test** | k6 scripts | Merciless. Finds every bottleneck. |
| **The Intern** | Summer hire | "I set the thread pool to Integer.MAX_VALUE. Problem solved?" |

## The Roadmap

| Ch | The Problem | What You Learn |
|---|---|---|
| 1 | 200 threads can't handle 10K requests | Platform thread costs, OS scheduling limits |
| 2 | Need 10K+ concurrent operations | Virtual thread creation, lifecycle, scheduling |
| 3 | Threads leak, partial failures are silent | StructuredTaskScope, join policies |
| 4 | ThreadLocal costs 1MB × 1M threads | ScopedValue, immutable context propagation |
| 5 | Blocking I/O wastes platform threads | Virtual threads unmount on blocking, carrier threads |
| 6 | Database connection pool is now the bottleneck | JDBC with virtual threads, pool sizing strategy |
| 7 | synchronized pins carrier threads | Pinning detection, migration to ReentrantLock |
| 8 | Tomcat thread pool limits request handling | Virtual thread executor in Spring Boot |
| 9 | Unlimited concurrency overwhelms downstream | Semaphores, bulkheads, controlled parallelism |
| 10 | Can't see what million threads are doing | JFR events, thread dumps, diagnostic tools |
| 11 | Legacy code uses thread pools everywhere | Migration patterns, compatibility, gradual rollout |
| 12 | Ready for production? | Monitoring, known pitfalls, operational patterns |

## Prerequisites

Two things: Java 21 and a load testing tool.

### Java 21+

Virtual threads are GA (General Availability) in Java 21. Not preview. Not incubator. Production-ready.

```bash
java --version
# openjdk 21.0.x or higher
```

If you're on an older version:

```bash
# SDKMAN (recommended)
sdk install java 21.0.2-tem

# Or download from https://adoptium.net/
```

### Build Tool

Examples use Gradle with the Kotlin DSL, but Maven works too:

```kotlin
// build.gradle.kts
plugins {
    java
    id("org.springframework.boot") version "3.2.0"
}

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}
```

### Dependencies

```kotlin
dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-jdbc")
    implementation("org.postgresql:postgresql")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}
```

### Load Testing: k6

We'll use k6 to generate realistic load:

```bash
# macOS
brew install k6

# Linux
sudo apt install k6

# Windows
choco install k6
```

Quick check:

```bash
k6 version
```

### Quick Check

```java
public class VirtualThreadCheck {
    public static void main(String[] args) throws Exception {
        Thread vt = Thread.ofVirtual().name("hello").start(() -> {
            System.out.println("Hello from " + Thread.currentThread());
        });
        vt.join();
    }
}
```

```bash
javac VirtualThreadCheck.java && java VirtualThreadCheck
```

```
Hello from VirtualThread[#21,hello]/runnable@ForkJoinPool-1-worker-1
```

If you see `VirtualThread` in the output, you're ready.

## The Threading Model (The Only Theory Upfront)

Java has always had threads. What changed?

### Platform Threads (The Old Model)

```java
Thread t = new Thread(() -> doWork());
t.start();
```

A platform thread is a thin wrapper around an OS thread. The OS schedules it. The OS allocates its stack (typically 1MB). The OS limits how many you can have (usually a few thousand before things degrade).

**Cost per platform thread:**
- ~1MB stack memory
- ~1ms creation time
- OS context switch overhead
- Kernel scheduling overhead

At 200 concurrent requests, you use 200MB just for thread stacks. At 10,000, you need 10GB. That's why thread pools exist — to cap the damage.

### Virtual Threads (The New Model)

```java
Thread vt = Thread.ofVirtual().start(() -> doWork());
```

A virtual thread is a Java-managed thread that runs on top of a small pool of platform threads (called **carrier threads**). The JVM schedules it. The JVM allocates its stack (starts at ~1KB, grows as needed). The JVM can handle millions of them.

**Cost per virtual thread:**
- ~1KB initial stack (grows on demand)
- ~1μs creation time
- No OS context switch (JVM-managed)
- Mounted/unmounted from carrier threads

The key insight: when a virtual thread blocks (I/O, sleep, lock), it **unmounts** from its carrier thread. The carrier is free to run another virtual thread. When the I/O completes, the virtual thread remounts on any available carrier.

```
Platform Thread Model:
  Thread 1: [work][wait.........][work]  ← thread is BLOCKED, doing nothing
  Thread 2: [work][wait...][work]
  (200 threads, 9800 requests queued)

Virtual Thread Model:
  Carrier 1: [vt1-work][vt3-work][vt1-work][vt5-work]  ← always busy
  Carrier 2: [vt2-work][vt4-work][vt2-work][vt6-work]
  (8 carriers, 10000 virtual threads, no queue)
```

### What Doesn't Change

- `Thread` API is the same
- `synchronized`, `Lock`, `Semaphore` still work
- `ExecutorService` still works
- Your existing code still compiles and runs

### What Changes

- Thread creation is cheap → don't pool virtual threads
- Blocking is cheap → don't go async/reactive for I/O
- Thread count is unbounded → you need other backpressure mechanisms
- `ThreadLocal` is expensive at scale → use `ScopedValue`
- `synchronized` can pin → prefer `ReentrantLock`

That's the mental model. Let's see it break.

---

[Chapter 1: The Thread Pool Wall →](chapter-01-thread-pool-wall.md)

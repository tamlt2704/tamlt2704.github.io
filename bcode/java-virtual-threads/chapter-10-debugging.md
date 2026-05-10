# Chapter 10: Debugging & Profiling

[← Chapter 9: Backpressure](chapter-09-backpressure.md) | [Chapter 11: Migration Patterns →](chapter-11-migration.md)

---

## The Problem

Raj is staring at his monitoring dashboard: "We have 47,000 active threads. VisualVM crashed trying to render the thread list. The thread dump is 180MB. I can't find the 3 threads that are actually stuck."

With 200 platform threads, debugging was straightforward. You'd take a thread dump, scan for BLOCKED or WAITING states, find the culprit. With 47,000 virtual threads, the signal-to-noise ratio is catastrophic.

Traditional tooling wasn't built for millions of threads. You need new approaches.

## Thread Dumps with jcmd

The `jcmd` tool supports virtual threads in Java 21. It produces structured JSON output:

```bash
# Traditional thread dump (includes virtual threads)
jcmd <pid> Thread.dump_to_file -format=json threads.json

# Plain text format
jcmd <pid> Thread.dump_to_file threads.txt
```

The JSON format groups virtual threads by state:

```json
{
  "threadContainers": [
    {
      "container": "ForkJoinPool-1",
      "threads": [
        {
          "tid": "#48123",
          "name": "vaultpay-request-4812",
          "state": "WAITING",
          "stack": [
            "java.util.concurrent.locks.LockSupport.park",
            "com.zaxxer.hikari.pool.HikariPool.getConnection",
            "com.vaultpay.repository.TransactionRepo.findById"
          ]
        }
      ]
    }
  ]
}
```

Filter for stuck threads:

```bash
# Find threads waiting on database connections
jcmd <pid> Thread.dump_to_file -format=json /dev/stdout | \
  jq '.threadContainers[].threads[] | select(.stack[] | contains("HikariPool"))'
```

## JDK Flight Recorder (JFR) Events

JFR is the primary profiling tool for virtual threads. It captures events without the overhead of sampling every thread:

```bash
# Start recording
jcmd <pid> JFR.start name=vt-profile duration=60s filename=recording.jfr

# Or via JVM flags at startup
java -XX:StartFlightRecording=duration=60s,filename=recording.jfr \
     -jar vaultpay.jar
```

Key JFR events for virtual threads:

| Event | What It Tells You |
|---|---|
| `jdk.VirtualThreadStart` | Virtual thread created |
| `jdk.VirtualThreadEnd` | Virtual thread terminated |
| `jdk.VirtualThreadPinned` | Virtual thread pinned to carrier |
| `jdk.VirtualThreadSubmitFailed` | Scheduler rejected a task |

## Detecting Pinning with JFR

```bash
# Record with pinning events enabled
java -XX:StartFlightRecording=duration=30s,filename=pinning.jfr \
     -Djdk.tracePinnedThreads=full \
     -jar vaultpay.jar
```

Analyze with `jfr` CLI:

```bash
# List pinning events
jfr print --events jdk.VirtualThreadPinned pinning.jfr
```

Output:
```
jdk.VirtualThreadPinned {
  startTime = 2024-01-15T10:23:45.123
  duration = 52.3 ms
  eventThread = "vaultpay-request-1234" (virtual)
  stackTrace = [
    com.vaultpay.legacy.PaymentGateway.submit(PaymentGateway.java:87)
    -- monitors: 1
  ]
}
```

52ms pinned. That's a carrier thread stuck for 52ms. With 8 carriers, that's 12.5% of your scheduling capacity gone.

## Programmatic Thread Monitoring

Build a diagnostic endpoint for production:

```java
@RestController
@RequestMapping("/debug")
public class ThreadDiagnosticController {

    @GetMapping("/threads/summary")
    public Map<String, Object> threadSummary() {
        Set<Thread> allThreads = Thread.getAllStackTraces().keySet();

        long virtualCount = allThreads.stream()
            .filter(Thread::isVirtual).count();
        long platformCount = allThreads.stream()
            .filter(t -> !t.isVirtual()).count();

        Map<Thread.State, Long> virtualByState = allThreads.stream()
            .filter(Thread::isVirtual)
            .collect(Collectors.groupingBy(Thread::getState, Collectors.counting()));

        return Map.of(
            "virtualThreads", virtualCount,
            "platformThreads", platformCount,
            "virtualByState", virtualByState,
            "timestamp", Instant.now()
        );
    }

    @GetMapping("/threads/blocked")
    public List<Map<String, Object>> blockedThreads() {
        return Thread.getAllStackTraces().entrySet().stream()
            .filter(e -> e.getKey().isVirtual())
            .filter(e -> e.getKey().getState() == Thread.State.BLOCKED)
            .limit(50) // don't dump thousands
            .map(e -> Map.<String, Object>of(
                "name", e.getKey().getName(),
                "state", e.getKey().getState().name(),
                "stack", Arrays.stream(e.getValue())
                    .limit(10)
                    .map(StackTraceElement::toString)
                    .toList()
            ))
            .toList();
    }
}
```

## Structured Logging for Virtual Threads

Add thread context to your logs:

```java
@Component
public class VirtualThreadMDCFilter implements Filter {

    @Override
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
            throws IOException, ServletException {
        Thread current = Thread.currentThread();
        MDC.put("threadType", current.isVirtual() ? "virtual" : "platform");
        MDC.put("threadName", current.getName());
        try {
            chain.doFilter(req, res);
        } finally {
            MDC.clear();
        }
    }
}
```

```xml
<!-- logback.xml -->
<pattern>%d{HH:mm:ss} [%X{threadType}:%X{threadName}] %-5level %logger - %msg%n</pattern>
```

Output:
```
10:23:45 [virtual:vaultpay-request-4812] INFO  PaymentService - Processing payment txn-abc
10:23:45 [virtual:vaultpay-request-4813] INFO  PaymentService - Processing payment txn-def
```

## Metrics for Virtual Threads

Export thread metrics to your monitoring system:

```java
@Component
public class VirtualThreadMetrics {

    private final MeterRegistry registry;

    @Scheduled(fixedRate = 5000)
    public void recordMetrics() {
        Set<Thread> threads = Thread.getAllStackTraces().keySet();

        long virtual = threads.stream().filter(Thread::isVirtual).count();
        long blocked = threads.stream()
            .filter(Thread::isVirtual)
            .filter(t -> t.getState() == Thread.State.BLOCKED)
            .count();

        registry.gauge("vt.active", virtual);
        registry.gauge("vt.blocked", blocked);
    }
}
```

Alert when blocked virtual threads exceed a threshold — that usually means pinning or resource starvation.

## Common Debugging Scenarios

### "Throughput dropped suddenly"
1. Check `vt.blocked` metric — are threads stuck?
2. Take a thread dump: `jcmd <pid> Thread.dump_to_file -format=json dump.json`
3. Look for common stack frames in BLOCKED/WAITING threads
4. Common culprits: pinning, connection pool exhaustion, downstream timeout

### "Memory is growing"
1. Check virtual thread count — are threads accumulating?
2. Look for threads that never complete (leaked from unstructured concurrency)
3. Check ThreadLocal usage — each virtual thread holds its own copy
4. Use `jmap -histo` to find what's consuming heap

### "Carrier threads are all busy"
1. Check for pinning: `-Djdk.tracePinnedThreads=full`
2. Check for CPU-bound work on virtual threads (no yield points)
3. Verify carrier pool size: `-Djdk.virtualThreadScheduler.parallelism`

## What You Learned

- **jcmd Thread.dump_to_file** — JSON thread dumps that handle millions of threads
- **JFR events** — `VirtualThreadPinned`, `VirtualThreadStart/End` for profiling
- **Pinning detection** — JFR + `-Djdk.tracePinnedThreads` identifies stuck carriers
- **Diagnostic endpoints** — programmatic thread inspection for production
- **Structured logging** — MDC with thread type for filtering logs
- **Metrics** — gauge virtual thread count and blocked state for alerting
- **Debugging patterns** — systematic approach to throughput drops and memory growth

You can see what's happening now. But VaultPay still has 200K lines of legacy code using `ExecutorService`, `CompletableFuture`, and thread pools everywhere. You can't rewrite it all at once. You need a migration strategy that lets you adopt virtual threads incrementally.

---

[← Chapter 9: Backpressure](chapter-09-backpressure.md) | [Chapter 11: Migration Patterns →](chapter-11-migration.md)

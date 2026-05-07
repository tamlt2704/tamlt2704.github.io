# Chapter 8: Process 10,000 Messages Without Falling Over

[← Chapter 7: Retry and Dead-Letter](chapter-07-error-handling.md) | [Chapter 9: Don't Lose Messages on Restart →](chapter-09-message-store.md)

---

## The Disaster

It's Black Friday. The lab system sends 10,000 results in one hour instead of the usual 200. Your flow processes them sequentially — one at a time, on a single thread. Each message takes ~200ms (transform + SFTP upload). Math:

```
10,000 messages × 200ms = 2,000 seconds = 33 minutes
```

But they keep arriving. By the time you finish the first batch, another 5,000 have piled up. The queue grows. Memory fills. The app crashes with `OutOfMemoryError`. 3,000 messages are lost.

Miriam:

> "We need concurrency. Process multiple messages in parallel. But don't let it run away — if we open 1,000 SFTP connections, PharmaCo will ban us."

---

## DirectChannel: Single-Threaded by Default

The default `DirectChannel` is synchronous. The sender's thread processes the message all the way through the flow. One message at a time.

```
  [Poller Thread] → channel → transform → route → SFTP upload → done
                                                                  │
                                                                  ▼
                                                          (only THEN polls next message)
```

For 200 messages/hour, this is fine. For 10,000, it's a bottleneck.

---

## QueueChannel + TaskExecutor: Parallel Processing

```java
// src/main/java/com/medibridge/flows/ConcurrentLabFlow.java
package com.medibridge.flows;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.integration.channel.QueueChannel;
import org.springframework.integration.dsl.IntegrationFlow;
import org.springframework.integration.dsl.Pollers;
import org.springframework.integration.scheduling.PollerMetadata;
import org.springframework.messaging.MessageChannel;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;

import java.util.concurrent.Executor;

@Configuration
public class ConcurrentLabFlow {

    @Bean
    public MessageChannel processingQueue() {
        return new QueueChannel(1000);  // Buffer up to 1000 messages
    }

    @Bean
    public Executor labProcessingExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(5);
        executor.setMaxPoolSize(10);
        executor.setQueueCapacity(500);
        executor.setThreadNamePrefix("lab-proc-");
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.initialize();
        return executor;
    }

    @Bean
    public IntegrationFlow concurrentLabFlow(Hl7ToJsonTransformer transformer) {
        return IntegrationFlow
            .from(Files.inboundAdapter(new File("input/labs"))
                    .autoCreateDirectory(true)
                    .patternFilter("*.hl7"),
                e -> e.poller(Pollers.fixedDelay(1000)
                    .maxMessagesPerPoll(50)))  // Grab up to 50 files per poll
            .channel("processingQueue")        // Decouple: poller drops messages here
            .get();
    }

    @Bean
    public IntegrationFlow labProcessingFlow(Hl7ToJsonTransformer transformer) {
        return IntegrationFlow.from("processingQueue")
            // Poll the queue with multiple threads
            .bridge(e -> e.poller(Pollers.fixedDelay(100)
                .taskExecutor(labProcessingExecutor())
                .maxMessagesPerPoll(10)))
            .transform(Files.toStringTransformer())
            .transform(transformer, "transform")
            .handle(Sftp.outboundAdapter(pharmacySftpFactory)
                .remoteDirectory("/inbound/results"))
            .get();
    }
}
```

### What Changed

```
  BEFORE (single-threaded):
  [Poller] → transform → SFTP → (wait) → [Poller] → transform → SFTP → ...

  AFTER (concurrent):
  [Poller] → QueueChannel (buffer)
                    │
                    ├── Thread-1: transform → SFTP
                    ├── Thread-2: transform → SFTP
                    ├── Thread-3: transform → SFTP
                    ├── Thread-4: transform → SFTP
                    └── Thread-5: transform → SFTP
```

5 threads processing in parallel. Throughput: 5× faster. 10,000 messages in ~7 minutes instead of 33.

---

## ExecutorChannel: Simpler Concurrency

If you just want a channel that dispatches to a thread pool (without the queue buffer):

```java
@Bean
public MessageChannel concurrentChannel() {
    return new ExecutorChannel(labProcessingExecutor());
}

@Bean
public IntegrationFlow simpleParallelFlow(Hl7ToJsonTransformer transformer) {
    return IntegrationFlow.from("rawLabChannel")
        .channel("concurrentChannel")  // Messages dispatched to thread pool
        .transform(transformer, "transform")
        .handle(/* ... */)
        .get();
}
```

`ExecutorChannel` = `DirectChannel` + thread pool. Each message is handed to a thread from the pool. No buffering — if all threads are busy, the sender blocks (or the rejection policy kicks in).

---

## Backpressure: Don't Overwhelm Downstream

PharmaCo's SFTP allows max 5 concurrent connections. If you open 10, they ban your IP.

### Semaphore-Based Throttling

```java
@Bean
public IntegrationFlow throttledOutboundFlow() {
    return IntegrationFlow.from("processedLabChannel")
        .handle(Sftp.outboundAdapter(pharmacySftpFactory)
                .remoteDirectory("/inbound/results"),
            e -> e.advice(concurrencyAdvice()))
        .get();
}

// Limit concurrent executions of this endpoint
@Bean
public ConcurrencyThrottleAdvice concurrencyAdvice() {
    return new ConcurrencyThrottleAdvice(5);  // Max 5 concurrent
}
```

Or use a `Semaphore` directly:

```java
private final Semaphore sftpSemaphore = new Semaphore(5);

@ServiceActivator(inputChannel = "sftpUploadChannel")
public void uploadWithThrottle(Message<?> message) throws Exception {
    sftpSemaphore.acquire();
    try {
        sftpTemplate.send(message);
    } finally {
        sftpSemaphore.release();
    }
}
```

### Rate Limiting with Delayer

```java
@Bean
public IntegrationFlow rateLimitedFlow() {
    return IntegrationFlow.from("highVolumeChannel")
        .delay("delayer", d -> d
            .defaultDelay(100)  // 100ms between messages = max 10/second
            .messageStore(messageStore()))
        .handle(/* ... */)
        .get();
}
```

---

## Thread Safety: What Can Go Wrong

```java
// ❌ WRONG: shared mutable state in a handler
@Component
public class UnsafeCounter {
    private int count = 0;  // Shared across threads!

    @ServiceActivator(inputChannel = "countChannel")
    public void handle(Message<?> msg) {
        count++;  // Race condition!
        System.out.println("Processed: " + count);
    }
}

// ✓ RIGHT: use AtomicInteger or don't share state
@Component
public class SafeCounter {
    private final AtomicInteger count = new AtomicInteger(0);

    @ServiceActivator(inputChannel = "countChannel")
    public void handle(Message<?> msg) {
        int current = count.incrementAndGet();
        System.out.println("Processed: " + current);
    }
}
```

**Rules for concurrent flows:**
1. Messages are immutable — safe to share across threads
2. Handlers should be stateless (or use thread-safe state)
3. Don't assume message ordering — parallel processing means messages arrive out of order
4. If ordering matters, use a single-threaded channel for that segment

---

## Monitoring the Queue

```java
@Bean
public IntegrationFlow queueMonitorFlow() {
    return IntegrationFlow
        .from(() -> {
            QueueChannel queue = (QueueChannel) applicationContext.getBean("processingQueue");
            return MessageBuilder.withPayload(Map.of(
                "queueSize", queue.getQueueSize(),
                "remainingCapacity", queue.getRemainingCapacity()
            )).build();
        }, e -> e.poller(Pollers.fixedRate(10_000)))  // Check every 10s
        .handle((payload, headers) -> {
            Map<String, Integer> stats = (Map<String, Integer>) payload;
            if (stats.get("queueSize") > 800) {
                System.err.println("⚠️ Queue nearly full: " + stats.get("queueSize") + "/1000");
            }
            return null;
        })
        .get();
}
```

---

## The Configuration Summary

| Parameter | Value | Why |
|---|---|---|
| Queue capacity | 1000 | Buffer for burst traffic |
| Core pool size | 5 | Normal processing threads |
| Max pool size | 10 | Burst capacity |
| Max messages per poll | 50 | Don't starve other pollers |
| SFTP concurrency limit | 5 | PharmaCo's connection limit |
| Rejection policy | CallerRunsPolicy | Slow down producer instead of dropping messages |

---

## Report to Miriam

> **Concurrency implemented:**
> - QueueChannel buffers up to 1000 messages during bursts
> - 5-10 processing threads handle messages in parallel
> - SFTP uploads throttled to 5 concurrent connections (PharmaCo's limit)
> - CallerRunsPolicy prevents message loss when queue is full
> - Queue monitoring alerts when buffer exceeds 80% capacity
>
> Black Friday math: 10,000 messages × 200ms ÷ 5 threads = ~7 minutes. No crash. No OOM.

Miriam: "But what happens if the server restarts mid-processing? Those 1000 messages in the QueueChannel — they're in memory. They'll be lost."

---

## What You Learned

- **DirectChannel** = synchronous, single-threaded (default)
- **QueueChannel** = asynchronous buffer — decouples producer from consumer
- **ExecutorChannel** = DirectChannel + thread pool — parallel dispatch without buffering
- **TaskExecutor** controls thread pool size, queue capacity, rejection policy
- **`maxMessagesPerPoll`** limits how many messages a poller grabs per cycle
- **Backpressure** — semaphores, rate limiters, and `CallerRunsPolicy` prevent overwhelming downstream
- **Thread safety** — messages are immutable (safe), handlers must be stateless or use atomic operations
- **Ordering is not guaranteed** in concurrent flows — if order matters, use single-threaded segments
- Monitor queue depth — alert before it fills up, not after

---

[Next: Chapter 9 — "Don't Lose Messages on Restart" →](chapter-09-message-store.md)

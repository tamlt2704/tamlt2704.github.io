# Chapter 4: Spring Integration Flows

[← Chapter 3: Threading](/blog/spring-job-engine/chapter-03-threading) | [Chapter 5: Priority & Pause →](/blog/spring-job-engine/chapter-05-priority-pause)

---

## The Story

You have threads running jobs. But the flow is hardcoded — submit, execute, done. The PM wants: "Route different job types to different handlers. Add validation. Send notifications when done." You need a pipeline.

Spring Integration gives you message-driven architecture with channels, routers, transformers, and service activators — all configurable.

## The Big Picture

<Mermaid chart={`graph TD
  IC[Input Channel] --> V[Validator]
  V --> R[Priority Router]
  R -->|CRITICAL| HC[High Channel]
  R -->|MEDIUM| MC[Medium Channel]
  R -->|LOW| LC[Low Channel]
  HC --> E[Job Executor]
  MC --> E
  LC --> E
  E --> OC[Output Channel]
  OC --> K[Kafka]
  OC --> A[Audit Log]
`} />

## Step 1: Core Concepts

| Concept           | Analogy           | Purpose                              |
| ----------------- | ----------------- | ------------------------------------ |
| Message           | A letter          | Wraps the job payload + headers      |
| Channel           | A pipe            | Connects components                  |
| Gateway           | A mailbox         | Entry point from your code           |
| Router            | A sorting machine | Sends messages to different channels |
| Transformer       | A translator      | Converts message format              |
| Service Activator | A worker          | Does the actual work                 |
| Filter            | A bouncer         | Rejects invalid messages             |

### Channel Types

| Channel                     | Behavior                                                          | Use Case                                                 |
| --------------------------- | ----------------------------------------------------------------- | -------------------------------------------------------- |
| **DirectChannel**           | Synchronous, single subscriber. Sender's thread runs the handler. | Default. Fast, no buffering.                             |
| **QueueChannel**            | Asynchronous, buffered. Messages sit in a queue until polled.     | Decoupling producer from consumer, rate limiting.        |
| **PublishSubscribeChannel** | Broadcasts to all subscribers.                                    | Fan-out: send job events to both audit and notification. |
| **PriorityChannel**         | QueueChannel that orders messages by priority.                    | Critical jobs processed before low-priority ones.        |
| **ExecutorChannel**         | Like DirectChannel but dispatches to a thread pool.               | Non-blocking send, parallel consumers.                   |
| **RendezvousChannel**       | Zero-capacity queue — sender blocks until receiver picks up.      | Tight handoff, request-reply patterns.                   |

### Gateway

A **gateway** is the bridge between your regular Java code and the messaging world. You define an interface, Spring generates the implementation that:

1. Wraps your method argument into a `Message`
2. Sends it to the specified channel
3. Optionally waits for a reply (request-reply pattern)

Your code never touches `Message`, `Channel`, or any Spring Integration API directly — it just calls a method.

### Message Structure

A `Message<T>` has two parts:

- **Payload** — the actual data (e.g., a `Job` object)
- **Headers** — metadata (timestamps, correlation IDs, routing hints, custom values)

Headers travel with the message through the entire flow. Components can read, add, or modify them without touching the payload.

### Service Activator vs Handler

- **Service Activator** — calls a method on a Spring bean by name (e.g., `.handle("jobExecutor", "execute")`). Spring resolves the bean and invokes the method with the message payload.
- **Lambda handler** — inline logic (e.g., `.handle(m -> ...)`). Quick and anonymous, but harder to test in isolation.

### Error Channel

Every Spring Integration application has a global `errorChannel`. When an exception occurs in any async flow, it's wrapped in a `MessagingException` (containing the failed message + cause) and routed there automatically. You subscribe to it to handle failures centrally.

### Poller

Channels like `QueueChannel` don't push messages — they must be **polled**. A poller defines:

- **fixedDelay / fixedRate** — how often to check for messages
- **maxMessagesPerPoll** — how many to grab per cycle
- **taskExecutor** — which thread pool runs the polling

Without a poller, messages in a `QueueChannel` sit there forever.

## Step 2: Define the Integration Flow

```java
@Configuration
@RequiredArgsConstructor
public class JobIntegrationFlow {

    private final JobService jobService;
    private final AuditService auditService;  // defined in Chapter 7 — use a no-op stub for now

    @Bean
    public IntegrationFlow jobSubmissionFlow() {
        return IntegrationFlow
            // 1. Entry point: messages arrive on this channel (from JobController or gateway)
            .from("jobInputChannel")
            // 2. Filter: reject jobs with no params → sends rejects to "invalidJobChannel"
            .filter(Job.class, job -> job.getParams() != null,
                f -> f.discardChannel("invalidJobChannel"))
            // 3. Enrich: stamp the message header with submission time (metadata, not on entity)
            .enrichHeaders(h -> h.header("submittedAt", Instant.now()))
            // 4. Route: inspect priority and send to the appropriate channel
            //    CRITICAL → immediate execution, HIGH → priority lane, others → normal queue
            .route(Job.class, job -> job.getPriority().name(),
                r -> r
                    .channelMapping("CRITICAL", "criticalJobChannel")
                    .channelMapping("HIGH", "highPriorityChannel")
                    .defaultOutputChannel("normalJobChannel"))
            .get();
    }

    @Bean
    public IntegrationFlow criticalJobFlow() {
        return IntegrationFlow
            .from("criticalJobChannel")
            .handle("jobExecutor", "execute")
            .channel("jobCompletionChannel")
            .get();
    }

    @Bean
    public IntegrationFlow normalJobFlow() {
        return IntegrationFlow
            .from("normalJobChannel")
            .handle("jobExecutor", "execute")
            .channel("jobCompletionChannel")
            .get();
    }

    @Bean
    public IntegrationFlow completionFlow() {
        return IntegrationFlow
            .from("jobCompletionChannel")
            .handle(message -> {
                Job job = (Job) message.getPayload();
                auditService.log(job.getId(), "COMPLETED", "system", null);
            })
            .get();
    }
}
```

## Step 3: The Gateway (Entry Point)

```java
@MessagingGateway
public interface JobGateway {

    @Gateway(requestChannel = "jobInputChannel")
    void submit(Job job);
}
```

**What happens when `submit(job)` is called:**

1. Spring's generated proxy wraps the `Job` into a `Message<Job>` (with auto-generated id + timestamp headers)
2. The message is sent to `jobInputChannel`
3. Since `jobInputChannel` is a `DirectChannel` (default), the call is **synchronous** — the caller's thread executes the entire flow
4. The flow runs: filter → enrich headers → route to priority channel
5. `submit()` returns only after the message reaches a `QueueChannel` boundary or the flow completes

> If you want `submit()` to be fire-and-forget (non-blocking), change `jobInputChannel` to an `ExecutorChannel`. The caller returns immediately and a pool thread handles the flow.

Now your `JobController` just calls the gateway to enter the flow:

```java
// JobRequest.java
public record JobRequest(String type, JobPriority priority, String params) {}
```

```java
// In JobController.java
@RestController
@RequiredArgsConstructor
public class JobController {

    private final JobService jobService;
    private final JobGateway jobGateway;

    @PostMapping("/api/jobs")
    public Job submitJob(@RequestBody JobRequest request) {
        Job job = jobService.create(request);
        jobGateway.submit(job);  // enters the integration flow
        return job;
    }
}
```

## Step 4: Priority Channels with Capacity

```java
@Bean
public PriorityChannel criticalJobChannel() {
    return new PriorityChannel(10,
        Comparator.comparing(m -> ((Job) m.getPayload()).getSubmittedAt()));
}
```

Priority channels sort messages. Queue channels buffer them.

## Step 5: Error Handling

Spring Integration has a built-in `errorChannel` — you don't wire it manually. Any unhandled exception in **any** flow is automatically wrapped in a `MessagingException` and routed there. This `@Bean` subscribes to it:

```java
@Bean
public IntegrationFlow errorFlow() {
    return IntegrationFlow
        .from("errorChannel")  // Spring Integration's global error channel
        .handle(message -> {
            MessagingException ex = (MessagingException) message.getPayload();
            Job job = (Job) ex.getFailedMessage().getPayload();
            jobService.transition(job.getId(), JobStatus.FAILED);
            auditService.log(job.getId(), "FAILED", "system", ex.getCause().getMessage());
        })
        .get();
}
```

Any unhandled exception in the flow lands in `errorChannel`. We catch it, mark the job as failed, and log it.

> **Note:** `AuditService` is fully built in [Chapter 7](/blog/spring-job-engine/chapter-07-audit). For now, create a minimal stub:

```java
@Service
public class AuditService {
    public void log(String jobId, String action, String performedBy, String details) {
        // Chapter 7 will persist this to the database
    }
}
```

## Step 6: Polling Consumer (Thread Pool Integration)

For polling to work, the channel must be a `QueueChannel` (pollable). Define it:

```java
@Bean
public QueueChannel normalJobChannel() {
    return new QueueChannel(100);
}
```

Then the polling flow:

```java
@Bean
public IntegrationFlow pollingFlow(
        @Qualifier("jobExecutor") ThreadPoolTaskExecutor platformExecutor,
        @Qualifier("virtualExecutor") ExecutorService virtualExecutor,
        JobExecutor jobExecutor) {
    return IntegrationFlow
        .from(normalJobChannel())
        // Route by job type, then each branch gets its own mini-flow (subflow)
        // A subflow is an inline flow definition — no need for a separate @Bean
        .route(Job.class, job -> job.getType().endsWith("_IO") ? "io" : "cpu",
            r -> r
                // Subflow for I/O-bound jobs: dispatched on virtual threads
                .subFlowMapping("io", sf -> sf
                    .handle(m -> virtualExecutor.submit(() ->
                        jobExecutor.execute((Job) m.getPayload()))))
                // Subflow for CPU-bound jobs: polled from queue, run on platform thread pool
                .subFlowMapping("cpu", sf -> sf
                    .handle("jobExecutor", "execute",
                        e -> e.poller(Pollers.fixedDelay(500)
                            .taskExecutor(platformExecutor)
                            .maxMessagesPerPoll(5)))))
        .get();
}
```

This polls the queue every 500ms, picks up to 5 messages, and runs them on the thread pool. Spring Integration manages the threading for you.

## Why Spring Integration?

Without it:

```java
// Spaghetti
if (job.getPriority() == HIGH) { ... }
if (job.getType().equals("EXPORT")) { ... }
try { execute(job); } catch { ... }
notify(job);
audit(job);
```

With it:

```java
// Declarative pipeline
.filter(...)
.route(...)
.handle(...)
.channel(...)
```

Each concern is a separate, testable component. Add a new step? Insert it in the flow. Remove one? Delete the line.

## What We Have

- Message-driven job pipeline
- Priority routing (critical jobs get dedicated channel)
- Validation filter (rejects bad jobs)
- Error handling flow
- Completion notifications
- Thread pool integration via pollers

## Next

We'll add the ability to pause, resume, and cancel running jobs — with priority reordering.

[Chapter 5: Priority, Pause & Resume →](/blog/spring-job-engine/chapter-05-priority-pause)

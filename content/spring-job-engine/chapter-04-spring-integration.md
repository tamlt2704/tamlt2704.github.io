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

## Step 2: Define the Integration Flow

```java
@Configuration
public class JobIntegrationFlow {

    @Bean
    public IntegrationFlow jobSubmissionFlow() {
        return IntegrationFlow
            .from("jobInputChannel")
            .filter(Job.class, job -> job.getParams() != null,
                f -> f.discardChannel("invalidJobChannel"))
            .enrichHeaders(h -> h.header("submittedAt", Instant.now()))
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
            .handle("jobExecutor", "executeCritical")
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
            .handle("auditService", "logCompletion")
            .handle("kafkaProducer", "publishEvent")
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

Now your controller just calls:

```java
@PostMapping("/api/jobs")
public Job submitJob(@RequestBody JobRequest request) {
    Job job = jobService.create(request);
    jobGateway.submit(job);  // enters the integration flow
    return job;
}
```

## Step 4: Priority Channels with Capacity

```java
@Bean
public PriorityChannel criticalJobChannel() {
    return new PriorityChannel(10,
        Comparator.comparing(m -> ((Job) m.getPayload()).getSubmittedAt()));
}

@Bean
public QueueChannel normalJobChannel() {
    return new QueueChannel(100);  // buffered queue
}
```

Priority channels sort messages. Queue channels buffer them.

## Step 5: Error Handling

```java
@Bean
public IntegrationFlow errorFlow() {
    return IntegrationFlow
        .from("errorChannel")  // Spring Integration's global error channel
        .handle(message -> {
            MessagingException ex = (MessagingException) message.getPayload();
            Job job = (Job) ex.getFailedMessage().getPayload();
            jobService.transition(job.getId(), JobStatus.FAILED);
            auditService.log(job.getId(), "FAILED", ex.getCause().getMessage());
        })
        .get();
}
```

Any unhandled exception in the flow lands in `errorChannel`. We catch it, mark the job as failed, and log it.

## Step 6: Polling Consumer (Thread Pool Integration)

```java
@Bean
public IntegrationFlow pollingFlow() {
    return IntegrationFlow
        .from("normalJobChannel",
            c -> c.poller(Pollers.fixedDelay(500)
                .taskExecutor(jobExecutor())
                .maxMessagesPerPoll(5)))
        .handle("jobExecutor", "execute")
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

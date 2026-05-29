# Chapter 9: Kafka Event Streaming

[← Chapter 8: Redis](/blog/spring-job-engine/chapter-08-redis) | [Chapter 10: Final →](/blog/spring-job-engine/chapter-10-final)

---

## The Story

The job engine works on one server. But the company is growing — you need multiple instances processing jobs. And other services want to react to job events: the notification service sends emails, the dashboard updates in real-time, the billing service tracks usage.

Kafka decouples everything.

## The Architecture

<Mermaid chart={`graph TD
  E1[Job Engine 1] --> K[Kafka Cluster]
  E2[Job Engine 2] --> K
  E3[Job Engine 3] --> K
  K -->|job.submitted| K
  K -->|job.status-changed| K
  K -->|job.completed| K
  K --> N[Notification Service]
  K --> D[Dashboard - WebSocket]
`} />

## Step 1: Define Events

```java
// event/JobEvent.java
public record JobEvent(
    String jobId,
    String type,        // SUBMITTED, STARTED, COMPLETED, FAILED, PAUSED
    String user,
    JobPriority priority,
    Instant timestamp,
    Map<String, Object> metadata
) {}
```

## Step 2: Kafka Producer

```java
// event/JobEventPublisher.java
@Service
public class JobEventPublisher {

    private final KafkaTemplate<String, JobEvent> kafka;

    public void publish(Job job, String eventType) {
        JobEvent event = new JobEvent(
            job.getId(),
            eventType,
            job.getSubmittedBy(),
            job.getPriority(),
            Instant.now(),
            Map.of("progress", job.getProgress())
        );

        kafka.send("job.status-changed", job.getId(), event);
    }

    public void publishCompletion(Job job) {
        kafka.send("job.completed", job.getId(), new JobEvent(
            job.getId(), "COMPLETED", job.getSubmittedBy(),
            job.getPriority(), Instant.now(),
            Map.of("result", job.getResult(), "duration",
                Duration.between(job.getStartedAt(), job.getCompletedAt()).toMillis())
        ));
    }
}
```

The key is `job.getId()` — ensures all events for the same job go to the same partition (ordering guaranteed).

## Step 3: Kafka Consumer (Notification Service)

```java
// event/NotificationConsumer.java
@Component
public class NotificationConsumer {

    // EmailService — implement with JavaMailSender or a third-party provider
    private final EmailService emailService;

    @KafkaListener(topics = "job.completed", groupId = "notification-service")
    public void onJobCompleted(JobEvent event) {
        emailService.send(
            event.user(),
            "Job Complete: " + event.jobId(),
            "Your job finished in " + event.metadata().get("duration") + "ms"
        );
    }

    @KafkaListener(topics = "job.status-changed", groupId = "notification-service")
    public void onStatusChange(JobEvent event) {
        if ("FAILED".equals(event.type())) {
            emailService.sendAlert(event.user(), "Job " + event.jobId() + " failed!");
        }
    }
}
```

## Step 4: Distributing Jobs via Kafka

Instead of polling the DB, publish jobs to Kafka and let instances consume them:

```java
// Add to controller/JobController.java (Kafka-based submission replaces gateway)

// Producer: submit job to Kafka
@PostMapping("/api/jobs")
public Job submitJob(@RequestBody JobRequest request) {
    Job job = jobService.create(request);
    kafka.send("job.submitted", job.getId(), job);
    return job;
}

// Consumer: each instance picks jobs from the topic
@KafkaListener(topics = "job.submitted", groupId = "job-engine",
    concurrency = "4")  // 4 consumer threads
public void onJobSubmitted(Job job) {
    if (lockService.acquireLock(job.getId(), Duration.ofMinutes(5))) {
        jobExecutor.execute(job);
    }
}
```

With 3 instances and 12 partitions, each instance gets ~4 partitions. Jobs are distributed automatically.

## Step 5: Dead Letter Topic

Failed messages go to a DLT for investigation:

```java
@Bean
public DefaultErrorHandler errorHandler(KafkaTemplate<String, Object> template) {
    DeadLetterPublishingRecoverer recoverer =
        new DeadLetterPublishingRecoverer(template);

    return new DefaultErrorHandler(recoverer, new FixedBackOff(1000L, 3));
    // Retry 3 times, 1s apart, then send to DLT
}
```

## Step 6: Spring Integration + Kafka

### How It Fits With the Current Architecture

Up to now, the flow is entirely in-memory within a single JVM:

```
Controller → Gateway → jobInputChannel → filter → route → executor
                       (in-memory)
```

With Kafka, the channel boundary moves **across the network**:

```
Before (single instance):
  Controller → Gateway → [in-memory channel] → flow → executor

After (multi-instance):
  Controller → Kafka.send("job.submitted") → [Kafka topic] → Kafka.receive → [in-memory channel] → flow → executor
               ↑ replaces the gateway                         ↑ each instance consumes
```

Spring Integration has native Kafka adapters that plug into your existing flows — you don't rewrite the flow logic, you just swap the entry/exit points:

- **Outbound adapter** — takes messages from a Spring Integration channel and publishes to Kafka
- **Inbound adapter** — consumes from Kafka and feeds into a Spring Integration channel

Your existing `jobSubmissionFlow` (filter → enrich → route) stays unchanged. Only the source changes from a local gateway to a Kafka topic.

```java
// integration/JobIntegrationFlow.java
@Bean
public IntegrationFlow kafkaOutboundFlow() {
    return IntegrationFlow
        .from("jobCompletionChannel")
        .handle(Kafka.outboundChannelAdapter(kafkaTemplate)
            .topic("job.completed")
            .messageKey(m -> ((Job) m.getPayload()).getId()))
        .get();
}

@Bean
public IntegrationFlow kafkaInboundFlow() {
    return IntegrationFlow
        .from(Kafka.messageDrivenChannelAdapter(consumerFactory, "job.submitted"))
        .channel("jobInputChannel")  // feeds into the existing integration flow
        .get();
}
```

## Consumer Groups & Scaling

```
Topic: job.submitted (12 partitions)

Consumer Group: "job-engine"
  Instance 1: partitions [0,1,2,3]
  Instance 2: partitions [4,5,6,7]
  Instance 3: partitions [8,9,10,11]

→ Add Instance 4: Kafka rebalances automatically
  Instance 1: partitions [0,1,2]
  Instance 2: partitions [3,4,5]
  Instance 3: partitions [6,7,8]
  Instance 4: partitions [9,10,11]
```

## Key Concepts

| Concept        | Purpose                                                     |
| -------------- | ----------------------------------------------------------- |
| Topic          | Named stream of events                                      |
| Partition      | Parallelism unit (ordered within partition)                 |
| Consumer Group | Load balancing across instances                             |
| Key            | Determines partition (same key = same partition = ordering) |
| DLT            | Dead letter topic for failed messages                       |
| Exactly-once   | Idempotent producer + transactional consumer                |

---

[Chapter 10: Putting It All Together →](/blog/spring-job-engine/chapter-10-final)

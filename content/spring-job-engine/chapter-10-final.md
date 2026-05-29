# Chapter 10: Putting It All Together

[← Chapter 9: Kafka](/blog/spring-job-engine/chapter-09-kafka) | [Overview](/blog/spring-job-engine/chapter-00-overview)

---

## The Story

Ten chapters later, you have a production-grade job engine. Let's see how all the pieces connect — from a user clicking "Submit" to the job completing and everyone being notified.

## The Full Request Flow

<Mermaid chart={`sequenceDiagram
participant U as User
participant API as REST API + JWT
participant SI as Spring Integration
participant TP as Thread Pool
participant R as Redis
participant K as Kafka
participant DB as PostgreSQL

U->>API: POST /api/jobs (Bearer JWT)
API->>API: Validate JWT, extract user
API->>DB: Save Job (QUEUED)
API->>R: Cache job state
API->>K: Publish job.submitted
API-->>U: 201 Created + job ID

K->>SI: Message arrives
SI->>SI: Filter → Router (by priority)
SI->>TP: Dispatch to worker thread

TP->>R: Acquire distributed lock
TP->>DB: Status → RUNNING
loop Every 10%
TP->>R: Update progress
end
TP->>DB: Status → COMPLETED
TP->>R: Release lock, cache result
TP->>K: Publish job.completed

K->>U: Notification (email)
K->>U: Dashboard (WebSocket)
`} />

## Production Checklist

### Health & Metrics

```java
@RestController
@RequestMapping("/api/admin")
@RequiredArgsConstructor
public class AdminController {

    private final ThreadPoolTaskExecutor executor;
    private final PriorityJobQueue priorityQueue;
    private final JobProgressStore progressStore;

    @GetMapping("/metrics")
    public Map<String, Object> metrics() {
        return Map.of(
            "engine", Map.of(
                "activeThreads", executor.getActiveCount(),
                "queuedJobs", priorityQueue.size(),
                "completedTotal", executor.getCompletedTaskCount()
            ),
            "redis", Map.of(
                "runningJobs", progressStore.getRunningJobs().size(),
                "cacheHitRate", cacheManager.getCacheNames()
            ),
            "kafka", Map.of(
                "lag", kafkaAdmin.getConsumerLag()
            )
        );
    }
}
```

### Graceful Shutdown

```java
@Component
public class GracefulShutdown implements DisposableBean {

    private final ThreadPoolTaskExecutor executor;
    private final JobService jobService;

    @Override
    public void destroy() {
        // 1. Stop accepting new jobs
        // 2. Wait for running jobs (up to 30s)
        executor.setWaitForTasksToCompleteOnShutdown(true);
        executor.setAwaitTerminationSeconds(30);

        // 3. Mark still-running jobs as QUEUED (will be picked up on restart)
        progressStore.getRunningJobs().forEach(jobId ->
            jobService.transition(jobId, JobStatus.QUEUED)
        );
    }
}
```

### Retry with Exponential Backoff

```java
@Retryable(maxAttempts = 3, backoff = @Backoff(delay = 1000, multiplier = 2))
public void executeWithRetry(Job job) {
    doWork(job);
}

@Recover
public void onRetryExhausted(Exception e, Job job) {
    jobService.transition(job.getId(), JobStatus.FAILED);
    auditService.log(job.getId(), "FAILED", "system", "Retries exhausted: " + e.getMessage());
}
```

## Testing Strategy

```java
// Integration test with embedded Kafka + H2
@SpringBootTest
@EmbeddedKafka(topics = {"job.submitted", "job.completed"})
class JobEngineIntegrationTest {

    @Autowired JobService jobService;
    @Autowired KafkaTemplate<String, JobEvent> kafka;

    @Test
    void submitAndComplete() {
        Job job = jobService.submit("TEST", JobPriority.HIGH, "{}", "test@co.com");

        await().atMost(10, SECONDS).until(
            () -> jobService.getJob(job.getId()).getStatus() == JobStatus.COMPLETED
        );

        List<AuditLog> audit = auditService.getHistory(job.getId());
        assertThat(audit).extracting("action")
            .containsExactly("SUBMITTED", "STARTED", "COMPLETED");
    }
}
```

## Architecture Summary

| Layer         | Technology         | Responsibility                   |
| ------------- | ------------------ | -------------------------------- |
| API           | Spring MVC + JWT   | Authentication, request handling |
| Orchestration | Spring Integration | Message routing, flow control    |
| Execution     | ThreadPoolExecutor | Parallel job processing          |
| State         | PostgreSQL + JPA   | Persistent job storage           |
| Cache         | Redis              | Hot data, progress, locks        |
| Events        | Kafka              | Async communication, scaling     |
| Audit         | JPA + AOP          | Compliance, traceability         |
| Security      | Spring Security    | Auth, authorization              |

## What You've Learned

1. **Spring Boot** — project setup, configuration, dependency injection
2. **Domain Modeling** — state machines, entities, transitions
3. **Concurrency** — thread pools, virtual threads, locks, atomic operations
4. **Spring Integration** — channels, routers, pollers, message-driven architecture
5. **Job Control** — priority queues, cooperative pause/resume
6. **Security** — JWT, filters, role-based access
7. **Auditing** — event listeners, AOP, immutable logs
8. **Caching** — Redis, TTL, distributed locks
9. **Event Streaming** — Kafka, consumer groups, dead letters
10. **Production** — graceful shutdown, retries, metrics, testing

## What's Next

- [Chapter 12: WebSocket](/blog/spring-job-engine/chapter-12-websocket) — push real-time progress to the frontend
- [Chapter 13: Scheduled Jobs](/blog/spring-job-engine/chapter-13-scheduled-jobs) — cron-like recurring execution
- [Chapter 14: Job Dependencies](/blog/spring-job-engine/chapter-14-job-dependencies) — Job B waits for Job A to complete
- [Chapter 15: Multi-Tenancy](/blog/spring-job-engine/chapter-15-multi-tenancy) — isolate jobs by organization
- [Chapter 16: Rate Limiting](/blog/spring-job-engine/chapter-16-rate-limiting) — per-user job submission limits

---

You built a job engine. From zero to production. 🚀

[← Overview](/blog/spring-job-engine/chapter-00-overview)

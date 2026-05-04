# Chapter 8: The Audit — Observability & Hardening

[← Chapter 7: The War Room Screen](chapter-07-real-time-api.md) | [Chapter 9: Who Did What →](chapter-09-auth-and-audit.md)

---

## The Incident

Captain Deadline hires a consultant. The consultant walks around the office for two hours, then asks three questions:

1. "What's your p95 job duration?"
2. "How do you know when the dead-letter queue is growing?"
3. "Where are your logs?"

You: "We have `System.out.println`."

The consultant leaves. Captain Deadline does not look happy.

## Structured Logging: "Every Log Line Tells a Story"

Your current logs look like this:

```
Processing job abc-123
Done
Error: Connection refused
Processing job def-456
```

Which job failed? What type was it? Which worker instance ran it? You can't tell. The logs are useless for debugging.

### The Test

```java
@Test
void structuredLog_shouldIncludeJobContext() {
    Job job = jobRepository.save(new Job("CSV_IMPORT",
        "{\"file\": \"src/test/resources/small.csv\"}"));

    await().atMost(10, SECONDS).untilAsserted(() ->
        assertEquals(JobStatus.COMPLETED,
            jobRepository.findById(job.getId()).orElseThrow().getStatus()));

    List<LogEntry> logs = logCapture.getLogsForJob(job.getId());
    assertTrue(logs.size() > 0);
    logs.forEach(log -> {
        assertEquals(job.getId(), log.getMdc("jobId"));
        assertEquals("CSV_IMPORT", log.getMdc("jobType"));
    });
}
```

### The Fix

Logback with JSON encoder + MDC (Mapped Diagnostic Context):

```java
private void process(Job job) {
    MDC.put("jobId", job.getId());
    MDC.put("jobType", job.getType());
    MDC.put("instanceId", instanceId);
    try {
        log.info("Starting job");
        // ... run handler
        log.info("Job completed");
    } catch (Exception e) {
        log.error("Job failed", e);
    } finally {
        MDC.clear();
    }
}
```

Now every log line is JSON with context:

```json
{"timestamp":"2026-05-04T14:23:01Z","level":"INFO","message":"Starting job",
 "jobId":"abc-123","jobType":"CSV_IMPORT","instanceId":"worker-1"}
{"timestamp":"2026-05-04T14:23:04Z","level":"INFO","message":"Job completed",
 "jobId":"abc-123","jobType":"CSV_IMPORT","instanceId":"worker-1"}
```

Searchable. Filterable. The consultant would approve.

## Metrics: "Numbers, Not Feelings"

### The Test

```java
@Test
void metrics_shouldTrackJobDuration() {
    jobRepository.save(new Job("CSV_IMPORT",
        "{\"file\": \"src/test/resources/small.csv\"}"));

    await().atMost(10, SECONDS).untilAsserted(() ->
        assertEquals(1, jobRepository.countByStatus(JobStatus.COMPLETED)));

    Timer timer = meterRegistry.find("job.duration")
        .tag("type", "CSV_IMPORT").timer();
    assertNotNull(timer);
    assertEquals(1, timer.count());
    assertTrue(timer.totalTime(TimeUnit.SECONDS) > 0);
}
```

### The Fix

Micrometer — Spring Boot's metrics library:

```java
private void process(Job job) {
    Timer.Sample sample = Timer.start(meterRegistry);
    try {
        // ... run handler
        meterRegistry.counter("job.completed", "type", job.getType()).increment();
    } catch (Exception e) {
        meterRegistry.counter("job.failed", "type", job.getType()).increment();
    } finally {
        sample.stop(meterRegistry.timer("job.duration", "type", job.getType()));
    }
}
```

```bash
# Prometheus endpoint (built into Spring Boot Actuator)
curl http://localhost:8080/actuator/prometheus | grep job_duration

# job_duration_seconds_count{type="CSV_IMPORT"} 1423
# job_duration_seconds_sum{type="CSV_IMPORT"} 2847.3
# job_duration_seconds_max{type="CSV_IMPORT"} 12.4
```

## Grafana Dashboard

Wire Prometheus to Grafana. Build a dashboard with:

- **Throughput**: jobs completed per minute, by type
- **Error rate**: failed / total, with alert threshold
- **p95 latency**: 95th percentile job duration
- **Queue depth**: pending jobs over time
- **Dead-letter count**: with Slack alert if > 10

```yaml
# docker-compose.yml additions
prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
```

Captain Deadline puts the Grafana dashboard on the 65-inch TV. It replaces the curl terminal. He's happier.

## Load Test: "Will It Hold?"

### The Test (Gatling)

```scala
class JobEngineSimulation extends Simulation {
  val submit = scenario("Submit Jobs")
    .repeat(1000) {
      exec(http("submit-csv").post("/jobs")
        .body(StringBody("""{"type":"CSV_IMPORT","payload":"{}"}"""))
        .check(status.is(201)))
    }

  setUp(
    submit.inject(rampUsers(500).during(10))
  ).assertions(
    global.responseTime.percentile3.lt(500),
    global.successfulRequests.percent.gt(99.0)
  )
}
```

```bash
./gradlew gatlingRun
# → p95 response time: 127ms ✓
# → success rate: 99.8% ✓
# → 1000 jobs submitted in 10 seconds
```

## What You Learned

- **Structured logging** — JSON + MDC, every log line has jobId/type/instance
- **Micrometer metrics** — counters, timers, gauges for job throughput and latency
- **Prometheus + Grafana** — scraping, dashboards, alerting
- **Load testing** — Gatling simulations with assertions

The consultant comes back. Sees the Grafana dashboard. Sees the structured logs. Sees the load test results. Nods. "Not bad."

Captain Deadline almost smiles.

Next chapter: someone cancels 12,000 jobs and nobody knows who did it.

---

[← Chapter 7: The War Room Screen](chapter-07-real-time-api.md) | [Chapter 9: Who Did What →](chapter-09-auth-and-audit.md)

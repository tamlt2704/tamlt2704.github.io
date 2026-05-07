# Chapter 8: The Dashboard — Monitoring and Metrics

[← Chapter 7: The Pipeline](chapter-07-job-orchestration.md) | [Chapter 9: Testing →](chapter-09-testing.md)

---

## The Incident

Monday morning. Admiral Uptime opens his laptop. Three jobs ran overnight. Did they succeed? He checks Slack — no alerts. He checks email — nothing. He opens the server logs and scrolls through 50,000 lines.

"This is barbaric. I want a dashboard. Green means good. Red means someone gets paged. I want to see it from my phone."

## JobExplorer: Querying Job History

Spring Batch stores everything in its metadata tables. `JobExplorer` is the read-only interface to query them:

```java
// src/main/java/com/megabank/controller/MonitoringController.java
package com.megabank.controller;

import org.springframework.batch.core.*;
import org.springframework.batch.core.explore.JobExplorer;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/monitoring")
public class MonitoringController {

    private final JobExplorer jobExplorer;

    public MonitoringController(JobExplorer jobExplorer) {
        this.jobExplorer = jobExplorer;
    }

    @GetMapping("/jobs")
    public List<String> listJobNames() {
        return jobExplorer.getJobNames();
    }

    @GetMapping("/jobs/{jobName}/executions")
    public List<Map<String, Object>> getExecutions(@PathVariable String jobName,
                                                     @RequestParam(defaultValue = "10") int limit) {
        return jobExplorer.getJobInstances(jobName, 0, limit).stream()
            .flatMap(instance -> jobExplorer.getJobExecutions(instance).stream())
            .map(this::toSummary)
            .collect(Collectors.toList());
    }

    @GetMapping("/jobs/{jobName}/latest")
    public Map<String, Object> getLatestExecution(@PathVariable String jobName) {
        List<JobInstance> instances = jobExplorer.getJobInstances(jobName, 0, 1);
        if (instances.isEmpty()) {
            return Map.of("status", "NEVER_RUN");
        }

        List<JobExecution> executions = jobExplorer.getJobExecutions(instances.get(0));
        if (executions.isEmpty()) {
            return Map.of("status", "NO_EXECUTIONS");
        }

        return toSummary(executions.get(0));
    }

    @GetMapping("/jobs/running")
    public List<Map<String, Object>> getRunningJobs() {
        return jobExplorer.getJobNames().stream()
            .flatMap(name -> jobExplorer.findRunningJobExecutions(name).stream())
            .map(this::toSummary)
            .collect(Collectors.toList());
    }

    private Map<String, Object> toSummary(JobExecution execution) {
        return Map.of(
            "executionId", execution.getId(),
            "jobName", execution.getJobInstance().getJobName(),
            "status", execution.getStatus().toString(),
            "startTime", execution.getStartTime() != null ? execution.getStartTime().toString() : "N/A",
            "endTime", execution.getEndTime() != null ? execution.getEndTime().toString() : "N/A",
            "exitStatus", execution.getExitStatus().getExitCode(),
            "steps", execution.getStepExecutions().stream()
                .map(s -> Map.of(
                    "name", s.getStepName(),
                    "status", s.getStatus().toString(),
                    "readCount", s.getReadCount(),
                    "writeCount", s.getWriteCount(),
                    "skipCount", s.getSkipCount()
                ))
                .toList()
        );
    }
}
```

```bash
# What jobs exist?
curl http://localhost:8080/monitoring/jobs
# → ["reconciliationJob", "monthEndJob", "archiveJob"]

# Latest execution of reconciliation
curl http://localhost:8080/monitoring/jobs/reconciliationJob/latest
# → {"status":"COMPLETED","startTime":"2024-01-22T05:00:01","readCount":2147000,...}

# What's running right now?
curl http://localhost:8080/monitoring/jobs/running
# → []
```

## Spring Boot Actuator: Health and Metrics

Add Actuator for production-grade monitoring:

```groovy
// build.gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-actuator'
    implementation 'io.micrometer:micrometer-registry-prometheus' // for Grafana
}
```

```properties
# application.properties
management.endpoints.web.exposure.include=health,metrics,prometheus,info
management.endpoint.health.show-details=always
```

### Custom Health Indicator

```java
// src/main/java/com/megabank/health/BatchHealthIndicator.java
package com.megabank.health;

import org.springframework.batch.core.*;
import org.springframework.batch.core.explore.JobExplorer;
import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.stereotype.Component;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.List;

@Component
public class BatchHealthIndicator implements HealthIndicator {

    private final JobExplorer jobExplorer;

    public BatchHealthIndicator(JobExplorer jobExplorer) {
        this.jobExplorer = jobExplorer;
    }

    @Override
    public Health health() {
        Health.Builder builder = Health.up();

        for (String jobName : jobExplorer.getJobNames()) {
            List<JobInstance> instances = jobExplorer.getJobInstances(jobName, 0, 1);
            if (instances.isEmpty()) continue;

            List<JobExecution> executions = jobExplorer.getJobExecutions(instances.get(0));
            if (executions.isEmpty()) continue;

            JobExecution latest = executions.get(0);

            if (latest.getStatus() == BatchStatus.FAILED) {
                builder.down()
                    .withDetail(jobName + ".status", "FAILED")
                    .withDetail(jobName + ".failedAt", latest.getEndTime().toString())
                    .withDetail(jobName + ".exitDescription",
                        latest.getExitStatus().getExitDescription());
            } else if (latest.getStatus() == BatchStatus.STARTED) {
                // Check for ghost jobs
                Duration running = Duration.between(
                    latest.getStartTime(), LocalDateTime.now());
                if (running.toHours() > 2) {
                    builder.down()
                        .withDetail(jobName + ".status", "STUCK")
                        .withDetail(jobName + ".runningFor", running.toString());
                }
            } else {
                builder.withDetail(jobName + ".status", latest.getStatus().toString())
                    .withDetail(jobName + ".lastRun", latest.getEndTime().toString());
            }
        }

        return builder.build();
    }
}
```

```bash
curl http://localhost:8080/actuator/health
```

```json
{
  "status": "DOWN",
  "components": {
    "batch": {
      "status": "DOWN",
      "details": {
        "reconciliationJob.status": "FAILED",
        "reconciliationJob.failedAt": "2024-01-22T05:38:47",
        "monthEndJob.status": "COMPLETED",
        "monthEndJob.lastRun": "2024-01-31T04:23:15"
      }
    }
  }
}
```

Admiral Uptime points his monitoring tool at `/actuator/health`. Red = page someone.

## Micrometer Metrics: Grafana Dashboards

Spring Batch 5 integrates with Micrometer out of the box. Add custom metrics:

```java
// src/main/java/com/megabank/listener/MetricsJobListener.java
package com.megabank.listener;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import org.springframework.batch.core.JobExecution;
import org.springframework.batch.core.JobExecutionListener;
import org.springframework.stereotype.Component;

import java.time.Duration;

@Component
public class MetricsJobListener implements JobExecutionListener {

    private final MeterRegistry registry;

    public MetricsJobListener(MeterRegistry registry) {
        this.registry = registry;
    }

    @Override
    public void beforeJob(JobExecution jobExecution) {
        Counter.builder("batch.job.started")
            .tag("job", jobExecution.getJobInstance().getJobName())
            .register(registry)
            .increment();
    }

    @Override
    public void afterJob(JobExecution jobExecution) {
        String jobName = jobExecution.getJobInstance().getJobName();
        String status = jobExecution.getStatus().toString();

        Counter.builder("batch.job.completed")
            .tag("job", jobName)
            .tag("status", status)
            .register(registry)
            .increment();

        if (jobExecution.getStartTime() != null && jobExecution.getEndTime() != null) {
            Duration duration = Duration.between(
                jobExecution.getStartTime(), jobExecution.getEndTime());
            Timer.builder("batch.job.duration")
                .tag("job", jobName)
                .tag("status", status)
                .register(registry)
                .record(duration);
        }

        // Track items processed
        jobExecution.getStepExecutions().forEach(step -> {
            registry.gauge("batch.step.read_count",
                List.of(Tag.of("job", jobName), Tag.of("step", step.getStepName())),
                step.getReadCount());
            registry.gauge("batch.step.skip_count",
                List.of(Tag.of("job", jobName), Tag.of("step", step.getStepName())),
                step.getSkipCount());
        });
    }
}
```

Prometheus endpoint:

```bash
curl http://localhost:8080/actuator/prometheus
```

```
# HELP batch_job_duration_seconds
# TYPE batch_job_duration_seconds summary
batch_job_duration_seconds{job="reconciliationJob",status="COMPLETED"} 243.5
batch_job_duration_seconds{job="reconciliationJob",status="FAILED"} 38.2

# HELP batch_job_completed_total
# TYPE batch_job_completed_total counter
batch_job_completed_total{job="reconciliationJob",status="COMPLETED"} 28
batch_job_completed_total{job="reconciliationJob",status="FAILED"} 2
```

## Chunk Progress: Real-Time Tracking

Brenda: "The job's been running for 3 minutes. How far along is it?"

```java
// src/main/java/com/megabank/listener/ProgressListener.java
package com.megabank.listener;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.batch.core.ChunkListener;
import org.springframework.batch.core.StepExecution;
import org.springframework.batch.core.scope.context.ChunkContext;
import org.springframework.stereotype.Component;

@Component
public class ProgressListener implements ChunkListener {

    private static final Logger log = LoggerFactory.getLogger(ProgressListener.class);
    private long totalExpected = 0;

    public void setTotalExpected(long total) {
        this.totalExpected = total;
    }

    @Override
    public void afterChunk(ChunkContext context) {
        StepExecution step = context.getStepContext().getStepExecution();
        long processed = step.getReadCount() + step.getReadSkipCount();

        if (totalExpected > 0) {
            double percent = (double) processed / totalExpected * 100;
            log.info("Progress: {}/{} ({:.1f}%) — {} skipped",
                processed, totalExpected, percent, step.getSkipCount());
        } else {
            log.info("Progress: {} items processed, {} skipped",
                processed, step.getSkipCount());
        }
    }
}
```

Add a progress endpoint:

```java
@GetMapping("/jobs/{executionId}/progress")
public Map<String, Object> getProgress(@PathVariable Long executionId) {
    JobExecution execution = jobExplorer.getJobExecution(executionId);
    if (execution == null) return Map.of("error", "not found");

    return execution.getStepExecutions().stream()
        .filter(s -> s.getStatus() == BatchStatus.STARTED)
        .findFirst()
        .map(step -> Map.<String, Object>of(
            "step", step.getStepName(),
            "readCount", step.getReadCount(),
            "writeCount", step.getWriteCount(),
            "skipCount", step.getSkipCount(),
            "commitCount", step.getCommitCount(),
            "status", "RUNNING"
        ))
        .orElse(Map.of("status", execution.getStatus().toString()));
}
```

```bash
curl http://localhost:8080/monitoring/jobs/42/progress
# → {"step":"reconcileChunkStep","readCount":1250000,"writeCount":1250000,"commitCount":1250}
```

## Alerting: PagerDuty Integration

```java
// src/main/java/com/megabank/listener/AlertingJobListener.java
package com.megabank.listener;

import org.springframework.batch.core.BatchStatus;
import org.springframework.batch.core.JobExecution;
import org.springframework.batch.core.JobExecutionListener;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Component
public class AlertingJobListener implements JobExecutionListener {

    private final RestTemplate restTemplate;
    private final String webhookUrl;

    public AlertingJobListener(RestTemplate restTemplate,
                                @Value("${alerting.webhook-url}") String webhookUrl) {
        this.restTemplate = restTemplate;
        this.webhookUrl = webhookUrl;
    }

    @Override
    public void afterJob(JobExecution jobExecution) {
        if (jobExecution.getStatus() == BatchStatus.FAILED) {
            String jobName = jobExecution.getJobInstance().getJobName();
            String error = jobExecution.getExitStatus().getExitDescription();

            restTemplate.postForEntity(webhookUrl, Map.of(
                "severity", "critical",
                "summary", jobName + " FAILED",
                "details", error != null ? error : "No error details",
                "source", "megabank-batch"
            ), Void.class);
        }
    }
}
```

## The Test: Monitoring Endpoints

```java
@Test
void monitoringEndpoint_shouldReturnJobHistory() throws Exception {
    // Run a job
    jobLauncherTestUtils.launchJob(defaultParams());

    // Query monitoring
    var response = restTemplate.getForObject(
        "/monitoring/jobs/reconciliationJob/latest", Map.class);

    assertThat(response.get("status")).isEqualTo("COMPLETED");
    assertThat(response.get("steps")).isNotNull();
}

@Test
void healthEndpoint_shouldReportDown_whenJobFailed() throws Exception {
    // Run a failing job
    processor.setAlwaysFail(true);
    jobLauncherTestUtils.launchJob(defaultParams());

    var health = restTemplate.getForObject("/actuator/health", Map.class);
    assertThat(health.get("status")).isEqualTo("DOWN");
}

@Test
void progressEndpoint_shouldShowLiveProgress() throws Exception {
    generateTestCsv(inputPath, 100_000);

    // Launch async
    CompletableFuture.runAsync(() -> {
        try { jobLauncherTestUtils.launchJob(defaultParams()); }
        catch (Exception e) { throw new RuntimeException(e); }
    });

    // Wait for job to start processing
    Thread.sleep(2000);

    var progress = restTemplate.getForObject(
        "/monitoring/jobs/" + getRunningExecutionId() + "/progress", Map.class);
    assertThat((int) progress.get("readCount")).isGreaterThan(0);
    assertThat(progress.get("status")).isEqualTo("RUNNING");
}
```

## What You Learned

- **`JobExplorer`** — read-only access to job execution history
- **Health indicators** — `/actuator/health` for monitoring tools
- **Micrometer metrics** — counters, timers, gauges for Prometheus/Grafana
- **`ChunkListener`** — real-time progress tracking per chunk
- **`JobExecutionListener`** — job-level metrics and alerting
- **Progress endpoint** — live read/write/skip counts for running jobs
- **Alerting** — webhook integration for failed jobs

Admiral Uptime has his dashboard. Green dots for successful nightly runs. Red alerts when something fails. Progress bars for running jobs. He can check from his phone at 6 AM without opening a terminal.

One thing remains: how do you test all of this without a real database, real files, and real APIs? How do you write fast, reliable tests for batch jobs that process millions of rows?

That's Chapter 9.

---

[← Chapter 7: The Pipeline](chapter-07-job-orchestration.md) | [Chapter 9: Testing →](chapter-09-testing.md)

# Chapter 17: Building a Batch Platform

[prev: Testing Strategies](chapter-16-testing.md) | [Overview](chapter-00-overview.md)

## From Jobs to Platform

When you have 10+ batch jobs, you need a platform: centralized management, monitoring, self-service job creation, and operational tooling. This chapter shows how to build one.

## Platform Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Batch Platform                         │
├─────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │ REST API │  │ Dashboard│  │ Job Registry          │  │
│  │ (manage) │  │ (monitor)│  │ (discover & configure)│  │
│  └────┬─────┘  └────┬─────┘  └──────────┬───────────┘  │
│       │              │                    │              │
│  ┌────▼──────────────▼────────────────────▼───────────┐ │
│  │              Job Orchestrator                        │ │
│  │  (scheduling, dependencies, concurrency control)    │ │
│  └────────────────────┬───────────────────────────────┘ │
│                       │                                  │
│  ┌────────────────────▼───────────────────────────────┐ │
│  │              Job Executor Pool                       │ │
│  │  (thread pools, partitioning, remote workers)       │ │
│  └────────────────────┬───────────────────────────────┘ │
│                       │                                  │
│  ┌────────────────────▼───────────────────────────────┐ │
│  │         Shared Infrastructure                       │ │
│  │  (JobRepository, metrics, alerting, audit log)      │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Job Registry — Self-Service Job Definition

```java
@Entity
@Table(name = "job_definitions")
public class JobDefinition {
    @Id
    private String jobName;
    private String description;
    private String cronExpression;
    private String ownerTeam;
    private boolean enabled;
    private int maxConcurrency;
    private int timeoutMinutes;
    private String alertChannel; // Slack channel for failures

    @ElementCollection
    private Map<String, String> defaultParameters;

    @ElementCollection
    private List<String> dependencies; // Jobs that must complete first
}
```

```java
@RestController
@RequestMapping("/api/jobs")
public class JobRegistryController {

    private final JobDefinitionRepository registry;
    private final JobLauncher jobLauncher;
    private final JobExplorer jobExplorer;

    @GetMapping
    public List<JobDefinition> listJobs() {
        return registry.findAll();
    }

    @PostMapping("/{jobName}/run")
    public ResponseEntity<JobExecutionDto> triggerJob(
            @PathVariable String jobName,
            @RequestBody Map<String, String> parameters) {

        JobDefinition def = registry.findById(jobName)
                .orElseThrow(() -> new NotFoundException("Job not found: " + jobName));

        if (!def.isEnabled()) {
            return ResponseEntity.status(409).build();
        }

        // Check concurrency
        long running = jobExplorer.findRunningJobExecutions(jobName).size();
        if (running >= def.getMaxConcurrency()) {
            return ResponseEntity.status(429).body(null);
        }

        JobParameters params = buildParameters(def, parameters);
        JobExecution execution = jobLauncher.run(getJob(jobName), params);

        return ResponseEntity.accepted().body(JobExecutionDto.from(execution));
    }

    @PostMapping("/{jobName}/stop")
    public ResponseEntity<Void> stopJob(@PathVariable String jobName) {
        jobExplorer.findRunningJobExecutions(jobName).forEach(exec -> {
            exec.setStatus(BatchStatus.STOPPING);
            jobRepository.update(exec);
        });
        return ResponseEntity.ok().build();
    }
}
```

## Dynamic Job Scheduling

```java
@Component
public class DynamicScheduler {

    private final ScheduledTaskRegistrar taskRegistrar;
    private final JobDefinitionRepository registry;
    private final Map<String, ScheduledFuture<?>> scheduledJobs = new ConcurrentHashMap<>();

    @PostConstruct
    public void scheduleAllJobs() {
        registry.findByEnabledTrue().forEach(this::scheduleJob);
    }

    public void scheduleJob(JobDefinition def) {
        cancelJob(def.getJobName());

        if (def.getCronExpression() == null) return;

        ScheduledFuture<?> future = taskScheduler.schedule(
                () -> launchJob(def),
                new CronTrigger(def.getCronExpression())
        );
        scheduledJobs.put(def.getJobName(), future);
    }

    public void cancelJob(String jobName) {
        ScheduledFuture<?> existing = scheduledJobs.remove(jobName);
        if (existing != null) existing.cancel(false);
    }

    // Called when job definition is updated
    @EventListener
    public void onJobDefinitionChanged(JobDefinitionChangedEvent event) {
        scheduleJob(event.getDefinition());
    }
}
```

## Job Dependency Management

```java
@Component
public class DependencyAwareScheduler {

    private final JobDefinitionRepository registry;
    private final JobExplorer jobExplorer;

    public boolean canRun(String jobName) {
        JobDefinition def = registry.findById(jobName).orElseThrow();

        for (String dependency : def.getDependencies()) {
            JobExecution lastExecution = getLastExecution(dependency);

            if (lastExecution == null || lastExecution.getStatus() != BatchStatus.COMPLETED) {
                log.info("Job {} blocked: dependency {} not completed", jobName, dependency);
                return false;
            }

            // Check if dependency ran today (for daily jobs)
            if (lastExecution.getEndTime().isBefore(LocalDate.now().atStartOfDay().toInstant(ZoneOffset.UTC))) {
                log.info("Job {} blocked: dependency {} hasn't run today", jobName, dependency);
                return false;
            }
        }
        return true;
    }

    private JobExecution getLastExecution(String jobName) {
        return jobExplorer.getJobInstances(jobName, 0, 1).stream()
                .flatMap(instance -> jobExplorer.getJobExecutions(instance).stream())
                .max(Comparator.comparing(JobExecution::getCreateTime))
                .orElse(null);
    }
}
```

## Monitoring Dashboard API

```java
@RestController
@RequestMapping("/api/monitoring")
public class MonitoringController {

    @GetMapping("/overview")
    public PlatformOverview getOverview() {
        return PlatformOverview.builder()
                .totalJobs(registry.count())
                .runningJobs(jobExplorer.findRunningJobExecutions("*").size())
                .failedToday(countFailedToday())
                .completedToday(countCompletedToday())
                .avgDurationMs(calculateAvgDuration())
                .build();
    }

    @GetMapping("/jobs/{jobName}/history")
    public List<JobExecutionSummary> getJobHistory(
            @PathVariable String jobName,
            @RequestParam(defaultValue = "30") int days) {

        return jobExplorer.getJobInstances(jobName, 0, 100).stream()
                .flatMap(instance -> jobExplorer.getJobExecutions(instance).stream())
                .filter(exec -> exec.getCreateTime().isAfter(Instant.now().minus(Duration.ofDays(days))))
                .map(exec -> new JobExecutionSummary(
                        exec.getId(),
                        exec.getStatus(),
                        exec.getStartTime(),
                        exec.getEndTime(),
                        exec.getStepExecutions().stream().mapToLong(StepExecution::getWriteCount).sum()
                ))
                .sorted(Comparator.comparing(JobExecutionSummary::startTime).reversed())
                .toList();
    }

    @GetMapping("/alerts")
    public List<Alert> getActiveAlerts() {
        return jobExplorer.findRunningJobExecutions("*").stream()
                .filter(this::isStuck)
                .map(exec -> new Alert("STUCK_JOB", exec.getJobInstance().getJobName(),
                        "Running for " + Duration.between(exec.getStartTime(), Instant.now()).toMinutes() + " minutes"))
                .toList();
    }
}
```

## Metrics with Micrometer

```java
@Component
public class BatchMetricsListener implements JobExecutionListener, StepExecutionListener {

    private final MeterRegistry meterRegistry;

    @Override
    public void afterJob(JobExecution jobExecution) {
        String jobName = jobExecution.getJobInstance().getJobName();
        String status = jobExecution.getStatus().toString();

        meterRegistry.counter("batch.job.completed", "job", jobName, "status", status).increment();

        if (jobExecution.getEndTime() != null) {
            long durationMs = Duration.between(jobExecution.getStartTime(), jobExecution.getEndTime()).toMillis();
            meterRegistry.timer("batch.job.duration", "job", jobName).record(durationMs, TimeUnit.MILLISECONDS);
        }
    }

    @Override
    public ExitStatus afterStep(StepExecution stepExecution) {
        String jobName = stepExecution.getJobExecution().getJobInstance().getJobName();
        String stepName = stepExecution.getStepName();

        meterRegistry.gauge("batch.step.read_count", Tags.of("job", jobName, "step", stepName),
                stepExecution.getReadCount());
        meterRegistry.gauge("batch.step.write_count", Tags.of("job", jobName, "step", stepName),
                stepExecution.getWriteCount());
        meterRegistry.gauge("batch.step.skip_count", Tags.of("job", jobName, "step", stepName),
                stepExecution.getSkipCount());

        return stepExecution.getExitStatus();
    }
}
```

## Alerting on Failures

```java
@Component
public class BatchAlertingListener implements JobExecutionListener {

    private final SlackClient slackClient;
    private final JobDefinitionRepository registry;

    @Override
    public void afterJob(JobExecution jobExecution) {
        if (jobExecution.getStatus() == BatchStatus.FAILED) {
            JobDefinition def = registry.findById(jobExecution.getJobInstance().getJobName()).orElse(null);
            String channel = def != null ? def.getAlertChannel() : "#batch-alerts";

            String message = """
                🚨 *Batch Job Failed*
                • Job: `%s`
                • Status: %s
                • Started: %s
                • Duration: %s
                • Error: %s
                """.formatted(
                    jobExecution.getJobInstance().getJobName(),
                    jobExecution.getStatus(),
                    jobExecution.getStartTime(),
                    Duration.between(jobExecution.getStartTime(), Instant.now()),
                    jobExecution.getAllFailureExceptions().stream()
                            .map(Throwable::getMessage).findFirst().orElse("Unknown")
            );

            slackClient.send(channel, message);
        }
    }
}
```

## Multi-Tenant Batch Processing

```java
@Component
public class TenantAwareBatchLauncher {

    private final JobLauncher jobLauncher;
    private final TenantRepository tenantRepo;

    public void runForAllTenants(Job job) {
        List<Tenant> tenants = tenantRepo.findAllActive();

        for (Tenant tenant : tenants) {
            JobParameters params = new JobParametersBuilder()
                    .addString("tenantId", tenant.getId())
                    .addString("tenantDb", tenant.getDatabaseUrl())
                    .addLong("timestamp", System.currentTimeMillis())
                    .toJobParameters();

            try {
                jobLauncher.run(job, params);
            } catch (Exception e) {
                log.error("Failed to run job for tenant {}", tenant.getId(), e);
            }
        }
    }
}

@Bean
@StepScope
public DataSource tenantDataSource(
        @Value("#{jobParameters['tenantDb']}") String dbUrl) {
    return DataSourceBuilder.create().url(dbUrl).build();
}
```

## Operational Endpoints

```java
@RestController
@RequestMapping("/api/ops")
public class OperationsController {

    @PostMapping("/jobs/{jobName}/restart/{executionId}")
    public ResponseEntity<JobExecutionDto> restartJob(
            @PathVariable String jobName,
            @PathVariable Long executionId) throws Exception {

        JobExecution failed = jobExplorer.getJobExecution(executionId);
        if (failed.getStatus() != BatchStatus.FAILED) {
            return ResponseEntity.badRequest().build();
        }

        JobExecution restarted = jobLauncher.run(
                getJob(jobName), failed.getJobParameters());
        return ResponseEntity.ok(JobExecutionDto.from(restarted));
    }

    @PostMapping("/jobs/{jobName}/abandon/{executionId}")
    public ResponseEntity<Void> abandonJob(
            @PathVariable String jobName,
            @PathVariable Long executionId) {

        JobExecution execution = jobExplorer.getJobExecution(executionId);
        execution.setStatus(BatchStatus.ABANDONED);
        jobRepository.update(execution);
        return ResponseEntity.ok().build();
    }

    @DeleteMapping("/jobs/{jobName}/history")
    public ResponseEntity<Map<String, Long>> purgeHistory(
            @PathVariable String jobName,
            @RequestParam(defaultValue = "90") int olderThanDays) {

        long deleted = purgeJobHistory(jobName, olderThanDays);
        return ResponseEntity.ok(Map.of("deletedExecutions", deleted));
    }
}
```

## Docker Deployment

```dockerfile
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY build/libs/batch-platform.jar app.jar

ENV JAVA_OPTS="-Xms512m -Xmx2g -XX:+UseG1GC"
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
```

```yaml
# docker-compose.yml
services:
  batch-platform:
    build: .
    environment:
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/batch
      SPRING_PROFILES_ACTIVE: production
    depends_on:
      postgres:
        condition: service_healthy
    deploy:
      resources:
        limits:
          memory: 2g
          cpus: "2"

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: batch
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"]
      interval: 5s

volumes:
  pgdata:
```

## Key Takeaways

- A batch platform centralizes job management, monitoring, and operations
- Dynamic scheduling allows runtime changes without redeployment
- Job dependencies prevent out-of-order execution in pipelines
- Metrics + alerting give visibility into job health
- Multi-tenancy requires tenant-aware data sources and job parameters
- REST APIs enable self-service job management and integration with CI/CD
- Operational endpoints (restart, abandon, purge) are essential for production

# Chapter 15: Event-Driven Batch

[prev: Reporting & Aggregation](chapter-14-reporting.md) | [next: Testing Strategies](chapter-16-testing.md)

## Combining Events with Batch

Not all batch jobs run on a schedule. Many are triggered by events: a file lands in S3, a Kafka topic accumulates enough messages, or an upstream system signals completion.

## Kafka-Triggered Batch Jobs

Accumulate events, then process in batch:

```java
@Component
public class KafkaBatchTrigger {

    private final JobLauncher jobLauncher;
    private final Job orderProcessingJob;
    private final List<String> buffer = Collections.synchronizedList(new ArrayList<>());

    @KafkaListener(topics = "order-events", groupId = "batch-processor")
    public void onOrderEvent(ConsumerRecord<String, String> record) {
        buffer.add(record.value());

        if (buffer.size() >= 1000) {
            triggerBatch();
        }
    }

    @Scheduled(fixedDelay = 60000) // Also trigger every minute if buffer has items
    public void scheduledFlush() {
        if (!buffer.isEmpty()) {
            triggerBatch();
        }
    }

    private synchronized void triggerBatch() {
        if (buffer.isEmpty()) return;

        List<String> batch = new ArrayList<>(buffer);
        buffer.clear();

        // Write batch to temp file for the job to read
        Path tempFile = writeBatchToFile(batch);

        try {
            jobLauncher.run(orderProcessingJob, new JobParametersBuilder()
                    .addString("inputFile", tempFile.toString())
                    .addLong("timestamp", System.currentTimeMillis())
                    .toJobParameters());
        } catch (Exception e) {
            log.error("Failed to launch batch job", e);
            // Re-queue the events
            buffer.addAll(batch);
        }
    }
}
```

## S3 Event-Triggered Processing

```java
@Component
public class S3EventListener {

    private final JobLauncher jobLauncher;
    private final Job fileIngestionJob;

    @SqsListener("file-upload-notifications")
    public void onS3Event(S3EventNotification notification) {
        for (S3EventNotification.S3EventNotificationRecord record : notification.getRecords()) {
            String bucket = record.getS3().getBucket().getName();
            String key = record.getS3().getObject().getKey();

            if (key.endsWith(".csv") && key.startsWith("incoming/")) {
                launchJob(bucket, key);
            }
        }
    }

    private void launchJob(String bucket, String key) {
        try {
            jobLauncher.run(fileIngestionJob, new JobParametersBuilder()
                    .addString("s3Bucket", bucket)
                    .addString("s3Key", key)
                    .addLong("timestamp", System.currentTimeMillis())
                    .toJobParameters());
        } catch (Exception e) {
            log.error("Failed to process s3://{}/{}", bucket, key, e);
        }
    }
}
```

## Micro-Batching from Streams

Process streaming data in configurable windows:

```java
@Component
public class MicroBatchAccumulator {

    private final BlockingQueue<Event> queue = new LinkedBlockingQueue<>(10_000);
    private final JobLauncher jobLauncher;
    private final Job microBatchJob;

    @KafkaListener(topics = "high-volume-events")
    public void accumulate(Event event) {
        if (!queue.offer(event)) {
            log.warn("Queue full, triggering immediate batch");
            triggerBatch();
            queue.offer(event);
        }
    }

    @Scheduled(fixedRate = 10000) // Every 10 seconds
    public void windowTrigger() {
        if (queue.size() >= 100) { // Minimum batch size
            triggerBatch();
        }
    }

    private void triggerBatch() {
        List<Event> batch = new ArrayList<>();
        queue.drainTo(batch, 5000); // Max 5000 per batch

        if (batch.isEmpty()) return;

        // Store batch for job to read
        String batchId = UUID.randomUUID().toString();
        batchStore.save(batchId, batch);

        try {
            jobLauncher.run(microBatchJob, new JobParametersBuilder()
                    .addString("batchId", batchId)
                    .addLong("batchSize", (long) batch.size())
                    .addLong("timestamp", System.currentTimeMillis())
                    .toJobParameters());
        } catch (Exception e) {
            log.error("Micro-batch failed for batchId={}", batchId, e);
        }
    }
}
```

## Job Chaining via Events

One job completes → triggers the next:

```java
@Component
public class JobChainListener implements JobExecutionListener {

    private final ApplicationEventPublisher eventPublisher;

    @Override
    public void afterJob(JobExecution jobExecution) {
        if (jobExecution.getStatus() == BatchStatus.COMPLETED) {
            eventPublisher.publishEvent(new JobCompletedEvent(
                    jobExecution.getJobInstance().getJobName(),
                    jobExecution.getJobParameters()
            ));
        }
    }
}

@Component
public class JobChainOrchestrator {

    private final JobLauncher jobLauncher;
    private final Map<String, Job> jobs;

    @EventListener
    public void onJobCompleted(JobCompletedEvent event) {
        String nextJob = getNextJob(event.getJobName());
        if (nextJob == null) return;

        try {
            JobParameters params = new JobParametersBuilder(event.getParameters())
                    .addString("triggeredBy", event.getJobName())
                    .addLong("chainTimestamp", System.currentTimeMillis())
                    .toJobParameters();

            jobLauncher.run(jobs.get(nextJob), params);
        } catch (Exception e) {
            log.error("Failed to chain job {} after {}", nextJob, event.getJobName(), e);
        }
    }

    private String getNextJob(String completedJob) {
        return switch (completedJob) {
            case "extractJob" -> "transformJob";
            case "transformJob" -> "loadJob";
            case "loadJob" -> "reportJob";
            default -> null;
        };
    }
}
```

## Dead Letter Queue Processing

Reprocess failed events from DLQ:

```java
@Configuration
public class DlqReprocessConfig {

    @Bean
    public Job dlqReprocessJob(JobRepository jobRepository, Step reprocessStep) {
        return new JobBuilder("dlqReprocessJob", jobRepository)
                .start(reprocessStep)
                .build();
    }

    @Bean
    public Step reprocessStep(JobRepository jobRepository,
                              PlatformTransactionManager txManager) {
        return new StepBuilder("reprocess", jobRepository)
                .<FailedEvent, ProcessedEvent>chunk(100, txManager)
                .reader(dlqReader())
                .processor(retryProcessor())
                .writer(successWriter())
                .faultTolerant()
                .skip(PermanentFailureException.class)
                .skipLimit(Integer.MAX_VALUE)
                .listener(new DlqSkipListener()) // Log permanently failed items
                .build();
    }

    @Bean
    public ItemReader<FailedEvent> dlqReader() {
        return new JdbcPagingItemReaderBuilder<FailedEvent>()
                .name("dlqReader")
                .dataSource(dataSource)
                .selectClause("SELECT *")
                .fromClause("FROM dead_letter_queue")
                .whereClause("WHERE retry_count < 3 AND created_at > :cutoff")
                .sortKeys(Map.of("created_at", Order.ASCENDING))
                .parameterValues(Map.of("cutoff", Timestamp.from(Instant.now().minus(Duration.ofDays(7)))))
                .pageSize(100)
                .rowMapper(new FailedEventRowMapper())
                .build();
    }
}
```

## Async Job Launcher for Event Processing

```java
@Configuration
public class AsyncJobConfig {

    @Bean
    public JobLauncher asyncJobLauncher(JobRepository jobRepository) {
        TaskExecutorJobLauncher launcher = new TaskExecutorJobLauncher();
        launcher.setJobRepository(jobRepository);
        launcher.setTaskExecutor(new SimpleAsyncTaskExecutor("batch-"));
        return launcher;
    }
}
```

## Idempotency for Event-Triggered Jobs

```java
@Component
public class IdempotentJobLauncher {

    private final JobLauncher jobLauncher;
    private final JobExplorer jobExplorer;

    public JobExecution launchIfNotRunning(Job job, JobParameters params) throws Exception {
        // Check if same job with same params is already running
        List<JobExecution> running = jobExplorer.findRunningJobExecutions(job.getName());

        for (JobExecution exec : running) {
            if (exec.getJobParameters().equals(params)) {
                log.info("Job {} already running with same params, skipping", job.getName());
                return exec;
            }
        }

        return jobLauncher.run(job, params);
    }
}
```

## Key Takeaways

- Kafka listeners + buffer + scheduled flush = reliable micro-batching
- S3/SQS events trigger file processing jobs without polling
- Job chaining via Spring events creates loosely-coupled pipelines
- Dead letter queue reprocessing recovers from transient failures
- Always use async job launcher for event-triggered jobs to avoid blocking
- Idempotency checks prevent duplicate job executions from duplicate events

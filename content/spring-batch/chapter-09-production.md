# Chapter 9: Production

[prev: Scaling](chapter-08-scaling.md) | [Overview](chapter-00-overview.md)

## Scheduling with @Scheduled

Simple scheduling built into Spring:

```java
@Configuration
@EnableScheduling
public class BatchScheduler {

    private final JobLauncher jobLauncher;
    private final Job importJob;

    public BatchScheduler(JobLauncher jobLauncher, Job importJob) {
        this.jobLauncher = jobLauncher;
        this.importJob = importJob;
    }

    @Scheduled(cron = "0 0 2 * * MON-FRI") // 2 AM weekdays
    public void runImport() throws Exception {
        JobParameters params = new JobParametersBuilder()
                .addLong("timestamp", System.currentTimeMillis())
                .addString("date", LocalDate.now().toString())
                .toJobParameters();
        jobLauncher.run(importJob, params);
    }
}
```

## Scheduling with Quartz

For more robust scheduling with persistence, clustering, and misfire handling.

Add dependency:

```groovy
implementation 'org.springframework.boot:spring-boot-starter-quartz'
```

```java
@Configuration
public class QuartzBatchConfig {

    @Bean
    public JobDetail batchJobDetail() {
        return JobBuilder.newJob(BatchJobLauncher.class)
                .withIdentity("importJob")
                .storeDurably()
                .build();
    }

    @Bean
    public Trigger batchJobTrigger() {
        return TriggerBuilder.newTrigger()
                .forJob(batchJobDetail())
                .withIdentity("importTrigger")
                .withSchedule(CronScheduleBuilder.cronSchedule("0 0 2 * * ?"))
                .build();
    }
}

public class BatchJobLauncher extends QuartzJobBean {

    @Autowired
    private JobLauncher jobLauncher;

    @Autowired
    private Job importJob;

    @Override
    protected void executeInternal(JobExecutionContext context) {
        try {
            JobParameters params = new JobParametersBuilder()
                    .addLong("timestamp", System.currentTimeMillis())
                    .toJobParameters();
            jobLauncher.run(importJob, params);
        } catch (Exception e) {
            throw new RuntimeException("Batch job failed", e);
        }
    }
}
```

## Monitoring with Micrometer

Spring Batch 5 integrates with Micrometer for metrics out of the box.

```groovy
implementation 'org.springframework.boot:spring-boot-starter-actuator'
implementation 'io.micrometer:micrometer-registry-prometheus'
```

```properties
management.endpoints.web.exposure.include=health,metrics,prometheus
management.metrics.tags.application=batch-app
```

Available metrics:

- `spring.batch.job` — job execution duration and status
- `spring.batch.job.active` — currently running jobs
- `spring.batch.step` — step execution duration
- `spring.batch.item.read` — items read count
- `spring.batch.item.process` — items processed count
- `spring.batch.chunk.write` — chunk write duration

### Custom Metrics

```java
@Component
public class BatchMetricsListener implements JobExecutionListener {

    private final MeterRegistry meterRegistry;

    public BatchMetricsListener(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
    }

    @Override
    public void afterJob(JobExecution jobExecution) {
        meterRegistry.counter("batch.job.completed",
                "job", jobExecution.getJobInstance().getJobName(),
                "status", jobExecution.getStatus().toString()
        ).increment();
    }
}
```

## Job Parameters

Design parameters for idempotency and traceability:

```java
@Bean
public Job importJob(JobRepository jobRepository, Step importStep) {
    return new JobBuilder("importJob", jobRepository)
            .incrementer(new RunIdIncrementer()) // auto-increment run.id
            .start(importStep)
            .build();
}
```

Custom incrementer for date-based runs:

```java
public class DailyJobParametersIncrementer implements JobParametersIncrementer {

    @Override
    public JobParameters getNext(JobParameters parameters) {
        return new JobParametersBuilder(parameters != null ? parameters : new JobParameters())
                .addString("runDate", LocalDate.now().toString())
                .addLong("runTimestamp", System.currentTimeMillis())
                .toJobParameters();
    }
}
```

## Idempotent Jobs

Ensure a job can be re-run safely without duplicating data:

```java
@Bean
public Step idempotentStep(JobRepository jobRepository,
                           PlatformTransactionManager transactionManager,
                           ItemReader<Person> reader,
                           JdbcBatchItemWriter<PersonDto> writer) {
    // Use UPSERT instead of INSERT
    writer.setSql(
        "INSERT INTO person_output (email, first_name, last_name, age) " +
        "VALUES (:email, :firstName, :lastName, :age) " +
        "ON CONFLICT (email) DO UPDATE SET " +
        "first_name = EXCLUDED.first_name, last_name = EXCLUDED.last_name, age = EXCLUDED.age"
    );

    return new StepBuilder("idempotentStep", jobRepository)
            .<Person, PersonDto>chunk(500, transactionManager)
            .reader(reader)
            .writer(writer)
            .build();
}
```

### Pre-cleanup Pattern

```java
@Bean
public Job idempotentJob(JobRepository jobRepository,
                         Step cleanupStep, Step importStep) {
    return new JobBuilder("idempotentJob", jobRepository)
            .start(cleanupStep)
            .next(importStep)
            .build();
}

@Bean
public Step cleanupStep(JobRepository jobRepository,
                        PlatformTransactionManager transactionManager,
                        JdbcTemplate jdbcTemplate) {
    return new StepBuilder("cleanupStep", jobRepository)
            .tasklet((contribution, chunkContext) -> {
                String runDate = chunkContext.getStepContext()
                        .getJobParameters().get("runDate").toString();
                jdbcTemplate.update("DELETE FROM person_output WHERE run_date = ?", runDate);
                return RepeatStatus.FINISHED;
            }, transactionManager)
            .build();
}
```

## Testing with @SpringBatchTest

```java
@SpringBatchTest
@SpringBootTest
class ImportJobTest {

    @Autowired
    private JobLauncherTestUtils jobLauncherTestUtils;

    @Autowired
    private JobRepositoryTestUtils jobRepositoryTestUtils;

    @BeforeEach
    void cleanup() {
        jobRepositoryTestUtils.removeJobExecutions();
    }

    @Test
    void testFullJob() throws Exception {
        JobParameters params = new JobParametersBuilder()
                .addString("inputFile", "src/test/resources/test-input.csv")
                .toJobParameters();

        JobExecution execution = jobLauncherTestUtils.launchJob(params);

        assertThat(execution.getStatus()).isEqualTo(BatchStatus.COMPLETED);
        assertThat(execution.getStepExecutions()).hasSize(1);

        StepExecution step = execution.getStepExecutions().iterator().next();
        assertThat(step.getReadCount()).isEqualTo(100);
        assertThat(step.getWriteCount()).isEqualTo(95); // 5 filtered
        assertThat(step.getSkipCount()).isEqualTo(0);
    }

    @Test
    void testSingleStep() throws Exception {
        JobExecution execution = jobLauncherTestUtils.launchStep("importStep");
        assertThat(execution.getStatus()).isEqualTo(BatchStatus.COMPLETED);
    }
}
```

Test configuration:

```java
@TestConfiguration
@EnableBatchProcessing
class BatchTestConfig {

    @Bean
    public DataSource dataSource() {
        return new EmbeddedDatabaseBuilder()
                .setType(EmbeddedDatabaseType.H2)
                .addScript("/org/springframework/batch/core/schema-h2.sql")
                .build();
    }
}
```

## Docker Deployment

```dockerfile
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY build/libs/batch-app-1.0.0.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
```

Docker Compose with PostgreSQL:

```yaml
services:
  batch-app:
    build: .
    environment:
      SPRING_PROFILES_ACTIVE: prod
      SPRING_DATASOURCE_URL: jdbc:postgresql://db:5432/batchdb
      SPRING_DATASOURCE_USERNAME: batch_user
      SPRING_DATASOURCE_PASSWORD: secret
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./data:/data

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: batchdb
      POSTGRES_USER: batch_user
      POSTGRES_PASSWORD: secret
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U batch_user -d batchdb"]
      interval: 5s
      timeout: 5s
      retries: 5
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

Build and run:

```bash
./gradlew bootJar
docker compose up --build
```

## Handling Large Files (Millions of Rows)

Key strategies for processing files with millions of records:

### 1. Tune Chunk Size

```java
// For large files, chunk size 1000-5000 is typical
.<Person, PersonDto>chunk(2000, transactionManager)
```

### 2. Use Partitioning

Split the file and process partitions in parallel (see Chapter 8).

### 3. Optimize Database Writes

```properties
# PostgreSQL batch insert optimization
spring.datasource.hikari.maximum-pool-size=20
spring.jpa.properties.hibernate.jdbc.batch_size=50
```

### 4. Memory Management

```java
// Use streaming readers, avoid loading all data into memory
// JdbcCursorItemReader streams one row at a time
// FlatFileItemReader streams one line at a time
```

### 5. JVM Tuning

```bash
java -Xms512m -Xmx2g -XX:+UseG1GC -jar app.jar
```

### Complete Large File Job

```java
@Configuration
public class LargeFileJobConfig {

    @Bean
    public Job largeFileJob(JobRepository jobRepository, Step partitionedStep) {
        return new JobBuilder("largeFileJob", jobRepository)
                .start(partitionedStep)
                .build();
    }

    @Bean
    public Step partitionedStep(JobRepository jobRepository, Step workerStep,
                                Partitioner partitioner) {
        return new StepBuilder("partitionedStep", jobRepository)
                .partitioner("workerStep", partitioner)
                .step(workerStep)
                .gridSize(Runtime.getRuntime().availableProcessors())
                .taskExecutor(batchTaskExecutor())
                .build();
    }

    @Bean
    public Step workerStep(JobRepository jobRepository,
                           PlatformTransactionManager transactionManager,
                           ItemReader<Person> reader,
                           ItemProcessor<Person, PersonDto> processor,
                           JdbcBatchItemWriter<PersonDto> writer) {
        return new StepBuilder("workerStep", jobRepository)
                .<Person, PersonDto>chunk(2000, transactionManager)
                .reader(reader)
                .processor(processor)
                .writer(writer)
                .faultTolerant()
                .skip(FlatFileParseException.class)
                .skipLimit(1000)
                .build();
    }

    @Bean
    public TaskExecutor batchTaskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(Runtime.getRuntime().availableProcessors());
        executor.setMaxPoolSize(Runtime.getRuntime().availableProcessors() * 2);
        executor.setQueueCapacity(10);
        executor.setThreadNamePrefix("batch-worker-");
        executor.initialize();
        return executor;
    }
}
```

## Exercises

1. Set up Micrometer + Prometheus monitoring. Run a job and observe metrics in Prometheus/Grafana.
2. Write a complete test suite for a multi-step job using `@SpringBatchTest`. Test both success and failure scenarios.
3. Dockerize your batch application and run it with PostgreSQL via Docker Compose.
4. Generate a CSV with 1,000,000 rows. Process it using partitioning with 8 workers. Target: complete in under 30 seconds.
5. Make your job idempotent using UPSERT. Run it twice with the same parameters and verify no duplicate data.

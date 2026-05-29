# Chapter 2: Project Setup

[prev: Concepts](chapter-01-concepts.md) | [next: Readers](chapter-03-readers.md)

## Gradle Dependencies

```groovy
plugins {
    id 'java'
    id 'org.springframework.boot' version '3.3.0'
    id 'io.spring.dependency-management' version '1.1.5'
}

group = 'com.example'
version = '1.0.0'

java {
    sourceCompatibility = JavaVersion.VERSION_17
}

repositories {
    mavenCentral()
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-batch'
    implementation 'org.springframework.boot:spring-boot-starter-jdbc'

    runtimeOnly 'com.h2database:h2'
    runtimeOnly 'org.postgresql:postgresql'

    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testImplementation 'org.springframework.batch:spring-batch-test'
}

tasks.named('test') {
    useJUnitPlatform()
}
```

## Spring Boot 3 Auto-Configuration

In Spring Boot 3.3 with Spring Batch 5, `@EnableBatchProcessing` is **no longer required**. Spring Boot auto-configures:

- A `JobRepository` backed by your DataSource
- A `JobLauncher`
- Batch metadata tables (auto-created for embedded databases)

If you add `@EnableBatchProcessing`, it **disables** Boot's auto-configuration — only use it when you need full manual control.

```java
@SpringBootApplication
public class BatchApplication {
    public static void main(String[] args) {
        SpringApplication.run(BatchApplication.class, args);
    }
}
```

## Database Configuration

### H2 (Development)

```properties
# application.properties
spring.datasource.url=jdbc:h2:mem:batchdb
spring.datasource.driver-class-name=org.h2.Driver
spring.batch.jdbc.initialize-schema=always
```

### PostgreSQL (Production)

```properties
# application-prod.properties
spring.datasource.url=jdbc:postgresql://localhost:5432/batchdb
spring.datasource.username=batch_user
spring.datasource.password=secret
spring.batch.jdbc.initialize-schema=never
```

For PostgreSQL, initialize the schema manually using the DDL scripts shipped with Spring Batch (found in `spring-batch-core` JAR under `org/springframework/batch/core/schema-postgresql.sql`).

## First Job: Hello World

```java
package com.example.batch.config;

import org.springframework.batch.core.Job;
import org.springframework.batch.core.Step;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.batch.repeat.RepeatStatus;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.transaction.PlatformTransactionManager;

@Configuration
public class HelloJobConfig {

    @Bean
    public Job helloJob(JobRepository jobRepository, Step helloStep) {
        return new JobBuilder("helloJob", jobRepository)
                .start(helloStep)
                .build();
    }

    @Bean
    public Step helloStep(JobRepository jobRepository,
                          PlatformTransactionManager transactionManager) {
        return new StepBuilder("helloStep", jobRepository)
                .tasklet((contribution, chunkContext) -> {
                    System.out.println("Hello, Spring Batch!");
                    return RepeatStatus.FINISHED;
                }, transactionManager)
                .build();
    }
}
```

Run it:

```bash
./gradlew bootRun
```

Spring Boot auto-launches all defined jobs on startup by default.

## Running Jobs

### Disable Auto-Launch

```properties
spring.batch.job.enabled=false
```

### Option 1: CommandLineRunner

```java
@Component
public class JobRunner implements CommandLineRunner {

    private final JobLauncher jobLauncher;
    private final Job helloJob;

    public JobRunner(JobLauncher jobLauncher, Job helloJob) {
        this.jobLauncher = jobLauncher;
        this.helloJob = helloJob;
    }

    @Override
    public void run(String... args) throws Exception {
        JobParameters params = new JobParametersBuilder()
                .addString("runId", String.valueOf(System.currentTimeMillis()))
                .toJobParameters();
        jobLauncher.run(helloJob, params);
    }
}
```

### Option 2: REST Trigger

```java
@RestController
@RequestMapping("/api/jobs")
public class JobController {

    private final JobLauncher jobLauncher;
    private final Job importJob;

    public JobController(JobLauncher jobLauncher, Job importJob) {
        this.jobLauncher = jobLauncher;
        this.importJob = importJob;
    }

    @PostMapping("/import")
    public ResponseEntity<String> runImport(@RequestParam String inputFile)
            throws Exception {
        JobParameters params = new JobParametersBuilder()
                .addString("inputFile", inputFile)
                .addLong("timestamp", System.currentTimeMillis())
                .toJobParameters();
        JobExecution execution = jobLauncher.run(importJob, params);
        return ResponseEntity.ok("Job started: " + execution.getId());
    }
}
```

Add `spring-boot-starter-web` to dependencies for this approach.

### Option 3: Scheduler

```java
@Configuration
@EnableScheduling
public class ScheduledJobConfig {

    private final JobLauncher jobLauncher;
    private final Job dailyJob;

    public ScheduledJobConfig(JobLauncher jobLauncher, Job dailyJob) {
        this.jobLauncher = jobLauncher;
        this.dailyJob = dailyJob;
    }

    @Scheduled(cron = "0 0 2 * * *") // 2 AM daily
    public void runDailyJob() throws Exception {
        JobParameters params = new JobParametersBuilder()
                .addLong("timestamp", System.currentTimeMillis())
                .toJobParameters();
        jobLauncher.run(dailyJob, params);
    }
}
```

## Project Structure

```
src/main/java/com/example/batch/
  BatchApplication.java
  config/
    HelloJobConfig.java
  model/
    Person.java
  reader/
  processor/
  writer/
src/main/resources/
  application.properties
  application-prod.properties
```

## Exercises

1. Create the project from scratch using the Gradle config above. Run the hello job and verify the output.
2. Switch to PostgreSQL, initialize the schema manually, and confirm job metadata is persisted across restarts.
3. Implement the REST trigger and launch the hello job via `curl -X POST http://localhost:8080/api/jobs/import?inputFile=test.csv`.

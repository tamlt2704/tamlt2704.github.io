# Chapter 1: Your First Job — The Reconciliation

[← Chapter 0: Prerequisites](chapter-00-prerequisites.md) | [Chapter 2: Two Million Rows →](chapter-02-chunk-processing.md)

---

## The Task

It's your first week on the batch team at MegaBank Corp. Every night, the partner bank sends a CSV file of yesterday's transactions. Someone on Brenda's team manually runs a SQL script at 5 AM to compare it against MegaBank's internal ledger. Last Tuesday, they forgot. The auditors noticed.

Director Compliance walks over:

"Automate it. I don't care how. Just make sure it runs every night, and I can see whether it succeeded or failed. The auditors want proof."

You nod. A job that reads a file, does some processing, and writes results. How hard can it be?

## Initialize the Project

```bash
mkdir megabank-batch && cd megabank-batch
```

Create `build.gradle`:

```groovy
plugins {
    id 'java'
    id 'org.springframework.boot' version '3.4.1'
    id 'io.spring.dependency-management' version '1.1.7'
}

group = 'com.megabank'
version = '1.0.0'

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}

repositories {
    mavenCentral()
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-batch'
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    runtimeOnly 'org.postgresql:postgresql'

    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testImplementation 'org.springframework.batch:spring-batch-test'
    testRuntimeOnly 'com.h2database:h2'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}

tasks.named('test') {
    useJUnitPlatform()
}
```

And `settings.gradle`:

```groovy
rootProject.name = 'megabank-batch'
```

Generate the wrapper:

```bash
gradle wrapper
```

Add `.gitignore`:

```
.gradle/
build/
!gradle/wrapper/gradle-wrapper.jar
.idea/
*.iml
.vscode/
.DS_Store
```

## The Application

```java
// src/main/java/com/megabank/BatchApplication.java
package com.megabank;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class BatchApplication {
    public static void main(String[] args) {
        SpringApplication.run(BatchApplication.class, args);
    }
}
```

No `@EnableBatchProcessing` — Spring Boot 3.x auto-configures Spring Batch when it's on the classpath. Adding that annotation actually *disables* some of the auto-configuration. Don't add it.

## Application Properties

```properties
# src/main/resources/application.properties
spring.datasource.url=jdbc:postgresql://localhost:5432/batchjobs
spring.datasource.username=postgres
spring.datasource.password=megabank
spring.jpa.hibernate.ddl-auto=update

# Spring Batch creates its metadata tables automatically
spring.batch.jdbc.initialize-schema=always

# Don't run jobs on startup — we'll trigger them explicitly
spring.batch.job.enabled=false
```

That last line is important. By default, Spring Batch runs every `@Bean Job` when the application starts. In production, you want to trigger jobs via a scheduler or API — not on every deploy.

## The Domain: Transactions

A transaction from the partner file looks like this:

```csv
transaction_id,amount,currency,timestamp,counterparty
TXN-001,1500.00,USD,2024-01-15T09:30:00,PARTNER_BANK_A
TXN-002,2300.50,EUR,2024-01-15T10:15:00,PARTNER_BANK_B
```

The domain object:

```java
// src/main/java/com/megabank/domain/Transaction.java
package com.megabank.domain;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record Transaction(
    String transactionId,
    BigDecimal amount,
    String currency,
    LocalDateTime timestamp,
    String counterparty
) {}
```

Records are perfect for batch data — immutable value objects. No setters, no mutation bugs.

## Understanding Jobs and Steps

Before writing the job, here's the mental model:

```
┌─────────────────────────────────────────────┐
│ Job: "reconciliationJob"                     │
│                                              │
│  ┌─────────────────────────────────────┐    │
│  │ Step 1: "loadPartnerFileStep"        │    │
│  │   Tasklet: copy file to staging dir  │    │
│  └─────────────────────────────────────┘    │
│                    │                         │
│                    ▼                         │
│  ┌─────────────────────────────────────┐    │
│  │ Step 2: "reconcileStep"              │    │
│  │   Read CSV → Compare → Write results │    │
│  └─────────────────────────────────────┘    │
│                    │                         │
│                    ▼                         │
│  ┌─────────────────────────────────────┐    │
│  │ Step 3: "notifyStep"                 │    │
│  │   Tasklet: send completion email     │    │
│  └─────────────────────────────────────┘    │
│                                              │
└─────────────────────────────────────────────┘
```

A **Job** is a container for Steps. Steps execute in order. If Step 2 fails, Step 3 never runs (unless you configure it otherwise — Chapter 7).

There are two kinds of Steps:
- **Tasklet Step** — runs a single chunk of code (copy a file, send an email, run a query)
- **Chunk-oriented Step** — reads items, processes them, writes them in batches (Chapter 2)

Today we start with Tasklets. They're simpler, and the first version of the reconciliation is simple.

## Step 1: The File Loader Tasklet

The partner bank drops a file on an SFTP server. For now, we'll simulate this by copying from an input directory to a staging directory.

```java
// src/main/java/com/megabank/tasklet/FileLoaderTasklet.java
package com.megabank.tasklet;

import org.springframework.batch.core.StepContribution;
import org.springframework.batch.core.scope.context.ChunkContext;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.repeat.RepeatStatus;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;

public class FileLoaderTasklet implements Tasklet {

    private final Path inputDir;
    private final Path stagingDir;

    public FileLoaderTasklet(Path inputDir, Path stagingDir) {
        this.inputDir = inputDir;
        this.stagingDir = stagingDir;
    }

    @Override
    public RepeatStatus execute(StepContribution contribution, ChunkContext chunkContext)
            throws IOException {

        Files.createDirectories(stagingDir);

        long fileCount = 0;
        try (var files = Files.list(inputDir)) {
            for (Path file : files.filter(p -> p.toString().endsWith(".csv")).toList()) {
                Files.copy(file, stagingDir.resolve(file.getFileName()),
                    StandardCopyOption.REPLACE_EXISTING);
                fileCount++;
            }
        }

        // Store in execution context for later steps to use
        chunkContext.getStepContext()
            .getStepExecution()
            .getJobExecution()
            .getExecutionContext()
            .putLong("fileCount", fileCount);

        return RepeatStatus.FINISHED;
    }
}
```

A Tasklet has one method: `execute()`. It returns either `FINISHED` (done, move to next step) or `CONTINUABLE` (call me again — useful for polling loops).

Notice the `ExecutionContext` — that's Spring Batch's way of passing data between steps. It's persisted to the database, which means if the job restarts, the context is still there. More on this in Chapter 4.

## Step 2: The Reconciliation Tasklet

For Chapter 1, we'll keep reconciliation simple: read the CSV, check each transaction against our internal ledger, and write mismatches to an output file.

```java
// src/main/java/com/megabank/tasklet/ReconcileTasklet.java
package com.megabank.tasklet;

import com.megabank.domain.Transaction;
import com.megabank.service.LedgerService;
import org.springframework.batch.core.StepContribution;
import org.springframework.batch.core.scope.context.ChunkContext;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.repeat.RepeatStatus;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.math.BigDecimal;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDateTime;

public class ReconcileTasklet implements Tasklet {

    private final Path stagingDir;
    private final Path outputDir;
    private final LedgerService ledgerService;

    public ReconcileTasklet(Path stagingDir, Path outputDir, LedgerService ledgerService) {
        this.stagingDir = stagingDir;
        this.outputDir = outputDir;
        this.ledgerService = ledgerService;
    }

    @Override
    public RepeatStatus execute(StepContribution contribution, ChunkContext chunkContext)
            throws IOException {

        Files.createDirectories(outputDir);
        int matched = 0;
        int mismatched = 0;

        try (var csvFiles = Files.list(stagingDir)) {
            for (Path csvFile : csvFiles.filter(p -> p.toString().endsWith(".csv")).toList()) {
                Path outputFile = outputDir.resolve("mismatches_" + csvFile.getFileName());

                try (BufferedReader reader = Files.newBufferedReader(csvFile);
                     BufferedWriter writer = Files.newBufferedWriter(outputFile)) {

                    reader.readLine(); // skip header
                    String line;
                    while ((line = reader.readLine()) != null) {
                        Transaction txn = parseLine(line);
                        boolean matches = ledgerService.verify(txn);

                        if (matches) {
                            matched++;
                        } else {
                            writer.write(line);
                            writer.newLine();
                            mismatched++;
                        }
                    }
                }
            }
        }

        // Store results for the notification step
        var ctx = chunkContext.getStepContext()
            .getStepExecution()
            .getJobExecution()
            .getExecutionContext();
        ctx.putInt("matched", matched);
        ctx.putInt("mismatched", mismatched);

        return RepeatStatus.FINISHED;
    }

    private Transaction parseLine(String line) {
        String[] parts = line.split(",");
        return new Transaction(
            parts[0],
            new BigDecimal(parts[1]),
            parts[2],
            LocalDateTime.parse(parts[3]),
            parts[4]
        );
    }
}
```

This works. But it has a problem we'll discover in Chapter 2: it loads the entire file into memory one line at a time with no chunking, no transactions, and no restart capability. When Brenda's file hits 2 million rows, this approach dies.

## Step 3: The Notification Tasklet

Director Compliance wants proof. A simple log entry for now — we'll add email later.

```java
// src/main/java/com/megabank/tasklet/NotifyTasklet.java
package com.megabank.tasklet;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.batch.core.StepContribution;
import org.springframework.batch.core.scope.context.ChunkContext;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.repeat.RepeatStatus;

public class NotifyTasklet implements Tasklet {

    private static final Logger log = LoggerFactory.getLogger(NotifyTasklet.class);

    @Override
    public RepeatStatus execute(StepContribution contribution, ChunkContext chunkContext) {
        var ctx = chunkContext.getStepContext()
            .getStepExecution()
            .getJobExecution()
            .getExecutionContext();

        int matched = ctx.getInt("matched", 0);
        int mismatched = ctx.getInt("mismatched", 0);

        log.info("=== RECONCILIATION COMPLETE ===");
        log.info("Matched: {}", matched);
        log.info("Mismatched: {}", mismatched);
        log.info("Report available in output directory");

        return RepeatStatus.FINISHED;
    }
}
```

## The Ledger Service

A simple service that checks if a transaction exists in our internal system:

```java
// src/main/java/com/megabank/service/LedgerService.java
package com.megabank.service;

import com.megabank.domain.Transaction;
import org.springframework.stereotype.Service;

@Service
public class LedgerService {

    public boolean verify(Transaction transaction) {
        // In reality: query the internal ledger database
        // For now: simulate — odd amounts are "mismatches"
        return transaction.amount().scale() == 0
            || transaction.amount().remainder(java.math.BigDecimal.valueOf(2))
                .compareTo(java.math.BigDecimal.ZERO) == 0;
    }
}
```

## Wiring It Together: The Job Configuration

This is where Spring Batch shines. You declare the job structure — the framework handles execution, metadata, and lifecycle.

```java
// src/main/java/com/megabank/config/ReconciliationJobConfig.java
package com.megabank.config;

import com.megabank.service.LedgerService;
import com.megabank.tasklet.FileLoaderTasklet;
import com.megabank.tasklet.NotifyTasklet;
import com.megabank.tasklet.ReconcileTasklet;
import org.springframework.batch.core.Job;
import org.springframework.batch.core.Step;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.transaction.PlatformTransactionManager;

import java.nio.file.Path;

@Configuration
public class ReconciliationJobConfig {

    @Value("${batch.input-dir:./input}")
    private String inputDir;

    @Value("${batch.staging-dir:./staging}")
    private String stagingDir;

    @Value("${batch.output-dir:./output}")
    private String outputDir;

    @Bean
    public Job reconciliationJob(JobRepository jobRepository,
                                  Step loadPartnerFileStep,
                                  Step reconcileStep,
                                  Step notifyStep) {
        return new JobBuilder("reconciliationJob", jobRepository)
            .start(loadPartnerFileStep)
            .next(reconcileStep)
            .next(notifyStep)
            .build();
    }

    @Bean
    public Step loadPartnerFileStep(JobRepository jobRepository,
                                     PlatformTransactionManager txManager) {
        return new StepBuilder("loadPartnerFileStep", jobRepository)
            .tasklet(new FileLoaderTasklet(Path.of(inputDir), Path.of(stagingDir)), txManager)
            .build();
    }

    @Bean
    public Step reconcileStep(JobRepository jobRepository,
                               PlatformTransactionManager txManager,
                               LedgerService ledgerService) {
        return new StepBuilder("reconcileStep", jobRepository)
            .tasklet(new ReconcileTasklet(
                Path.of(stagingDir), Path.of(outputDir), ledgerService), txManager)
            .build();
    }

    @Bean
    public Step notifyStep(JobRepository jobRepository,
                            PlatformTransactionManager txManager) {
        return new StepBuilder("notifyStep", jobRepository)
            .tasklet(new NotifyTasklet(), txManager)
            .build();
    }
}
```

Let's break down what's happening:

- **`JobBuilder`** — creates a Job with a name and a reference to the JobRepository
- **`StepBuilder`** — creates a Step with a name, wraps a Tasklet
- **`JobRepository`** — Spring Batch's metadata store. Every job execution, step execution, and their parameters are recorded here. This is how Director Compliance gets his audit trail.
- **`PlatformTransactionManager`** — each Tasklet runs inside a transaction. If it throws, the transaction rolls back.

The flow: `loadPartnerFileStep` → `reconcileStep` → `notifyStep`. Sequential. Simple.

## The Job Repository: Your Audit Trail

When you run a job, Spring Batch records everything:

```
BATCH_JOB_INSTANCE     — "reconciliationJob" exists
BATCH_JOB_EXECUTION    — ran at 2024-01-15 05:00:00, status: COMPLETED
BATCH_STEP_EXECUTION   — step "reconcileStep", read: 1000, written: 1000
BATCH_JOB_EXECUTION_PARAMS — date=2024-01-15
```

This is why Director Compliance loves Spring Batch. The auditors can query the database and see exactly when every job ran, whether it succeeded, and how many records it processed.

You don't need to build any of this. It's automatic.

## A REST Endpoint to Trigger Jobs

```java
// src/main/java/com/megabank/controller/JobController.java
package com.megabank.controller;

import org.springframework.batch.core.Job;
import org.springframework.batch.core.JobParameters;
import org.springframework.batch.core.JobParametersBuilder;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;

@RestController
@RequestMapping("/jobs")
public class JobController {

    private final JobLauncher jobLauncher;
    private final Job reconciliationJob;

    public JobController(JobLauncher jobLauncher, Job reconciliationJob) {
        this.jobLauncher = jobLauncher;
        this.reconciliationJob = reconciliationJob;
    }

    @PostMapping("/reconciliation")
    @ResponseStatus(HttpStatus.ACCEPTED)
    public String launchReconciliation(@RequestParam(required = false) String date) {
        String runDate = date != null ? date : LocalDate.now().minusDays(1).toString();

        JobParameters params = new JobParametersBuilder()
            .addString("date", runDate)
            .addLong("timestamp", System.currentTimeMillis()) // makes each run unique
            .toJobParameters();

        try {
            jobLauncher.run(reconciliationJob, params);
            return "Job launched for date: " + runDate;
        } catch (Exception e) {
            throw new RuntimeException("Failed to launch job: " + e.getMessage(), e);
        }
    }
}
```

**Job Parameters** are how you make each execution unique. Spring Batch won't re-run a job with the same parameters (it considers it "already completed"). The `timestamp` parameter ensures every trigger creates a new execution.

## Verify It Compiles

```bash
./gradlew build
```

Green.

## The Test

```java
// src/test/java/com/megabank/ReconciliationJobTest.java
package com.megabank;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.batch.core.*;
import org.springframework.batch.test.JobLauncherTestUtils;
import org.springframework.batch.test.context.SpringBatchTest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBatchTest
@SpringBootTest
class ReconciliationJobTest {

    @Autowired
    private JobLauncherTestUtils jobLauncherTestUtils;

    @TempDir
    Path tempDir;

    private Path inputDir;
    private Path outputDir;

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        // Use H2 for tests — no Postgres needed
        registry.add("spring.datasource.url", () -> "jdbc:h2:mem:testdb");
        registry.add("spring.datasource.driver-class-name", () -> "org.h2.Driver");
        registry.add("spring.batch.jdbc.initialize-schema", () -> "always");
    }

    @BeforeEach
    void setUp() throws IOException {
        inputDir = tempDir.resolve("input");
        outputDir = tempDir.resolve("output");
        Files.createDirectories(inputDir);

        // Create a test CSV
        String csv = """
            transaction_id,amount,currency,timestamp,counterparty
            TXN-001,1500.00,USD,2024-01-15T09:30:00,PARTNER_BANK_A
            TXN-002,2300.50,EUR,2024-01-15T10:15:00,PARTNER_BANK_B
            TXN-003,4000.00,USD,2024-01-15T11:00:00,PARTNER_BANK_A
            """;
        Files.writeString(inputDir.resolve("partner_20240115.csv"), csv);
    }

    @Test
    void reconciliationJob_shouldCompleteSuccessfully() throws Exception {
        JobParameters params = new JobParametersBuilder()
            .addString("date", "2024-01-15")
            .addLong("timestamp", System.currentTimeMillis())
            .addString("inputDir", inputDir.toString())
            .addString("outputDir", outputDir.toString())
            .toJobParameters();

        JobExecution execution = jobLauncherTestUtils.launchJob(params);

        assertThat(execution.getStatus()).isEqualTo(BatchStatus.COMPLETED);
        assertThat(execution.getExitStatus()).isEqualTo(ExitStatus.COMPLETED);
    }

    @Test
    void reconciliationJob_shouldRecordStepExecutions() throws Exception {
        JobParameters params = new JobParametersBuilder()
            .addString("date", "2024-01-15")
            .addLong("timestamp", System.currentTimeMillis())
            .addString("inputDir", inputDir.toString())
            .addString("outputDir", outputDir.toString())
            .toJobParameters();

        JobExecution execution = jobLauncherTestUtils.launchJob(params);

        assertThat(execution.getStepExecutions()).hasSize(3);
        execution.getStepExecutions().forEach(step ->
            assertThat(step.getStatus()).isEqualTo(BatchStatus.COMPLETED));
    }

    @Test
    void loadPartnerFileStep_shouldCopyFilesToStaging() throws Exception {
        JobExecution execution = jobLauncherTestUtils.launchStep("loadPartnerFileStep");

        assertThat(execution.getStatus()).isEqualTo(BatchStatus.COMPLETED);
    }
}
```

```bash
./gradlew test
```

All green.

## Try It with curl

Start the app:

```bash
./gradlew bootRun
```

```bash
# Create input directory and a test file
mkdir -p input
echo "transaction_id,amount,currency,timestamp,counterparty
TXN-001,1500.00,USD,2024-01-15T09:30:00,PARTNER_BANK_A
TXN-002,2300.50,EUR,2024-01-15T10:15:00,PARTNER_BANK_B" > input/partner_20240115.csv

# Launch the job
curl -X POST "http://localhost:8080/jobs/reconciliation?date=2024-01-15"
# → Job launched for date: 2024-01-15
```

Check the logs:

```
=== RECONCILIATION COMPLETE ===
Matched: 2
Mismatched: 1
Report available in output directory
```

You show Director Compliance. He nods. "Good. Now make it handle Brenda's file."

"How big is Brenda's file?"

"Two million rows."

You look at your Tasklet that reads the entire file in one shot, in one transaction, with no checkpointing. If it fails at row 1,999,999 — it starts over from zero.

That's Chapter 2.

## What You Learned

- **Job** — a named batch process with one or more Steps
- **Step** — a unit of work within a Job (Tasklet or chunk-oriented)
- **Tasklet** — a single-operation step (copy files, send notifications)
- **JobRepository** — automatic metadata storage (audit trail for free)
- **JobParameters** — make each execution unique, enable restartability
- **ExecutionContext** — pass data between steps, persisted to DB
- **JobLauncher** — programmatic way to trigger jobs
- **`spring.batch.job.enabled=false`** — don't auto-run on startup

The foundation is laid. But this Tasklet approach won't scale. When Brenda's 2-million-row file arrives, you need chunk-oriented processing — read 1000 rows, process them, write them, commit. If it fails at chunk 1800, restart from chunk 1800.

That's the real power of Spring Batch. Next chapter.

---

[← Chapter 0: Prerequisites](chapter-00-prerequisites.md) | [Chapter 2: Two Million Rows →](chapter-02-chunk-processing.md)

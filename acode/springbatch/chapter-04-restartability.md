# Chapter 4: The Restart — Picking Up Where You Left Off

[← Chapter 3: Garbage In](chapter-03-skip-logic.md) | [Chapter 5: The Retry →](chapter-05-retry-logic.md)

---

## The Incident

Thursday. 5:12 AM. The reconciliation job is humming along — 1.8 million rows processed, 200 chunks left. Then the database connection pool exhausts. PostgreSQL hit its max connections because Index Ivan was running a maintenance query at the same time.

```
org.springframework.dao.DataAccessResourceFailureException:
  Unable to acquire JDBC Connection
```

The job fails. 1,800,000 rows already committed. 200,000 left.

You restart the job. It starts from row 1. Again.

Brenda: "It's 6:45. The markets open in 15 minutes. Why is it reprocessing rows I already reconciled?"

You: "Because the job doesn't know where it stopped."

Brenda: "Make it know."

## The Problem

Your job has no memory. When it restarts, the `FlatFileItemReader` opens the file from the beginning. The writer inserts everything again. You get duplicates in the reconciliation table AND waste 30 minutes reprocessing data that's already committed.

Spring Batch was designed to solve exactly this. The mechanism: **ExecutionContext** + **restartable readers**.

## How Restartability Works

Every time a chunk commits, Spring Batch persists the reader's state to the `BATCH_STEP_EXECUTION_CONTEXT` table:

```
┌─────────────────────────────────────────────────────────┐
│ Chunk 1800 commits                                       │
│                                                           │
│ Step ExecutionContext saved to DB:                        │
│   { "transactionReader.read.count": 1800000 }            │
│                                                           │
└─────────────────────────────────────────────────────────┘
                         │
                    JOB FAILS
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ Job restarts                                             │
│                                                           │
│ Spring Batch reads ExecutionContext from DB:              │
│   { "transactionReader.read.count": 1800000 }            │
│                                                           │
│ Reader opens file, skips to line 1800001                 │
│ Processing resumes from chunk 1801                        │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

This is automatic — IF your reader is restartable and your job is configured correctly.

## The Test: Restart From Failure Point

```java
@Test
void shouldRestartFromLastCommittedChunk_notFromBeginning() throws Exception {
    generateTestCsv(inputPath, 10000); // 10 chunks of 1000

    // First run: simulate failure at chunk 8
    JobParameters params = new JobParametersBuilder()
        .addString("inputFile", inputPath.toString())
        .addString("date", "2024-01-18")
        .toJobParameters();

    // Inject a failure at row 7500
    processor.setFailAtRow(7500);

    JobExecution firstRun = jobLauncherTestUtils.launchJob(params);
    assertThat(firstRun.getStatus()).isEqualTo(BatchStatus.FAILED);

    StepExecution failedStep = firstRun.getStepExecutions().iterator().next();
    assertThat(failedStep.getReadCount()).isEqualTo(7000); // 7 full chunks committed
    assertThat(failedStep.getWriteCount()).isEqualTo(7000);

    // Second run: same parameters = restart (not new execution)
    processor.clearFailure();

    JobExecution secondRun = jobLauncherTestUtils.launchJob(params);
    assertThat(secondRun.getStatus()).isEqualTo(BatchStatus.COMPLETED);

    StepExecution restartedStep = secondRun.getStepExecutions().iterator().next();
    assertThat(restartedStep.getReadCount()).isEqualTo(3000); // only remaining rows!
    assertThat(restartedStep.getWriteCount()).isEqualTo(3000);
}
```

The second run processes only 3,000 rows — not 10,000. It resumed from where it failed.

## The Key: Same Job Parameters = Restart

Spring Batch identifies job instances by **Job name + Job parameters**. If you launch a job with the same parameters as a previously failed execution, it **restarts** that execution instead of creating a new one.

```java
// This creates a NEW job instance (different timestamp)
new JobParametersBuilder()
    .addString("date", "2024-01-18")
    .addLong("timestamp", System.currentTimeMillis()) // ← unique every time!
    .toJobParameters();

// This RESTARTS the failed instance (same parameters)
new JobParametersBuilder()
    .addString("date", "2024-01-18")
    // no timestamp — same params as the failed run
    .toJobParameters();
```

This is why we used `timestamp` in Chapter 1 — to force new instances. For restartable jobs, you want **identifying parameters** (like `date`) without random uniquifiers.

### Job Parameter Types

```java
JobParameters params = new JobParametersBuilder()
    .addString("date", "2024-01-18", true)    // identifying (true = default)
    .addString("runId", uuid, false)           // non-identifying
    .addLong("chunkSize", 1000L, false)        // non-identifying
    .toJobParameters();
```

Only **identifying** parameters determine the job instance. Non-identifying parameters can change between restarts without creating a new instance.

## ExecutionContext: The Job's Memory

The `ExecutionContext` is a key-value map persisted to the database after every chunk. Two scopes:

| Scope | Shared Between | Use Case |
|---|---|---|
| Step ExecutionContext | Chunks within a step | Reader position, running totals |
| Job ExecutionContext | Steps within a job | Pass data between steps |

### Step ExecutionContext (Reader State)

The `FlatFileItemReader` automatically saves its position:

```java
// After chunk 5 commits, the step execution context contains:
{
    "transactionReader.read.count": 5000
}
```

On restart, the reader calls `open(executionContext)` and skips to line 5001.

### Job ExecutionContext (Cross-Step Data)

```java
// In Step 1: save data for Step 2
chunkContext.getStepContext()
    .getStepExecution()
    .getJobExecution()
    .getExecutionContext()
    .putString("partnerFile", "partner_20240118.csv");

// In Step 2: read data from Step 1
String file = chunkContext.getStepContext()
    .getStepExecution()
    .getJobExecution()
    .getExecutionContext()
    .getString("partnerFile");
```

### Custom State in ExecutionContext

Your processor tracks running totals. You want them to survive a restart:

```java
// src/main/java/com/megabank/processor/StatefulProcessor.java
package com.megabank.processor;

import com.megabank.domain.ReconciliationResult;
import com.megabank.domain.TransactionDto;
import org.springframework.batch.core.StepExecution;
import org.springframework.batch.core.annotation.BeforeStep;
import org.springframework.batch.item.ExecutionContext;
import org.springframework.batch.item.ItemProcessor;
import org.springframework.batch.item.ItemStream;
import org.springframework.batch.item.ItemStreamException;

import java.math.BigDecimal;

public class StatefulProcessor
        implements ItemProcessor<TransactionDto, ReconciliationResult>, ItemStream {

    private BigDecimal totalMismatchAmount = BigDecimal.ZERO;
    private int mismatchCount = 0;

    @Override
    public void open(ExecutionContext executionContext) throws ItemStreamException {
        // Restore state on restart
        if (executionContext.containsKey("totalMismatchAmount")) {
            totalMismatchAmount = new BigDecimal(
                executionContext.getString("totalMismatchAmount"));
            mismatchCount = executionContext.getInt("mismatchCount");
        }
    }

    @Override
    public void update(ExecutionContext executionContext) throws ItemStreamException {
        // Save state after each chunk
        executionContext.putString("totalMismatchAmount", totalMismatchAmount.toString());
        executionContext.putInt("mismatchCount", mismatchCount);
    }

    @Override
    public void close() throws ItemStreamException {
        // cleanup if needed
    }

    @Override
    public ReconciliationResult process(TransactionDto item) {
        // ... reconciliation logic ...
        // if mismatch:
        //   totalMismatchAmount = totalMismatchAmount.add(difference);
        //   mismatchCount++;
        return null; // placeholder
    }
}
```

The `ItemStream` interface gives you three hooks:
- **`open()`** — called when the step starts (or restarts). Restore state here.
- **`update()`** — called after every chunk commit. Save state here.
- **`close()`** — called when the step finishes. Cleanup here.

Register it as a stream in the step:

```java
@Bean
public Step reconcileChunkStep(...) {
    return new StepBuilder("reconcileChunkStep", jobRepository)
        .<TransactionDto, ReconciliationResult>chunk(1000, txManager)
        .reader(reader)
        .processor(statefulProcessor)
        .writer(writer)
        .stream(statefulProcessor) // ← register as ItemStream
        .build();
}
```

## Preventing Duplicate Writes on Restart

The reader knows where to resume. But what about the writer? If the job failed mid-chunk (after some items were written but before the commit), those items are rolled back. On restart, the chunk is reprocessed and rewritten. No duplicates.

But what if your writer calls an external API that doesn't support transactions? You need idempotent writes:

```java
// src/main/java/com/megabank/writer/IdempotentWriter.java
package com.megabank.writer;

import com.megabank.domain.ReconciliationResult;
import org.springframework.batch.item.Chunk;
import org.springframework.batch.item.ItemWriter;
import org.springframework.jdbc.core.JdbcTemplate;

public class IdempotentWriter implements ItemWriter<ReconciliationResult> {

    private final JdbcTemplate jdbcTemplate;

    public IdempotentWriter(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @Override
    public void write(Chunk<? extends ReconciliationResult> chunk) {
        String sql = """
            INSERT INTO reconciliation_results
            (transaction_id, partner_amount, ledger_amount, status, reconciled_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT (transaction_id) DO UPDATE SET
                status = EXCLUDED.status,
                reconciled_at = EXCLUDED.reconciled_at
            """;

        for (ReconciliationResult result : chunk) {
            jdbcTemplate.update(sql,
                result.transactionId(),
                result.partnerAmount(),
                result.ledgerAmount(),
                result.status(),
                result.reconciledAt());
        }
    }
}
```

`ON CONFLICT ... DO UPDATE` — if the row already exists (from a previous partial run), update it instead of failing. Idempotent. Safe to retry.

## Configuring Restartability

### Allow Restart (default)

```java
@Bean
public Job reconciliationJob(JobRepository jobRepository, Step reconcileStep) {
    return new JobBuilder("reconciliationJob", jobRepository)
        .start(reconcileStep)
        .build();
    // restartable by default
}
```

### Prevent Restart

Some jobs should never restart — they must run fresh every time:

```java
@Bean
public Job oneTimeImportJob(JobRepository jobRepository, Step importStep) {
    return new JobBuilder("oneTimeImportJob", jobRepository)
        .preventRestart() // ← cannot be restarted
        .start(importStep)
        .build();
}
```

### Allow Restart Limit

```java
@Bean
public Step reconcileStep(...) {
    return new StepBuilder("reconcileStep", jobRepository)
        .<TransactionDto, ReconciliationResult>chunk(1000, txManager)
        .reader(reader)
        .processor(processor)
        .writer(writer)
        .startLimit(3) // ← max 3 attempts, then give up
        .build();
}
```

## The Ghost Job: Stuck Executions

Remember The Ghost Job from Chapter 0? A job that's been STARTED since last Thursday? Here's how it happens:

1. Job starts, status = STARTED
2. JVM crashes (kill -9, OOM, power failure)
3. No graceful shutdown — status never updated
4. Spring Batch sees status = STARTED and refuses to restart ("already running")

The fix: mark abandoned executions.

```java
// src/main/java/com/megabank/service/GhostJobCleaner.java
package com.megabank.service;

import org.springframework.batch.core.*;
import org.springframework.batch.core.explore.JobExplorer;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.time.Duration;
import java.time.Instant;
import java.util.Set;

@Component
public class GhostJobCleaner {

    private final JobExplorer jobExplorer;
    private final JobRepository jobRepository;

    public GhostJobCleaner(JobExplorer jobExplorer, JobRepository jobRepository) {
        this.jobExplorer = jobExplorer;
        this.jobRepository = jobRepository;
    }

    @Scheduled(fixedDelay = 300_000) // every 5 minutes
    public void cleanGhostJobs() {
        Set<JobExecution> running = jobExplorer.findRunningJobExecutions("reconciliationJob");

        for (JobExecution execution : running) {
            Instant lastUpdated = execution.getLastUpdated().toInstant();
            if (Duration.between(lastUpdated, Instant.now()).toMinutes() > 30) {
                execution.setStatus(BatchStatus.FAILED);
                execution.setExitStatus(ExitStatus.FAILED.addExitDescription(
                    "Marked as failed by GhostJobCleaner — no heartbeat for 30 minutes"));
                execution.getStepExecutions().forEach(step -> {
                    if (step.getStatus() == BatchStatus.STARTED) {
                        step.setStatus(BatchStatus.FAILED);
                    }
                });
                jobRepository.update(execution);
            }
        }
    }
}
```

The Ghost Job is exorcised. Again.

## The Test: Full Restart Scenario

```java
@Test
void fullRestartScenario_shouldResumeAndComplete() throws Exception {
    generateTestCsv(inputPath, 50000); // 50 chunks

    JobParameters params = new JobParametersBuilder()
        .addString("date", "2024-01-18")
        .addString("inputFile", inputPath.toString())
        .toJobParameters();

    // Run 1: fail at chunk 30
    processor.setFailAtRow(30000);
    JobExecution run1 = jobLauncherTestUtils.launchJob(params);
    assertThat(run1.getStatus()).isEqualTo(BatchStatus.FAILED);

    StepExecution step1 = run1.getStepExecutions().iterator().next();
    int firstRunWrites = step1.getWriteCount();
    assertThat(firstRunWrites).isGreaterThan(25000); // at least 25 chunks committed

    // Run 2: fail at chunk 45
    processor.setFailAtRow(45000);
    JobExecution run2 = jobLauncherTestUtils.launchJob(params);
    assertThat(run2.getStatus()).isEqualTo(BatchStatus.FAILED);

    StepExecution step2 = run2.getStepExecutions().iterator().next();
    assertThat(step2.getReadCount()).isLessThan(25000); // didn't re-read everything

    // Run 3: complete
    processor.clearFailure();
    JobExecution run3 = jobLauncherTestUtils.launchJob(params);
    assertThat(run3.getStatus()).isEqualTo(BatchStatus.COMPLETED);

    StepExecution step3 = run3.getStepExecutions().iterator().next();
    assertThat(step3.getReadCount()).isLessThan(10000); // only the remaining rows

    // Total across all runs = 50,000
    int totalWrites = step1.getWriteCount() + step2.getWriteCount() + step3.getWriteCount();
    assertThat(totalWrites).isEqualTo(50000);
}
```

Three runs, three failures, zero duplicates, zero lost rows. The job picks up exactly where it left off each time.

## What You Learned

- **Restartability** — Spring Batch resumes from the last committed chunk, not from the beginning
- **ExecutionContext** — persisted state that survives restarts (reader position, custom counters)
- **Job Parameters** — same identifying params = restart; different params = new instance
- **`ItemStream`** — interface for saving/restoring custom state
- **Idempotent writers** — `ON CONFLICT DO UPDATE` prevents duplicates on restart
- **`.preventRestart()`** — for jobs that must always run fresh
- **`.startLimit(n)`** — maximum restart attempts
- **Ghost Job cleanup** — detect and mark abandoned executions
- **Non-identifying parameters** — change config between restarts without creating new instances

The job now survives infrastructure failures gracefully. Database drops? Network blip? JVM crash? Restart and it picks up where it left off.

But what about transient failures that fix themselves? The exchange-rate API returns a 503 for 10 seconds, then recovers. You don't want to fail the entire job and restart manually — you want to retry automatically.

That's Chapter 5.

---

[← Chapter 3: Garbage In](chapter-03-skip-logic.md) | [Chapter 5: The Retry →](chapter-05-retry-logic.md)

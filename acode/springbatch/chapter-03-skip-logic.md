# Chapter 3: Garbage In — Skip Logic and Error Handling

[← Chapter 2: Two Million Rows](chapter-02-chunk-processing.md) | [Chapter 4: The Restart →](chapter-04-restartability.md)

---

## The Incident

Wednesday. 5:47 AM. PagerDuty fires.

**ALERT: reconciliationJob FAILED — Step reconcileChunkStep**

You check the logs:

```
org.springframework.batch.item.file.FlatFileParseException:
  Parsing error at line: 47832 in resource=[file:input/partner_20240116.csv]
  ...
Caused by: java.lang.NumberFormatException: For input string: "N/A"
```

The partner bank sent a file with 50,000 rows where the `amount` field is `"N/A"` instead of a number. Your job processed 47,831 rows successfully, hit the bad row, and died. All progress after the last committed chunk is lost.

Brenda: "So 47,000 rows are done but the other 2 million aren't? And I can't just restart because it'll duplicate the first 47,000?"

You: "..."

Brenda: "Fix it. Bad rows happen every week. The job should skip them and keep going."

## The Problem

Right now, any exception during reading, processing, or writing kills the entire step. One bad row out of 2 million = total failure. That's unacceptable for batch processing where dirty data is the norm, not the exception.

You need:
1. **Skip** — bad rows get logged and skipped, the job continues
2. **Skip limit** — if MORE than N rows are bad, something is seriously wrong, fail the job
3. **Skip listener** — log every skipped item for investigation

## The Test: Bad Rows Should Be Skipped

```java
@Test
void shouldSkipMalformedRows_andContinueProcessing() throws Exception {
    String csv = """
        transaction_id,amount,currency,timestamp,counterparty
        TXN-001,1500.00,USD,2024-01-16T09:30:00,PARTNER_A
        TXN-002,N/A,USD,2024-01-16T09:31:00,PARTNER_A
        TXN-003,2300.50,EUR,2024-01-16T10:15:00,PARTNER_B
        TXN-004,,USD,2024-01-16T10:16:00,PARTNER_B
        TXN-005,4000.00,USD,2024-01-16T11:00:00,PARTNER_A
        """;
    Files.writeString(inputPath, csv);

    JobExecution execution = jobLauncherTestUtils.launchJob(defaultParams());

    assertThat(execution.getStatus()).isEqualTo(BatchStatus.COMPLETED);

    StepExecution step = execution.getStepExecutions().iterator().next();
    assertThat(step.getReadCount()).isEqualTo(3);      // 3 good rows read
    assertThat(step.getReadSkipCount()).isEqualTo(2);  // 2 bad rows skipped
    assertThat(step.getWriteCount()).isEqualTo(3);     // 3 rows written
}

@Test
void shouldFailJob_whenSkipLimitExceeded() throws Exception {
    // Generate file with 60% bad rows — way over our 10% threshold
    generateCsvWithBadRows(inputPath, 1000, 600);

    JobExecution execution = jobLauncherTestUtils.launchJob(defaultParams());

    assertThat(execution.getStatus()).isEqualTo(BatchStatus.FAILED);
    assertThat(execution.getExitStatus().getExitDescription())
        .contains("Skip limit");
}
```

## The Fix: Skip Configuration

```java
@Bean
public Step reconcileChunkStep(JobRepository jobRepository,
                                PlatformTransactionManager txManager,
                                FlatFileItemReader<TransactionDto> reader,
                                ReconciliationProcessor processor,
                                JdbcBatchItemWriter<ReconciliationResult> writer,
                                SkipListener<TransactionDto, ReconciliationResult> skipListener) {
    return new StepBuilder("reconcileChunkStep", jobRepository)
        .<TransactionDto, ReconciliationResult>chunk(1000, txManager)
        .reader(reader)
        .processor(processor)
        .writer(writer)
        .faultTolerant()
        .skipLimit(10000)
        .skip(FlatFileParseException.class)
        .skip(NumberFormatException.class)
        .skip(ValidationException.class)
        .noSkip(DatabaseException.class)  // DB errors = stop immediately
        .listener(skipListener)
        .build();
}
```

The key additions:
- **`.faultTolerant()`** — enables skip/retry capabilities on this step
- **`.skipLimit(10000)`** — skip up to 10,000 bad items. If exceeded, fail the job.
- **`.skip(Exception.class)`** — which exceptions trigger a skip
- **`.noSkip(Exception.class)`** — which exceptions should NEVER be skipped (always fail)

### How Skip Works Internally

When an exception occurs during **reading**:
```
read() → throws FlatFileParseException
  → increment skip count
  → log the error
  → call read() again for the next item
  → continue filling the chunk
```

When an exception occurs during **processing**:
```
process(item) → throws ValidationException
  → increment skip count
  → remove item from chunk
  → continue processing remaining items
```

When an exception occurs during **writing**:
```
write([item1, item2, item3, ...item1000]) → throws Exception
  → ROLLBACK the entire chunk
  → re-process items ONE BY ONE to find the bad one
  → skip the bad item, write the rest
  → COMMIT
```

That last one is important. If writing fails, Spring Batch can't know which item caused it (because they're written as a batch). So it falls back to single-item mode for that chunk — processing and writing each item individually to isolate the failure.

## Custom SkipPolicy: Percentage-Based

A fixed skip limit of 10,000 doesn't scale. If the file has 100 rows and 10 are bad, that's 10% — suspicious. If the file has 2 million rows and 10,000 are bad, that's 0.5% — probably fine.

```java
// src/main/java/com/megabank/policy/PercentageSkipPolicy.java
package com.megabank.policy;

import org.springframework.batch.core.step.skip.SkipPolicy;

public class PercentageSkipPolicy implements SkipPolicy {

    private final double maxSkipPercentage;
    private final int minimumRows;
    private int totalRead = 0;
    private int totalSkipped = 0;

    public PercentageSkipPolicy(double maxSkipPercentage, int minimumRows) {
        this.maxSkipPercentage = maxSkipPercentage;
        this.minimumRows = minimumRows;
    }

    @Override
    public boolean shouldSkip(Throwable t, long skipCount) {
        totalSkipped = (int) skipCount;

        // Always skip if we haven't read enough to judge
        if (totalRead < minimumRows) {
            return true;
        }

        double skipPercentage = (double) totalSkipped / totalRead;
        return skipPercentage <= maxSkipPercentage;
    }

    public void incrementReadCount() {
        totalRead++;
    }
}
```

Wire it in:

```java
.faultTolerant()
.skipPolicy(new PercentageSkipPolicy(0.10, 100)) // max 10% bad rows
.skip(FlatFileParseException.class)
.skip(ValidationException.class)
```

If more than 10% of rows are bad, the file is probably corrupt — fail fast and alert someone.

## The Skip Listener: "What Did We Skip?"

Director Compliance: "You're skipping rows? Which ones? I need a report."

```java
// src/main/java/com/megabank/listener/ReconciliationSkipListener.java
package com.megabank.listener;

import com.megabank.domain.ReconciliationResult;
import com.megabank.domain.TransactionDto;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.batch.core.SkipListener;
import org.springframework.stereotype.Component;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;

@Component
public class ReconciliationSkipListener
        implements SkipListener<TransactionDto, ReconciliationResult> {

    private static final Logger log = LoggerFactory.getLogger(ReconciliationSkipListener.class);
    private final PrintWriter skipLog;

    public ReconciliationSkipListener() throws IOException {
        this.skipLog = new PrintWriter(
            new BufferedWriter(new FileWriter("output/skipped_rows.log", true)));
    }

    @Override
    public void onSkipInRead(Throwable t) {
        log.warn("Skipped during READ: {}", t.getMessage());
        skipLog.println("READ_SKIP|" + t.getMessage());
        skipLog.flush();
    }

    @Override
    public void onSkipInProcess(TransactionDto item, Throwable t) {
        log.warn("Skipped during PROCESS: txn={}, error={}",
            item.getTransactionId(), t.getMessage());
        skipLog.println("PROCESS_SKIP|" + item.getTransactionId() + "|" + t.getMessage());
        skipLog.flush();
    }

    @Override
    public void onSkipInWrite(ReconciliationResult item, Throwable t) {
        log.warn("Skipped during WRITE: txn={}, error={}",
            item.transactionId(), t.getMessage());
        skipLog.println("WRITE_SKIP|" + item.transactionId() + "|" + t.getMessage());
        skipLog.flush();
    }
}
```

Now every skipped row is logged with context. Director Compliance can review the skip log and decide if the partner bank needs a call.

## Validation: Catch Bad Data in the Processor

Instead of letting `NumberFormatException` bubble up from deep in the code, validate explicitly:

```java
// src/main/java/com/megabank/processor/ValidatingProcessor.java
package com.megabank.processor;

import com.megabank.domain.TransactionDto;
import com.megabank.domain.ReconciliationResult;
import org.springframework.batch.item.ItemProcessor;
import org.springframework.batch.item.validator.ValidationException;

import java.math.BigDecimal;

public class ValidatingProcessor implements ItemProcessor<TransactionDto, ReconciliationResult> {

    private final ReconciliationProcessor delegate;

    public ValidatingProcessor(ReconciliationProcessor delegate) {
        this.delegate = delegate;
    }

    @Override
    public ReconciliationResult process(TransactionDto item) throws ValidationException {
        validate(item);
        return delegate.process(item);
    }

    private void validate(TransactionDto item) {
        if (item.getTransactionId() == null || item.getTransactionId().isBlank()) {
            throw new ValidationException("Missing transaction ID");
        }
        if (item.getAmount() == null) {
            throw new ValidationException("Missing amount for txn: " + item.getTransactionId());
        }
        if (item.getAmount().compareTo(BigDecimal.ZERO) < 0) {
            throw new ValidationException(
                "Negative amount for txn: " + item.getTransactionId());
        }
        if (item.getCurrency() == null || item.getCurrency().length() != 3) {
            throw new ValidationException(
                "Invalid currency for txn: " + item.getTransactionId());
        }
    }
}
```

Validation exceptions are clear and actionable. Much better than a raw `NumberFormatException` from somewhere in the stack.

## Composite Processor: Chain Multiple Processors

What if you need validation AND reconciliation AND enrichment? Chain them:

```java
@Bean
public CompositeItemProcessor<TransactionDto, ReconciliationResult> compositeProcessor(
        ValidatingProcessor validator,
        ReconciliationProcessor reconciler) {
    return new CompositeItemProcessorBuilder<TransactionDto, ReconciliationResult>()
        .delegates(List.of(validator, reconciler))
        .build();
}
```

Each processor in the chain receives the output of the previous one. If any returns `null`, the item is filtered. If any throws, the item is skipped (if skip is configured).

## Step Listeners: Before and After

Beyond skip listeners, you can hook into the step lifecycle:

```java
// src/main/java/com/megabank/listener/StepMetricsListener.java
package com.megabank.listener;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.batch.core.ExitStatus;
import org.springframework.batch.core.StepExecution;
import org.springframework.batch.core.StepExecutionListener;
import org.springframework.stereotype.Component;

@Component
public class StepMetricsListener implements StepExecutionListener {

    private static final Logger log = LoggerFactory.getLogger(StepMetricsListener.class);
    private long startTime;

    @Override
    public void beforeStep(StepExecution stepExecution) {
        startTime = System.currentTimeMillis();
        log.info("Starting step: {}", stepExecution.getStepName());
    }

    @Override
    public ExitStatus afterStep(StepExecution stepExecution) {
        long duration = System.currentTimeMillis() - startTime;
        log.info("Step {} completed in {}ms — read: {}, written: {}, skipped: {}",
            stepExecution.getStepName(),
            duration,
            stepExecution.getReadCount(),
            stepExecution.getWriteCount(),
            stepExecution.getSkipCount());

        // Custom exit status based on skip count
        if (stepExecution.getSkipCount() > 0) {
            return new ExitStatus("COMPLETED_WITH_SKIPS");
        }
        return stepExecution.getExitStatus();
    }
}
```

Custom exit statuses let you build conditional flows later (Chapter 7): "if the step completed with skips, run the alert step; otherwise, skip it."

## The Listener Hierarchy

Spring Batch has listeners at every level:

| Listener | Scope | Events |
|---|---|---|
| `JobExecutionListener` | Job | beforeJob, afterJob |
| `StepExecutionListener` | Step | beforeStep, afterStep |
| `ChunkListener` | Chunk | beforeChunk, afterChunk, afterChunkError |
| `ItemReadListener` | Read | beforeRead, afterRead, onReadError |
| `ItemProcessListener` | Process | beforeProcess, afterProcess, onProcessError |
| `ItemWriteListener` | Write | beforeWrite, afterWrite, onWriteError |
| `SkipListener` | Skip | onSkipInRead, onSkipInProcess, onSkipInWrite |

You don't need all of these. But when Admiral Uptime asks "how long does each chunk take?" — `ChunkListener` is your answer.

## The Test: Everything Together

```java
@Test
void fullReconciliation_withBadRows_shouldCompleteAndLogSkips() throws Exception {
    // 10,000 rows: 9,500 good, 300 bad amounts, 200 missing IDs
    generateMixedCsv(inputPath, 10000, 300, 200);

    JobExecution execution = jobLauncherTestUtils.launchJob(defaultParams());

    assertThat(execution.getStatus()).isEqualTo(BatchStatus.COMPLETED);

    StepExecution step = execution.getStepExecutions().iterator().next();
    assertThat(step.getReadCount()).isEqualTo(9700);     // 10000 - 300 parse failures
    assertThat(step.getReadSkipCount()).isEqualTo(300);  // bad amounts during read
    assertThat(step.getProcessSkipCount()).isEqualTo(200); // missing IDs during process
    assertThat(step.getWriteCount()).isEqualTo(9500);    // 9700 - 200 filtered

    // Verify skip log exists and has entries
    Path skipLog = Path.of("output/skipped_rows.log");
    assertThat(Files.exists(skipLog)).isTrue();
    assertThat(Files.lines(skipLog).count()).isEqualTo(500);
}

@Test
void shouldFailGracefully_whenFileIsMostlyCorrupt() throws Exception {
    // 1000 rows, 600 bad — exceeds 10% threshold
    generateMixedCsv(inputPath, 1000, 600, 0);

    JobExecution execution = jobLauncherTestUtils.launchJob(defaultParams());

    assertThat(execution.getStatus()).isEqualTo(BatchStatus.FAILED);
}
```

## What You Learned

- **`.faultTolerant()`** — enables skip and retry on a step
- **`.skip(Exception.class)`** — which exceptions to skip
- **`.noSkip(Exception.class)`** — which exceptions should always fail
- **`.skipLimit(n)`** — maximum skips before failing
- **`SkipPolicy`** — custom logic (percentage-based, time-based, etc.)
- **`SkipListener`** — log every skipped item with context
- **Write-skip isolation** — Spring Batch retries items individually to find the bad one
- **`CompositeItemProcessor`** — chain validation + business logic
- **`StepExecutionListener`** — custom exit statuses for conditional flows
- **Listener hierarchy** — hooks at every level (job, step, chunk, item)

The job now handles dirty data gracefully. 500 bad rows out of 2 million? Skipped, logged, reported. The other 1,999,500 process normally.

But what happens when the job fails at row 1.8 million — not because of bad data, but because the database connection drops? Right now, restarting means processing all 1.8 million rows again. The committed chunks are safe, but Spring Batch needs to know where to resume.

That's restartability. Chapter 4.

---

[← Chapter 2: Two Million Rows](chapter-02-chunk-processing.md) | [Chapter 4: The Restart →](chapter-04-restartability.md)

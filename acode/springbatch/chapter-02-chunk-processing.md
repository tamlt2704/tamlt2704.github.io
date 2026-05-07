# Chapter 2: Two Million Rows — Chunk-Oriented Processing

[← Chapter 1: Your First Job](chapter-01-first-job.md) | [Chapter 3: Garbage In →](chapter-03-skip-logic.md)

---

## The Incident

Tuesday morning. Brenda from Reconciliation sends an email at 6:47 AM:

**Subject: JOB FAILED AGAIN**

"The reconciliation didn't finish. I came in at 6 and it was still running. Then it crashed. Something about memory. I need this done before the markets open at 7."

You check the logs:

```
java.lang.OutOfMemoryError: Java heap space
    at com.megabank.tasklet.ReconcileTasklet.execute(ReconcileTasklet.java:47)
```

The partner file today: **2,147,000 rows**. Your Tasklet tried to process them all in one transaction. The JVM ran out of memory at row ~1.8 million. And because it's a single Tasklet — no checkpointing — if you restart, it starts from row 1.

Two problems:
1. Memory — you can't hold 2M rows in a single transaction
2. Restartability — a failure means starting over

This is exactly what chunk-oriented processing solves.

## The Mental Model

Instead of "read everything, process everything, write everything," chunk processing works like this:

```
┌─────────────────────────────────────────────────────┐
│ Chunk 1 (commit-interval = 1000)                     │
│                                                       │
│  READ 1000 items → PROCESS 1000 items → WRITE 1000  │
│                                                       │
│  ✓ COMMIT                                            │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│ Chunk 2                                              │
│                                                       │
│  READ 1000 items → PROCESS 1000 items → WRITE 1000  │
│                                                       │
│  ✓ COMMIT                                            │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
                       ...
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│ Chunk 2147 (last chunk — 147 items)                  │
│                                                       │
│  READ 147 items → PROCESS 147 items → WRITE 147     │
│                                                       │
│  ✓ COMMIT                                            │
└─────────────────────────────────────────────────────┘
```

Each chunk is its own transaction. If chunk 1800 fails:
- Chunks 1–1799 are already committed — that data is safe
- Only chunk 1800 rolls back
- On restart, Spring Batch knows to resume from chunk 1800

Memory stays flat: you only hold 1000 items at a time, not 2 million.

## The Three Interfaces

Chunk processing has three components:

| Interface | Responsibility | Example |
|---|---|---|
| `ItemReader<T>` | Read one item at a time | Read a line from CSV |
| `ItemProcessor<I, O>` | Transform/filter one item | Validate, enrich, convert |
| `ItemWriter<T>` | Write a batch of items | Insert 1000 rows to DB |

The framework calls `read()` repeatedly until it has `chunk-size` items (or the reader returns `null` meaning EOF). Then it calls `process()` on each item. Then it calls `write()` with the entire chunk. Then it commits.

```
reader.read() → item 1
reader.read() → item 2
...
reader.read() → item 1000
processor.process(item 1) → processed 1
processor.process(item 2) → processed 2
...
processor.process(item 1000) → processed 1000
writer.write([processed 1, processed 2, ..., processed 1000])
COMMIT
```

## The ItemReader: FlatFileItemReader

Spring Batch ships with readers for common sources. For CSV files:

```java
// src/main/java/com/megabank/config/ReconciliationChunkJobConfig.java
package com.megabank.config;

import com.megabank.domain.Transaction;
import org.springframework.batch.item.file.FlatFileItemReader;
import org.springframework.batch.item.file.builder.FlatFileItemReaderBuilder;
import org.springframework.batch.item.file.mapping.BeanWrapperFieldSetMapper;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.FileSystemResource;

@Configuration
public class ReconciliationChunkJobConfig {

    @Bean
    public FlatFileItemReader<Transaction> transactionReader() {
        return new FlatFileItemReaderBuilder<Transaction>()
            .name("transactionReader")
            .resource(new FileSystemResource("input/partner_transactions.csv"))
            .linesToSkip(1) // skip header
            .delimited()
            .names("transactionId", "amount", "currency", "timestamp", "counterparty")
            .targetType(Transaction.class)
            .build();
    }
}
```

Wait — `Transaction` is a record. `BeanWrapperFieldSetMapper` needs setters. We need a mutable DTO for the reader, then convert to our immutable record in the processor.

```java
// src/main/java/com/megabank/domain/TransactionDto.java
package com.megabank.domain;

import java.math.BigDecimal;

public class TransactionDto {
    private String transactionId;
    private BigDecimal amount;
    private String currency;
    private String timestamp;
    private String counterparty;

    // Getters and setters
    public String getTransactionId() { return transactionId; }
    public void setTransactionId(String id) { this.transactionId = id; }
    public BigDecimal getAmount() { return amount; }
    public void setAmount(BigDecimal amount) { this.amount = amount; }
    public String getCurrency() { return currency; }
    public void setCurrency(String currency) { this.currency = currency; }
    public String getTimestamp() { return timestamp; }
    public void setTimestamp(String timestamp) { this.timestamp = timestamp; }
    public String getCounterparty() { return counterparty; }
    public void setCounterparty(String counterparty) { this.counterparty = counterparty; }
}
```

Updated reader:

```java
@Bean
public FlatFileItemReader<TransactionDto> transactionReader() {
    return new FlatFileItemReaderBuilder<TransactionDto>()
        .name("transactionReader")
        .resource(new FileSystemResource("input/partner_transactions.csv"))
        .linesToSkip(1)
        .delimited()
        .names("transactionId", "amount", "currency", "timestamp", "counterparty")
        .targetType(TransactionDto.class)
        .build();
}
```

The reader is **stateful** — it tracks which line it's on. Spring Batch persists this position in the `ExecutionContext`. If the job restarts, the reader picks up where it left off. This is the magic of restartability.

## The ItemProcessor: Reconciliation Logic

The processor takes a `TransactionDto`, validates it against the ledger, and produces a `ReconciliationResult`:

```java
// src/main/java/com/megabank/domain/ReconciliationResult.java
package com.megabank.domain;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record ReconciliationResult(
    String transactionId,
    BigDecimal partnerAmount,
    BigDecimal ledgerAmount,
    String status, // MATCHED, MISMATCHED, MISSING
    LocalDateTime reconciledAt
) {}
```

```java
// src/main/java/com/megabank/processor/ReconciliationProcessor.java
package com.megabank.processor;

import com.megabank.domain.ReconciliationResult;
import com.megabank.domain.TransactionDto;
import com.megabank.service.LedgerService;
import org.springframework.batch.item.ItemProcessor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public class ReconciliationProcessor implements ItemProcessor<TransactionDto, ReconciliationResult> {

    private final LedgerService ledgerService;

    public ReconciliationProcessor(LedgerService ledgerService) {
        this.ledgerService = ledgerService;
    }

    @Override
    public ReconciliationResult process(TransactionDto item) {
        BigDecimal ledgerAmount = ledgerService.findAmount(item.getTransactionId());

        if (ledgerAmount == null) {
            return new ReconciliationResult(
                item.getTransactionId(),
                item.getAmount(),
                null,
                "MISSING",
                LocalDateTime.now()
            );
        }

        String status = item.getAmount().compareTo(ledgerAmount) == 0
            ? "MATCHED"
            : "MISMATCHED";

        return new ReconciliationResult(
            item.getTransactionId(),
            item.getAmount(),
            ledgerAmount,
            status,
            LocalDateTime.now()
        );
    }
}
```

Key rule: if `process()` returns `null`, the item is **filtered out** — it won't be passed to the writer. This is useful for "only write mismatches":

```java
@Override
public ReconciliationResult process(TransactionDto item) {
    // ... reconciliation logic ...

    // Only write mismatches — matched items are filtered out
    if ("MATCHED".equals(status)) {
        return null; // filtered!
    }

    return new ReconciliationResult(...);
}
```

## The ItemWriter: Database Writer

Write reconciliation results to a database table:

```java
// src/main/java/com/megabank/writer/ReconciliationWriter.java
package com.megabank.writer;

import com.megabank.domain.ReconciliationResult;
import org.springframework.batch.item.Chunk;
import org.springframework.batch.item.ItemWriter;
import org.springframework.jdbc.core.JdbcTemplate;

public class ReconciliationWriter implements ItemWriter<ReconciliationResult> {

    private final JdbcTemplate jdbcTemplate;

    public ReconciliationWriter(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @Override
    public void write(Chunk<? extends ReconciliationResult> chunk) {
        String sql = """
            INSERT INTO reconciliation_results
            (transaction_id, partner_amount, ledger_amount, status, reconciled_at)
            VALUES (?, ?, ?, ?, ?)
            """;

        for (ReconciliationResult result : chunk) {
            jdbcTemplate.update(sql,
                result.transactionId(),
                result.partnerAmount(),
                result.ledgerAmount(),
                result.status(),
                result.reconciledAt()
            );
        }
    }
}
```

Notice: `write()` receives a `Chunk` — a list of items. This is where you batch your database inserts. One `INSERT` per item is fine for now, but for 2 million rows you'd want `JdbcBatchItemWriter` (which uses JDBC batch operations under the hood):

```java
@Bean
public JdbcBatchItemWriter<ReconciliationResult> reconciliationWriter(DataSource dataSource) {
    return new JdbcBatchItemWriterBuilder<ReconciliationResult>()
        .sql("""
            INSERT INTO reconciliation_results
            (transaction_id, partner_amount, ledger_amount, status, reconciled_at)
            VALUES (:transactionId, :partnerAmount, :ledgerAmount, :status, :reconciledAt)
            """)
        .dataSource(dataSource)
        .beanMapped()
        .build();
}
```

`JdbcBatchItemWriter` uses named parameters and JDBC batching — one round-trip to the database for the entire chunk instead of 1000 individual inserts. Index Ivan approves.

## Wiring the Chunk Step

```java
@Bean
public Job reconciliationJob(JobRepository jobRepository,
                              Step reconcileChunkStep) {
    return new JobBuilder("reconciliationJob", jobRepository)
        .start(reconcileChunkStep)
        .build();
}

@Bean
public Step reconcileChunkStep(JobRepository jobRepository,
                                PlatformTransactionManager txManager,
                                FlatFileItemReader<TransactionDto> reader,
                                ReconciliationProcessor processor,
                                JdbcBatchItemWriter<ReconciliationResult> writer) {
    return new StepBuilder("reconcileChunkStep", jobRepository)
        .<TransactionDto, ReconciliationResult>chunk(1000, txManager)
        .reader(reader)
        .processor(processor)
        .writer(writer)
        .build();
}
```

The magic number: `chunk(1000, txManager)`. This means:
- Read 1000 items
- Process all 1000
- Write all 1000
- Commit the transaction
- Repeat

Why 1000? It's a balance:
- Too small (10): too many commits, slow
- Too large (100,000): too much memory, long transactions
- 1000: sweet spot for most file-to-database jobs

You can tune it. Index Ivan will have opinions.

## The Test: 2 Million Rows in Chunks

```java
@Test
void chunkProcessing_shouldHandle2MillionRows() throws Exception {
    // Generate a 2M-row test file
    generateTestCsv(inputPath, 2_000_000);

    JobParameters params = new JobParametersBuilder()
        .addString("inputFile", inputPath.toString())
        .addLong("timestamp", System.currentTimeMillis())
        .toJobParameters();

    JobExecution execution = jobLauncherTestUtils.launchJob(params);

    assertThat(execution.getStatus()).isEqualTo(BatchStatus.COMPLETED);

    // Verify all rows were processed
    StepExecution stepExecution = execution.getStepExecutions().iterator().next();
    assertThat(stepExecution.getReadCount()).isEqualTo(2_000_000);
    assertThat(stepExecution.getWriteCount()).isGreaterThan(0);
}

@Test
void chunkProcessing_shouldNotExceedMemoryLimit() throws Exception {
    generateTestCsv(inputPath, 2_000_000);

    Runtime runtime = Runtime.getRuntime();
    long memBefore = runtime.totalMemory() - runtime.freeMemory();

    jobLauncherTestUtils.launchJob(defaultParams());

    long memAfter = runtime.totalMemory() - runtime.freeMemory();
    long memUsed = memAfter - memBefore;

    // Should use less than 200MB regardless of file size
    assertThat(memUsed).isLessThan(200 * 1024 * 1024);
}
```

The first test passes. 2 million rows, processed in chunks of 1000, committed 2000 times. Memory stays flat. Brenda's file finishes in 4 minutes instead of crashing.

## Built-in Readers and Writers

Spring Batch ships with readers/writers for common sources. Don't reinvent these:

### Readers

| Reader | Source |
|---|---|
| `FlatFileItemReader` | CSV, fixed-width, delimited files |
| `JdbcCursorItemReader` | Database via JDBC cursor |
| `JdbcPagingItemReader` | Database via paged queries |
| `JpaPagingItemReader` | Database via JPA |
| `JsonItemReader` | JSON files |
| `StaxEventItemReader` | XML files |
| `KafkaItemReader` | Kafka topics |

### Writers

| Writer | Destination |
|---|---|
| `FlatFileItemWriter` | CSV/text files |
| `JdbcBatchItemWriter` | Database via JDBC batch |
| `JpaItemWriter` | Database via JPA |
| `JsonFileItemWriter` | JSON files |
| `KafkaItemWriter` | Kafka topics |
| `CompositeItemWriter` | Multiple writers (fan-out) |

### Example: Database-to-Database

```java
@Bean
public JdbcCursorItemReader<TransactionDto> dbReader(DataSource dataSource) {
    return new JdbcCursorItemReaderBuilder<TransactionDto>()
        .name("transactionDbReader")
        .dataSource(dataSource)
        .sql("SELECT * FROM partner_transactions WHERE recon_date = ?")
        .preparedStatementSetter(ps -> ps.setDate(1, Date.valueOf(reconDate)))
        .rowMapper((rs, rowNum) -> {
            TransactionDto dto = new TransactionDto();
            dto.setTransactionId(rs.getString("transaction_id"));
            dto.setAmount(rs.getBigDecimal("amount"));
            dto.setCurrency(rs.getString("currency"));
            return dto;
        })
        .build();
}
```

### Example: Write to Multiple Destinations

```java
@Bean
public CompositeItemWriter<ReconciliationResult> compositeWriter(
        JdbcBatchItemWriter<ReconciliationResult> dbWriter,
        FlatFileItemWriter<ReconciliationResult> fileWriter) {
    return new CompositeItemWriterBuilder<ReconciliationResult>()
        .delegates(List.of(dbWriter, fileWriter))
        .build();
}
```

Write to the database AND a file. Both happen in the same transaction — if either fails, both roll back.

## Chunk Size Tuning

Admiral Uptime wants the job to finish faster. You experiment:

| Chunk Size | Time (2M rows) | Memory | DB Round-trips |
|---|---|---|---|
| 100 | 12 min | 15 MB | 20,000 |
| 1,000 | 4 min | 45 MB | 2,000 |
| 5,000 | 3.5 min | 180 MB | 400 |
| 10,000 | 3.2 min | 350 MB | 200 |
| 50,000 | OOM 💀 | — | — |

The sweet spot depends on your item size and available memory. Start at 1000, measure, adjust.

## The Execution Metadata

After the job runs, query the batch tables:

```sql
SELECT job_instance_id, job_name, status, start_time, end_time
FROM batch_job_execution
ORDER BY start_time DESC;
```

```
| job_instance_id | job_name          | status    | start_time          | end_time            |
|-----------------|-------------------|-----------|---------------------|---------------------|
| 42              | reconciliationJob | COMPLETED | 2024-01-15 05:00:01 | 2024-01-15 05:04:23 |
| 41              | reconciliationJob | FAILED    | 2024-01-14 05:00:01 | 2024-01-14 05:38:47 |
```

```sql
SELECT step_name, read_count, write_count, commit_count, status
FROM batch_step_execution
WHERE job_execution_id = 42;
```

```
| step_name         | read_count | write_count | commit_count | status    |
|-------------------|------------|-------------|--------------|-----------|
| reconcileChunkStep| 2147000    | 2147000     | 2148         | COMPLETED |
```

2148 commits = 2147 full chunks of 1000 + 1 partial chunk. Every chunk committed independently. Director Compliance can see exactly how many records were processed.

## What You Learned

- **Chunk-oriented processing** — read N, process N, write N, commit. Repeat.
- **`ItemReader`** — reads one item at a time, stateful (tracks position)
- **`ItemProcessor`** — transforms one item, return `null` to filter
- **`ItemWriter`** — writes a batch of items in one transaction
- **`FlatFileItemReader`** — built-in CSV/delimited file reader
- **`JdbcBatchItemWriter`** — efficient batch inserts via JDBC
- **`CompositeItemWriter`** — write to multiple destinations
- **Chunk size tuning** — balance between speed, memory, and transaction size
- **Execution metadata** — read/write/commit counts tracked automatically

The 2-million-row file now processes in 4 minutes with flat memory usage. Brenda is happy. For now.

But next week, the partner bank sends a file with 50,000 malformed rows — bad dates, negative amounts, missing fields. Your job crashes on the first bad row and all 2 million rows need reprocessing.

You need skip logic.

---

[← Chapter 1: Your First Job](chapter-01-first-job.md) | [Chapter 3: Garbage In →](chapter-03-skip-logic.md)

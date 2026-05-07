# Chapter 6: The Deadline — Partitioning and Parallel Processing

[← Chapter 5: The Retry](chapter-05-retry-logic.md) | [Chapter 7: The Pipeline →](chapter-07-job-orchestration.md)

---

## The Incident

Monday. The partner file arrives at 5:52 AM. The reconciliation job takes 4 minutes. Markets open at 6:00 AM. Brenda needs the results before open.

5:52 + 4 minutes = 5:56. Four-minute margin. Fine.

Then the partner bank adds a new data feed. The file grows to 5 million rows. Processing time: 11 minutes. 5:52 + 11 = 6:03 AM. Three minutes late.

Admiral Uptime: "The reconciliation missed the window. This cannot happen again."

Brenda: "I have 8 CPU cores sitting idle. Why is only one doing the work?"

She's right. Your single-threaded step reads one row at a time, processes one row at a time. Seven cores are watching.

## Three Ways to Go Faster

Spring Batch offers three parallelism strategies:

| Strategy | How It Works | Best For |
|---|---|---|
| Multi-threaded Step | Multiple threads share one reader | Simple speedup, thread-safe reader |
| Partitioning | Split input into partitions, each gets its own step | Large files, database ranges |
| Parallel Flows | Run independent steps simultaneously | Steps with no dependencies |

We'll use all three. But partitioning is the big one.

## Strategy 1: Multi-Threaded Step

The simplest approach: add a `TaskExecutor` to the step. Multiple threads pull from the same reader.

```java
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
        .taskExecutor(new SimpleAsyncTaskExecutor())
        .throttleLimit(4) // max 4 concurrent threads
        .build();
}
```

**Problem:** `FlatFileItemReader` is NOT thread-safe. Two threads calling `read()` simultaneously will get interleaved lines. Corrupted data.

**Fix:** Wrap it in a `SynchronizedItemStreamReader`:

```java
@Bean
public SynchronizedItemStreamReader<TransactionDto> synchronizedReader(
        FlatFileItemReader<TransactionDto> reader) {
    SynchronizedItemStreamReader<TransactionDto> syncReader = new SynchronizedItemStreamReader<>();
    syncReader.setDelegate(reader);
    return syncReader;
}
```

This works but has a bottleneck: the reader is synchronized, so threads queue up waiting to read. You get maybe 2x speedup, not 4x.

**Bigger problem:** `SynchronizedItemStreamReader` is NOT restartable. The synchronized wrapper can't track per-thread read positions. If the job fails, you restart from the beginning.

For simple jobs where restartability isn't critical, multi-threaded steps are fine. For Brenda's 5-million-row reconciliation? We need partitioning.

## Strategy 2: Partitioning

Partitioning splits the input into independent chunks, each processed by its own step instance with its own reader. No shared state, no synchronization, full restartability.

```
┌─────────────────────────────────────────────────────────┐
│ Manager Step (partitioner)                               │
│                                                           │
│  "Split 5M rows into 5 partitions of 1M each"           │
│                                                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                │
│  │Partition 1│ │Partition 2│ │Partition 3│  ...           │
│  │ rows 0-1M │ │rows 1M-2M│ │rows 2M-3M│               │
│  │ (thread 1)│ │(thread 2) │ │(thread 3) │              │
│  └──────────┘ └──────────┘ └──────────┘                │
│                                                           │
│  Each partition has its OWN reader, processor, writer    │
│  Each partition has its OWN ExecutionContext             │
│  Each partition is independently restartable             │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### The Partitioner

The partitioner decides how to split the work:

```java
// src/main/java/com/megabank/partition/FilePartitioner.java
package com.megabank.partition;

import org.springframework.batch.core.partition.support.Partitioner;
import org.springframework.batch.item.ExecutionContext;

import java.util.HashMap;
import java.util.Map;

public class FilePartitioner implements Partitioner {

    private final String filePath;
    private final int totalLines;

    public FilePartitioner(String filePath, int totalLines) {
        this.filePath = filePath;
        this.totalLines = totalLines;
    }

    @Override
    public Map<String, ExecutionContext> partition(int gridSize) {
        Map<String, ExecutionContext> partitions = new HashMap<>();
        int linesPerPartition = totalLines / gridSize;
        int remainder = totalLines % gridSize;

        int start = 0;
        for (int i = 0; i < gridSize; i++) {
            ExecutionContext context = new ExecutionContext();
            context.putString("filePath", filePath);
            context.putInt("startLine", start);

            int size = linesPerPartition + (i < remainder ? 1 : 0);
            context.putInt("endLine", start + size);

            partitions.put("partition" + i, context);
            start += size;
        }

        return partitions;
    }
}
```

Each partition gets its own `ExecutionContext` with `startLine` and `endLine`. The reader for each partition only reads its assigned range.

### The Partitioned Reader

```java
@Bean
@StepScope
public FlatFileItemReader<TransactionDto> partitionedReader(
        @Value("#{stepExecutionContext['filePath']}") String filePath,
        @Value("#{stepExecutionContext['startLine']}") int startLine,
        @Value("#{stepExecutionContext['endLine']}") int endLine) {

    return new FlatFileItemReaderBuilder<TransactionDto>()
        .name("partitionedTransactionReader")
        .resource(new FileSystemResource(filePath))
        .linesToSkip(startLine + 1) // +1 for header
        .maxItemCount(endLine - startLine)
        .delimited()
        .names("transactionId", "amount", "currency", "timestamp", "counterparty")
        .targetType(TransactionDto.class)
        .build();
}
```

**`@StepScope`** is critical. It means a new reader instance is created for each partition (each step execution). Without it, all partitions would share one reader — disaster.

### The Partitioned Step

```java
@Bean
public Step managerStep(JobRepository jobRepository,
                         Step workerStep,
                         Partitioner partitioner) {
    return new StepBuilder("managerStep", jobRepository)
        .partitioner("workerStep", partitioner)
        .step(workerStep)
        .gridSize(8) // 8 partitions
        .taskExecutor(partitionTaskExecutor())
        .build();
}

@Bean
public Step workerStep(JobRepository jobRepository,
                        PlatformTransactionManager txManager,
                        FlatFileItemReader<TransactionDto> reader,
                        ReconciliationProcessor processor,
                        JdbcBatchItemWriter<ReconciliationResult> writer) {
    return new StepBuilder("workerStep", jobRepository)
        .<TransactionDto, ReconciliationResult>chunk(1000, txManager)
        .reader(reader)
        .processor(processor)
        .writer(writer)
        .faultTolerant()
        .skipLimit(1000)
        .skip(ValidationException.class)
        .retryLimit(3)
        .retry(HttpServerErrorException.class)
        .build();
}

@Bean
public TaskExecutor partitionTaskExecutor() {
    ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
    executor.setCorePoolSize(8);
    executor.setMaxPoolSize(8);
    executor.setQueueCapacity(0);
    executor.setThreadNamePrefix("partition-");
    executor.initialize();
    return executor;
}
```

### The Job

```java
@Bean
public Job reconciliationJob(JobRepository jobRepository, Step managerStep) {
    return new JobBuilder("reconciliationJob", jobRepository)
        .start(managerStep)
        .build();
}
```

### Performance

| Approach | 5M rows | Threads | Time |
|---|---|---|---|
| Single-threaded | 5,000,000 | 1 | 11 min |
| Multi-threaded (4) | 5,000,000 | 4 | ~6 min |
| Partitioned (8) | 5,000,000 | 8 | ~1.5 min |

Partitioning with 8 threads: 1.5 minutes. Well within the 6 AM deadline.

## Database Partitioning

Files aren't the only thing you can partition. For database-to-database jobs, partition by ID range:

```java
// src/main/java/com/megabank/partition/DatabasePartitioner.java
package com.megabank.partition;

import org.springframework.batch.core.partition.support.Partitioner;
import org.springframework.batch.item.ExecutionContext;
import org.springframework.jdbc.core.JdbcTemplate;

import java.util.HashMap;
import java.util.Map;

public class DatabasePartitioner implements Partitioner {

    private final JdbcTemplate jdbcTemplate;
    private final String table;

    public DatabasePartitioner(JdbcTemplate jdbcTemplate, String table) {
        this.jdbcTemplate = jdbcTemplate;
        this.table = table;
    }

    @Override
    public Map<String, ExecutionContext> partition(int gridSize) {
        Long min = jdbcTemplate.queryForObject(
            "SELECT MIN(id) FROM " + table, Long.class);
        Long max = jdbcTemplate.queryForObject(
            "SELECT MAX(id) FROM " + table, Long.class);

        if (min == null || max == null) return Map.of();

        long range = (max - min) / gridSize + 1;
        Map<String, ExecutionContext> partitions = new HashMap<>();

        for (int i = 0; i < gridSize; i++) {
            ExecutionContext ctx = new ExecutionContext();
            ctx.putLong("minId", min + (i * range));
            ctx.putLong("maxId", min + ((i + 1) * range) - 1);
            partitions.put("partition" + i, ctx);
        }

        return partitions;
    }
}
```

```java
@Bean
@StepScope
public JdbcPagingItemReader<TransactionDto> partitionedDbReader(
        DataSource dataSource,
        @Value("#{stepExecutionContext['minId']}") Long minId,
        @Value("#{stepExecutionContext['maxId']}") Long maxId) {

    Map<String, Order> sortKeys = Map.of("id", Order.ASCENDING);

    return new JdbcPagingItemReaderBuilder<TransactionDto>()
        .name("partitionedDbReader")
        .dataSource(dataSource)
        .selectClause("SELECT *")
        .fromClause("FROM partner_transactions")
        .whereClause("WHERE id >= :minId AND id <= :maxId")
        .parameterValues(Map.of("minId", minId, "maxId", maxId))
        .sortKeys(sortKeys)
        .pageSize(1000)
        .rowMapper(transactionRowMapper())
        .build();
}
```

Index Ivan approves: each partition queries a non-overlapping ID range. No lock contention. The database index on `id` makes each query fast.

## Strategy 3: Parallel Flows

Some steps are independent — they can run simultaneously:

```java
@Bean
public Job monthEndJob(JobRepository jobRepository,
                        Flow reconciliationFlow,
                        Flow reportGenerationFlow,
                        Step notifyStep) {
    return new JobBuilder("monthEndJob", jobRepository)
        .start(parallelFlows(reconciliationFlow, reportGenerationFlow))
        .next(notifyStep) // runs after BOTH flows complete
        .build();
}

private Flow parallelFlows(Flow... flows) {
    FlowBuilder<SimpleFlow> builder = new FlowBuilder<>("parallelFlows");
    SimpleAsyncTaskExecutor executor = new SimpleAsyncTaskExecutor();

    builder.split(executor).add(flows);
    return builder.build();
}

@Bean
public Flow reconciliationFlow(Step reconcileStep) {
    return new FlowBuilder<SimpleFlow>("reconciliationFlow")
        .start(reconcileStep)
        .build();
}

@Bean
public Flow reportGenerationFlow(Step generateReportStep) {
    return new FlowBuilder<SimpleFlow>("reportGenerationFlow")
        .start(generateReportStep)
        .build();
}
```

Reconciliation and report generation run in parallel. The notification step waits for both to finish.

## The Test: Partitioning Performance

```java
@Test
void partitionedJob_shouldProcessFasterThanSingleThreaded() throws Exception {
    generateTestCsv(inputPath, 100_000); // 100K rows

    // Single-threaded baseline
    long singleStart = System.currentTimeMillis();
    jobLauncherTestUtils.launchJob(singleThreadParams());
    long singleDuration = System.currentTimeMillis() - singleStart;

    // Partitioned (8 threads)
    long partStart = System.currentTimeMillis();
    jobLauncherTestUtils.launchJob(partitionedParams());
    long partDuration = System.currentTimeMillis() - partStart;

    // Should be at least 3x faster with 8 partitions
    assertThat(partDuration).isLessThan(singleDuration / 3);
}

@Test
void partitionedJob_shouldBeRestartable() throws Exception {
    generateTestCsv(inputPath, 50_000);

    // Fail partition 3 at row 5000
    processor.setFailForPartition("partition3", 5000);

    JobExecution run1 = jobLauncherTestUtils.launchJob(defaultParams());
    assertThat(run1.getStatus()).isEqualTo(BatchStatus.FAILED);

    // Partitions 0-2, 4-7 completed. Only partition 3 needs restart.
    processor.clearFailure();
    JobExecution run2 = jobLauncherTestUtils.launchJob(defaultParams());
    assertThat(run2.getStatus()).isEqualTo(BatchStatus.COMPLETED);

    // Only partition 3 was re-executed
    long reprocessed = run2.getStepExecutions().stream()
        .filter(s -> s.getStepName().contains("partition3"))
        .mapToLong(StepExecution::getReadCount)
        .sum();
    assertThat(reprocessed).isLessThan(10000); // only partition 3's remaining rows
}
```

Key insight: when a partitioned job restarts, only the **failed partitions** re-execute. The completed partitions are skipped. This is why partitioning is superior to multi-threaded steps for restartability.

## Choosing Grid Size

| Factor | Guidance |
|---|---|
| CPU cores | gridSize ≤ available cores (no benefit beyond this for CPU-bound work) |
| I/O bound | gridSize can exceed cores (threads wait on I/O, not CPU) |
| DB connections | gridSize ≤ connection pool size (each partition needs a connection) |
| Memory | Each partition holds chunk-size items in memory |
| Diminishing returns | Beyond 8-16 partitions, overhead outweighs benefit |

For Brenda's reconciliation (I/O bound — file reads + DB writes):
- 8 cores, 20 DB connections → gridSize = 8 is optimal
- Each partition: 625K rows, ~1.5 min
- Total: ~1.5 min (limited by slowest partition)

## What You Learned

- **Multi-threaded Step** — simple but loses restartability, reader must be thread-safe
- **Partitioning** — splits work into independent step instances, fully restartable
- **`Partitioner`** — decides how to split (by line range, ID range, file, etc.)
- **`@StepScope`** — creates new bean instances per step execution (per partition)
- **`gridSize`** — number of partitions (≈ number of threads)
- **Parallel Flows** — run independent steps simultaneously
- **Database partitioning** — split by ID range for zero lock contention
- **Restart behavior** — only failed partitions re-execute

The 5-million-row file now processes in 1.5 minutes. Brenda has her results by 5:54 AM. Admiral Uptime sleeps through the night.

But month-end is coming. Director Compliance needs 5 different jobs to run in a specific order: reconciliation first, then position calculation, then regulatory report, then archive, then notification. If reconciliation fails, nothing else should run. If the report has warnings, send an alert but continue.

That's job orchestration. Chapter 7.

---

[← Chapter 5: The Retry](chapter-05-retry-logic.md) | [Chapter 7: The Pipeline →](chapter-07-job-orchestration.md)

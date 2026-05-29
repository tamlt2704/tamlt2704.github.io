# Chapter 1: Core Concepts

[Overview](chapter-00-overview.md) | [next: Setup](chapter-02-setup.md)

## Architecture Overview

```
+-----------------------------------------------------------+
|                      JobLauncher                           |
|                          |                                |
|                          v                                |
|  +------------------- Job -------------------------+     |
|  |                                                 |     |
|  |  +--- Step 1 ----+    +--- Step 2 ----+       |     |
|  |  |                |    |               |       |     |
|  |  |  ItemReader    |    |   Tasklet     |       |     |
|  |  |      |         |    |               |       |     |
|  |  |      v         |    +---------------+       |     |
|  |  | ItemProcessor  |                            |     |
|  |  |      |         |                            |     |
|  |  |      v         |                            |     |
|  |  |  ItemWriter    |                            |     |
|  |  |                |                            |     |
|  |  +----------------+                            |     |
|  +-------------------------------------------------+     |
|                          |                                |
|                          v                                |
|                   JobRepository                           |
|              (metadata in database)                       |
+-----------------------------------------------------------+
```

## Core Domain Objects

### Job

A Job is the top-level container representing an entire batch process. It is composed of one or more Steps.

```java
@Bean
public Job importJob(JobRepository jobRepository, Step step1, Step step2) {
    return new JobBuilder("importJob", jobRepository)
            .start(step1)
            .next(step2)
            .build();
}
```

### Step

A Step is a single phase of a Job. Each Step has exactly one processing strategy: either chunk-oriented or tasklet-based.

### ItemReader

Reads one item at a time from a data source (file, database, queue). Returns `null` when input is exhausted.

### ItemProcessor

Transforms or validates a single item. Optional — you can go directly from reader to writer.

### ItemWriter

Writes a chunk (list) of items to a destination. Receives the entire chunk at once for efficient batch writes.

### JobRepository

Stores metadata about job executions: status, start/end times, parameters, step execution counts. Backed by a relational database.

### JobLauncher

Entry point for starting a Job with a set of JobParameters.

### ExecutionContext

A key-value store persisted between step executions. Used for checkpointing — if a job restarts, it can resume from where it left off.

## Chunk-Oriented Processing Model

The chunk model reads items one at a time, processes them, and writes them in chunks of a configurable size. A transaction wraps each chunk.

```
+----------------------------------------------+
|              Chunk (size = 10)                |
|                                              |
|  read() -> item1    --+                      |
|  read() -> item2      |                      |
|  read() -> item3      |  process each item   |
|  ...                   +-------------------+ |
|  read() -> item10   --+                      |
|                                              |
|  write([processed1, processed2, ..., p10])   |
|                                              |
|  --- COMMIT TRANSACTION ---                  |
+----------------------------------------------+
```

```java
@Bean
public Step chunkStep(JobRepository jobRepository,
                      PlatformTransactionManager transactionManager,
                      ItemReader<Person> reader,
                      ItemProcessor<Person, Person> processor,
                      ItemWriter<Person> writer) {
    return new StepBuilder("chunkStep", jobRepository)
            .<Person, Person>chunk(100, transactionManager)
            .reader(reader)
            .processor(processor)
            .writer(writer)
            .build();
}
```

## Tasklet vs Chunk

| Aspect      | Chunk                                  | Tasklet                                    |
| ----------- | -------------------------------------- | ------------------------------------------ |
| Use case    | Processing large datasets item by item | Single operation (cleanup, file move, DDL) |
| Transaction | Per chunk                              | Per execution                              |
| Restart     | Resumes from last committed chunk      | Re-executes entire tasklet                 |
| Components  | Reader + Processor + Writer            | Single execute() method                    |

### Tasklet Example

```java
@Bean
public Step cleanupStep(JobRepository jobRepository,
                        PlatformTransactionManager transactionManager) {
    return new StepBuilder("cleanupStep", jobRepository)
            .tasklet((contribution, chunkContext) -> {
                Files.deleteIfExists(Path.of("/tmp/staging.csv"));
                return RepeatStatus.FINISHED;
            }, transactionManager)
            .build();
}
```

## Job Parameters

Job parameters make each execution unique and allow passing runtime values:

```java
@Bean
@StepScope
public FlatFileItemReader<Person> reader(
        @Value("#{jobParameters['inputFile']}") String inputFile) {
    return new FlatFileItemReaderBuilder<Person>()
            .name("personReader")
            .resource(new FileSystemResource(inputFile))
            .delimited()
            .names("firstName", "lastName", "email")
            .targetType(Person.class)
            .build();
}
```

## Execution Lifecycle

1. `JobLauncher.run(job, parameters)` is called
2. JobRepository creates a new `JobExecution`
3. For each Step, a `StepExecution` is created
4. Chunks are read, processed, written, and committed
5. ExecutionContext is persisted after each chunk
6. On completion (or failure), status is updated in JobRepository

## Exercises

1. Draw the relationship between Job, Step, and chunk on paper. Identify where transactions begin and commit.
2. Explain why `ItemWriter` receives a list while `ItemReader` returns a single item.
3. Given a job that processes 1,000,000 records with chunk size 500, how many transactions will be committed?

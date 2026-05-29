# Chapter 8: Scaling

[prev: Error Handling](chapter-07-error-handling.md) | [next: Production](chapter-09-production.md)

## Scaling Strategies Overview

```
+------------------------------------------------------------------+
|  Strategy              | Complexity | Best For                    |
|------------------------+------------+-----------------------------|
|  Multi-threaded step   | Low        | I/O-bound processing        |
|  Parallel steps        | Low        | Independent data sources    |
|  Partitioning          | Medium     | Large datasets, DB reads    |
|  Remote chunking       | High       | CPU-intensive processing    |
|  Async processor/writer| Medium     | Slow external calls         |
+------------------------------------------------------------------+
```

## Multi-Threaded Step

Add a `TaskExecutor` to process multiple chunks concurrently. Simplest scaling approach.

```java
@Bean
public Step multiThreadedStep(JobRepository jobRepository,
                              PlatformTransactionManager transactionManager,
                              ItemReader<Person> reader,
                              ItemProcessor<Person, PersonDto> processor,
                              ItemWriter<PersonDto> writer) {
    return new StepBuilder("multiThreadedStep", jobRepository)
            .<Person, PersonDto>chunk(500, transactionManager)
            .reader(reader)
            .processor(processor)
            .writer(writer)
            .taskExecutor(new SimpleAsyncTaskExecutor())
            .throttleLimit(8) // max concurrent threads
            .build();
}
```

With a thread pool:

```java
@Bean
public TaskExecutor batchTaskExecutor() {
    ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
    executor.setCorePoolSize(4);
    executor.setMaxPoolSize(8);
    executor.setQueueCapacity(25);
    executor.setThreadNamePrefix("batch-");
    executor.initialize();
    return executor;
}
```

**Important**: `FlatFileItemReader` is NOT thread-safe. Use `SynchronizedItemStreamReader` wrapper:

```java
@Bean
public SynchronizedItemStreamReader<Person> synchronizedReader(
        FlatFileItemReader<Person> delegate) {
    SynchronizedItemStreamReader<Person> reader = new SynchronizedItemStreamReader<>();
    reader.setDelegate(delegate);
    return reader;
}
```

Or use `JdbcPagingItemReader` which is thread-safe by design.

## Parallel Steps (Split/Flow)

Execute independent steps simultaneously. Covered in Chapter 6, but here is the scaling perspective:

```java
@Bean
public Job parallelLoadJob(JobRepository jobRepository,
                           Step loadCustomers, Step loadOrders, Step loadProducts) {
    Flow flow1 = new FlowBuilder<SimpleFlow>("f1").start(loadCustomers).build();
    Flow flow2 = new FlowBuilder<SimpleFlow>("f2").start(loadOrders).build();
    Flow flow3 = new FlowBuilder<SimpleFlow>("f3").start(loadProducts).build();

    return new JobBuilder("parallelLoadJob", jobRepository)
            .start(new FlowBuilder<SimpleFlow>("parallel")
                    .split(batchTaskExecutor())
                    .add(flow1, flow2, flow3)
                    .build())
            .end()
            .build();
}
```

## Partitioning

Divide a dataset into partitions and process each partition in a separate thread (or remote worker). The most powerful local scaling strategy.

### Partitioner

Defines how to split the work:

```java
public class RangePartitioner implements Partitioner {

    private final JdbcTemplate jdbcTemplate;

    public RangePartitioner(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @Override
    public Map<String, ExecutionContext> partition(int gridSize) {
        Long min = jdbcTemplate.queryForObject("SELECT MIN(id) FROM person", Long.class);
        Long max = jdbcTemplate.queryForObject("SELECT MAX(id) FROM person", Long.class);

        long range = (max - min) / gridSize + 1;
        Map<String, ExecutionContext> partitions = new HashMap<>();

        for (int i = 0; i < gridSize; i++) {
            ExecutionContext context = new ExecutionContext();
            context.putLong("minId", min + (i * range));
            context.putLong("maxId", min + ((i + 1) * range) - 1);
            partitions.put("partition" + i, context);
        }
        return partitions;
    }
}
```

### Partitioned Step Configuration

```java
@Bean
public Step partitionedStep(JobRepository jobRepository, Step workerStep,
                            Partitioner partitioner) {
    return new StepBuilder("partitionedStep", jobRepository)
            .partitioner("workerStep", partitioner)
            .step(workerStep)
            .gridSize(8)
            .taskExecutor(batchTaskExecutor())
            .build();
}

@Bean
public Step workerStep(JobRepository jobRepository,
                       PlatformTransactionManager transactionManager,
                       ItemReader<Person> partitionedReader,
                       ItemWriter<PersonDto> writer) {
    return new StepBuilder("workerStep", jobRepository)
            .<Person, PersonDto>chunk(500, transactionManager)
            .reader(partitionedReader)
            .writer(writer)
            .build();
}

@Bean
@StepScope
public JdbcPagingItemReader<Person> partitionedReader(
        DataSource dataSource,
        @Value("#{stepExecutionContext['minId']}") Long minId,
        @Value("#{stepExecutionContext['maxId']}") Long maxId) {
    return new JdbcPagingItemReaderBuilder<Person>()
            .name("partitionedReader")
            .dataSource(dataSource)
            .selectClause("SELECT id, first_name, last_name, email, age")
            .fromClause("FROM person")
            .whereClause("WHERE id >= :minId AND id <= :maxId")
            .parameterValues(Map.of("minId", minId, "maxId", maxId))
            .sortKeys(Map.of("id", Order.ASCENDING))
            .pageSize(500)
            .rowMapper((rs, rowNum) -> new Person(
                    rs.getString("first_name"),
                    rs.getString("last_name"),
                    rs.getString("email"),
                    rs.getInt("age")))
            .build();
}
```

### File-Based Partitioner

Split a large file into partitions by line ranges:

```java
public class FilePartitioner implements Partitioner {

    private final String filePath;

    public FilePartitioner(String filePath) {
        this.filePath = filePath;
    }

    @Override
    public Map<String, ExecutionContext> partition(int gridSize) {
        try {
            long lineCount = Files.lines(Path.of(filePath)).count() - 1; // exclude header
            long linesPerPartition = lineCount / gridSize;

            Map<String, ExecutionContext> partitions = new HashMap<>();
            for (int i = 0; i < gridSize; i++) {
                ExecutionContext context = new ExecutionContext();
                context.putLong("startLine", 1 + (i * linesPerPartition));
                context.putLong("endLine", (i == gridSize - 1) ? lineCount : (i + 1) * linesPerPartition);
                partitions.put("partition" + i, context);
            }
            return partitions;
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }
}
```

## Remote Chunking

The manager reads items and sends them over middleware (e.g., RabbitMQ, Kafka) to remote workers for processing and writing. Use when processing is the bottleneck.

```
+----------+          +------------------+          +----------+
|  Manager |  ---->   |  Message Broker  |  ---->   |  Worker  |
|  (reads) |          |  (RabbitMQ)      |          | (process |
|          |  <----   |                  |  <----   |  + write)|
+----------+          +------------------+          +----------+
```

Add dependency:

```groovy
implementation 'org.springframework.batch:spring-batch-integration'
implementation 'org.springframework.boot:spring-boot-starter-amqp'
```

Manager configuration:

```java
@Configuration
public class ManagerConfig {

    @Bean
    public Step managerStep(JobRepository jobRepository,
                            RemoteChunkingManagerStepBuilderFactory managerStepBuilder,
                            ItemReader<Person> reader) {
        return managerStepBuilder.get("managerStep")
                .<Person, Person>chunk(100)
                .reader(reader)
                .outputChannel(outboundChannel())
                .inputChannel(inboundChannel())
                .build();
    }
}
```

## AsyncItemProcessor and AsyncItemWriter

Wrap existing processor/writer to execute asynchronously. Each item is processed in a separate thread via `Future`.

```java
@Bean
public AsyncItemProcessor<Person, PersonDto> asyncProcessor(
        ItemProcessor<Person, PersonDto> delegate) {
    AsyncItemProcessor<Person, PersonDto> processor = new AsyncItemProcessor<>();
    processor.setDelegate(delegate);
    processor.setTaskExecutor(batchTaskExecutor());
    return processor;
}

@Bean
public AsyncItemWriter<PersonDto> asyncWriter(ItemWriter<PersonDto> delegate) {
    AsyncItemWriter<PersonDto> writer = new AsyncItemWriter<>();
    writer.setDelegate(delegate);
    return writer;
}

@Bean
public Step asyncStep(JobRepository jobRepository,
                      PlatformTransactionManager transactionManager,
                      ItemReader<Person> reader,
                      AsyncItemProcessor<Person, PersonDto> asyncProcessor,
                      AsyncItemWriter<PersonDto> asyncWriter) {
    return new StepBuilder("asyncStep", jobRepository)
            .<Person, Future<PersonDto>>chunk(100, transactionManager)
            .reader(reader)
            .processor(asyncProcessor)
            .writer(asyncWriter)
            .build();
}
```

## Exercises

1. Take the CSV import job from earlier chapters. Add multi-threading with 4 threads. Measure throughput improvement vs single-threaded.
2. Implement partitioning for a database table with 1M rows. Use `RangePartitioner` with grid size 8. Compare with single-threaded.
3. Create a job that processes 3 independent CSV files in parallel using split/flow, then writes a summary report.
4. Wrap a slow processor (add `Thread.sleep(10)`) with `AsyncItemProcessor`. Measure the throughput difference.

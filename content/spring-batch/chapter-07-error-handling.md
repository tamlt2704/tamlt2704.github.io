# Chapter 7: Error Handling

[prev: Flow Control](chapter-06-flow.md) | [next: Scaling](chapter-08-scaling.md)

## Skip Policy

Skip allows a job to continue processing even when some items fail. Configure which exceptions to skip and a maximum skip count.

```java
@Bean
public Step importStep(JobRepository jobRepository,
                       PlatformTransactionManager transactionManager,
                       ItemReader<Person> reader,
                       ItemProcessor<Person, PersonDto> processor,
                       ItemWriter<PersonDto> writer) {
    return new StepBuilder("importStep", jobRepository)
            .<Person, PersonDto>chunk(500, transactionManager)
            .reader(reader)
            .processor(processor)
            .writer(writer)
            .faultTolerant()
            .skip(FlatFileParseException.class)
            .skip(ValidationException.class)
            .skipLimit(100)
            .build();
}
```

### Custom SkipPolicy

For more complex skip logic:

```java
public class FileVerificationSkipPolicy implements SkipPolicy {

    @Override
    public boolean shouldSkip(Throwable t, long skipCount) throws SkipLimitExceededException {
        if (t instanceof FlatFileParseException) {
            return true; // always skip parse errors
        }
        if (t instanceof ValidationException && skipCount < 50) {
            return true; // skip up to 50 validation errors
        }
        return false; // fail on anything else
    }
}
```

```java
.faultTolerant()
.skipPolicy(new FileVerificationSkipPolicy())
```

### Skip Listener (Logging Skipped Items)

```java
@Component
public class SkipListener implements org.springframework.batch.core.SkipListener<Person, PersonDto> {

    private static final Logger log = LoggerFactory.getLogger(SkipListener.class);

    @Override
    public void onSkipInRead(Throwable t) {
        log.warn("Skipped item during read: {}", t.getMessage());
    }

    @Override
    public void onSkipInProcess(Person item, Throwable t) {
        log.warn("Skipped item during process: {} - {}", item, t.getMessage());
    }

    @Override
    public void onSkipInWrite(PersonDto item, Throwable t) {
        log.warn("Skipped item during write: {} - {}", item, t.getMessage());
    }
}
```

Register it:

```java
.listener(skipListener)
```

## Retry Policy

Retry transient failures (network timeouts, deadlocks) before giving up.

```java
@Bean
public Step apiWriteStep(JobRepository jobRepository,
                         PlatformTransactionManager transactionManager,
                         ItemReader<Person> reader,
                         ItemWriter<Person> writer) {
    return new StepBuilder("apiWriteStep", jobRepository)
            .<Person, Person>chunk(100, transactionManager)
            .reader(reader)
            .writer(writer)
            .faultTolerant()
            .retry(DeadlockLoserDataAccessException.class)
            .retry(ConnectTimeoutException.class)
            .retryLimit(3)
            .build();
}
```

### Backoff Policy

Add exponential backoff between retries:

```java
@Bean
public Step retryWithBackoffStep(JobRepository jobRepository,
                                 PlatformTransactionManager transactionManager,
                                 ItemReader<Person> reader,
                                 ItemWriter<Person> writer) {
    return new StepBuilder("retryWithBackoff", jobRepository)
            .<Person, Person>chunk(100, transactionManager)
            .reader(reader)
            .writer(writer)
            .faultTolerant()
            .retry(ConnectTimeoutException.class)
            .retryLimit(5)
            .backOffPolicy(new ExponentialBackOffPolicy() {{
                setInitialInterval(1000);  // 1 second
                setMultiplier(2.0);        // doubles each retry
                setMaxInterval(30000);     // max 30 seconds
            }})
            .build();
}
```

### Retry Listener

```java
public class RetryLogListener implements RetryListener {

    private static final Logger log = LoggerFactory.getLogger(RetryLogListener.class);

    @Override
    public <T, E extends Throwable> void onError(RetryContext context,
            RetryCallback<T, E> callback, Throwable throwable) {
        log.warn("Retry attempt {} for: {}", context.getRetryCount(), throwable.getMessage());
    }
}
```

## Combining Skip and Retry

Skip after retries are exhausted:

```java
.faultTolerant()
.retry(DeadlockLoserDataAccessException.class)
.retryLimit(3)
.skip(DeadlockLoserDataAccessException.class)
.skipLimit(10)
```

This means: retry up to 3 times, and if still failing, skip the item (up to 10 skipped items total).

## Restart and Checkpointing

Spring Batch persists `ExecutionContext` after each chunk commit. If a job fails, it can restart from the last committed chunk.

```java
@Bean
public Job restartableJob(JobRepository jobRepository, Step importStep) {
    return new JobBuilder("restartableJob", jobRepository)
            .start(importStep)
            .build();
    // Jobs are restartable by default
}
```

### Preventing Restart

```java
@Bean
public Job nonRestartableJob(JobRepository jobRepository, Step importStep) {
    return new JobBuilder("nonRestartableJob", jobRepository)
            .preventRestart()
            .start(importStep)
            .build();
}
```

### ExecutionContext Checkpointing

Store custom state for restart:

```java
@Component
@StepScope
public class CheckpointingReader implements ItemReader<Record>, ItemStream {

    private int currentIndex = 0;

    @Override
    public void open(ExecutionContext executionContext) {
        if (executionContext.containsKey("currentIndex")) {
            currentIndex = executionContext.getInt("currentIndex");
        }
    }

    @Override
    public void update(ExecutionContext executionContext) {
        executionContext.putInt("currentIndex", currentIndex);
    }

    @Override
    public Record read() {
        // read from currentIndex position
        currentIndex++;
        return fetchRecord(currentIndex);
    }

    @Override
    public void close() {}

    private Record fetchRecord(int index) {
        // implementation
        return null; // null signals end
    }
}
```

## No-Rollback Exceptions

By default, any exception during write triggers a transaction rollback. Mark exceptions as no-rollback to commit the chunk anyway:

```java
@Bean
public Step stepWithNoRollback(JobRepository jobRepository,
                               PlatformTransactionManager transactionManager,
                               ItemReader<Person> reader,
                               ItemWriter<Person> writer) {
    return new StepBuilder("noRollbackStep", jobRepository)
            .<Person, Person>chunk(500, transactionManager)
            .reader(reader)
            .writer(writer)
            .faultTolerant()
            .noRollback(NotificationException.class)
            .build();
}
```

Use case: sending email notifications in the writer — if the email fails, you still want the database write to commit.

## Complete Fault-Tolerant Step

```java
@Bean
public Step faultTolerantStep(JobRepository jobRepository,
                              PlatformTransactionManager transactionManager,
                              ItemReader<Person> reader,
                              ItemProcessor<Person, PersonDto> processor,
                              ItemWriter<PersonDto> writer,
                              SkipListener skipListener) {
    return new StepBuilder("faultTolerantStep", jobRepository)
            .<Person, PersonDto>chunk(500, transactionManager)
            .reader(reader)
            .processor(processor)
            .writer(writer)
            .faultTolerant()
            // Skip configuration
            .skip(FlatFileParseException.class)
            .skip(ValidationException.class)
            .skipLimit(200)
            // Retry configuration
            .retry(DeadlockLoserDataAccessException.class)
            .retry(ConnectTimeoutException.class)
            .retryLimit(3)
            .backOffPolicy(new ExponentialBackOffPolicy() {{
                setInitialInterval(500);
                setMultiplier(2.0);
                setMaxInterval(10000);
            }})
            // No-rollback
            .noRollback(MailSendException.class)
            // Listeners
            .listener(skipListener)
            .build();
}
```

## Exercises

1. Create a job that reads a CSV with intentionally malformed rows. Configure skip to handle up to 50 parse errors and log each skipped line.
2. Simulate a flaky database writer (randomly throw `DeadlockLoserDataAccessException`). Configure retry with exponential backoff.
3. Build a restartable job that processes a large file. Kill it mid-way and restart — verify it resumes from the last checkpoint.
4. Combine skip and retry: retry transient DB errors 3 times, then skip. Write skipped items to an error file for manual review.

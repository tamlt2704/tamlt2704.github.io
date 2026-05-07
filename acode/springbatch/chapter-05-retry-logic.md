# Chapter 5: The Retry — Transient Failures

[← Chapter 4: The Restart](chapter-04-restartability.md) | [Chapter 6: The Deadline →](chapter-06-partitioning.md)

---

## The Incident

Friday. 5:08 AM. The reconciliation job is running. At chunk 342, the enrichment step calls the exchange-rate API to convert EUR transactions to USD. The API returns HTTP 503 for 12 seconds (their nightly maintenance window). Your job fails.

```
org.springframework.web.client.HttpServerErrorException$ServiceUnavailable:
  503 Service Unavailable
```

You restart the job. It resumes from chunk 342 (thanks to Chapter 4). The API is back. Everything completes.

Admiral Uptime: "Why did I get paged at 5 AM for a 12-second blip? Can't the job just... wait and try again?"

You: "It can. That's called retry."

## Skip vs. Retry: When to Use Which

| Strategy | Use When | Example |
|---|---|---|
| **Skip** | Data is permanently bad | Malformed CSV row, invalid amount |
| **Retry** | Failure is transient | API timeout, DB connection blip, lock contention |
| **Skip after Retry** | Tried N times, still failing | API returns 404 for one specific record |

Skip says "this item is broken, move on." Retry says "this might work if I try again."

## The Test: Transient API Failure Should Retry

```java
@Test
void shouldRetryOnTransientFailure_andSucceedOnSecondAttempt() throws Exception {
    // API fails twice, then succeeds
    exchangeRateApi.setFailuresBeforeSuccess(2);

    generateTestCsv(inputPath, 100);

    JobExecution execution = jobLauncherTestUtils.launchJob(defaultParams());

    assertThat(execution.getStatus()).isEqualTo(BatchStatus.COMPLETED);
    assertThat(exchangeRateApi.getCallCount()).isGreaterThan(100); // retries happened
}

@Test
void shouldFailAfterMaxRetries_andSkipTheItem() throws Exception {
    // API always fails for this specific transaction
    exchangeRateApi.setAlwaysFailFor("TXN-999");

    generateTestCsv(inputPath, 100); // includes TXN-999

    JobExecution execution = jobLauncherTestUtils.launchJob(defaultParams());

    assertThat(execution.getStatus()).isEqualTo(BatchStatus.COMPLETED);

    StepExecution step = execution.getStepExecutions().iterator().next();
    assertThat(step.getProcessSkipCount()).isEqualTo(1); // TXN-999 skipped after retries
    assertThat(step.getWriteCount()).isEqualTo(99);      // other 99 succeeded
}
```

## The Fix: Retry Configuration

```java
@Bean
public Step enrichmentStep(JobRepository jobRepository,
                            PlatformTransactionManager txManager,
                            ItemReader<TransactionDto> reader,
                            EnrichmentProcessor processor,
                            JdbcBatchItemWriter<EnrichedTransaction> writer) {
    return new StepBuilder("enrichmentStep", jobRepository)
        .<TransactionDto, EnrichedTransaction>chunk(1000, txManager)
        .reader(reader)
        .processor(processor)
        .writer(writer)
        .faultTolerant()
        // Retry configuration
        .retryLimit(3)
        .retry(HttpServerErrorException.class)       // 5xx errors
        .retry(ResourceAccessException.class)        // connection timeout
        .retry(CannotAcquireLockException.class)     // DB lock contention
        .noRetry(HttpClientErrorException.class)     // 4xx = don't retry (bad request)
        // Skip after retries exhausted
        .skipLimit(100)
        .skip(HttpServerErrorException.class)
        .skip(ResourceAccessException.class)
        .build();
}
```

The flow:
1. Process item → API throws 503
2. Wait, retry (attempt 2) → API throws 503 again
3. Wait, retry (attempt 3) → API returns 200 ✓

If all 3 retries fail:
4. Skip the item (if skip is configured) OR fail the step

## How Retry Works Internally

### During Processing

```
process(item) → throws HttpServerErrorException
  → retry attempt 1
process(item) → throws HttpServerErrorException
  → retry attempt 2
process(item) → success ✓
  → continue to next item
```

### During Writing

Writing is trickier. The entire chunk is written together. If writing fails:

```
write([item1, item2, ..., item1000]) → throws Exception
  → ROLLBACK chunk
  → re-process and write items ONE BY ONE
  → item 47 fails → retry item 47
  → item 47 fails again → retry item 47
  → item 47 fails third time → skip item 47
  → write remaining 999 items
  → COMMIT
```

This is the same single-item fallback from Chapter 3's skip logic, but now with retries before skipping.

## Backoff: Don't Hammer the API

Retrying immediately is rude. If the API is overloaded, hammering it makes things worse. Use exponential backoff:

```java
@Bean
public Step enrichmentStep(...) {
    return new StepBuilder("enrichmentStep", jobRepository)
        .<TransactionDto, EnrichedTransaction>chunk(1000, txManager)
        .reader(reader)
        .processor(processor)
        .writer(writer)
        .faultTolerant()
        .retryLimit(5)
        .retry(HttpServerErrorException.class)
        .backOffPolicy(exponentialBackOff())
        .skipLimit(100)
        .skip(HttpServerErrorException.class)
        .build();
}

private BackOffPolicy exponentialBackOff() {
    ExponentialBackOffPolicy policy = new ExponentialBackOffPolicy();
    policy.setInitialInterval(1000);   // 1 second
    policy.setMultiplier(2.0);          // double each time
    policy.setMaxInterval(30000);       // cap at 30 seconds
    return policy;
}
```

Retry timeline:
```
Attempt 1: immediate
  → fail
Attempt 2: wait 1s
  → fail
Attempt 3: wait 2s
  → fail
Attempt 4: wait 4s
  → fail
Attempt 5: wait 8s
  → fail → skip (retries exhausted)
```

Total wait: 15 seconds. Much better than failing the entire 2-million-row job.

## RetryTemplate: Retry Outside of Spring Batch

Sometimes you need retry logic inside your processor — not managed by the step:

```java
// src/main/java/com/megabank/processor/EnrichmentProcessor.java
package com.megabank.processor;

import com.megabank.domain.EnrichedTransaction;
import com.megabank.domain.TransactionDto;
import com.megabank.service.ExchangeRateService;
import org.springframework.batch.item.ItemProcessor;
import org.springframework.retry.support.RetryTemplate;
import org.springframework.retry.backoff.ExponentialBackOffPolicy;
import org.springframework.retry.policy.SimpleRetryPolicy;

import java.math.BigDecimal;
import java.util.Map;

public class EnrichmentProcessor implements ItemProcessor<TransactionDto, EnrichedTransaction> {

    private final ExchangeRateService exchangeRateService;
    private final RetryTemplate retryTemplate;

    public EnrichmentProcessor(ExchangeRateService exchangeRateService) {
        this.exchangeRateService = exchangeRateService;
        this.retryTemplate = buildRetryTemplate();
    }

    @Override
    public EnrichedTransaction process(TransactionDto item) {
        BigDecimal rateUsd = retryTemplate.execute(context ->
            exchangeRateService.getRate(item.getCurrency(), "USD")
        );

        BigDecimal amountUsd = item.getAmount().multiply(rateUsd);

        return new EnrichedTransaction(
            item.getTransactionId(),
            item.getAmount(),
            item.getCurrency(),
            amountUsd,
            rateUsd
        );
    }

    private RetryTemplate buildRetryTemplate() {
        RetryTemplate template = new RetryTemplate();

        SimpleRetryPolicy retryPolicy = new SimpleRetryPolicy(
            3, Map.of(
                RuntimeException.class, true  // retry all runtime exceptions
            )
        );

        ExponentialBackOffPolicy backOff = new ExponentialBackOffPolicy();
        backOff.setInitialInterval(500);
        backOff.setMultiplier(2.0);
        backOff.setMaxInterval(5000);

        template.setRetryPolicy(retryPolicy);
        template.setBackOffPolicy(backOff);
        return template;
    }
}
```

When to use step-level retry vs. `RetryTemplate`:

| Approach | Use When |
|---|---|
| Step-level `.retry()` | The entire chunk should be retried (DB write failures) |
| `RetryTemplate` in processor | Individual API calls need retry (enrichment, validation) |
| Both | Belt and suspenders for critical jobs |

## Retry Listener: Track What's Happening

Admiral Uptime wants to know when retries are happening — it might indicate an upstream problem:

```java
// src/main/java/com/megabank/listener/RetryMetricsListener.java
package com.megabank.listener;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.retry.RetryCallback;
import org.springframework.retry.RetryContext;
import org.springframework.retry.RetryListener;

import java.util.concurrent.atomic.AtomicInteger;

public class RetryMetricsListener implements RetryListener {

    private static final Logger log = LoggerFactory.getLogger(RetryMetricsListener.class);
    private final AtomicInteger totalRetries = new AtomicInteger(0);

    @Override
    public <T, E extends Throwable> boolean open(RetryContext context,
                                                   RetryCallback<T, E> callback) {
        return true; // proceed with retry
    }

    @Override
    public <T, E extends Throwable> void onError(RetryContext context,
                                                   RetryCallback<T, E> callback,
                                                   Throwable throwable) {
        int attempt = context.getRetryCount();
        totalRetries.incrementAndGet();
        log.warn("Retry attempt {} — error: {}", attempt, throwable.getMessage());

        if (attempt >= 3) {
            log.error("Max retries reached. Total retries this run: {}",
                totalRetries.get());
        }
    }

    @Override
    public <T, E extends Throwable> void close(RetryContext context,
                                                 RetryCallback<T, E> callback,
                                                 Throwable throwable) {
        if (throwable != null) {
            log.error("All retries exhausted for item. Final error: {}",
                throwable.getMessage());
        }
    }

    public int getTotalRetries() {
        return totalRetries.get();
    }
}
```

## Circuit Breaker: "Stop Trying, It's Dead"

If the API is down for 5 minutes, retrying every item individually wastes time. A circuit breaker detects sustained failures and fails fast:

```java
// src/main/java/com/megabank/service/CircuitBreakingExchangeRateService.java
package com.megabank.service;

import java.time.Instant;
import java.util.concurrent.atomic.AtomicInteger;

public class CircuitBreakingExchangeRateService {

    private final ExchangeRateService delegate;
    private final AtomicInteger failureCount = new AtomicInteger(0);
    private volatile Instant circuitOpenedAt = null;
    private static final int FAILURE_THRESHOLD = 5;
    private static final long COOLDOWN_SECONDS = 60;

    public CircuitBreakingExchangeRateService(ExchangeRateService delegate) {
        this.delegate = delegate;
    }

    public java.math.BigDecimal getRate(String from, String to) {
        // Circuit is open — fail fast
        if (circuitOpenedAt != null) {
            if (Instant.now().isBefore(circuitOpenedAt.plusSeconds(COOLDOWN_SECONDS))) {
                throw new CircuitOpenException(
                    "Circuit breaker open — API unavailable. Retry after cooldown.");
            }
            // Cooldown expired — try again (half-open)
            circuitOpenedAt = null;
            failureCount.set(0);
        }

        try {
            var rate = delegate.getRate(from, to);
            failureCount.set(0); // success resets counter
            return rate;
        } catch (Exception e) {
            if (failureCount.incrementAndGet() >= FAILURE_THRESHOLD) {
                circuitOpenedAt = Instant.now();
            }
            throw e;
        }
    }
}
```

After 5 consecutive failures, the circuit opens. For the next 60 seconds, all calls fail immediately (no waiting for timeouts). After 60 seconds, it tries one call — if it succeeds, the circuit closes. If it fails, the circuit stays open.

Configure the step to skip `CircuitOpenException`:

```java
.faultTolerant()
.retryLimit(3)
.retry(HttpServerErrorException.class)
.noRetry(CircuitOpenException.class) // don't retry — circuit is open
.skip(CircuitOpenException.class)    // skip items while circuit is open
.skipLimit(10000)
```

## The Test: Circuit Breaker

```java
@Test
void circuitBreaker_shouldFailFast_whenApiIsDown() throws Exception {
    exchangeRateApi.setDownForSeconds(30);
    generateTestCsv(inputPath, 1000);

    long start = System.currentTimeMillis();
    JobExecution execution = jobLauncherTestUtils.launchJob(defaultParams());
    long duration = System.currentTimeMillis() - start;

    // Without circuit breaker: 1000 items × 3 retries × 5s timeout = 4+ hours
    // With circuit breaker: fails fast after 5 items, skips the rest
    assertThat(duration).isLessThan(30_000); // completes in under 30s

    StepExecution step = execution.getStepExecutions().iterator().next();
    assertThat(step.getProcessSkipCount()).isGreaterThan(900); // most items skipped
}
```

## Combining Skip + Retry: The Full Picture

```java
@Bean
public Step enrichmentStep(...) {
    return new StepBuilder("enrichmentStep", jobRepository)
        .<TransactionDto, EnrichedTransaction>chunk(1000, txManager)
        .reader(reader)
        .processor(processor)
        .writer(writer)
        .faultTolerant()
        // Retry: transient failures
        .retryLimit(3)
        .retry(HttpServerErrorException.class)
        .retry(ResourceAccessException.class)
        .backOffPolicy(exponentialBackOff())
        .listener(retryListener)
        // Skip: permanent failures (or retries exhausted)
        .skipLimit(500)
        .skip(HttpServerErrorException.class)
        .skip(ResourceAccessException.class)
        .skip(CircuitOpenException.class)
        .skip(ValidationException.class)
        // Never skip/retry these
        .noRetry(HttpClientErrorException.class)
        .noSkip(DatabaseException.class)
        .listener(skipListener)
        .build();
}
```

The decision tree for each item:
```
process(item) → exception?
  │
  ├─ No → write normally
  │
  └─ Yes → is it retryable?
       │
       ├─ No (noRetry) → is it skippable?
       │    ├─ Yes → skip, log, continue
       │    └─ No → FAIL the step
       │
       └─ Yes → retry (up to retryLimit)
            │
            ├─ Succeeds → write normally
            │
            └─ All retries fail → is it skippable?
                 ├─ Yes → skip, log, continue
                 └─ No → FAIL the step
```

## What You Learned

- **`.retry(Exception.class)`** — which exceptions trigger a retry
- **`.retryLimit(n)`** — maximum retry attempts per item
- **`.backOffPolicy()`** — exponential backoff between retries
- **`RetryTemplate`** — retry logic inside processors for API calls
- **`RetryListener`** — track retry attempts for monitoring
- **Circuit breaker** — fail fast when an upstream service is down
- **Skip after retry** — if retries are exhausted, skip instead of failing
- **`.noRetry()`** — exceptions that should never be retried (4xx, validation)
- **Step-level vs. processor-level retry** — different scopes for different needs

The job now handles transient failures gracefully. A 12-second API blip? Retry 3 times with backoff. API down for 5 minutes? Circuit breaker kicks in, skips affected items, job completes with a report of what was skipped.

But Brenda's 2-million-row file still takes 4 minutes with one thread. The processing window is 6 AM. Some nights, the file arrives at 5:50 AM. Ten minutes isn't enough margin.

"Can we make it faster?" Admiral Uptime asks.

You can. Partitioning splits the work across multiple threads — or even multiple machines.

That's Chapter 6.

---

[← Chapter 4: The Restart](chapter-04-restartability.md) | [Chapter 6: The Deadline →](chapter-06-partitioning.md)

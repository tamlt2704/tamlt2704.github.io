# Chapter 7: If It Fails, Retry Then Dead-Letter It

[← Chapter 6: Send Results to the Pharmacy](chapter-06-outbound-adapters.md) | [Chapter 8: Process 10,000 Messages →](chapter-08-concurrency.md)

---

## The Disaster

PharmaCo's SFTP server goes down for maintenance every Sunday at 2am. Your flow retries 3 times, fails, and... the message disappears. Monday morning, 47 prescriptions are missing. Patients don't get their medication. Dr. Patel is furious. Compliance Carl is drafting an incident report.

> "Where did those messages go?"
> "They... threw an exception."
> "And then?"
> "They're gone."

Miriam:

> "Every message must end up somewhere — either successfully delivered or in a dead-letter queue with full context about why it failed. Nothing vanishes. Ever."

---

## Error Channels: Where Failed Messages Go

Spring Integration has a global `errorChannel`. Any unhandled exception in an async flow lands there:

```java
// src/main/java/com/medibridge/flows/ErrorHandlingFlow.java
package com.medibridge.flows;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.integration.dsl.IntegrationFlow;
import org.springframework.messaging.MessagingException;

@Configuration
public class ErrorHandlingFlow {

    @Bean
    public IntegrationFlow globalErrorFlow() {
        return IntegrationFlow.from("errorChannel")
            .handle(message -> {
                MessagingException ex = (MessagingException) message.getPayload();
                System.err.println("FAILED MESSAGE:");
                System.err.println("  Cause: " + ex.getCause().getMessage());
                System.err.println("  Original payload: " + ex.getFailedMessage().getPayload());
                System.err.println("  Headers: " + ex.getFailedMessage().getHeaders());
            })
            .get();
    }
}
```

The `errorChannel` receives `ErrorMessage` objects. The payload is a `MessagingException` that wraps:
- The original failed message (`.getFailedMessage()`)
- The exception that caused the failure (`.getCause()`)

---

## Custom Error Channels Per Flow

The global `errorChannel` catches everything. But you want different handling for different flows:

```java
@Bean
public IntegrationFlow prescriptionFlowWithErrorChannel() {
    return IntegrationFlow.from("prescriptionChannel")
        .transform(/* ... */)
        .handle(Sftp.outboundAdapter(pharmacySftpFactory)
                .remoteDirectory("/inbound/prescriptions"),
            e -> e.advice(retryAdvice())
                  // Send failures to a specific error channel
                  .requiresReply(false))
        .get();
}

// Dedicated error handling for prescription failures
@Bean
public IntegrationFlow prescriptionErrorFlow() {
    return IntegrationFlow.from("prescriptionErrorChannel")
        .handle((payload, headers) -> {
            // Log, alert, store in dead-letter table
            deadLetterRepository.save(new DeadLetter(
                headers.get("prescriptionId", String.class),
                "PRESCRIPTION",
                payload.toString(),
                headers.get("errorMessage", String.class),
                Instant.now()
            ));
            return null;
        })
        .get();
}
```

---

## Retry with Exponential Backoff

Simple retry isn't enough. If the SFTP server is down, retrying every 5 seconds for 15 seconds won't help. You need **exponential backoff** — wait longer between each attempt:

```java
@Bean
public RequestHandlerRetryAdvice exponentialRetryAdvice() {
    RequestHandlerRetryAdvice advice = new RequestHandlerRetryAdvice();

    RetryTemplate retryTemplate = RetryTemplate.builder()
        .maxAttempts(5)
        .exponentialBackoff(1000, 2.0, 30000)
        // Attempt 1: immediate
        // Attempt 2: wait 1s
        // Attempt 3: wait 2s
        // Attempt 4: wait 4s
        // Attempt 5: wait 8s (capped at 30s)
        .retryOn(MessagingException.class)
        .build();

    advice.setRetryTemplate(retryTemplate);

    // After all retries exhausted, send to dead-letter channel
    advice.setRecoveryCallback(context -> {
        Throwable lastError = context.getLastThrowable();
        Message<?> failedMessage = ((MessagingException) lastError).getFailedMessage();

        // Enrich with error info and send to dead-letter
        Message<?> deadLetter = MessageBuilder.fromMessage(failedMessage)
            .setHeader("errorMessage", lastError.getMessage())
            .setHeader("errorTimestamp", Instant.now().toString())
            .setHeader("retryCount", context.getRetryCount())
            .build();

        deadLetterChannel.send(deadLetter);
        return null;
    });

    return advice;
}
```

---

## Circuit Breaker: Stop Hammering a Dead System

If the SFTP server is down, retrying every message is pointless — and might get your IP banned. A **circuit breaker** stops trying after repeated failures:

```java
@Bean
public RequestHandlerCircuitBreakerAdvice circuitBreakerAdvice() {
    RequestHandlerCircuitBreakerAdvice advice = new RequestHandlerCircuitBreakerAdvice();
    advice.setThreshold(5);           // Open circuit after 5 consecutive failures
    advice.setHalfOpenAfter(60_000);  // Try again after 60 seconds
    return advice;
}

@Bean
public IntegrationFlow prescriptionWithCircuitBreaker() {
    return IntegrationFlow.from("prescriptionChannel")
        .handle(Sftp.outboundAdapter(pharmacySftpFactory)
                .remoteDirectory("/inbound/prescriptions"),
            e -> e.advice(
                circuitBreakerAdvice(),   // Circuit breaker (outer)
                exponentialRetryAdvice()   // Retry (inner)
            ))
        .get();
}
```

The circuit breaker has three states:

```
  CLOSED (normal) → failures < threshold → messages flow through
       │
       │ 5 consecutive failures
       ▼
  OPEN (tripped) → all messages immediately fail → sent to error channel
       │
       │ 60 seconds pass
       ▼
  HALF-OPEN → let ONE message through
       │
       ├── success → back to CLOSED
       └── failure → back to OPEN
```

---

## Dead-Letter Queue: The Last Resort

```java
// src/main/java/com/medibridge/deadletter/DeadLetterStore.java
package com.medibridge.deadletter;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.integration.dsl.IntegrationFlow;
import org.springframework.integration.jdbc.JdbcMessageHandler;

import javax.sql.DataSource;

@Configuration
public class DeadLetterStore {

    @Bean
    public IntegrationFlow deadLetterFlow(DataSource dataSource) {
        return IntegrationFlow.from("deadLetterChannel")
            .handle(new JdbcMessageHandler(dataSource,
                """
                INSERT INTO dead_letters (message_id, channel, payload, headers, error_message, failed_at)
                VALUES (:headers[id], :headers[errorChannel], :payload, :headers, :headers[errorMessage], NOW())
                """))
            .get();
    }
}
```

SQL schema:

```sql
CREATE TABLE dead_letters (
    id BIGSERIAL PRIMARY KEY,
    message_id VARCHAR(255),
    channel VARCHAR(255),
    payload TEXT,
    headers TEXT,
    error_message TEXT,
    failed_at TIMESTAMP,
    retried_at TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE
);
```

Now every failed message is stored with full context. Compliance Carl can query it. Ops can retry individual messages. Nothing vanishes.

---

## Retry from Dead-Letter

```java
@Bean
public IntegrationFlow retryDeadLetterFlow() {
    return IntegrationFlow.from("retryDeadLetterChannel")
        .handle((payload, headers) -> {
            // Load from dead_letter table, re-send to original channel
            Long deadLetterId = headers.get("deadLetterId", Long.class);
            DeadLetter dl = deadLetterRepository.findById(deadLetterId).orElseThrow();

            Message<?> retryMessage = MessageBuilder
                .withPayload(dl.getPayload())
                .copyHeaders(dl.getOriginalHeaders())
                .setHeader("retryAttempt", true)
                .build();

            // Send back to the original flow
            MessageChannel originalChannel = channelResolver.resolveDestination(dl.getChannel());
            originalChannel.send(retryMessage);

            // Mark as retried
            dl.setRetriedAt(Instant.now());
            deadLetterRepository.save(dl);

            return null;
        })
        .get();
}
```

---

## Error Handling Strategy Summary

```
  Message arrives
       │
       ▼
  [Endpoint] — try to process
       │
       ├── Success → continue flow
       │
       └── Failure
            │
            ▼
       [Retry Advice] — exponential backoff (5 attempts)
            │
            ├── Retry succeeds → continue flow
            │
            └── All retries exhausted
                 │
                 ▼
            [Circuit Breaker] — if too many failures, stop trying
                 │
                 ▼
            [Dead-Letter Channel] — store with full context
                 │
                 ▼
            [Dead-Letter Table] — queryable, retryable, auditable
```

---

## Testing Error Handling

```java
@Test
void shouldDeadLetterAfterRetriesExhausted() {
    // Simulate SFTP being down
    sftpContainer.stop();

    // Send a prescription
    prescriptionChannel.send(MessageBuilder
        .withPayload("{\"id\": \"RX-FAIL\"}")
        .setHeader("prescriptionId", "RX-FAIL")
        .build());

    // Wait for retries to exhaust
    await().atMost(Duration.ofSeconds(30)).untilAsserted(() -> {
        var deadLetter = deadLetterRepository.findByMessageId("RX-FAIL");
        assertThat(deadLetter).isPresent();
        assertThat(deadLetter.get().getErrorMessage()).contains("Connection refused");
    });
}
```

---

## Report to Miriam (and Compliance Carl)

> **Error handling implemented:**
> - Exponential backoff: 5 retries (1s, 2s, 4s, 8s, 16s)
> - Circuit breaker: stops after 5 consecutive failures, retries after 60s
> - Dead-letter table: every failed message stored with payload, headers, error, timestamp
> - Retry-from-dead-letter endpoint: ops can re-send individual messages
> - Nothing vanishes. Every message is either delivered or accounted for.
>
> The 47 missing prescriptions? Would be in the dead-letter table with "Connection refused" errors. Ops would see them Monday morning and retry after SFTP comes back.

Compliance Carl: "Acceptable. But I also need to know about the 10,000 messages that *succeed*. We'll talk about that in Chapter 10."

Miriam: "Next problem — Black Friday. The lab system sends 10,000 results in an hour instead of the usual 200. The single-threaded flow can't keep up."

---

## What You Learned

- **Error channel** — where failed messages go (global `errorChannel` or custom per-flow)
- **`ErrorMessage`** wraps the original message + the exception — full context preserved
- **Retry advice** — configurable attempts, backoff strategy, recovery callback
- **Exponential backoff** — wait longer between retries (1s, 2s, 4s, 8s...)
- **Circuit breaker** — stop trying after repeated failures, auto-recover after cooldown
- **Dead-letter queue** — persistent store for messages that can't be delivered
- **Recovery callback** — what happens after all retries are exhausted
- The rule: every message ends up somewhere. Delivered OR dead-lettered. Never vanished.
- Test error paths explicitly — simulate failures with Testcontainers

---

[Next: Chapter 8 — "Process 10,000 Messages" →](chapter-08-concurrency.md)

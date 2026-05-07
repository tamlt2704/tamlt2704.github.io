# Chapter 9: Don't Lose Messages When the Server Restarts

[← Chapter 8: Process 10,000 Messages](chapter-08-concurrency.md) | [Chapter 10: Prove Every Message Was Delivered →](chapter-10-observability.md)

---

## The Disaster

It's 3am. The server runs out of memory (a different service leaked). Kubernetes restarts the pod. Your `QueueChannel` had 847 messages buffered in memory. They're gone. Poof. No trace.

Monday morning: 847 lab results never reached the hospitals. Dr. Patel's patients are waiting for results that will never arrive — unless someone manually re-sends them from the lab system. The lab system doesn't have a "re-send" button.

Miriam:

> "In-memory queues are fine for development. Production needs persistent message stores. If the server dies, messages survive."

---

## The Problem: In-Memory State

```java
// This queue lives in RAM. Server dies = messages die.
@Bean
public MessageChannel processingQueue() {
    return new QueueChannel(1000);  // Gone on restart
}
```

The aggregator from Chapter 4 also holds state in memory — partial message groups waiting for completion. Restart = partial groups lost = batches never complete.

---

## JdbcChannelMessageStore: Persistent Queues

```groovy
// build.gradle — add JDBC support
implementation 'org.springframework.integration:spring-integration-jdbc'
implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
runtimeOnly 'org.postgresql:postgresql'
```

```java
// src/main/java/com/medibridge/config/MessageStoreConfig.java
package com.medibridge.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.integration.jdbc.store.JdbcChannelMessageStore;
import org.springframework.integration.jdbc.store.channel.PostgresChannelMessageStoreQueryProvider;

import javax.sql.DataSource;

@Configuration
public class MessageStoreConfig {

    @Bean
    public JdbcChannelMessageStore messageStore(DataSource dataSource) {
        JdbcChannelMessageStore store = new JdbcChannelMessageStore(dataSource);
        store.setChannelMessageStoreQueryProvider(new PostgresChannelMessageStoreQueryProvider());
        store.setRegion("MEDIBRIDGE");
        return store;
    }
}
```

### Schema

Spring Integration provides the schema. For PostgreSQL:

```sql
-- From spring-integration-jdbc JAR: org/springframework/integration/jdbc/schema-postgresql.sql
CREATE TABLE INT_CHANNEL_MESSAGE (
    MESSAGE_ID CHAR(36) NOT NULL,
    GROUP_KEY CHAR(36) NOT NULL,
    REGION VARCHAR(100) NOT NULL,
    CREATED_DATE BIGINT NOT NULL,
    MESSAGE_PRIORITY BIGINT,
    MESSAGE_SEQUENCE BIGINT NOT NULL DEFAULT NEXTVAL('INT_MESSAGE_SEQ'),
    MESSAGE_BYTES BYTEA,
    CONSTRAINT INT_CHANNEL_MESSAGE_PK PRIMARY KEY (REGION, GROUP_KEY, MESSAGE_ID)
);

CREATE SEQUENCE INT_MESSAGE_SEQ;

CREATE TABLE INT_GROUP_TO_MESSAGE (
    GROUP_KEY CHAR(36) NOT NULL,
    MESSAGE_ID CHAR(36) NOT NULL,
    REGION VARCHAR(100) NOT NULL
);

CREATE TABLE INT_MESSAGE_GROUP (
    GROUP_KEY CHAR(36) NOT NULL,
    REGION VARCHAR(100) NOT NULL,
    COMPLETE BIGINT,
    LAST_RELEASED_SEQUENCE BIGINT,
    CREATED_DATE BIGINT NOT NULL,
    UPDATED_DATE BIGINT DEFAULT 0,
    CONSTRAINT INT_MESSAGE_GROUP_PK PRIMARY KEY (REGION, GROUP_KEY)
);
```

### Use the Persistent Queue

```java
@Bean
public IntegrationFlow persistentQueueFlow(JdbcChannelMessageStore messageStore) {
    return IntegrationFlow
        .from(Files.inboundAdapter(new File("input/labs"))
                .autoCreateDirectory(true)
                .patternFilter("*.hl7"),
            e -> e.poller(Pollers.fixedDelay(1000)))
        .transform(Files.toStringTransformer())
        // Persistent queue — survives restarts
        .channel(c -> c.queue(messageStore, "lab-processing-queue"))
        .get();
}

@Bean
public IntegrationFlow labConsumerFlow(
        JdbcChannelMessageStore messageStore,
        Hl7ToJsonTransformer transformer) {
    return IntegrationFlow
        .from("lab-processing-queue")  // Reads from persistent store
        .bridge(e -> e.poller(Pollers.fixedDelay(100)
            .maxMessagesPerPoll(10)
            .taskExecutor(labProcessingExecutor())
            .transactional()))  // Each poll is transactional!
        .transform(transformer, "transform")
        .handle(/* ... */)
        .get();
}
```

Now messages are stored in PostgreSQL. If the server restarts:
1. Unprocessed messages remain in the `INT_CHANNEL_MESSAGE` table
2. On startup, the poller resumes reading from where it left off
3. Zero messages lost

---

## Transactions: All-or-Nothing Processing

The `.transactional()` on the poller means: read the message from the store AND process it in a single transaction. If processing fails, the transaction rolls back, and the message stays in the store for retry.

```java
@Bean
public IntegrationFlow transactionalFlow(JdbcChannelMessageStore messageStore) {
    return IntegrationFlow.from("persistent-queue")
        .bridge(e -> e.poller(Pollers.fixedDelay(100)
            .transactional()  // Read + process in one transaction
            .maxMessagesPerPoll(1)))
        .transform(transformer, "transform")
        .handle(sftpOutboundAdapter)
        .get();
}
```

**Without transaction**: Message read from store → processing fails → message already removed from store → LOST.

**With transaction**: Message read from store → processing fails → transaction rolls back → message stays in store → retried on next poll.

---

## Persistent Aggregator Groups

The aggregator from Chapter 4 holds partial groups in memory. Make it persistent:

```java
@Bean
public IntegrationFlow persistentAggregatorFlow(JdbcChannelMessageStore messageStore) {
    return IntegrationFlow.from("splitLabChannel")
        .aggregate(a -> a
            .messageStore(messageStore)  // Groups stored in DB
            .correlationStrategy(msg ->
                msg.getHeaders().get(IntegrationMessageHeaderAccessor.CORRELATION_ID))
            .releaseStrategy(group ->
                group.size() == group.getSequenceSize())
            .groupTimeout(60_000)
            .sendPartialResultOnExpiry(true)
            .expireGroupsUponCompletion(true))
        .channel("aggregatedLabChannel")
        .get();
}
```

Now if the server restarts mid-batch:
- Partial groups survive in the database
- On restart, the aggregator picks up where it left off
- When the remaining messages arrive, the group completes normally

---

## Idempotent Processing: Handle Duplicates

With persistent stores and retries, a message might be processed more than once (read from store, process, crash before marking complete). Your handlers must be **idempotent** — processing the same message twice produces the same result.

```java
@Bean
public IntegrationFlow idempotentFlow(JdbcMetadataStore metadataStore) {
    return IntegrationFlow.from("labChannel")
        // Idempotent receiver — skip messages we've already processed
        .filter(Message.class,
            msg -> {
                String messageId = msg.getHeaders().getId().toString();
                String existing = metadataStore.get(messageId);
                if (existing != null) {
                    System.out.println("Duplicate detected, skipping: " + messageId);
                    return false;  // Already processed
                }
                return true;
            })
        .transform(transformer, "transform")
        .handle((payload, headers) -> {
            // Process...
            // Mark as processed AFTER successful handling
            metadataStore.put(headers.getId().toString(), "PROCESSED");
            return null;
        })
        .get();
}
```

---

## Claim Check Pattern: Large Messages

Lab results are small (KB). But imaging results (X-rays, MRIs) can be 50MB+. Storing those in the message store bloats the database.

The **claim check** pattern: store the large payload externally, pass only a reference through the flow.

```java
@Bean
public IntegrationFlow claimCheckFlow() {
    return IntegrationFlow.from("largeMessageChannel")
        // Store payload, replace with claim ticket
        .claimCheckIn(messageStore())
        // Now the message payload is just a UUID (the claim ticket)
        .transform(/* lightweight processing on metadata only */)
        .route(/* routing based on headers, not payload */)
        // Retrieve the full payload when needed
        .claimCheckOut(messageStore())
        // Now the full payload is back
        .handle(/* final processing */)
        .get();
}
```

---

## Testing Persistence

```java
@SpringBootTest
@SpringIntegrationTest
class PersistentQueueTest {

    @Autowired
    private JdbcChannelMessageStore messageStore;

    @Autowired
    @Qualifier("lab-processing-queue")
    private MessageChannel persistentQueue;

    @Test
    void messageSurvivesSimulatedRestart() {
        // Send a message to the persistent queue
        persistentQueue.send(MessageBuilder
            .withPayload("MSH|^~\\&|LAB|MB|HOSP_A...")
            .setHeader("batchId", "BATCH-001")
            .build());

        // Verify it's in the store
        assertThat(messageStore.getMessageCount("lab-processing-queue")).isEqualTo(1);

        // Simulate restart: don't process it, just verify it persists
        // (In a real test, you'd restart the Spring context)

        // Message is still there
        Message<?> retrieved = messageStore.pollMessageFromGroup("lab-processing-queue");
        assertThat(retrieved).isNotNull();
        assertThat(retrieved.getPayload().toString()).contains("MSH|");
    }
}
```

---

## Report to Miriam

> **Message persistence implemented:**
> - `QueueChannel` backed by `JdbcChannelMessageStore` — messages survive restarts
> - Transactional polling — message stays in store until processing succeeds
> - Aggregator groups persisted — partial batches survive restarts
> - Idempotent receiver — duplicate messages detected and skipped
> - Claim check pattern ready for large payloads (imaging results)
>
> The 847 lost messages? Impossible now. They'd be in PostgreSQL, waiting to be processed after restart.

Miriam: "One last thing. Compliance Carl wants proof that every message was delivered. Wire tap, audit trail, metrics. He wants dashboards."

---

## What You Learned

- **In-memory channels lose messages on restart** — use `JdbcChannelMessageStore` for production
- **Transactional polling** ensures messages aren't removed from the store until processing succeeds
- **Persistent aggregator groups** survive restarts — partial batches complete normally after recovery
- **Idempotent receivers** handle duplicate delivery — same message processed twice = same result
- **Claim check pattern** keeps large payloads out of the message store
- The schema is provided by Spring Integration — just run the SQL
- **`CallerRunsPolicy`** + persistent queue = no message loss even under extreme load
- Test persistence explicitly — verify messages survive simulated restarts

---

[Next: Chapter 10 — "Prove Every Message Was Delivered" →](chapter-10-observability.md)

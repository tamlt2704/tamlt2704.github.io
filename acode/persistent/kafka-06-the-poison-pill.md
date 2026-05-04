# Chapter 6: The Poison Pill — "One Bad Message Killed the Entire Pipeline"

[← The Consumer Lag Crisis](kafka-05-the-consumer-lag-crisis.md) | [Next: The Rebalance Storm →](kafka-07-the-rebalance-storm.md)

---

Wednesday. The inventory team deployed a schema change to their producer. They added a field and changed the serialization format. They didn't tell anyone.

One malformed message enters `order-events`. Your payment consumer tries to deserialize it. Fails. Retries. Fails. Retries. Fails. Forever.

PagerDuty fires:

> **ALERT**: Consumer group `payment-service` — lag increasing, no progress for 10 minutes.

You check the logs:

```
ERROR o.s.k.l.KafkaMessageListenerContainer
  - Error handler threw an exception
Caused by: DeserializationException:
  Can't deserialize data from topic order-events
  ...
ERROR o.s.k.l.KafkaMessageListenerContainer
  - Error handler threw an exception
Caused by: DeserializationException:
  Can't deserialize data from topic order-events
  ...
(repeating every 100ms, forever)
```

Raj walks over:

> "Poison pill. One bad message blocks every message behind it. The consumer is stuck in an infinite retry loop because it can't skip past a message it can't read."

---

## The Default Behavior (Dangerous)

```
Bad message → DeserializationException
  → consumer retries → same exception → retries
  → same exception → retries → forever
  ↑ Consumer is STUCK. All messages behind this are blocked.
```

Spring Kafka's default error handler retries 10 times, then... retries 10 more times. For a deserialization error, retrying is pointless — the bytes won't magically become valid JSON on the 11th attempt.

---

## Step 1: Write a Test That Proves the Bug

```java
// src/test/java/com/eventstream/consumer/PoisonPillTest.java
@EmbeddedKafka(partitions = 1, topics = "order-events")
@SpringBootTest
class PoisonPillTest {

    @Autowired
    private KafkaTemplate<String, String> rawKafka;

    @Test
    void badMessage_blocksConsumer() throws Exception {
        // Send garbage that can't deserialize to OrderEvent
        rawKafka.send("order-events", "ORD-BAD",
            "{invalid json!!!}").get();

        // Send a valid message AFTER the bad one
        rawKafka.send("order-events", "ORD-GOOD",
            "{\"orderId\":\"ORD-GOOD\"}").get();

        Thread.sleep(5000);
        // ⚠️ BUG: ORD-GOOD is never processed because
        // the consumer is stuck retrying ORD-BAD
    }
}
```

---

## Step 2: Fix — Dead Letter Topic + Error Classification

```java
// src/main/java/com/eventstream/config/KafkaErrorConfig.java
@Configuration
public class KafkaErrorConfig {

    @Bean
    public DefaultErrorHandler errorHandler(
            KafkaTemplate<String, Object> kafka) {
        var recoverer = new DeadLetterPublishingRecoverer(
            kafka,
            (record, ex) -> new TopicPartition(
                record.topic() + ".DLT",
                record.partition()));

        var handler = new DefaultErrorHandler(
            recoverer, new FixedBackOff(1000L, 2));

        // Don't retry deserialization errors — pointless
        handler.addNotRetryableExceptions(
            DeserializationException.class);

        return handler;
    }
}
```

This does:

1. **Transient errors** (DB down, network timeout) → retry 2 times with 1-second backoff
2. **Still failing** → send to `order-events.DLT` (dead letter topic)
3. **Consumer moves on** to the next message
4. **`DeserializationException`** → skip retries entirely, straight to DLT

---

## Step 3: Monitor the Dead Letter Topic

```java
// src/main/java/com/eventstream/consumer/DltMonitor.java
@Service
@Slf4j
public class DltMonitor {

    @KafkaListener(
        topics = "order-events.DLT",
        groupId = "dlt-monitor")
    public void handleDeadLetter(
            ConsumerRecord<String, byte[]> record) {
        log.error("Dead letter: topic={} key={} p={} offset={}",
            record.topic(), record.key(),
            record.partition(), record.offset());
        // Alert to Slack/PagerDuty
        // Store for manual inspection
    }
}
```

---

## Step 4: Test That Proves the Fix

```java
// src/test/java/com/eventstream/consumer/PoisonPillTest.java
@Test
void withDLT_badMessageIsSkipped_goodMessageProcessed()
        throws Exception {
    rawKafka.send("order-events", "ORD-BAD",
        "{invalid json!!!}").get();
    rawKafka.send("order-events", "ORD-GOOD",
        validOrderJson("ORD-GOOD")).get();

    Thread.sleep(5000);

    // ✅ Bad message went to DLT
    // ✅ Good message was processed normally
    assertThat(paymentRepo.existsByOrderId("ORD-GOOD"))
        .isTrue();
}
```

Test goes green. The poison pill goes to the DLT. The pipeline keeps flowing.

---

## The Error Handling Decision Tree

```
Message fails
  ├── Transient error? (DB down, network timeout)
  │     → Retry with backoff (2-3 attempts)
  │         ├── Recovers → ✅ continue
  │         └── Still failing → send to DLT
  │
  └── Permanent error? (bad data, schema mismatch)
        → Don't retry → send to DLT immediately
```

Sana reviews the PR:

> "Good. Set up a Slack alert on the DLT consumer. If dead letters spike, we know a producer broke their contract."

You deploy. The pipeline is resilient now. But Thursday morning, something worse happens — the consumers start rebalancing every 30 seconds.

*That's [Chapter 7](kafka-07-the-rebalance-storm.md).*

---

[← The Consumer Lag Crisis](kafka-05-the-consumer-lag-crisis.md) | [Next: The Rebalance Storm →](kafka-07-the-rebalance-storm.md)

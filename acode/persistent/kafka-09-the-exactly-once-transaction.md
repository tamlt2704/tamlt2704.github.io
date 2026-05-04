# Chapter 9: The Exactly-Once Transaction — "We Moved to Kafka Streams and Money Went Missing"

[← The Schema Evolution](kafka-08-the-schema-evolution.md) | [Next: The Production Checklist →](kafka-10-the-production-checklist.md)

---

You build a Kafka Streams enrichment app. It reads from `order-events`, looks up customer data, and writes enriched orders to `enriched-orders`. Simple pipeline.

It works great — until the app crashes mid-transaction during a deploy. On restart, some messages get processed again. Duplicate enriched orders appear in the output topic. The analytics team reports inflated revenue numbers.

Sana is not happy:

> "The CFO just asked why revenue jumped 12% overnight. It didn't. Your enrichment app double-counted orders."

---

## The Problem: Read-Process-Write Atomicity

```
Read from order-events
  → Process (enrich with customer data)
    → Write to enriched-orders
      → Commit consumer offset
                ↑ crash here
        ↑ already written

Result: on restart, message is reprocessed
  → duplicate in enriched-orders
```

The read, the write, and the offset commit are three separate operations. If the app crashes after writing but before committing the offset, the message gets reprocessed.

---

## The Buggy Code

```java
// src/main/java/com/eventstream/stream/EnrichmentProcessor.java
// ⚠️ BUG: no transactional guarantee across read-process-write
@KafkaListener(
    topics = "order-events",
    groupId = "enrichment-service")
public void process(OrderEvent event) {
    EnrichedOrder enriched = enrich(event);
    kafka.send("enriched-orders",
        event.orderId(), enriched);
    // Offset auto-committed AFTER this method returns.
    // Crash between send() and offset commit = duplicate.
}
```

---

## Step 1: Write a Test That Proves the Bug

```java
// src/test/java/com/eventstream/stream/ExactlyOnceTest.java
@EmbeddedKafka(
    partitions = 1,
    topics = {"order-events", "enriched-orders"})
@SpringBootTest
class ExactlyOnceTest {

    @Autowired
    private KafkaTemplate<String, OrderEvent> kafka;
    @Autowired
    private Consumer<String, EnrichedOrder> testConsumer;

    @Test
    void withoutTransactions_crashCausesDuplicates()
            throws Exception {
        var event = new OrderEvent("ORD-TX-001", "CUST-1",
            new BigDecimal("200.00"),
            OrderStatus.CREATED, Instant.now());

        // Send same event, simulating reprocessing after crash
        kafka.send("order-events", event.orderId(), event).get();
        kafka.send("order-events", event.orderId(), event).get();

        Thread.sleep(5000);

        var records = KafkaTestUtils.getRecords(testConsumer);
        // ⚠️ BUG: 2 enriched orders for the same event
        assertThat(records.count()).isEqualTo(2);
    }
}
```

---

## Step 2: Fix — Kafka Transactions

### Config

```yaml
# src/main/resources/application.yml
spring:
  kafka:
    producer:
      transaction-id-prefix: eventstream-tx-
      properties:
        enable.idempotence: true
    consumer:
      properties:
        isolation.level: read_committed
```

`isolation.level: read_committed` — downstream consumers only see messages from **committed** transactions. Aborted transaction messages are invisible.

### Transactional Read-Process-Write

```java
// src/main/java/com/eventstream/stream/EnrichmentProcessor.java
@Service
@RequiredArgsConstructor
public class EnrichmentProcessor {

    private final KafkaTemplate<String, EnrichedOrder> kafka;

    @KafkaListener(
        topics = "order-events",
        groupId = "enrichment-service")
    public void process(OrderEvent event) {
        kafka.executeInTransaction(ops -> {
            EnrichedOrder enriched = enrich(event);
            ops.send("enriched-orders",
                event.orderId(), enriched);
            return true;
            // Consumer offset + producer write = atomic
        });
    }
}
```

---

## Step 3: Test That Proves the Fix

```java
// src/test/java/com/eventstream/stream/ExactlyOnceTest.java
@Test
void withTransactions_noDuplicatesInOutput()
        throws Exception {
    var event = new OrderEvent("ORD-TX-002", "CUST-1",
        new BigDecimal("200.00"),
        OrderStatus.CREATED, Instant.now());

    kafka.send("order-events", event.orderId(), event).get();

    Thread.sleep(5000);

    var records = KafkaTestUtils.getRecords(testConsumer);
    long count = StreamSupport
        .stream(records.spliterator(), false)
        .filter(r -> r.key().equals("ORD-TX-002"))
        .count();

    assertThat(count).isEqualTo(1); // ✅ Exactly one
}
```

Test goes green. The transaction ensures the output write and offset commit are atomic.

---

## The Exactly-Once Spectrum

```
──────────────────┬──────────────────────────────────┬──────────────────────
 Guarantee        │ How                              │ Cost
──────────────────┼──────────────────────────────────┼──────────────────────
 At-most-once     │ Commit offset before processing  │ Messages can be lost
──────────────────┼──────────────────────────────────┼──────────────────────
 At-least-once    │ Commit offset after processing   │ Best default — use
                  │ + idempotent consumer             │ with Chapter 3 dedup
──────────────────┼──────────────────────────────────┼──────────────────────
 Exactly-once     │ Kafka transactions               │ Higher latency,
                  │                                  │ lower throughput
──────────────────┴──────────────────────────────────┴──────────────────────
```

Raj gives you the senior insight:

> "True exactly-once is expensive. For most services, **at-least-once + idempotent consumers** ([Chapter 3](kafka-03-the-duplicate-payment.md)) is the right tradeoff. Reserve Kafka transactions for stream processing pipelines where read-process-write must be atomic. Don't reach for the heaviest tool when a lighter one works."

You nod. The enrichment pipeline is solid. Derek schedules the final architecture review before launch.

*That's [Chapter 10](kafka-10-the-production-checklist.md).*

---

[← The Schema Evolution](kafka-08-the-schema-evolution.md) | [Next: The Production Checklist →](kafka-10-the-production-checklist.md)

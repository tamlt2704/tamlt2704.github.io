# Chapter 3: The Duplicate Payment — "We Charged the Customer Twice"

[← The Lost Order Incident](kafka-02-the-lost-order-incident.md) | [Next: The Outbox Pattern →](kafka-04-the-outbox-pattern.md)

---

Week three. Slack from the finance team:

> **#finance**: "Customer #9201 was charged $500 twice for the same order. Please advise."

You check the payment service logs. Two entries for `ORD-3847`. Same amount, same customer, two seconds apart. Your stomach drops.

Raj doesn't even look surprised:

> "Kafka retried a message. Your consumer processed it twice. You didn't build idempotency."

---

## Why Duplicates Happen

Raj draws the timeline:

```
Producer → sends message → network timeout
  → producer retries → Kafka now has 2 copies
                          ↓
Consumer reads both → charges customer twice
```

> "Even with `enable.idempotence=true` on the producer, the **consumer** can still see duplicates. Consumer processes a message, crashes before committing the offset. On restart, it re-reads the same message."

---

## The Buggy Consumer

This is what you deployed in [Chapter 1](kafka-01-the-genesis.md):

```java
// src/main/java/com/eventstream/consumer/PaymentConsumer.java
// ⚠️ BUG: no idempotency check — processes duplicates
@KafkaListener(
    topics = "order-events",
    groupId = "payment-service")
public void handle(OrderEvent event) {
    if (event.status() == OrderStatus.CREATED) {
        paymentRepo.save(new Payment(
            event.orderId(), event.amount(),
            PaymentStatus.CHARGED));
        // Duplicate message? Charged twice. Oops.
    }
}
```

---

## Step 1: Write a Test That Proves the Bug

```java
// src/test/java/com/eventstream/consumer/DuplicatePaymentTest.java
@EmbeddedKafka(partitions = 1, topics = "order-events")
@SpringBootTest
class DuplicatePaymentTest {

    @Autowired private PaymentRepository paymentRepo;
    @Autowired private KafkaTemplate<String, OrderEvent> kafka;

    @Test
    void duplicateMessage_chargesCustomerTwice() throws Exception {
        var event = new OrderEvent("ORD-3847", "CUST-9201",
            new BigDecimal("500.00"),
            OrderStatus.CREATED, Instant.now());

        // Simulate Kafka retry — same message sent twice
        kafka.send("order-events", event.orderId(), event).get();
        kafka.send("order-events", event.orderId(), event).get();

        Thread.sleep(3000); // wait for consumer

        long count = paymentRepo.countByOrderId("ORD-3847");
        // ⚠️ BUG: count is 2 — customer charged twice!
        assertThat(count).isEqualTo(2);
    }
}
```

Test passes. Two payments for the same order. That's the bug.

---

## Step 2: Fix — Idempotent Consumer with DB Dedup

```java
// src/main/java/com/eventstream/consumer/PaymentConsumer.java
@Service
@RequiredArgsConstructor
public class PaymentConsumer {

    private final PaymentRepository paymentRepo;

    @KafkaListener(
        topics = "order-events",
        groupId = "payment-service")
    public void handle(OrderEvent event) {
        if (event.status() != OrderStatus.CREATED) return;

        // Idempotency check — already processed?
        if (paymentRepo.existsByOrderId(event.orderId())) {
            return; // Skip duplicate
        }

        paymentRepo.save(new Payment(
            event.orderId(), event.amount(),
            PaymentStatus.CHARGED));
    }
}
```

**Rule**: Every Kafka consumer must be idempotent. Processing the same message twice must produce the same result.

---

## Step 3: Test That Proves the Fix

```java
// src/test/java/com/eventstream/consumer/DuplicatePaymentTest.java
@Test
void withIdempotency_duplicateIsIgnored() throws Exception {
    var event = new OrderEvent("ORD-3848", "CUST-9201",
        new BigDecimal("500.00"),
        OrderStatus.CREATED, Instant.now());

    kafka.send("order-events", event.orderId(), event).get();
    kafka.send("order-events", event.orderId(), event).get();

    Thread.sleep(3000);

    long count = paymentRepo.countByOrderId("ORD-3848");
    assertThat(count).isEqualTo(1); // ✅ Only charged once
}
```

Test goes green. Duplicate ignored.

---

## Bonus: Bloom Filter for High Throughput

Raj leans over:

> "That DB check on every message? At 50K messages/sec, that's 50K queries/sec just for dedup. Use a Bloom filter."

```java
// src/main/java/com/eventstream/consumer/PaymentConsumer.java
@Service
public class PaymentConsumer {

    private final BloomFilter<String> processed =
        BloomFilter.create(
            Funnels.stringFunnel(StandardCharsets.UTF_8),
            10_000_000, 0.01);
    private final PaymentRepository paymentRepo;

    @KafkaListener(
        topics = "order-events",
        groupId = "payment-service")
    public void handle(OrderEvent event) {
        if (event.status() != OrderStatus.CREATED) return;

        if (processed.mightContain(event.orderId())) {
            if (paymentRepo.existsByOrderId(event.orderId()))
                return;
        }

        paymentRepo.save(new Payment(
            event.orderId(), event.amount(),
            PaymentStatus.CHARGED));
        processed.put(event.orderId());
    }
}
```

The Bloom filter eliminates 99% of DB lookups for duplicates. The 1% false positive rate just means an unnecessary (but harmless) DB check. No false negatives — if the filter says "not seen", it's definitely new.

Sana merges your PR. You feel good. Then Raj says:

> "What happens when the DB commits but Kafka is down? The event is lost."

*He's right. We'll discover that in [Chapter 4](kafka-04-the-outbox-pattern.md).*

---

[← The Lost Order Incident](kafka-02-the-lost-order-incident.md) | [Next: The Outbox Pattern →](kafka-04-the-outbox-pattern.md)

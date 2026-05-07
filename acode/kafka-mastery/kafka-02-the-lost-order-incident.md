# Chapter 2: The Lost Order Incident — "The Customer Paid But We Never Shipped"

[← The Genesis](kafka-01-the-genesis.md) | [Next: The Duplicate Payment →](kafka-03-the-duplicate-payment.md)

---

Week two. Friday afternoon. Slack lights up:

> **#customer-support**: "Customer #8842 paid $320 but order never shipped. Shipping service says it never received the event."

Sana assigns you the ticket. You check the order service logs — it published the event. You check the shipping consumer logs — nothing. The message vanished between producer and broker.

Raj pulls up a chair:

> "Show me your producer config."

You show him. He sighs.

> "Fire and forget. No acks. The producer sent the message, got a network blip, and moved on. Kafka never received it."

---

## The Buggy Code

This is what you deployed in [Chapter 1](kafka-01-the-genesis.md):

```java
// src/main/java/com/eventstream/producer/OrderEventProducer.java
// ⚠️ BUG: fire-and-forget — no acknowledgment, no error handling
public void publish(OrderEvent event) {
    kafka.send("order-events", event.orderId(), event);
    // Producer returned, but message might not be in Kafka.
    // Network blip → message lost → customer never ships.
}
```

By default, the producer doesn't wait for Kafka to acknowledge. The `send()` returns a `CompletableFuture` that you're ignoring. The message can vanish and you'll never know.

---

## Step 1: Write a Test That Proves the Bug

```java
// src/test/java/com/eventstream/producer/ProducerAcksTest.java
@EmbeddedKafka(partitions = 1, topics = "order-events")
@SpringBootTest
class ProducerAcksTest {

    @Autowired
    private KafkaTemplate<String, OrderEvent> kafka;

    @Test
    void fireAndForget_canLoseMessages() {
        var event = new OrderEvent(
            "ORD-001", "CUST-1", new BigDecimal("320.00"),
            OrderStatus.CREATED, Instant.now());

        // ⚠️ BUG: no .get(), no callback — we never know if it arrived
        kafka.send("order-events", event.orderId(), event);

        // In production, a network blip here = lost message.
        // We can't even assert failure — that's the problem.
    }
}
```

The test "passes" — but that's exactly the bug. You can't detect failure when you don't check for it.

---

## Step 2: Understand Why

Raj draws on the whiteboard:

```
Producer → send() → [network] → Broker
                        ↑
              acks=0: don't wait
              acks=1: wait for leader
              acks=all: wait for ALL replicas
```

> "With `acks=0` (the effective default when you ignore the future), the producer doesn't wait. With `acks=all`, the leader AND all in-sync replicas must confirm. Combined with `enable.idempotence=true`, retries won't create duplicates on the broker side."

---

## Step 3: Fix the Config

```yaml
# src/main/resources/application.yml
spring:
  kafka:
    producer:
      acks: all
      retries: 3
      properties:
        enable.idempotence: true
        max.in.flight.requests.per.connection: 5
        delivery.timeout.ms: 120000
```

---

## Step 4: Fix the Producer

```java
// src/main/java/com/eventstream/producer/OrderEventProducer.java
@Service
@RequiredArgsConstructor
@Slf4j
public class OrderEventProducer {

    private final KafkaTemplate<String, OrderEvent> kafka;

    public CompletableFuture<SendResult<String, OrderEvent>>
            publish(OrderEvent event) {
        return kafka.send(
            "order-events", event.orderId(), event
        ).whenComplete((result, ex) -> {
            if (ex != null) {
                log.error("Failed to publish order {}: {}",
                    event.orderId(), ex.getMessage());
                // Store to outbox for retry — Chapter 4
            } else {
                log.debug("Published order {} to p{} offset {}",
                    event.orderId(),
                    result.getRecordMetadata().partition(),
                    result.getRecordMetadata().offset());
            }
        });
    }
}
```

---

## Step 5: Test That Proves the Fix

```java
// src/test/java/com/eventstream/producer/ProducerAcksTest.java
@Test
void withAcksAll_messageIsConfirmed() throws Exception {
    var event = new OrderEvent(
        "ORD-002", "CUST-1", new BigDecimal("320.00"),
        OrderStatus.CREATED, Instant.now());

    SendResult<String, OrderEvent> result =
        kafka.send("order-events", event.orderId(), event)
            .get(10, TimeUnit.SECONDS);

    assertThat(result.getRecordMetadata().offset())
        .isGreaterThanOrEqualTo(0);
    assertThat(result.getRecordMetadata().topic())
        .isEqualTo("order-events");
}
```

Test goes green. The producer now **waits** for Kafka to confirm. If the broker is down, you get an exception instead of silent data loss.

---

## The Delivery Guarantees Cheat Sheet

```
────────┬──────────────────────────┬──────────┬──────────────────────────────
 acks   │ Durability               │ Latency  │ When to Use
────────┼──────────────────────────┼──────────┼──────────────────────────────
 0      │ None — fire and forget   │ Lowest   │ Metrics, logs you can lose
────────┼──────────────────────────┼──────────┼──────────────────────────────
 1      │ Leader only              │ Medium   │ Most use cases
────────┼──────────────────────────┼──────────┼──────────────────────────────
 all    │ All in-sync replicas     │ Highest  │ Money, orders, anything
        │                          │          │ you can't afford to lose
────────┴──────────────────────────┴──────────┴──────────────────────────────
```

Sana reviews your PR:

> "Good. But you fixed the producer. The consumer still has bugs."

*She's right. We'll discover them in [Chapter 3](kafka-03-the-duplicate-payment.md).*

---

[← The Genesis](kafka-01-the-genesis.md) | [Next: The Duplicate Payment →](kafka-03-the-duplicate-payment.md)

# Chapter 1: The Genesis — "We Just Need a Message Queue"

[← Overview](kafka-00-overview.md) | [Next: The Lost Order Incident →](kafka-02-the-lost-order-incident.md)

---

Your first Monday at EventStream. Derek is at the whiteboard:

> "Orders, payments, inventory — they need to talk. Kafka. Ship it."

He walks out. Sana turns to you:

> "Kafka isn't a message queue. It's a **distributed commit log**. Messages aren't deleted after consumption — they sit on disk, ordered, replayable. Think of it as a sharded append-only table."

She draws this on the whiteboard:

```
Producer → [ Topic: order-events ]
              ├── Partition 0: [msg0, msg3, msg6 ...]
              ├── Partition 1: [msg1, msg4, msg7 ...]
              └── Partition 2: [msg2, msg5, msg8 ...]
                                    ↑
                    Consumer Group A (3 consumers)
                    Consumer Group B (2 consumers)
```

> "Partitions are the shards. Consumer groups are independent cursors. Each consumer in a group reads from different partitions. Two groups can read the same topic independently."

You nod. You open IntelliJ. How hard can it be?

---

## The Order Event

```java
// src/main/java/com/eventstream/event/OrderEvent.java
public record OrderEvent(
    String orderId,
    String customerId,
    BigDecimal amount,
    OrderStatus status,
    Instant occurredAt
) {}
```

Four statuses: `CREATED`, `PAID`, `SHIPPED`, `CANCELLED`. Simple.

---

## The Producer — Your First Attempt

```java
// src/main/java/com/eventstream/producer/OrderEventProducer.java
@Service
@RequiredArgsConstructor
public class OrderEventProducer {

    private final KafkaTemplate<String, OrderEvent> kafka;

    // ⚠️ BUG: fire-and-forget — no error handling
    public void publish(OrderEvent event) {
        kafka.send("order-events", event.orderId(), event);
    }
}
```

You key on `orderId`. Kafka hashes the key to pick a partition. Same key = same partition = **guaranteed ordering** for that order. This is the single most important Kafka concept.

*This has bugs. We'll discover them in [Chapter 2](kafka-02-the-lost-order-incident.md).*

---

## The Consumer

```java
// src/main/java/com/eventstream/consumer/PaymentConsumer.java
@Service
@Slf4j
public class PaymentConsumer {

    @KafkaListener(
        topics = "order-events",
        groupId = "payment-service"
    )
    public void handle(OrderEvent event) {
        if (event.status() == OrderStatus.CREATED) {
            log.info("Processing payment for order {}",
                event.orderId());
            // charge the customer
        }
    }
}
```

*This also has bugs. We'll discover them in [Chapter 3](kafka-03-the-duplicate-payment.md).*

---

## Minimal Config

```yaml
# src/main/resources/application.yml
spring:
  kafka:
    bootstrap-servers: localhost:9092
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
    consumer:
      group-id: payment-service
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.springframework.kafka.support.serializer.JsonDeserializer
      properties:
        spring.json.trusted.packages: "com.eventstream.*"
      auto-offset-reset: earliest
```

`auto-offset-reset: earliest` — when a new consumer group appears, start from the beginning. Use `latest` if you only care about new messages. Get this wrong and you either miss history or reprocess everything.

---

## You Deploy

You push to `main`. CI/CD deploys to staging. You send a few test orders. The consumer picks them up. Payments get processed.

Raj walks by your desk, glances at your screen, and says:

> "This works on your laptop. In production, messages will vanish."

You laugh. He doesn't.

---

[← Overview](kafka-00-overview.md) | [Next: The Lost Order Incident →](kafka-02-the-lost-order-incident.md)

# Chapter 5: The Consumer Lag Crisis — "We're 2 Million Messages Behind"

[← The Outbox Pattern](kafka-04-the-outbox-pattern.md) | [Next: The Poison Pill →](kafka-06-the-poison-pill.md)

---

Monday morning. You open Grafana. The consumer lag dashboard is bright red.

Sana pings you on Slack:

> **Sana**: "Notification service has 2M lag. Customers aren't getting shipping emails. Derek is asking why."

You pull up the numbers:

```
Topic: order-events (3 partitions)
  Partition 0: latest offset = 5,000,000
  Partition 1: latest offset = 4,800,000
  Partition 2: latest offset = 5,100,000

Consumer Group: notification-service
  Partition 0: committed offset = 4,200,000  → lag: 800,000
  Partition 1: committed offset = 4,100,000  → lag: 700,000
  Partition 2: committed offset = 4,600,000  → lag: 500,000
                                        Total lag: 2,000,000
```

The notification consumer processes one message at a time. Each one triggers an email API call that takes 50ms. At 20 messages/sec, it'll take **28 hours** to catch up — while new messages keep arriving.

Raj looks at the dashboard:

> "Three partitions, one consumer instance. You're leaving parallelism on the table."

---

## The Buggy Setup

```java
// src/main/java/com/eventstream/consumer/NotificationConsumer.java
// ⚠️ BUG: single-threaded, one-at-a-time processing
@KafkaListener(
    topics = "order-events",
    groupId = "notification-service")
public void handle(OrderEvent event) {
    if (event.status() == OrderStatus.SHIPPED) {
        emailService.send(event.customerId(),
            "Your order " + event.orderId() + " shipped!");
        // 50ms per email × millions of messages = disaster
    }
}
```

---

## Fix 1: Increase Partitions + Consumers

Kafka's parallelism unit is the partition. 3 partitions = max 3 consumers in a group.

```bash
# Increase to 12 partitions (can't decrease later!)
kafka-topics.sh --alter \
  --topic order-events \
  --partitions 12 \
  --bootstrap-server localhost:9092
```

Then scale to 12 consumer instances. Each gets 1 partition.

**Warning**: Increasing partitions **breaks key ordering** for existing data. New messages with the same key may land on a different partition than before. Plan partition count upfront.

*This is why [Chapter 10](kafka-10-the-production-checklist.md) says start with 12+ partitions.*

---

## Fix 2: Batch Consumption

Instead of one message at a time, consume in batches:

```java
// src/main/java/com/eventstream/consumer/NotificationConsumer.java
@KafkaListener(
    topics = "order-events",
    groupId = "notification-service")
public void handleBatch(List<OrderEvent> events) {
    List<Notification> notifications = events.stream()
        .filter(e -> e.status() == OrderStatus.SHIPPED)
        .map(e -> new Notification(e.customerId(),
            "Your order " + e.orderId() + " shipped!"))
        .toList();

    notificationRepo.saveAll(notifications); // Bulk insert
    emailService.sendBatch(notifications);   // Batch API
}
```

```yaml
# src/main/resources/application.yml
spring:
  kafka:
    listener:
      type: batch
    consumer:
      max-poll-records: 500
      fetch-min-size: 50000    # Wait for 50KB of data
      fetch-max-wait: 1000     # Or 1 second, whichever first
```

---

## Fix 3: Concurrent Consumers Within One Instance

```java
// src/main/java/com/eventstream/config/KafkaConfig.java
@Bean
public ConcurrentKafkaListenerContainerFactory<String, OrderEvent>
        kafkaListenerContainerFactory(
            ConsumerFactory<String, OrderEvent> cf) {
    var factory =
        new ConcurrentKafkaListenerContainerFactory
            <String, OrderEvent>();
    factory.setConsumerFactory(cf);
    factory.setConcurrency(4); // 4 threads per instance
    factory.setBatchListener(true);
    return factory;
}
```

`concurrency=4` on 3 instances = 12 consumer threads. Match this to your partition count. More threads than partitions = idle threads.

---

## Step 4: Test That Proves the Fix

```java
// src/test/java/com/eventstream/consumer/LagTest.java
@EmbeddedKafka(partitions = 4, topics = "order-events")
@SpringBootTest
class LagTest {

    @Autowired
    private KafkaTemplate<String, OrderEvent> kafka;
    @Autowired
    private NotificationRepository notificationRepo;

    @Test
    void batchConsumer_processesInBulk() throws Exception {
        for (int i = 0; i < 100; i++) {
            kafka.send("order-events", "ORD-" + i,
                new OrderEvent("ORD-" + i, "CUST-1",
                    BigDecimal.TEN, OrderStatus.SHIPPED,
                    Instant.now()));
        }

        Thread.sleep(5000);

        assertThat(notificationRepo.count())
            .isEqualTo(100); // ✅ All processed
    }
}
```

---

## The Lag Monitoring Rule

```
────────────────┬──────────┬──────────────────────────────────────────
 Lag            │ Status   │ Action
────────────────┼──────────┼──────────────────────────────────────────
 < 1,000        │ ✅ Healthy│ None
────────────────┼──────────┼──────────────────────────────────────────
 1,000–100,000  │ ⚠️ Warning│ Monitor, check consumer throughput
────────────────┼──────────┼──────────────────────────────────────────
 100,000+       │ 🔴 Critical│ Scale consumers, batch mode, check
                │          │ slow downstream dependencies
────────────────┴──────────┴──────────────────────────────────────────
```

The lag drops from 2M to zero in 20 minutes. Derek stops asking questions. Sana approves the PR.

Then on Wednesday, the entire pipeline freezes. One bad message. Infinite retry loop.

*That's [Chapter 6](kafka-06-the-poison-pill.md).*

---

[← The Outbox Pattern](kafka-04-the-outbox-pattern.md) | [Next: The Poison Pill →](kafka-06-the-poison-pill.md)

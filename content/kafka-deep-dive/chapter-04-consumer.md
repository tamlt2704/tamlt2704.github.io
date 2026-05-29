---
title: "Chapter 4: Consumer (Java/Spring)"
date: 2026-05-29
series: "kafka-deep-dive"
chapter: 4
---

# Chapter 4: Consumer (Java/Spring)

[← Chapter 3: Producer](../chapter-03-producer) | [Chapter 5: Patterns →](../chapter-05-patterns)

---

## Configuration

```yaml
# application.yml
spring:
  kafka:
    bootstrap-servers: localhost:9092
    consumer:
      group-id: order-service
      auto-offset-reset: earliest
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.springframework.kafka.support.serializer.JsonDeserializer
      properties:
        spring.json.trusted.packages: com.example.*
        max.poll.records: 500
        max.poll.interval.ms: 300000
```

## Basic Consumer with @KafkaListener

```java
@Component
public class OrderConsumer {

    @KafkaListener(topics = "orders", groupId = "order-service")
    public void consume(OrderEvent event) {
        System.out.printf("Received order: %s, amount: %.2f%n",
            event.orderId(), event.amount());
    }
}
```

### Consuming with metadata

```java
@KafkaListener(topics = "orders")
public void consume(
        @Payload OrderEvent event,
        @Header(KafkaHeaders.RECEIVED_PARTITION) int partition,
        @Header(KafkaHeaders.OFFSET) long offset,
        @Header(KafkaHeaders.RECEIVED_TIMESTAMP) long timestamp) {
    System.out.printf("partition=%d offset=%d event=%s%n",
        partition, offset, event);
}
```

### Consuming raw ConsumerRecord

```java
@KafkaListener(topics = "orders")
public void consume(ConsumerRecord<String, OrderEvent> record) {
    System.out.printf("key=%s partition=%d offset=%d value=%s%n",
        record.key(), record.partition(), record.offset(), record.value());
}
```

### Batch consumption

```java
@KafkaListener(topics = "orders", batch = "true")
public void consumeBatch(List<OrderEvent> events) {
    System.out.printf("Received batch of %d events%n", events.size());
    events.forEach(this::processEvent);
}
```

## Deserialization

### JSON Deserializer

```yaml
spring:
  kafka:
    consumer:
      value-deserializer: org.springframework.kafka.support.serializer.JsonDeserializer
      properties:
        spring.json.trusted.packages: com.example.*
        spring.json.value.default.type: com.example.OrderEvent
```

### Custom Deserializer

```java
public class OrderEventDeserializer implements Deserializer<OrderEvent> {

    private final ObjectMapper mapper = new ObjectMapper();

    @Override
    public OrderEvent deserialize(String topic, byte[] data) {
        try {
            return mapper.readValue(data, OrderEvent.class);
        } catch (IOException e) {
            throw new SerializationException("Error deserializing", e);
        }
    }
}
```

### Error-tolerant deserialization

```java
@Bean
public ConcurrentKafkaListenerContainerFactory<String, OrderEvent> kafkaListenerContainerFactory(
        ConsumerFactory<String, OrderEvent> consumerFactory) {
    var factory = new ConcurrentKafkaListenerContainerFactory<String, OrderEvent>();
    factory.setConsumerFactory(consumerFactory);
    factory.setCommonErrorHandler(new DefaultErrorHandler(
        new DeadLetterPublishingRecoverer(kafkaTemplate),
        new FixedBackOff(1000L, 3)
    ));
    return factory;
}
```

## Offset Management

```
┌─────────────────────────────────────────────────┐
│  Offset Commit Strategies                       │
│                                                 │
│  Auto commit:                                   │
│    Consumer polls → processes → auto-commits    │
│    (every auto.commit.interval.ms)              │
│                                                 │
│  Manual commit:                                 │
│    Consumer polls → processes → explicit commit │
│    (SYNC or ASYNC)                              │
└─────────────────────────────────────────────────┘
```

### Auto commit (default)

```yaml
spring:
  kafka:
    consumer:
      enable-auto-commit: true
      auto-commit-interval: 5000
```

Risk: messages processed but crash before auto-commit → reprocessing on restart.

### Manual commit (recommended for reliability)

```yaml
spring:
  kafka:
    consumer:
      enable-auto-commit: false
    listener:
      ack-mode: MANUAL_IMMEDIATE
```

```java
@KafkaListener(topics = "orders")
public void consume(OrderEvent event, Acknowledgment ack) {
    try {
        processOrder(event);
        ack.acknowledge();  // commit offset only after successful processing
    } catch (Exception e) {
        // offset not committed → message will be redelivered
        throw e;
    }
}
```

### Ack modes

| Mode               | Behavior                                         |
| ------------------ | ------------------------------------------------ |
| `RECORD`           | Commit after each record                         |
| `BATCH`            | Commit after all records in poll batch           |
| `MANUAL`           | Commit when `ack.acknowledge()` called (batched) |
| `MANUAL_IMMEDIATE` | Commit immediately on `ack.acknowledge()`        |

## Rebalancing

```
Before rebalance (3 partitions, 2 consumers):
  Consumer A: P0, P1
  Consumer B: P2

Consumer C joins group → rebalance triggered:
  Consumer A: P0
  Consumer B: P1
  Consumer C: P2
```

### Rebalance Listener

```java
@Component
public class OrderConsumerRebalanceListener implements ConsumerAwareRebalanceListener {

    @Override
    public void onPartitionsRevoked(Consumer<?, ?> consumer,
                                     Collection<TopicPartition> partitions) {
        // Commit offsets or flush state before losing partitions
        consumer.commitSync();
        System.out.println("Revoked: " + partitions);
    }

    @Override
    public void onPartitionsAssigned(Consumer<?, ?> consumer,
                                      Collection<TopicPartition> partitions) {
        System.out.println("Assigned: " + partitions);
    }
}
```

Register with listener:

```java
@Bean
public ConcurrentKafkaListenerContainerFactory<String, OrderEvent> kafkaListenerContainerFactory(
        ConsumerFactory<String, OrderEvent> consumerFactory,
        OrderConsumerRebalanceListener rebalanceListener) {
    var factory = new ConcurrentKafkaListenerContainerFactory<String, OrderEvent>();
    factory.setConsumerFactory(consumerFactory);
    factory.getContainerProperties().setConsumerRebalanceListener(rebalanceListener);
    return factory;
}
```

### Cooperative Sticky Assignor (reduces stop-the-world rebalances)

```yaml
spring:
  kafka:
    consumer:
      properties:
        partition.assignment.strategy: org.apache.kafka.clients.consumer.CooperativeStickyAssignor
```

## Concurrency

```java
@KafkaListener(topics = "orders", concurrency = "3")
public void consume(OrderEvent event) {
    // 3 consumer threads, each assigned partitions
    processOrder(event);
}
```

Or via factory:

```java
factory.setConcurrency(3);  // 3 threads = 3 consumers in the group
```

## Exercises

1. Create a consumer that reads `OrderEvent` from the `orders` topic and logs each event with partition and offset.

2. Implement manual offset commit. Simulate a failure mid-batch and verify that uncommitted messages are redelivered.

3. Start 3 consumer instances in the same group for a 6-partition topic. Observe partition assignment. Kill one instance and observe rebalancing.

4. Implement a `ConsumerAwareRebalanceListener` that logs partition assignments and revocations.

---

[← Chapter 3: Producer](../chapter-03-producer) | [Chapter 5: Patterns →](../chapter-05-patterns)

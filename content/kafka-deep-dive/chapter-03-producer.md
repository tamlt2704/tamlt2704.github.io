---
title: "Chapter 3: Producer (Java/Spring)"
date: 2026-05-29
series: "kafka-deep-dive"
chapter: 3
---

# Chapter 3: Producer (Java/Spring)

[← Chapter 2: Setup](../chapter-02-setup) | [Chapter 4: Consumer →](../chapter-04-consumer)

---

## Dependencies (Gradle)

```groovy
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter'
    implementation 'org.springframework.kafka:spring-kafka'
    implementation 'com.fasterxml.jackson.core:jackson-databind'
}
```

## Configuration

```yaml
# application.yml
spring:
  kafka:
    bootstrap-servers: localhost:9092
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
      acks: all
      retries: 3
      properties:
        enable.idempotence: true
        max.in.flight.requests.per.connection: 5
        linger.ms: 5
        batch.size: 16384
```

## Basic Producer with KafkaTemplate

```java
@Service
public class OrderProducer {

    private final KafkaTemplate<String, OrderEvent> kafkaTemplate;

    public OrderProducer(KafkaTemplate<String, OrderEvent> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    public CompletableFuture<SendResult<String, OrderEvent>> send(OrderEvent event) {
        return kafkaTemplate.send("orders", event.orderId(), event);
    }

    public void sendWithCallback(OrderEvent event) {
        kafkaTemplate.send("orders", event.orderId(), event)
            .whenComplete((result, ex) -> {
                if (ex == null) {
                    var metadata = result.getRecordMetadata();
                    System.out.printf("Sent to partition=%d offset=%d%n",
                        metadata.partition(), metadata.offset());
                } else {
                    System.err.println("Failed to send: " + ex.getMessage());
                }
            });
    }
}
```

```java
public record OrderEvent(String orderId, String customerId, double amount) {}
```

## Serializers

### JSON Serializer (default for objects)

Spring Kafka provides `JsonSerializer` out of the box. Configure type info in headers:

```yaml
spring:
  kafka:
    producer:
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
      properties:
        spring.json.add.type.headers: true
```

### Custom Serializer

```java
public class OrderEventSerializer implements Serializer<OrderEvent> {

    private final ObjectMapper mapper = new ObjectMapper();

    @Override
    public byte[] serialize(String topic, OrderEvent data) {
        try {
            return mapper.writeValueAsBytes(data);
        } catch (JsonProcessingException e) {
            throw new SerializationException("Error serializing", e);
        }
    }
}
```

### Avro Serializer (with Schema Registry)

```groovy
dependencies {
    implementation 'io.confluent:kafka-avro-serializer:7.6.0'
}
```

```yaml
spring:
  kafka:
    producer:
      value-serializer: io.confluent.kafka.serializers.KafkaAvroSerializer
      properties:
        schema.registry.url: http://localhost:8081
```

## Partitioning Strategies

```
Producer decides partition:
┌──────────────────────────────────────────┐
│  Key present?                            │
│    YES → hash(key) % numPartitions       │
│    NO  → round-robin (sticky partition)  │
└──────────────────────────────────────────┘
```

### Default (key-based hash)

Messages with the same key always go to the same partition:

```java
// key = orderId → consistent partition assignment
kafkaTemplate.send("orders", event.orderId(), event);
```

### Custom Partitioner

```java
public class RegionPartitioner implements Partitioner {

    @Override
    public int partition(String topic, Object key, byte[] keyBytes,
                         Object value, byte[] valueBytes, Cluster cluster) {
        var partitions = cluster.partitionsForTopic(topic);
        // Route by region prefix in key
        if (key != null && key.toString().startsWith("EU-")) {
            return 0;
        }
        return Math.abs(key.hashCode()) % partitions.size();
    }

    @Override public void close() {}
    @Override public void configure(Map<String, ?> configs) {}
}
```

Register in config:

```yaml
spring:
  kafka:
    producer:
      properties:
        partitioner.class: com.example.RegionPartitioner
```

## Acknowledgments (acks)

```
acks=0:   Fire and forget. No confirmation.
           Producer ──→ Broker (no response)

acks=1:   Leader confirms write.
           Producer ──→ Broker Leader ──→ ACK

acks=all:  All ISR replicas confirm.
           Producer ──→ Leader ──→ Followers ──→ ACK
```

| Setting    | Durability | Throughput | Latency |
| ---------- | ---------- | ---------- | ------- |
| `acks=0`   | Lowest     | Highest    | Lowest  |
| `acks=1`   | Medium     | Medium     | Medium  |
| `acks=all` | Highest    | Lowest     | Highest |

## Retries and Error Handling

```yaml
spring:
  kafka:
    producer:
      retries: 2147483647 # max int (rely on delivery.timeout.ms)
      properties:
        delivery.timeout.ms: 120000
        retry.backoff.ms: 100
```

### ProducerListener for global error handling

```java
@Bean
public ProducerListener<String, Object> producerListener() {
    return new ProducerListener<>() {
        @Override
        public void onError(ProducerRecord<String, Object> record,
                           RecordMetadata metadata, Exception exception) {
            System.err.printf("Failed to send to %s: %s%n",
                record.topic(), exception.getMessage());
        }
    };
}
```

## Idempotent Producer

Prevents duplicate messages on retries. Kafka assigns a Producer ID (PID) and sequence number to each message.

```
Without idempotence:
  Producer sends msg → Broker writes → ACK lost → Producer retries → DUPLICATE

With idempotence:
  Producer sends msg (PID=1, seq=0) → Broker writes → ACK lost
  → Producer retries (PID=1, seq=0) → Broker detects duplicate → returns ACK
```

Enable:

```yaml
spring:
  kafka:
    producer:
      properties:
        enable.idempotence: true
        max.in.flight.requests.per.connection: 5 # max allowed with idempotence
```

Requirements for idempotent producer:

- `acks=all`
- `retries > 0`
- `max.in.flight.requests.per.connection <= 5`

## Transactional Producer

For exactly-once semantics across multiple sends:

```yaml
spring:
  kafka:
    producer:
      transaction-id-prefix: tx-
```

```java
@Service
public class TransactionalOrderProducer {

    private final KafkaTemplate<String, OrderEvent> kafkaTemplate;

    public TransactionalOrderProducer(KafkaTemplate<String, OrderEvent> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    public void sendBatch(List<OrderEvent> events) {
        kafkaTemplate.executeInTransaction(ops -> {
            for (var event : events) {
                ops.send("orders", event.orderId(), event);
            }
            return null;
        });
    }
}
```

## Exercises

1. Create a producer that sends `OrderEvent` records with JSON serialization. Verify messages arrive with `kafka-console-consumer`.

2. Implement a custom partitioner that routes orders above a certain amount to a "priority" partition.

3. Test idempotent producer: configure `acks=all` and simulate network issues. Verify no duplicates using consumer offset tracking.

4. Implement a transactional producer that sends to two topics atomically.

---

[← Chapter 2: Setup](../chapter-02-setup) | [Chapter 4: Consumer →](../chapter-04-consumer)

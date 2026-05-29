---
title: "Chapter 7: Production"
date: 2026-05-29
series: "kafka-deep-dive"
chapter: 7
---

# Chapter 7: Production

[← Chapter 6: Kafka Streams](../chapter-06-streams) | [Overview →](../chapter-00-overview)

---

## Monitoring

### Key Metrics

```
┌─────────────────────────────────────────────────────┐
│  Critical Metrics to Monitor                        │
│                                                     │
│  Consumer Lag:                                      │
│    lag = log-end-offset - consumer-committed-offset │
│    Alert if lag grows continuously                  │
│                                                     │
│  Throughput:                                        │
│    messages/sec (in and out)                        │
│    bytes/sec (in and out)                           │
│                                                     │
│  Broker Health:                                     │
│    Under-replicated partitions (should be 0)        │
│    Active controller count (exactly 1)              │
│    ISR shrink rate                                  │
└─────────────────────────────────────────────────────┘
```

### Spring Boot Actuator + Micrometer

```groovy
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-actuator'
    implementation 'io.micrometer:micrometer-registry-prometheus'
}
```

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,metrics,prometheus
  metrics:
    tags:
      application: order-service
```

Key Kafka metrics exposed:

| Metric                                                | Description                |
| ----------------------------------------------------- | -------------------------- |
| `kafka_consumer_records_lag`                          | Consumer lag per partition |
| `kafka_consumer_fetch_manager_records_consumed_total` | Total records consumed     |
| `kafka_producer_record_send_total`                    | Total records sent         |
| `kafka_producer_record_error_total`                   | Send errors                |

### Monitoring Consumer Lag with CLI

```bash
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --describe --group order-service
```

### Grafana Dashboard Queries (PromQL)

```
# Consumer lag
sum(kafka_consumer_records_lag{group="order-service"}) by (topic, partition)

# Consumption rate
rate(kafka_consumer_fetch_manager_records_consumed_total[5m])

# Producer error rate
rate(kafka_producer_record_error_total[5m])
```

## Scaling Partitions

```
Scaling consumers:
  Partitions = max parallelism
  Consumers in group <= partitions

  3 partitions, 3 consumers → 1 partition each (optimal)
  3 partitions, 5 consumers → 2 consumers idle (waste)
  6 partitions, 3 consumers → 2 partitions each
```

### Guidelines for partition count

- Start with `partitions = expected peak throughput / throughput per consumer`
- Rule of thumb: `partitions >= number of consumer instances`
- You can increase partitions but NEVER decrease them
- More partitions = more memory, more file handles, longer leader elections

```bash
# Increase partitions (cannot decrease)
kafka-topics.sh --bootstrap-server localhost:9092 \
  --alter --topic orders --partitions 12
```

Warning: increasing partitions breaks key-based ordering for existing keys.

## Exactly-Once Semantics (EOS)

```
Delivery guarantees:
  At-most-once:  may lose messages (acks=0)
  At-least-once: may duplicate messages (default)
  Exactly-once:  no loss, no duplicates (EOS)

EOS requires:
  1. Idempotent producer (enable.idempotence=true)
  2. Transactional producer (transactional.id)
  3. Consumer with isolation.level=read_committed
```

### Configuration for EOS

```yaml
spring:
  kafka:
    producer:
      transaction-id-prefix: order-tx-
      properties:
        enable.idempotence: true
    consumer:
      properties:
        isolation.level: read_committed
```

### Consume-Transform-Produce pattern (EOS)

```java
@Bean
public ConcurrentKafkaListenerContainerFactory<String, String> eosFactory(
        ConsumerFactory<String, String> consumerFactory,
        KafkaTemplate<String, String> kafkaTemplate) {
    var factory = new ConcurrentKafkaListenerContainerFactory<String, String>();
    factory.setConsumerFactory(consumerFactory);
    factory.getContainerProperties().setTransactionManager(
        new KafkaTransactionManager<>(kafkaTemplate.getProducerFactory()));
    factory.getContainerProperties().setEosMode(
        ContainerProperties.EOSMode.V2);
    return factory;
}
```

## Schema Registry

Manage and enforce schemas for Kafka messages (Avro, JSON Schema, Protobuf).

```
┌──────────┐     schema     ┌─────────────────┐
│ Producer │ ──register───→ │ Schema Registry │
│          │ ←──schema-id── │                 │
└──────────┘                └─────────────────┘
      │                            ▲
      │ data + schema-id           │ fetch schema
      ▼                            │
┌──────────┐                ┌──────────┐
│  Kafka   │ ──────────────→│ Consumer │
└──────────┘                └──────────┘
```

### Docker setup

```yaml
schema-registry:
  image: confluentinc/cp-schema-registry:7.6.0
  ports:
    - "8081:8081"
  environment:
    SCHEMA_REGISTRY_HOST_NAME: schema-registry
    SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS: kafka:9092
  depends_on:
    - kafka
```

### Gradle dependencies

```groovy
repositories {
    mavenCentral()
    maven { url 'https://packages.confluent.io/maven/' }
}

dependencies {
    implementation 'io.confluent:kafka-avro-serializer:7.6.0'
    implementation 'org.apache.avro:avro:1.11.3'
}
```

### Avro schema

```json
{
  "type": "record",
  "name": "OrderEvent",
  "namespace": "com.example.avro",
  "fields": [
    { "name": "orderId", "type": "string" },
    { "name": "customerId", "type": "string" },
    { "name": "amount", "type": "double" },
    {
      "name": "status",
      "type": { "type": "enum", "name": "Status", "symbols": ["CREATED", "PAID", "SHIPPED"] }
    }
  ]
}
```

### Spring configuration with Schema Registry

```yaml
spring:
  kafka:
    producer:
      value-serializer: io.confluent.kafka.serializers.KafkaAvroSerializer
      properties:
        schema.registry.url: http://localhost:8081
        auto.register.schemas: true
    consumer:
      value-deserializer: io.confluent.kafka.serializers.KafkaAvroDeserializer
      properties:
        schema.registry.url: http://localhost:8081
        specific.avro.reader: true
```

### Schema compatibility modes

| Mode     | Rule                         |
| -------- | ---------------------------- |
| BACKWARD | New schema can read old data |
| FORWARD  | Old schema can read new data |
| FULL     | Both backward and forward    |
| NONE     | No compatibility check       |

## Security

### SASL/PLAIN Authentication

```yaml
# Broker config (server.properties)
listeners=SASL_PLAINTEXT://0.0.0.0:9092
security.inter.broker.protocol=SASL_PLAINTEXT
sasl.mechanism.inter.broker.protocol=PLAIN
sasl.enabled.mechanisms=PLAIN
```

### Spring Boot client with SASL

```yaml
spring:
  kafka:
    bootstrap-servers: kafka:9092
    properties:
      security.protocol: SASL_SSL
      sasl.mechanism: PLAIN
      sasl.jaas.config: >
        org.apache.kafka.common.security.plain.PlainLoginModule required
        username="app-user"
        password="app-secret";
    ssl:
      trust-store-location: classpath:truststore.jks
      trust-store-password: changeit
```

### SSL/TLS Encryption

```yaml
spring:
  kafka:
    ssl:
      trust-store-location: classpath:kafka.truststore.jks
      trust-store-password: changeit
      key-store-location: classpath:kafka.keystore.jks
      key-store-password: changeit
    properties:
      security.protocol: SSL
```

### ACLs (Access Control Lists)

```bash
# Grant producer access
kafka-acls.sh --bootstrap-server localhost:9092 \
  --add --allow-principal User:order-service \
  --operation Write --topic orders

# Grant consumer access
kafka-acls.sh --bootstrap-server localhost:9092 \
  --add --allow-principal User:order-service \
  --operation Read --topic orders --group order-service
```

## Production Checklist

```
Broker Configuration:
  [ ] Replication factor >= 3
  [ ] min.insync.replicas = 2
  [ ] unclean.leader.election.enable = false
  [ ] log.retention.hours appropriate for use case
  [ ] num.partitions sized for throughput

Producer Configuration:
  [ ] acks = all
  [ ] enable.idempotence = true
  [ ] retries = MAX_INT (rely on delivery.timeout.ms)
  [ ] delivery.timeout.ms set appropriately

Consumer Configuration:
  [ ] enable.auto.commit = false (manual commit)
  [ ] isolation.level = read_committed (if using transactions)
  [ ] max.poll.records tuned for processing time
  [ ] session.timeout.ms and heartbeat.interval.ms tuned

Monitoring:
  [ ] Consumer lag alerting
  [ ] Under-replicated partitions alerting
  [ ] Disk usage monitoring
  [ ] Network throughput monitoring

Security:
  [ ] SASL authentication enabled
  [ ] SSL/TLS encryption enabled
  [ ] ACLs configured (least privilege)
  [ ] Credentials in secrets manager (not config files)
```

## Exercises

1. Set up Prometheus + Grafana monitoring for a Spring Boot Kafka application. Create a dashboard showing consumer lag, throughput, and error rate.

2. Configure exactly-once semantics for a consume-transform-produce pipeline. Verify no duplicates under failure conditions.

3. Set up Schema Registry with Avro. Evolve a schema (add a field) and verify backward compatibility.

4. Configure SASL/SSL authentication. Create ACLs that restrict a producer to write only to specific topics.

---

[← Chapter 6: Kafka Streams](../chapter-06-streams) | [Overview →](../chapter-00-overview)

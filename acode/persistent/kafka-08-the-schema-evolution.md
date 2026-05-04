# Chapter 8: The Schema Evolution — "We Need to Add a Field Without Breaking Everything"

[← The Rebalance Storm](kafka-07-the-rebalance-storm.md) | [Next: The Exactly-Once Transaction →](kafka-09-the-exactly-once-transaction.md)

---

Six months in. Derek walks into standup:

> "We're expanding to Europe. Every order needs a `currency` field. Make it happen."

You open `OrderEvent.java`. Easy — just add a field. Then Sana stops you:

> "15 services consume `order-events`. You can't deploy them all simultaneously. If you change the schema, old consumers will break on new messages. New consumers will break on old messages."

---

## The Problem: V1 → V2

```java
// src/main/java/com/eventstream/event/OrderEvent.java
// V1 — what's in production right now
public record OrderEvent(
    String orderId, String customerId,
    BigDecimal amount, OrderStatus status,
    Instant occurredAt
) {}
```

```java
// V2 — what you want to deploy
// ⚠️ BUG: breaks all 15 existing consumers
public record OrderEvent(
    String orderId, String customerId,
    BigDecimal amount, String currency,
    OrderStatus status, Instant occurredAt
) {}
```

If you deploy the producer first, old consumers explode on the unknown field. If you deploy consumers first, they expect a field that doesn't exist yet. There's no safe order.

Raj has seen this before:

> "This is why JSON serialization without a schema registry is a ticking time bomb. You need **Avro** and a **Schema Registry**."

---

## Step 1: Add Schema Registry + Avro

```xml
<!-- pom.xml -->
<dependency>
    <groupId>io.confluent</groupId>
    <artifactId>kafka-avro-serializer</artifactId>
    <version>7.6.0</version>
</dependency>
```

### The Avro Schema — Backward Compatible

```json
// src/main/avro/OrderEvent.avsc
{
  "type": "record",
  "name": "OrderEvent",
  "namespace": "com.eventstream.events",
  "fields": [
    {"name": "orderId",    "type": "string"},
    {"name": "customerId", "type": "string"},
    {"name": "amount",     "type": "string"},
    {"name": "currency",   "type": "string",
     "default": "USD"},
    {"name": "status",     "type": "string"},
    {"name": "occurredAt", "type": "long"}
  ]
}
```

The key: `"default": "USD"`. Old messages without `currency` get the default. Old consumers ignore the unknown field. **Backward compatible.**

---

## Step 2: Config for Schema Registry

```yaml
# src/main/resources/application.yml
spring:
  kafka:
    properties:
      schema.registry.url: http://localhost:8081
    producer:
      value-serializer: >-
        io.confluent.kafka.serializers.KafkaAvroSerializer
    consumer:
      value-deserializer: >-
        io.confluent.kafka.serializers.KafkaAvroDeserializer
      properties:
        specific.avro.reader: true
```

---

## Step 3: Test That Proves Backward Compatibility

```java
// src/test/java/com/eventstream/schema/SchemaEvolutionTest.java
@SpringBootTest
class SchemaEvolutionTest {

    @Test
    void v1Message_deserializesWithDefault() {
        // Simulate a V1 message (no currency field)
        GenericRecord v1 = new GenericData.Record(v1Schema);
        v1.put("orderId", "ORD-EU-001");
        v1.put("customerId", "CUST-1");
        v1.put("amount", "99.99");
        v1.put("status", "CREATED");
        v1.put("occurredAt", Instant.now().toEpochMilli());

        // Deserialize with V2 schema
        GenericRecord result = deserializeWithV2(v1);

        // ✅ currency defaults to "USD"
        assertThat(result.get("currency").toString())
            .isEqualTo("USD");
    }
}
```

Test goes green. Old messages get the default. No consumers break.

---

## The Compatibility Rules

```
──────────────┬──────────────────────────────────┬──────────────────────────
 Mode         │ Rule                             │ Use Case
──────────────┼──────────────────────────────────┼──────────────────────────
 BACKWARD     │ New schema can read old data     │ Add fields with defaults
 (default)    │                                  │
──────────────┼──────────────────────────────────┼──────────────────────────
 FORWARD      │ Old schema can read new data     │ Remove optional fields
──────────────┼──────────────────────────────────┼──────────────────────────
 FULL         │ Both directions                  │ Safest, most restrictive
──────────────┼──────────────────────────────────┼──────────────────────────
 NONE         │ No checks                        │ Chaos. Don't.
──────────────┴──────────────────────────────────┴──────────────────────────
```

Raj's rule:

> "Use `BACKWARD` compatibility. Always add fields with defaults. Never remove or rename fields. Old consumers ignore unknown fields; new consumers use defaults for missing fields. That's the contract."

You deploy the producer with V2. The 15 consumer teams upgrade at their own pace over the next two weeks. Nothing breaks.

Then the Kafka Streams enrichment app crashes mid-transaction. Duplicates appear in the output topic.

*That's [Chapter 9](kafka-09-the-exactly-once-transaction.md).*

---

[← The Rebalance Storm](kafka-07-the-rebalance-storm.md) | [Next: The Exactly-Once Transaction →](kafka-09-the-exactly-once-transaction.md)

---
title: "Chapter 6: Kafka Streams"
date: 2026-05-29
series: "kafka-deep-dive"
chapter: 6
---

# Chapter 6: Kafka Streams

[← Chapter 5: Patterns](../chapter-05-patterns) | [Chapter 7: Production →](../chapter-07-production)

---

## Overview

Kafka Streams is a client library for building real-time streaming applications. No separate cluster needed — it runs inside your application.

```
┌─────────────────────────────────────────────┐
│           Kafka Streams Application          │
│                                             │
│  Input Topic → [Processor Topology] → Output Topic
│                                             │
│  ┌─────┐    ┌──────────┐    ┌─────────┐   │
│  │Source│───→│Processors│───→│  Sink   │   │
│  └─────┘    └──────────┘    └─────────┘   │
│                  │                          │
│                  ▼                          │
│           ┌────────────┐                   │
│           │ State Store │                   │
│           └────────────┘                   │
└─────────────────────────────────────────────┘
```

## Dependencies (Gradle)

```groovy
dependencies {
    implementation 'org.apache.kafka:kafka-streams'
    implementation 'org.springframework.kafka:spring-kafka'
}
```

## KStream vs KTable

```
KStream (event stream):
  Each record is an independent event.
  key=A, value=1
  key=A, value=2   ← both records exist
  key=A, value=3

KTable (changelog stream):
  Each record is an update to a key.
  key=A, value=1
  key=A, value=2   ← replaces previous
  key=A, value=3   ← current state: A=3
```

|           | KStream              | KTable               |
| --------- | -------------------- | -------------------- |
| Semantics | Append-only log      | Latest value per key |
| Analogy   | INSERT               | UPSERT               |
| Use case  | Events, transactions | State, aggregations  |

## Basic Stream Processing

```java
@Configuration
@EnableKafkaStreams
public class StreamsConfig {

    @Bean(name = KafkaStreamsDefaultConfiguration.DEFAULT_STREAMS_CONFIG_BEAN_NAME)
    public KafkaStreamsConfiguration kStreamsConfig() {
        Map<String, Object> props = new HashMap<>();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "order-streams");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.StringSerde.class);
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.StringSerde.class);
        return new KafkaStreamsConfiguration(props);
    }
}
```

### Filter and map

```java
@Bean
public KStream<String, String> orderStream(StreamsBuilder builder) {
    KStream<String, String> orders = builder.stream("orders");

    // Filter high-value orders
    KStream<String, String> highValue = orders
        .filter((key, value) -> parseAmount(value) > 1000);

    // Transform
    KStream<String, String> enriched = highValue
        .mapValues(value -> enrich(value));

    enriched.to("high-value-orders");
    return orders;
}
```

### Branch (split stream)

```java
@Bean
public KStream<String, OrderEvent> orderStream(StreamsBuilder builder) {
    KStream<String, OrderEvent> orders = builder.stream("orders",
        Consumed.with(Serdes.String(), orderEventSerde()));

    var branches = orders.split(Named.as("order-"))
        .branch((key, order) -> order.amount() > 1000, Branched.as("high-value"))
        .branch((key, order) -> order.amount() > 100, Branched.as("medium-value"))
        .defaultBranch(Branched.as("low-value"));

    branches.get("order-high-value").to("high-value-orders");
    branches.get("order-medium-value").to("medium-value-orders");
    branches.get("order-low-value").to("low-value-orders");

    return orders;
}
```

## Stateful Processing: Aggregations

### Count by key

```java
@Bean
public KTable<String, Long> orderCountByCustomer(StreamsBuilder builder) {
    return builder.stream("orders",
            Consumed.with(Serdes.String(), orderEventSerde()))
        .groupBy((key, order) -> order.customerId(),
            Grouped.with(Serdes.String(), orderEventSerde()))
        .count(Materialized.as("order-count-store"));
}
```

### Aggregate

```java
@Bean
public KTable<String, Double> totalByCustomer(StreamsBuilder builder) {
    return builder.stream("orders",
            Consumed.with(Serdes.String(), orderEventSerde()))
        .groupBy((key, order) -> order.customerId(),
            Grouped.with(Serdes.String(), orderEventSerde()))
        .aggregate(
            () -> 0.0,  // initializer
            (key, order, total) -> total + order.amount(),  // aggregator
            Materialized.<String, Double, KeyValueStore<Bytes, byte[]>>as("total-store")
                .withValueSerde(Serdes.Double())
        );
}
```

## Joins

```
KStream-KStream Join (windowed):
  orders ──┐
            ├──→ joined stream
  payments ─┘
  (within time window)

KStream-KTable Join (lookup enrichment):
  orders ──────┐
               ├──→ enriched orders
  customers ───┘
  (KTable = latest customer info)
```

### KStream-KTable join

```java
@Bean
public KStream<String, EnrichedOrder> enrichedOrders(StreamsBuilder builder) {
    KStream<String, OrderEvent> orders = builder.stream("orders",
        Consumed.with(Serdes.String(), orderEventSerde()));

    KTable<String, Customer> customers = builder.table("customers",
        Consumed.with(Serdes.String(), customerSerde()));

    // Join order with customer info (key must match)
    return orders
        .selectKey((key, order) -> order.customerId())  // re-key by customerId
        .join(customers,
            (order, customer) -> new EnrichedOrder(order, customer.name(), customer.email()))
        .to("enriched-orders", Produced.with(Serdes.String(), enrichedOrderSerde()));
}
```

### KStream-KStream join (windowed)

```java
@Bean
public KStream<String, OrderWithPayment> orderPaymentJoin(StreamsBuilder builder) {
    KStream<String, OrderEvent> orders = builder.stream("orders");
    KStream<String, PaymentEvent> payments = builder.stream("payments");

    var window = JoinWindows.ofTimeDifferenceWithNoGrace(Duration.ofMinutes(5));

    return orders.join(payments,
        (order, payment) -> new OrderWithPayment(order, payment),
        window,
        StreamJoined.with(Serdes.String(), orderSerde(), paymentSerde())
    );
}
```

## Windowing

```
Tumbling Window (fixed, non-overlapping):
|----5min----|----5min----|----5min----|
|  window 1  |  window 2  |  window 3  |

Hopping Window (fixed, overlapping):
|----5min----|
     |----5min----|
          |----5min----|
  (advance = 1min)

Session Window (activity-based):
|--session 1--|   gap   |--session 2--|
```

### Tumbling window aggregation

```java
@Bean
public KTable<Windowed<String>, Long> ordersPerMinute(StreamsBuilder builder) {
    return builder.stream("orders",
            Consumed.with(Serdes.String(), orderEventSerde()))
        .groupBy((key, order) -> order.customerId(),
            Grouped.with(Serdes.String(), orderEventSerde()))
        .windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofMinutes(1)))
        .count(Materialized.as("orders-per-minute"));
}
```

### Session window

```java
@Bean
public KTable<Windowed<String>, Long> userSessions(StreamsBuilder builder) {
    return builder.stream("page-views",
            Consumed.with(Serdes.String(), Serdes.String()))
        .groupByKey()
        .windowedBy(SessionWindows.ofInactivityGapWithNoGrace(Duration.ofMinutes(30)))
        .count(Materialized.as("user-sessions"));
}
```

## Interactive Queries (Read State Stores)

```java
@RestController
public class OrderCountController {

    private final StreamsBuilderFactoryBean factoryBean;

    @GetMapping("/orders/count/{customerId}")
    public Long getOrderCount(@PathVariable String customerId) {
        var store = factoryBean.getKafkaStreams()
            .store(StoreQueryParameters.fromNameAndType(
                "order-count-store", QueryableStoreTypes.keyValueStore()));
        Long count = store.get(customerId);
        return count != null ? count : 0L;
    }
}
```

## Topology Diagram

```
Example topology for order processing:

  [orders] ──→ filter(amount > 0)
                    │
                    ├──→ groupBy(customerId)
                    │         │
                    │         ▼
                    │    aggregate(sum)
                    │         │
                    │         ▼
                    │    [customer-totals] (KTable)
                    │
                    ├──→ selectKey(customerId)
                    │         │
                    │         ▼
                    │    join(customers KTable)
                    │         │
                    │         ▼
                    │    [enriched-orders]
                    │
                    └──→ branch
                          ├── high-value → [alerts]
                          └── normal → [processed-orders]
```

## Exercises

1. Build a stream that reads from `orders`, filters orders above a threshold, and writes to `high-value-orders`.

2. Implement a windowed count: count orders per customer per 5-minute tumbling window. Expose via REST endpoint.

3. Join an `orders` KStream with a `customers` KTable to produce enriched orders with customer name and email.

4. Build a session window that groups user page views into sessions (30-minute inactivity gap) and counts pages per session.

---

[← Chapter 5: Patterns](../chapter-05-patterns) | [Chapter 7: Production →](../chapter-07-production)

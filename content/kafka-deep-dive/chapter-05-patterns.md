---
title: "Chapter 5: Patterns"
date: 2026-05-29
series: "kafka-deep-dive"
chapter: 5
---

# Chapter 5: Patterns

[← Chapter 4: Consumer](../chapter-04-consumer) | [Chapter 6: Kafka Streams →](../chapter-06-streams)

---

## Event Sourcing

Store state changes as a sequence of events rather than current state.

```
Traditional:  UPDATE orders SET status='shipped' WHERE id=1
Event Sourced: append OrderShipped{orderId=1, timestamp=...}

Event Store (Kafka topic "order-events"):
┌──────────────┬───────────────┬──────────────┬───────────────┐
│ OrderCreated │ OrderPaid     │ OrderShipped │ OrderDelivered│
│ {id:1}       │ {id:1}        │ {id:1}       │ {id:1}        │
└──────────────┴───────────────┴──────────────┴───────────────┘
                                                        ▲
                                              current state = replay all
```

```java
// Event types
public sealed interface OrderEvent permits OrderCreated, OrderPaid, OrderShipped {
    String orderId();
}
public record OrderCreated(String orderId, String customerId, double amount) implements OrderEvent {}
public record OrderPaid(String orderId, String paymentId) implements OrderEvent {}
public record OrderShipped(String orderId, String trackingNumber) implements OrderEvent {}

// Producer - append events
@Service
public class OrderEventStore {

    private final KafkaTemplate<String, OrderEvent> kafkaTemplate;

    public OrderEventStore(KafkaTemplate<String, OrderEvent> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    public void append(OrderEvent event) {
        kafkaTemplate.send("order-events", event.orderId(), event);
    }
}

// Consumer - rebuild state
@Component
public class OrderProjection {

    private final Map<String, Order> orders = new ConcurrentHashMap<>();

    @KafkaListener(topics = "order-events", groupId = "order-projection")
    public void on(OrderEvent event) {
        orders.compute(event.orderId(), (id, order) -> apply(order, event));
    }

    private Order apply(Order current, OrderEvent event) {
        if (current == null) current = new Order();
        return switch (event) {
            case OrderCreated e -> current.withStatus("CREATED").withAmount(e.amount());
            case OrderPaid e -> current.withStatus("PAID");
            case OrderShipped e -> current.withStatus("SHIPPED");
        };
    }
}
```

## CQRS (Command Query Responsibility Segregation)

```
┌──────────┐     Commands      ┌──────────────┐
│  Client  │ ────────────────→ │ Command Side │
└──────────┘                   │ (Write Model)│
     │                         └──────┬───────┘
     │                                │ events
     │                                ▼
     │                         ┌──────────────┐
     │         Queries         │    Kafka     │
     │ ←────────────────────── │              │
     │                         └──────┬───────┘
     │                                │ consume
     │                                ▼
     │                         ┌──────────────┐
     └────────────────────────→│  Query Side  │
               reads           │ (Read Model) │
                               └──────────────┘
```

```java
// Command side - writes events to Kafka
@RestController
public class OrderCommandController {

    private final OrderEventStore eventStore;

    @PostMapping("/orders")
    public ResponseEntity<String> createOrder(@RequestBody CreateOrderRequest req) {
        var event = new OrderCreated(UUID.randomUUID().toString(), req.customerId(), req.amount());
        eventStore.append(event);
        return ResponseEntity.accepted().body(event.orderId());
    }
}

// Query side - maintains read-optimized view
@Component
public class OrderQueryService {

    private final OrderRepository repository;

    @KafkaListener(topics = "order-events", groupId = "order-query")
    public void project(OrderEvent event) {
        switch (event) {
            case OrderCreated e -> repository.save(new OrderView(e.orderId(), e.amount(), "CREATED"));
            case OrderPaid e -> repository.updateStatus(e.orderId(), "PAID");
            case OrderShipped e -> repository.updateStatus(e.orderId(), "SHIPPED");
        }
    }
}
```

## Saga Pattern

Coordinate distributed transactions across services using events.

```
Order Saga:
┌─────────┐    OrderCreated    ┌─────────────┐
│  Order  │ ─────────────────→ │   Payment   │
│ Service │                    │   Service   │
└─────────┘                    └──────┬──────┘
     ▲                                │
     │         PaymentCompleted       │
     │ ←──────────────────────────────┘
     │
     │         OrderConfirmed         ┌───────────┐
     └───────────────────────────────→│ Inventory │
                                      │  Service  │
                                      └───────────┘

Compensation (on failure):
  PaymentFailed → OrderCancelled → RefundIssued
```

```java
// Saga orchestrator
@Component
public class OrderSagaOrchestrator {

    private final KafkaTemplate<String, Object> kafkaTemplate;

    @KafkaListener(topics = "payment-results", groupId = "order-saga")
    public void onPaymentResult(PaymentResult result) {
        if (result.success()) {
            kafkaTemplate.send("inventory-commands",
                result.orderId(),
                new ReserveInventory(result.orderId()));
        } else {
            // Compensating action
            kafkaTemplate.send("order-commands",
                result.orderId(),
                new CancelOrder(result.orderId(), "Payment failed"));
        }
    }

    @KafkaListener(topics = "inventory-results", groupId = "order-saga")
    public void onInventoryResult(InventoryResult result) {
        if (result.success()) {
            kafkaTemplate.send("order-commands",
                result.orderId(),
                new ConfirmOrder(result.orderId()));
        } else {
            // Compensating actions
            kafkaTemplate.send("payment-commands",
                result.orderId(),
                new RefundPayment(result.orderId()));
            kafkaTemplate.send("order-commands",
                result.orderId(),
                new CancelOrder(result.orderId(), "Out of stock"));
        }
    }
}
```

## Outbox Pattern

Guarantee atomicity between database write and Kafka publish.

```
Problem:
  1. Save to DB  ✓
  2. Send to Kafka  ✗ (crash here = inconsistency)

Solution - Outbox:
  1. Save entity + outbox event in SAME DB transaction
  2. Separate process reads outbox table and publishes to Kafka
  3. Mark outbox entry as published

┌─────────────────────────────────────────┐
│  Database (single transaction)          │
│  ┌────────────┐  ┌──────────────────┐  │
│  │   orders   │  │  outbox_events   │  │
│  │  (entity)  │  │  (to publish)    │  │
│  └────────────┘  └──────────────────┘  │
└─────────────────────────────────────────┘
                          │
                          ▼  (poll or CDC)
                   ┌─────────────┐
                   │    Kafka    │
                   └─────────────┘
```

```java
// Outbox entity
@Entity
@Table(name = "outbox_events")
public class OutboxEvent {
    @Id
    private String id;
    private String aggregateType;
    private String aggregateId;
    private String eventType;
    private String payload;
    private Instant createdAt;
    private boolean published;
}

// Service - write entity + outbox in same transaction
@Service
@Transactional
public class OrderService {

    private final OrderRepository orderRepo;
    private final OutboxRepository outboxRepo;
    private final ObjectMapper mapper;

    public Order createOrder(CreateOrderRequest req) {
        var order = new Order(UUID.randomUUID().toString(), req.customerId(), req.amount());
        orderRepo.save(order);

        var outboxEvent = new OutboxEvent();
        outboxEvent.setId(UUID.randomUUID().toString());
        outboxEvent.setAggregateType("Order");
        outboxEvent.setAggregateId(order.getId());
        outboxEvent.setEventType("OrderCreated");
        outboxEvent.setPayload(mapper.writeValueAsString(order));
        outboxEvent.setCreatedAt(Instant.now());
        outboxRepo.save(outboxEvent);

        return order;
    }
}

// Outbox publisher - polls and sends to Kafka
@Component
public class OutboxPublisher {

    private final OutboxRepository outboxRepo;
    private final KafkaTemplate<String, String> kafkaTemplate;

    @Scheduled(fixedDelay = 1000)
    @Transactional
    public void publishPending() {
        var events = outboxRepo.findByPublishedFalseOrderByCreatedAt();
        for (var event : events) {
            kafkaTemplate.send(
                event.getAggregateType().toLowerCase() + "-events",
                event.getAggregateId(),
                event.getPayload()
            );
            event.setPublished(true);
            outboxRepo.save(event);
        }
    }
}
```

## Dead Letter Topics (DLT)

Route failed messages to a separate topic for investigation.

```
Main topic: "orders"
  │
  ├── Success → process normally
  │
  └── Failure (after retries) → "orders.DLT"
                                    │
                                    └── Manual inspection / reprocessing
```

```java
@Bean
public ConcurrentKafkaListenerContainerFactory<String, OrderEvent> kafkaListenerContainerFactory(
        ConsumerFactory<String, OrderEvent> consumerFactory,
        KafkaTemplate<String, Object> kafkaTemplate) {
    var factory = new ConcurrentKafkaListenerContainerFactory<String, OrderEvent>();
    factory.setConsumerFactory(consumerFactory);

    var recoverer = new DeadLetterPublishingRecoverer(kafkaTemplate,
        (record, ex) -> new TopicPartition(record.topic() + ".DLT", record.partition()));

    var errorHandler = new DefaultErrorHandler(recoverer, new FixedBackOff(1000L, 3));
    factory.setCommonErrorHandler(errorHandler);
    return factory;
}
```

## Retry Topics

More granular retry with increasing delays using separate topics.

```
orders → orders-retry-1 (1s) → orders-retry-2 (10s) → orders-retry-3 (60s) → orders-DLT
```

```java
@RetryableTopic(
    attempts = "4",
    backoff = @Backoff(delay = 1000, multiplier = 10, maxDelay = 60000),
    dltStrategy = DltStrategy.FAIL_ON_ERROR,
    topicSuffixingStrategy = TopicSuffixingStrategy.SUFFIX_WITH_INDEX_VALUE
)
@KafkaListener(topics = "orders", groupId = "order-service")
public void consume(OrderEvent event) {
    processOrder(event);  // throws exception → retried on retry topics
}

@DltHandler
public void handleDlt(OrderEvent event, @Header(KafkaHeaders.RECEIVED_TOPIC) String topic) {
    System.err.printf("DLT received from %s: %s%n", topic, event);
    // Alert, store for manual review, etc.
}
```

## Exercises

1. Implement event sourcing for a simple bank account (events: AccountCreated, MoneyDeposited, MoneyWithdrawn). Build a projection that maintains current balance.

2. Implement the outbox pattern: save an order to a database and publish an event atomically.

3. Configure retry topics with 3 retry levels (1s, 5s, 30s) and a DLT. Simulate failures and observe message flow through retry topics.

4. Implement a saga for: CreateOrder → ReserveInventory → ProcessPayment with compensation on failure.

---

[← Chapter 4: Consumer](../chapter-04-consumer) | [Chapter 6: Kafka Streams →](../chapter-06-streams)

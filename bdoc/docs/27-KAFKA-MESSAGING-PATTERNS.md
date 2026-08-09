# Chapter 27: Kafka Messaging Patterns — Build an Event-Driven Order System

## What you'll learn

- Kafka fundamentals: topics, partitions, consumer groups, offsets
- Producer patterns: fire-and-forget, sync, async, idempotent
- Consumer patterns: at-most-once, at-least-once, exactly-once
- Event-driven architecture: event sourcing, CQRS, saga pattern
- Spring Boot + Kafka integration
- Build: a complete order system with events flowing between microservices

---

## PART 1: Kafka Fundamentals

## 27.1 What is Kafka?

Kafka is a distributed event streaming platform. Think of it as a durable, ordered, replayable message log.

```
┌────────────┐                              ┌────────────┐
│ Producer A │──┐                        ┌──│ Consumer X │
└────────────┘  │    ┌──────────────┐   │  └────────────┘
                ├───►│  KAFKA TOPIC │───┤
┌────────────┐  │    │  (partitioned│   │  ┌────────────┐
│ Producer B │──┘    │   durable    │   └──│ Consumer Y │
└────────────┘       │   log)       │      └────────────┘
                     └──────────────┘
```

**vs traditional message queues (RabbitMQ, SQS):**
| Feature | Traditional Queue | Kafka |
|---------|-------------------|-------|
| Message consumed | Deleted after consumption | Retained (configurable TTL) |
| Replay | Can't re-read old messages | Can replay from any offset |
| Ordering | FIFO (single queue) | Per-partition ordering |
| Consumer groups | Competing consumers | Both: competing + broadcast |
| Throughput | Thousands/sec | Millions/sec |
| Use case | Task queues, RPC | Event streaming, logs, real-time pipelines |

## 27.2 Core concepts

**Topic** — a named category of messages (like a database table):
```
orders-topic, payments-topic, inventory-topic, notifications-topic
```

**Partition** — a topic is split into partitions for parallelism:
```
orders-topic:
  Partition 0: [msg1, msg4, msg7, msg10, ...]
  Partition 1: [msg2, msg5, msg8, msg11, ...]
  Partition 2: [msg3, msg6, msg9, msg12, ...]
```

Messages with the same KEY go to the same partition → guaranteed ordering per key.

**Consumer Group** — a set of consumers that share the work:
```
Consumer Group "order-service":
  Consumer A → reads Partition 0
  Consumer B → reads Partition 1
  Consumer C → reads Partition 2
  (each message is processed by exactly ONE consumer in the group)

Consumer Group "analytics-service":
  Consumer D → reads Partition 0, 1, 2
  (gets ALL messages — independent from group above)
```

**Offset** — position of a consumer in a partition:
```
Partition 0: [msg0, msg1, msg2, msg3, msg4, msg5, ...]
                                       ↑
                              Consumer A offset = 4 (next to read)
```

## 27.3 Kafka guarantees

| Guarantee | How |
|-----------|-----|
| **Ordering** | Per partition (not across partitions). Use message key for related events. |
| **Durability** | Messages replicated across brokers. `acks=all` = message written to ALL replicas before ack. |
| **At-least-once** | Consumer commits offset AFTER processing. Crash = re-process (need idempotent consumers). |
| **Exactly-once** | Kafka transactions + idempotent producer + transactional consumer (complex but possible). |

---

## PART 2: Spring Boot + Kafka

## 27.4 Setup

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.kafka</groupId>
    <artifactId>spring-kafka</artifactId>
</dependency>
```

```yaml
# application.yml
spring:
  kafka:
    bootstrap-servers: localhost:9092
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
      acks: all
      properties:
        enable.idempotence: true
    consumer:
      group-id: order-service
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.springframework.kafka.support.serializer.JsonDeserializer
      auto-offset-reset: earliest
      properties:
        spring.json.trusted.packages: "*"
```

## 27.5 Define events

```java
// Base event
public abstract class OrderEvent {
    private String orderId;
    private String eventType;
    private Instant timestamp;
    private String correlationId; // trace across services

    // constructors, getters
}

// Specific events
public class OrderCreatedEvent extends OrderEvent {
    private String customerId;
    private List<OrderItem> items;
    private BigDecimal totalAmount;
}

public class OrderValidatedEvent extends OrderEvent {
    private boolean valid;
    private String reason;
}

public class PaymentProcessedEvent extends OrderEvent {
    private String paymentId;
    private PaymentStatus status;
}

public class InventoryReservedEvent extends OrderEvent {
    private Map<String, Integer> reservedItems; // itemId → quantity
}

public class OrderCompletedEvent extends OrderEvent {
    private Instant completedAt;
}

public class OrderFailedEvent extends OrderEvent {
    private String failureReason;
    private String failedStep;
}
```

## 27.6 Producer — publishing events

```java
@Service
public class OrderEventPublisher {
    private final KafkaTemplate<String, OrderEvent> kafkaTemplate;

    public OrderEventPublisher(KafkaTemplate<String, OrderEvent> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    // Async publish (fire-and-forget with callback)
    public void publish(String topic, OrderEvent event) {
        kafkaTemplate.send(topic, event.getOrderId(), event)
            .whenComplete((result, ex) -> {
                if (ex != null) {
                    log.error("Failed to publish event: {}", event.getOrderId(), ex);
                    // Retry logic or dead letter queue
                } else {
                    log.info("Published {} to partition {} offset {}",
                        event.getEventType(),
                        result.getRecordMetadata().partition(),
                        result.getRecordMetadata().offset());
                }
            });
    }

    // Sync publish (blocks until ack — for critical events)
    public void publishSync(String topic, OrderEvent event) {
        try {
            kafkaTemplate.send(topic, event.getOrderId(), event).get(5, TimeUnit.SECONDS);
        } catch (Exception e) {
            throw new EventPublishException("Failed to publish: " + event.getOrderId(), e);
        }
    }
}
```

**Key: `event.getOrderId()` as the message key** → all events for the same order go to the same partition → processed in order.

## 27.7 Consumer — processing events

```java
@Service
public class PaymentConsumer {

    private final PaymentService paymentService;
    private final OrderEventPublisher publisher;

    @KafkaListener(topics = "order-validated", groupId = "payment-service")
    public void handleOrderValidated(OrderValidatedEvent event) {
        log.info("Received validated order: {}", event.getOrderId());

        if (!event.isValid()) {
            publisher.publish("order-events", new OrderFailedEvent(
                event.getOrderId(), event.getReason(), "VALIDATION"
            ));
            return;
        }

        try {
            PaymentResult result = paymentService.processPayment(event.getOrderId(), event.getTotalAmount());

            publisher.publish("payment-processed", new PaymentProcessedEvent(
                event.getOrderId(), result.getPaymentId(), PaymentStatus.SUCCESS
            ));
        } catch (PaymentException e) {
            publisher.publish("payment-processed", new PaymentProcessedEvent(
                event.getOrderId(), null, PaymentStatus.FAILED
            ));
        }
    }
}
```

## 27.8 Consumer error handling

```java
@Configuration
public class KafkaConsumerConfig {

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, OrderEvent> kafkaListenerContainerFactory(
            ConsumerFactory<String, OrderEvent> consumerFactory
    ) {
        var factory = new ConcurrentKafkaListenerContainerFactory<String, OrderEvent>();
        factory.setConsumerFactory(consumerFactory);

        // Retry 3 times with backoff, then send to dead letter topic
        factory.setCommonErrorHandler(new DefaultErrorHandler(
            new DeadLetterPublishingRecoverer(kafkaTemplate),
            new FixedBackOff(1000L, 3L) // 1 second between retries, max 3 retries
        ));

        return factory;
    }
}
```

---

## PART 3: Messaging Patterns

## 27.9 Pattern 1: Event-Driven Choreography

Each service reacts to events and publishes its own events. No central orchestrator.

```
OrderService               PaymentService            InventoryService         NotificationService
    │                           │                         │                        │
    │ publish                   │                         │                        │
    │ OrderCreatedEvent        │                         │                        │
    ├──────────────────────────►│                         │                        │
    │                           │ process payment         │                        │
    │                           │ publish                 │                        │
    │                           │ PaymentProcessedEvent   │                        │
    │                           ├────────────────────────►│                        │
    │                           │                         │ reserve stock          │
    │                           │                         │ publish                │
    │                           │                         │ InventoryReservedEvent │
    │                           │                         ├───────────────────────►│
    │                           │                         │                        │ send email
```

**Pros:** Loosely coupled, each service is independent, easy to add new consumers.
**Cons:** Hard to track overall flow, no single place that knows the full business process.

## 27.10 Pattern 2: Saga Pattern (orchestration)

A central orchestrator coordinates the multi-step transaction:

```java
@Service
public class OrderSagaOrchestrator {

    @KafkaListener(topics = "order-created")
    public void startSaga(OrderCreatedEvent event) {
        // Step 1: Validate
        publisher.publish("validate-order-cmd", new ValidateOrderCommand(event));
    }

    @KafkaListener(topics = "order-validated")
    public void onValidated(OrderValidatedEvent event) {
        if (event.isValid()) {
            // Step 2: Process payment
            publisher.publish("process-payment-cmd", new ProcessPaymentCommand(event));
        } else {
            // Compensate: cancel order
            publisher.publish("order-events", new OrderFailedEvent(event.getOrderId(), "Invalid"));
        }
    }

    @KafkaListener(topics = "payment-processed")
    public void onPaymentProcessed(PaymentProcessedEvent event) {
        if (event.getStatus() == PaymentStatus.SUCCESS) {
            // Step 3: Reserve inventory
            publisher.publish("reserve-inventory-cmd", new ReserveInventoryCommand(event));
        } else {
            // Compensate: refund not needed (payment failed)
            publisher.publish("order-events", new OrderFailedEvent(event.getOrderId(), "Payment failed"));
        }
    }

    @KafkaListener(topics = "inventory-reserved")
    public void onInventoryReserved(InventoryReservedEvent event) {
        if (event.isReserved()) {
            // All steps complete!
            publisher.publish("order-events", new OrderCompletedEvent(event.getOrderId()));
        } else {
            // Compensate: refund payment
            publisher.publish("refund-payment-cmd", new RefundCommand(event.getOrderId()));
            publisher.publish("order-events", new OrderFailedEvent(event.getOrderId(), "Out of stock"));
        }
    }
}
```

**Compensation (rollback):** If step 3 fails, undo step 2. Each service provides a compensating action.

## 27.11 Pattern 3: Event Sourcing

Instead of storing current state, store ALL events that happened. Rebuild state by replaying.

```java
// Traditional: store current state
// orders table: { id: "ORD-1", status: "SHIPPED", total: 150.00 }

// Event sourcing: store events
// order_events table:
// { orderId: "ORD-1", type: "CREATED",   data: { items: [...], total: 150 } }
// { orderId: "ORD-1", type: "PAID",      data: { paymentId: "PAY-1" } }
// { orderId: "ORD-1", type: "SHIPPED",   data: { trackingNo: "TRK-1" } }

// Rebuild current state:
Order rebuildOrder(String orderId) {
    List<OrderEvent> events = eventStore.getEvents(orderId);
    Order order = new Order();
    for (OrderEvent event : events) {
        order.apply(event); // each event mutates the state
    }
    return order;
}
```

**Benefits:** Complete audit trail, time-travel debugging, rebuild read models.
**Cost:** More storage, eventual consistency for read models, complexity.

## 27.12 Pattern 4: CQRS (Command Query Responsibility Segregation)

Separate the write model (commands/events) from the read model (queries):

```
WRITE SIDE:                              READ SIDE:
┌─────────────┐                          ┌─────────────────┐
│  Commands   │                          │  Query API      │
│  (create,   │                          │  (search, list, │
│   update)   │                          │   aggregate)    │
└──────┬──────┘                          └────────┬────────┘
       │                                          │
       ▼                                          ▼
┌─────────────┐     Events      ┌─────────────────────────┐
│ Event Store │ ───────────────► │  Read DB (denormalized) │
│ (Kafka/DB)  │                  │  (Elasticsearch, Redis) │
└─────────────┘                  └─────────────────────────┘
```

**Write side:** validates, stores events, enforces business rules.
**Read side:** projects events into query-optimized views (denormalized, pre-computed).

```java
// Write side: handles command, emits event
@Service
public class OrderCommandHandler {
    public void handle(CreateOrderCommand cmd) {
        // Validate business rules
        Order order = Order.create(cmd.getCustomerId(), cmd.getItems());
        // Store event
        eventStore.append(new OrderCreatedEvent(order));
        // Publish to Kafka for read-side projection
        publisher.publish("order-events", new OrderCreatedEvent(order));
    }
}

// Read side: listens to events, updates query-optimized store
@Service
public class OrderProjection {
    @KafkaListener(topics = "order-events")
    public void project(OrderEvent event) {
        switch (event.getEventType()) {
            case "ORDER_CREATED" -> orderSearchIndex.index(event);
            case "ORDER_SHIPPED" -> orderDashboard.updateStatus(event);
            case "ORDER_COMPLETED" -> analytics.recordCompletion(event);
        }
    }
}
```

## 27.13 Pattern 5: Dead Letter Queue (DLQ)

Messages that repeatedly fail go to a separate topic for investigation:

```
Main Topic: "orders"
  → Consumer processes message
  → Fails 3 times
  → Moved to: "orders.DLT" (Dead Letter Topic)

// Monitor DLT, alert on new messages, manual retry or fix
```

```java
// Spring Kafka auto-configures DLT:
@KafkaListener(topics = "orders")
@RetryableTopic(
    attempts = "3",
    backoff = @Backoff(delay = 1000, multiplier = 2),
    topicSuffixingStrategy = TopicSuffixingStrategy.SUFFIX_WITH_INDEX_VALUE
)
public void processOrder(OrderCreatedEvent event) {
    // If this throws 3 times → goes to "orders-retry-0", "orders-retry-1", then "orders-dlt"
}

@DltHandler
public void handleDlt(OrderCreatedEvent event) {
    log.error("Failed to process order after retries: {}", event.getOrderId());
    alertService.notifyOps("Order processing failed: " + event.getOrderId());
}
```

---

## PART 4: Production Considerations

## 27.14 Idempotent consumers

Since Kafka guarantees at-least-once delivery, your consumer might process the same message twice. Make operations idempotent:

```java
@Service
public class PaymentConsumer {
    private final Set<String> processedEvents = ConcurrentHashMap.newKeySet();
    // In production: use a database table for processed event IDs

    @KafkaListener(topics = "order-validated")
    public void handle(OrderValidatedEvent event) {
        // Idempotency check
        String eventId = event.getOrderId() + ":" + event.getTimestamp();
        if (!processedEvents.add(eventId)) {
            log.info("Duplicate event, skipping: {}", eventId);
            return;
        }

        // Process...
    }
}
```

## 27.15 Monitoring and observability

```java
// Consumer lag — how far behind is the consumer?
// If lag grows, consumer is slower than producer → scale up consumers

// Key metrics:
// - consumer_lag (messages behind)
// - messages_consumed_per_second
// - processing_time_per_message
// - error_rate
// - dead_letter_queue_size
```

## 27.16 Topic design guidelines

| Principle | Guideline |
|-----------|-----------|
| One event type per topic | `order-created`, `payment-processed` (not mixed) |
| Partition key = entity ID | `orderId` → all events for same order are ordered |
| Partitions = max consumers | 12 partitions → max 12 parallel consumers |
| Retention | 7 days for operational, 30+ days for event sourcing |
| Schema | Use Avro/Protobuf + Schema Registry for evolution |

---

## Summary

✅ Kafka fundamentals: topics, partitions, consumer groups, offsets
✅ Spring Boot integration: producer with callbacks, consumer with error handling
✅ Event-driven choreography: services react to events autonomously
✅ Saga pattern: orchestrated multi-step transactions with compensation
✅ Event sourcing: store events, rebuild state by replaying
✅ CQRS: separate optimized read/write models
✅ Dead Letter Queue: handle poison messages gracefully
✅ Idempotent consumers: handle at-least-once delivery safely
✅ Built: a complete order processing pipeline across microservices

## Key takeaway

**Kafka is a commit log, not a queue.** Messages are retained, can be replayed, and multiple consumer groups can each read independently. This makes Kafka the backbone for event-driven architectures — every service produces events about what happened, and any interested service can subscribe without the producer knowing.

**Design events as facts that happened** (past tense: OrderCreated, PaymentProcessed), not as commands (CreateOrder, ProcessPayment). Facts are immutable and can be consumed by any number of services. Commands are directed at specific services.

---

→ [Back to Chapter 26: Java Concurrency](./26-JAVA-CONCURRENCY.md)

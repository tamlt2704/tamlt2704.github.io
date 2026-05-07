# Chapter 4: The Outbox Pattern — "The Database Says Yes, Kafka Says No"

[← The Duplicate Payment](kafka-03-the-duplicate-payment.md) | [Next: The Consumer Lag Crisis →](kafka-05-the-consumer-lag-crisis.md)

---

Week four. The Kafka cluster goes down for 90 seconds during a broker rolling restart. When it comes back, Sana checks the data:

> "12 payments were charged in the DB. Only 9 payment events made it to Kafka. Inventory never reserved 3 items. Customers got charged for stuff we might not have."

You check the payment service code. It writes to the DB, then publishes to Kafka. Two separate systems. If Kafka is down after the DB commits — the event is gone.

Raj saw this coming:

> "You can't atomically write to a database AND Kafka. They're separate systems. This is the **dual-write problem**."

---

## The Buggy Code

```java
// src/main/java/com/eventstream/service/PaymentService.java
// ⚠️ BUG: dual-write — DB and Kafka are not atomic
@Transactional
public void processPayment(OrderEvent event) {
    paymentRepo.save(new Payment(
        event.orderId(), event.amount(),
        PaymentStatus.CHARGED));

    kafka.send("payment-events", event.orderId(),
        new PaymentEvent(event.orderId(), event.amount()));
    // ↑ NOT part of the DB transaction.
    // DB commits, Kafka fails → inconsistency
}
```

The `@Transactional` only covers the database. The `kafka.send()` is outside that boundary. Two systems, no shared transaction.

---

## Step 1: Write a Test That Proves the Bug

```java
// src/test/java/com/eventstream/service/DualWriteTest.java
@SpringBootTest
class DualWriteTest {

    @Autowired private PaymentService paymentService;
    @Autowired private PaymentRepository paymentRepo;
    @MockBean private KafkaTemplate<String, PaymentEvent> kafka;

    @Test
    void dbCommits_butKafkaFails_eventLost() {
        // Simulate Kafka being down
        when(kafka.send(any(), any(), any()))
            .thenThrow(new KafkaException("Broker unavailable"));

        var event = new OrderEvent("ORD-5001", "CUST-1",
            new BigDecimal("75.00"),
            OrderStatus.CREATED, Instant.now());

        assertThatThrownBy(() ->
            paymentService.processPayment(event));

        // ⚠️ BUG: payment exists in DB, no event in Kafka
        assertThat(paymentRepo.existsByOrderId("ORD-5001"))
            .isTrue(); // DB committed before Kafka failed
    }
}
```

---

## Step 2: The Fix — Transactional Outbox

Write the event to a database table **in the same transaction**. A separate process reads the table and publishes to Kafka.

### The Outbox Entity

```java
// src/main/java/com/eventstream/outbox/OutboxEvent.java
@Entity
@Table(name = "outbox_events")
public class OutboxEvent {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String aggregateId;
    private String topic;
    private String eventType;
    @Column(columnDefinition = "jsonb")
    private String payload;
    private Instant createdAt;
    private boolean published;
}
```

### The Fixed Service — Same Transaction

```java
// src/main/java/com/eventstream/service/PaymentService.java
@Service
@RequiredArgsConstructor
public class PaymentService {

    private final PaymentRepository paymentRepo;
    private final OutboxRepository outboxRepo;

    @Transactional // Both writes in ONE transaction — atomic
    public void processPayment(OrderEvent event) {
        paymentRepo.save(new Payment(
            event.orderId(), event.amount(),
            PaymentStatus.CHARGED));

        outboxRepo.save(new OutboxEvent(
            event.orderId(), "payment-events",
            "PaymentCompleted",
            toJson(new PaymentEvent(
                event.orderId(), event.amount())),
            Instant.now(), false));
    }
}
```

If the DB commits, the outbox row is there. If the DB rolls back, the outbox row is gone too. **Atomic.**

### The Relay — Publishes to Kafka

```java
// src/main/java/com/eventstream/outbox/OutboxRelay.java
@Service
@RequiredArgsConstructor
public class OutboxRelay {

    private final OutboxRepository outboxRepo;
    private final KafkaTemplate<String, String> kafka;

    @Scheduled(fixedDelay = 500)
    @Transactional
    public void publishPending() {
        var events = outboxRepo
            .findTop100ByPublishedFalseOrderByCreatedAt();
        for (OutboxEvent e : events) {
            kafka.send(e.getTopic(),
                e.getAggregateId(), e.getPayload());
            e.setPublished(true);
        }
    }
}
```

---

## Step 3: Test That Proves the Fix

```java
// src/test/java/com/eventstream/service/OutboxTest.java
@SpringBootTest
class OutboxTest {

    @Autowired private PaymentService paymentService;
    @Autowired private PaymentRepository paymentRepo;
    @Autowired private OutboxRepository outboxRepo;

    @Test
    void outbox_guaranteesAtomicity() {
        var event = new OrderEvent("ORD-5002", "CUST-1",
            new BigDecimal("75.00"),
            OrderStatus.CREATED, Instant.now());

        paymentService.processPayment(event);

        assertThat(paymentRepo.existsByOrderId("ORD-5002"))
            .isTrue();
        assertThat(outboxRepo.existsByAggregateId("ORD-5002"))
            .isTrue(); // ✅ Both in same transaction
    }
}
```

Test goes green. Payment and outbox event live or die together.

---

## Production Upgrade: Debezium

Raj reviews your PR:

> "The polling relay works, but it adds up to 500ms latency and hammers the DB. For production, use **Debezium** — it reads PostgreSQL's WAL (write-ahead log) and streams outbox rows to Kafka in near-real-time. No polling, no delay."

You nod and file a follow-up ticket. The outbox pattern is solid. Debezium is the optimization.

*The dual-write problem is solved. But Monday morning, you'll discover a new problem: the notification service is 2 million messages behind. [Chapter 5](kafka-05-the-consumer-lag-crisis.md).*

---

[← The Duplicate Payment](kafka-03-the-duplicate-payment.md) | [Next: The Consumer Lag Crisis →](kafka-05-the-consumer-lag-crisis.md)

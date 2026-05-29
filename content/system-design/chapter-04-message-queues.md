# Chapter 4: Message Queues & Async Processing

[← Chapter 3: Caching](/blog/system-design/chapter-03-caching) | [Chapter 5: API Design →](/blog/system-design/chapter-05-api-design)

---

## Why Message Queues?

Synchronous calls create tight coupling and cascading failures:

```
SYNCHRONOUS (fragile):
User → Order Service → Payment Service → Notification Service
                              ↓ (down!)
                        Everything fails

ASYNCHRONOUS (resilient):
User → Order Service → [Queue] → Payment Service
                       [Queue] → Notification Service
                              ↓ (down? messages wait)
                        Order still accepted
```

**Use a queue when:**

- The caller doesn't need an immediate response
- Work is expensive (video encoding, report generation)
- You need to absorb traffic spikes
- Services should be independently deployable/scalable
- You need guaranteed delivery (retry on failure)

---

## Core Concepts

```
┌──────────┐     ┌───────────────────┐     ┌──────────┐
│ Producer │────▶│      Queue        │────▶│ Consumer │
│          │     │  [msg1][msg2][msg3]│     │          │
└──────────┘     └───────────────────┘     └──────────┘
```

| Term                        | Meaning                                      |
| --------------------------- | -------------------------------------------- |
| **Producer**                | Sends messages to the queue                  |
| **Consumer**                | Reads and processes messages                 |
| **Broker**                  | The queue server (Kafka, RabbitMQ, SQS)      |
| **Topic/Queue**             | Named channel for messages                   |
| **Partition**               | Subdivision of a topic for parallelism       |
| **Offset**                  | Position of a consumer in the message stream |
| **Dead Letter Queue (DLQ)** | Where failed messages go after max retries   |

---

## Queue vs Topic (Point-to-Point vs Pub/Sub)

```
QUEUE (Point-to-Point):
Each message consumed by exactly ONE consumer.

Producer → [msg1][msg2][msg3] → Consumer A gets msg1
                               → Consumer B gets msg2
                               → Consumer A gets msg3

TOPIC (Pub/Sub):
Each message delivered to ALL subscribers.

Producer → [msg1] → Consumer A gets msg1
                  → Consumer B gets msg1
                  → Consumer C gets msg1
```

---

## Delivery Guarantees

| Guarantee         | Meaning                               | Tradeoff                                               |
| ----------------- | ------------------------------------- | ------------------------------------------------------ |
| **At-most-once**  | Message may be lost, never duplicated | Fast, no overhead. Use for metrics/logs.               |
| **At-least-once** | Message never lost, may be duplicated | Must handle duplicates (idempotency). Most common.     |
| **Exactly-once**  | Message delivered exactly once        | Expensive. Requires transactions. Kafka supports this. |

### Idempotency — Handling Duplicates

Since at-least-once is the default, your consumers MUST be idempotent:

```java
// BAD: Not idempotent — double-processing charges user twice
public void processPayment(PaymentEvent event) {
    paymentGateway.charge(event.getUserId(), event.getAmount());
}

// GOOD: Idempotent — uses idempotency key
public void processPayment(PaymentEvent event) {
    if (processedEvents.contains(event.getId())) {
        return;  // already processed
    }
    paymentGateway.charge(event.getUserId(), event.getAmount());
    processedEvents.add(event.getId());
}
```

**Idempotency strategies:**

- Unique message ID + deduplication table
- Database unique constraints (INSERT ... ON CONFLICT DO NOTHING)
- Conditional updates (UPDATE ... WHERE version = expected_version)

---

## Kafka vs RabbitMQ vs SQS

| Feature    | Kafka                                  | RabbitMQ                  | AWS SQS                        |
| ---------- | -------------------------------------- | ------------------------- | ------------------------------ |
| Model      | Distributed log                        | Message broker            | Managed queue                  |
| Ordering   | Per-partition                          | Per-queue                 | Best-effort (FIFO available)   |
| Retention  | Days/weeks (replay)                    | Until consumed            | 14 days max                    |
| Throughput | Millions/sec                           | Thousands/sec             | Thousands/sec                  |
| Replay     | Yes (re-read old messages)             | No (consumed = gone)      | No                             |
| Complexity | High (ZooKeeper/KRaft)                 | Medium                    | Low (managed)                  |
| Best for   | Event streaming, logs, high throughput | Task queues, RPC, routing | Simple async tasks, serverless |

**Decision:**

- Need event replay / event sourcing? → **Kafka**
- Need complex routing (headers, priority)? → **RabbitMQ**
- Want zero ops, simple queue? → **SQS**

---

## Kafka Deep Dive

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Kafka Cluster                      │
│                                                      │
│  Topic: "orders"                                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐    │
│  │Partition 0 │  │Partition 1 │  │Partition 2 │    │
│  │[0][1][2][3]│  │[0][1][2]   │  │[0][1][2][3]│   │
│  └────────────┘  └────────────┘  └────────────┘    │
│                                                      │
│  Broker 1          Broker 2          Broker 3        │
└─────────────────────────────────────────────────────┘
         ▲                                    │
         │                                    ▼
    ┌──────────┐                      ┌──────────────┐
    │ Producer │                      │Consumer Group│
    └──────────┘                      │ C1  C2  C3  │
                                      └──────────────┘
```

### Consumer Groups

Each partition is consumed by exactly one consumer in a group:

```
Partition 0 → Consumer A
Partition 1 → Consumer B
Partition 2 → Consumer C

If Consumer B dies:
Partition 0 → Consumer A
Partition 1 → Consumer C  (rebalanced)
Partition 2 → Consumer C
```

**Rule:** You can't have more consumers than partitions in a group. Extra consumers sit idle.

### Ordering Guarantees

Kafka guarantees order **within a partition**, not across partitions.

```java
// Ensure all events for same user go to same partition:
producer.send(new ProducerRecord<>("orders", userId, orderEvent));
//                                  topic     key    value
// Key determines partition: hash(userId) % numPartitions
```

---

## Common Patterns

### 1. Work Queue (Fan-Out)

Distribute work across multiple workers:

```
                    ┌──────────┐
              ┌────▶│ Worker 1 │
              │     └──────────┘
┌──────────┐  │     ┌──────────┐
│ Producer │──┼────▶│ Worker 2 │
└──────────┘  │     └──────────┘
              │     ┌──────────┐
              └────▶│ Worker 3 │
                    └──────────┘
```

Use case: Video encoding, image resizing, report generation.

### 2. Event Sourcing

Store state as a sequence of events, not current state:

```
Events (immutable log):
1. OrderCreated { id: 123, items: [...], total: $50 }
2. PaymentReceived { orderId: 123, amount: $50 }
3. OrderShipped { orderId: 123, tracking: "UPS123" }
4. OrderDelivered { orderId: 123 }

Current state = replay all events
```

### 3. Saga Pattern (Distributed Transactions)

Coordinate multi-service transactions without 2PC:

```
Order Saga:
1. Order Service: Create order (PENDING)
2. Payment Service: Charge card
   → Success: continue
   → Failure: Order Service: Cancel order (COMPENSATE)
3. Inventory Service: Reserve stock
   → Success: Order Service: Confirm order
   → Failure: Payment Service: Refund (COMPENSATE)
```

### 4. Dead Letter Queue (DLQ)

Messages that fail repeatedly go to a separate queue for investigation:

```
Main Queue → Consumer → Process
                │
                ├── Success → ACK, remove from queue
                │
                └── Failure → Retry (3 times)
                                 │
                                 └── Still failing → DLQ
                                                      │
                                                      ▼
                                              Manual investigation
                                              or automated alerting
```

---

## Backpressure

When producers are faster than consumers:

| Strategy              | How                            | Tradeoff                                 |
| --------------------- | ------------------------------ | ---------------------------------------- |
| **Buffering**         | Queue absorbs the spike        | Works for bursts, not sustained overload |
| **Dropping**          | Discard messages when full     | Data loss, but system stays alive        |
| **Rate limiting**     | Slow down producers (HTTP 429) | Producers must handle backoff            |
| **Scaling consumers** | Auto-scale consumer count      | Lag before new consumers start           |

```
Monitor consumer lag:
  lag = latest_offset - consumer_offset

  lag < 100    → healthy
  lag 100-1000 → warning, consider scaling
  lag > 1000   → critical, consumers can't keep up
```

---

## Design Checklist for Async Systems

1. **Idempotency** — Can the consumer safely process the same message twice?
2. **Ordering** — Does order matter? Use partition keys if yes.
3. **Retry policy** — How many retries? Exponential backoff?
4. **DLQ** — Where do failed messages go?
5. **Monitoring** — Consumer lag, processing time, error rate.
6. **Poison pill** — One bad message shouldn't block the entire queue.
7. **Graceful shutdown** — Finish in-flight messages before stopping.

---

[Chapter 5: API Design →](/blog/system-design/chapter-05-api-design)

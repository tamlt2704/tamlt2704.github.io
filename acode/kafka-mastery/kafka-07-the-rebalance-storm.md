# Chapter 7: The Rebalance Storm — "Consumers Keep Disconnecting"

[← The Poison Pill](kafka-06-the-poison-pill.md) | [Next: The Schema Evolution →](kafka-08-the-schema-evolution.md)

---

Thursday. Grafana shows a sawtooth pattern — throughput spikes, drops to zero, spikes, drops to zero. Every 30 seconds, like clockwork.

Sana pulls up the consumer group status:

```
$ kafka-consumer-groups.sh --describe --group payment-service
GROUP           TOPIC          PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
payment-service order-events   0          -               5200000         -
payment-service order-events   1          -               4900000         -
                                          ↑ no current offset = rebalancing
```

> "They're rebalancing. Every 30 seconds, all partitions get revoked and reassigned. During rebalance, **nothing is processed**."

Raj checks the consumer logs:

> "Your batch processing takes 45 seconds. `max.poll.interval.ms` is 300 seconds by default, but the real problem is the eager assignor. Every time a consumer joins or leaves, ALL partitions get revoked."

---

## Why Rebalances Happen

```
Consumer A joins group → REBALANCE (all stop, reassign)
Consumer B crashes     → REBALANCE
Consumer C is too slow → Kafka thinks it's dead → REBALANCE
Deploy new version     → REBALANCE × N instances
```

The #1 cause: **consumer processing takes longer than `max.poll.interval.ms`**. Kafka assumes the consumer is dead and kicks it out. Then it rejoins. Then it gets kicked again. Storm.

---

## The Buggy Config

```yaml
# src/main/resources/application.yml
# ⚠️ BUG: default settings cause rebalance storms
spring:
  kafka:
    consumer:
      max-poll-records: 500
      # max.poll.interval.ms: 300000 (default)
      # session.timeout.ms: 45000 (default)
      # partition.assignment.strategy: RangeAssignor (default)
```

500 records × slow downstream processing = exceeds poll interval = kicked from group = rebalance.

---

## Fix 1: Tune Poll Interval and Batch Size

```yaml
# src/main/resources/application.yml
spring:
  kafka:
    consumer:
      max-poll-records: 100
      properties:
        max.poll.interval.ms: 600000
        session.timeout.ms: 45000
        heartbeat.interval.ms: 15000
```

**Rule**: `heartbeat.interval.ms` < `session.timeout.ms / 3`. Heartbeats prove the consumer is alive. Session timeout is how long Kafka waits before declaring it dead.

Fewer records per poll = faster processing per batch = stays within the interval.

---

## Fix 2: Cooperative Sticky Assignor

The default assignor revokes **ALL** partitions during rebalance. Cooperative sticky only moves what's necessary:

```yaml
# src/main/resources/application.yml
spring:
  kafka:
    consumer:
      properties:
        partition.assignment.strategy: >-
          org.apache.kafka.clients.consumer.CooperativeStickyAssignor
```

**Before** (eager): All 12 partitions revoked → reassigned → full stop-the-world.

**After** (cooperative): Only 2 partitions move from old consumer to new → 10 partitions keep processing.

---

## Fix 3: Static Group Membership for Rolling Deploys

Every time you deploy, instances restart. Each restart = a rebalance. With 12 instances, that's 12 rebalances during a rolling deploy.

```yaml
# src/main/resources/application.yml
spring:
  kafka:
    consumer:
      properties:
        group.instance.id: ${HOSTNAME}
        session.timeout.ms: 300000
```

With static membership, a consumer that restarts within `session.timeout.ms` gets its **same partitions back** — no rebalance at all. The `HOSTNAME` ensures each pod gets a unique, stable identity.

---

## Step 4: Test That Proves the Fix

```java
// src/test/java/com/eventstream/consumer/RebalanceTest.java
@EmbeddedKafka(partitions = 4, topics = "order-events")
@SpringBootTest(properties = {
    "spring.kafka.consumer.properties.partition.assignment.strategy="
    + "org.apache.kafka.clients.consumer.CooperativeStickyAssignor",
    "spring.kafka.consumer.max-poll-records=50"
})
class RebalanceTest {

    @Autowired
    private KafkaTemplate<String, OrderEvent> kafka;

    @Test
    void cooperativeAssignor_minimizesRebalanceImpact()
            throws Exception {
        for (int i = 0; i < 200; i++) {
            kafka.send("order-events", "ORD-" + i,
                new OrderEvent("ORD-" + i, "CUST-1",
                    BigDecimal.TEN, OrderStatus.CREATED,
                    Instant.now()));
        }

        Thread.sleep(10000);
        // ✅ No rebalance storms with tuned config
    }
}
```

The sawtooth pattern disappears. Throughput is smooth. Sana approves the PR.

Then product asks you to add a `currency` field to `OrderEvent`. 15 services consume that topic.

*How hard can it be? Very. [Chapter 8](kafka-08-the-schema-evolution.md).*

---

[← The Poison Pill](kafka-06-the-poison-pill.md) | [Next: The Schema Evolution →](kafka-08-the-schema-evolution.md)

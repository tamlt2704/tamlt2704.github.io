# Chapter 10: The Production Checklist — What Separates Senior from Staff

[← The Exactly-Once Transaction](kafka-09-the-exactly-once-transaction.md) | [Back to Overview →](kafka-00-overview.md)

---

Launch week. Derek books a conference room for the final architecture review. He brings Sana, Raj, and you. Whiteboard markers everywhere.

> "Walk me through the system. I want to know it won't fall over on Black Friday."

---

## 10.1 — Topic Design Rules

Raj goes to the whiteboard first:

```bash
kafka-topics.sh --create --topic order-events \
  --partitions 12 \
  --replication-factor 3 \
  --config retention.ms=604800000 \
  --config min.insync.replicas=2 \
  --bootstrap-server localhost:9092
```

```
──────────────────────┬────────┬──────────────────────────────────────
 Setting              │ Value  │ Why
──────────────────────┼────────┼──────────────────────────────────────
 partitions           │ 12+    │ Parallelism ceiling. Plan for peak,
                      │        │ not current. Can't decrease later.
──────────────────────┼────────┼──────────────────────────────────────
 replication-factor   │ 3      │ Survive 2 broker failures
──────────────────────┼────────┼──────────────────────────────────────
 min.insync.replicas  │ 2      │ With acks=all, ensures 2 copies
                      │        │ before acknowledging
──────────────────────┼────────┼──────────────────────────────────────
 retention.ms         │ 7 days │ Balance between replay ability
                      │        │ and disk cost
──────────────────────┴────────┴──────────────────────────────────────
```

> "The ISR formula: `min.insync.replicas` must be **less than** `replication-factor`. If they're equal, one broker failure = topic goes read-only. With RF=3 and ISR=2, you can lose one broker and keep writing."

Derek nods.

---

## 10.2 — The Final Architecture

Sana draws the full picture:

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Order Service │  │ Payment Svc  │  │ Inventory Svc│
│  (Producer)   │  │  (Consumer)  │  │  (Consumer)  │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       │    ┌────────────┴─────────────┐   │
       │    │     Schema Registry      │   │
       │    └────────────┬─────────────┘   │
       │                 │                 │
┌──────▼─────────────────▼─────────────────▼──────┐
│                 Kafka Cluster                    │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐         │
│  │Broker 1 │  │Broker 2 │  │Broker 3 │         │
│  │(Leader) │←→│(Replica)│←→│(Replica)│         │
│  └─────────┘  └─────────┘  └─────────┘         │
│                                                  │
│  Topics:                                         │
│  ├── order-events     (12 partitions, RF=3)     │
│  ├── payment-events   (12 partitions, RF=3)     │
│  ├── enriched-orders  (12 partitions, RF=3)     │
│  └── order-events.DLT (dead letters)            │
└──────────────────────────────────────────────────┘
       │                 │                 │
       ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Notification │  │ Enrichment   │  │ Analytics    │
│   Service    │  │  (Streams)   │  │  Service     │
└──────────────┘  └──────────────┘  └──────────────┘
```

Derek points at each box. You explain what you built:

- **Producers**: `acks=all`, idempotent, error callbacks ([Chapter 2](kafka-02-the-lost-order-incident.md))
- **Consumers**: Idempotent with dedup checks ([Chapter 3](kafka-03-the-duplicate-payment.md))
- **Outbox**: Transactional outbox for DB+Kafka atomicity ([Chapter 4](kafka-04-the-outbox-pattern.md))
- **Scaling**: 12 partitions, batch consumption, concurrent listeners ([Chapter 5](kafka-05-the-consumer-lag-crisis.md))
- **Error handling**: Dead letter topics, error classification ([Chapter 6](kafka-06-the-poison-pill.md))
- **Rebalance**: Cooperative sticky assignor, static membership ([Chapter 7](kafka-07-the-rebalance-storm.md))
- **Schema**: Avro + Schema Registry, backward compatibility ([Chapter 8](kafka-08-the-schema-evolution.md))
- **Transactions**: Exactly-once for stream processing ([Chapter 9](kafka-09-the-exactly-once-transaction.md))

---

## 10.3 — The Cheat Sheet

Derek asks for a one-pager. You write it on the whiteboard:

```
──────────────────────────┬──────────────────────────┬──────────────────────────────
 Problem                  │ Wrong Approach           │ Right Approach
──────────────────────────┼──────────────────────────┼──────────────────────────────
 Message loss             │ acks=1, no error         │ acks=all + idempotence
                          │ handling                 │ + outbox pattern
──────────────────────────┼──────────────────────────┼──────────────────────────────
 Duplicate processing     │ Assume Kafka deduplicates│ Idempotent consumers
                          │                          │ with dedup check
──────────────────────────┼──────────────────────────┼──────────────────────────────
 Dual-write inconsistency │ Write DB + Kafka         │ Transactional outbox
                          │ separately               │ + Debezium
──────────────────────────┼──────────────────────────┼──────────────────────────────
 Consumer lag             │ Bigger instance           │ More partitions + batch
                          │                          │ + concurrency
──────────────────────────┼──────────────────────────┼──────────────────────────────
 Poison pill messages     │ Infinite retry           │ Dead letter topic
                          │                          │ + error classification
──────────────────────────┼──────────────────────────┼──────────────────────────────
 Rebalance storms         │ Default settings         │ Cooperative sticky
                          │                          │ + static membership
──────────────────────────┼──────────────────────────┼──────────────────────────────
 Schema changes           │ JSON YOLO                │ Schema Registry + Avro
                          │                          │ + backward compatibility
──────────────────────────┼──────────────────────────┼──────────────────────────────
 Ordering                 │ Random keys              │ Partition key =
                          │                          │ business entity ID
──────────────────────────┼──────────────────────────┼──────────────────────────────
 Exactly-once             │ Kafka transactions       │ At-least-once + idempotent
                          │ everywhere               │ consumers (default)
──────────────────────────┼──────────────────────────┼──────────────────────────────
 Partition count          │ Start with 3             │ Start with 12+, plan
                          │                          │ for peak throughput
──────────────────────────┴──────────────────────────┴──────────────────────────────
```

---

## Derek's Verdict

Derek looks at the whiteboard. Looks at you. Looks at Sana and Raj.

> "Ship it."

---

You started as a junior dev who thought Kafka was just a message queue. You lost messages, charged customers twice, broke 15 services with a schema change, and watched consumers rebalance into oblivion.

Every incident taught you something. Every bug made the system stronger.

The story of EventStream continues — Kafka Streams for stateful processing, Kafka Connect for CDC pipelines, multi-datacenter replication with MirrorMaker 2. But the foundation you built takes you from a naive `kafka.send()` to a production-grade event platform.

Raj walks by your desk one last time:

> "Not bad for a PayFlow intern."

---

[← The Exactly-Once Transaction](kafka-09-the-exactly-once-transaction.md) | [Back to Overview →](kafka-00-overview.md)

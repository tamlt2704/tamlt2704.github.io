---
title: "Chapter 1: Core Concepts"
date: 2026-05-29
series: "kafka-deep-dive"
chapter: 1
---

# Chapter 1: Core Concepts

[← Overview](../chapter-00-overview) | [Chapter 2: Setup →](../chapter-02-setup)

---

## What is Apache Kafka?

Apache Kafka is a distributed event streaming platform capable of handling trillions of events per day. It provides publish/subscribe messaging, durable storage of streams, and real-time stream processing.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Kafka Cluster                         │
│                                                         │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐          │
│  │  Broker 0 │  │  Broker 1 │  │  Broker 2 │          │
│  │  P0 (L)   │  │  P1 (L)   │  │  P2 (L)   │          │
│  │  P1 (R)   │  │  P2 (R)   │  │  P0 (R)   │          │
│  └───────────┘  └───────────┘  └───────────┘          │
└─────────────────────────────────────────────────────────┘
        ▲                                    │
        │                                    ▼
  ┌───────────┐                      ┌───────────────┐
  │ Producers │                      │   Consumers   │
  └───────────┘                      └───────────────┘
```

L = Leader replica, R = Follower replica

## Topics

A **topic** is a category or feed name to which records are published. Topics are multi-subscriber.

```
Topic: "orders"
┌─────────────────────────────────────────┐
│  Partition 0: [msg0][msg1][msg2][msg3]  │
│  Partition 1: [msg0][msg1][msg2]        │
│  Partition 2: [msg0][msg1][msg2][msg3]  │
└─────────────────────────────────────────┘
```

- Topics are split into **partitions** for parallelism
- Each message within a partition gets a sequential **offset**
- Messages are immutable once written
- Retention is configurable (time-based or size-based)

## Partitions

Partitions are the unit of parallelism in Kafka.

```
Partition 0:
┌─────┬─────┬─────┬─────┬─────┬─────┐
│  0  │  1  │  2  │  3  │  4  │  5  │  ← offsets
└─────┴─────┴─────┴─────┴─────┴─────┘
                              ▲
                         write position
```

- Each partition is an ordered, immutable sequence of records
- Ordering is guaranteed **only within a partition**
- A partition lives on a single broker (leader) with replicas on others
- Number of partitions determines max consumer parallelism

## Brokers

A **broker** is a single Kafka server. A cluster consists of multiple brokers.

Responsibilities:

- Receive and store messages from producers
- Serve messages to consumers
- Replicate data for fault tolerance
- One broker acts as the **controller** (leader election, partition assignment)

## Producers

A **producer** publishes data to topics.

```
Producer
   │
   ├── serialize key + value
   ├── determine partition (key hash, round-robin, or custom)
   ├── batch messages
   └── send to partition leader broker
```

Key decisions: acknowledgments (acks), retries, batching, partitioning strategy.

## Consumers and Consumer Groups

A **consumer** reads data from topics. Each consumer belongs to a **consumer group**.

```
Topic with 4 partitions, Consumer Group with 3 consumers:

  Partition 0 ──→ Consumer A
  Partition 1 ──→ Consumer A
  Partition 2 ──→ Consumer B
  Partition 3 ──→ Consumer C
```

Rules:

- Each partition is consumed by exactly **one** consumer in a group
- A consumer can read from multiple partitions
- If consumers > partitions, some consumers are idle
- Different consumer groups independently consume the same topic

## Offsets

An **offset** is a unique sequential ID for each message within a partition.

```
Partition 0:
Offset:  0    1    2    3    4    5    6    7
       ┌────┬────┬────┬────┬────┬────┬────┬────┐
       │ m0 │ m1 │ m2 │ m3 │ m4 │ m5 │ m6 │ m7 │
       └────┴────┴────┴────┴────┴────┴────┴────┘
                        ▲              ▲
                   committed       log-end
                    offset          offset

  lag = log-end offset - committed offset
```

- Stored in internal topic `__consumer_offsets`
- Can be committed automatically or manually
- Enables replay by resetting offsets

## Replication

```
Topic "orders", Partition 0, replication-factor=3:

  Broker 0: P0 (Leader)    ← producers write here
  Broker 1: P0 (Follower)  ← replicates from leader
  Broker 2: P0 (Follower)  ← replicates from leader

ISR (In-Sync Replicas) = {Broker 0, Broker 1, Broker 2}
```

- **Leader** handles all reads and writes
- **Followers** replicate the leader
- If leader fails, a follower from ISR becomes new leader

## Key Guarantees

| Guarantee              | Scope                                          |
| ---------------------- | ---------------------------------------------- |
| Ordering               | Within a single partition                      |
| Durability             | Configurable via replication factor and acks   |
| At-least-once delivery | Default behavior                               |
| No message loss        | When `acks=all` and `min.insync.replicas >= 2` |

## Exercises

1. Sketch a 3-broker cluster with a topic having 6 partitions and replication factor 2. Identify leaders and followers.

2. If a topic has 8 partitions and your consumer group has 3 consumers, how are partitions assigned? What happens if you add a 4th consumer?

3. A consumer has committed offset 50 but crashes. When it restarts, from which offset does it resume?

4. You have a topic with 4 partitions. Messages with key "user-123" always go to partition 2. What happens if you increase partitions to 6?

---

[← Overview](../chapter-00-overview) | [Chapter 2: Setup →](../chapter-02-setup)

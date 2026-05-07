# Kafka Mastery: An Event-Driven Survival Story

You're at **FleetPulse** — a logistics startup that tracks 12,000 delivery trucks in real time. GPS pings every 5 seconds. Order status updates. Driver check-ins. Route changes. ETA recalculations.

The current architecture: every truck sends an HTTP POST to a REST API. The API writes to PostgreSQL. A cron job runs every 60 seconds to check for new events and notify downstream systems — the dispatcher dashboard, the customer tracking page, the billing system, the analytics warehouse.

It worked at 500 trucks. At 12,000 trucks, the cron job takes 90 seconds to run. Events are delayed by 2 minutes. The dispatcher sees stale positions. Customers call asking "where's my package?" because the tracking page is behind. The database is drowning in writes — 2,400 GPS pings per second, plus all the status updates.

**Nadia**, the VP of Engineering, calls an all-hands:

> "We're signing a contract with a national carrier next month. 80,000 trucks. Our architecture can't handle 12,000. We need real-time event streaming. No more polling. No more cron jobs. No more 2-minute delays. We need Kafka."

She turns to you:

> "You've got 3 weeks to build the event backbone. Every system that needs truck data should get it in under 500 milliseconds. Go."

You open your terminal. You've heard of Kafka. "It's like a queue, right?" Nadia winces.

---

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Backend Engineer | "I know RabbitMQ. How different can Kafka be?" |
| **Nadia** | VP Engineering | "Real-time means real-time. Not 'eventually.'" |
| **Carlos** | Data Engineer | "I need every event in the warehouse. Don't lose a single one." |
| **Preet** | Frontend Lead | "The map needs to update in under a second." |
| **Ops Yuki** | SRE | "The last time we added infrastructure, it took 3 months to stabilize." |
| **The Cron Job** | Legacy system | Runs every 60 seconds. Falls behind. Misses events. |
| **Consumer Lag** | That one metric | Grows silently until someone notices the dashboard is 10 minutes behind. |

---

## The Stack

| Tool | What It Does |
|---|---|
| **Apache Kafka 3.7+** | Distributed event streaming platform |
| **Kafka Connect** | Move data between Kafka and external systems |
| **Schema Registry** | Enforce event schemas (Avro/JSON Schema) |
| **ksqlDB** | Stream processing with SQL (optional) |
| **Docker Compose** | Run the full Kafka cluster locally |
| **Python (confluent-kafka)** | Producer/consumer client |
| **Java (Spring Kafka)** | Alternative client examples |

---

## How to Read This

Every chapter follows the same loop:

```
  📋 An event delivery problem surfaces
   │
   ▼
  🤔 You identify why the current approach fails
   │
   ▼
  ⌨️  You learn the Kafka concept that solves it
   │
   ▼
  💥 The fix creates a new problem (lag, ordering, duplicates, rebalancing)
   │
   ▼
  🧠 You understand the tradeoff and fix it properly
   │
   ▼
  📋 Next problem
```

No concept shows up before you need it. You won't hear about consumer groups until one consumer can't keep up. You won't touch partitioning until ordering breaks. You won't learn about exactly-once until duplicates corrupt the billing system.

The events come first. The architecture follows.

---

## The Roadmap

### Part 1: Foundations — "Replace the Cron Job"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Problem                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 01 │ Cron job is 2 minutes behind           │ Kafka basics — topics, producers, consumers, brokers
────┼────────────────────────────────────────┼──────────────────────────────────────
 02 │ GPS events arrive out of order         │ Partitions, keys, ordering guarantees
────┼────────────────────────────────────────┼──────────────────────────────────────
 03 │ One consumer can't keep up with 2400/s │ Consumer groups, parallel consumption, rebalancing
────┼────────────────────────────────────────┼──────────────────────────────────────
 04 │ Consumer crashes, misses events        │ Offsets, commits, at-least-once delivery
────┼────────────────────────────────────────┼──────────────────────────────────────
 05 │ "What does this event mean?"           │ Schemas — Avro, JSON Schema, Schema Registry
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 2: Patterns — "Make It Reliable"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Problem                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 06 │ Billing gets duplicate charges         │ Exactly-once semantics, idempotent producers, transactions
────┼────────────────────────────────────────┼──────────────────────────────────────
 07 │ Dashboard needs enriched events        │ Stream processing — joins, filters, transformations
────┼────────────────────────────────────────┼──────────────────────────────────────
 08 │ Need events in the data warehouse      │ Kafka Connect — sinks, sources, connectors
────┼────────────────────────────────────────┼──────────────────────────────────────
 09 │ Dead letter queue for failed events    │ Error handling — DLQ, retries, poison pills
────┼────────────────────────────────────────┼──────────────────────────────────────
 10 │ Events need to trigger workflows       │ Event-driven architecture patterns — choreography vs orchestration
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 3: Scale — "Handle 80,000 Trucks"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Problem                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 11 │ 3 brokers can't handle the throughput  │ Cluster sizing, replication factor, ISR
────┼────────────────────────────────────────┼──────────────────────────────────────
 12 │ Adding partitions breaks consumers     │ Partition strategy, rebalancing protocols, cooperative
────┼────────────────────────────────────────┼──────────────────────────────────────
 13 │ Disk filling up, events from 6 months  │ Retention policies, compaction, tiered storage
    │ ago                                    │
────┼────────────────────────────────────────┼──────────────────────────────────────
 14 │ Consumer lag growing silently          │ Monitoring — JMX, consumer lag, broker metrics
────┼────────────────────────────────────────┼──────────────────────────────────────
 15 │ Broker dies during peak traffic        │ Fault tolerance — leader election, unclean leader, rack awareness
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 4: Production — "Ship It"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Problem                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 16 │ Schema change breaks consumers         │ Schema evolution — compatibility modes, migration
────┼────────────────────────────────────────┼──────────────────────────────────────
 17 │ Need to replay events from last week   │ Event sourcing, replay, temporal queries
────┼────────────────────────────────────────┼──────────────────────────────────────
 18 │ Securing the cluster                   │ Authentication (SASL), authorization (ACLs), encryption
────┼────────────────────────────────────────┼──────────────────────────────────────
 19 │ Testing event-driven systems           │ Testcontainers, embedded Kafka, contract testing
────┼────────────────────────────────────────┼──────────────────────────────────────
 20 │ 80,000 trucks go live                  │ Capacity planning, performance tuning, the launch checklist
────┴────────────────────────────────────────┴──────────────────────────────────────
```

---

## Kafka vs. What You Already Know

Nadia draws this on the whiteboard:

```
REST API (current):              Kafka (target):
───────────────────              ──────────────
Request/Response                 Publish/Subscribe
Synchronous                      Asynchronous
Point-to-point                   Broadcast to many consumers
Data gone after response         Data persisted (replayable)
Consumer pulls on schedule       Consumer gets events in real-time
Tight coupling                   Loose coupling
```

```
RabbitMQ (what you know):        Kafka (what you'll learn):
─────────────────────────        ────────────────────────
Message queue                    Event log
Message consumed = gone          Events persist (retention)
Smart broker, dumb consumer      Dumb broker, smart consumer
Good for task distribution       Good for event streaming
Thousands/sec                    Millions/sec
```

> "RabbitMQ is a post office — deliver the letter, throw it away. Kafka is a newspaper — publish it, everyone reads it, and you can read last week's edition." — Nadia

---

## The Architecture We're Building

By Chapter 20:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FleetPulse Event Backbone                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Producers:                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐   │
│  │ GPS Pings│  │  Orders  │  │  Driver  │  │  Route Changes       │   │
│  │ (12K/sec)│  │  (200/s) │  │  Events  │  │  (50/s)              │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────────┬───────────┘   │
│       │              │              │                    │               │
│       ▼              ▼              ▼                    ▼               │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    Kafka Cluster (5 brokers)                       │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────┐  │   │
│  │  │ truck.gps  │ │ orders     │ │ driver.    │ │ route.       │  │   │
│  │  │ (24 parts) │ │ (12 parts) │ │ events     │ │ changes      │  │   │
│  │  └────────────┘ └────────────┘ └────────────┘ └──────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│       │              │              │                    │               │
│       ▼              ▼              ▼                    ▼               │
│  Consumers:                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐   │
│  │Dispatcher│  │ Customer │  │ Billing  │  │  Data Warehouse      │   │
│  │Dashboard │  │ Tracking │  │ System   │  │  (Kafka Connect)     │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Schema Registry │ Monitoring (Grafana) │ Kafka Connect          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Core Concepts (Preview)

| Concept | One-Line Explanation |
|---|---|
| **Topic** | A named stream of events (like a database table for events) |
| **Partition** | A topic split into ordered segments for parallelism |
| **Producer** | Writes events to a topic |
| **Consumer** | Reads events from a topic |
| **Consumer Group** | Multiple consumers sharing the work of reading a topic |
| **Offset** | A consumer's position in a partition (like a bookmark) |
| **Broker** | A Kafka server that stores and serves events |
| **Replication** | Copies of partitions across brokers for fault tolerance |
| **Retention** | How long events are kept (hours, days, forever) |

---

## Prerequisites

### Docker Compose (Kafka Cluster)

```yaml
# docker-compose.yml
services:
  kafka:
    image: confluentinc/cp-kafka:7.6.0
    hostname: kafka
    ports:
      - "9092:9092"
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:29092,CONTROLLER://0.0.0.0:29093,EXTERNAL://0.0.0.0:9092
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,EXTERNAL://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT,EXTERNAL:PLAINTEXT
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka:29093
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      CLUSTER_ID: "MkU3OEVBNTcwNTJENDM2Qk"

  schema-registry:
    image: confluentinc/cp-schema-registry:7.6.0
    ports:
      - "8081:8081"
    environment:
      SCHEMA_REGISTRY_HOST_NAME: schema-registry
      SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS: kafka:29092
    depends_on:
      - kafka
```

```bash
docker compose up -d
```

### Python Client

```bash
pip install confluent-kafka fastavro
```

### Verify

```python
from confluent_kafka.admin import AdminClient

admin = AdminClient({"bootstrap.servers": "localhost:9092"})
metadata = admin.list_topics(timeout=5)
print(f"Connected! Brokers: {len(metadata.brokers)}")
print(f"Topics: {list(metadata.topics.keys())}")
```

If you see "Connected! Brokers: 1" — you're ready.

### CLI Tools

```bash
# Create a topic
docker exec -it kafka kafka-topics --create \
  --topic test --partitions 3 --replication-factor 1 \
  --bootstrap-server localhost:29092

# Produce a message
echo "hello kafka" | docker exec -i kafka kafka-console-producer \
  --topic test --bootstrap-server localhost:29092

# Consume messages
docker exec -it kafka kafka-console-consumer \
  --topic test --from-beginning --bootstrap-server localhost:29092
```

If you see "hello kafka" in the consumer — the cluster works.

---

## Kafka is Not a Queue

The biggest misconception: "Kafka is just a message queue."

| Message Queue (RabbitMQ) | Event Log (Kafka) |
|---|---|
| Message consumed → deleted | Event consumed → still there |
| One consumer gets each message | Many consumers read same events |
| No replay | Replay from any point in time |
| Broker tracks who got what | Consumer tracks its own position |
| Good for: task distribution | Good for: event streaming, audit, replay |

In Kafka, events are **immutable facts** that happened. "Truck 4521 was at lat 40.7, lng -74.0 at 14:32:07." That fact doesn't disappear after someone reads it. The billing system reads it. The dispatcher reads it. The analytics warehouse reads it. The event stays.

---

[Next: Chapter 1 — Replacing the Cron Job →](chapter-01-replacing-the-cron.md)

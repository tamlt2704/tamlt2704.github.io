# Kafka Mastery: An Event-Driven Survival Story

12,000 trucks. GPS pings every 5 seconds. A cron job that's 2 minutes behind. A contract for 80,000 trucks next month. Replace polling with real-time event streaming.

## The Story

You're at **FleetPulse** — a logistics startup tracking delivery trucks in real time. The current architecture polls the database every 60 seconds. At 12,000 trucks, it can't keep up. The dispatcher sees stale positions. Customers call asking where their package is. You have 3 weeks to build a Kafka-based event backbone before the 80,000-truck contract goes live.

## Chapters

### Part 1: Replace the Cron Job

| # | The Problem | What You Learn |
|---|------------|----------------|
| 01 | Cron job is 2 minutes behind | Topics, producers, consumers, brokers |
| 02 | GPS events arrive out of order | Partitions, keys, ordering guarantees |
| 03 | One consumer can't keep up | Consumer groups, parallel consumption |
| 04 | Consumer crashes, misses events | Offsets, commits, at-least-once |
| 05 | "What does this event mean?" | Schemas — Avro, JSON Schema, Registry |

### Part 2: Make It Reliable

| # | The Problem | What You Learn |
|---|------------|----------------|
| 06 | Billing gets duplicate charges | Exactly-once, idempotent producers, transactions |
| 07 | Dashboard needs enriched events | Stream processing — joins, filters |
| 08 | Need events in the warehouse | Kafka Connect — sinks, sources |
| 09 | Dead letter queue for failures | Error handling, DLQ, poison pills |
| 10 | Events need to trigger workflows | Choreography vs orchestration |

### Part 3: Handle 80,000 Trucks

| # | The Problem | What You Learn |
|---|------------|----------------|
| 11 | 3 brokers can't handle throughput | Cluster sizing, replication, ISR |
| 12 | Adding partitions breaks consumers | Rebalancing protocols, cooperative |
| 13 | Disk filling up | Retention, compaction, tiered storage |
| 14 | Consumer lag growing silently | Monitoring — JMX, lag, broker metrics |
| 15 | Broker dies during peak | Fault tolerance, leader election, rack awareness |

### Part 4: Ship It

| # | The Problem | What You Learn |
|---|------------|----------------|
| 16 | Schema change breaks consumers | Schema evolution, compatibility modes |
| 17 | Need to replay last week's events | Event sourcing, replay, temporal queries |
| 18 | Securing the cluster | SASL, ACLs, encryption |
| 19 | Testing event-driven systems | Testcontainers, embedded Kafka, contracts |
| 20 | 80,000 trucks go live | Capacity planning, tuning, launch checklist |

## Key Insight

Kafka is not a message queue. It's an immutable event log. Events don't disappear after consumption — they persist. Multiple consumers read the same events independently. You can replay from any point in time.

## Prerequisites

```bash
docker compose up -d  # Kafka + Schema Registry
pip install confluent-kafka fastavro
```

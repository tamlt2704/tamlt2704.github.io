---
title: "Chapter 2: Setup & CLI Tools"
date: 2026-05-29
series: "kafka-deep-dive"
chapter: 2
---

# Chapter 2: Setup & CLI Tools

[← Chapter 1: Concepts](../chapter-01-concepts) | [Chapter 3: Producer →](../chapter-03-producer)

---

## Docker Compose Setup (KRaft Mode)

```yaml
# docker-compose.yml
version: "3.8"
services:
  kafka:
    image: apache/kafka:3.7.0
    container_name: kafka
    ports:
      - "9092:9092"
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka:9093
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_LOG_DIRS: /tmp/kraft-combined-logs
      CLUSTER_ID: MkU3OEVBNTcwNTJENDM2Qk
    volumes:
      - kafka-data:/tmp/kraft-combined-logs

volumes:
  kafka-data:
```

Start and verify:

```bash
docker compose up -d
docker logs kafka
```

## CLI Tools

Enter the container:

```bash
docker exec -it kafka bash
```

### kafka-topics

```bash
# Create a topic
kafka-topics.sh --bootstrap-server localhost:9092 \
  --create --topic orders --partitions 3 --replication-factor 1

# List topics
kafka-topics.sh --bootstrap-server localhost:9092 --list

# Describe a topic
kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic orders

# Increase partitions
kafka-topics.sh --bootstrap-server localhost:9092 \
  --alter --topic orders --partitions 6

# Delete a topic
kafka-topics.sh --bootstrap-server localhost:9092 --delete --topic orders
```

### kafka-console-producer

```bash
# Simple producer (one message per line)
kafka-console-producer.sh --bootstrap-server localhost:9092 --topic orders

# Producer with keys (separator is ":")
kafka-console-producer.sh --bootstrap-server localhost:9092 \
  --topic orders \
  --property parse.key=true \
  --property key.separator=:
```

Example input with keys:

```
order-1:{"id":"order-1","amount":100}
order-2:{"id":"order-2","amount":200}
```

### kafka-console-consumer

```bash
# Consume from beginning
kafka-console-consumer.sh --bootstrap-server localhost:9092 \
  --topic orders --from-beginning

# Consume with keys and timestamps
kafka-console-consumer.sh --bootstrap-server localhost:9092 \
  --topic orders --from-beginning \
  --property print.key=true \
  --property print.timestamp=true

# Consume with a consumer group
kafka-console-consumer.sh --bootstrap-server localhost:9092 \
  --topic orders --group my-group
```

### kafka-consumer-groups

```bash
# List groups
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list

# Describe group (shows lag)
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --describe --group my-group

# Reset offsets to earliest
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group my-group --reset-offsets --to-earliest --topic orders --execute
```

## Workflow Diagram

```
  1. docker compose up -d
           │
           ▼
  2. kafka-topics.sh --create --topic orders
           │
           ▼
  3. kafka-console-producer.sh --topic orders
           │  (send test messages)
           ▼
  4. kafka-console-consumer.sh --topic orders
           │  (verify messages arrive)
           ▼
  5. Develop Java/Spring application
```

## Exercises

1. Start Kafka with Docker. Create topic `test-events` with 3 partitions. Produce 10 messages and consume them.

2. Produce keyed messages with keys `user-1`, `user-2`, `user-3`. Verify same key always goes to same partition.

3. Open two terminals with consumers in the same group. Observe partition distribution.

4. Consume some messages, then reset offsets to beginning. Verify re-consumption.

---

[← Chapter 1: Concepts](../chapter-01-concepts) | [Chapter 3: Producer →](../chapter-03-producer)

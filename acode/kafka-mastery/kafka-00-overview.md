# The Tale of EventStream: A Kafka Survival Guide

Remember PayFlow? The fintech startup where you survived dirty reads, deadlocks at 3 AM, and the million-TPS challenge?

You got promoted.

Derek — the CTO who once said *"PostgreSQL, Spring Boot, JPA. Ship it."* — now runs **EventStream**, an e-commerce platform. He poached you, Sana (your tech lead), and Raj (the senior dev who saved your career twice). Same crew, bigger stakes.

Day one, Derek pulls you into a conference room:

> "Orders, payments, inventory, notifications — they all need to talk to each other in real time. We're using Kafka. You're on it."

You nod. You've used message queues before. How hard can it be?

*You have no idea what's coming.*

---

## How to Read This

Every chapter follows the same loop — the same loop you'll live through at EventStream:

```
1. Something breaks (Slack alert / PagerDuty / angry customer)
2. You write a test that reproduces the bug
3. You understand WHY it broke
4. You fix it
5. The test goes green
6. You deploy and move on — until the next incident
```

The code always starts **wrong on purpose**. You'll see `⚠️ BUG` comments. You'll deploy the buggy code. It will break in production. Then you'll fix it. That's how you actually learn Kafka — not from docs, but from incidents.

---

## The Roadmap

Every chapter is a production incident. Every fix teaches a Kafka concept.

```
────┬────────────────────────────────────┬────────────────────────────────────────────────
Part│The Incident                        │What You Learn
────┼────────────────────────────────────┼────────────────────────────────────────────────
 01 │ Derek says "Ship Kafka"            │ Topics, partitions, producers, consumers, keys
────┼────────────────────────────────────┼────────────────────────────────────────────────
 02 │ Customer paid, order never shipped │ Delivery guarantees, acks, idempotent producer
────┼────────────────────────────────────┼────────────────────────────────────────────────
 03 │ Customer charged $500 twice        │ Idempotent consumers, deduplication
────┼────────────────────────────────────┼────────────────────────────────────────────────
 04 │ DB committed, Kafka lost the event │ Dual-write problem, transactional outbox
────┼────────────────────────────────────┼────────────────────────────────────────────────
 05 │ 2 million messages of consumer lag │ Partitions, batch consumption, concurrency
────┼────────────────────────────────────┼────────────────────────────────────────────────
 06 │ One bad message kills the pipeline │ Error handling, dead letter topics
────┼────────────────────────────────────┼────────────────────────────────────────────────
 07 │ Consumers rebalance every 30 sec   │ Rebalance tuning, sticky assignor, static groups
────┼────────────────────────────────────┼────────────────────────────────────────────────
 08 │ Adding a field breaks 15 services  │ Schema Registry, Avro, compatibility modes
────┼────────────────────────────────────┼────────────────────────────────────────────────
 09 │ Kafka Streams app creates dupes    │ Kafka transactions, isolation levels
────┼────────────────────────────────────┼────────────────────────────────────────────────
 10 │ Derek's final review before launch │ Topic design, architecture, production checklist
────┴────────────────────────────────────┴────────────────────────────────────────────────
```

---

## Prerequisites

You need one dependency. That's it.

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.kafka</groupId>
    <artifactId>spring-kafka</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.kafka</groupId>
    <artifactId>spring-kafka-test</artifactId>
    <scope>test</scope>
</dependency>
```

Kafka running locally? Use the Docker Compose from the [setup guide](setup-00-overview.md). Or just read the code — every chapter stands on its own.

---

## The Cast

- **Derek** — CTO. Makes the business decisions. Says things like *"Ship it"* and *"Why is the customer angry?"*
- **Sana** — Tech lead. Assigns your tasks. Reviews your PRs. Catches your bugs before production does (usually).
- **Raj** — Senior dev. Has seen every Kafka disaster. Mentors you through each incident. Drinks too much coffee.
- **You** — Junior dev. Fresh from PayFlow. About to learn Kafka the hard way.

---

[Next: The Genesis →](kafka-01-the-genesis.md)

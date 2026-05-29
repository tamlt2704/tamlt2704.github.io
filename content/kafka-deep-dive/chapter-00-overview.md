---
title: "Kafka Deep Dive: From Zero to Production"
date: 2026-05-29
series: "kafka-deep-dive"
chapter: 0
---

# Kafka Deep Dive: From Zero to Production

A comprehensive guide to Apache Kafka covering core concepts, hands-on setup, producer/consumer patterns, streaming, and production-grade deployment with Java/Spring Boot.

## Chapters

| #   | Chapter                                          | Description                                                                 |
| --- | ------------------------------------------------ | --------------------------------------------------------------------------- |
| 1   | [Core Concepts](../chapter-01-concepts)          | Topics, partitions, brokers, producers, consumers, offsets, consumer groups |
| 2   | [Setup & CLI Tools](../chapter-02-setup)         | Docker Compose setup, topic management, console producer/consumer           |
| 3   | [Producer (Java/Spring)](../chapter-03-producer) | KafkaTemplate, serializers, partitioning, acks, retries, idempotency        |
| 4   | [Consumer (Java/Spring)](../chapter-04-consumer) | @KafkaListener, deserialization, offset management, rebalancing             |
| 5   | [Patterns](../chapter-05-patterns)               | Event sourcing, CQRS, saga, outbox, dead letter topics, retry topics        |
| 6   | [Kafka Streams](../chapter-06-streams)           | KStream, KTable, joins, windowing, stateful processing                      |
| 7   | [Production](../chapter-07-production)           | Monitoring, scaling, exactly-once semantics, Schema Registry, security      |

## Prerequisites

- Java 17+
- Docker and Docker Compose
- Gradle 8+
- Basic understanding of distributed systems

## Project Setup

All examples use Spring Boot 3.x with Gradle:

```groovy
plugins {
    id 'java'
    id 'org.springframework.boot' version '3.2.5'
    id 'io.spring.dependency-management' version '1.1.4'
}

group = 'com.example'
version = '0.0.1-SNAPSHOT'

java {
    sourceCompatibility = '17'
}

repositories {
    mavenCentral()
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter'
    implementation 'org.springframework.kafka:spring-kafka'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testImplementation 'org.springframework.kafka:spring-kafka-test'
}
```

## How to Use This Guide

Work through chapters sequentially. Each chapter builds on the previous one and includes conceptual explanations with diagrams, working code examples, and practical exercises.

---

Next: [Chapter 1 - Core Concepts](../chapter-01-concepts)

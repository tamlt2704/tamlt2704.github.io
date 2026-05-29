# ActiveMQ: From Basics to Production

[next: Messaging Concepts](/blog/activemq/chapter-01-concepts)

## What is ActiveMQ?

Apache ActiveMQ is an open-source message broker that implements the Java Message Service (JMS) specification. It enables applications to communicate asynchronously by sending messages through queues and topics, decoupling producers from consumers.

There are two major versions:

- **ActiveMQ Classic** — The original, mature broker with a wide feature set and extensive community support
- **ActiveMQ Artemis** — The next-generation broker (formerly HornetQ), designed for high performance with a non-blocking architecture and journal-based persistence

## When to Use ActiveMQ

- Decoupling microservices
- Asynchronous task processing (order processing, email sending)
- Event-driven architectures
- Load balancing work across multiple consumers
- Reliable message delivery with guaranteed processing

## Classic vs Artemis at a Glance

| Feature       | Classic                     | Artemis                              |
| ------------- | --------------------------- | ------------------------------------ |
| Storage       | KahaDB                      | Journal-based (libaio/NIO)           |
| Protocol      | OpenWire, STOMP, AMQP, MQTT | AMQP, STOMP, MQTT, OpenWire, HornetQ |
| Clustering    | Network of Brokers          | Live/Backup pairs                    |
| Address Model | Queues + Topics (JMS)       | Addresses with anycast/multicast     |
| Performance   | Good                        | Higher throughput, lower latency     |
| Web Console   | Built-in                    | Hawtio-based                         |

## Chapters

1. [Messaging Concepts](/blog/activemq/chapter-01-concepts) — Fundamentals of messaging, JMS, queues, topics, and message types
2. [Setup](/blog/activemq/chapter-02-setup) — Docker setup, web console, CLI tools, and embedded broker
3. [Spring Boot + JMS](/blog/activemq/chapter-03-spring-jms) — JmsTemplate, listeners, message converters, and configuration
4. [Messaging Patterns](/blog/activemq/chapter-04-patterns) — Request-reply, competing consumers, DLQ, scheduled delivery
5. [Reliability](/blog/activemq/chapter-05-reliability) — Persistence, transactions, acknowledgment, redelivery, idempotency
6. [ActiveMQ Artemis Specifics](/blog/activemq/chapter-06-artemis) — Address model, diverts, large messages, multi-protocol support
7. [Production](/blog/activemq/chapter-07-production) — Clustering, HA, monitoring, security, and performance tuning

## Prerequisites

- Java 17+
- Docker
- Gradle 8+
- Spring Boot 3.x
- Basic understanding of distributed systems

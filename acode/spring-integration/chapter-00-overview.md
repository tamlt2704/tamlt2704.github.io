# FlowForge: A Spring Integration Survival Story

You've built REST APIs. You've wired up databases. You thought enterprise Java was just CRUD endpoints and JSON responses.

Then **Miriam**, the integration architect at **MediBridge** — a healthcare data company that routes lab results, prescriptions, and insurance claims between 40 hospitals, 12 pharmacies, and 3 insurance providers — sends you a message:

> "We're replacing the legacy ESB. It's a $200k/year IBM box that routes HL7 messages, transforms XML, polls FTP servers, and nobody knows how it works. The vendor is sunsetting it. You start Monday."

You show up. The ESB has 347 "flows" configured through a drag-and-drop GUI. No version control. No tests. The last person who understood it retired in 2021. The only documentation is a Visio diagram from 2018 with a sticky note that says "DO NOT TOUCH FLOW #214."

Your mission: rebuild it in Spring Integration — message by message, channel by channel, flow by flow.

---

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Integration Developer | "I know Spring Boot. How different can this be?" |
| **Miriam** | Integration Architect | Thinks in message flows. Draws channel diagrams on napkins. |
| **The ESB** | Legacy System | 347 flows. Zero tests. Haunted by Flow #214. |
| **Dr. Patel** | Hospital CTO | "If lab results are late, patients suffer. No pressure." |
| **Compliance Carl** | Security Officer | "Every message must be auditable. Every. Single. One." |
| **The Dead Letter** | Failed Messages | Where messages go to die. Nobody checks it. |

---

## The Tools

Everything runs on your laptop. No ESB license needed.

| Tool | What It Does |
|---|---|
| **Java 21** | The language |
| **Spring Boot 3.3+** | Application framework |
| **Spring Integration 6.3+** | Enterprise Integration Patterns (EIP) implementation |
| **Spring Integration DSL** | Java-based flow configuration (no XML) |
| **H2 / PostgreSQL** | Message store, metadata |
| **Docker** | For external systems (FTP, SFTP, ActiveMQ, RabbitMQ) |
| **Testcontainers** | Integration tests with real infrastructure |

---

## How to Read This

Every chapter follows the same loop:

```
  📋 Miriam assigns a flow to migrate
   │
   ▼
  🤔 You learn the Enterprise Integration Pattern behind it
   │
   ▼
  ⌨️  You implement it in Spring Integration DSL
   │
   ▼
  💥 Something breaks (messages lost, duplicates, ordering issues)
   │
   ▼
  🧠 You understand WHY and fix it
   │
   ▼
  ✓  Tests prove it works — even under failure conditions
```

No pattern shows up before you need it. You won't hear about message stores until messages get lost. You won't touch aggregators until partial results corrupt a report.

The failures come first. The patterns follow.

---

## The Roadmap

| Ch | The Flow to Migrate | What You Learn |
|---|---|---|
| 1 | "Route a message from A to B" | Messages, channels, endpoints, the DSL basics |
| 2 | "Transform HL7 to JSON" | Transformers, message headers, content type |
| 3 | "Route labs to the right hospital" | Routers, header-based routing, recipient lists |
| 4 | "Split a batch file into individual records" | Splitters, aggregators, correlation |
| 5 | "Poll the FTP server every 5 minutes" | Inbound adapters, pollers, idempotent receivers |
| 6 | "Send results to the pharmacy's SFTP" | Outbound adapters, gateways, error handling |
| 7 | "If it fails, retry 3 times then dead-letter it" | Error channels, retry, circuit breaker |
| 8 | "Process 10,000 messages without falling over" | Executors, QueueChannels, backpressure, throttling |
| 9 | "Don't lose messages when the server restarts" | Message stores, JdbcChannelMessageStore, transactions |
| 10 | "Prove to Compliance Carl that every message was delivered" | Wire tap, channel interceptors, metrics, observability |

---

## Prerequisites

Three things: Java 21, Docker, and a terminal.

### Java 21 (Amazon Corretto)

```bash
# Windows (winget)
winget install Amazon.Corretto.21

# macOS
brew install --cask corretto21

# Linux
curl -LO https://corretto.aws/downloads/latest/amazon-corretto-21-x64-linux-jdk.tar.gz
tar -xzf amazon-corretto-21-x64-linux-jdk.tar.gz
export JAVA_HOME=$(pwd)/amazon-corretto-21.*
export PATH=$JAVA_HOME/bin:$PATH
```

### Docker

```bash
# Verify
docker --version
```

We'll use Docker for FTP servers, message brokers, and databases in later chapters.

### Project Setup

```bash
mkdir flowforge && cd flowforge
```

Use [start.spring.io](https://start.spring.io) or create `build.gradle`:

```groovy
plugins {
    id 'java'
    id 'org.springframework.boot' version '3.3.0'
    id 'io.spring.dependency-management' version '1.1.5'
}

group = 'com.medibridge'
version = '1.0.0'

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}

repositories {
    mavenCentral()
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-integration'
    implementation 'org.springframework.integration:spring-integration-file'

    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testImplementation 'org.springframework.integration:spring-integration-test'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}

tasks.named('test') {
    useJUnitPlatform()
}
```

And `settings.gradle`:

```groovy
rootProject.name = 'flowforge'
```

Generate the wrapper:

```bash
gradle wrapper
```

### Verify

```java
// src/main/java/com/medibridge/FlowForgeApplication.java
package com.medibridge;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.integration.annotation.IntegrationComponentScan;

@SpringBootApplication
@IntegrationComponentScan
public class FlowForgeApplication {
    public static void main(String[] args) {
        SpringApplication.run(FlowForgeApplication.class, args);
    }
}
```

```bash
./gradlew bootRun
```

If it starts without errors, you're ready.

---

## The Mental Model

Spring Integration implements **Enterprise Integration Patterns** (the book by Hohpe & Woolf). The core idea:

```
  Producer → Channel → Endpoint → Channel → Consumer
```

- **Message**: A packet of data (payload) + metadata (headers)
- **Channel**: A pipe that connects components. Messages flow through channels.
- **Endpoint**: Something that processes a message (transform, route, filter, split, aggregate)
- **Adapter**: Connects to external systems (files, FTP, HTTP, JMS, databases)

Think of it like plumbing. Messages are water. Channels are pipes. Endpoints are valves, filters, and splitters. Adapters are the faucets and drains that connect to the outside world.

The ESB did all this with a GUI. You'll do it with code — testable, version-controlled, reviewable code.

---

## The Dataset

Throughout this series, we'll work with healthcare messages:

| Message Type | Format | Example |
|---|---|---|
| Lab Result | HL7 v2 / JSON | Blood test results for patient |
| Prescription | JSON | Medication order from doctor |
| Insurance Claim | XML | Billing claim to insurance provider |
| Appointment | JSON | Scheduled visit notification |

We'll simulate these with test fixtures. No real patient data — Compliance Carl would have a heart attack.

---

[Next: Chapter 1 — "Route a Message from A to B" →](chapter-01-messages-channels.md)

# Setup: Spring Boot Configuration

[← Docker Services](setup-01-docker.md) | [Back to Quick Start →](setup-00-overview.md)

---

## pom.xml Dependencies

```xml
<dependencies>
    <!-- Web -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>

    <!-- JPA + PostgreSQL -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>
    <dependency>
        <groupId>org.postgresql</groupId>
        <artifactId>postgresql</artifactId>
        <scope>runtime</scope>
    </dependency>

    <!-- Kafka -->
    <dependency>
        <groupId>org.springframework.kafka</groupId>
        <artifactId>spring-kafka</artifactId>
    </dependency>
</dependencies>
```

## application.yml

```yaml
spring:
  # ── PostgreSQL ──────────────────────────────────
  datasource:
    url: jdbc:postgresql://localhost:5432/payflow?reWriteBatchedInserts=true
    username: payflow
    password: payflow
    hikari:
      maximum-pool-size: 20
      minimum-idle: 20

  jpa:
    hibernate:
      ddl-auto: update          # Dev only. Use Flyway/Liquibase in production.
    open-in-view: false          # Always disable — prevents lazy-loading bugs
    properties:
      hibernate:
        jdbc:
          batch_size: 50
          batch_versioned_data: true
        order_inserts: true
        order_updates: true

  # ── Kafka ───────────────────────────────────────
  kafka:
    bootstrap-servers: localhost:9092
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
      acks: all
      properties:
        enable.idempotence: true
    consumer:
      group-id: ${spring.application.name}
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.springframework.kafka.support.serializer.JsonDeserializer
      auto-offset-reset: earliest
      properties:
        spring.json.trusted.packages: "com.yourpackage.*"
        partition.assignment.strategy: org.apache.kafka.clients.consumer.CooperativeStickyAssignor

  application:
    name: payflow
```

## Key Config Decisions Explained

### PostgreSQL Side

| Setting | Value | Why |
|---|---|---|
| `reWriteBatchedInserts=true` | In JDBC URL | 2-5x insert throughput ([Chapter 4 of JPA guide](04-the-million-tps-challenge.md)) |
| `batch_size: 50` | Hibernate | Batches INSERT/UPDATE statements |
| `open-in-view: false` | Spring | Prevents accidental lazy loading in controllers |
| `ddl-auto: update` | Dev only | Auto-creates tables. Use Flyway in production. |

### Kafka Side

| Setting | Value | Why |
|---|---|---|
| `acks: all` | Producer | No message loss ([Chapter 2 of Kafka guide](kafka-02-the-lost-order-incident.md)) |
| `enable.idempotence` | Producer | Prevents duplicates on retry |
| `auto-offset-reset: earliest` | Consumer | New consumer groups read from beginning |
| `CooperativeStickyAssignor` | Consumer | Minimizes rebalance disruption ([Chapter 7](kafka-07-the-rebalance-storm.md)) |

## Smoke Test

Create a minimal producer and consumer to verify everything works:

### Producer Endpoint

```java
@RestController
@RequiredArgsConstructor
public class TestController {

    private final KafkaTemplate<String, String> kafka;

    @PostMapping("/test")
    public String send(@RequestParam String msg) {
        kafka.send("test-topic", msg);
        return "sent: " + msg;
    }
}
```

### Consumer

```java
@Service
@Slf4j
public class TestConsumer {

    @KafkaListener(topics = "test-topic", groupId = "test-group")
    public void listen(String message) {
        log.info("Received: {}", message);
    }
}
```

### Run It

```bash
# 1. Start Docker services
docker compose up -d

# 2. Start your Spring Boot app
./mvnw spring-boot:run

# 3. Send a test message
curl -X POST "http://localhost:8088/test?msg=hello"

# 4. Check your app logs — you should see "Received: hello"

# 5. Open Kafka UI at http://localhost:8080 — see the message in test-topic
```

If you see `Received: hello` in the logs, everything is wired correctly. You're ready to build the PayFlow/EventStream apps from the tutorials.

---

[← Docker Services](setup-01-docker.md) | [Back to Quick Start →](setup-00-overview.md)

# Chapter 10: Prove Every Message Was Delivered

[← Chapter 9: Don't Lose Messages on Restart](chapter-09-message-store.md)

---

## The Task

Compliance Carl walks over with a clipboard:

> "For our HIPAA audit, I need to answer three questions for any message:
> 1. Did it arrive?
> 2. Where did it go?
> 3. When was it delivered?
>
> For every single message. Going back 7 years. Can your system do that?"

Miriam translates:

> "Wire tap every channel. Log every message. Expose metrics. Build an audit trail that Compliance Carl can query."

---

## Wire Tap: Non-Invasive Monitoring

A **wire tap** copies every message on a channel to a secondary channel — without affecting the main flow. Like a phone tap: the conversation continues normally, but someone's listening.

```java
// src/main/java/com/medibridge/config/AuditConfig.java
package com.medibridge.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.integration.channel.DirectChannel;
import org.springframework.integration.channel.interceptor.WireTap;
import org.springframework.integration.dsl.IntegrationFlow;
import org.springframework.messaging.MessageChannel;

@Configuration
public class AuditConfig {

    @Bean
    public MessageChannel auditChannel() {
        return new DirectChannel();
    }

    @Bean
    public WireTap auditWireTap() {
        return new WireTap("auditChannel");
    }

    // Apply wire tap to specific channels
    @Bean
    public MessageChannel rawLabChannel() {
        DirectChannel channel = new DirectChannel();
        channel.addInterceptor(auditWireTap());
        return channel;
    }

    @Bean
    public MessageChannel processedLabChannel() {
        DirectChannel channel = new DirectChannel();
        channel.addInterceptor(auditWireTap());
        return channel;
    }
}
```

### The Audit Flow

```java
@Bean
public IntegrationFlow auditFlow(DataSource dataSource) {
    return IntegrationFlow.from("auditChannel")
        .handle(new JdbcMessageHandler(dataSource,
            """
            INSERT INTO message_audit
              (message_id, correlation_id, channel_name, payload_type, payload_summary,
               headers_json, received_at)
            VALUES
              (:headers[id], :headers[correlationId], :headers[history][-1],
               :payload.class.simpleName, LEFT(CAST(:payload AS TEXT), 500),
               CAST(:headers AS TEXT), NOW())
            """))
        .get();
}
```

Schema:

```sql
CREATE TABLE message_audit (
    id BIGSERIAL PRIMARY KEY,
    message_id VARCHAR(36) NOT NULL,
    correlation_id VARCHAR(36),
    channel_name VARCHAR(255),
    payload_type VARCHAR(100),
    payload_summary TEXT,
    headers_json TEXT,
    received_at TIMESTAMP NOT NULL,
    INDEX idx_audit_message_id (message_id),
    INDEX idx_audit_correlation_id (correlation_id),
    INDEX idx_audit_received_at (received_at)
);
```

Now every message that passes through `rawLabChannel` or `processedLabChannel` gets a row in the audit table. Compliance Carl can query: "Show me message MSG-001 — when did it arrive, where did it go?"

---

## Channel Interceptors: Custom Monitoring

Wire taps copy messages. **Interceptors** let you observe (or modify) messages at specific lifecycle points:

```java
// src/main/java/com/medibridge/interceptors/TimingInterceptor.java
package com.medibridge.interceptors;

import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import org.springframework.messaging.Message;
import org.springframework.messaging.MessageChannel;
import org.springframework.messaging.support.ChannelInterceptor;
import org.springframework.stereotype.Component;

@Component
public class TimingInterceptor implements ChannelInterceptor {

    private final MeterRegistry meterRegistry;

    public TimingInterceptor(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
    }

    @Override
    public Message<?> preSend(Message<?> message, MessageChannel channel) {
        // Record when the message enters the channel
        return message;  // Return null to block the message
    }

    @Override
    public void afterSendCompletion(Message<?> message, MessageChannel channel,
                                     boolean sent, Exception ex) {
        String channelName = channel.toString();
        if (sent) {
            meterRegistry.counter("messages.sent", "channel", channelName).increment();
        } else {
            meterRegistry.counter("messages.failed", "channel", channelName).increment();
        }
    }
}
```

### Global Interceptor (All Channels)

```java
@Bean
public GlobalChannelInterceptor globalTimingInterceptor(TimingInterceptor interceptor) {
    return new GlobalChannelInterceptor() {
        // Applied to all channels automatically
    };
}

// Or via configuration:
@Bean
@GlobalChannelInterceptor(patterns = "*")
public ChannelInterceptor metricsInterceptor(MeterRegistry registry) {
    return new TimingInterceptor(registry);
}
```

---

## Micrometer Metrics: Dashboards

Spring Integration has built-in Micrometer support:

```groovy
// build.gradle
implementation 'org.springframework.boot:spring-boot-starter-actuator'
implementation 'io.micrometer:micrometer-registry-prometheus'
```

```yaml
# application.yml
management:
  endpoints:
    web:
      exposure:
        include: health, metrics, prometheus, integrationgraph
  metrics:
    tags:
      application: flowforge
spring:
  integration:
    management:
      observation-patterns: "*"  # Enable observation for all components
```

This exposes metrics at `/actuator/prometheus`:

```
# Messages sent per channel
spring_integration_channel_sends_total{channel="rawLabChannel"} 10234
spring_integration_channel_sends_total{channel="processedLabChannel"} 10198

# Message handling duration
spring_integration_handler_duration_seconds{handler="hl7ToJsonTransformer"} 0.045

# Queue depth
spring_integration_channel_queue_size{channel="processingQueue"} 47

# Error count
spring_integration_channel_sends_total{channel="errorChannel"} 36
```

---

## Integration Graph: Visualize the Flows

Spring Integration exposes a graph of all components:

```
GET /actuator/integrationgraph
```

```json
{
  "nodes": [
    {"nodeId": 1, "name": "labRoutingFlow.channel#0", "componentType": "DirectChannel"},
    {"nodeId": 2, "name": "hl7ToJsonTransformer", "componentType": "transformer"},
    {"nodeId": 3, "name": "headerRouter", "componentType": "router"}
  ],
  "links": [
    {"from": 1, "to": 2},
    {"from": 2, "to": 3}
  ]
}
```

This powers visual dashboards — you can see message flow in real time.

---

## End-to-End Tracking: Correlation IDs

Every message gets a unique ID. But when a message is split into 200 pieces, transformed, and routed — how do you trace the full journey?

**Correlation IDs** link related messages:

```java
@Bean
public IntegrationFlow trackedFlow() {
    return IntegrationFlow.from("inboundChannel")
        .enrichHeaders(h -> h
            .headerExpression("traceId",
                "headers['traceId'] ?: T(java.util.UUID).randomUUID().toString()")
            .header("entryTimestamp", System.currentTimeMillis()))
        .transform(/* ... */)
        .split(/* ... */)
        // Each split message inherits the traceId
        .transform(/* ... */)
        .handle((payload, headers) -> {
            // Log the complete trace
            auditService.recordDelivery(
                headers.get("traceId", String.class),
                headers.get("id").toString(),
                "DELIVERED",
                Instant.now()
            );
            return payload;
        })
        .get();
}
```

Now Compliance Carl can query: "Show me everything related to trace `abc-123`" — and get the full journey from inbound to delivery.

---

## The Compliance Query

```sql
-- "Show me the journey of message MSG-001"
SELECT message_id, channel_name, payload_type, received_at
FROM message_audit
WHERE correlation_id = 'abc-123-def-456'
ORDER BY received_at;
```

```
message_id  | channel_name        | payload_type | received_at
------------|---------------------|--------------|--------------------
msg-001     | rawLabChannel       | String       | 2024-03-15 08:00:01
msg-001     | transformedChannel  | String       | 2024-03-15 08:00:01
msg-001-1   | splitChannel        | String       | 2024-03-15 08:00:02
msg-001-2   | splitChannel        | String       | 2024-03-15 08:00:02
msg-001-1   | hospAChannel        | String       | 2024-03-15 08:00:02
msg-001-2   | hospBChannel        | String       | 2024-03-15 08:00:02
```

Compliance Carl: "I can see it arrived at 08:00:01, was split into 2 results, and delivered to Hospital A and B by 08:00:02. Acceptable."

---

## Health Checks

```java
@Component
public class IntegrationHealthIndicator implements HealthIndicator {

    private final QueueChannel processingQueue;
    private final JdbcChannelMessageStore messageStore;

    @Override
    public Health health() {
        int queueDepth = processingQueue.getQueueSize();
        long deadLetters = deadLetterRepository.countUnresolved();

        Health.Builder builder = (queueDepth < 900 && deadLetters < 100)
            ? Health.up()
            : Health.down();

        return builder
            .withDetail("queueDepth", queueDepth)
            .withDetail("queueCapacity", 1000)
            .withDetail("unresolvedDeadLetters", deadLetters)
            .withDetail("messagesProcessedToday", auditRepository.countToday())
            .build();
    }
}
```

---

## The Complete Architecture

```
  Lab System (FTP/SFTP)
       │
       │ poll every 5 min
       ▼
  [Inbound Adapter] ──wire tap──→ [Audit DB]
       │
       ▼
  [Persistent Queue] (JdbcChannelMessageStore)
       │
       │ 5 threads, transactional
       ▼
  [Transformer] (HL7 → JSON) ──wire tap──→ [Audit DB]
       │
       ▼
  [Splitter] (batch → individual)
       │
       ▼
  [Router] (destination header)
       │
       ├── HOSP_A → [SFTP Adapter] ──wire tap──→ [Audit DB]
       ├── HOSP_B → [SFTP Adapter] ──wire tap──→ [Audit DB]
       ├── HOSP_C → [SFTP Adapter] ──wire tap──→ [Audit DB]
       └── unknown → [Dead Letter]
       
  Error path:
  [Any failure] → [Retry 5×] → [Circuit Breaker] → [Dead Letter Table]
  
  Monitoring:
  /actuator/prometheus → Grafana dashboards
  /actuator/health → Kubernetes liveness/readiness
  /actuator/integrationgraph → Flow visualization
```

---

## Report to Compliance Carl

> **Audit trail complete:**
> - Every message wire-tapped at entry, transformation, and delivery
> - Correlation IDs link split/routed messages back to their source
> - Audit table queryable by message ID, correlation ID, time range, channel
> - 7-year retention via database partitioning
> - Prometheus metrics: messages/sec, queue depth, error rate, latency
> - Health endpoint: queue depth, dead-letter count, daily throughput
>
> For any message, we can answer: Did it arrive? ✓ Where did it go? ✓ When was it delivered? ✓

Compliance Carl signs off. The audit passes.

---

## The Migration is Done

The ESB had 347 flows. You've rebuilt the patterns that cover all of them:

| Chapter | Pattern | ESB Equivalent |
|---|---|---|
| 1 | Messages, Channels, Endpoints | Basic flow wiring |
| 2 | Transformers | Transformation maps |
| 3 | Routers, Filters | Content-based routing |
| 4 | Splitters, Aggregators | Batch processing |
| 5 | Inbound Adapters, Pollers | FTP/SFTP polling |
| 6 | Outbound Adapters, Gateways | External system delivery |
| 7 | Error handling, Retry, Circuit Breaker | Exception management |
| 8 | Concurrency, Backpressure | Throughput scaling |
| 9 | Message Stores, Transactions | Persistence, reliability |
| 10 | Wire Tap, Metrics, Audit | Observability, compliance |

The $200k/year ESB is replaced by a Spring Boot application that's:
- **Version controlled** (not a GUI blob)
- **Testable** (integration tests for every flow)
- **Observable** (Prometheus, health checks, audit trail)
- **Resilient** (retries, circuit breakers, persistent queues)
- **Scalable** (thread pools, backpressure, horizontal scaling)

---

## What You Learned (Series Recap)

1. **Messages** = payload + headers. Immutable. The unit of work.
2. **Channels** connect components. DirectChannel (sync) vs QueueChannel (async).
3. **Transformers** change payloads. Header enrichers change metadata.
4. **Routers** direct traffic. Filters drop unwanted messages.
5. **Splitters** break batches into individual messages. Aggregators reassemble them.
6. **Inbound adapters** read from external systems. Pollers control the rhythm.
7. **Outbound adapters** write to external systems. Gateways provide request-reply.
8. **Error channels** catch failures. Retry + circuit breaker + dead-letter = nothing vanishes.
9. **Concurrency** via thread pools and QueueChannels. Backpressure prevents overload.
10. **Message stores** persist state across restarts. Transactions ensure all-or-nothing.
11. **Wire taps** and interceptors provide non-invasive monitoring.
12. **The DSL** makes flows readable, testable, and version-controllable.

---

## Next Steps (If You Keep Going)

- **Spring Cloud Stream** — when you outgrow in-process channels and need Kafka/RabbitMQ
- **Spring Integration + Kubernetes** — scaling flows across pods
- **Event-driven architecture** — CQRS, event sourcing with Spring Integration
- **Custom adapters** — write your own for proprietary protocols
- **Spring Batch + Integration** — large-scale batch processing with messaging triggers

But that's another series.

---

*The ESB is dead. Long live the flow.*

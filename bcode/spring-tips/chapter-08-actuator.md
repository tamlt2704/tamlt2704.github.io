# Chapter 8: Actuator & Observability — Know What Your App Is Doing

[← Chapter 7: Testing](chapter-07-testing.md) | [Chapter 9: Security →](chapter-09-security.md)

---

## The Problem

"My app is slow in production but I don't know why. I can't tell if the database pool is exhausted or if an external API is timing out. When something breaks at 3am, I'm flying blind."

## Actuator Setup

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

```yaml
# application.yml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: when-authorized
  metrics:
    tags:
      application: ${spring.application.name}
```

## Custom Health Indicators

```java
@Component
public class PaymentGatewayHealthIndicator implements HealthIndicator {

    private final PaymentClient paymentClient;

    public PaymentGatewayHealthIndicator(PaymentClient paymentClient) {
        this.paymentClient = paymentClient;
    }

    @Override
    public Health health() {
        try {
            long start = System.currentTimeMillis();
            boolean reachable = paymentClient.ping();
            long latency = System.currentTimeMillis() - start;

            if (!reachable) {
                return Health.down()
                    .withDetail("reason", "Payment gateway unreachable")
                    .build();
            }
            return Health.up()
                .withDetail("latencyMs", latency)
                .withDetail("gateway", "stripe")
                .build();
        } catch (Exception e) {
            return Health.down(e).build();
        }
    }
}
```

Response at `/actuator/health`:
```json
{
  "status": "UP",
  "components": {
    "paymentGateway": { "status": "UP", "details": { "latencyMs": 45, "gateway": "stripe" } },
    "db": { "status": "UP" },
    "diskSpace": { "status": "UP" }
  }
}
```

## Custom Metrics with Micrometer

```java
@Service
public class OrderService {
    private final Counter ordersCreated;
    private final Counter ordersFailed;
    private final Timer orderProcessingTime;
    private final AtomicInteger activeOrders;

    public OrderService(MeterRegistry registry) {
        this.ordersCreated = Counter.builder("orders.created")
            .description("Total orders created")
            .tag("service", "order")
            .register(registry);

        this.ordersFailed = Counter.builder("orders.failed")
            .description("Total failed orders")
            .register(registry);

        this.orderProcessingTime = Timer.builder("orders.processing.time")
            .description("Order processing duration")
            .publishPercentiles(0.5, 0.95, 0.99)
            .register(registry);

        // Gauge — tracks current value (not cumulative)
        this.activeOrders = registry.gauge("orders.active",
            new AtomicInteger(0));
    }

    public Order createOrder(OrderRequest request) {
        activeOrders.incrementAndGet();
        try {
            return orderProcessingTime.record(() -> {
                Order order = processOrder(request);
                ordersCreated.increment();
                return order;
            });
        } catch (Exception e) {
            ordersFailed.increment();
            throw e;
        } finally {
            activeOrders.decrementAndGet();
        }
    }
}
```

## Custom Actuator Endpoint

```java
@Component
@Endpoint(id = "features")
public class FeatureEndpoint {

    private final FeatureFlags featureFlags;

    public FeatureEndpoint(FeatureFlags featureFlags) {
        this.featureFlags = featureFlags;
    }

    @ReadOperation
    public Map<String, Boolean> features() {
        return Map.of(
            "emailNotifications", featureFlags.emailNotifications(),
            "experimentalSearch", featureFlags.experimentalSearch(),
            "rateLimiting", featureFlags.rateLimiting()
        );
    }

    @WriteOperation
    public Map<String, String> toggle(@Selector String feature, boolean enabled) {
        // Toggle at runtime (if backed by mutable source)
        return Map.of("feature", feature, "enabled", String.valueOf(enabled));
    }
}
```

Access: `GET /actuator/features`, `POST /actuator/features/experimentalSearch`

## Structured Logging

```xml
<!-- logback-spring.xml -->
<configuration>
    <springProfile name="prod">
        <appender name="JSON" class="ch.qos.logback.core.ConsoleAppender">
            <encoder class="net.logstash.logback.encoder.LogstashEncoder">
                <includeMdcKeyName>traceId</includeMdcKeyName>
                <includeMdcKeyName>userId</includeMdcKeyName>
            </encoder>
        </appender>
        <root level="INFO"><appender-ref ref="JSON" /></root>
    </springProfile>
</configuration>
```

Add context to every log line:

```java
@Component
public class RequestContextFilter extends OncePerRequestFilter {
    @Override
    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res,
                                     FilterChain chain) throws ServletException, IOException {
        try {
            MDC.put("userId", extractUserId(req));
            MDC.put("requestId", UUID.randomUUID().toString());
            chain.doFilter(req, res);
        } finally {
            MDC.clear();
        }
    }
}
```

## Distributed Tracing

```xml
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-tracing-bridge-otel</artifactId>
</dependency>
<dependency>
    <groupId>io.opentelemetry</groupId>
    <artifactId>opentelemetry-exporter-otlp</artifactId>
</dependency>
```

```yaml
management:
  tracing:
    sampling:
      probability: 1.0  # 100% in dev, lower in prod
  otlp:
    tracing:
      endpoint: http://localhost:4318/v1/traces
```

Spring Boot 3.2+ auto-propagates trace IDs across RestClient, WebClient, and JMS.

## What You Learned

- **Health indicators** — custom checks for external dependencies
- **Micrometer metrics** — counters, timers, gauges with percentiles
- **Custom endpoints** — expose app-specific operational data
- **Structured logging** — JSON logs with MDC context (userId, traceId)
- **Distributed tracing** — auto-propagated trace IDs with OpenTelemetry
- **Prometheus** — `/actuator/prometheus` for Grafana dashboards

---

[← Chapter 7: Testing](chapter-07-testing.md) | [Chapter 9: Security →](chapter-09-security.md)

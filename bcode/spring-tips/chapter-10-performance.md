# Chapter 10: Performance — Make Spring Boot Fast

[← Chapter 9: Security](chapter-09-security.md) | [README →](README.md)

---

## The Problem

"My app takes 12 seconds to start. The connection pool exhausts under load. I want sub-100ms response times but I'm calling three external services per request."

## HikariCP Tuning

Spring Boot uses HikariCP by default. The defaults are conservative:

```yaml
# application.yml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20          # Default: 10. Set to 2x CPU cores for most apps
      minimum-idle: 5                # Keep connections warm
      idle-timeout: 300000           # 5 min — close idle connections
      max-lifetime: 1800000          # 30 min — recycle before DB timeout
      connection-timeout: 5000       # 5s — fail fast if pool exhausted
      leak-detection-threshold: 30000  # Log warning if connection held > 30s
```

Rule of thumb: `pool size = (CPU cores * 2) + effective_spindle_count`. For most cloud apps with SSDs, 15-25 is the sweet spot. More connections ≠ more throughput.

## Lazy Bean Initialization

Speed up startup by deferring bean creation until first use:

```yaml
# application.yml — global lazy init
spring:
  main:
    lazy-initialization: true
```

Selective lazy init (better for production):

```java
@Configuration
public class ExpensiveConfig {

    @Bean
    @Lazy  // Only created when first injected
    public ReportEngine reportEngine() {
        // Takes 3 seconds to initialize — don't block startup
        return new ReportEngine(loadTemplates());
    }
}
```

Tradeoff: first request to a lazy bean is slower. Use for rarely-used beans, not core request paths.

## Startup Time Optimization

```yaml
# Disable what you don't use
spring:
  jmx:
    enabled: false
  main:
    banner-mode: off

# Skip classpath scanning for large codebases
logging:
  level:
    org.springframework.boot.autoconfigure: WARN
```

Use `@ComponentScan` with specific packages instead of scanning everything:

```java
@SpringBootApplication(scanBasePackages = "com.myapp")
@EnableAutoConfiguration(exclude = {
    DataSourceAutoConfiguration.class,  // If not using JDBC
    SecurityAutoConfiguration.class     // If not using security
})
public class MyApp { }
```

Measure startup:

```java
@SpringBootApplication
public class MyApp {
    public static void main(String[] args) {
        var app = new SpringApplication(MyApp.class);
        app.setApplicationStartup(new BufferingApplicationStartup(2048));
        app.run(args);
    }
}
// Then check /actuator/startup for timing breakdown
```

## Virtual Threads for I/O-Bound Services

If your service calls databases, APIs, or queues — virtual threads are a massive win:

```yaml
# application.yml — Spring Boot 3.2+
spring:
  threads:
    virtual:
      enabled: true
```

Before: 200 platform threads, each blocking on I/O = 200 concurrent requests max.
After: millions of virtual threads, each blocking cheaply = thousands of concurrent requests.

```java
// Custom executor for background tasks
@Bean
public TaskExecutor applicationTaskExecutor() {
    return new TaskExecutorAdapter(Executors.newVirtualThreadPerTaskExecutor());
}
```

When NOT to use virtual threads: CPU-bound work (image processing, encryption). Platform threads are better for compute-heavy tasks.

## Response Compression

```yaml
# application.yml
server:
  compression:
    enabled: true
    min-response-size: 1024        # Only compress responses > 1KB
    mime-types:
      - application/json
      - application/xml
      - text/html
      - text/plain
```

Typical JSON API responses compress 60-80%. A 50KB response becomes 10KB over the wire.

## Spring AOT & Native Image

For serverless or fast-startup requirements:

```xml
<!-- pom.xml -->
<plugin>
    <groupId>org.graalvm.buildtools</groupId>
    <artifactId>native-maven-plugin</artifactId>
</plugin>
```

```bash
# Build native image (requires GraalVM)
./mvnw -Pnative native:compile

# Result: ~50ms startup instead of ~3s
```

AOT processing (ahead-of-time) without full native:

```bash
# Generate AOT-optimized classes for faster JVM startup
./mvnw spring-boot:process-aot
java -Dspring.aot.enabled=true -jar app.jar
```

Tradeoffs: no runtime reflection tricks, longer build time, larger binary.

## Connection Pooling for HTTP Clients

```java
@Configuration
public class HttpClientConfig {

    @Bean
    public RestClient restClient() {
        return RestClient.builder()
            .baseUrl("https://api.external.com")
            .requestFactory(clientHttpRequestFactory())
            .build();
    }

    private ClientHttpRequestFactory clientHttpRequestFactory() {
        var factory = new JdkClientHttpRequestFactory();
        factory.setReadTimeout(Duration.ofSeconds(5));
        return factory;
    }
}
```

## Quick Wins Checklist

| Optimization | Impact | Effort |
|---|---|---|
| Enable response compression | 60-80% smaller responses | 3 lines of YAML |
| Virtual threads | 5-10x concurrent capacity | 2 lines of YAML |
| Tune HikariCP pool size | Prevent pool exhaustion | 5 lines of YAML |
| Lazy init for heavy beans | 1-3s faster startup | `@Lazy` annotation |
| Exclude unused auto-config | 0.5-2s faster startup | One annotation |
| Native image | 50ms startup | Build pipeline change |
| Index database queries | 10-100x query speed | Schema migration |

## What You Learned

- **HikariCP** — pool size formula, leak detection, fail-fast timeout
- **Lazy init** — `@Lazy` or global flag for faster startup
- **Startup optimization** — exclude auto-config, disable JMX, measure with `/actuator/startup`
- **Virtual threads** — one property for massive I/O concurrency (Spring Boot 3.2+)
- **Compression** — 60-80% smaller JSON responses with 3 lines of config
- **Native image** — 50ms startup with GraalVM AOT compilation
- **HTTP client pooling** — reuse connections to external services

---

[← Chapter 9: Security](chapter-09-security.md) | [README →](README.md)

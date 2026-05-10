# Chapter 1: Available Beans — What's in Your Context?

[← Chapter 0: Events](chapter-00-events.md) | [Chapter 2: Profiles →](chapter-02-profiles.md)

---

## The Problem

"I injected `DataSource` but which one did I get? Is my custom `ObjectMapper` actually being used? Why is Spring creating a bean I didn't ask for?"

Spring Boot auto-configures hundreds of beans. Knowing what's in your context — and how to inspect, override, or disable them — is essential.

## List All Beans at Startup

```java
@SpringBootApplication
public class MyApp {
    public static void main(String[] args) {
        var ctx = SpringApplication.run(MyApp.class, args);

        // Print all bean names
        String[] beanNames = ctx.getBeanDefinitionNames();
        Arrays.sort(beanNames);
        System.out.println("=== Beans (" + beanNames.length + ") ===");
        for (String name : beanNames) {
            System.out.println("  " + name + " → " + ctx.getBean(name).getClass().getSimpleName());
        }
    }
}
```

Typical Spring Boot app: 200-400 beans. Most are auto-configured.

## Filter Beans by Type

```java
@Component
@RequiredArgsConstructor
public class BeanInspector implements CommandLineRunner {
    private final ApplicationContext ctx;

    @Override
    public void run(String... args) {
        // Find all beans of a specific type
        Map<String, DataSource> dataSources = ctx.getBeansOfType(DataSource.class);
        System.out.println("DataSources: " + dataSources.keySet());

        // Find all beans with a specific annotation
        Map<String, Object> restControllers = ctx.getBeansWithAnnotation(RestController.class);
        System.out.println("Controllers: " + restControllers.keySet());

        // Check if a bean exists
        boolean hasRedis = ctx.containsBean("redisTemplate");
        System.out.println("Redis configured: " + hasRedis);
    }
}
```

## Actuator: /beans Endpoint

The easiest way in a running app:

```yaml
# application.yml
management:
  endpoints:
    web:
      exposure:
        include: beans, conditions, env, health, info
```

```bash
# List all beans (JSON)
curl http://localhost:8080/actuator/beans | jq '.contexts[].beans | keys[]'

# Why was a bean created (or not)?
curl http://localhost:8080/actuator/conditions | jq '.contexts[].positiveMatches'
```

The `/actuator/conditions` endpoint is gold — it tells you exactly WHY each auto-configuration was applied or skipped.

## Key Auto-Configured Beans You Get for Free

| Bean | Auto-configured when | What it does |
|---|---|---|
| `DataSource` | `spring-boot-starter-jdbc` on classpath | Database connection pool (HikariCP) |
| `JdbcTemplate` | DataSource exists | Simple SQL queries |
| `ObjectMapper` | Jackson on classpath | JSON serialization |
| `RestTemplate` / `WebClient` | Manual (not auto) | HTTP client |
| `TaskExecutor` | Always | Thread pool for @Async |
| `CacheManager` | `spring-boot-starter-cache` | Caching infrastructure |
| `PasswordEncoder` | Spring Security | BCrypt by default |
| `MeterRegistry` | Micrometer on classpath | Metrics collection |
| `HealthIndicator` (multiple) | Various starters | Health checks |

## Overriding Auto-Configured Beans

Spring Boot backs off when you define your own:

```java
@Configuration
public class JacksonConfig {

    // This REPLACES the auto-configured ObjectMapper
    @Bean
    @Primary
    public ObjectMapper objectMapper() {
        return new ObjectMapper()
            .registerModule(new JavaTimeModule())
            .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS)
            .setSerializationInclusion(JsonInclude.Include.NON_NULL);
    }
}
```

Spring sees your `ObjectMapper` bean and skips its own auto-configuration. This is the `@ConditionalOnMissingBean` pattern.

## @ConditionalOn* — When Beans Are Created

Spring Boot uses conditions to decide what to auto-configure:

```java
// Only create this bean if a class is on the classpath
@ConditionalOnClass(RedisTemplate.class)
@Bean
public CacheManager redisCacheManager() { ... }

// Only create if NO bean of this type exists already
@ConditionalOnMissingBean(CacheManager.class)
@Bean
public CacheManager defaultCacheManager() { ... }

// Only create if a property is set
@ConditionalOnProperty(name = "app.feature.notifications", havingValue = "true")
@Bean
public NotificationService notificationService() { ... }

// Only create in specific profiles
@Profile("production")
@Bean
public DataSource productionDataSource() { ... }
```

## Useful Beans You Might Not Know About

### Environment — Access All Properties

```java
@Autowired
private Environment env;

String dbUrl = env.getProperty("spring.datasource.url");
int port = env.getProperty("server.port", Integer.class, 8080);
boolean isProd = env.acceptsProfiles(Profiles.of("production"));
```

### ApplicationContext — The Container Itself

```java
@Autowired
private ApplicationContext ctx;

// Dynamic bean lookup (avoid if possible — prefer injection)
MyService service = ctx.getBean(MyService.class);

// Get active profiles
String[] profiles = ctx.getEnvironment().getActiveProfiles();
```

### ResourceLoader — Load Files

```java
@Autowired
private ResourceLoader resourceLoader;

Resource resource = resourceLoader.getResource("classpath:templates/email.html");
String content = new String(resource.getInputStream().readAllBytes());
```

### ConversionService — Type Conversion

```java
@Autowired
private ConversionService conversionService;

// Convert between types (String → Integer, String → Enum, etc.)
Integer port = conversionService.convert("8080", Integer.class);
```

## Bean Ordering

Control the order beans are initialized:

```java
// @Order — lower number = higher priority
@Component
@Order(1)
public class FirstFilter implements Filter { ... }

@Component
@Order(2)
public class SecondFilter implements Filter { ... }

// @DependsOn — explicit dependency
@Bean
@DependsOn("dataSource")
public JdbcTemplate jdbcTemplate() { ... }

// SmartInitializingSingleton — runs after ALL beans are created
@Component
public class PostInitSetup implements SmartInitializingSingleton {
    @Override
    public void afterSingletonsInstantiated() {
        // All beans exist now — safe to do cross-bean setup
    }
}
```

## Bean Scopes

```java
@Scope("singleton")   // Default — one instance for the entire app
@Scope("prototype")   // New instance every time it's injected
@Scope("request")     // One per HTTP request (web only)
@Scope("session")     // One per HTTP session (web only)

// Prototype example: each injection gets a fresh instance
@Bean
@Scope("prototype")
public ReportGenerator reportGenerator() {
    return new ReportGenerator();  // New instance each time
}
```

## Debugging Bean Issues

```yaml
# Show auto-configuration report at startup
logging:
  level:
    org.springframework.boot.autoconfigure: DEBUG

# Or use the --debug flag
# java -jar app.jar --debug
```

This prints:
```
============================
CONDITIONS EVALUATION REPORT
============================

Positive matches:
-----------------
   DataSourceAutoConfiguration matched:
      - @ConditionalOnClass found required classes 'javax.sql.DataSource', 'org.springframework.jdbc.datasource.embedded.EmbeddedDatabaseType'

Negative matches:
-----------------
   RedisAutoConfiguration:
      Did not match:
         - @ConditionalOnClass did not find required class 'org.springframework.data.redis.core.RedisOperations'
```

## Quick Reference: Finding What You Need

| I want to... | Look for... |
|---|---|
| See all beans | `/actuator/beans` or `ctx.getBeanDefinitionNames()` |
| See why a bean was/wasn't created | `/actuator/conditions` or `--debug` flag |
| Override an auto-configured bean | Define your own `@Bean` of the same type |
| Disable auto-configuration | `@SpringBootApplication(exclude = {DataSourceAutoConfiguration.class})` |
| Check if a bean exists | `ctx.containsBean("name")` or `ctx.getBeansOfType(Type.class)` |
| See all properties | `/actuator/env` |

## What You Learned

- **List beans** — `ctx.getBeanDefinitionNames()` or `/actuator/beans`
- **Filter by type** — `ctx.getBeansOfType(DataSource.class)`
- **Conditions report** — `--debug` flag or `/actuator/conditions`
- **Override** — define your own `@Bean` and Spring backs off
- **@ConditionalOn*** — control when beans are created
- **Useful built-ins** — Environment, ResourceLoader, ConversionService
- **Bean ordering** — @Order, @DependsOn, SmartInitializingSingleton
- **Scopes** — singleton (default), prototype, request, session

---

[← Chapter 0: Events](chapter-00-events.md) | [Chapter 2: Profiles →](chapter-02-profiles.md)

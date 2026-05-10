# Chapter 2: Profiles & Configuration — Dev vs Prod Without the Pain

[← Chapter 1: Beans](chapter-01-beans.md) | [Chapter 3: Annotations →](chapter-03-annotations.md)

---

## The Problem

"I hardcoded the database URL and pushed to prod. Now I need different configs per environment, feature flags that don't require redeployment, and beans that only exist in certain contexts."

## Profile-Specific YAML Files

Spring Boot automatically loads `application-{profile}.yml`:

```yaml
# application.yml (always loaded — shared defaults)
spring:
  application:
    name: my-service
server:
  port: 8080

# application-dev.yml (loaded when "dev" profile is active)
spring:
  datasource:
    url: jdbc:h2:mem:devdb
    driver-class-name: org.h2.Driver
  jpa:
    show-sql: true
    hibernate:
      ddl-auto: create-drop

# application-prod.yml (loaded when "prod" profile is active)
spring:
  datasource:
    url: jdbc:postgresql://${DB_HOST}:5432/myapp
    username: ${DB_USER}
    password: ${DB_PASS}
  jpa:
    show-sql: false
    hibernate:
      ddl-auto: validate
```

## Activating Profiles

```bash
# CLI argument
java -jar app.jar --spring.profiles.active=prod

# Environment variable (most common in containers)
SPRING_PROFILES_ACTIVE=prod java -jar app.jar

# In application.yml (default profile)
spring:
  profiles:
    active: dev

# Multiple profiles
SPRING_PROFILES_ACTIVE=prod,metrics,verbose
```

Programmatic activation:

```java
public static void main(String[] args) {
    var app = new SpringApplication(MyApp.class);
    app.setAdditionalProfiles("metrics");  // Always add "metrics"
    app.run(args);
}
```

## @Profile — Beans That Only Exist in Certain Environments

```java
@Configuration
public class DataSourceConfig {

    @Bean
    @Profile("dev")
    public DataSource devDataSource() {
        // Embedded H2 — no external DB needed
        return new EmbeddedDatabaseBuilder()
            .setType(EmbeddedDatabaseType.H2)
            .addScript("schema.sql")
            .build();
    }

    @Bean
    @Profile("prod")
    public DataSource prodDataSource(
            @Value("${spring.datasource.url}") String url,
            @Value("${spring.datasource.username}") String user,
            @Value("${spring.datasource.password}") String pass) {
        var ds = new HikariDataSource();
        ds.setJdbcUrl(url);
        ds.setUsername(user);
        ds.setPassword(pass);
        ds.setMaximumPoolSize(20);
        return ds;
    }
}
```

## @ConditionalOnProperty — Feature Flags

```yaml
# application.yml
app:
  features:
    email-notifications: true
    experimental-search: false
    rate-limiting: ${RATE_LIMIT_ENABLED:true}
```

```java
@Configuration
public class FeatureConfig {

    @Bean
    @ConditionalOnProperty(name = "app.features.email-notifications", havingValue = "true")
    public EmailNotificationService emailService() {
        return new EmailNotificationService();
    }

    @Bean
    @ConditionalOnProperty(name = "app.features.experimental-search", havingValue = "true")
    public ExperimentalSearchEngine searchEngine() {
        return new ExperimentalSearchEngine();
    }

    // matchIfMissing = true → bean created unless explicitly disabled
    @Bean
    @ConditionalOnProperty(name = "app.features.rate-limiting", matchIfMissing = true)
    public RateLimitFilter rateLimitFilter() {
        return new RateLimitFilter();
    }
}
```

## Type-Safe Configuration with @ConfigurationProperties

```java
@ConfigurationProperties(prefix = "app.features")
public record FeatureFlags(
    boolean emailNotifications,
    boolean experimentalSearch,
    boolean rateLimiting
) {}

@SpringBootApplication
@EnableConfigurationProperties(FeatureFlags.class)
public class MyApp { }

// Usage — inject anywhere
@Service
@RequiredArgsConstructor
public class SearchService {
    private final FeatureFlags features;

    public List<Result> search(String query) {
        if (features.experimentalSearch()) {
            return experimentalSearch(query);
        }
        return standardSearch(query);
    }
}
```

## Profile Groups — Combine Profiles

```yaml
# application.yml
spring:
  profiles:
    group:
      production: prod,metrics,ssl
      local: dev,mock-services
```

Now `SPRING_PROFILES_ACTIVE=production` activates `prod`, `metrics`, and `ssl` together.

## Testing with Profiles

```java
@SpringBootTest
@ActiveProfiles("test")  // Uses application-test.yml
class OrderServiceTest {
    // Test-specific beans and config loaded
}
```

## What You Learned

- **Profile YAML** — `application-{profile}.yml` auto-loads per environment
- **Activation** — env var, CLI, or programmatic
- **@Profile** — beans that only exist in certain environments
- **@ConditionalOnProperty** — feature flags without redeployment
- **@ConfigurationProperties** — type-safe config with records
- **Profile groups** — combine multiple profiles under one name
- **matchIfMissing** — default-on features that can be disabled

---

[← Chapter 1: Beans](chapter-01-beans.md) | [Chapter 3: Annotations →](chapter-03-annotations.md)

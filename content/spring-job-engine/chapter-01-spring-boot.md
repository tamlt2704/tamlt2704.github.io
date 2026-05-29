# Chapter 1: Spring Boot Foundation

[← Overview](/blog/spring-job-engine/chapter-00-overview) | [Chapter 2: The Job Model →](/blog/spring-job-engine/chapter-02-job-model)

---

## The Story

Day one. You open IntelliJ, create a new project. The goal: a running Spring Boot app with the right dependencies wired up. Nothing fancy yet — just the skeleton that everything else will hang on.

## Step 1: Initialize the Project

```kotlin
// build.gradle.kts
plugins {
    java
    id("org.springframework.boot") version "3.3.0"
    id("io.spring.dependency-management") version "1.1.5"
}

group = "com.company"
version = "0.0.1-SNAPSHOT"

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}

repositories {
    mavenCentral()
}

dependencies {
    // Web
    implementation("org.springframework.boot:spring-boot-starter-web")

    // Spring Integration
    implementation("org.springframework.integration:spring-integration-core")

    // JPA + PostgreSQL
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    runtimeOnly("org.postgresql:postgresql")

    // Security
    implementation("org.springframework.boot:spring-boot-starter-security")

    // Redis
    implementation("org.springframework.boot:spring-boot-starter-data-redis")

    // Kafka
    implementation("org.springframework.kafka:spring-kafka")

    // JWT
    implementation("io.jsonwebtoken:jjwt-api:0.12.5")
    runtimeOnly("io.jsonwebtoken:jjwt-impl:0.12.5")
    runtimeOnly("io.jsonwebtoken:jjwt-jackson:0.12.5")

    // WebSocket (for frontend real-time updates)
    implementation("org.springframework.boot:spring-boot-starter-websocket")

    // Lombok
    compileOnly("org.projectlombok:lombok")
    annotationProcessor("org.projectlombok:lombok")

    // Test
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("org.springframework.kafka:spring-kafka-test")
}
```

```bash
# Initialize with Spring Initializr or manually
mkdir job-engine && cd job-engine
gradle init --type java-application
# Then replace build.gradle.kts with the above
```

## Step 2: Docker Compose for Infrastructure

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: jobengine
      POSTGRES_USER: app
      POSTGRES_PASSWORD: secret
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  kafka:
    image: confluentinc/cp-kafka:7.6.0
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@localhost:9093
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      CLUSTER_ID: "MkU3OEVBNTcwNTJENDM2Qk"
    ports:
      - "9092:9092"
```

```bash
docker compose up -d
```

## Step 3: Application Configuration

```yaml
# application.yml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/jobengine
    username: app
    password: secret
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: false
  data:
    redis:
      host: localhost
      port: 6379
  kafka:
    bootstrap-servers: localhost:9092
    consumer:
      group-id: job-engine
      auto-offset-reset: earliest
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer

server:
  port: 8080

job-engine:
  thread-pool:
    core-size: 4
    max-size: 16
    queue-capacity: 100
```

## Step 4: The Main Class

```java
// JobEngineApplication.java
@SpringBootApplication
@EnableIntegration
public class JobEngineApplication {
    public static void main(String[] args) {
        SpringApplication.run(JobEngineApplication.class, args);
    }
}
```

`@EnableIntegration` activates Spring Integration — the backbone of our job flow.

## Step 5: Security Config (Permit Health Endpoint)

Since we added `spring-boot-starter-security`, **all endpoints are locked down by default**. Without configuration, `curl http://localhost:8080/api/health` returns `401 Unauthorized`.

We need to explicitly permit the health endpoint:

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/health").permitAll()
                .anyRequest().authenticated()
            );
        return http.build();
    }
}
```

> **Why does this happen?** Spring Security's default behavior is to require authentication for every request. This is secure-by-default — you opt endpoints _out_ of security rather than opting them _in_.

> **Note:** This is a starter SecurityConfig. It gets replaced with a full JWT-based version in [Chapter 6](/blog/spring-job-engine/chapter-06-security).

## Step 6: Health Check

```java
@RestController
@RequestMapping("/api")
public class HealthController {

    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of("status", "UP", "engine", "ready");
    }
}
```

```bash
curl http://localhost:8080/api/health
# {"status":"UP","engine":"ready"}
```

## Project Structure

```
src/main/java/com/company/jobengine/
├── JobEngineApplication.java
├── config/
│   ├── SecurityConfig.java
│   ├── RedisConfig.java
│   ├── KafkaConfig.java
│   └── ThreadPoolConfig.java
├── model/
│   ├── Job.java
│   ├── JobStatus.java
│   └── AuditLog.java
├── repository/
│   ├── JobRepository.java
│   └── AuditRepository.java
├── service/
│   ├── JobService.java
│   ├── JobExecutor.java
│   └── AuditService.java
├── integration/
│   └── JobIntegrationFlow.java
├── controller/
│   ├── JobController.java
│   └── AuthController.java
└── security/
    ├── JwtTokenProvider.java
    └── JwtAuthFilter.java
```

## What We Have

- Spring Boot 3 project with all dependencies
- Docker Compose for PostgreSQL, Redis, Kafka
- Configuration for all services
- Health endpoint proving it runs

## Next

We'll define what a "Job" actually is — the entity, its states, and how it moves through the system.

[Chapter 2: The Job Model →](/blog/spring-job-engine/chapter-02-job-model)

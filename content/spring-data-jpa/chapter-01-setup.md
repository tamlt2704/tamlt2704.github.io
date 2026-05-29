# Chapter 1: Project Setup

[Overview](chapter-00-overview.md) | [next: Entities](chapter-02-entities.md)

## Gradle Dependencies

```kotlin
// build.gradle.kts
plugins {
    java
    id("org.springframework.boot") version "3.2.5"
    id("io.spring.dependency-management") version "1.1.4"
}

group = "com.example"
version = "0.0.1-SNAPSHOT"

java {
    sourceCompatibility = JavaVersion.VERSION_17
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("org.springframework.boot:spring-boot-starter-web")
    runtimeOnly("org.postgresql:postgresql")

    // Flyway for migrations
    implementation("org.flywaydb:flyway-core")
    implementation("org.flywaydb:flyway-database-postgresql")

    // Lombok
    compileOnly("org.projectlombok:lombok")
    annotationProcessor("org.projectlombok:lombok")

    // Testing
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testRuntimeOnly("com.h2database:h2")
}

tasks.withType<Test> {
    useJUnitPlatform()
}
```

## Application Configuration (PostgreSQL)

```yaml
# src/main/resources/application.yml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/mydb
    username: postgres
    password: postgres
    driver-class-name: org.postgresql.Driver
  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: true
    properties:
      hibernate:
        format_sql: true
        dialect: org.hibernate.dialect.PostgreSQLDialect
  flyway:
    enabled: true
    locations: classpath:db/migration
```

## Hibernate ddl-auto Modes

| Mode          | Behavior                            | Use Case                 |
| ------------- | ----------------------------------- | ------------------------ |
| `none`        | Does nothing                        | Production with Flyway   |
| `validate`    | Validates schema matches entities   | Production (recommended) |
| `update`      | Updates schema, never drops         | Development (risky)      |
| `create`      | Drops and recreates on startup      | Testing only             |
| `create-drop` | Creates on start, drops on shutdown | Unit tests               |

**Rule of thumb**: Use `validate` or `none` in production. Use `create-drop` in tests. Never use `update` in production — it cannot drop columns or rename things safely.

## H2 for Testing

```yaml
# src/test/resources/application-test.yml
spring:
  datasource:
    url: jdbc:h2:mem:testdb;DB_CLOSE_DELAY=-1
    driver-class-name: org.h2.Driver
    username: sa
    password:
  jpa:
    hibernate:
      ddl-auto: create-drop
    database-platform: org.hibernate.dialect.H2Dialect
  flyway:
    enabled: false
```

```java
@DataJpaTest
@ActiveProfiles("test")
class UserRepositoryTest {
    @Autowired
    private UserRepository userRepository;

    @Test
    void shouldSaveAndFind() {
        User user = new User();
        user.setName("Alice");
        User saved = userRepository.save(user);

        assertThat(userRepository.findById(saved.getId())).isPresent();
    }
}
```

## Flyway Introduction

Flyway manages database schema changes through versioned SQL scripts.

```
src/main/resources/db/migration/
├── V1__create_users_table.sql
├── V2__add_email_to_users.sql
└── V3__create_orders_table.sql
```

```sql
-- V1__create_users_table.sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

```sql
-- V2__add_email_to_users.sql
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
CREATE INDEX idx_users_email ON users(email);
```

Naming convention: `V{version}__{description}.sql` (two underscores).

Flyway tracks applied migrations in a `flyway_schema_history` table. Once applied, never modify a migration file — create a new one instead.

## Exercises

1. Create a new Spring Boot project with the dependencies above
2. Configure PostgreSQL connection (or use Docker: `docker run -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:16`)
3. Write a Flyway migration that creates a `products` table with columns: id, name, price, created_at
4. Verify the application starts and Flyway applies the migration
5. Switch to H2 for tests and confirm `@DataJpaTest` works with `create-drop`

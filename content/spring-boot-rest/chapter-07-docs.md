---
title: "Chapter 7 - Documentation and Deployment"
date: 2026-05-29
series: "Spring Boot REST API"
chapter: 7
---

# Chapter 7: Documentation and Deployment

[Previous: Testing](../chapter-06-testing) | [Back to Overview](../chapter-00-overview)

---

## Overview

We add OpenAPI documentation with springdoc, implement HATEOAS links, version the API, containerize with Docker, and configure health checks with Actuator.

## OpenAPI with springdoc

### Dependency

```kotlin
// build.gradle.kts
implementation("org.springdoc:springdoc-openapi-starter-webmvc-ui:2.5.0")
```

### Configuration

```java
package com.example.bookstore.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.security.SecurityRequirement;
import io.swagger.v3.oas.models.security.SecurityScheme;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI bookstoreOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("Bookstore API")
                        .version("1.0")
                        .description("REST API for managing books"))
                .addSecurityItem(new SecurityRequirement().addList("Bearer"))
                .schemaRequirement("Bearer", new SecurityScheme()
                        .type(SecurityScheme.Type.HTTP)
                        .scheme("bearer")
                        .bearerFormat("JWT"));
    }
}
```

### Annotating Endpoints

```java
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;

@Tag(name = "Books", description = "Book management endpoints")
@RestController
@RequestMapping("/api/books")
public class BookController {

    @Operation(summary = "Get all books", description = "Returns paginated list of books")
    @ApiResponse(responseCode = "200", description = "Successful retrieval")
    @GetMapping
    public ResponseEntity<Page<BookResponse>> getAllBooks(Pageable pageable) {
        return ResponseEntity.ok(bookService.findAll(pageable));
    }
}
```

Access Swagger UI at: `http://localhost:8080/swagger-ui.html`

## HATEOAS

```kotlin
// build.gradle.kts
implementation("org.springframework.boot:spring-boot-starter-hateoas")
```

```java
import org.springframework.hateoas.EntityModel;
import static org.springframework.hateoas.server.mvc.WebMvcLinkBuilder.*;

@GetMapping("/{id}")
public ResponseEntity<EntityModel<BookResponse>> getBook(@PathVariable Long id) {
    BookResponse book = bookService.findById(id);
    EntityModel<BookResponse> model = EntityModel.of(book,
            linkTo(methodOn(BookController.class).getBook(id)).withSelfRel(),
            linkTo(methodOn(BookController.class).getAllBooks(null)).withRel("books")
    );
    return ResponseEntity.ok(model);
}
```

## API Versioning

URL-based versioning (simplest approach):

```java
@RestController
@RequestMapping("/api/v1/books")
public class BookControllerV1 { }

@RestController
@RequestMapping("/api/v2/books")
public class BookControllerV2 { }
```

## Spring Boot Actuator

```kotlin
// build.gradle.kts
implementation("org.springframework.boot:spring-boot-starter-actuator")
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
  info:
    env:
      enabled: true
```

Health endpoint: `http://localhost:8080/actuator/health`

## Dockerfile

```dockerfile
FROM eclipse-temurin:21-jre-alpine AS runtime

WORKDIR /app
COPY build/libs/bookstore-0.0.1-SNAPSHOT.jar app.jar

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
  CMD wget -qO- http://localhost:8080/actuator/health || exit 1

ENTRYPOINT ["java", "-jar", "app.jar"]
```

## Multi-stage Build

```dockerfile
FROM eclipse-temurin:21-jdk-alpine AS build
WORKDIR /workspace
COPY . .
RUN ./gradlew bootJar --no-daemon

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=build /workspace/build/libs/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

## Docker Compose

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: bookstore
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      SPRING_DATASOURCE_URL: jdbc:postgresql://db:5432/bookstore
      SPRING_DATASOURCE_USERNAME: postgres
      SPRING_DATASOURCE_PASSWORD: postgres
    depends_on:
      - db

volumes:
  pgdata:
```

## Build and Run

```bash
# Build the JAR
./gradlew bootJar

# Build and start with Docker Compose
docker compose up --build
```

## Summary

The complete Bookstore API now includes:

- RESTful CRUD with proper HTTP semantics
- Input validation with structured error responses
- PostgreSQL with Flyway migrations
- JWT authentication and role-based authorization
- Comprehensive test coverage
- OpenAPI documentation
- Docker deployment with health checks

---

[Previous: Testing](../chapter-06-testing) | [Back to Overview](../chapter-00-overview)

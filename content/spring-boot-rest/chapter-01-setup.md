---
title: "Chapter 1 - Project Setup"
date: 2026-05-29
series: "Spring Boot REST API"
chapter: 1
---

# Chapter 1: Project Setup

[Previous: Overview](../chapter-00-overview) | [Next: CRUD Operations](../chapter-02-crud)

---

## Spring Initializr

Generate a project at [start.spring.io](https://start.spring.io) with:

- **Project:** Gradle (Kotlin DSL)
- **Language:** Java
- **Spring Boot:** 3.3.x
- **Java:** 21
- **Dependencies:** Spring Web, Spring Data JPA, PostgreSQL Driver, Flyway Migration, Validation, Spring Security

## Gradle Build File

```kotlin
// build.gradle.kts
plugins {
    java
    id("org.springframework.boot") version "3.3.0"
    id("io.spring.dependency-management") version "1.1.5"
}

group = "com.example"
version = "0.0.1-SNAPSHOT"

java {
    sourceCompatibility = JavaVersion.VERSION_21
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("org.springframework.boot:spring-boot-starter-validation")
    implementation("org.springframework.boot:spring-boot-starter-security")
    implementation("org.flywaydb:flyway-core")
    implementation("org.flywaydb:flyway-database-postgresql")
    runtimeOnly("org.postgresql:postgresql")

    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("org.springframework.security:spring-security-test")
}

tasks.withType<Test> {
    useJUnitPlatform()
}
```

## Project Structure

```
src/
├── main/
│   ├── java/com/example/bookstore/
│   │   ├── BookstoreApplication.java
│   │   ├── controller/
│   │   ├── service/
│   │   ├── repository/
│   │   ├── model/
│   │   ├── dto/
│   │   ├── exception/
│   │   └── config/
│   └── resources/
│       ├── application.yml
│       └── db/migration/
└── test/
    └── java/com/example/bookstore/
```

## Application Entry Point

```java
package com.example.bookstore;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class BookstoreApplication {
    public static void main(String[] args) {
        SpringApplication.run(BookstoreApplication.class, args);
    }
}
```

## application.yml

```yaml
spring:
  application:
    name: bookstore-api
  datasource:
    url: jdbc:postgresql://localhost:5432/bookstore
    username: postgres
    password: postgres
  jpa:
    hibernate:
      ddl-auto: validate
    open-in-view: false
  flyway:
    enabled: true

server:
  port: 8080
```

## First Endpoint

```java
package com.example.bookstore.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api")
public class HealthController {

    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of("status", "UP"));
    }
}
```

## Running the Application

```bash
./gradlew bootRun
```

Test the endpoint:

```bash
curl http://localhost:8080/api/health
```

Response:

```json
{ "status": "UP" }
```

---

[Previous: Overview](../chapter-00-overview) | [Next: CRUD Operations](../chapter-02-crud)

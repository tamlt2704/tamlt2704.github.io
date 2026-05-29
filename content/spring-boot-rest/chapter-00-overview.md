---
title: "Spring Boot REST API - Overview"
date: 2026-05-29
series: "Spring Boot REST API"
chapter: 0
---

# Building Production REST APIs with Spring Boot

This series walks through building a production-ready REST API using Spring Boot 3.x and Java 21. We build a **Bookstore API** from scratch — starting with project setup and ending with Docker deployment.

## What You Will Build

A fully functional Bookstore REST API with:

- CRUD operations for books and authors
- Input validation and structured error responses
- PostgreSQL persistence with migrations
- JWT-based authentication and authorization
- Comprehensive test coverage
- OpenAPI documentation and Docker deployment

## Chapters

1. [Project Setup](../chapter-01-setup) — Spring Initializr, Gradle, project structure, first endpoint
2. [CRUD Operations](../chapter-02-crud) — Controllers, request/response mapping, DTOs
3. [Validation and Error Handling](../chapter-03-validation) — Bean Validation, global exception handling, RFC 7807
4. [Database](../chapter-04-database) — Spring Data JPA, repositories, pagination, Flyway
5. [Security](../chapter-05-security) — Spring Security, JWT, authorization, CORS
6. [Testing](../chapter-06-testing) — Unit tests, integration tests, Testcontainers
7. [Documentation and Deployment](../chapter-07-docs) — OpenAPI, Docker, Actuator, health checks

## Prerequisites

- Java 21+
- Gradle 8.x
- Docker (for database and deployment chapters)
- An IDE (IntelliJ IDEA recommended)

## Tech Stack

| Component  | Technology              |
| ---------- | ----------------------- |
| Framework  | Spring Boot 3.3         |
| Language   | Java 21                 |
| Build      | Gradle (Kotlin DSL)     |
| Database   | PostgreSQL              |
| Migrations | Flyway                  |
| Security   | Spring Security + JWT   |
| Docs       | springdoc-openapi       |
| Testing    | JUnit 5, Testcontainers |

---

Next: [Chapter 1 — Project Setup](../chapter-01-setup)

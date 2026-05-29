# Spring Data JPA: From Basics to Production

A comprehensive guide to Spring Data JPA with Spring Boot 3, covering entity mapping, repositories, performance optimization, and production-ready patterns.

## Chapters

1. [Setup](chapter-01-setup.md) — Gradle dependencies, PostgreSQL configuration, Hibernate ddl-auto, H2 testing, Flyway
2. [Entities](chapter-02-entities.md) — @Entity, @Id, generation strategies, column mapping, timestamps, Lombok
3. [Repositories](chapter-03-repositories.md) — JpaRepository, derived queries, @Query, pagination, sorting
4. [Relationships](chapter-04-relationships.md) — OneToOne, OneToMany, ManyToMany, cascade, fetch types
5. [N+1 Problem](chapter-05-n-plus-one.md) — Detection, JOIN FETCH, @EntityGraph, @BatchSize, DTO projections
6. [Transactions](chapter-06-transactions.md) — @Transactional, propagation, isolation, optimistic/pessimistic locking
7. [Specifications](chapter-07-specifications.md) — Dynamic queries, Criteria API, QueryDSL, reusable filters
8. [Auditing](chapter-08-auditing.md) — @CreatedBy, @LastModifiedDate, AuditorAware, Envers history
9. [Performance](chapter-09-performance.md) — Batch inserts, second-level cache, read replicas, HikariCP
10. [Production Patterns](chapter-10-patterns.md) — Soft delete, multi-tenancy, custom repositories, Testcontainers

## Prerequisites

- Java 17+
- Spring Boot 3.x
- Gradle (Kotlin DSL)
- PostgreSQL (or H2 for testing)

## Project Structure

```
src/
├── main/
│   ├── java/com/example/demo/
│   │   ├── entity/
│   │   ├── repository/
│   │   ├── service/
│   │   └── config/
│   └── resources/
│       ├── application.yml
│       └── db/migration/
└── test/
    └── java/com/example/demo/
```

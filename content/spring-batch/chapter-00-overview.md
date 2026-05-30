# Spring Batch: From Zero to Production

A comprehensive guide to Spring Batch 5 with Spring Boot 3.3 — from core concepts to building a full batch processing platform. Covers real-world use cases: data migration, ETL pipelines, file processing, API integration, reporting, event-driven batch, and platform engineering.

## Part 1: Fundamentals

1. [Core Concepts](chapter-01-concepts.md) — Job, Step, Readers, Processors, Writers, chunk-oriented processing
2. [Project Setup](chapter-02-setup.md) — Gradle dependencies, auto-configuration, first job
3. [ItemReaders](chapter-03-readers.md) — CSV, JDBC, JPA, JSON, custom readers
4. [ItemProcessors](chapter-04-processors.md) — Transformation, filtering, validation, chaining
5. [ItemWriters](chapter-05-writers.md) — CSV, JDBC, JPA, JSON, composite writers
6. [Job Flow Control](chapter-06-flow.md) — Conditional flow, parallel steps, deciders, listeners
7. [Error Handling](chapter-07-error-handling.md) — Skip, retry, restart, fault tolerance
8. [Scaling](chapter-08-scaling.md) — Multi-threaded steps, partitioning, remote chunking
9. [Production](chapter-09-production.md) — Scheduling, monitoring, testing, Docker deployment

## Part 2: Real-World Use Cases

10. [Data Migration](chapter-10-data-migration.md) — Cross-database migration, schema transformation, validation, rollback
11. [ETL Pipelines](chapter-11-etl-pipelines.md) — Multi-source extract, data warehouse loading, SCD, data quality
12. [File Processing](chapter-12-file-processing.md) — Multi-file, fixed-width, XML, Excel, S3, archival patterns
13. [API Integration](chapter-13-api-integration.md) — Paginated readers, rate limiting, retry, circuit breakers, webhooks
14. [Reporting & Aggregation](chapter-14-reporting.md) — Aggregation patterns, PDF/CSV/Excel generation, scheduled reports
15. [Event-Driven Batch](chapter-15-event-driven.md) — Kafka triggers, S3 events, micro-batching, job chaining, DLQ
16. [Testing Strategies](chapter-16-testing.md) — Unit tests, integration tests, Testcontainers, performance testing
17. [Building a Batch Platform](chapter-17-batch-platform.md) — Job registry, dynamic scheduling, monitoring, multi-tenancy, ops API

## Prerequisites

- Java 17+
- Gradle 8+
- Familiarity with Spring Boot basics
- A relational database (H2 for dev, PostgreSQL for production)

## What You Will Build

By the end of this guide you will be able to:

- Design batch jobs that process millions of records efficiently
- Handle errors gracefully with skip, retry, and restart policies
- Scale jobs across threads and partitions
- Migrate data between systems with validation and rollback
- Build ETL pipelines feeding data warehouses
- Process files from any source (local, S3, SFTP) in any format
- Integrate with external APIs respecting rate limits and handling failures
- Generate and distribute reports on schedule
- React to events (Kafka, S3, webhooks) with batch processing
- Write comprehensive tests for batch jobs
- Build a self-service batch platform with monitoring and alerting

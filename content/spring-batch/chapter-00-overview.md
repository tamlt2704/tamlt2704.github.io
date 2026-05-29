# Spring Batch: From Basics to Production

A comprehensive guide to Spring Batch 5 with Spring Boot 3.3, covering core concepts, implementation patterns, error handling, scaling strategies, and production deployment.

## Chapters

1. [Core Concepts](chapter-01-concepts.md) — Job, Step, Readers, Processors, Writers, chunk-oriented processing
2. [Project Setup](chapter-02-setup.md) — Gradle dependencies, auto-configuration, first job
3. [ItemReaders](chapter-03-readers.md) — CSV, JDBC, JPA, JSON, custom readers
4. [ItemProcessors](chapter-04-processors.md) — Transformation, filtering, validation, chaining
5. [ItemWriters](chapter-05-writers.md) — CSV, JDBC, JPA, JSON, composite writers
6. [Job Flow Control](chapter-06-flow.md) — Conditional flow, parallel steps, deciders, listeners
7. [Error Handling](chapter-07-error-handling.md) — Skip, retry, restart, fault tolerance
8. [Scaling](chapter-08-scaling.md) — Multi-threaded steps, partitioning, remote chunking
9. [Production](chapter-09-production.md) — Scheduling, monitoring, testing, Docker deployment

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
- Monitor and schedule jobs in production environments
- Write testable, idempotent batch processing pipelines

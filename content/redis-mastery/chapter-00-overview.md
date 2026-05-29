# Redis Mastery: From Basics to Advanced

A comprehensive guide to Redis covering data structures, Spring Boot integration, caching patterns, messaging, distributed systems, persistence, and performance tuning.

## Chapters

1. [Chapter 1: Redis Basics & Data Types](./chapter-01-basics.md)
2. [Chapter 2: Spring Data Redis](./chapter-02-spring-redis.md)
3. [Chapter 3: Caching Patterns](./chapter-03-caching.md)
4. [Chapter 4: Pub/Sub & Streams](./chapter-04-pubsub.md)
5. [Chapter 5: Distributed Patterns](./chapter-05-distributed.md)
6. [Chapter 6: Persistence & High Availability](./chapter-06-persistence.md)
7. [Chapter 7: Performance & Optimization](./chapter-07-performance.md)

## Prerequisites

- Java 17+
- Spring Boot 3.x
- Gradle
- Redis 7.x installed locally or via Docker

## Quick Start

```bash
# Run Redis via Docker
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Verify connection
redis-cli ping
# PONG
```

## Gradle Dependencies

```groovy
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-data-redis'
    implementation 'org.apache.commons:commons-pool2'
}
```

---

Next: [Chapter 1: Redis Basics & Data Types](./chapter-01-basics.md)

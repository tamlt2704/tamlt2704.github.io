# System Design: A Scaling Survival Story

A file-sharing startup went viral. One server. 2.4 million users. Three weeks until the podcast that brings 10 million more. Scale or die.

## The Story

You're the Staff Engineer at **GhostDrop**. The architecture is a single Django app on a single server. Everything — app, database, files, cache — lives on one box. It worked at 5,000 users. At 2.4 million, it's dying. You have 3 weeks to redesign it for 10 million.

## Chapters

### Part 1: Survive This Week

| # | The Crisis | What You Learn |
|---|-----------|----------------|
| 01 | One server, 2.4M users | Bottleneck analysis, vertical vs horizontal |
| 02 | Server dies = everything dies | Load balancers, redundancy |
| 03 | Files on local disk | Object storage (S3), CDN, signed URLs |
| 04 | DB on same box as app | Separating compute from storage |
| 05 | Every page hits the database | Caching — Redis, cache-aside, invalidation |

### Part 2: Survive This Month

| # | The Crisis | What You Learn |
|---|-----------|----------------|
| 06 | Uploads block web workers | Message queues, async processing |
| 07 | DB reads are 80% of load | Read replicas, read/write splitting |
| 08 | Monolith deploys take 40 min | Service decomposition, API gateway |
| 09 | Tokyo users get 800ms latency | CDN deep dive, edge caching, geo-routing |
| 10 | 10K req/sec, rate abuse | Rate limiting — token bucket, sliding window |

### Part 3: Survive Failure

| # | The Crisis | What You Learn |
|---|-----------|----------------|
| 11 | Redis dies, app crashes | Circuit breakers, graceful degradation |
| 12 | Upload succeeds, metadata fails | Distributed transactions, saga, idempotency |
| 13 | Cache says yes, storage says no | Consistency models — strong, eventual, causal |
| 14 | Deploy breaks production | Blue-green, canary, feature flags |
| 15 | "How do we know it's broken?" | Observability — metrics, traces, SLOs |

### Part 4: Survive 100M Users

| # | The Crisis | What You Learn |
|---|-----------|----------------|
| 16 | Single DB can't handle writes | Sharding — strategies, routing, resharding |
| 17 | Services need to react to events | Event-driven, Kafka, event sourcing |
| 18 | Share links at scale | URL shortener, ID generation, consistent hashing |
| 19 | Real-time notifications | WebSockets at scale, pub/sub, presence |
| 20 | The podcast: 10M users | Capacity planning, load testing, launch checklist |

## Core Principles

- No single point of failure
- Scale horizontally
- Async when possible
- Cache aggressively
- Measure everything
- Design for failure
- Tradeoffs, not solutions

## Prerequisites

Docker, basic SQL, basic HTTP. No cloud account needed — everything runs locally.

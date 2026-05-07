# Job Engine — The Intern's Tale

You're a fresh intern at **ShopZilla Inc.**, a chaotic e-commerce company where everything is on fire. Your manager, **Mrs. Jira**, creates tickets faster than your code compiles. The CTO, **Captain Deadline**, only speaks in "we need this yesterday." The senior dev, **Old Greg**, hasn't merged a PR since 2019 but has opinions about everything.

Your mission: build a job engine that actually works. No pressure.

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | The Intern | Eager, slightly terrified |
| **Mrs. Jira** | Product Manager | Fires tickets at 3am. "Just a small change." |
| **Captain Deadline** | CTO | Every sprint is a "war room." Loves Grafana. |
| **Old Greg** | Senior Dev | Reviews your PR 3 weeks later. "Why not use Semaphores?" |
| **Karen from Sales** | Stakeholder | "The CSV has 50,000 rows and I need it NOW." |
| **Silent Bob** | DevOps | Never speaks. Fixes prod at 2am. Communicates via Slack emoji. |
| **The Phantom** | That one stuck job | Running since Tuesday. No one knows what it does. |

## Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Backend | Java 21 + Spring Boot 3 | Industry standard, virtual threads, rich concurrency stdlib |
| Queue / State | PostgreSQL + Redis | Durable state + pub/sub for coordination |
| Build | Gradle (Kotlin DSL) | Modern, fast incremental builds |
| Containerization | Docker Compose | Run multiple worker instances locally |

## The Scenario: ShopZilla's Nightly Pipeline

Instead of dummy `Thread.sleep()` jobs, the engine processes real e-commerce work:

| Job Type | What It Does |
|---|---|
| `CSV_IMPORT` | Parse Karen's massive CSV into DB tables |
| `IMAGE_RESIZE` | Resize product images to thumb/medium/large |
| `PRICE_CALCULATION` | Recalculate prices with tax + currency conversion |
| `INVENTORY_SYNC` | Reconcile stock against warehouse REST API |
| `REPORT_GENERATION` | Aggregate orders into PDF sales reports |
| `EMAIL_DISPATCH` | Send batch emails (confirmations, reports) |
| `DATA_CLEANUP` | Archive old orders, purge expired sessions |

```
CSV_IMPORT (Karen's orders.csv)
    ├──→ PRICE_CALCULATION ──→ REPORT_GENERATION ──→ EMAIL_DISPATCH
    └──→ INVENTORY_SYNC
IMAGE_RESIZE (runs independently)
DATA_CLEANUP (runs independently)
```

## Chapters

Every chapter starts with a **problem**, a **failing test**, then builds the solution step by step until the test goes green.

| Ch | Title | The Incident | Read |
|---|---|---|---|
| 0 | Before You Start | Prerequisites, the story, the cast | [→ Chapter 0](./backend/chapter-00-prerequisites.md) |
| 1 | Your First Day | You build the engine | [→ Chapter 1](./backend/chapter-01-first-day.md) |
| 2 | The Thundering Herd | Karen gets duplicate products | [→ Chapter 2](./backend/chapter-02-multithreading.md) |
| 3 | Everything Breaks | The API goes down, all jobs fail | [→ Chapter 3](./backend/chapter-03-failure-handling.md) |
| 4 | The Big Red Button | Karen imports the wrong file | [→ Chapter 4](./backend/chapter-04-pause-resume-cancel.md) |
| 5 | The Dependency Web | Captain Deadline wants a nightly pipeline | [→ Chapter 5](./backend/chapter-05-dag-execution.md) |
| 6 | The Clone Wars | Silent Bob deploys 3 copies | [→ Chapter 6](./backend/chapter-06-multiple-instances.md) |
| 7 | The War Room Screen | No visibility into what's happening | [→ Chapter 7](./backend/chapter-07-real-time-api.md) |
| 8 | The Audit | Captain Deadline hires a consultant | [→ Chapter 8](./backend/chapter-08-observability.md) |
| 9 | Who Did What | Someone cancels 12,000 jobs | [→ Chapter 9](./backend/chapter-09-auth-and-audit.md) |

## What You'll Learn

### Chapter 1 — Single-threaded Runner
JPA entities, state machines, `@Scheduled` polling, REST controllers, CSV batch inserts

### Chapter 2 — Multi-threading & Concurrency
`ExecutorService`, `SELECT FOR UPDATE SKIP LOCKED`, `AtomicInteger`, `CompletableFuture`, `ReentrantLock`, `BlockingQueue`, `PriorityBlockingQueue`, `CountDownLatch`, `Semaphore`, virtual threads, graceful shutdown, Fork/Join, Redis caching, idempotency keys

### Chapter 3 — Failure Handling & Retries
Exception isolation, retry with exponential backoff, dead-letter queue, heartbeat monitoring, partial failure reporting

### Chapter 4 — Pause, Resume & Cancel
Cooperative cancellation, `JobHandler` strategy pattern, checkpointing, pause/resume lifecycle, batch operations

### Chapter 5 — DAG Execution
Directed acyclic graphs, cycle detection (Kahn's algorithm), topological sort, cascade failure, workflow orchestration

### Chapter 6 — Multiple Instances
Distributed locking (Redisson), leader election, service registration, job affinity, Docker Compose multi-instance

### Chapter 7 — Real-time API
Server-Sent Events (SSE), `curl` streaming, DAG query endpoints, progress tracking API

### Chapter 8 — Observability & Hardening
Structured logging (Logback + MDC), Micrometer metrics, Prometheus + Grafana, Gatling load testing

### Chapter 9 — Auth, Roles & Audit Trail
Spring Security + JWT, role-based access (VIEWER/OPERATOR/ADMIN), `@Audited` AOP aspect, audit log with user + action + timestamp + IP, Bucket4j rate limiting per user

## Project Structure

```
acode/jobengine/
├── README.md
├── backend/
│   ├── chapter-00-prerequisites.md
│   ├── chapter-01-first-day.md
│   ├── chapter-02-multithreading.md
│   ├── chapter-03-failure-handling.md
│   ├── chapter-04-pause-resume-cancel.md
│   ├── chapter-05-dag-execution.md
│   ├── chapter-06-multiple-instances.md
│   ├── chapter-07-real-time-api.md
│   ├── chapter-08-observability.md
│   ├── chapter-09-auth-and-audit.md
│   ├── images/                        # SVG illustrations per chapter
│   ├── build.gradle.kts
│   ├── settings.gradle.kts
│   └── src/
│       ├── main/java/com/jobengine/
│       │   ├── JobEngineApplication.java
│       │   ├── model/
│       │   ├── repository/
│       │   ├── engine/
│       │   ├── handler/
│       │   └── controller/
│       └── test/java/com/jobengine/
│           ├── Chapter1Test.java
│           ├── ...
│           └── Chapter9Test.java
├── docker-compose.yml
└── gatling/
```

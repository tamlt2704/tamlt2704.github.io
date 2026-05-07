# System Design: A Scaling Survival Story

You just became the first "Staff Engineer" at **GhostDrop** — a file-sharing startup that went viral on TikTok. Three weeks ago it had 5,000 users. Today it has 2.4 million. Next month the CEO is going on a podcast and expects 10 million.

The architecture is a single Django app on a single EC2 instance. One PostgreSQL database. One Redis. One server. Everything runs on one box.

It worked at 5,000 users. At 2.4 million, it's held together by prayers and a 64GB RAM upgrade someone panic-ordered at 2 AM.

The CTO — **Amir** — calls an emergency meeting:

> "We have three weeks before the podcast. If we go down on air, we're dead. The app needs to handle 10x current traffic. We need to redesign everything — but we can't stop shipping features. Figure out what to scale, in what order, and how."

He slides a napkin across the table:

> "Users upload files. Users share links. Users download files. That's it. Make it work at 10 million users. Go."

You open your notebook. The whiteboard is blank.

---

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Staff Engineer | "I've built CRUD apps. How different can 10M users be?" |
| **Amir** | CTO | Drew the original architecture on a napkin. It's still on a napkin. |
| **Sana** | Backend Lead | "If we add one more feature to the monolith, I'm quitting." |
| **Kai** | Frontend Lead | "The upload endpoint times out after 30 seconds." |
| **Ops Omar** | SRE | "The server has been at 98% CPU since Tuesday. I haven't slept." |
| **CEO Mia** | Founder | "The podcast is in 3 weeks. We cannot go down." |
| **The Single Server** | The architecture | One box. One process. One prayer. |

---

## The Current Architecture (Day 1)

```
┌─────────────────────────────────────────────────┐
│              Single EC2 Instance (r5.2xlarge)     │
│                                                   │
│  ┌───────────┐  ┌───────────┐  ┌─────────────┐ │
│  │  Django    │  │ PostgreSQL│  │    Redis     │ │
│  │  (gunicorn│  │  (local)  │  │   (local)   │ │
│  │   4 workers)│ │           │  │             │ │
│  └───────────┘  └───────────┘  └─────────────┘ │
│                                                   │
│  ┌───────────────────────────────────────────┐   │
│  │         Local Disk (500GB EBS)             │   │
│  │         (uploaded files live here)         │   │
│  └───────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
                        │
                   (port 443)
                        │
                   ┌────┴────┐
                   │  Users  │
                   │  2.4M   │
                   └─────────┘
```

Problems:
- Single point of failure (server dies = everything dies)
- Can't scale horizontally (one box)
- Files on local disk (can't add more servers)
- Database on same box (competes for CPU/RAM)
- No CDN (users in Tokyo download from us-east-1)
- No queue (uploads block the web workers)
- No monitoring (we find out it's down when Twitter tells us)

---

## How to Read This

Every chapter follows the same loop:

```
  📋 Traffic grows, something breaks
   │
   ▼
  🤔 You identify the bottleneck
   │
   ▼
  ⌨️  You learn the system design concept that fixes it
   │
   ▼
  💥 The fix creates a new problem (consistency, cost, complexity)
   │
   ▼
  🧠 You understand the tradeoff and make a decision
   │
   ▼
  📋 Traffic grows again
```

No concept shows up before you need it. You won't hear about sharding until a single database can't handle the write load. You won't touch event-driven architecture until synchronous processing blocks your web workers. You won't learn about consensus until your distributed cache serves stale data.

The traffic comes first. The architecture follows.

---

## The Roadmap

### Part 1: Foundations — "Survive This Week"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Crisis                             │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 01 │ One server, 2.4M users                 │ Bottleneck analysis, vertical vs horizontal scaling
────┼────────────────────────────────────────┼──────────────────────────────────────
 02 │ Server dies = everything dies           │ Load balancers, health checks, redundancy
────┼────────────────────────────────────────┼──────────────────────────────────────
 03 │ Files on local disk can't scale        │ Object storage (S3), CDN, signed URLs
────┼────────────────────────────────────────┼──────────────────────────────────────
 04 │ Database on same box as the app        │ Separating compute from storage, managed DB
────┼────────────────────────────────────────┼──────────────────────────────────────
 05 │ Every page hits the database           │ Caching layers — Redis, cache-aside, TTL, invalidation
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 2: Scale — "Survive This Month"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Crisis                             │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 06 │ Uploads block web workers for 30s      │ Message queues, async processing, workers
────┼────────────────────────────────────────┼──────────────────────────────────────
 07 │ Database reads are 80% of load         │ Read replicas, read/write splitting
────┼────────────────────────────────────────┼──────────────────────────────────────
 08 │ API is a monolith, deploys take 40 min │ Service decomposition, API gateway, when to split
────┼────────────────────────────────────────┼──────────────────────────────────────
 09 │ Users in Tokyo get 800ms latency       │ CDN deep dive, edge caching, geo-routing
────┼────────────────────────────────────────┼──────────────────────────────────────
 10 │ 10K requests/sec, rate abuse           │ Rate limiting — token bucket, sliding window, distributed
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 3: Reliability — "Survive Failure"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Crisis                             │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 11 │ Redis dies, app crashes                │ Circuit breakers, graceful degradation, fallbacks
────┼────────────────────────────────────────┼──────────────────────────────────────
 12 │ User uploads file, metadata save fails │ Distributed transactions, saga pattern, idempotency
────┼────────────────────────────────────────┼──────────────────────────────────────
 13 │ Cache says file exists, storage says no│ Consistency models — strong, eventual, causal
────┼────────────────────────────────────────┼──────────────────────────────────────
 14 │ Deploy breaks production               │ Blue-green, canary, feature flags, rollback
────┼────────────────────────────────────────┼──────────────────────────────────────
 15 │ "How do we know it's broken?"          │ Observability — metrics, traces, logs, SLOs, alerting
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 4: Advanced — "Survive 100M Users"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Crisis                             │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 16 │ Single DB can't handle write load      │ Database sharding — strategies, routing, resharding
────┼────────────────────────────────────────┼──────────────────────────────────────
 17 │ Services need to react to events       │ Event-driven architecture, Kafka, event sourcing
────┼────────────────────────────────────────┼──────────────────────────────────────
 18 │ Generating share links at scale        │ URL shortener design, ID generation, consistent hashing
────┼────────────────────────────────────────┼──────────────────────────────────────
 19 │ Real-time notifications                │ WebSockets at scale, pub/sub, presence
────┼────────────────────────────────────────┼──────────────────────────────────────
 20 │ The podcast: 10M users, 3 weeks        │ Capacity planning, load testing, the launch checklist
────┴────────────────────────────────────────┴──────────────────────────────────────
```

---

## The Architecture We're Building

By Chapter 20:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              GhostDrop v2                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────┐     ┌──────────────┐     ┌──────────────────────────────┐ │
│  │  CDN    │────→│ Load Balancer │────→│  API Servers (auto-scaled)   │ │
│  │(CloudFront)│  │  (ALB)       │     │  ├── upload-service          │ │
│  └─────────┘     └──────────────┘     │  ├── download-service        │ │
│                                        │  ├── share-service           │ │
│                                        │  └── user-service            │ │
│                                        └──────────────────────────────┘ │
│                                                     │                    │
│                          ┌──────────────────────────┼────────────┐      │
│                          │                          │            │      │
│                          ▼                          ▼            ▼      │
│                   ┌─────────────┐          ┌────────────┐  ┌────────┐  │
│                   │  PostgreSQL │          │   Redis    │  │  SQS   │  │
│                   │  (primary + │          │  (cluster) │  │ (queue)│  │
│                   │   replicas) │          └────────────┘  └───┬────┘  │
│                   └─────────────┘                              │       │
│                                                                ▼       │
│                   ┌─────────────┐                     ┌────────────┐   │
│                   │     S3      │                     │  Workers   │   │
│                   │  (files)    │                     │ (processing)│  │
│                   └─────────────┘                     └────────────┘   │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Observability: Prometheus + Grafana + Distributed Tracing        │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Core Principles

Every chapter comes back to these:

| Principle | Meaning |
|---|---|
| **No single point of failure** | If one thing dies, the system survives |
| **Scale horizontally** | Add more machines, not bigger machines |
| **Async when possible** | Don't make users wait for background work |
| **Cache aggressively** | The fastest query is the one you don't make |
| **Measure everything** | You can't fix what you can't see |
| **Design for failure** | Everything will break. Plan for it. |
| **Tradeoffs, not solutions** | Every choice has a cost. Know what you're paying. |

---

## The Tradeoff Triangle

Every design decision lives here:

```
        Consistency
           /\
          /  \
         /    \
        /      \
       /________\
 Availability    Performance
```

You can't have all three perfectly. Every chapter forces you to choose:
- Fast but eventually consistent? (CDN, cache)
- Consistent but slower? (synchronous replication)
- Available but possibly stale? (read replicas)

The right answer is always "it depends." This series teaches you what it depends *on*.

---

## Prerequisites

- **Docker** (for running services locally)
- **Basic SQL** (SELECT, JOIN, INSERT — the SQL Mastery series covers the rest)
- **Basic networking** (HTTP, DNS, TCP — we'll explain as needed)
- **Any programming language** (examples in Python, but concepts are universal)

```bash
# We'll spin up services as needed
docker --version  # 20+
```

No cloud account required for learning. Everything runs locally. When we discuss AWS/GCP services, we'll explain what they do and use local equivalents.

---

## How This Connects to Your Other Knowledge

| If you know... | This series adds... |
|---|---|
| Redis (redis101) | When to cache, invalidation strategies, cluster mode |
| Docker (docker101) | Container orchestration, service mesh, health checks |
| PostgreSQL (postgres-mastery) | Replication, sharding, connection pooling at scale |
| FastAPI | API gateway patterns, service decomposition |
| GitHub Workflow | CI/CD, blue-green deploys, feature flags |

System design is the glue. It's where all the individual tools come together into a coherent architecture.

---

## A Note on "The Right Answer"

There is no single correct architecture. There are tradeoffs. This series doesn't teach you "the answer" — it teaches you:

1. How to identify bottlenecks
2. What options exist to fix them
3. What each option costs (complexity, money, consistency)
4. How to choose based on your specific constraints

A startup with 10K users needs a different architecture than one with 10M. Both are "correct" for their context. Over-engineering is as dangerous as under-engineering.

---

[Next: Chapter 1 — The Bottleneck →](chapter-01-the-bottleneck.md)

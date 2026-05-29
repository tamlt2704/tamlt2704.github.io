# Chapter 1: Scalability

[← Chapter 0: Overview](/blog/system-design/chapter-00-overview) | [Chapter 2: Database →](/blog/system-design/chapter-02-database)

---

## What is Scalability?

A system is scalable if it can handle increased load without degrading performance — by adding resources, not rewriting code.

---

## Vertical vs Horizontal Scaling

```
Vertical Scaling (Scale Up)          Horizontal Scaling (Scale Out)
┌─────────────────────┐              ┌───────┐ ┌───────┐ ┌───────┐
│                     │              │Server │ │Server │ │Server │
│   BIGGER SERVER     │              │  1    │ │  2    │ │  3    │
│   More CPU, RAM     │              └───────┘ └───────┘ └───────┘
│   More Disk         │                    │       │       │
│                     │              ┌─────────────────────────────┐
└─────────────────────┘              │       Load Balancer         │
                                     └─────────────────────────────┘
```

| Aspect     | Vertical                                                   | Horizontal                  |
| ---------- | ---------------------------------------------------------- | --------------------------- |
| Simplicity | Easy — just upgrade hardware                               | Complex — distributed state |
| Limit      | Hardware ceiling (you can't buy a 1TB RAM machine forever) | Virtually unlimited         |
| Downtime   | Usually requires restart                                   | Zero downtime (add nodes)   |
| Cost       | Exponential (2x CPU ≠ 2x price)                            | Linear                      |
| Failure    | Single point of failure                                    | Redundancy built-in         |

**Rule of thumb:** Start vertical (simpler), go horizontal when you hit limits.

---

## Stateless vs Stateful Services

The #1 prerequisite for horizontal scaling: **make your services stateless**.

```
STATEFUL (hard to scale):
┌──────────┐
│ Server A │ ← stores user session in memory
└──────────┘
  If user's next request goes to Server B → session lost!

STATELESS (easy to scale):
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Server A │  │ Server B │  │ Server C │
└──────────┘  └──────────┘  └──────────┘
       │            │            │
       └────────────┼────────────┘
                    ▼
            ┌──────────────┐
            │ Shared State │  (Redis, DB, JWT)
            └──────────────┘
```

**How to make services stateless:**

- Store sessions in Redis or use JWT tokens
- Store file uploads in S3/object storage, not local disk
- Store config in environment variables or config service
- No in-memory caches that can't be lost (use Redis instead)

---

## The Scale Cube (AKF Scale Cube)

Three dimensions of scaling:

```
         Y-axis: Functional decomposition
         (split by service/feature)
              │
              │
              │
              │
              └──────────────── X-axis: Horizontal cloning
             /                  (more identical instances)
            /
           /
          Z-axis: Data partitioning
          (split by user/geography)
```

| Axis | Strategy          | Example                                                      |
| ---- | ----------------- | ------------------------------------------------------------ |
| X    | Clone everything  | 10 identical API servers behind LB                           |
| Y    | Split by function | Separate auth service, payment service, notification service |
| Z    | Split by data     | Users A-M → Shard 1, N-Z → Shard 2                           |

---

## Throughput, Latency, and Availability

**Throughput** — how many requests per second (QPS/RPS) the system handles.

**Latency** — how long a single request takes (p50, p95, p99).

**Availability** — percentage of time the system is operational.

```
Availability    Downtime/year    Downtime/month
99%             3.65 days        7.3 hours
99.9%           8.76 hours       43.8 minutes
99.99%          52.6 minutes     4.38 minutes
99.999%         5.26 minutes     26.3 seconds
```

**The tradeoff triangle:**

You often can't maximize all three simultaneously:

- High throughput + low latency → expensive (more servers)
- High availability + consistency → complex (distributed consensus)
- Low latency + high availability → may sacrifice consistency (eventual consistency)

---

## Common Scaling Patterns

### 1. Read Replicas

Most apps are read-heavy (90% reads, 10% writes):

```
Writes ──▶ ┌────────────┐
            │   Primary  │
            │   (Master) │
            └─────┬──────┘
                  │ replication
         ┌────────┼────────┐
         ▼        ▼        ▼
    ┌────────┐ ┌────────┐ ┌────────┐
    │Replica │ │Replica │ │Replica │
    │   1    │ │   2    │ │   3    │
    └────────┘ └────────┘ └────────┘
         ▲        ▲        ▲
         └────────┼────────┘
                  │
Reads ────────────┘
```

### 2. CQRS (Command Query Responsibility Segregation)

Separate the write model from the read model:

```
┌─────────────┐         ┌─────────────────┐
│  Write API  │────────▶│  Write Database  │
│ (commands)  │         │  (normalized)    │
└─────────────┘         └────────┬────────┘
                                 │ events
                                 ▼
┌─────────────┐         ┌─────────────────┐
│  Read API   │◀────────│  Read Database   │
│ (queries)   │         │  (denormalized)  │
└─────────────┘         └─────────────────┘
```

**When to use CQRS:**

- Read and write patterns are very different
- Read model needs different indexes/structure than write model
- You need to scale reads and writes independently

### 3. Event-Driven Architecture

Decouple services via events instead of synchronous calls:

```
┌──────────┐    event     ┌─────────────┐    event     ┌──────────┐
│ Order    │──────────────▶│  Message    │──────────────▶│ Payment  │
│ Service  │              │  Broker     │              │ Service  │
└──────────┘              │ (Kafka)     │              └──────────┘
                          └──────┬──────┘
                                 │ event
                                 ▼
                          ┌──────────────┐
                          │ Notification │
                          │   Service    │
                          └──────────────┘
```

### 4. Database Sharding

Split data across multiple database instances:

```
User ID % 3 = ?

  0 → Shard A (users 0, 3, 6, 9...)
  1 → Shard B (users 1, 4, 7, 10...)
  2 → Shard C (users 2, 5, 8, 11...)
```

---

## Scaling Checklist

When you need to scale, go through this in order:

1. **Optimize code** — fix N+1 queries, add indexes, reduce allocations
2. **Add caching** — Redis for hot data, CDN for static assets
3. **Scale vertically** — bigger machine (quick win)
4. **Scale horizontally** — more instances + load balancer
5. **Add read replicas** — offload read traffic
6. **Shard the database** — when single DB can't handle writes
7. **Go async** — message queues for non-critical paths
8. **Split services** — microservices for independent scaling

**Don't jump to step 8 before exhausting steps 1-3.** Premature optimization is the root of all evil, but premature distribution is worse.

---

## Real Example: Scaling a Notification Service

**Stage 1: 100 QPS** — Single server, PostgreSQL, synchronous sends.

**Stage 2: 1,000 QPS** — Add Redis cache for user preferences. Read replicas for DB.

**Stage 3: 10,000 QPS** — Message queue (Kafka) between API and sender. Multiple sender workers.

**Stage 4: 100,000 QPS** — Shard by user ID. Separate services for email/push/SMS. Rate limiting per channel.

```
Stage 4 Architecture:

┌─────────┐     ┌───────────┐     ┌─────────────┐
│  API    │────▶│   Kafka   │────▶│ Email Worker│ (x5)
│ Gateway │     │           │     └─────────────┘
└─────────┘     │           │────▶┌─────────────┐
                │           │     │ Push Worker │ (x3)
                │           │     └─────────────┘
                │           │────▶┌─────────────┐
                └───────────┘     │ SMS Worker  │ (x2)
                                  └─────────────┘
```

---

[Chapter 2: Database Design & Scaling →](/blog/system-design/chapter-02-database)

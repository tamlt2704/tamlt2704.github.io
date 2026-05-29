# Chapter 0: System Design for Backend Engineers

## Chapters

- [Chapter 0: Overview (this page)](/blog/system-design/chapter-00-overview)
- [Chapter 1: Scalability](/blog/system-design/chapter-01-scalability)
- [Chapter 2: Database Design & Scaling](/blog/system-design/chapter-02-database)
- [Chapter 3: Caching Strategies](/blog/system-design/chapter-03-caching)
- [Chapter 4: Message Queues & Async Processing](/blog/system-design/chapter-04-message-queues)
- [Chapter 5: API Design](/blog/system-design/chapter-05-api-design)
- [Chapter 6: Load Balancing & Reverse Proxies](/blog/system-design/chapter-06-load-balancing)
- [Chapter 7: Microservices Architecture](/blog/system-design/chapter-07-microservices)
- [Chapter 8: Consistency & Distributed Systems](/blog/system-design/chapter-08-consistency)
- [Chapter 9: Real-World System Designs](/blog/system-design/chapter-09-real-world)

---

## Why System Design?

You can write clean code. You can build REST APIs. But when the interviewer asks "Design Twitter" or your service starts getting 10,000 requests per second — you need to think at a different level.

System design is about **tradeoffs**. There's no perfect answer. Every choice has a cost.

---

## The Mental Framework

Every system design problem follows the same skeleton:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Clients    │────▶│   Services   │────▶│    Storage    │
│ (Web/Mobile) │     │  (Compute)   │     │  (Data)      │
└──────────────┘     └──────────────┘     └──────────────┘
       │                     │                     │
       ▼                     ▼                     ▼
  Rate Limiting        Load Balancing         Replication
  CDN / Edge           Caching               Sharding
  API Gateway          Message Queues        Consistency
```

**Step 1:** Clarify requirements (functional + non-functional)
**Step 2:** Estimate scale (QPS, storage, bandwidth)
**Step 3:** High-level design (boxes and arrows)
**Step 4:** Deep dive into components
**Step 5:** Address bottlenecks and failure modes

---

## Back-of-the-Envelope Estimation

Numbers every backend engineer should know:

| Operation                            | Latency |
| ------------------------------------ | ------- |
| L1 cache reference                   | 0.5 ns  |
| L2 cache reference                   | 7 ns    |
| RAM reference                        | 100 ns  |
| SSD random read                      | 150 μs  |
| HDD seek                             | 10 ms   |
| Network round trip (same datacenter) | 0.5 ms  |
| Network round trip (cross-continent) | 150 ms  |

**Quick math shortcuts:**

| Scale       | Requests/day | Requests/second |
| ----------- | ------------ | --------------- |
| 1 million   | 1M           | ~12 QPS         |
| 100 million | 100M         | ~1,200 QPS      |
| 1 billion   | 1B           | ~12,000 QPS     |

```
Seconds in a day ≈ 100,000 (actually 86,400)
1 million / 100,000 = 10 QPS (close enough for estimation)
```

**Storage:**

- 1 char = 1 byte (ASCII) or 2-4 bytes (UTF-8)
- 1 tweet (280 chars) ≈ 300 bytes
- 1 image ≈ 300 KB
- 1 video minute ≈ 50 MB

---

## The Topics We'll Cover

| Chapter | Topic          | Key Question                                    |
| ------- | -------------- | ----------------------------------------------- |
| 1       | Scalability    | How do I handle 10x, 100x, 1000x more traffic?  |
| 2       | Database       | SQL vs NoSQL? Sharding? Replication?            |
| 3       | Caching        | What to cache? Where? Invalidation?             |
| 4       | Message Queues | When to go async? Exactly-once delivery?        |
| 5       | API Design     | REST vs gRPC? Pagination? Versioning?           |
| 6       | Load Balancing | How to distribute traffic? Health checks?       |
| 7       | Microservices  | When to split? Service discovery?               |
| 8       | Consistency    | CAP theorem? Eventual vs strong?                |
| 9       | Real-World     | Design URL shortener, chat, notification system |

---

## Prerequisites

- Comfortable with at least one backend language (Java, Go, Python)
- Basic understanding of HTTP, TCP/IP, DNS
- Familiarity with SQL databases
- Experience deploying at least one web application

---

[Chapter 1: Scalability →](/blog/system-design/chapter-01-scalability)

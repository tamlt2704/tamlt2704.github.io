# Chapter 0: The System Design Interview Framework

[Next: URL Shortener →](./chapter-01-url-shortener.md)

---

## The Question

> "Before we dive into specific problems, let's talk about how you should structure any system design interview. You have 45 minutes. How do you use them?"

---

## The 7-Step Framework (45 Minutes)

### Step 1: Requirements & Scope (5 min)

Ask clarifying questions. Never jump into design without understanding:

- **Functional requirements** — What does the system do?
- **Non-functional requirements** — Scale, latency, availability, consistency
- **Out of scope** — What are we NOT building today?

Example questions to ask:
- "How many users? DAU vs MAU?"
- "What's the read/write ratio?"
- "Do we need strong consistency or is eventual OK?"
- "What's the expected latency SLA?"

### Step 2: Back-of-Envelope Estimation (5 min)

Show you can think about scale. Key numbers:

| Metric | Shorthand |
|--------|-----------|
| 1 million requests/day | ~12 req/sec |
| 100 million requests/day | ~1,200 req/sec |
| 1 billion requests/day | ~12,000 req/sec |
| 1 KB per record, 1B records | ~1 TB storage |

Estimate: QPS, storage, bandwidth, memory for cache.

### Step 3: API Design (5 min)

Define the contract. REST or RPC style:

```
POST /api/v1/resource
GET  /api/v1/resource/{id}
```

Include: parameters, return values, authentication approach.

### Step 4: Data Model (5 min)

Choose storage and define schema:

- SQL vs NoSQL — justify the choice
- Key tables/collections and their relationships
- Indexes you'll need
- Partitioning strategy (if at scale)

### Step 5: High-Level Architecture (10 min)

Draw the boxes and arrows. Include:

- Clients → Load Balancer → App Servers → Database
- Caches, queues, CDNs where appropriate
- Data flow for read and write paths

### Step 6: Deep Dive (10 min)

The interviewer picks 1-2 areas. Go deep on:

- Specific algorithms (consistent hashing, fan-out)
- Failure scenarios and recovery
- Trade-offs you're making and why

### Step 7: Bottlenecks & Scaling (5 min)

Identify single points of failure. Discuss:

- Horizontal scaling strategies
- Database sharding/replication
- Monitoring and alerting
- What breaks at 10x scale?

---

## Tips for the Interview

- **Drive the conversation** — Don't wait for the interviewer to guide you
- **Think out loud** — They're evaluating your thought process
- **Trade-offs over perfection** — Every choice has a cost; name it
- **Start simple, then scale** — Get a working design first, optimize second
- **Use numbers** — Concrete estimates beat hand-waving
- **Draw diagrams** — Visual communication is faster and clearer

---

## Common Mistakes

- Jumping into low-level details without establishing requirements
- Designing for Google scale when the problem is 1,000 users
- Not asking clarifying questions (shows poor communication)
- Picking technologies without justifying the choice
- Ignoring failure modes — "What if this server dies?"
- Over-engineering: adding Kafka, Redis, and microservices to a TODO app
- Spending too long on one section and running out of time
- Not discussing monitoring, logging, or operational concerns

---

## Key Talking Points

- Always start with requirements — scope determines design
- Estimation grounds your design in reality
- Every component should justify its existence
- Name trade-offs explicitly: consistency vs availability, latency vs throughput
- The interviewer wants to see structured thinking, not a perfect answer

---

[Next: URL Shortener →](./chapter-01-url-shortener.md)

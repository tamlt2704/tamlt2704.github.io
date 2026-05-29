# Chapter 9: Real-World System Designs

[← Chapter 8: Consistency](/blog/system-design/chapter-08-consistency)

---

## The Approach

Every system design interview follows the same structure:

1. **Clarify requirements** (2-3 min) — functional + non-functional
2. **Estimate scale** (2-3 min) — QPS, storage, bandwidth
3. **High-level design** (10 min) — components and data flow
4. **Deep dive** (15 min) — pick 2-3 components to detail
5. **Bottlenecks & tradeoffs** (5 min) — failure modes, scaling plan

---

## Design 1: URL Shortener (bit.ly)

### Requirements

**Functional:**

- Shorten a long URL → short URL
- Redirect short URL → original URL
- Optional: custom aliases, expiration, analytics

**Non-functional:**

- 100M URLs created/month
- 10:1 read:write ratio → 1B redirects/month
- Low latency redirects (< 50ms)
- High availability (redirects must always work)

### Estimation

```
Writes: 100M/month ÷ 2.5M sec/month ≈ 40 QPS
Reads:  1B/month ÷ 2.5M sec/month ≈ 400 QPS
Storage: 100M × 500 bytes = 50 GB/month → 3 TB over 5 years
```

### High-Level Design

```
┌──────────┐     ┌─────────────┐     ┌──────────┐     ┌──────────┐
│  Client  │────▶│  API Server │────▶│  Redis   │────▶│PostgreSQL│
└──────────┘     └─────────────┘     │  (cache) │     │  (store) │
                                     └──────────┘     └──────────┘
```

### Key Decisions

**URL encoding:** Base62 (a-z, A-Z, 0-9) with 7 characters = 62^7 = 3.5 trillion combinations.

**ID generation options:**

| Approach                  | Pros                      | Cons                              |
| ------------------------- | ------------------------- | --------------------------------- |
| Auto-increment + Base62   | Simple, sequential        | Predictable, single DB bottleneck |
| Hash (MD5/SHA) + truncate | No coordination           | Collisions possible               |
| Pre-generated IDs (range) | Fast, no collision        | Complexity of ID service          |
| Snowflake ID              | Distributed, time-ordered | 64-bit → longer short URL         |

**Recommended:** Pre-generate ranges. Each server gets a batch of IDs (e.g., 1000-1999). No coordination needed during writes.

**Read path (redirect):**

```
1. GET /abc1234
2. Check Redis cache → hit? 301 redirect
3. Cache miss → query PostgreSQL
4. Store in Redis (TTL 24h)
5. Return 301 redirect
```

**301 vs 302:**

- 301 (Permanent): Browser caches, fewer server hits, but can't track analytics
- 302 (Temporary): Every click hits server, enables analytics

---

## Design 2: Chat System (WhatsApp/Slack)

### Requirements

**Functional:**

- 1:1 messaging
- Group chat (up to 500 members)
- Online/offline status
- Message history
- Read receipts

**Non-functional:**

- 50M daily active users
- Each user sends 40 messages/day
- Low latency delivery (< 200ms)
- Messages must never be lost

### Estimation

```
Messages/day: 50M × 40 = 2B messages/day
QPS: 2B / 86400 ≈ 23,000 messages/sec
Storage: 2B × 100 bytes = 200 GB/day → 73 TB/year
Connections: 50M concurrent WebSocket connections
```

### High-Level Design

```
┌──────────┐    WebSocket    ┌──────────────┐     ┌─────────┐
│ Client A │◀───────────────▶│  Chat Server │◀───▶│  Kafka  │
└──────────┘                 │  (stateful)  │     └────┬────┘
                             └──────────────┘          │
┌──────────┐    WebSocket    ┌──────────────┐          │
│ Client B │◀───────────────▶│  Chat Server │◀─────────┘
└──────────┘                 │  (stateful)  │
                             └──────────────┘
                                    │
                             ┌──────┴──────┐
                             │  Cassandra  │  (message store)
                             └─────────────┘
```

### Key Decisions

**Connection management:**

- Each user maintains a WebSocket to one chat server
- Connection registry (Redis): `user_id → chat_server_id`
- When A sends to B: look up B's server, route message there

**Message delivery:**

```
1. Client A sends message via WebSocket
2. Chat server stores in Cassandra (partition key = chat_id)
3. Chat server publishes to Kafka topic
4. B's chat server consumes from Kafka
5. B's chat server pushes to Client B via WebSocket
6. If B is offline → store in "pending messages" queue
7. When B comes online → deliver pending messages
```

**Group messages:**

- Fan-out on write (small groups): write message to each member's inbox
- Fan-out on read (large groups): store once, members fetch on read

**Message storage (Cassandra):**

```sql
CREATE TABLE messages (
    chat_id UUID,
    message_id TIMEUUID,  -- time-ordered
    sender_id UUID,
    content TEXT,
    created_at TIMESTAMP,
    PRIMARY KEY (chat_id, message_id)
) WITH CLUSTERING ORDER BY (message_id DESC);
```

Partition by `chat_id` → all messages for a chat on same node → fast sequential reads.

---

## Design 3: Notification System

### Requirements

**Functional:**

- Push notifications (mobile)
- Email notifications
- SMS notifications
- In-app notifications
- User preferences (opt-in/out per channel)
- Rate limiting (don't spam users)

**Non-functional:**

- 100M notifications/day
- Soft real-time (< 5 second delivery for push)
- At-least-once delivery
- Pluggable channels

### High-Level Design

```
┌──────────────┐     ┌─────────────┐     ┌──────────────────┐
│ Trigger      │────▶│  Kafka      │────▶│  Notification    │
│ Services     │     │  (events)   │     │  Service         │
│ (Order,Auth) │     └─────────────┘     └────────┬─────────┘
└──────────────┘                                   │
                                          ┌────────┼────────┐
                                          ▼        ▼        ▼
                                     ┌────────┐┌───────┐┌──────┐
                                     │  Push  ││ Email ││ SMS  │
                                     │ Worker ││Worker ││Worker│
                                     └───┬────┘└───┬───┘└──┬───┘
                                         │         │       │
                                         ▼         ▼       ▼
                                       APNs/    SendGrid  Twilio
                                       FCM
```

### Key Decisions

**Event schema:**

```json
{
  "event_type": "ORDER_SHIPPED",
  "user_id": "user-123",
  "data": {
    "order_id": "order-456",
    "tracking": "UPS123"
  },
  "channels": ["push", "email"],
  "priority": "high"
}
```

**Processing pipeline:**

1. Event arrives in Kafka
2. Notification service checks user preferences (Redis cache)
3. Applies rate limiting (max 5 push/hour per user)
4. Renders template per channel
5. Routes to channel-specific worker queue
6. Worker delivers via external provider
7. Store delivery status (for retry/analytics)

**Deduplication:** Use event_id + user_id as idempotency key. Prevents duplicate notifications on retry.

**Priority queues:** High-priority (security alerts, OTP) bypass rate limits and use separate queues.

---

## Design 4: Rate Limiter

### Requirements

- Limit API requests per user/IP
- Multiple rules (100/min per user, 1000/hour per IP)
- Distributed (works across multiple API servers)
- Low latency (< 1ms overhead per request)

### Sliding Window Counter (Redis)

```
Key: rate:{user_id}:{minute_timestamp}
Value: request count

Algorithm:
1. Current minute count + weighted previous minute count
2. If total > limit → reject (429)
```

```java
public boolean isAllowed(String userId, int limit, int windowSec) {
    long now = System.currentTimeMillis();
    long currentWindow = now / (windowSec * 1000);
    long previousWindow = currentWindow - 1;

    String currentKey = "rate:" + userId + ":" + currentWindow;
    String previousKey = "rate:" + userId + ":" + previousWindow;

    // Atomic pipeline
    Long currentCount = redis.opsForValue().increment(currentKey);
    redis.expire(currentKey, Duration.ofSeconds(windowSec * 2));

    Long previousCount = Optional.ofNullable(
        redis.opsForValue().get(previousKey)
    ).map(Long::parseLong).orElse(0L);

    // Weighted: how far into current window are we?
    double weight = 1.0 - ((now % (windowSec * 1000.0)) / (windowSec * 1000.0));
    long total = (long)(previousCount * weight) + currentCount;

    return total <= limit;
}
```

### Where to Place the Rate Limiter

```
Option 1: API Gateway (centralized)
Client → [Rate Limiter in Gateway] → Service

Option 2: Middleware (per service)
Client → Gateway → [Rate Limiter Middleware] → Controller

Option 3: Sidecar (service mesh)
Client → Gateway → [Envoy Sidecar + Rate Limit] → Service
```

---

## Design 5: Distributed Job Scheduler

### Requirements

- Schedule jobs to run at specific times (cron-like)
- One-time and recurring jobs
- Exactly-once execution (no duplicates)
- Handle millions of scheduled jobs
- Survive node failures

### High-Level Design

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Scheduler   │────▶│   Job Queue  │────▶│   Workers    │
│  (picks due  │     │   (Kafka/    │     │  (execute)   │
│   jobs)      │     │    Redis)    │     │              │
└──────┬───────┘     └──────────────┘     └──────────────┘
       │
┌──────┴───────┐
│  Job Store   │  (PostgreSQL: job definitions, schedules)
│              │  (Redis sorted set: next execution times)
└──────────────┘
```

### Key Decisions

**Job scheduling with Redis sorted set:**

```
ZADD scheduled_jobs <next_run_timestamp> <job_id>

# Scheduler polls every second:
ZRANGEBYSCORE scheduled_jobs 0 <now> LIMIT 0 100
# Returns jobs due for execution
```

**Exactly-once execution:**

- Use distributed lock per job: `SETNX lock:job:{id} {worker_id} EX 300`
- Only the worker that acquires the lock executes
- On completion: update job status, release lock, schedule next run

**Recurring jobs:**

```
After execution:
1. Calculate next run time from cron expression
2. ZADD scheduled_jobs <next_run_timestamp> <job_id>
```

---

## Common Patterns Across All Designs

| Pattern                | Where Used                                                             |
| ---------------------- | ---------------------------------------------------------------------- |
| **Cache-aside**        | URL shortener (Redis), Chat (user status), Notifications (preferences) |
| **Message queue**      | Chat (Kafka), Notifications (channel workers), Job scheduler           |
| **Consistent hashing** | Chat (connection routing), URL shortener (ID generation)               |
| **Write-ahead log**    | Chat (message durability), Job scheduler (job state)                   |
| **Fan-out**            | Notifications (multi-channel), Chat (group messages)                   |
| **Idempotency**        | All systems (retry safety)                                             |
| **Rate limiting**      | API gateway, Notifications (per-user limits)                           |
| **Circuit breaker**    | Notifications (external providers), Chat (service calls)               |

---

## Interview Checklist

Before finishing any system design:

- [ ] Addressed single points of failure
- [ ] Discussed data partitioning strategy
- [ ] Mentioned monitoring and alerting
- [ ] Considered failure modes and recovery
- [ ] Discussed tradeoffs made (and alternatives)
- [ ] Estimated if the design handles the required scale
- [ ] Mentioned security (auth, encryption, input validation)

---

[← Chapter 8: Consistency](/blog/system-design/chapter-08-consistency)

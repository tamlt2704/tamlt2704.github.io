# Chapter 2: Design an API Rate Limiter

[← URL Shortener](./chapter-01-url-shortener.md) | [Next: Chat System →](./chapter-03-chat.md)

---

## The Question

> "Design a rate limiting system for an API gateway. It should support different rate limits per user, per endpoint, and per pricing tier. The system must work across multiple servers in a distributed environment."

---

## Step 1: Requirements & Scope

**Functional:**
- Limit requests per user/IP/API key
- Configurable rules (100 req/min for free, 1000 req/min for paid)
- Return 429 Too Many Requests when limit exceeded
- Include rate limit headers (X-RateLimit-Remaining, X-RateLimit-Reset)

**Non-functional:**
- Low latency (<5ms overhead per request)
- Distributed — works across multiple API servers
- Highly available (if rate limiter fails, allow traffic through)
- Accurate counting (minimal over-counting or under-counting)

**Out of scope:** DDoS protection (that's a different layer), billing integration.

---

## Step 2: Estimation

| Metric | Calculation | Result |
|--------|-------------|--------|
| Total API traffic | 500M requests/day | ~6,000 req/sec |
| Rate limit checks | 1 check per request | ~6,000 checks/sec |
| Rules storage | 1M users × 100 bytes | ~100 MB |
| Redis memory | Counters for active users | ~5 GB |

Redis handles 100K+ ops/sec on a single node — one cluster is sufficient.

---

## Step 3: API Design

Rate limiter is middleware, not a user-facing API. But configuration:

```
PUT /api/v1/rate-limits/rules
  Body: { "tier": "free", "endpoint": "/api/*", "limit": 100, "window": 60 }

Response Headers (on every API call):
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 67
  X-RateLimit-Reset: 1672531260
```

---

## Step 4: Data Model

**Rate Limit Rules (SQL — low volume, needs flexibility):**

| Field | Type |
|-------|------|
| id | UUID |
| tier | VARCHAR |
| endpoint_pattern | VARCHAR |
| max_requests | INT |
| window_seconds | INT |

**Counters (Redis):**

```
Key:   rate_limit:{user_id}:{endpoint}:{window_start}
Value: current_count
TTL:   window_seconds
```

---

## Step 5: High-Level Architecture

```
┌──────────┐     ┌──────────────┐     ┌─────────────────┐     ┌─────────────┐
│  Client  │────▶│ Load Balancer│────▶│  API Gateway /  │────▶│  App Server │
└──────────┘     └──────────────┘     │  Rate Limiter   │     └─────────────┘
                                      └────────┬────────┘
                                               │
                                               ▼
                                      ┌─────────────────┐
                                      │  Redis Cluster  │
                                      │  (counters)     │
                                      └─────────────────┘
                                               │
                                      ┌────────▼────────┐
                                      │  Rules Config   │
                                      │  (DB + cache)   │
                                      └─────────────────┘
```

**Flow:** Request → Gateway checks Redis counter → If under limit: increment & forward. If over: return 429.

---

## Step 6: Deep Dive — Algorithms

### Token Bucket
- Bucket holds N tokens, refills at rate R tokens/sec
- Each request consumes 1 token; rejected if bucket empty
- **Pro:** Allows bursts up to bucket size. **Con:** Memory per user per endpoint.

### Fixed Window Counter
- Count requests in fixed time windows (e.g., 12:00:00–12:01:00)
- **Pro:** Simple, low memory. **Con:** Boundary problem — 2x burst at window edges.

### Sliding Window Log
- Store timestamp of each request; count entries in last N seconds
- **Pro:** Precise. **Con:** High memory (stores every timestamp).

### Sliding Window Counter (Best Trade-off)
- Combine current window count + weighted previous window count
- Formula: `count = current_count + prev_count × overlap_percentage`
- **Pro:** Smooth, low memory. **Con:** Approximate (but within 0.003% error).

### Redis Implementation (Sliding Window)

```
-- Lua script for atomic check-and-increment
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local current = redis.call('INCR', key)
if current == 1 then
    redis.call('EXPIRE', key, window)
end
if current > limit then
    return 0  -- rejected
end
return 1  -- allowed
```

### Race Conditions in Distributed Systems

**Problem:** Two servers read count=99 (limit=100), both increment → count=101.

**Solutions:**
1. **Lua scripts** — Atomic read+increment in Redis (preferred)
2. **Redis INCR** — Atomic by nature, check after increment
3. **Sorted sets** — Use ZRANGEBYSCORE for sliding window (more memory)

---

## Step 7: Bottlenecks & Scaling

| Bottleneck | Solution |
|-----------|----------|
| Redis single point of failure | Redis Cluster with replicas |
| Network latency to Redis | Local in-memory cache with sync |
| Hot keys (one user hammering) | Already handled — one key per user |
| Rate limiter adds latency | Fail-open if Redis unreachable |
| Rule changes propagation | Pub/sub to notify all gateways |

**Fail-open vs fail-closed:**
- Fail-open: If Redis is down, allow all traffic (availability over protection)
- Fail-closed: If Redis is down, reject all traffic (protection over availability)
- Most systems choose fail-open — brief unprotected window is better than total outage.

---

## Key Talking Points

- Sliding window counter is the best balance of accuracy and memory
- Lua scripts in Redis solve the race condition atomically
- Fail-open is the standard choice for rate limiters
- Rate limit headers help clients self-throttle
- Token bucket is best when you want to allow controlled bursts

---

## Common Mistakes

- Using fixed window without acknowledging the boundary burst problem
- Forgetting race conditions in distributed counting
- Not discussing what happens when Redis is unavailable
- Implementing rate limiting per-server instead of globally (user hits different servers)
- Over-engineering with complex distributed consensus for a counter

---

[← URL Shortener](./chapter-01-url-shortener.md) | [Next: Chat System →](./chapter-03-chat.md)

# Chapter 1: Design a URL Shortener (bit.ly)

[← Overview](./chapter-00-overview.md) | [Next: Rate Limiter →](./chapter-02-rate-limiter.md)

---

## The Question

> "Design a URL shortening service like bit.ly. Users paste a long URL and get a short link. When someone clicks the short link, they're redirected to the original URL. We also want basic analytics — how many times each link was clicked."

---

## Step 1: Requirements & Scope

**Functional:**
- Shorten a long URL → short URL
- Redirect short URL → original URL (301/302)
- Custom aliases (optional)
- Link expiration (optional)
- Click analytics (count, timestamp, geo)

**Non-functional:**
- 100M URLs created per month
- 10:1 read-to-write ratio → 1B redirects/month
- Low latency redirects (<100ms)
- High availability (redirects must never fail)
- Eventual consistency is acceptable

---

## Step 2: Estimation

| Metric | Calculation | Result |
|--------|-------------|--------|
| Write QPS | 100M / (30 × 86400) | ~40 writes/sec |
| Read QPS | 40 × 10 | ~400 reads/sec |
| Peak QPS | 400 × 3 | ~1,200 reads/sec |
| Storage (5 years) | 100M × 12 × 5 × 1KB | ~6 TB |
| Cache (20% hot URLs) | 1B/month × 0.2 × 1KB / 30 | ~70 GB |

Short URL length: 7 characters in Base62 = 62^7 = ~3.5 trillion combinations. More than enough.

---

## Step 3: API Design

```
POST /api/v1/shorten
  Body: { "long_url": "https://...", "custom_alias": "my-link", "ttl": 3600 }
  Response: { "short_url": "https://short.ly/aB3x9Kz" }

GET /{short_code}
  Response: 301 Redirect to original URL

GET /api/v1/stats/{short_code}
  Response: { "clicks": 14523, "created_at": "...", "last_clicked": "..." }
```

---

## Step 4: Data Model

**URL Table (NoSQL — DynamoDB or Cassandra for write throughput):**

| Field | Type |
|-------|------|
| short_code (PK) | VARCHAR(7) |
| long_url | TEXT |
| user_id | VARCHAR |
| created_at | TIMESTAMP |
| expires_at | TIMESTAMP |
| click_count | INT |

**Why NoSQL?** Simple key-value lookups, no complex joins, high write throughput, easy horizontal scaling.

---

## Step 5: High-Level Architecture

```
┌──────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────┐
│  Client  │────▶│ Load Balancer│────▶│  App Server │────▶│ Database │
└──────────┘     └──────────────┘     └─────────────┘     └──────────┘
                                            │                    ▲
                                            ▼                    │
                                      ┌──────────┐              │
                                      │  Cache   │──────────────┘
                                      │ (Redis)  │
                                      └──────────┘
                                            │
                                            ▼
                                      ┌──────────────┐
                                      │  Analytics   │
                                      │  (Kafka →    │
                                      │   warehouse) │
                                      └──────────────┘
```

**Write path:** Client → App Server → Generate short code → Write to DB
**Read path:** Client → App Server → Check Cache → (miss) → Read DB → Cache → Redirect

---

## Step 6: Deep Dive — Short Code Generation

**Option A: Base62 Encoding of Auto-Increment ID**
- Use a distributed ID generator (Snowflake-style)
- Convert numeric ID to Base62 string
- Pro: No collisions. Con: Predictable/sequential.

**Option B: MD5/SHA256 Hash + Truncate**
- Hash the long URL, take first 7 chars of Base62-encoded hash
- Pro: Same URL → same short code (dedup). Con: Collisions possible.
- Handle collisions: append counter, rehash, or check-and-retry.

**Option C: Pre-generated Key Service**
- Background worker pre-generates unused keys in a pool
- App server grabs a key from the pool on each request
- Pro: Fast, no collision. Con: Extra service to maintain.

**Cache strategy:**
- Cache hot URLs in Redis (LRU eviction)
- 80/20 rule: 20% of URLs get 80% of traffic
- Cache ~70 GB covers most hot URLs

---

## Step 7: Bottlenecks & Scaling

| Bottleneck | Solution |
|-----------|----------|
| DB write throughput | Shard by short_code hash |
| Hot URLs overwhelming one shard | Cache layer absorbs reads |
| Single point of failure | Multi-region replication |
| Analytics slowing writes | Async via Kafka, separate analytics DB |
| Key generation contention | Pre-generated key ranges per server |

**301 vs 302 redirect?**
- 301 (permanent): Browser caches, reduces server load, but loses analytics
- 302 (temporary): Every click hits server, better for analytics

---

## Key Talking Points

- Base62 with 7 chars gives 3.5T combinations — more than enough
- Read-heavy workload → caching is critical
- Separate analytics from the hot path (async processing)
- 302 redirects if analytics matter, 301 if reducing load matters
- Pre-generated keys avoid collision handling entirely

---

## Common Mistakes

- Using MD5 without a collision resolution strategy
- Forgetting that 301 redirects bypass your server (no analytics)
- Not estimating storage — "just use a database" without sizing
- Over-complicating the hash function when a counter + Base62 works
- Ignoring cache invalidation for expired URLs

---

[← Overview](./chapter-00-overview.md) | [Next: Rate Limiter →](./chapter-02-rate-limiter.md)

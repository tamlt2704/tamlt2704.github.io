# Chapter 35: System Design Interview — The Complete Guide

## What you'll learn

- The 6-step framework for any system design interview (45 minutes)
- Back-of-envelope estimation (QPS, storage, bandwidth)
- Core building blocks: load balancers, caches, databases, queues, CDNs
- Scaling patterns: horizontal scaling, sharding, replication, partitioning
- 10 complete system design walkthroughs (Easy → Hard)
- Common mistakes and how to avoid them
- How to communicate your thinking (the interviewer wants to SEE your process)

---

## PART 1: The Framework

## 35.1 The 6-step structure (45 minutes)

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: REQUIREMENTS (5 min)                                     │
│   "What exactly are we building?"                                │
│   → Functional requirements (features)                           │
│   → Non-functional requirements (scale, latency, consistency)    │
│   → Out of scope (what we're NOT building)                       │
├─────────────────────────────────────────────────────────────────┤
│ Step 2: ESTIMATION (5 min)                                       │
│   "How big is this?"                                             │
│   → DAU, QPS, storage, bandwidth                                 │
│   → Read/write ratio                                             │
│   → Peak vs average                                              │
├─────────────────────────────────────────────────────────────────┤
│ Step 3: HIGH-LEVEL DESIGN (10 min)                               │
│   "What are the main components?"                                │
│   → API design (endpoints)                                       │
│   → Core components (boxes and arrows)                           │
│   → Data flow (happy path)                                       │
├─────────────────────────────────────────────────────────────────┤
│ Step 4: DETAILED DESIGN (15 min)                                 │
│   "Let's dive deep into 2-3 components"                          │
│   → Database schema + choice                                     │
│   → Key algorithms                                               │
│   → Caching strategy                                             │
│   → Data partitioning                                            │
├─────────────────────────────────────────────────────────────────┤
│ Step 5: BOTTLENECKS & SCALING (5 min)                            │
│   "What breaks at 10× scale?"                                    │
│   → Single points of failure                                     │
│   → Horizontal scaling plan                                      │
│   → Monitoring and alerting                                      │
├─────────────────────────────────────────────────────────────────┤
│ Step 6: WRAP-UP (5 min)                                          │
│   "Summary and extensions"                                       │
│   → Recap key decisions                                          │
│   → Tradeoffs acknowledged                                       │
│   → Future improvements                                          │
└─────────────────────────────────────────────────────────────────┘
```

## 35.2 What the interviewer is evaluating

| Signal | What they look for |
|--------|-------------------|
| **Communication** | Do you explain your thinking? Ask clarifying questions? |
| **Structured approach** | Do you follow a logical process or jump around randomly? |
| **Tradeoff discussion** | Can you articulate WHY you chose X over Y? |
| **Technical depth** | Can you go deep on the components that matter? |
| **Scope management** | Do you focus on what matters or get lost in details? |
| **Practical awareness** | Do you know real-world constraints (latency, cost, failure modes)? |

> **The biggest mistake:** Jumping straight into the solution without clarifying requirements. The interviewer deliberately gives a vague prompt ("Design Twitter"). You MUST ask questions first.

## 35.3 How to ask requirements questions

```
Interviewer: "Design a URL shortener."

You: "I have a few clarifying questions:

Functional:
- Should it support custom short URLs (vanity URLs)?
- Do we need analytics (click counts, geographic distribution)?
- Should URLs expire, or are they permanent?
- Is there a rate limit on creation?

Non-functional:
- What's our expected scale? (I'm thinking something like bit.ly — millions of URLs?)
- What latency target for redirects? (I'd assume <100ms for the redirect)
- Do we need 99.99% availability? (URL shorteners should be very reliable)
- How long do we retain data?

Let me also state what I think is OUT of scope:
- User authentication (assume anonymous creation for now)
- UI/frontend (focus on the backend system)
- Spam detection (mention at the end as an extension)

Does this align with what you had in mind?"
```

---

## PART 2: Estimation

## 35.4 Back-of-envelope numbers

**Latency numbers (memorise these):**
```
L1 cache reference:                    0.5 ns
RAM reference:                         100 ns
Read 1 MB sequentially from RAM:       250 μs
SSD random read:                       100 μs
Read 1 MB sequentially from SSD:       1 ms
Disk seek (HDD):                       10 ms
Read 1 MB sequentially from HDD:       20 ms
Send packet US → EU → US:              150 ms
```

**Throughput:**
```
Network (1 Gbps):                      125 MB/s
SSD sequential:                        500 MB/s
HDD sequential:                        100 MB/s
```

**Storage rules of thumb:**
```
1 character (ASCII):                   1 byte
1 character (UTF-8 avg):               2-3 bytes
1 tweet/short text (280 chars + meta): ~1 KB
1 image (compressed):                  200 KB - 2 MB
1 minute of video (720p):              ~50 MB
1 minute of video (1080p):             ~150 MB
```

**Scale:**
```
1 million = 10⁶
1 billion = 10⁹
1 day = 86,400 seconds ≈ 10⁵
1 month ≈ 2.5 × 10⁶ seconds
```

## 35.5 Estimation template

```
Given: 100M DAU (Daily Active Users)

QPS (Queries Per Second):
  Avg = 100M × (requests per user per day) / 86400
  Example: 100M × 10 requests / 100K seconds = 10,000 QPS average
  Peak = 2-3× average = 20,000 - 30,000 QPS

Storage (per year):
  New data per day = DAU × (data per user per day)
  Example: 100M × 1 KB = 100 GB/day
  Per year: 100 GB × 365 = ~36 TB/year

Bandwidth:
  Outgoing = QPS × response size
  Example: 10,000 QPS × 5 KB = 50 MB/s

Cache size:
  20% of daily data covers 80% of reads (Pareto principle)
  Cache: 0.2 × 100 GB = 20 GB (fits in one Redis node)
```

## 35.6 Practice: URL shortener estimation

```
Assumptions:
- 100M URLs created per month
- Read-heavy: 100:1 read/write ratio
- Average URL stored: 500 bytes (short URL + long URL + metadata)
- Store for 5 years

Write QPS:
  100M / (30 days × 86400) ≈ 40 QPS (low — writes are cheap)

Read QPS:
  40 × 100 = 4,000 QPS (moderate)
  Peak: ~12,000 QPS

Storage (5 years):
  100M × 12 months × 5 years = 6 billion URLs
  6B × 500 bytes = 3 TB

Cache:
  20% of 4,000 QPS = 800 hot URLs
  Cache 20% of daily reads: ~200 GB of URL mappings in Redis
```

---

## PART 3: Building Blocks

## 35.7 Architecture patterns — quick reference

```
                    ┌─────────┐
Users ──────────────►   CDN   │ (static assets: JS, CSS, images)
                    └────┬────┘
                         │ dynamic requests
                    ┌────▼────┐
                    │   LB    │ (load balancer)
                    └────┬────┘
              ┌──────────┼──────────┐
              ▼          ▼          ▼
         ┌────────┐ ┌────────┐ ┌────────┐
         │ App 1  │ │ App 2  │ │ App 3  │  (stateless app servers)
         └───┬────┘ └───┬────┘ └───┬────┘
             │           │           │
         ┌───▼───────────▼───────────▼───┐
         │           CACHE (Redis)        │  (hot data, sessions)
         └───────────────┬────────────────┘
                         │ cache miss
         ┌───────────────▼────────────────┐
         │      DATABASE (Primary)        │  (writes)
         │          │ replication          │
         │    ┌─────┼─────┐               │
         │    ▼     ▼     ▼               │
         │ Replica Replica Replica        │  (reads)
         └────────────────────────────────┘
```

## 35.8 Component deep-dive

### Load Balancer

```
Algorithms:
- Round Robin:           requests go to servers in order (1, 2, 3, 1, 2, 3...)
- Weighted Round Robin:  more powerful servers get more traffic
- Least Connections:     send to server with fewest active connections
- IP Hash:              same client always goes to same server (sticky sessions)
- Consistent Hashing:   for distributed caches (minimise redistribution on scale)

Layers:
- L4 (Transport):  routes by IP/port (fast, can't inspect HTTP)
- L7 (Application): routes by URL path, headers, cookies (flexible, slower)

Products: AWS ALB/NLB, nginx, HAProxy, Cloudflare
```

### Caching

```
Cache strategies:
┌─────────────────────────────────────────────────────────────────┐
│ Cache-Aside (Lazy Loading):                                      │
│   Read: check cache → HIT: return │ MISS: query DB, store, return│
│   Write: update DB, invalidate cache                             │
│   Pro: only caches what's needed. Con: cache miss = slow         │
├─────────────────────────────────────────────────────────────────┤
│ Write-Through:                                                   │
│   Write: update cache AND DB simultaneously                      │
│   Pro: cache always consistent. Con: write latency, caches unused│
├─────────────────────────────────────────────────────────────────┤
│ Write-Behind (Write-Back):                                       │
│   Write: update cache only, async flush to DB                    │
│   Pro: very fast writes. Con: data loss if cache crashes         │
├─────────────────────────────────────────────────────────────────┤
│ Read-Through:                                                    │
│   Cache itself fetches from DB on miss (app doesn't know about DB)│
│   Pro: simple app code. Con: cold start latency                  │
└─────────────────────────────────────────────────────────────────┘

Eviction policies:
- LRU (Least Recently Used) — most common
- LFU (Least Frequently Used) — for skewed distributions
- TTL (Time-To-Live) — expire after N seconds

Products: Redis, Memcached, CDN edge caches
```

### Database choices

```
┌──────────────────────────────────────────────────────────────────┐
│ SQL (PostgreSQL, MySQL)                                           │
│ ✓ ACID transactions (banking, orders)                            │
│ ✓ Complex queries (JOINs, aggregations)                          │
│ ✓ Strong consistency                                             │
│ ✗ Harder to scale writes (sharding is complex)                   │
│ Best for: user data, financial transactions, relational data      │
├──────────────────────────────────────────────────────────────────┤
│ NoSQL — Document (MongoDB, DynamoDB)                             │
│ ✓ Flexible schema (evolving data models)                         │
│ ✓ Horizontal scaling built-in                                    │
│ ✓ Good for hierarchical/nested data                              │
│ ✗ No JOINs (denormalization required)                            │
│ Best for: product catalogs, user profiles, content management    │
├──────────────────────────────────────────────────────────────────┤
│ NoSQL — Wide Column (Cassandra, HBase)                           │
│ ✓ Extreme write throughput (millions/sec)                        │
│ ✓ Time-series data                                               │
│ ✗ Limited query patterns (must design around partition key)       │
│ Best for: messaging, IoT, event logs, analytics                  │
├──────────────────────────────────────────────────────────────────┤
│ NoSQL — Key-Value (Redis, DynamoDB)                              │
│ ✓ Sub-millisecond latency                                        │
│ ✓ Simple get/set operations                                      │
│ ✗ No complex queries                                             │
│ Best for: caching, sessions, rate limiting, leaderboards          │
├──────────────────────────────────────────────────────────────────┤
│ Search Engine (Elasticsearch, Solr)                               │
│ ✓ Full-text search, fuzzy matching                               │
│ ✓ Faceted search, autocomplete                                   │
│ ✗ Not a primary data store                                       │
│ Best for: search features, log analysis                           │
└──────────────────────────────────────────────────────────────────┘
```

### Message Queues

```
Use when:
- Decouple producers from consumers
- Handle traffic spikes (buffer)
- Ensure reliable delivery (retry on failure)
- Async processing (don't block the user)

Patterns:
- Point-to-point: one message → one consumer (task queue)
- Pub/Sub: one message → many consumers (notifications)
- Event streaming: ordered, replayable log (Kafka)

Products: Kafka (streaming), RabbitMQ (task queue), AWS SQS (managed queue)
```

### CDN

```
Put static content close to users:
- JavaScript, CSS, images, videos
- Reduces latency from 200ms (origin) to 20ms (edge)
- Offloads traffic from origin servers
- Products: Cloudflare, AWS CloudFront, Akamai, Fastly
```

---

## PART 4: Scaling Patterns

## 35.9 Horizontal vs Vertical scaling

```
Vertical (scale UP):                Horizontal (scale OUT):
┌───────────────────┐              ┌─────┐ ┌─────┐ ┌─────┐
│                   │              │ App │ │ App │ │ App │
│   BIGGER SERVER   │              └─────┘ └─────┘ └─────┘
│   (more CPU/RAM)  │              ┌─────┐ ┌─────┐ ┌─────┐
│                   │              │ App │ │ App │ │ App │
└───────────────────┘              └─────┘ └─────┘ └─────┘

Limit: hardware ceiling              Limit: theoretically unlimited
Cost: exponential                    Cost: linear
Downtime to upgrade: yes             Downtime: no (add/remove nodes live)
```

**Rule:** Always design for horizontal scaling. Vertical has hard limits.

## 35.10 Database scaling patterns

```
1. READ REPLICAS (scale reads):
   Write → Primary → replicate → Replica 1, Replica 2, Replica 3
   Reads distributed across replicas (90% of traffic is reads)

2. SHARDING (scale writes):
   Users A-M → Shard 1
   Users N-Z → Shard 2
   (or hash-based: shard = hash(user_id) % num_shards)

3. CONSISTENT HASHING (minimise redistribution):
   When adding/removing shards, only 1/N of keys need to move
   (vs rehashing everything with simple modulo)

4. CQRS (separate read/write models):
   Write: normalised DB (fast writes, ACID)
   Read: denormalised DB or search engine (fast queries)
   Sync: event stream from write → read store
```

## 35.11 Consistency models

| Model | Guarantee | Latency | Use case |
|-------|-----------|---------|----------|
| **Strong consistency** | All reads see latest write | Higher (wait for all replicas) | Banking, inventory |
| **Eventual consistency** | Reads MAY be stale temporarily | Lower (return immediately) | Social feeds, likes |
| **Causal consistency** | Reads respect cause-effect order | Moderate | Chat messages |

**CAP Theorem:** In a network partition, you choose:
- **CP** (Consistency + Partition tolerance): reject requests rather than serve stale data (banking)
- **AP** (Availability + Partition tolerance): serve potentially stale data rather than reject (social media)

You CANNOT have all three simultaneously during a partition.



---

## PART 5: System Design Walkthroughs

## 35.12 Design a URL Shortener (Easy)

```
Requirements:
- Shorten long URLs → 7-char codes (e.g., short.ly/abc1234)
- Redirect short → original (301)
- Analytics: click count per URL
- Scale: 100M URLs/month, 10B redirects/month

Estimation:
- Write: 100M / 2.5M sec ≈ 40 QPS
- Read: 40 × 100 = 4,000 QPS (peak: 12K)
- Storage: 6B URLs × 500B = 3 TB over 5 years
- Cache: 20% of daily unique URLs ≈ 200 GB Redis

High-Level Design:
  Client → LB → App Server → Cache (Redis) → DB (PostgreSQL/DynamoDB)

API:
  POST /api/shorten  { "url": "https://long..." } → { "short": "abc1234" }
  GET  /abc1234      → 301 Redirect to original URL

Key Design Decisions:

1. ID Generation:
   - Auto-increment ID → Base62 encode → 7-char code
   - Counter service (centralized) or Snowflake ID (distributed)
   - Base62: [a-z, A-Z, 0-9] = 62 chars, 7 chars = 62⁷ = 3.5 trillion combinations

2. Database:
   - Table: short_code (PK) | original_url | created_at | click_count
   - NoSQL (DynamoDB): key-value lookup is the primary pattern
   - SQL (PostgreSQL): if analytics queries are complex

3. Read Path (optimized):
   Client → LB → App → Redis (short→original) → 301 Redirect
   Cache hit ratio: 80%+ (popular URLs are hit repeatedly)

4. Analytics:
   - Increment counter async (don't block redirect)
   - Write to Kafka → analytics service → aggregate in ClickHouse/Druid
```

## 35.13 Design a Rate Limiter (Easy)

```
Requirements:
- Limit requests per user per time window
- Support multiple rules (100 req/min, 1000 req/hour)
- Low latency (< 1ms overhead per request)
- Distributed (works across multiple app servers)

Algorithms:

1. Fixed Window:
   Key: user_123:minute:2024-01-01T10:05
   Increment counter, reject if > limit
   Pro: simple. Con: burst at window boundary (200 in 2 seconds spanning 2 windows)

2. Sliding Window Log:
   Store timestamp of every request in sorted set
   Count requests in [now - window, now]
   Pro: accurate. Con: memory-heavy (store every timestamp)

3. Token Bucket (RECOMMENDED):
   Bucket holds N tokens, refills at R tokens/second
   Each request costs 1 token. Empty bucket → reject.
   Pro: allows bursts up to bucket size, smooth rate. Con: slightly more state.

4. Sliding Window Counter:
   Weighted average of current + previous window
   Requests ≈ (prev_count × overlap%) + current_count
   Pro: low memory (2 counters), good accuracy. Con: approximation.

Implementation (Redis + Token Bucket):
  Key: rate_limit:{user_id}
  Value: { tokens: N, last_refill: timestamp }
  On request:
    1. Calculate tokens to add since last_refill
    2. tokens = min(tokens + refill_amount, max_tokens)
    3. If tokens > 0: allow, decrement. Else: reject (429).
  Use Redis Lua script for atomicity (read-modify-write in one command)

Response headers:
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 73
  X-RateLimit-Reset: 1609459200 (Unix timestamp)
```

## 35.14 Design a Chat System (Medium)

```
Requirements:
- 1:1 messaging and group chat (up to 500 members)
- Online/offline status
- Message history (persistent)
- Delivered/read receipts
- 50M DAU

Estimation:
- Messages/day: 50M users × 40 messages = 2B messages/day
- QPS: 2B / 86400 ≈ 23,000 msg/sec (peak: 70K)
- Storage: 2B × 200 bytes = 400 GB/day (146 TB/year)

High-Level:
  Client ←→ WebSocket Server ←→ Message Queue ←→ Chat Service ←→ DB
                                                  ↕
                                           Presence Service (Redis)

Key Decisions:

1. Real-time delivery: WebSocket (persistent bidirectional connection)
   - NOT HTTP polling (too many requests)
   - NOT long polling (OK but WebSocket is cleaner)
   - WebSocket servers: stateful (session affinity needed)

2. Message storage: Cassandra or ScyllaDB
   - Partition key: chat_id
   - Clustering key: timestamp (messages ordered by time)
   - Write-heavy, time-series pattern → Cassandra is ideal

3. Message delivery:
   Sender → WebSocket → Message Service → check if recipient online
   - Online: push via recipient's WebSocket connection
   - Offline: store in message queue, deliver when they reconnect

4. Group chat fan-out:
   - Small groups (< 50): fan-out on write (push to all members' queues)
   - Large groups (50-500): fan-out on read (pull when user opens group)

5. Online presence:
   - Redis with heartbeat (user sends heartbeat every 30s)
   - TTL on presence key: 60s (missed 2 heartbeats → offline)
   - Subscribe to friends' status changes via Pub/Sub

6. Message ordering:
   - Per-conversation ordering (not global)
   - Sequence number per conversation (monotonic)
   - Server assigns sequence number (not client — unreliable clocks)
```

## 35.15 Design a News Feed (Medium-Hard)

```
Requirements:
- User posts content (text, images, videos)
- User sees feed of posts from people they follow
- Sorted by relevance (not just chronological)
- 300M DAU, avg user follows 200 people
- Feed loads in < 500ms

The Core Problem: Fan-out

Two approaches:

1. Fan-out on WRITE (push model):
   User posts → immediately write to ALL followers' feed caches
   
   Pro: feed read is O(1) — pre-computed, instant
   Con: celebrity problem (Beyoncé has 100M followers → 100M writes per post)
   
2. Fan-out on READ (pull model):
   User opens feed → query all followed users' posts → merge → rank → return
   
   Pro: no celebrity problem (write is O(1))
   Con: feed read is slow (query 200 users' posts, merge, rank)

3. HYBRID (what Facebook/Twitter actually does):
   - Regular users (< 10K followers): fan-out on write
   - Celebrities (> 10K followers): fan-out on read
   - When user opens feed: merge pre-computed feed + celebrity posts

Architecture:
  Post Service → Fan-out Service → Feed Cache (per user, Redis sorted set)
                                 → Feed Read Service → merge cached + celebrity posts
                                                     → Ranking Service (ML model)

Feed storage:
  Redis sorted set per user: { post_id: timestamp }
  Keep last 500 posts per user feed (evict oldest)
  
  Feed read:
  1. Get user's pre-computed feed from Redis (instant)
  2. Fetch celebrity posts in real-time (parallel queries)
  3. Merge, rank, paginate, return top 20

Ranking:
  Simple: chronological (newest first)
  Better: engagement prediction (ML model predicts P(like), P(comment), P(share))
  Factors: recency, relationship strength, content type, engagement history
```

## 35.16 Design YouTube/Video Streaming (Hard)

```
Requirements:
- Upload videos (up to 1 hour, any resolution)
- Stream videos to millions of concurrent viewers
- Adaptive bitrate (quality adjusts to network speed)
- 2B DAU, 500M videos watched/day

Key Challenges:
1. Upload: accept large files reliably (resume on failure)
2. Processing: transcode to multiple resolutions/formats
3. Storage: petabytes of video data
4. Delivery: stream to millions globally with low latency

Architecture:

  Upload → API → Object Store (S3) → Transcode Pipeline → CDN
                                       ↓
                              Multiple resolutions:
                              - 1080p, 720p, 480p, 360p
                              - HLS/DASH segments (10s chunks)

  Watch → CDN edge → (cache miss) → Origin (S3)

Key Decisions:

1. Upload (resumable):
   - Chunked upload (5MB chunks)
   - Each chunk has a sequence number
   - On failure: resume from last successful chunk
   - Direct upload to S3 (signed URL) — bypass app servers

2. Transcoding pipeline:
   - DAG (Directed Acyclic Graph) of tasks:
     Video → Split into segments → Transcode each (parallel) → Merge → Upload to CDN
   - Horizontal scaling: 100s of transcode workers
   - Priority queue: popular creator videos processed first
   - Message queue (Kafka/SQS) for job distribution

3. Streaming:
   - HLS (HTTP Live Streaming) or DASH
   - Video split into 2-10 second segments
   - Manifest file (.m3u8) lists all segments + quality levels
   - Client requests segments one by one (adaptive: picks quality per segment)
   - CDN caches popular segments (90%+ cache hit rate)

4. Storage:
   - Raw uploads: S3 (hot storage initially, move to Glacier after 30 days)
   - Transcoded segments: S3 + CDN
   - Metadata (title, description, tags): PostgreSQL/DynamoDB
   - Comments: Cassandra (write-heavy, time-ordered)
```

## 35.17 Design a Distributed Cache (Hard)

```
Requirements:
- Key-value store (GET/SET/DELETE)
- Sub-millisecond latency
- Support billions of keys
- Handle node failures gracefully
- Scale horizontally (add nodes without downtime)

Architecture: Distributed hash ring

  ┌─────────────────────────────────┐
  │        Hash Ring                │
  │     Node A                      │
  │    ╱     ╲                      │
  │  Node D   Node B               │
  │    ╲     ╱                      │
  │     Node C                      │
  └─────────────────────────────────┘

Key decisions:

1. Partitioning: Consistent Hashing
   - Hash(key) → position on ring → assigned to next clockwise node
   - Adding a node: only 1/N of keys redistribute (not ALL)
   - Virtual nodes: each physical node → multiple positions on ring (even distribution)

2. Replication:
   - Each key replicated to N nodes (N=3 typical)
   - Write to primary + 2 replicas
   - Quorum: W + R > N for strong consistency
     - W=2, R=2, N=3: strong consistency (overlap guaranteed)
     - W=1, R=1, N=3: high availability (fast but possibly stale)

3. Failure handling:
   - Gossip protocol: nodes detect failures by heartbeat
   - Hinted handoff: if replica is down, temp node holds writes, forwards when node recovers
   - Anti-entropy: Merkle trees detect inconsistencies between replicas

4. Eviction:
   - LRU per node (evict least recently used when memory full)
   - TTL on keys (auto-expire)

5. Client interaction:
   - Client knows the hash ring topology
   - Routes directly to correct node (no central coordinator)
   - Library handles retries, failover to replicas
```

## 35.18 More designs (brief outlines)

### Design Twitter Search
```
- Inverted index: word → [tweet_ids]
- Elasticsearch cluster (sharded by time or hash)
- Real-time indexing: Kafka → indexing workers → ES
- Query: parse, expand, search multiple shards, merge, rank, return
```

### Design Notification System
```
- Multi-channel: push, SMS, email
- Priority queue per channel
- Rate limiting (don't spam users)
- Preference service (user opts in/out per type)
- Template engine (personalise messages)
- Analytics (delivery rate, open rate)
```

### Design Google Maps
```
- Tile-based map rendering (pre-rendered image tiles at each zoom level)
- Routing: Dijkstra/A* on road graph (pre-computed for highways: contraction hierarchies)
- Real-time traffic: aggregate GPS data from drivers → update edge weights
- ETA prediction: ML model on historical + real-time data
- Geospatial index: QuadTree or Geohash for nearby places
```

---

## PART 6: Tradeoffs & Communication

## 35.19 Key tradeoffs to discuss

| Tradeoff | When to pick A | When to pick B |
|----------|---------------|---------------|
| **Consistency vs Availability** | A: Banking, inventory (correct > fast) | B: Social feeds, likes (fast > correct) |
| **SQL vs NoSQL** | A: Complex queries, transactions, JOINs | B: Horizontal scale, flexible schema, simple lookups |
| **Push vs Pull** | A: Real-time needed, few subscribers | B: Many subscribers, batch OK |
| **Monolith vs Microservices** | A: Small team, MVP, speed of development | B: Large team, independent deployment, scale specific components |
| **Normalize vs Denormalize** | A: Write-heavy, storage matters, consistency | B: Read-heavy, latency matters, scale |
| **Sync vs Async** | A: User needs immediate result (payment) | B: Result can wait (email, video processing) |
| **Cache vs No cache** | A: Read-heavy, data changes slowly, latency matters | B: Write-heavy, strong consistency needed, data always fresh |
| **Single leader vs Multi-leader** | A: Strong consistency, simple conflict resolution | B: Multi-region availability, low write latency globally |

## 35.20 Communication tips

**1. Think out loud.** The interviewer can't read your mind. Narrate your reasoning:
- "I'm choosing Cassandra here because we have a write-heavy time-series pattern..."
- "The tradeoff is consistency — we'll be eventually consistent, which is acceptable for a social feed..."

**2. Draw as you talk.** Boxes and arrows on a whiteboard (or shared doc). Label everything.

**3. Ask "does this make sense so far?" periodically.** Gives the interviewer a chance to redirect you if needed.

**4. Don't over-engineer.** Start simple, add complexity only when the scale demands it:
- "For 1,000 users, a single PostgreSQL handles this easily."
- "At 10M users, we need read replicas and caching."
- "At 100M users, we need sharding and a CDN."

**5. Acknowledge what you're NOT solving:**
- "I'm skipping auth for now — it's a standard OAuth2 flow."
- "Monitoring is important but I'll mention it at the end rather than design it in detail."

## 35.21 Common mistakes

| Mistake | Fix |
|---------|-----|
| Jumping to solution without requirements | ALWAYS spend 5 min on requirements first |
| Designing for Google scale on a startup problem | Match complexity to stated scale |
| Going too deep on one component | Budget time: 15 min for detailed design, touch 2-3 components |
| No numbers (estimation) | Always do back-of-envelope: QPS, storage, bandwidth |
| No tradeoff discussion | Every decision has an alternative — state why you chose this one |
| Ignoring failure modes | "What happens when X crashes?" should be part of your design |
| Overusing buzzwords without understanding | Only mention technologies you can explain in depth |
| Not drawing a diagram | Visual > verbal for architecture (always draw) |

---

## Summary

✅ The 6-step framework: Requirements → Estimation → High-level → Detailed → Bottlenecks → Wrap-up
✅ Estimation: QPS, storage, bandwidth from DAU and per-user activity
✅ Building blocks: LB, cache (4 strategies), databases (SQL/NoSQL/search), queues, CDN
✅ Scaling: horizontal > vertical, read replicas, sharding, consistent hashing, CQRS
✅ Consistency: strong vs eventual, CAP theorem (CP vs AP)
✅ 6 full walkthroughs: URL Shortener, Rate Limiter, Chat, News Feed, Video Streaming, Distributed Cache
✅ 3 brief outlines: Twitter Search, Notification System, Google Maps
✅ Communication: think out loud, draw diagrams, discuss tradeoffs, acknowledge simplifications

## Key takeaways

**System design is a conversation, not an exam.** There's no single correct answer. The interviewer wants to see: structured thinking, tradeoff awareness, practical knowledge, and the ability to adapt when they push back or ask "what if we need 10× more scale?"

**Start simple, then scale.** "A single server handles this at our current scale. Here's how I'd evolve it as we grow..." is better than immediately drawing 50 microservices.

**Estimation gives you credibility.** When you say "we need ~4,000 QPS for reads, which a single Redis node handles comfortably" — you've shown you can think quantitatively, not just architecturally.

**Every design is a set of tradeoffs.** The interviewer's follow-up will almost always be "what are the downsides?" Have the answer ready before they ask.

---

→ [Back to Chapter 34: Linear Programming](./34-LINEAR-PROGRAMMING.md)

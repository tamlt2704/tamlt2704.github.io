# Chapter 4: Design a News Feed (Twitter/Instagram)

[← Chat System](./chapter-03-chat.md) | [Next: File Storage →](./chapter-05-storage.md)

---

## The Question

> "Design the news feed system for a social media platform like Twitter or Instagram. When a user opens the app, they see a personalized feed of posts from people they follow, ranked by relevance. The system needs to handle users with millions of followers."

---

## Step 1: Requirements & Scope

**Functional:**
- Users create posts (text, images, video)
- Users follow other users
- Feed shows posts from followed users, ranked
- Support pagination (infinite scroll)
- Near real-time: new posts appear within seconds

**Non-functional:**
- 300M DAU, average user checks feed 10x/day
- Average user follows 200 people
- Feed generation latency <500ms
- High availability — feed must always load
- Eventual consistency is acceptable (few seconds delay OK)

---

## Step 2: Estimation

| Metric | Calculation | Result |
|--------|-------------|--------|
| Feed requests/day | 300M × 10 | 3B/day |
| Feed QPS | 3B / 86400 | ~35,000 req/sec |
| New posts/day | 300M × 2 posts avg | 600M posts/day |
| Post writes/sec | 600M / 86400 | ~7,000 writes/sec |
| Storage/day | 600M × 2KB avg | ~1.2 TB/day |

---

## Step 3: API Design

```
POST /api/v1/posts
  Body: { "content": "Hello world", "media_ids": ["img_123"] }
  Response: { "post_id": "post_789", "created_at": "..." }

GET /api/v1/feed?page_token=xxx&limit=20
  Response: { "posts": [...], "next_page_token": "yyy" }

POST /api/v1/follow
  Body: { "target_user_id": "user_456" }
```

---

## Step 4: Data Model

**Posts (SQL or NoSQL):**

| Field | Type |
|-------|------|
| post_id (PK) | UUID |
| user_id | UUID |
| content | TEXT |
| media_urls | JSON |
| created_at | TIMESTAMP |
| like_count | INT |

**Feed Cache (Redis sorted set per user):**

```
Key:   feed:{user_id}
Value: Sorted set of post_ids scored by ranking_score
```

**Follow Graph (SQL or graph DB):**

| Field | Type |
|-------|------|
| follower_id | UUID |
| followee_id | UUID |
| created_at | TIMESTAMP |

---

## Step 5: High-Level Architecture

```
┌──────────┐     ┌──────────────┐     ┌─────────────────┐
│  Client  │────▶│ Load Balancer│────▶│  Feed Service   │
└──────────┘     └──────────────┘     └────────┬────────┘
                                               │
                         ┌─────────────────────┼──────────────────┐
                         ▼                     ▼                   ▼
                ┌──────────────┐     ┌──────────────┐    ┌──────────────┐
                │  Feed Cache  │     │  Post Store  │    │  Fan-out     │
                │  (Redis)     │     │  (DB)        │    │  Service     │
                └──────────────┘     └──────────────┘    └──────┬───────┘
                                                                │
                                                                ▼
                                                       ┌──────────────┐
                                                       │  Message     │
                                                       │  Queue       │
                                                       └──────────────┘
```

**Write path:** User posts → Fan-out service → Push post_id to followers' feed caches
**Read path:** User opens app → Feed service → Read from feed cache → Hydrate posts

---

## Step 6: Deep Dive — Fan-Out Strategies

### Fan-Out on Write (Push Model)

When a user publishes a post:
1. Look up all followers
2. Insert post_id into each follower's feed cache
3. Done at write time — feed reads are instant

**Pro:** Fast reads (pre-computed feed). **Con:** Slow writes for celebrities.

### Fan-Out on Read (Pull Model)

When a user opens their feed:
1. Look up all users they follow
2. Fetch recent posts from each
3. Merge and rank in real-time

**Pro:** No write amplification. **Con:** Slow reads, high compute per request.

### Hybrid Approach (The Answer)

- **Regular users** (< 10K followers): Fan-out on write
- **Celebrities** (> 10K followers): Fan-out on read

When building a feed:
1. Start with pre-computed feed from cache (push)
2. Merge in recent posts from followed celebrities (pull)
3. Apply ranking algorithm
4. Return top N posts

### The Celebrity Problem

A user with 50M followers posts → 50M cache writes. This is:
- Slow (minutes to propagate)
- Expensive (massive write amplification)
- Wasteful (most followers won't check feed soon)

Solution: Don't fan-out for celebrities. Pull their posts at read time.

### Ranking Algorithm

Simple scoring function:

```
score = affinity × recency × engagement

affinity   = how often viewer interacts with author (0-1)
recency    = time_decay(post_age)  // exponential decay
engagement = normalize(likes + comments + shares)
```

---

## Step 7: Bottlenecks & Scaling

| Bottleneck | Solution |
|-----------|----------|
| Celebrity posts (write amplification) | Hybrid: pull for celebrities |
| Feed cache memory | Keep only last 500 posts per user |
| Ranking computation | Pre-compute scores, update periodically |
| Cold start (new user) | Pull model until cache warms up |
| Stale feeds | Background refresh + real-time push for close friends |

**Cache invalidation:** When a post is deleted, remove from all follower caches (async, eventual consistency is fine — deleted post showing briefly is acceptable).

**Pagination:** Use cursor-based pagination (not offset). Cursor = last post's score/timestamp. Stable even as new posts arrive.

---

## Key Talking Points

- Hybrid fan-out is the industry standard (push for normal, pull for celebrities)
- The celebrity problem is THE key insight interviewers look for
- Ranking is a spectrum: chronological → simple scoring → ML models
- Feed cache in Redis sorted sets enables fast ranked retrieval
- Cursor-based pagination handles real-time content gracefully

---

## Common Mistakes

- Using only fan-out on write without addressing the celebrity problem
- Using only fan-out on read (too slow for 35K QPS)
- Ignoring ranking — "just show chronological" misses the point
- Not discussing cache size limits (can't store infinite feed)
- Using offset pagination (breaks with real-time inserts)
- Forgetting to handle the cold-start case for new users

---

[← Chat System](./chapter-03-chat.md) | [Next: File Storage →](./chapter-05-storage.md)

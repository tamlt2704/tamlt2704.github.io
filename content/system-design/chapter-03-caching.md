# Chapter 3: Caching Strategies

[← Chapter 2: Database](/blog/system-design/chapter-02-database) | [Chapter 4: Message Queues →](/blog/system-design/chapter-04-message-queues)

---

## Why Cache?

Databases are slow (milliseconds). Memory is fast (nanoseconds). Caching puts frequently accessed data closer to the consumer.

```
Without cache:
Client → Server → Database (10ms)

With cache:
Client → Server → Cache (0.5ms) ✓ hit
                → Database (10ms) ✗ miss → write to cache
```

**The numbers:**

- Redis GET: ~0.1-0.5ms
- PostgreSQL simple query: ~2-10ms
- PostgreSQL complex join: ~50-500ms
- External API call: ~100-2000ms

A cache with 90% hit rate means 90% of requests are 20x faster.

---

## Caching Layers

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ Browser  │──▶│   CDN    │──▶│  App     │──▶│  Redis   │──▶│ Database │
│  Cache   │   │  Cache   │   │  Cache   │   │  Cache   │   │          │
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
  HTTP cache    Static assets   In-process     Distributed    Source of
  headers       edge servers    (Caffeine)     shared cache   truth
```

| Layer               | What to Cache                               | TTL             | Example                       |
| ------------------- | ------------------------------------------- | --------------- | ----------------------------- |
| Browser             | Static assets, API responses                | Hours-days      | `Cache-Control: max-age=3600` |
| CDN                 | Images, CSS, JS, public pages               | Hours-days      | CloudFront, Cloudflare        |
| Application (local) | Hot objects, computed results               | Seconds-minutes | Caffeine, Guava cache         |
| Distributed (Redis) | Session data, DB query results, rate limits | Minutes-hours   | Redis, Memcached              |

---

## Cache Strategies

### 1. Cache-Aside (Lazy Loading)

Application manages the cache explicitly. Most common pattern.

```
Read:
1. Check cache → hit? return
2. Miss → query DB
3. Write result to cache
4. Return result

Write:
1. Write to DB
2. Invalidate cache (delete key)
```

```java
public User getUser(String id) {
    // 1. Check cache
    User cached = redis.get("user:" + id);
    if (cached != null) return cached;

    // 2. Cache miss → query DB
    User user = userRepo.findById(id);

    // 3. Populate cache
    redis.setex("user:" + id, 3600, user);  // TTL 1 hour

    return user;
}
```

**Pros:** Only caches what's actually requested. Cache failure doesn't break the app.
**Cons:** First request always slow (cold cache). Stale data possible between write and invalidation.

### 2. Write-Through

Every write goes to cache AND database simultaneously.

```
Write:
1. Write to cache
2. Cache writes to DB (synchronously)

Read:
1. Always read from cache (guaranteed fresh)
```

**Pros:** Cache is always consistent with DB. Reads are always fast.
**Cons:** Write latency increases (two writes). Cache fills with data that may never be read.

### 3. Write-Behind (Write-Back)

Write to cache immediately, flush to DB asynchronously.

```
Write:
1. Write to cache → return immediately
2. Background: batch flush to DB every N seconds

Read:
1. Read from cache
```

**Pros:** Extremely fast writes. Batching reduces DB load.
**Cons:** Data loss risk if cache crashes before flush. Complex to implement correctly.

### 4. Read-Through

Cache sits between app and DB. Cache itself fetches on miss.

```
Read:
1. App asks cache for data
2. Cache checks itself → hit? return
3. Miss → cache queries DB, stores result, returns
```

**Pros:** Application code is simpler (no cache logic).
**Cons:** First request still slow. Less control over what gets cached.

---

## Cache Invalidation

> "There are only two hard things in Computer Science: cache invalidation and naming things." — Phil Karlton

### Strategies

| Strategy               | How                                 | When to Use                                |
| ---------------------- | ----------------------------------- | ------------------------------------------ |
| **TTL (Time-to-Live)** | Key expires after N seconds         | Most cases. Simple, predictable.           |
| **Event-based**        | Invalidate on write/update event    | When freshness matters (e-commerce prices) |
| **Version-based**      | Key includes version: `user:123:v5` | When you need atomic updates               |
| **Write-through**      | Update cache on every write         | When reads >> writes                       |

### The Thundering Herd Problem

When a popular cache key expires, hundreds of requests simultaneously hit the DB:

```
Cache key "trending_posts" expires
  → 500 concurrent requests all get cache miss
  → 500 identical DB queries fire simultaneously
  → DB overloaded
```

**Solutions:**

```java
// 1. Mutex/Lock — only one thread refreshes
public List<Post> getTrending() {
    List<Post> cached = redis.get("trending");
    if (cached != null) return cached;

    // Try to acquire lock
    if (redis.setnx("trending:lock", "1", 10)) {
        List<Post> posts = db.queryTrending();
        redis.setex("trending", 300, posts);
        redis.del("trending:lock");
        return posts;
    }

    // Another thread is refreshing — wait and retry
    Thread.sleep(50);
    return getTrending();
}

// 2. Stale-while-revalidate — serve stale, refresh in background
// 3. Pre-warm — refresh cache before TTL expires (background job)
```

---

## Cache Eviction Policies

When cache is full, which key to remove?

| Policy                          | Description                      | Best For                        |
| ------------------------------- | -------------------------------- | ------------------------------- |
| **LRU** (Least Recently Used)   | Remove key not accessed longest  | General purpose (Redis default) |
| **LFU** (Least Frequently Used) | Remove key accessed fewest times | Skewed access patterns          |
| **FIFO**                        | Remove oldest key                | Simple, predictable             |
| **TTL-based**                   | Remove expired keys first        | Time-sensitive data             |
| **Random**                      | Remove random key                | When access is uniform          |

Redis eviction policies:

```
maxmemory-policy allkeys-lru    # Evict any key, LRU
maxmemory-policy volatile-lru   # Evict only keys with TTL set
maxmemory-policy noeviction     # Return error when full
```

---

## Redis as a Cache — Practical Patterns

### Pattern 1: Cache with Fallback

```java
@Service
public class ProductService {
    private final RedisTemplate<String, Product> redis;
    private final ProductRepository repo;

    public Product getProduct(Long id) {
        String key = "product:" + id;
        Product cached = redis.opsForValue().get(key);
        if (cached != null) return cached;

        Product product = repo.findById(id).orElseThrow();
        redis.opsForValue().set(key, product, Duration.ofMinutes(30));
        return product;
    }

    public void updateProduct(Long id, ProductUpdate update) {
        repo.save(update);
        redis.delete("product:" + id);  // invalidate
    }
}
```

### Pattern 2: Distributed Rate Limiting

```java
public boolean isAllowed(String userId, int maxRequests, int windowSeconds) {
    String key = "rate:" + userId;
    Long count = redis.opsForValue().increment(key);
    if (count == 1) {
        redis.expire(key, Duration.ofSeconds(windowSeconds));
    }
    return count <= maxRequests;
}
```

### Pattern 3: Leaderboard (Sorted Set)

```java
// Add score
redis.opsForZSet().add("leaderboard", userId, score);

// Top 10
Set<String> top10 = redis.opsForZSet()
    .reverseRange("leaderboard", 0, 9);

// User's rank
Long rank = redis.opsForZSet()
    .reverseRank("leaderboard", userId);
```

---

## CDN (Content Delivery Network)

For static assets and cacheable API responses:

```
User in Tokyo                    User in New York
     │                                │
     ▼                                ▼
┌─────────────┐                ┌─────────────┐
│ CDN Edge    │                │ CDN Edge    │
│ (Tokyo)     │                │ (New York)  │
└──────┬──────┘                └──────┬──────┘
       │ cache miss                   │ cache miss
       └──────────────┬───────────────┘
                      ▼
               ┌─────────────┐
               │   Origin    │
               │  (Server)   │
               └─────────────┘
```

**What to put on CDN:**

- Static files (JS, CSS, images, fonts)
- Pre-rendered HTML pages
- API responses that are the same for all users (public data)
- Video/audio streaming

**What NOT to put on CDN:**

- User-specific data
- Real-time data (stock prices, chat)
- Authenticated API responses

---

## Cache Design Decisions

| Question       | Guidance                                                                        |
| -------------- | ------------------------------------------------------------------------------- |
| What to cache? | Data that's read often, expensive to compute, and tolerates staleness           |
| TTL?           | Short (seconds) for volatile data, long (hours) for stable data                 |
| Cache size?    | Monitor hit rate. If < 80%, cache is too small or wrong data is cached          |
| Consistency?   | Accept eventual consistency for most reads. Use write-through for critical data |
| Failure mode?  | Cache should be optional — app works without it (just slower)                   |

---

[Chapter 4: Message Queues & Async Processing →](/blog/system-design/chapter-04-message-queues)

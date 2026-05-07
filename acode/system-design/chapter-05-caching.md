# Chapter 5: Caching

[← Ch 4](chapter-04-database-separation.md) | [Ch 6 →](chapter-06-message-queues.md)

---

## The Crisis

Monday morning. The podcast promo clip dropped on Twitter. Traffic doubles in an hour.

**Omar** (Slack, 9:15 AM):
> Database CPU at 82%. Query latency p99 is 340ms. Up from 12ms last week.

**Sana**:
> I ran `pg_stat_statements`. The top 5 queries account for 70% of load. They're all reads. User profiles, file metadata, share link lookups. The same data, over and over.

**Amir**:
> We already have Redis on the box. Why aren't we caching?

**Sana**:
> We use Redis for sessions. Nobody added caching for actual data. Every request hits Postgres directly.

---

## Architecture (Before)

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Server 1 │     │ Server 2 │     │ Server 3 │
└─────┬────┘     └─────┬────┘     └─────┬────┘
      │                 │                 │
      └────────────┬────┴────────────────┘
                   │  ALL reads hit DB
                   ▼
          ┌────────────────┐
          │   PostgreSQL    │  ← CPU 82%, drowning in reads
          └────────────────┘
```

## Architecture (After)

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Server 1 │     │ Server 2 │     │ Server 3 │
└─────┬────┘     └─────┬────┘     └─────┬────┘
      │                 │                 │
      └────────────┬────┴────────────────┘
                   │
              ┌────┴────┐
              ▼         ▼
     ┌──────────┐  ┌──────────────┐
     │  Redis   │  │  PostgreSQL   │
     │ (cache)  │  │  (source of   │
     │          │  │   truth)      │
     └──────────┘  └──────────────┘

     Flow: Check Redis first → if miss → query Postgres → store in Redis
```

---

## Concept: Caching Strategies

### Cache-Aside (Lazy Loading)

The application manages the cache explicitly.

```python
def get_user_profile(user_id: str):
    # 1. Check cache
    cached = redis.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)
    
    # 2. Cache miss — query database
    profile = db.query("SELECT * FROM users WHERE id = %s", user_id)
    
    # 3. Store in cache for next time
    redis.setex(f"user:{user_id}", 300, json.dumps(profile))  # TTL: 5 min
    
    return profile
```

**Pros**: Only caches data that's actually requested. Simple to implement.
**Cons**: First request is always slow (cache miss). Stale data possible.

### Write-Through

Every write goes to cache AND database simultaneously.

```python
def update_user_profile(user_id: str, data: dict):
    # 1. Write to database
    db.execute("UPDATE users SET ... WHERE id = %s", user_id)
    
    # 2. Write to cache (immediately consistent)
    redis.setex(f"user:{user_id}", 300, json.dumps(data))
```

**Pros**: Cache is always fresh after writes. No stale reads after your own writes.
**Cons**: Every write is slower (two writes). Caches data that may never be read.

### Write-Behind (Write-Back)

Write to cache first, asynchronously flush to database.

```python
def update_user_profile(user_id: str, data: dict):
    # 1. Write to cache only (fast!)
    redis.setex(f"user:{user_id}", 300, json.dumps(data))
    
    # 2. Queue async write to database
    queue.enqueue("flush_to_db", user_id=user_id, data=data)
```

**Pros**: Writes are extremely fast. Can batch multiple writes.
**Cons**: Data loss risk if cache dies before flush. Complex failure handling.

### GhostDrop's Choice

**Cache-aside** for reads + **write-through** for profile updates.

Why not write-behind? If Redis dies before flushing, we lose user data. Unacceptable for a file-sharing app where metadata = ownership.

---

## Concept: TTL and Invalidation

### Time-To-Live (TTL)

Every cached value expires after a set time.

```python
# Different TTLs for different data
CACHE_TTLS = {
    "user_profile": 300,      # 5 minutes (changes rarely)
    "file_metadata": 60,      # 1 minute (might be renamed)
    "share_link": 3600,       # 1 hour (almost never changes)
    "storage_quota": 30,      # 30 seconds (changes with uploads)
    "download_count": 10,     # 10 seconds (changes frequently)
}
```

### Invalidation Strategies

| Strategy | How | When to Use |
|----------|-----|-------------|
| **TTL expiry** | Data expires after N seconds | Acceptable staleness window |
| **Explicit delete** | Delete cache key on write | Must be fresh immediately |
| **Versioned keys** | `user:123:v7` → increment version | Complex objects, atomic updates |
| **Pub/Sub invalidation** | Broadcast "invalidate user:123" | Multiple cache layers |

```python
# Explicit invalidation on write
def rename_file(file_id: str, new_name: str):
    db.execute("UPDATE files SET name = %s WHERE id = %s", new_name, file_id)
    
    # Invalidate all related cache keys
    redis.delete(f"file:{file_id}")
    redis.delete(f"file_list:{file.owner_id}")
```

---

## Concept: Cache Stampede

**Omar**: "What happens when a popular cache key expires and 1,000 requests hit the database simultaneously?"

That's a **cache stampede** (thundering herd).

```
Cache key "popular_file:abc" expires
  → 1000 concurrent requests all get cache miss
  → 1000 identical queries hit Postgres
  → Database CPU spikes to 100%
  → Cascade failure
```

### Solutions

**1. Locking (Mutex)**
```python
def get_with_lock(key: str, query_fn):
    value = redis.get(key)
    if value:
        return json.loads(value)
    
    # Try to acquire lock
    lock_key = f"lock:{key}"
    if redis.set(lock_key, "1", nx=True, ex=5):  # Only one wins
        # Winner: query DB and populate cache
        value = query_fn()
        redis.setex(key, 300, json.dumps(value))
        redis.delete(lock_key)
        return value
    else:
        # Losers: wait and retry
        time.sleep(0.1)
        return get_with_lock(key, query_fn)
```

**2. Early Expiration (Probabilistic)**
```python
def get_with_early_refresh(key: str, query_fn, ttl=300):
    value, expiry = redis.get_with_ttl(key)
    
    if value and expiry > 30:  # More than 30s left
        return json.loads(value)
    
    if value and random.random() < 0.1:  # 10% chance: refresh early
        # Refresh in background, return stale value
        background_refresh(key, query_fn, ttl)
        return json.loads(value)
    
    # Actually expired — must query
    result = query_fn()
    redis.setex(key, ttl, json.dumps(result))
    return result
```

**3. Never Expire (Background Refresh)**
```python
# Cache never expires. A background job refreshes every N seconds.
# Reads always hit cache. Writes trigger immediate refresh.
```

### GhostDrop's Choice

Locking for high-traffic keys (popular shared files). TTL-based expiry for everything else. The 99th percentile case doesn't justify complexity everywhere.

---

## GhostDrop Redis Patterns

```python
# Cache layer implementation
class GhostDropCache:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def get_file_metadata(self, file_id: str):
        """Cache-aside with 60s TTL"""
        key = f"file:{file_id}"
        cached = self.redis.get(key)
        if cached:
            return json.loads(cached)
        
        meta = db.get_file(file_id)
        if meta:
            self.redis.setex(key, 60, json.dumps(meta))
        return meta
    
    def invalidate_file(self, file_id: str, owner_id: str):
        """Invalidate file and related list caches"""
        pipe = self.redis.pipeline()
        pipe.delete(f"file:{file_id}")
        pipe.delete(f"files:user:{owner_id}")
        pipe.delete(f"quota:{owner_id}")
        pipe.execute()
    
    def get_share_link(self, link_id: str):
        """Long TTL — share links rarely change"""
        key = f"share:{link_id}"
        cached = self.redis.get(key)
        if cached:
            return json.loads(cached)
        
        link = db.get_share_link(link_id)
        if link:
            self.redis.setex(key, 3600, json.dumps(link))
        return link
```

### Results After Caching

| Metric | Before | After |
|--------|--------|-------|
| DB queries/sec | 2,800 | 840 (70% cache hit) |
| DB CPU | 82% | 31% |
| p99 latency | 340ms | 45ms |
| Cache hit rate | 0% | 72% |

---

## Tradeoffs

| Decision | Gain | Cost |
|----------|------|------|
| Cache-aside | Simple, only caches hot data | Cold start penalty, stale reads |
| Short TTLs (30-300s) | Data stays relatively fresh | Lower hit rate |
| Explicit invalidation on writes | Immediate consistency for writers | Must track all related keys |
| Redis (managed ElastiCache) | Sub-ms reads, no ops | $0.068/hr for cache.r6g.large |

---

## Why Not Just...

**"Why not cache everything with a 1-hour TTL?"**
Users would see stale data for up to an hour after changes. Rename a file? Still shows old name. Delete a file? Still appears in the list. Unacceptable UX.

**"Why not use application-level caching (in-memory dict)?"**
With 3 app servers, each has its own cache. User updates profile on Server 1, Server 2 still serves stale data. You need a shared cache (Redis).

**"Why not use Memcached instead of Redis?"**
Memcached is simpler and slightly faster for pure key-value. But Redis gives you data structures (sorted sets for leaderboards, pub/sub for invalidation, Lua scripting for atomic operations). GhostDrop already uses Redis for sessions — one fewer system to manage.

---

## Exercise

GhostDrop's "Recent Files" page shows the 20 most recently uploaded files for a user. This list changes with every upload.

1. What caching strategy would you use? (TTL? Invalidation? Both?)
2. What's the cache key structure?
3. How do you handle the case where a user uploads a file and immediately refreshes — they should see it?

<details>
<summary>Hint</summary>

Use write-through: when a file is uploaded, update the cache immediately (push to a Redis sorted set by timestamp, trim to 20). The cache key is `recent_files:{user_id}`. On read, check Redis first. This guarantees read-your-writes consistency. Set a TTL of 5 minutes as a safety net in case invalidation fails.
</details>

---

## Quick Reference

| Term | Definition |
|------|-----------|
| **Cache-Aside** | App checks cache, on miss queries DB and fills cache |
| **Write-Through** | App writes to cache and DB simultaneously |
| **Write-Behind** | App writes to cache, async flush to DB |
| **TTL** | Time-To-Live — automatic cache expiration |
| **Cache Stampede** | Many requests hit DB simultaneously when a key expires |
| **Cache Hit Rate** | % of requests served from cache (target: 70-95%) |
| **Invalidation** | Removing stale data from cache |
| **Cold Start** | First request after deploy/restart — empty cache |

---

## What Breaks Next

Caching drops database load by 70%. Response times are fast. The system handles the traffic spike from the promo clip.

But then Sana notices: file uploads are taking 8-12 seconds. Not because of network — because the upload endpoint does virus scanning, thumbnail generation, and metadata extraction synchronously. The web worker is blocked the entire time.

"We need to process this stuff in the background," she says.

You need message queues.

[← Ch 4](chapter-04-database-separation.md) | [Ch 6 →](chapter-06-message-queues.md)

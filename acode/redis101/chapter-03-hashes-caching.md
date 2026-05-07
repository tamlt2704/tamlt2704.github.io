# Chapter 3: Player Profiles — Hashes and Caching Patterns

[← Chapter 2: Sorted Sets](chapter-02-sorted-sets.md) | [Chapter 4: The Matchmaking Queue →](chapter-04-lists-queues.md)

---

## The Problem

Derek wants player profile cards on the leaderboard. Each card shows username, avatar URL, country, level, and last login. For the top 100 players, that's 100 profile lookups.

Your first instinct: cache each profile as a JSON string.

```python
r.set("player:42:profile", json.dumps({"username": "alice", "avatar": "...", ...}), ex=300)
```

It works. But then the game updates a player's score after every match. To update just the score, you have to:
1. GET the full JSON blob
2. Deserialize it
3. Change one field
4. Serialize it back
5. SET the whole thing again

For 50,000 score updates per minute, that's 50,000 read-modify-write cycles. And if two requests update the same player simultaneously, one overwrites the other's changes.

Marta: "Use hashes. That's what they're for."

## Hashes: Structured Objects

A Redis hash is a map of field-value pairs stored under a single key. Like a row in a database table, or a Python dictionary.

```redis
HSET player:42 username "alice" avatar "https://cdn.pingpong.io/alice.png" country "US" level 27 score 1650 last_login "2024-01-15T09:30:00Z"
# (integer) 6 — six fields set

HGET player:42 username
# "alice"

HGET player:42 score
# "1650"

HGETALL player:42
# 1) "username"
# 2) "alice"
# 3) "avatar"
# 4) "https://cdn.pingpong.io/alice.png"
# 5) "country"
# 6) "US"
# 7) "level"
# 8) "27"
# 9) "score"
# 10) "1650"
# 11) "last_login"
# 12) "2024-01-15T09:30:00Z"
```

### Update One Field Without Touching Others

```redis
HINCRBY player:42 score 50
# (integer) 1700 — only the score field changes

HSET player:42 last_login "2024-01-15T10:00:00Z"
# Updates just last_login
```

No read-modify-write. No race condition. `HINCRBY` is atomic on a single field.

### Get Multiple Fields

```redis
HMGET player:42 username score level
# 1) "alice"
# 2) "1700"
# 3) "27"
```

Fetch only what you need. The leaderboard card needs username, avatar, and country — not the full profile.

## Hash Commands Reference

| Command | Description | Complexity |
|---|---|---|
| `HSET key field value [field value ...]` | Set one or more fields | O(N) |
| `HGET key field` | Get one field | O(1) |
| `HMGET key field [field ...]` | Get multiple fields | O(N) |
| `HGETALL key` | Get all fields and values | O(N) |
| `HINCRBY key field increment` | Atomic integer increment | O(1) |
| `HINCRBYFLOAT key field increment` | Atomic float increment | O(1) |
| `HDEL key field [field ...]` | Delete fields | O(N) |
| `HEXISTS key field` | Check if field exists | O(1) |
| `HLEN key` | Number of fields | O(1) |
| `HKEYS key` | All field names | O(N) |
| `HVALS key` | All values | O(N) |

## Caching Patterns

Now that you have the data structure, how do you keep it in sync with Postgres? Three patterns, each with tradeoffs.

### Pattern 1: Cache-Aside (Lazy Loading)

The application manages the cache. Check Redis first. On miss, query DB, populate cache.

```python
def get_player_profile(player_id: int) -> dict:
    cache_key = f"player:{player_id}"

    # 1. Check cache
    cached = r.hgetall(cache_key)
    if cached:
        return cached

    # 2. Cache miss — query DB
    cursor = db.cursor()
    cursor.execute("SELECT username, avatar, country, level, score FROM players WHERE id = %s", (player_id,))
    row = cursor.fetchone()
    if not row:
        return None

    profile = {
        "username": row[0], "avatar": row[1],
        "country": row[2], "level": str(row[3]), "score": str(row[4])
    }

    # 3. Populate cache
    r.hset(cache_key, mapping=profile)
    r.expire(cache_key, 300)  # 5 min TTL

    return profile
```

**Pros:** Only caches data that's actually requested. Simple.
**Cons:** First request is always slow (cache miss). Stale data until TTL expires.

### Pattern 2: Write-Through

Every write goes to both the DB and the cache. Cache is always fresh.

```python
def update_player_score(player_id: int, new_score: int):
    # 1. Write to DB
    cursor = db.cursor()
    cursor.execute("UPDATE players SET score = %s WHERE id = %s", (new_score, player_id))
    db.commit()

    # 2. Update cache
    cache_key = f"player:{player_id}"
    r.hset(cache_key, "score", str(new_score))
```

**Pros:** Cache is always consistent with DB.
**Cons:** Every write is slower (two writes). Cache fills with data nobody reads.

### Pattern 3: Write-Behind (Write-Back)

Write to cache immediately, flush to DB asynchronously in batches.

```python
def update_player_score_fast(player_id: int, points: int):
    cache_key = f"player:{player_id}"

    # 1. Update cache immediately (fast)
    r.hincrby(cache_key, "score", points)

    # 2. Queue DB write for later
    r.rpush("db:write_queue", json.dumps({
        "table": "players", "id": player_id,
        "field": "score", "increment": points
    }))

# Background worker flushes queue to DB every 5 seconds
def flush_writes():
    batch = []
    while True:
        item = r.lpop("db:write_queue")
        if not item:
            break
        batch.append(json.loads(item))
    # Batch INSERT/UPDATE to Postgres
    execute_batch(batch)
```

**Pros:** Writes are instant. DB gets efficient batch updates.
**Cons:** Data loss if Redis crashes before flush. Complex. Eventual consistency.

### Which Pattern for PingPong?

| Data | Pattern | Why |
|---|---|---|
| Player profiles | Cache-aside | Read-heavy, rarely changes |
| Scores | Write-through | Changes every match, must be accurate |
| Match history | Write-behind | High volume, slight delay acceptable |
| Leaderboard | Sorted set (no caching) | Redis IS the source of truth |

## Cache Invalidation: The Hard Problem

> "There are only two hard things in Computer Science: cache invalidation and naming things." — Phil Karlton

When the source data changes, the cache must be updated or deleted. Three strategies:

### TTL-Based Expiration

Set a TTL. Accept staleness within that window.

```python
r.hset("player:42", mapping=profile)
r.expire("player:42", 300)  # Stale for up to 5 minutes
```

Simple. Works for data where "slightly stale" is acceptable (player profiles, leaderboard positions).

### Event-Based Invalidation

When data changes, explicitly delete or update the cache.

```python
def on_player_profile_updated(player_id: int):
    r.delete(f"player:{player_id}")
    # Next read will re-populate from DB
```

More complex. Requires your write path to know about the cache. But guarantees freshness.

### Versioned Keys

Include a version number in the key. Bump the version to invalidate.

```python
def get_player_profile(player_id: int):
    version = r.get(f"player:{player_id}:version") or "1"
    cache_key = f"player:{player_id}:v{version}"
    cached = r.hgetall(cache_key)
    if cached:
        return cached
    # ... fetch from DB and cache under versioned key

def invalidate_player(player_id: int):
    r.incr(f"player:{player_id}:version")
    # Old versioned key will expire via TTL
```

Useful when you can't delete the old key immediately (other requests might be reading it).

## The Thundering Herd Problem

A popular player's cache expires. 1,000 concurrent requests all see a cache miss. All 1,000 query the database simultaneously. Postgres melts.

```
Request 1: GET player:42 → miss → query DB
Request 2: GET player:42 → miss → query DB
Request 3: GET player:42 → miss → query DB
...
Request 1000: GET player:42 → miss → query DB
```

### Fix: Cache Stampede Protection

Use a lock to ensure only one request rebuilds the cache:

```python
def get_player_profile_safe(player_id: int) -> dict:
    cache_key = f"player:{player_id}"

    # 1. Check cache
    cached = r.hgetall(cache_key)
    if cached:
        return cached

    # 2. Try to acquire rebuild lock
    lock_key = f"lock:rebuild:{cache_key}"
    acquired = r.set(lock_key, "1", nx=True, ex=5)

    if not acquired:
        # Another request is rebuilding — wait and retry
        time.sleep(0.1)
        return get_player_profile_safe(player_id)

    try:
        # 3. Double-check (another thread might have populated it)
        cached = r.hgetall(cache_key)
        if cached:
            return cached

        # 4. Query DB and populate cache
        profile = fetch_from_db(player_id)
        r.hset(cache_key, mapping=profile)
        r.expire(cache_key, 300)
        return profile
    finally:
        r.delete(lock_key)
```

Only one request hits the DB. The other 999 wait briefly and get the cached result.

## Fetching Profiles for the Leaderboard

The leaderboard shows top 100 players. Each needs a profile card. Naive approach: 100 individual HGETALL calls. Better: pipeline them.

```python
def get_leaderboard_with_profiles(page: int = 1, page_size: int = 20):
    start = (page - 1) * page_size
    end = start + page_size - 1

    # 1. Get top players from sorted set
    top_players = r.zrange("leaderboard:global", start, end, desc=True, withscores=True)

    # 2. Pipeline profile fetches
    pipe = r.pipeline()
    for username, score in top_players:
        pipe.hmget(f"player:{username}", "avatar", "country", "level")
    profiles = pipe.execute()

    # 3. Combine
    results = []
    for i, (username, score) in enumerate(top_players):
        avatar, country, level = profiles[i]
        results.append({
            "rank": start + i + 1,
            "username": username,
            "score": int(score),
            "avatar": avatar,
            "country": country,
            "level": level
        })

    return results
```

Two round-trips total: one for the sorted set, one pipeline for all profiles. Not 101 individual calls.

## Memory Efficiency: Small Hashes

Redis has a special encoding for small hashes called `ziplist` (or `listpack` in Redis 7+). When a hash has fewer than 128 fields and all values are under 64 bytes, Redis stores it as a compact byte array instead of a hash table.

This means small player profiles (6-10 fields) use significantly less memory than you'd expect.

Check the encoding:

```redis
OBJECT ENCODING player:42
# "listpack" — compact encoding (good!)

# If you add too many fields or large values:
OBJECT ENCODING player:42
# "hashtable" — standard encoding (uses more memory)
```

Configure thresholds in `redis.conf`:

```
hash-max-listpack-entries 128
hash-max-listpack-value 64
```

For PingPong's player profiles (6 fields, short values), every profile uses the compact encoding. 2 million profiles × ~200 bytes = ~400MB. Fits comfortably in a 4GB Redis instance.

## Sets: Unordered Collections

While we're here — Redis also has plain sets (unordered, unique members). Useful for:

```redis
# Track which players are online
SADD online:players "alice" "bob" "charlie"

# Is alice online?
SISMEMBER online:players "alice"
# (integer) 1

# How many online?
SCARD online:players
# (integer) 3

# Remove when they disconnect
SREM online:players "alice"

# All online players
SMEMBERS online:players
# 1) "bob"
# 2) "charlie"

# Friends of alice who are online (intersection)
SADD friends:alice "bob" "derek" "eve"
SINTER friends:alice online:players
# 1) "bob"
```

Sets are O(1) for add/remove/membership checks. Perfect for "is this player online?" or "mutual friends" queries.

## What You Learned

- **HSET/HGET/HGETALL** — store structured objects as field-value maps
- **HINCRBY** — atomic field-level updates without read-modify-write
- **HMGET** — fetch specific fields only
- **Cache-aside** — lazy loading on miss
- **Write-through** — update cache on every write
- **Write-behind** — async batch writes to DB
- **Cache invalidation** — TTL, event-based, versioned keys
- **Thundering herd** — lock-based stampede protection
- **Pipelines** — batch profile fetches for the leaderboard
- **Sets** — unordered collections for online status, friends, tags

The leaderboard now shows rich profile cards in under 5ms. Profiles update atomically. The thundering herd is tamed.

But Derek has a new request. "Players are waiting 30 seconds to find a match. The matchmaking is too slow." The current system polls Postgres every 5 seconds looking for available players. You need a real-time queue.

That's Chapter 4.

---

[← Chapter 2: Sorted Sets](chapter-02-sorted-sets.md) | [Chapter 4: The Matchmaking Queue →](chapter-04-lists-queues.md)

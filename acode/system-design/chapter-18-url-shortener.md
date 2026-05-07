# Chapter 18: URL Shortener Design

[← Ch 17](chapter-17-event-driven.md) | [Ch 19 →](chapter-19-realtime.md)

---

## The Crisis

Product meeting, week four. GhostDrop is stable at 10M users.

**Mia** (CEO):
> Our share links are ugly. `ghostdrop.io/share/a3f8c2e1-b7d1-4f2a-9c3e-1234567890ab` doesn't fit in a tweet. I want `gdrop.io/x7Kp2`. Short, memorable, shareable.

**Kai**:
> Also, we need analytics on share links. How many times was it clicked? From which countries? When?

**Sana**:
> We have 50 million share links already. We're creating 500K new ones per day. The lookup needs to be sub-10ms — it's in the critical path of every file download.

**Amir**:
> This is basically a URL shortener at scale. How do we generate unique short codes without collisions, and serve them fast?

---

## The Requirements

```
Functional:
  - Generate short code for any share link (6-8 chars)
  - Redirect short URL to original share link
  - Track click analytics (count, country, timestamp)
  - Links can expire (optional TTL)

Non-Functional:
  - Read-heavy: 100:1 read-to-write ratio
  - Latency: < 10ms for redirect (p99)
  - Scale: 500K new links/day, 50M reads/day
  - Uniqueness: No collisions, ever
  - Availability: 99.99% (links must always resolve)
```

---

## Concept: ID Generation Strategies

### 1. Auto-Increment + Base62 Encoding

```python
# Database auto-increment ID → base62 string
CHARSET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def encode_base62(num: int) -> str:
    if num == 0:
        return CHARSET[0]
    result = []
    while num > 0:
        result.append(CHARSET[num % 62])
        num //= 62
    return ''.join(reversed(result))

def decode_base62(s: str) -> int:
    num = 0
    for char in s:
        num = num * 62 + CHARSET.index(char)
    return num

# Examples:
# ID 1         → "1"        (1 char)
# ID 1000      → "g8"       (2 chars)
# ID 1000000   → "4c92"     (4 chars)
# ID 56800235583 → "zzzzzz" (6 chars = max for 6-char codes)
```

**Capacity**: 6 chars = 62^6 = 56.8 billion unique codes. Enough for decades.

**Pros**: Sequential, compact, predictable length
**Cons**: Predictable (can enumerate links), requires centralized counter

### 2. UUID (Truncated)

```python
import uuid

def generate_short_code():
    return uuid.uuid4().hex[:8]  # First 8 hex chars

# Example: "a3f8c2e1"
```

**Pros**: No coordination needed, works in distributed systems
**Cons**: Collision risk (8 hex chars = 4 billion combinations, birthday problem at ~77K)

### 3. Snowflake ID

```
┌─────────────────────────────────────────────────────────────┐
│ 1 bit │  41 bits timestamp  │ 10 bits machine │ 12 bits seq │
│ (sign)│  (ms since epoch)   │    ID           │  (counter)  │
└─────────────────────────────────────────────────────────────┘

Total: 64 bits → base62 encode → 7-11 chars
```

```python
import time

class SnowflakeGenerator:
    EPOCH = 1704067200000  # 2024-01-01 in ms
    
    def __init__(self, machine_id: int):
        self.machine_id = machine_id & 0x3FF  # 10 bits
        self.sequence = 0
        self.last_timestamp = 0
    
    def generate(self) -> int:
        timestamp = int(time.time() * 1000) - self.EPOCH
        
        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & 0xFFF  # 12 bits
            if self.sequence == 0:
                # Wait for next millisecond
                while timestamp <= self.last_timestamp:
                    timestamp = int(time.time() * 1000) - self.EPOCH
        else:
            self.sequence = 0
        
        self.last_timestamp = timestamp
        
        return (timestamp << 22) | (self.machine_id << 12) | self.sequence

# Usage
gen = SnowflakeGenerator(machine_id=1)
snowflake_id = gen.generate()
short_code = encode_base62(snowflake_id)  # "3kTm9Xp"
```

**Pros**: Globally unique without coordination, time-sortable, no collisions
**Cons**: Longer codes (7-11 chars), requires machine ID assignment

### 4. Pre-Generated Pool

```python
# Background job pre-generates codes and stores in a pool
# Workers grab codes from the pool (no generation at request time)

def refill_code_pool():
    """Background job: keep 100K codes ready."""
    while redis.llen("code_pool") < 100_000:
        code = generate_unique_code()
        if not db.exists(code):  # Verify uniqueness
            redis.rpush("code_pool", code)

def get_next_code() -> str:
    """Grab a pre-generated code (O(1), no collision check)."""
    return redis.lpop("code_pool")
```

**Pros**: Zero latency at request time, guaranteed unique
**Cons**: Pool management complexity, wasted codes if not used

### GhostDrop's Choice: Snowflake + Base62

- Globally unique without coordination (works across shards)
- Time-sortable (useful for analytics)
- 7 chars is short enough for sharing
- No collision checking needed

---

## Concept: Read-Heavy Optimization

50M reads/day = ~580 reads/sec average, 5,000/sec peak.

### Caching Strategy

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │────→│   CDN    │────→│  Redis   │────→ PostgreSQL
└──────────┘     └──────────┘     └──────────┘     (last resort)
                  (cache 1hr)      (cache 24hr)

Cache layers:
  1. CDN (CloudFront): Cache redirect for 1 hour
  2. Redis: Cache link data for 24 hours
  3. PostgreSQL: Source of truth (rarely hit)
```

```python
# Redirect handler — optimized for speed
@app.get("/{short_code}")
async def redirect(short_code: str):
    # Layer 1: Redis cache (sub-ms)
    cached = redis.get(f"link:{short_code}")
    if cached:
        link_data = json.loads(cached)
    else:
        # Layer 2: Database (5-10ms)
        link_data = db.get_link(short_code)
        if not link_data:
            raise HTTPException(404, "Link not found")
        
        # Warm cache
        redis.setex(f"link:{short_code}", 86400, json.dumps(link_data))
    
    # Check expiration
    if link_data.get("expires_at") and link_data["expires_at"] < time.time():
        raise HTTPException(410, "Link expired")
    
    # Track click asynchronously (don't slow down redirect)
    track_click_async(short_code, request)
    
    # 301 for permanent links, 302 for expiring links
    status = 301 if not link_data.get("expires_at") else 302
    return RedirectResponse(link_data["target_url"], status_code=status)
```

### Why 301 vs 302?

| Code | Meaning | Browser Behavior | Analytics Impact |
|------|---------|-----------------|------------------|
| **301** | Permanent redirect | Browser caches, never asks again | Lose click tracking |
| **302** | Temporary redirect | Browser asks every time | Full click tracking |

**GhostDrop's choice**: 302 for all links (we want analytics). CDN caches the redirect response for 1 hour (balances speed vs tracking accuracy).

---

## Concept: Analytics Tracking

```python
# Async click tracking (doesn't slow down redirect)
async def track_click_async(short_code: str, request: Request):
    event = {
        "short_code": short_code,
        "timestamp": datetime.utcnow().isoformat(),
        "ip": request.client.host,
        "country": request.headers.get("cf-ipcountry", "unknown"),
        "user_agent": request.headers.get("user-agent"),
        "referer": request.headers.get("referer"),
    }
    
    # Publish to Kafka for async processing
    producer.send("link.clicks", key=short_code, value=event)
    
    # Increment counter in Redis (real-time display)
    redis.incr(f"clicks:{short_code}")

# Analytics consumer aggregates clicks
class ClickAnalyticsConsumer:
    def handle_click(self, event):
        short_code = event["short_code"]
        date = event["timestamp"][:10]  # "2024-01-20"
        
        # Daily click count
        redis.hincrby(f"analytics:{short_code}", date, 1)
        
        # Country breakdown
        redis.hincrby(f"analytics:{short_code}:geo", event["country"], 1)
        
        # Periodic flush to PostgreSQL for long-term storage
        if should_flush():
            flush_to_postgres(short_code)
```

---

## Concept: Consistent Hashing for Link Distribution

With sharded databases, short codes need to route to the correct shard:

```python
# Short code → shard routing
def get_link_shard(short_code: str) -> str:
    # Use consistent hashing on the short code itself
    return hash_ring.get_node(short_code)

# This means:
# - Link creation writes to a specific shard
# - Link lookup reads from the same shard
# - No cross-shard queries for redirects
```

---

## GhostDrop Implementation

```python
# link_service.py
class LinkService:
    def __init__(self):
        self.snowflake = SnowflakeGenerator(machine_id=get_machine_id())
        self.cache = redis.Redis()
        self.db = ShardRouter()
    
    def create_short_link(self, target_url: str, user_id: str, 
                          expires_in: int = None) -> dict:
        # Generate unique short code
        snowflake_id = self.snowflake.generate()
        short_code = encode_base62(snowflake_id)[:7]  # 7 chars
        
        # Calculate expiration
        expires_at = None
        if expires_in:
            expires_at = int(time.time()) + expires_in
        
        # Store in database
        link_data = {
            "short_code": short_code,
            "target_url": target_url,
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "click_count": 0,
        }
        
        shard = self.db.get_connection(short_code)
        shard.execute(
            "INSERT INTO links (short_code, target_url, user_id, expires_at) "
            "VALUES (%s, %s, %s, %s)",
            (short_code, target_url, user_id, expires_at)
        )
        
        # Warm cache
        self.cache.setex(
            f"link:{short_code}", 86400, json.dumps(link_data, default=str)
        )
        
        return {"short_url": f"https://gdrop.io/{short_code}", **link_data}
    
    def resolve_link(self, short_code: str) -> dict:
        # Check cache first
        cached = self.cache.get(f"link:{short_code}")
        if cached:
            return json.loads(cached)
        
        # Database lookup
        shard = self.db.get_connection(short_code)
        link = shard.execute(
            "SELECT * FROM links WHERE short_code = %s", (short_code,)
        )
        
        if link:
            self.cache.setex(f"link:{short_code}", 86400, json.dumps(link))
        
        return link
```

### Performance Results

| Metric | Value |
|--------|-------|
| Link creation | 12ms (p99) |
| Link resolution (cache hit) | 0.8ms (p99) |
| Link resolution (cache miss) | 8ms (p99) |
| Cache hit rate | 96% (popular links cached) |
| Throughput | 15,000 redirects/sec |

---

## Tradeoffs

| Decision | Gain | Cost |
|----------|------|------|
| Snowflake IDs | No coordination, globally unique | Slightly longer codes (7 chars) |
| Multi-layer cache | Sub-ms redirects | Cache invalidation for expired links |
| 302 redirects | Full click analytics | No browser caching (more requests) |
| Async analytics | Redirect isn't slowed by tracking | Slight delay in analytics display |
| Sharding by short_code | Single-shard lookups | Link creation needs shard routing |

---

## Why Not Just...

**"Why not use auto-increment IDs?"**
Sequential IDs are predictable. Users could enumerate all share links by incrementing the code. Security risk for a file-sharing app. Snowflake IDs are non-sequential and non-guessable.

**"Why not just use UUIDs?"**
UUIDs are 36 characters. Even truncated to 8 chars, you get collision risk. Snowflake IDs are guaranteed unique without truncation concerns.

**"Why not use a third-party URL shortener (Bitly)?"**
Dependency on external service. Rate limits. Can't customize the domain. Can't control the data. For a core feature, own it.

**"Why not cache with 301 redirects and skip analytics?"**
Mia specifically asked for click analytics. 301 means browsers cache the redirect and never ask again — you lose all tracking after the first click.

---

## Exercise

GhostDrop wants to add "vanity URLs" — users can choose their own short code (e.g., `gdrop.io/my-resume`). 

1. How do you handle conflicts (two users want the same vanity code)?
2. How do you prevent abuse (someone squatting on `gdrop.io/admin`)?
3. How does this interact with the auto-generated codes?

<details>
<summary>Hint</summary>

Conflicts: First-come-first-served with a reservation system. Check availability before confirming. Use a distributed lock during creation. Abuse prevention: Maintain a blocklist of reserved words (admin, api, login, etc.). Require account verification for vanity URLs. Limit to paid users. Interaction with auto-generated: Use different character sets or lengths. Auto-generated are always 7 chars alphanumeric. Vanity URLs allow hyphens and are 3-30 chars. No overlap possible.
</details>

---

## Quick Reference

| Term | Definition |
|------|-----------|
| **Base62** | Encoding using 0-9, a-z, A-Z (62 characters) |
| **Snowflake ID** | Timestamp + machine ID + sequence number |
| **Collision** | Two different inputs generating the same short code |
| **301 Redirect** | Permanent — browser caches it |
| **302 Redirect** | Temporary — browser asks every time |
| **Read-Heavy** | System where reads vastly outnumber writes |
| **Pre-Generated Pool** | Batch-create IDs ahead of time for instant allocation |
| **Vanity URL** | User-chosen custom short code |

---

## What Breaks Next

Short links are live. `gdrop.io/x7Kp2` works beautifully. Analytics track every click. The system handles 15K redirects/sec.

But users want more: real-time upload progress, instant notifications when someone downloads their file, live collaboration indicators. HTTP request-response isn't enough — you need the server to push data to clients.

You need real-time communication at scale.

[← Ch 17](chapter-17-event-driven.md) | [Ch 19 →](chapter-19-realtime.md)

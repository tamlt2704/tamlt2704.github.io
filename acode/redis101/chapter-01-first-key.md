# Chapter 1: Your First Key — The Leaderboard Is Dying

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: The Ranking Problem →](chapter-02-sorted-sets.md)

---

## The Problem

The leaderboard page takes 8 seconds to load. Derek from frontend has been complaining for weeks. You open the endpoint and find this:

```sql
SELECT username, score, wins, losses
FROM players
ORDER BY score DESC
LIMIT 100;
```

One query. 2 million rows. Full table scan because someone forgot the index. But even with an index, this query runs on every single page load. 50,000 players check the leaderboard every hour. That's 50,000 identical queries returning the same 100 rows.

Marta: "Cache it. Use Redis. You have until end of day."

## What Is Redis, Actually?

Redis is a data structure server that lives in RAM. Not a cache bolted onto a database — a server that speaks data structures natively. Strings, lists, sets, sorted sets, hashes, streams. Each with O(1) or O(log N) operations.

It's fast because:
- Everything lives in memory (~100ns access vs ~10ms for disk)
- Single-threaded event loop — no lock contention
- Purpose-built data structures — not generic B-trees

Think of it as a giant `HashMap` that lives outside your application, speaks its own protocol, and has superpowers.

## Connecting

Fire up the CLI:

```bash
docker exec -it redis-dev redis-cli
```

You're in. The prompt looks like:

```
127.0.0.1:6379>
```

## SET and GET: The Basics

The simplest Redis operation: store a value, retrieve it later.

```redis
SET greeting "hello world"
# OK

GET greeting
# "hello world"
```

That's it. A key (`greeting`) maps to a value (`"hello world"`). Like a variable that lives on a server instead of in your code.

### Keys Are Strings

Keys can be anything, but use a naming convention. PingPong uses colons as separators:

```
player:42:score
leaderboard:global:top100
match:abc-123:state
```

This isn't enforced — it's convention. But it makes `KEYS player:*` useful for debugging.

### Values Are Typed

The value of `SET` is always a string. But Redis has other commands for other data types. We'll get to those.

## Caching the Leaderboard

Here's the plan: run the expensive query once, store the result in Redis, serve it from memory for the next 60 seconds.

### Step 1: Store It

```python
import redis
import json
import psycopg2

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
db = psycopg2.connect("dbname=pingpong")

def refresh_leaderboard():
    cursor = db.cursor()
    cursor.execute("""
        SELECT username, score, wins, losses
        FROM players ORDER BY score DESC LIMIT 100
    """)
    rows = [{"username": row[0], "score": row[1],
             "wins": row[2], "losses": row[3]} for row in cursor.fetchall()]

    r.set("leaderboard:global:top100", json.dumps(rows), ex=60)
    return rows
```

`ex=60` means the key expires in 60 seconds. After that, it vanishes. Next request triggers a fresh query.

### Step 2: Read It

```python
def get_leaderboard():
    cached = r.get("leaderboard:global:top100")
    if cached:
        return json.loads(cached)
    return refresh_leaderboard()
```

First request: cache miss → query DB → store in Redis → return.
Next 59 seconds: cache hit → return from memory → DB untouched.

### The Result

```
Before: 8,000ms (DB query on every request)
After:  2ms (Redis GET on cache hit)
```

Derek stops complaining. For now.

## TTL: Time to Live

Every cached value needs an expiration. Without one, stale data lives forever.

```redis
SET player:42:score 1500 EX 300
# Key expires in 300 seconds (5 minutes)

TTL player:42:score
# (integer) 297  — seconds remaining

# Already set a key without TTL? Add one:
EXPIRE player:42:score 300

# Remove expiration (key lives forever):
PERSIST player:42:score
```

### TTL Strategies

| Strategy | TTL | Use Case |
|---|---|---|
| Short (10-60s) | Rapidly changing data | Leaderboard, live scores |
| Medium (5-30min) | Moderate change rate | Player profiles, settings |
| Long (1-24h) | Rarely changes | Game configs, asset URLs |
| No TTL | Never changes (or manually invalidated) | Feature flags, static data |

The leaderboard uses 60 seconds. If a player scores, they'll see it within a minute. Good enough for a global ranking.

## Key Expiration: How It Actually Works

Redis doesn't run a timer for every key. That would be expensive with millions of keys. Instead:

1. **Lazy expiration**: When you `GET` an expired key, Redis checks the TTL, deletes it, returns nil. Zero cost until accessed.
2. **Active expiration**: 10 times per second, Redis randomly samples 20 keys with TTLs. If >25% are expired, it repeats. This prevents memory from filling with dead keys nobody reads.

This means an expired key might linger for a few milliseconds before being cleaned up. For caching, this is fine. For security tokens, use `PEXPIRE` (millisecond precision) and always check on read.

## INCR: Atomic Counters

CEO Chad wants to know how many games were played today. You could query Postgres. Or:

```redis
INCR stats:games:2024-01-15
# (integer) 1

INCR stats:games:2024-01-15
# (integer) 2

INCR stats:games:2024-01-15
# (integer) 3

GET stats:games:2024-01-15
# "3"
```

`INCR` is atomic. 1,000 concurrent requests all calling `INCR` will produce exactly 1,000. No race conditions. No locks. The single-threaded event loop guarantees it.

Set a TTL so yesterday's counter auto-deletes:

```redis
INCR stats:games:2024-01-15
EXPIRE stats:games:2024-01-15 172800
# Auto-deletes after 48 hours
```

### INCRBY, DECR, INCRBYFLOAT

```redis
INCRBY player:42:score 50
# Add 50 points

DECR player:42:lives
# Subtract 1 life

INCRBYFLOAT player:42:rating 0.25
# Floating point increment
```

## MSET and MGET: Batch Operations

One round-trip to Redis takes ~0.5ms over localhost. 100 individual GETs = 50ms of network overhead. Batch them:

```redis
MSET player:1:name "Alice" player:2:name "Bob" player:3:name "Charlie"
# OK

MGET player:1:name player:2:name player:3:name
# 1) "Alice"
# 2) "Bob"
# 3) "Charlie"
```

One round-trip instead of three. For the leaderboard, this matters when you're fetching 100 player details.

## NX and XX: Conditional Sets

```redis
SET lock:match:abc LOCKED NX EX 30
# OK — only sets if key does NOT exist (NX)
# Returns nil if key already exists

SET player:42:score 1600 XX
# OK — only sets if key DOES exist (XX)
# Returns nil if key doesn't exist
```

`NX` is the foundation of distributed locks (Chapter 7). `XX` is useful for "update only if already cached."

## EXISTS, DEL, UNLINK

```redis
EXISTS player:42:score
# (integer) 1 — exists

DEL player:42:score
# (integer) 1 — deleted

EXISTS player:42:score
# (integer) 0 — gone
```

`DEL` is synchronous — blocks until the key is freed. For large keys (a list with 10 million items), use `UNLINK` instead:

```redis
UNLINK huge:list
# (integer) 1 — schedules deletion in background
```

Same result, but `UNLINK` returns immediately and frees memory in a background thread.

## KEYS vs SCAN: Finding Keys

```redis
KEYS player:*
# Lists ALL matching keys — blocks the server while scanning
# NEVER use in production with millions of keys
```

`KEYS` is O(N) and blocks the single-threaded event loop. On a server with 5 million keys, it freezes Redis for seconds. Use `SCAN` instead:

```redis
SCAN 0 MATCH player:* COUNT 100
# Returns a cursor + batch of results
# 1) "4096"    ← next cursor
# 2) 1) "player:42:score"
#    2) "player:7:score"
#    ...

SCAN 4096 MATCH player:* COUNT 100
# Continue from cursor 4096...
# When cursor returns "0", you've seen everything
```

`SCAN` is iterative — it returns a batch and a cursor. Call it in a loop until the cursor is 0. It never blocks the server for more than a few microseconds.

## The Full Leaderboard Endpoint

Putting it all together:

```python
from flask import Flask, jsonify
import redis
import json
import psycopg2

app = Flask(__name__)
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
db = psycopg2.connect("dbname=pingpong")

CACHE_KEY = "leaderboard:global:top100"
CACHE_TTL = 60  # seconds

@app.route("/leaderboard")
def leaderboard():
    # Try cache first
    cached = r.get(CACHE_KEY)
    if cached:
        return jsonify(json.loads(cached))

    # Cache miss — query DB
    cursor = db.cursor()
    cursor.execute("""
        SELECT username, score, wins, losses
        FROM players ORDER BY score DESC LIMIT 100
    """)
    rows = [{"username": row[0], "score": row[1],
             "wins": row[2], "losses": row[3]} for row in cursor.fetchall()]

    # Store in cache
    r.set(CACHE_KEY, json.dumps(rows), ex=CACHE_TTL)

    return jsonify(rows)

@app.route("/leaderboard/refresh", methods=["POST"])
def force_refresh():
    r.delete(CACHE_KEY)
    return jsonify({"status": "cache cleared"})
```

## Verify It Works

```bash
# First request — cache miss, hits DB
curl http://localhost:5000/leaderboard
# Response time: ~200ms (DB query)

# Second request — cache hit
curl http://localhost:5000/leaderboard
# Response time: ~3ms (Redis GET)

# Check TTL
docker exec -it redis-dev redis-cli TTL leaderboard:global:top100
# (integer) 54

# Force refresh
curl -X POST http://localhost:5000/leaderboard/refresh
# Next GET will re-query the DB
```

## What You Learned

- **SET/GET** — store and retrieve string values
- **EX/TTL** — automatic key expiration
- **INCR** — atomic counters without locks
- **MSET/MGET** — batch operations to reduce round-trips
- **NX/XX** — conditional writes
- **DEL/UNLINK** — synchronous vs async deletion
- **SCAN** — safe key iteration (never use KEYS in production)
- **Cache-aside pattern** — check cache → miss → query DB → populate cache

The leaderboard loads in 3ms instead of 8 seconds. Derek is happy. CEO Chad is happy.

But Marta isn't. "The leaderboard shows the top 100 players. But players want to know their rank. 'Am I #4,521 or #4,522?' You can't answer that with a cached JSON blob."

She's right. You need a data structure that knows about ordering and ranking natively.

That's Chapter 2.

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: The Ranking Problem →](chapter-02-sorted-sets.md)

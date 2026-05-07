# Chapter 6: Spam Bots Flood the API — Rate Limiting

[← Chapter 5: Pub/Sub and Streams](chapter-05-pubsub-streams.md) | [Chapter 7: Distributed Locks →](chapter-07-distributed-locks.md)

---

## The Problem

Ops Olga's dashboard lights up red. 15,000 requests per second from 200 IP addresses. Spam bots are:
- Creating fake accounts (100/minute from one IP)
- Flooding matchmaking (joining and leaving repeatedly)
- Spamming chat with links to sketchy websites

The API has no rate limiting. Every request hits Redis and Postgres at full speed. The legitimate players experience lag because the bots are consuming all the capacity.

Marta: "Rate limit at the Redis layer. It's the only thing fast enough to check every request without adding latency."

## Fixed Window Counter

The simplest rate limiter: count requests per time window. If the count exceeds the limit, reject.

```python
def is_rate_limited(client_id: str, limit: int = 100, window_seconds: int = 60) -> bool:
    """Allow 100 requests per 60-second window."""
    key = f"ratelimit:{client_id}:{int(time.time()) // window_seconds}"

    current = r.incr(key)
    if current == 1:
        r.expire(key, window_seconds)  # Auto-cleanup

    return current > limit
```

```python
# In your API middleware
@app.before_request
def check_rate_limit():
    client_ip = request.remote_addr
    if is_rate_limited(client_ip, limit=100, window_seconds=60):
        abort(429, "Too Many Requests")
```

### The Edge Case: Window Boundaries

Fixed windows have a flaw. A client sends 100 requests at second 59 of window 1, then 100 more at second 0 of window 2. That's 200 requests in 2 seconds — but both windows show "100" (under the limit).

```
Window 1 (0:00-0:59):  .............................[100 requests at 0:59]
Window 2 (1:00-1:59):  [100 requests at 1:00].............................
                        ← 200 requests in 1 second! →
```

For PingPong's API, this burst is acceptable. For payment APIs or login attempts, it's not. You need a sliding window.

## Sliding Window Log

Track the timestamp of every request. Count how many fall within the last N seconds.

```python
def is_rate_limited_sliding(client_id: str, limit: int = 100, window_seconds: int = 60) -> bool:
    """Sliding window — no boundary exploits."""
    key = f"ratelimit:sliding:{client_id}"
    now = time.time()
    window_start = now - window_seconds

    pipe = r.pipeline()
    # Remove entries older than the window
    pipe.zremrangebyscore(key, 0, window_start)
    # Add current request
    pipe.zadd(key, {str(now): now})
    # Count entries in window
    pipe.zcard(key)
    # Set TTL for cleanup
    pipe.expire(key, window_seconds)
    results = pipe.execute()

    count = results[2]
    return count > limit
```

Uses a sorted set where the score is the timestamp. `ZREMRANGEBYSCORE` removes old entries. `ZCARD` counts current entries. Accurate to the millisecond.

**Tradeoff:** Uses more memory (stores every request timestamp) vs the fixed window (one counter). For 100 requests/minute per user, that's 100 sorted set entries per user. With 10,000 active users: ~10MB. Acceptable.

## Sliding Window Counter (Hybrid)

A compromise: use two fixed windows and interpolate. Less memory than the log, more accurate than a single fixed window.

```python
def is_rate_limited_hybrid(client_id: str, limit: int = 100, window_seconds: int = 60) -> bool:
    """Weighted average of current and previous window."""
    now = time.time()
    current_window = int(now) // window_seconds
    previous_window = current_window - 1

    current_key = f"ratelimit:{client_id}:{current_window}"
    previous_key = f"ratelimit:{client_id}:{previous_window}"

    pipe = r.pipeline()
    pipe.get(current_key)
    pipe.get(previous_key)
    results = pipe.execute()

    current_count = int(results[0] or 0)
    previous_count = int(results[1] or 0)

    # How far into the current window are we? (0.0 to 1.0)
    elapsed_ratio = (now % window_seconds) / window_seconds

    # Weighted estimate
    estimated = previous_count * (1 - elapsed_ratio) + current_count
    return estimated > limit
```

If we're 30% into the current window, we weight 70% of the previous window's count plus the current count. Smooth, memory-efficient, and eliminates the boundary exploit.

## Lua Scripts: Atomic Rate Limiting

The pipeline-based approaches have a subtle race condition. Between `INCR` and `EXPIRE`, another request could slip in. For critical rate limits (login attempts, payment APIs), use a Lua script — it executes atomically on the Redis server.

```python
RATE_LIMIT_SCRIPT = """
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
"""

# Register the script
rate_limit_sha = r.script_load(RATE_LIMIT_SCRIPT)

def is_allowed(client_id: str, limit: int = 100, window: int = 60) -> bool:
    key = f"ratelimit:{client_id}:{int(time.time()) // window}"
    result = r.evalsha(rate_limit_sha, 1, key, limit, window)
    return result == 1
```

### Why Lua?

Redis is single-threaded. A Lua script runs atomically — no other command can interleave. The INCR and EXPIRE happen as one unit. No race conditions. No partial state.

Lua scripts are also faster than pipelines because there's no round-trip between commands — everything executes server-side.

### Token Bucket in Lua

A more sophisticated algorithm: tokens refill at a steady rate. Each request consumes a token. When tokens run out, requests are rejected.

```python
TOKEN_BUCKET_SCRIPT = """
local key = KEYS[1]
local max_tokens = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])  -- tokens per second
local now = tonumber(ARGV[3])

local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
local tokens = tonumber(bucket[1]) or max_tokens
local last_refill = tonumber(bucket[2]) or now

-- Refill tokens based on elapsed time
local elapsed = now - last_refill
local new_tokens = math.min(max_tokens, tokens + (elapsed * refill_rate))

-- Try to consume one token
if new_tokens >= 1 then
    new_tokens = new_tokens - 1
    redis.call('HMSET', key, 'tokens', new_tokens, 'last_refill', now)
    redis.call('EXPIRE', key, math.ceil(max_tokens / refill_rate) * 2)
    return 1  -- allowed
else
    redis.call('HMSET', key, 'tokens', new_tokens, 'last_refill', now)
    redis.call('EXPIRE', key, math.ceil(max_tokens / refill_rate) * 2)
    return 0  -- rejected
end
"""

token_bucket_sha = r.script_load(TOKEN_BUCKET_SCRIPT)

def check_token_bucket(client_id: str, max_tokens: int = 10, refill_rate: float = 1.0) -> bool:
    """Token bucket: 10 tokens max, refills 1 per second."""
    key = f"bucket:{client_id}"
    now = time.time()
    result = r.evalsha(token_bucket_sha, 1, key, max_tokens, refill_rate, now)
    return result == 1
```

Token bucket allows short bursts (up to `max_tokens`) while enforcing a long-term average rate (`refill_rate`). Perfect for APIs where occasional bursts are fine but sustained abuse isn't.

## Per-Endpoint Rate Limits

Different endpoints need different limits:

```python
RATE_LIMITS = {
    "/api/matchmaking/join": {"limit": 5, "window": 60},      # 5 joins/minute
    "/api/chat/send": {"limit": 30, "window": 60},            # 30 messages/minute
    "/api/accounts/create": {"limit": 3, "window": 3600},     # 3 accounts/hour
    "/api/leaderboard": {"limit": 120, "window": 60},         # 120 reads/minute
}

@app.before_request
def rate_limit_middleware():
    endpoint = request.path
    config = RATE_LIMITS.get(endpoint)
    if not config:
        return  # No limit for this endpoint

    client_id = f"{request.remote_addr}:{endpoint}"
    if not is_allowed(client_id, config["limit"], config["window"]):
        remaining = 0
        response = jsonify({"error": "Rate limit exceeded", "retry_after": config["window"]})
        response.status_code = 429
        response.headers["X-RateLimit-Limit"] = str(config["limit"])
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["Retry-After"] = str(config["window"])
        return response
```

## IP Banning: The Nuclear Option

Some IPs are clearly malicious. After hitting the rate limit 10 times in an hour, ban them entirely:

```python
def check_and_ban(client_ip: str) -> bool:
    """Returns True if the IP is banned."""
    # Check ban list first (O(1))
    if r.sismember("banned:ips", client_ip):
        return True

    # Track rate limit violations
    violations_key = f"violations:{client_ip}"
    violations = int(r.get(violations_key) or 0)

    if violations >= 10:
        r.sadd("banned:ips", client_ip)
        r.expire("banned:ips", 86400)  # Ban expires after 24h
        log.warning(f"Banned IP {client_ip} after {violations} violations")
        return True

    return False

def record_violation(client_ip: str):
    """Called when a rate limit is hit."""
    key = f"violations:{client_ip}"
    r.incr(key)
    r.expire(key, 3600)  # Reset violation count after 1 hour
```

## Response Headers: Being a Good API Citizen

Always tell clients their rate limit status:

```python
@app.after_request
def add_rate_limit_headers(response):
    endpoint = request.path
    config = RATE_LIMITS.get(endpoint)
    if not config:
        return response

    client_id = f"{request.remote_addr}:{endpoint}"
    key = f"ratelimit:{client_id}:{int(time.time()) // config['window']}"
    current = int(r.get(key) or 0)

    response.headers["X-RateLimit-Limit"] = str(config["limit"])
    response.headers["X-RateLimit-Remaining"] = str(max(0, config["limit"] - current))
    response.headers["X-RateLimit-Reset"] = str(
        (int(time.time()) // config["window"] + 1) * config["window"]
    )
    return response
```

```bash
curl -i http://localhost:5000/api/leaderboard
# HTTP/1.1 200 OK
# X-RateLimit-Limit: 120
# X-RateLimit-Remaining: 117
# X-RateLimit-Reset: 1705312860
```

## Algorithm Comparison

| Algorithm | Accuracy | Memory | Burst Handling | Complexity |
|---|---|---|---|---|
| Fixed Window | Low (boundary exploit) | Very low | Allows 2x burst | Simple |
| Sliding Log | Perfect | High (stores all timestamps) | No burst | Medium |
| Sliding Counter | Good (approximation) | Low | Minimal burst | Medium |
| Token Bucket | Good | Low | Controlled burst | Medium |
| Leaky Bucket | Perfect | Low | No burst (smooths) | Medium |

For PingPong:
- **Account creation:** Sliding log (must be precise, low volume)
- **API endpoints:** Token bucket (allows small bursts, smooth long-term)
- **Chat messages:** Fixed window (good enough, high volume)

## What You Learned

- **Fixed window** — simple INCR counter per time window
- **Sliding window log** — sorted set of timestamps (precise but memory-heavy)
- **Sliding window counter** — weighted average of two windows (good compromise)
- **Token bucket** — refilling tokens for burst-tolerant limiting
- **Lua scripts** — atomic server-side execution (no race conditions)
- **Per-endpoint limits** — different rules for different APIs
- **IP banning** — escalation after repeated violations
- **Rate limit headers** — X-RateLimit-Limit, Remaining, Reset

The spam bots are throttled. Legitimate players are unaffected. Ops Olga's dashboard returns to green.

But there's a new problem. PingPong runs two API servers behind a load balancer. When a match is found, both servers try to assign it simultaneously. Two players get matched to the same opponent. The matchmaking is broken — you need a way to coordinate between servers.

That's Chapter 7.

---

[← Chapter 5: Pub/Sub and Streams](chapter-05-pubsub-streams.md) | [Chapter 7: Distributed Locks →](chapter-07-distributed-locks.md)

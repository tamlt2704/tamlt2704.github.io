# Chapter 10: Rate Limiting

[← Ch 9](chapter-09-cdn-edge.md) | [Ch 11 →](chapter-11-circuit-breakers.md)

---

## The Crisis

Friday, week two. Podcast in 6 days.

**Omar** (Slack, 6:45 AM):
> Something is hammering the API. One IP made 47,000 requests in the last hour. It's trying random file IDs — looks like someone scraping or brute-forcing share links.

**Sana**:
> We also have a bot farm hitting the download endpoint. They're burning through our CloudFront bandwidth — $200 in egress in the last 4 hours.

**Kai**:
> Legitimate users are getting slow responses because these bad actors are consuming all our capacity.

**Amir**:
> We need rate limiting. But we can't block legitimate users who upload a lot of files.

---

## Architecture (Before)

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Legit   │────→│          │────→│          │
│  Users   │     │    LB    │     │  Servers │
└──────────┘     │          │     │          │
                 │          │     │          │
┌──────────┐     │          │     │          │
│   Bots   │────→│          │────→│          │  ← All requests treated equally
│ 10K/min  │     └──────────┘     └──────────┘
└──────────┘
```

## Architecture (After)

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Legit   │────→│   Rate   │────→│    LB    │────→│  Servers │
│  Users   │     │  Limiter │     │          │     │          │
└──────────┘     │          │     │          │     │          │
                 │          │     └──────────┘     └──────────┘
┌──────────┐     │          │
│   Bots   │────→│  429 ⛔  │  ← Rejected: Too Many Requests
│ 10K/min  │     └──────────┘
└──────────┘
```

---

## Concept: Rate Limiting Algorithms

### 1. Token Bucket

```
Bucket capacity: 100 tokens
Refill rate: 10 tokens/second

Request arrives:
  - Bucket has tokens? → Allow, remove 1 token
  - Bucket empty? → Reject (429)

Allows bursts (up to bucket size) while enforcing average rate.
```

```python
class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
    
    def allow(self) -> bool:
        self._refill()
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False
    
    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
```

### 2. Sliding Window Log

```
Window: 1 minute
Limit: 100 requests

Track timestamp of every request in the window.
New request arrives:
  - Remove timestamps older than 1 minute
  - Count remaining: >= 100? → Reject
  - Otherwise: Add timestamp, Allow
```

**Pros**: Precise. No burst issues.
**Cons**: Memory-intensive (stores every timestamp).

### 3. Sliding Window Counter

```
Current window (minute 5): 42 requests
Previous window (minute 4): 78 requests
We're 30 seconds into minute 5 (50% through)

Weighted count = 78 * 0.5 + 42 = 81
Limit: 100 → Allow (81 < 100)
```

**Pros**: Low memory (two counters per window). Smooth.
**Cons**: Approximate (but good enough).

### Comparison

| Algorithm | Memory | Precision | Burst Handling |
|-----------|--------|-----------|----------------|
| Token Bucket | O(1) | Good | Allows controlled bursts |
| Sliding Window Log | O(n) | Exact | No bursts |
| Sliding Window Counter | O(1) | Approximate | Smooth |
| Fixed Window | O(1) | Poor (boundary issues) | Allows 2x burst at boundary |

---

## Concept: Distributed Rate Limiting

With 3 app servers, each server needs to share rate limit state.

```
Without shared state:
  Server 1 sees 90 requests from IP X → allows
  Server 2 sees 90 requests from IP X → allows
  Server 3 sees 90 requests from IP X → allows
  Total: 270 requests! (limit was 100)

With shared state (Redis):
  All servers check/increment the same Redis counter
  Total across all servers: enforced at 100
```

### Redis Implementation

```python
import redis

r = redis.Redis()

def is_rate_limited(key: str, limit: int, window_seconds: int) -> bool:
    """Sliding window counter using Redis."""
    pipe = r.pipeline()
    now = int(time.time())
    window_key = f"rate:{key}:{now // window_seconds}"
    
    pipe.incr(window_key)
    pipe.expire(window_key, window_seconds * 2)
    results = pipe.execute()
    
    current_count = results[0]
    return current_count > limit

# Usage in middleware
def rate_limit_middleware(request):
    # Rate limit by IP
    ip = request.client.host
    if is_rate_limited(f"ip:{ip}", limit=100, window_seconds=60):
        return JSONResponse(
            {"error": "Too many requests"},
            status_code=429,
            headers={"Retry-After": "60"}
        )
    
    # Rate limit by API key (higher limit for authenticated users)
    if request.user:
        if is_rate_limited(f"user:{request.user.id}", limit=1000, window_seconds=60):
            return JSONResponse(
                {"error": "Rate limit exceeded"},
                status_code=429,
                headers={"Retry-After": "60"}
            )
    
    return None  # Allow request
```

---

## Concept: Rate Limit Tiers

Different users get different limits:

| Tier | Requests/min | Upload/hour | Download/hour |
|------|-------------|-------------|---------------|
| Anonymous | 30 | 0 | 10 |
| Free user | 100 | 20 | 100 |
| Pro user | 1,000 | 200 | 1,000 |
| Enterprise | 10,000 | 2,000 | 10,000 |
| Internal service | 50,000 | N/A | N/A |

```python
RATE_LIMITS = {
    "anonymous": {"requests": 30, "window": 60},
    "free": {"requests": 100, "window": 60},
    "pro": {"requests": 1000, "window": 60},
    "enterprise": {"requests": 10000, "window": 60},
}

def get_rate_limit(user):
    if not user:
        return RATE_LIMITS["anonymous"]
    return RATE_LIMITS.get(user.tier, RATE_LIMITS["free"])
```

---

## Concept: API Keys and Abuse Prevention

### API Key Rate Limiting

```python
# Per-endpoint rate limiting
ENDPOINT_LIMITS = {
    "POST /api/upload": {"limit": 20, "window": 3600},      # 20 uploads/hour
    "GET /api/files": {"limit": 200, "window": 60},          # 200 list requests/min
    "POST /api/share": {"limit": 50, "window": 3600},        # 50 shares/hour
    "GET /download/*": {"limit": 100, "window": 3600},       # 100 downloads/hour
}
```

### Abuse Detection Beyond Rate Limiting

| Signal | Action |
|--------|--------|
| 100+ failed auth attempts | Block IP for 1 hour |
| Scanning sequential file IDs | Block + alert |
| Downloading same file 1000x | Throttle to 1 req/min |
| Uploading malware repeatedly | Account suspension |

---

## Concept: 429 Response Best Practices

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 47
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1705334400

{
  "error": "rate_limit_exceeded",
  "message": "You've exceeded 100 requests per minute. Please retry after 47 seconds.",
  "retry_after": 47
}
```

### Headers to Include

| Header | Purpose |
|--------|---------|
| `Retry-After` | Seconds until limit resets |
| `X-RateLimit-Limit` | Max requests allowed |
| `X-RateLimit-Remaining` | Requests left in window |
| `X-RateLimit-Reset` | Unix timestamp when window resets |

---

## GhostDrop Implementation

```python
# middleware/rate_limit.py
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import redis
import time

redis_client = redis.Redis(host='elasticache-endpoint', decode_responses=True)

class RateLimiter:
    def __init__(self):
        self.limits = {
            "anonymous": (30, 60),
            "free": (100, 60),
            "pro": (1000, 60),
        }
    
    async def __call__(self, request: Request, call_next):
        key = self._get_key(request)
        limit, window = self._get_limit(request)
        
        # Sliding window counter
        current = self._check_rate(key, limit, window)
        
        if current > limit:
            return JSONResponse(
                status_code=429,
                content={"error": "rate_limit_exceeded"},
                headers={
                    "Retry-After": str(window),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                }
            )
        
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, limit - current))
        return response
    
    def _get_key(self, request: Request) -> str:
        if hasattr(request.state, 'user') and request.state.user:
            return f"user:{request.state.user.id}"
        return f"ip:{request.client.host}"
    
    def _check_rate(self, key: str, limit: int, window: int) -> int:
        now = int(time.time())
        window_key = f"rate:{key}:{now // window}"
        
        pipe = redis_client.pipeline()
        pipe.incr(window_key)
        pipe.expire(window_key, window * 2)
        count, _ = pipe.execute()
        return count
```

### Results

| Metric | Before | After |
|--------|--------|-------|
| Abusive requests/hour | 47,000 | 0 (blocked) |
| Bandwidth abuse cost | $200/4hr | $0 |
| Legitimate user impact | Degraded (shared capacity) | Normal |
| Bot scraping | Unrestricted | Blocked after 30 req/min |

---

## Tradeoffs

| Decision | Gain | Cost |
|----------|------|------|
| Redis-based distributed limiting | Consistent across servers | Redis dependency, ~1ms per check |
| Sliding window counter | Low memory, smooth limiting | Slightly approximate |
| Per-user + per-IP | Catches both auth'd abuse and anonymous bots | More Redis keys |
| Generous limits for paid users | Revenue incentive to upgrade | Paid abusers harder to catch |

---

## Why Not Just...

**"Why not just use AWS WAF?"**
WAF is great for IP-based blocking and known attack patterns. But it can't do per-user rate limiting based on your application's tier system. Use both: WAF for L3/L4 attacks, application rate limiting for L7 abuse.

**"Why not rate limit at the load balancer?"**
ALB doesn't have built-in rate limiting. You'd need a WAF rule or application-level logic. Nginx can do basic rate limiting, but not per-user or per-tier.

**"Why not just block bad IPs in the firewall?"**
Reactive, not proactive. By the time you identify and block an IP, the damage is done. Rate limiting is automatic and immediate. Also, attackers rotate IPs.

---

## Exercise

GhostDrop launches a public API for third-party integrations. A popular app integrates and sends 50,000 requests/minute from a single API key.

1. Should you rate limit them the same as regular users?
2. How would you design tiered API access (free/pro/enterprise)?
3. What happens if their rate limit is hit mid-batch-operation?

<details>
<summary>Hint</summary>

Enterprise tier with higher limits (10K-50K/min). Provide rate limit headers so they can self-throttle. For batch operations, offer a dedicated batch endpoint that accepts multiple items in one request (reducing call count). If limit is hit mid-batch, return partial success with a list of processed/unprocessed items and a Retry-After header.
</details>

---

## Quick Reference

| Term | Definition |
|------|-----------|
| **Rate Limiting** | Restricting request frequency per client |
| **Token Bucket** | Algorithm allowing controlled bursts |
| **Sliding Window** | Time-based request counting (smooth) |
| **429 Too Many Requests** | HTTP status for rate-limited responses |
| **Retry-After** | Header telling client when to retry |
| **API Key** | Identifier for tracking/limiting API consumers |
| **Backpressure** | Slowing producers when consumers are overwhelmed |
| **WAF** | Web Application Firewall (network-level protection) |

---

## What Breaks Next

Rate limiting is in place. Bots are blocked. Legitimate users are protected. The system is handling 10K requests/second.

Then on Saturday night, the Redis cache goes down for 90 seconds. Every request that relied on cache now hits the database directly. Database CPU spikes to 100%. The entire app goes down.

"One component failed and took everything with it," Omar says. "We need the app to survive partial failures."

You need circuit breakers.

[← Ch 9](chapter-09-cdn-edge.md) | [Ch 11 →](chapter-11-circuit-breakers.md)

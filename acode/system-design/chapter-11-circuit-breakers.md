# Chapter 11: Circuit Breakers

[← Ch 10](chapter-10-rate-limiting.md) | [Ch 12 →](chapter-12-distributed-transactions.md)

---

## The Crisis

Saturday night, 11:47 PM. Omar's phone buzzes.

**PagerDuty**: `CRITICAL: Redis ElastiCache — node unreachable`

**Omar** (Slack, 11:48 PM):
> Redis is down. ElastiCache is failing over to the standby node. ETA: 60-90 seconds.

Within 10 seconds:

**Monitoring**:
> - Cache miss rate: 100%
> - Database queries/sec: 2,800 → 11,200 (4x spike)
> - Database CPU: 28% → 100%
> - API response time: 45ms → timeout
> - Error rate: 0.1% → 94%

**Sana** (Slack, 11:49 PM):
> The app assumes Redis is always there. Every cache miss goes to the database. With 100% miss rate, the database is getting ALL the traffic that cache was absorbing. It's a cascade failure.

**Amir** (Slack, 11:52 PM):
> One component went down and took the entire system with it. That can't happen.

---

## Architecture (Before — Cascade Failure)

```
Redis dies
    │
    ▼
All cache lookups fail
    │
    ▼
All requests hit database
    │
    ▼
Database overwhelmed (100% CPU)
    │
    ▼
Database queries timeout
    │
    ▼
App returns 500 to ALL users
    │
    ▼
Users retry (making it worse)
    │
    ▼
Complete system failure
```

## Architecture (After — Graceful Degradation)

```
Redis dies
    │
    ▼
Circuit breaker OPENS for Redis
    │
    ▼
App skips cache (doesn't even try)
    │
    ▼
Rate-limited DB queries (bulkhead)
    │
    ▼
Some features degraded, core works
    │
    ▼
Redis recovers → circuit CLOSES
    │
    ▼
Normal operation resumes
```

---

## Concept: Circuit Breaker Pattern

Inspired by electrical circuit breakers. When a dependency fails, stop calling it.

### Three States

```
┌──────────┐         ┌──────────┐         ┌──────────────┐
│  CLOSED  │────────→│   OPEN   │────────→│  HALF-OPEN   │
│ (normal) │ failures│ (failing)│  timer  │  (testing)   │
│          │ exceed  │          │ expires │              │
│ Allow all│ threshold│ Reject  │         │ Allow 1 req  │
│ requests │         │ all reqs │         │              │
└──────────┘         └──────────┘         └──────┬───────┘
      ▲                                          │
      │              success                     │
      └──────────────────────────────────────────┘
                     │
                     │ failure → back to OPEN
```

### States Explained

| State | Behavior | Transitions |
|-------|----------|-------------|
| **CLOSED** | All requests pass through | → OPEN when failure rate > threshold |
| **OPEN** | All requests fail immediately (no call made) | → HALF-OPEN after timeout |
| **HALF-OPEN** | Allow one test request | → CLOSED if success, → OPEN if failure |

---

## Concept: Implementation

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30, 
                 success_threshold=2):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
    
    def call(self, func, *args, fallback=None, **kwargs):
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                # Fast fail — don't even try
                if fallback:
                    return fallback()
                raise CircuitOpenError("Circuit is open")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            if fallback:
                return fallback()
            raise
    
    def _on_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
        else:
            self.failure_count = 0
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.success_count = 0
    
    def _should_attempt_reset(self):
        return (time.time() - self.last_failure_time) >= self.recovery_timeout
```

---

## Concept: Timeouts

Every external call needs a timeout. Without one, a slow dependency blocks your workers forever.

```python
# BAD: No timeout — worker blocked indefinitely
response = requests.get("http://notification-service/send")

# GOOD: Timeout after 2 seconds
response = requests.get("http://notification-service/send", timeout=2.0)

# BETTER: Connect timeout + read timeout
response = requests.get(
    "http://notification-service/send",
    timeout=(1.0, 3.0)  # 1s to connect, 3s to read
)
```

### Timeout Guidelines

| Dependency | Connect Timeout | Read Timeout |
|-----------|----------------|--------------|
| Redis (cache) | 100ms | 200ms |
| PostgreSQL | 500ms | 5s |
| External API | 1s | 10s |
| S3 | 1s | 30s (large files) |
| Internal service | 500ms | 3s |

---

## Concept: Retries with Exponential Backoff

When a call fails, retry — but not immediately.

```python
import random

def retry_with_backoff(func, max_retries=3, base_delay=0.5):
    for attempt in range(max_retries + 1):
        try:
            return func()
        except TransientError as e:
            if attempt == max_retries:
                raise
            
            # Exponential backoff with jitter
            delay = base_delay * (2 ** attempt)
            jitter = random.uniform(0, delay * 0.1)
            time.sleep(delay + jitter)
    
    raise MaxRetriesExceeded()

# Retry schedule:
# Attempt 0: immediate
# Attempt 1: wait 0.5s  (+ jitter)
# Attempt 2: wait 1.0s  (+ jitter)
# Attempt 3: wait 2.0s  (+ jitter)
# Give up
```

**Why jitter?** Without it, all retries happen at the same time (thundering herd). Jitter spreads them out.

**Why exponential?** Gives the failing service time to recover. Linear retries keep hammering it.

---

## Concept: Bulkheads

Isolate failures so one bad dependency doesn't consume all resources.

```
Without bulkhead:
  Thread pool: 100 threads (shared)
  Redis calls hang → all 100 threads blocked → nothing works

With bulkhead:
  Redis pool: 20 threads max
  DB pool: 50 threads max
  External API pool: 30 threads max
  
  Redis calls hang → only 20 threads blocked → 80 threads still serve requests
```

```python
from concurrent.futures import ThreadPoolExecutor

# Separate thread pools per dependency
redis_pool = ThreadPoolExecutor(max_workers=20, thread_name_prefix="redis")
db_pool = ThreadPoolExecutor(max_workers=50, thread_name_prefix="db")
api_pool = ThreadPoolExecutor(max_workers=30, thread_name_prefix="api")

async def get_user_profile(user_id):
    # Redis call limited to redis_pool
    try:
        cached = await asyncio.get_event_loop().run_in_executor(
            redis_pool, lambda: redis.get(f"user:{user_id}")
        )
        if cached:
            return json.loads(cached)
    except Exception:
        pass  # Redis down — fall through to DB
    
    # DB call limited to db_pool
    return await asyncio.get_event_loop().run_in_executor(
        db_pool, lambda: db.get_user(user_id)
    )
```

---

## Concept: Graceful Degradation

When a component fails, serve a degraded experience instead of an error.

| Component Down | Full Experience | Degraded Experience |
|---------------|-----------------|---------------------|
| Redis cache | Fast responses | Slower (DB direct), still works |
| Notification service | Email on upload | Upload works, email delayed |
| Thumbnail service | Preview images | Generic file icon |
| Analytics | View counts shown | "View count unavailable" |
| Search | Full-text search | Basic filename filter |

```python
# Graceful degradation for file listing
redis_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)

def get_file_list(user_id: str):
    # Try cache first (with circuit breaker)
    try:
        cached = redis_breaker.call(
            lambda: redis.get(f"files:{user_id}"),
            fallback=lambda: None
        )
        if cached:
            return json.loads(cached)
    except CircuitOpenError:
        pass  # Skip cache entirely
    
    # Fall back to database (with rate limiting to protect DB)
    files = db.get_user_files(user_id)
    
    # Try to warm cache (best effort)
    try:
        redis_breaker.call(
            lambda: redis.setex(f"files:{user_id}", 60, json.dumps(files))
        )
    except:
        pass  # Cache write failed — that's okay
    
    return files
```

---

## GhostDrop Implementation

```python
# resilience.py — GhostDrop's resilience layer
from circuitbreaker import circuit

# Circuit breaker for Redis
@circuit(failure_threshold=5, recovery_timeout=30, expected_exception=RedisError)
def redis_get(key: str):
    return redis_client.get(key)

@circuit(failure_threshold=5, recovery_timeout=30, expected_exception=RedisError)
def redis_set(key: str, value: str, ttl: int):
    return redis_client.setex(key, ttl, value)

# Circuit breaker for notification service
@circuit(failure_threshold=3, recovery_timeout=60, expected_exception=RequestException)
def send_notification(user_id: str, message: str):
    return requests.post(
        "http://notify-svc/send",
        json={"user_id": user_id, "message": message},
        timeout=(1.0, 3.0)
    )

# Graceful wrapper
def notify_user(user_id: str, message: str):
    try:
        send_notification(user_id, message)
    except (CircuitBreakerError, RequestException):
        # Queue for later delivery
        sqs.send_message(
            QueueUrl=NOTIFICATION_DLQ,
            MessageBody=json.dumps({"user_id": user_id, "message": message})
        )
```

### Results: Redis Failure Scenario

| Metric | Before (no breaker) | After (with breaker) |
|--------|---------------------|---------------------|
| Redis down duration | 90 seconds | 90 seconds |
| Total downtime | 90 seconds (full outage) | 0 seconds |
| User experience | 500 errors for everyone | Slower responses (200ms vs 45ms) |
| Database impact | 100% CPU, cascade failure | 55% CPU, manageable |
| Recovery time | 5+ minutes (DB recovery) | Instant when Redis returns |

---

## Tradeoffs

| Decision | Gain | Cost |
|----------|------|------|
| Circuit breaker on Redis | Survive cache failures | Slightly complex code |
| Timeouts on all calls | No indefinite blocking | Must tune per dependency |
| Exponential backoff | Don't overwhelm recovering services | Slower recovery for individual requests |
| Bulkheads | Isolate failure domains | More resource management |
| Graceful degradation | Users get something vs nothing | Degraded features need design/testing |

---

## Why Not Just...

**"Why not just make Redis highly available so it never fails?"**
ElastiCache Multi-AZ has 99.99% uptime — but that's still 52 minutes of downtime per year. Your app must handle those 52 minutes gracefully. Also: network partitions, maintenance windows, and bugs happen.

**"Why not just retry immediately?"**
Immediate retries amplify the problem. If Redis is down and 1,000 requests retry instantly, you've just doubled the load on a failing system. Backoff gives it time to recover.

**"Why not just catch all exceptions and return a default?"**
That hides real bugs. Circuit breakers are explicit: they track failure rates and make a conscious decision to stop calling a failing service. A bare `except: pass` hides everything including programming errors.

---

## Exercise

GhostDrop's share link service depends on both Redis (for caching) and PostgreSQL (for the source of truth). Design the resilience strategy:

1. What happens if Redis is down but Postgres is up?
2. What happens if Postgres is down but Redis is up?
3. What happens if both are down?
4. What's the user experience in each scenario?

<details>
<summary>Hint</summary>

1. Redis down + Postgres up: Circuit breaker opens for Redis. All reads go to Postgres. Slower but functional. 2. Postgres down + Redis up: Serve cached data (may be stale). Writes fail — return 503 for share creation but allow viewing existing shares from cache. 3. Both down: Return 503 with a friendly error page. Queue any write operations for retry. Show cached static content if available. The key insight: design for each failure mode independently.
</details>

---

## Quick Reference

| Term | Definition |
|------|-----------|
| **Circuit Breaker** | Pattern that stops calling a failing service |
| **CLOSED** | Normal state — requests pass through |
| **OPEN** | Failing state — requests rejected immediately |
| **HALF-OPEN** | Testing state — one request allowed to test recovery |
| **Timeout** | Maximum time to wait for a response |
| **Exponential Backoff** | Increasing delay between retries (1s, 2s, 4s, 8s...) |
| **Jitter** | Random variation added to backoff to prevent thundering herd |
| **Bulkhead** | Isolating resources per dependency |
| **Graceful Degradation** | Serving reduced functionality instead of errors |
| **Cascade Failure** | One failure causing a chain of failures |

---

## What Breaks Next

The system survives partial failures now. Redis can go down without taking everything with it. Timeouts prevent blocking. Circuit breakers prevent cascade failures.

But Monday morning, Sana finds a new problem: a user uploaded a file, the metadata was saved to the database, but the virus scan failed. The file is marked "ready" but was never scanned. Another user's share link was created, but the notification email never sent.

"We have operations that span multiple services," Sana says. "If one step fails, the others don't know about it."

You need distributed transactions.

[← Ch 10](chapter-10-rate-limiting.md) | [Ch 12 →](chapter-12-distributed-transactions.md)

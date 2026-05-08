"""
Rate Limiter — Core Implementation
====================================
Demonstrates: Token bucket, sliding window log, sliding window counter.

In a real system:
- State would be in Redis (MULTI/EXEC for atomicity)
- Rules would be configurable per API key/endpoint
- Distributed: each node checks Redis, not local state
"""

import time
from collections import defaultdict, deque
from dataclasses import dataclass, field


# ─── Strategy 1: Token Bucket ─────────────────────────────────────────────────

@dataclass
class TokenBucket:
    """
    Token bucket algorithm:
    - Bucket fills at a constant rate (tokens_per_second)
    - Each request consumes one token
    - If bucket is empty, request is rejected
    - Bucket has a maximum capacity (burst size)

    Pros: Allows bursts, simple, memory-efficient
    Cons: Doesn't guarantee exact rate over a window
    """
    capacity: int           # Max tokens (burst size)
    refill_rate: float      # Tokens added per second
    tokens: float = field(init=False)
    last_refill: float = field(init=False)

    def __post_init__(self):
        self.tokens = float(self.capacity)
        self.last_refill = time.time()

    def allow(self) -> bool:
        """Check if request is allowed. Returns True/False."""
        now = time.time()
        # Refill tokens based on elapsed time
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

    @property
    def remaining(self) -> int:
        return int(self.tokens)


# ─── Strategy 2: Sliding Window Log ──────────────────────────────────────────

class SlidingWindowLog:
    """
    Sliding window log algorithm:
    - Keep a log of all request timestamps
    - Count requests in the last N seconds
    - If count >= limit, reject

    Pros: Exact rate limiting, no boundary issues
    Cons: Memory-heavy (stores every timestamp)
    """

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window = window_seconds
        self.requests: deque[float] = deque()

    def allow(self) -> bool:
        now = time.time()
        # Remove expired entries
        while self.requests and self.requests[0] <= now - self.window:
            self.requests.popleft()

        if len(self.requests) < self.limit:
            self.requests.append(now)
            return True
        return False

    @property
    def remaining(self) -> int:
        now = time.time()
        while self.requests and self.requests[0] <= now - self.window:
            self.requests.popleft()
        return max(0, self.limit - len(self.requests))


# ─── Strategy 3: Sliding Window Counter ──────────────────────────────────────

class SlidingWindowCounter:
    """
    Sliding window counter algorithm:
    - Divide time into fixed windows
    - Weight the previous window's count by overlap percentage
    - Approximation, but memory-efficient

    Pros: Low memory (2 counters per key), good approximation
    Cons: Not exact — can allow slight over-limit
    """

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window = window_seconds
        self.current_window_start: float = 0
        self.current_count: int = 0
        self.previous_count: int = 0

    def allow(self) -> bool:
        now = time.time()
        current_window = int(now // self.window) * self.window

        # Rotate windows if needed
        if current_window != self.current_window_start:
            self.previous_count = self.current_count
            self.current_count = 0
            self.current_window_start = current_window

        # Calculate weighted count
        elapsed_in_window = now - current_window
        weight = 1 - (elapsed_in_window / self.window)
        estimated_count = self.previous_count * weight + self.current_count

        if estimated_count < self.limit:
            self.current_count += 1
            return True
        return False


# ─── Distributed Rate Limiter (simulated) ────────────────────────────────────

class DistributedRateLimiter:
    """
    Simulates a distributed rate limiter using Redis-like operations.

    In production, this would use Redis with Lua scripts for atomicity:
    ```lua
    local key = KEYS[1]
    local limit = tonumber(ARGV[1])
    local window = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])

    redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
    local count = redis.call('ZCARD', key)
    if count < limit then
        redis.call('ZADD', key, now, now .. math.random())
        redis.call('EXPIRE', key, window)
        return 1
    end
    return 0
    ```
    """

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window = window_seconds
        # Simulates Redis sorted sets per client
        self.client_logs: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, client_id: str) -> bool:
        """Check if a specific client's request is allowed."""
        now = time.time()
        log = self.client_logs[client_id]

        # Remove expired entries (ZREMRANGEBYSCORE equivalent)
        while log and log[0] <= now - self.window:
            log.popleft()

        # Check limit (ZCARD equivalent)
        if len(log) < self.limit:
            log.append(now)
            return True
        return False

    def get_headers(self, client_id: str) -> dict[str, str]:
        """Generate rate limit response headers."""
        now = time.time()
        log = self.client_logs[client_id]
        while log and log[0] <= now - self.window:
            log.popleft()

        remaining = max(0, self.limit - len(log))
        reset_time = int(log[0] + self.window) if log else int(now + self.window)

        return {
            "X-RateLimit-Limit": str(self.limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_time),
        }


# ─── Demo ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Rate Limiter Demo ===\n")

    # --- Token Bucket ---
    print("--- Token Bucket (10 tokens, refill 2/sec) ---")
    bucket = TokenBucket(capacity=10, refill_rate=2.0)

    # Burst: send 12 requests instantly
    results = [bucket.allow() for _ in range(12)]
    allowed = sum(results)
    print(f"  Burst of 12 requests: {allowed} allowed, {12-allowed} rejected")
    print(f"  Remaining tokens: {bucket.remaining}")

    # Wait and try again
    time.sleep(0.5)  # Should refill ~1 token
    print(f"  After 0.5s: allow={bucket.allow()}, remaining={bucket.remaining}")

    # --- Sliding Window Log ---
    print("\n--- Sliding Window Log (5 requests per 1 second) ---")
    swl = SlidingWindowLog(limit=5, window_seconds=1)

    results = [swl.allow() for _ in range(7)]
    print(f"  7 rapid requests: {sum(results)} allowed, {7-sum(results)} rejected")
    print(f"  Remaining: {swl.remaining}")

    time.sleep(1.1)
    print(f"  After 1.1s: allow={swl.allow()}, remaining={swl.remaining}")

    # --- Distributed Rate Limiter ---
    print("\n--- Distributed Rate Limiter (100 req/min per client) ---")
    limiter = DistributedRateLimiter(limit=100, window_seconds=60)

    # Simulate multiple clients
    for i in range(105):
        limiter.allow("client_A")
    for i in range(50):
        limiter.allow("client_B")

    headers_a = limiter.get_headers("client_A")
    headers_b = limiter.get_headers("client_B")
    print(f"  Client A: {headers_a}")
    print(f"  Client B: {headers_b}")

    # --- Comparison ---
    print("\n--- Algorithm Comparison ---")
    print(f"  {'Algorithm':<25} {'Memory':<15} {'Accuracy':<12} {'Best For'}")
    print(f"  {'Token Bucket':<25} {'O(1)':<15} {'Approximate':<12} Burst-tolerant APIs")
    print(f"  {'Sliding Window Log':<25} {'O(N)':<15} {'Exact':<12} Strict rate limits")
    print(f"  {'Sliding Window Counter':<25} {'O(1)':<15} {'Approximate':<12} Memory-constrained")

# Chapter 7: Two Servers, One Match — Distributed Locks

[← Chapter 6: Rate Limiting](chapter-06-rate-limiting.md) | [Chapter 8: Persistence →](chapter-08-persistence.md)

---

## The Problem

PingPong now runs two API servers behind a load balancer. The matchmaker finds two players and creates a match. But both servers run the matchmaker simultaneously. They both pop the same players from the queue and both try to create the match.

Result: Player A gets two match invitations. Player B gets two match invitations. One match has no players. Chaos.

```
Server 1: BRPOP → alice, bob → create_match(alice, bob) ✓
Server 2: BRPOP → alice, bob → create_match(alice, bob) ✓  ← DUPLICATE!
```

Wait — BRPOP is atomic. Two servers can't pop the same item. The real bug is subtler. The matchmaker pops alice, then pops bob. Between those two pops, the other server could pop bob too (from a different queue in the skill-bracket system). Or the match creation involves multiple steps (check availability, reserve players, create match record) and both servers pass the availability check before either reserves.

You need mutual exclusion across servers. A distributed lock.

## The Naive Lock: SET NX

```redis
SET lock:matchmaking LOCKED NX EX 10
# NX — only set if key doesn't exist
# EX 10 — auto-expire after 10 seconds (safety net)
# Returns OK if acquired, nil if someone else holds it
```

In Python:

```python
def acquire_lock(lock_name: str, timeout: int = 10) -> bool:
    return r.set(f"lock:{lock_name}", "1", nx=True, ex=timeout)

def release_lock(lock_name: str):
    r.delete(f"lock:{lock_name}")
```

### The Problem: Releasing Someone Else's Lock

```
Server 1: acquire_lock("match:abc") → OK (expires in 10s)
Server 1: ... processing takes 12 seconds (slow DB) ...
           ... lock expires at t=10 ...
Server 2: acquire_lock("match:abc") → OK (Server 1's lock expired)
Server 1: release_lock("match:abc") → DELETES Server 2's lock!
Server 3: acquire_lock("match:abc") → OK ← THREE servers in the critical section
```

Server 1 released a lock it no longer owned. The fix: include a unique identifier and only release if it's yours.

## The Correct Lock: SET NX + Owner Check

```python
import uuid

def acquire_lock(lock_name: str, timeout: int = 10) -> str | None:
    """Returns a token if acquired, None if not."""
    token = str(uuid.uuid4())
    acquired = r.set(f"lock:{lock_name}", token, nx=True, ex=timeout)
    if acquired:
        return token
    return None

# Lua script: only delete if the value matches our token
RELEASE_SCRIPT = """
if redis.call('GET', KEYS[1]) == ARGV[1] then
    return redis.call('DEL', KEYS[1])
else
    return 0
end
"""

def release_lock(lock_name: str, token: str) -> bool:
    """Release only if we still own it."""
    result = r.eval(RELEASE_SCRIPT, 1, f"lock:{lock_name}", token)
    return result == 1
```

The Lua script makes the check-and-delete atomic. Without it, another server could acquire the lock between your GET and DEL.

## Using the Lock: Safe Matchmaking

```python
def create_match_safely(player_a: str, player_b: str) -> str | None:
    """Create a match with distributed locking."""
    # Lock both players to prevent double-matching
    lock_a = acquire_lock(f"player:{player_a}:matching", timeout=5)
    if not lock_a:
        return None  # Player A is already being matched

    lock_b = acquire_lock(f"player:{player_b}:matching", timeout=5)
    if not lock_b:
        release_lock(f"player:{player_a}:matching", lock_a)
        return None  # Player B is already being matched

    try:
        # Both players locked — safe to create match
        match_id = str(uuid.uuid4())
        r.hset(f"match:{match_id}", mapping={
            "player_a": player_a,
            "player_b": player_b,
            "status": "created",
            "created_at": str(time.time())
        })
        return match_id
    finally:
        release_lock(f"player:{player_a}:matching", lock_a)
        release_lock(f"player:{player_b}:matching", lock_b)
```

Now if Server 1 is matching alice, Server 2 can't also match alice. The lock prevents double-booking.

## Lock Timeout: The Tradeoff

The `EX` timeout is a safety net. If the lock holder crashes, the lock auto-releases after N seconds. But:

- **Too short:** Lock expires while you're still processing → another server enters the critical section
- **Too long:** Crashed server holds the lock for minutes → everything waits

For PingPong's matchmaking (takes <1 second): 5-second timeout. For a long-running operation (data migration): 60 seconds with renewal.

### Lock Renewal (Watchdog)

For operations that might take longer than the timeout:

```python
import threading

class RenewableLock:
    def __init__(self, lock_name: str, timeout: int = 10):
        self.lock_name = lock_name
        self.timeout = timeout
        self.token = None
        self._renewal_thread = None
        self._stop_renewal = threading.Event()

    def acquire(self) -> bool:
        self.token = str(uuid.uuid4())
        acquired = r.set(f"lock:{self.lock_name}", self.token, nx=True, ex=self.timeout)
        if acquired:
            self._start_renewal()
            return True
        return False

    def release(self):
        self._stop_renewal.set()
        if self._renewal_thread:
            self._renewal_thread.join()
        release_lock(self.lock_name, self.token)

    def _start_renewal(self):
        def renew():
            while not self._stop_renewal.is_set():
                time.sleep(self.timeout / 3)
                if self._stop_renewal.is_set():
                    break
                # Extend TTL only if we still own it
                r.eval("""
                    if redis.call('GET', KEYS[1]) == ARGV[1] then
                        return redis.call('PEXPIRE', KEYS[1], ARGV[2])
                    end
                    return 0
                """, 1, f"lock:{self.lock_name}", self.token, self.timeout * 1000)

        self._renewal_thread = threading.Thread(target=renew, daemon=True)
        self._renewal_thread.start()
```

The watchdog renews the lock every `timeout/3` seconds. If the process dies, the thread dies too, and the lock expires naturally.

## Fencing Tokens: Preventing Stale Operations

Even with correct locks, there's a subtle problem:

```
Server 1: acquires lock (token=A), starts writing to DB
Server 1: GC pause for 15 seconds → lock expires
Server 2: acquires lock (token=B), writes to DB
Server 1: GC pause ends, writes to DB ← STALE WRITE (lock expired!)
```

Server 1 doesn't know its lock expired. It writes stale data over Server 2's fresh data.

Fix: **fencing tokens** — monotonically increasing numbers. The resource (DB, API) rejects writes with a token lower than the last one it saw.

```python
def acquire_lock_with_fence(lock_name: str, timeout: int = 10):
    """Returns (token, fence_number) or None."""
    token = str(uuid.uuid4())
    acquired = r.set(f"lock:{lock_name}", token, nx=True, ex=timeout)
    if acquired:
        fence = r.incr(f"fence:{lock_name}")  # Monotonically increasing
        return token, fence
    return None

def write_with_fence(resource_key: str, fence: int, data: dict):
    """Only write if our fence is the latest."""
    result = r.eval("""
        local current_fence = tonumber(redis.call('GET', KEYS[2]) or '0')
        if tonumber(ARGV[1]) >= current_fence then
            redis.call('SET', KEYS[2], ARGV[1])
            redis.call('HSET', KEYS[1], unpack(ARGV, 2))
            return 1
        end
        return 0
    """, 2, resource_key, f"{resource_key}:fence", fence, *flatten(data))
    return result == 1
```

Server 1 gets fence=5. Server 2 gets fence=6. When Server 1 tries to write with fence=5, the resource sees that fence=6 already wrote, and rejects it.

## Redlock: Multi-Node Locking

A single Redis instance is a single point of failure. If it crashes, all locks are lost. Redlock uses multiple independent Redis instances:

1. Try to acquire the lock on N instances (typically 5)
2. If you acquire it on a majority (≥3 out of 5), the lock is valid
3. The lock's effective TTL is reduced by the time spent acquiring

```python
import time

class Redlock:
    def __init__(self, redis_instances: list, ttl: int = 10000):
        self.instances = redis_instances  # List of Redis connections
        self.ttl = ttl  # milliseconds
        self.quorum = len(redis_instances) // 2 + 1

    def acquire(self, resource: str) -> dict | None:
        token = str(uuid.uuid4())
        start = time.time() * 1000

        acquired_count = 0
        for instance in self.instances:
            try:
                if instance.set(f"lock:{resource}", token, nx=True, px=self.ttl):
                    acquired_count += 1
            except redis.ConnectionError:
                continue  # Instance down — skip it

        elapsed = time.time() * 1000 - start
        effective_ttl = self.ttl - elapsed

        if acquired_count >= self.quorum and effective_ttl > 0:
            return {"token": token, "valid_until": time.time() + effective_ttl / 1000}
        else:
            # Failed — release any locks we did acquire
            self._release_all(resource, token)
            return None

    def release(self, resource: str, token: str):
        self._release_all(resource, token)

    def _release_all(self, resource: str, token: str):
        for instance in self.instances:
            try:
                instance.eval(RELEASE_SCRIPT, 1, f"lock:{resource}", token)
            except redis.ConnectionError:
                continue
```

### When to Use Redlock

| Scenario | Lock Type |
|---|---|
| Single Redis, best-effort | Simple SET NX |
| Single Redis, correctness matters | SET NX + fencing token |
| Multiple Redis instances, high availability | Redlock |
| Need strong consistency guarantees | Use ZooKeeper or etcd instead |

For PingPong's matchmaking: simple SET NX is sufficient. The worst case (double-match) is annoying but not catastrophic — the game can detect it and cancel one.

For payment processing or inventory management: Redlock or an external consensus system.

## Context Manager: Clean Lock Usage

```python
from contextlib import contextmanager

@contextmanager
def distributed_lock(lock_name: str, timeout: int = 10):
    """Use as a context manager for clean lock/unlock."""
    token = None
    try:
        token = acquire_lock(lock_name, timeout)
        if token is None:
            raise LockNotAcquiredError(f"Could not acquire lock: {lock_name}")
        yield token
    finally:
        if token:
            release_lock(lock_name, token)

# Usage
try:
    with distributed_lock("player:alice:matching", timeout=5):
        # Critical section — only one server executes this
        create_match(alice, bob)
except LockNotAcquiredError:
    # Another server is handling this player
    pass
```

## Retry with Backoff

If the lock is held, don't spin. Wait with exponential backoff:

```python
def acquire_with_retry(lock_name: str, timeout: int = 10,
                       max_retries: int = 5, base_delay: float = 0.1) -> str | None:
    for attempt in range(max_retries):
        token = acquire_lock(lock_name, timeout)
        if token:
            return token
        # Exponential backoff with jitter
        delay = base_delay * (2 ** attempt) + random.uniform(0, 0.1)
        time.sleep(delay)
    return None
```

## What You Learned

- **SET NX EX** — basic distributed lock acquisition
- **Owner tokens** — prevent releasing someone else's lock
- **Lua-based release** — atomic check-and-delete
- **Lock timeout** — safety net for crashed holders
- **Lock renewal (watchdog)** — extend TTL for long operations
- **Fencing tokens** — prevent stale writes after lock expiry
- **Redlock** — multi-instance locking for high availability
- **Context managers** — clean acquire/release patterns
- **Retry with backoff** — graceful contention handling

No more double-matches. Two servers coordinate safely through Redis locks. The matchmaking is correct even under concurrent load.

But Ops Olga raises a concern: "What happens when Redis crashes? All the locks disappear. All the cached data is gone. The leaderboard resets to zero. We need persistence."

She's right. Redis lives in RAM. RAM is volatile. You need a plan for when the power goes out.

That's Chapter 8.

---

[← Chapter 6: Rate Limiting](chapter-06-rate-limiting.md) | [Chapter 8: Persistence →](chapter-08-persistence.md)

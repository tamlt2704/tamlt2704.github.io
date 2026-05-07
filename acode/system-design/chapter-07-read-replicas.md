# Chapter 7: Read Replicas

[← Ch 6](chapter-06-message-queues.md) | [Ch 8 →](chapter-08-service-decomposition.md)

---

## The Crisis

Week two. The podcast is in 10 days. Traffic is growing 15% daily.

**Omar** (Slack, Tuesday 8:30 AM):
> Database CPU at 74%. We're back in danger territory. Cache hit rate is 72% but the 28% of misses are still 780 queries/sec hitting the primary.

**Sana**:
> I analyzed the query patterns. Read-to-write ratio is 8:1. For every write, we do 8 reads. File listings, profile lookups, share permission checks — all reads.

**Amir**:
> Can we just get a bigger database instance?

**You**:
> We're on db.r6g.xlarge (4 vCPU, 32GB). We could go to 4xlarge (16 vCPU, 128GB) — that's $1,100/mo. But it only buys us 4x headroom. At 15% daily growth, we burn through that in 10 days.

**Sana**:
> Or we split the reads to separate database copies. The primary handles writes. Replicas handle reads.

---

## Architecture (Before)

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Server 1 │  │ Server 2 │  │ Server 3 │
└─────┬────┘  └─────┬────┘  └─────┬────┘
      │              │              │
      └──────────────┼──────────────┘
                     │
                     ▼  (ALL queries: reads + writes)
            ┌────────────────┐
            │   Primary DB    │  ← CPU 74%
            │  (single node)  │
            └────────────────┘
```

## Architecture (After)

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Server 1 │  │ Server 2 │  │ Server 3 │
└─────┬────┘  └─────┬────┘  └─────┬────┘
      │              │              │
      │   ┌──────────┴──────────┐   │
      │   │                     │   │
      ▼   ▼                     ▼   ▼
┌──────────────┐         ┌──────────────┐
│  Primary DB   │────────→│  Replica 1   │  (async replication)
│  (writes)     │────┐    │  (reads)     │
└──────────────┘    │    └──────────────┘
                    │
                    └───→┌──────────────┐
                         │  Replica 2   │
                         │  (reads)     │
                         └──────────────┘
```

---

## Concept: How Replication Works

### Streaming Replication (PostgreSQL)

```
1. Client writes to Primary
2. Primary writes to WAL (Write-Ahead Log)
3. Primary streams WAL to Replica(s)
4. Replica applies WAL entries
5. Replica is now (nearly) up to date
```

### Synchronous vs Asynchronous

| Mode | Behavior | Latency | Data Safety |
|------|----------|---------|-------------|
| **Synchronous** | Primary waits for replica ACK | +2-5ms per write | Zero data loss |
| **Asynchronous** | Primary doesn't wait | No write penalty | Up to seconds of lag |

**GhostDrop's choice**: Asynchronous. We can't afford 2-5ms on every write. We'll handle the lag.

---

## Concept: Replication Lag

With async replication, replicas are always slightly behind the primary.

```
Timeline:
  t=0ms:   User uploads file, primary writes metadata
  t=0ms:   Primary sends WAL to replica
  t=50ms:  Replica receives and applies WAL
  
  If user reads from replica at t=25ms → file doesn't exist yet!
```

### Typical Lag

| Condition | Lag |
|-----------|-----|
| Normal load | 10-50ms |
| Heavy writes | 100-500ms |
| Replica under load | 1-5 seconds |
| Network issues | 10+ seconds |

### The Problem

**Kai**: "User uploads a file, page refreshes, file isn't in their list. They upload again. Now they have duplicates."

This is the **read-after-write consistency** problem.

---

## Concept: Read/Write Splitting

### Routing Logic

```python
class DatabaseRouter:
    def __init__(self, primary, replicas):
        self.primary = primary
        self.replicas = replicas
    
    def get_connection(self, query_type: str, user_context: dict = None):
        if query_type == "write":
            return self.primary
        
        # Read-after-write: if user just wrote, read from primary
        if user_context and user_context.get("last_write_at"):
            elapsed = time.time() - user_context["last_write_at"]
            if elapsed < 2.0:  # Within 2 seconds of a write
                return self.primary
        
        # Otherwise, round-robin across replicas
        return random.choice(self.replicas)
```

### Which Reads Go Where?

| Query | Route To | Why |
|-------|----------|-----|
| File list (own files) | Primary (if just uploaded) | Read-your-writes |
| File list (browsing) | Replica | Slight lag is fine |
| User profile (own) | Primary (if just edited) | Read-your-writes |
| User profile (others) | Replica | Don't need real-time |
| Share link lookup | Replica | Immutable after creation |
| Download count | Replica | Approximate is fine |
| Permission check | Primary | Security-critical |

---

## Concept: Handling Replication Lag

### Strategy 1: Read-Your-Writes from Primary

```python
# After a write, set a flag with TTL
def after_write(user_id: str):
    redis.setex(f"recent_write:{user_id}", 5, "1")

# Before a read, check the flag
def route_read(user_id: str):
    if redis.get(f"recent_write:{user_id}"):
        return primary_db
    return random.choice(replicas)
```

### Strategy 2: Monotonic Reads

Ensure a user always reads from the same replica (so they never go "back in time"):

```python
def get_replica_for_user(user_id: str):
    # Consistent hashing: same user always hits same replica
    replica_index = hash(user_id) % len(replicas)
    return replicas[replica_index]
```

### Strategy 3: Causal Consistency Token

```python
# Write returns a position token
def create_file(user_id, file_data):
    result = primary.execute("INSERT INTO files ...")
    wal_position = primary.execute("SELECT pg_current_wal_lsn()")
    return {"file_id": result.id, "consistency_token": wal_position}

# Read waits for replica to catch up to that position
def get_files(user_id, consistency_token=None):
    replica = get_replica()
    if consistency_token:
        replica.execute(
            "SELECT pg_last_wal_replay_lsn() >= %s", 
            consistency_token
        )
        # If not caught up, fall back to primary
    return replica.execute("SELECT * FROM files WHERE user_id = %s", user_id)
```

---

## GhostDrop Implementation

### Django Database Router

```python
# db_router.py
class GhostDropRouter:
    def db_for_read(self, model, **hints):
        """Route reads to replica unless recent write."""
        request = hints.get('request')
        if request and hasattr(request, 'user'):
            if self._recent_write(request.user.id):
                return 'default'  # primary
        
        # Security-critical models always read from primary
        if model.__name__ in ('Permission', 'AccessToken', 'Session'):
            return 'default'
        
        return 'replica'
    
    def db_for_write(self, model, **hints):
        """All writes go to primary."""
        return 'default'
    
    def _recent_write(self, user_id):
        return cache.get(f'recent_write:{user_id}') is not None

# settings.py
DATABASES = {
    'default': {  # Primary
        'HOST': 'ghostdrop-primary.rds.amazonaws.com',
    },
    'replica': {  # Read replica
        'HOST': 'ghostdrop-replica-1.rds.amazonaws.com',
    },
}
DATABASE_ROUTERS = ['app.db_router.GhostDropRouter']
```

### Results

| Metric | Before | After (2 replicas) |
|--------|--------|-------------------|
| Primary CPU | 74% | 28% |
| Read latency (p50) | 8ms | 6ms |
| Read capacity | 780 qps | 2,340 qps (3x) |
| Write capacity | Unchanged | Unchanged |
| Monthly cost | $277 | $831 (+$554) |

---

## Concept: When Replicas Aren't Enough

Replicas scale reads. They don't help with:

- **Write-heavy workloads**: All writes still go to one primary
- **Large transactions**: Long-running queries on replicas can lag further
- **Schema migrations**: ALTER TABLE locks propagate to replicas
- **Single-row hot spots**: One popular file's metadata hit repeatedly

When you hit write limits, you need **sharding** (Chapter 16).

---

## Tradeoffs

| Decision | Gain | Cost |
|----------|------|------|
| 2 read replicas | 3x read capacity | 3x database cost |
| Async replication | No write penalty | Replication lag (10-500ms) |
| Read-your-writes routing | Consistent UX after writes | Complexity, some reads hit primary |
| Security reads from primary | No stale permission data | Primary handles more load |

---

## Why Not Just...

**"Why not just add more cache?"**
Cache hit rate is already 72%. Pushing to 90% means caching data that changes frequently (file lists, quotas). Short TTLs mean frequent misses anyway. Replicas handle the misses.

**"Why not use synchronous replication?"**
Every write would take 2-5ms longer. At 100 writes/sec, that's 200-500ms of added latency per second. For a file-sharing app where writes are uploads (already slow), this might be acceptable — but async gives us room to grow.

**"Why not just scale up the primary?"**
We could go from 4 vCPU to 16 vCPU ($277 → $1,100/mo). That's 4x capacity for 4x cost. Two replicas give us 3x read capacity for 3x cost, AND we get redundancy — if the primary fails, a replica can be promoted.

---

## Exercise

GhostDrop adds a "file views" counter. Every time someone views a shared file, the counter increments. This generates 5,000 writes/sec to the primary.

1. Should view counts go through the primary database?
2. What alternative storage would you use for high-frequency counters?
3. How would you display the count to users? (Exact? Approximate?)

<details>
<summary>Hint</summary>

Don't write every view to PostgreSQL. Use Redis INCR for real-time counting (handles 100K+ ops/sec). Periodically flush to PostgreSQL (every 60 seconds or every 100 increments). Display approximate counts ("~1.2K views") from Redis. Exact counts don't matter for vanity metrics — "1,247 views" vs "~1.2K views" is the same to users.
</details>

---

## Quick Reference

| Term | Definition |
|------|-----------|
| **Read Replica** | Database copy that serves read queries |
| **Replication Lag** | Time delay between primary write and replica update |
| **Read-Your-Writes** | Guarantee that you see your own recent writes |
| **WAL** | Write-Ahead Log — stream of database changes |
| **Streaming Replication** | Continuous WAL shipping to replicas |
| **Promotion** | Converting a replica to a primary (during failover) |
| **Read/Write Splitting** | Routing reads to replicas, writes to primary |
| **Monotonic Reads** | Never reading older data than previously seen |

---

## What Breaks Next

Read replicas handle the query load. Primary CPU is down to 28%. You have headroom.

But deploys are getting painful. The monolith takes 40 minutes to build, test, and deploy. A bug in the notification system requires redeploying the entire app. Sana's team and Kai's team step on each other's code daily.

"We need to split this thing up," Sana says. "But carefully."

You need service decomposition.

[← Ch 6](chapter-06-message-queues.md) | [Ch 8 →](chapter-08-service-decomposition.md)

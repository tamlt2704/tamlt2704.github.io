# Chapter 13: Consistency Models

[← Ch 12](chapter-12-distributed-transactions.md) | [Ch 14 →](chapter-14-deployments.md)

---

## The Crisis

Tuesday, week three. Podcast in 3 days.

**Kai** (Slack, 11:00 AM):
> Bug report: User deleted a file. Refreshed the page. File is still there. Refreshed again. Gone. Refreshed again. Back again. They think we have ghosts.

**Sana**:
> The delete went to the primary database. But the file list reads from a replica. Replication lag is ~200ms normally, but under load it's spiking to 2-3 seconds. The user's read hit a stale replica.

**Omar**:
> Also found: cache says share link "xyz" is valid. Database says it was revoked 30 seconds ago. A user accessed a file they shouldn't have.

**Amir**:
> So different parts of our system disagree about reality. How do we decide what level of consistency each feature needs?

---

## The Problem Visualized

```
Timeline:
  t=0s:    User deletes file (write → primary)
  t=0.1s:  Primary sends WAL to replica
  t=0.5s:  User refreshes page (read → replica)
  t=0.5s:  Replica hasn't applied the delete yet → FILE STILL SHOWS
  t=2.1s:  Replica applies the delete
  t=3.0s:  User refreshes again → file gone ✓

The user saw inconsistent state for 2 seconds.
```

---

## Concept: Consistency Models

### Strong Consistency

Every read returns the most recent write. Period.

```
Write(x=5) at t=0
Read(x) at t=0.001 → returns 5 (guaranteed)

No stale reads. Ever.
```

**Cost**: High latency (must wait for all replicas to acknowledge). Lower availability (if a replica is unreachable, writes block).

### Eventual Consistency

If no new writes occur, all replicas will *eventually* converge to the same value.

```
Write(x=5) at t=0
Read(x) at t=0.001 → might return 3 (old value)
Read(x) at t=2.0   → returns 5 (eventually consistent)

"Eventually" = milliseconds to seconds (usually)
```

**Cost**: Stale reads possible. Simple to implement. High availability.

### Causal Consistency

If operation B depends on operation A, everyone sees A before B. Unrelated operations can be seen in any order.

```
User A: Write("file created")     → t=0
User A: Write("file shared")      → t=1  (causally depends on creation)

Any reader sees: "created" before "shared" (causal order preserved)
But two unrelated users' writes? No ordering guarantee.
```

### Read-Your-Writes Consistency

You always see your own writes. Others might see stale data.

```
You: Write(x=5) at t=0
You: Read(x) at t=0.001 → returns 5 (your write is visible to you)
Other user: Read(x) at t=0.001 → might return 3 (stale, that's okay)
```

---

## Concept: CAP Theorem (Practical)

In a distributed system, during a network partition, you must choose:

```
┌─────────────────────────────────────────┐
│              CAP Theorem                 │
│                                          │
│         Consistency (C)                  │
│            /        \                    │
│           /          \                   │
│    Availability (A)───Partition           │
│                       Tolerance (P)      │
│                                          │
│  Pick 2 of 3 (but P is mandatory in     │
│  distributed systems, so really: C or A) │
└─────────────────────────────────────────┘
```

### In Practice

| Choice | Behavior During Partition | Example |
|--------|--------------------------|---------|
| **CP** | Reject requests to maintain consistency | Bank transfers, inventory |
| **AP** | Serve stale data to maintain availability | Social media feeds, view counts |

**Key insight**: You don't choose one for the entire system. You choose per feature.

---

## Concept: Choosing Consistency Per Feature

### GhostDrop's Feature Analysis

| Feature | Consistency Needed | Why | Implementation |
|---------|-------------------|-----|----------------|
| File ownership | Strong | Security: wrong owner = data breach | Read from primary |
| Share permissions | Strong | Security: stale permission = unauthorized access | Read from primary |
| File list (own) | Read-your-writes | UX: user should see their upload immediately | Read from primary after write |
| File list (shared) | Eventual (2s) | Slight delay showing new shares is acceptable | Read from replica |
| Download count | Eventual (60s) | Vanity metric, approximate is fine | Redis counter, periodic flush |
| Storage quota | Read-your-writes | User should see updated quota after upload | Cache invalidation on write |
| User profile | Eventual (5s) | Name change visible to others within seconds | Cache with TTL |

---

## GhostDrop Implementation

```python
# consistency.py — route queries based on consistency requirements

class ConsistencyRouter:
    """Route reads based on required consistency level."""
    
    def __init__(self, primary, replicas, cache):
        self.primary = primary
        self.replicas = replicas
        self.cache = cache
    
    def read_strong(self, query, params):
        """Always read from primary. Use for security-critical data."""
        return self.primary.execute(query, params)
    
    def read_your_writes(self, query, params, user_id: str):
        """Read from primary if user recently wrote, else replica."""
        last_write = self.cache.get(f"last_write:{user_id}")
        if last_write and (time.time() - float(last_write)) < 5.0:
            return self.primary.execute(query, params)
        return random.choice(self.replicas).execute(query, params)
    
    def read_eventual(self, query, params):
        """Read from any replica. Fastest, may be stale."""
        return random.choice(self.replicas).execute(query, params)
    
    def write(self, query, params, user_id: str = None):
        """All writes go to primary. Mark user's last write time."""
        result = self.primary.execute(query, params)
        if user_id:
            self.cache.setex(f"last_write:{user_id}", 5, str(time.time()))
        return result

# Usage
router = ConsistencyRouter(primary_db, replica_dbs, redis)

# Security-critical: always primary
def check_file_permission(user_id, file_id):
    return router.read_strong(
        "SELECT * FROM permissions WHERE user_id=%s AND file_id=%s",
        (user_id, file_id)
    )

# User's own file list: read-your-writes
def get_my_files(user_id):
    return router.read_your_writes(
        "SELECT * FROM files WHERE owner_id=%s ORDER BY created_at DESC",
        (user_id,),
        user_id=user_id
    )

# Public stats: eventual is fine
def get_download_count(file_id):
    return router.read_eventual(
        "SELECT download_count FROM files WHERE id=%s",
        (file_id,)
    )
```

---

## Concept: Resolving the Cache Inconsistency

The share link problem: cache says valid, database says revoked.

```
t=0:   Share link created → cached with 1-hour TTL
t=30s: Share link revoked → database updated
t=31s: Request checks cache → "valid" (stale!)
t=60m: Cache expires → next request checks DB → "revoked"

Window of inconsistency: up to 60 minutes!
```

### Solution: Invalidate on Security-Critical Writes

```python
def revoke_share_link(link_id: str):
    # 1. Update database
    db.execute("UPDATE share_links SET revoked=true WHERE id=%s", link_id)
    
    # 2. Immediately invalidate cache
    redis.delete(f"share:{link_id}")
    
    # 3. Publish invalidation event (for other cache layers)
    redis.publish("cache_invalidation", json.dumps({
        "type": "share_link_revoked",
        "link_id": link_id
    }))

def check_share_link(link_id: str):
    # For security-critical checks: ALWAYS verify against primary
    # Cache is only for performance, not for authorization decisions
    cached = redis.get(f"share:{link_id}")
    if cached:
        link = json.loads(cached)
        if link.get("revoked"):
            return None
        # Even if cache says valid, verify revocation status from primary
        is_revoked = db.primary.execute(
            "SELECT revoked FROM share_links WHERE id=%s", link_id
        )
        if is_revoked:
            redis.delete(f"share:{link_id}")
            return None
        return link
    
    # Cache miss: query primary
    return db.primary.execute("SELECT * FROM share_links WHERE id=%s", link_id)
```

---

## Architecture: Consistency Zones

```
┌─────────────────────────────────────────────────────────┐
│                    GhostDrop System                       │
│                                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │  STRONG CONSISTENCY ZONE                         │    │
│  │  (Primary DB only)                               │    │
│  │                                                   │    │
│  │  • File permissions                              │    │
│  │  • Share link validation                         │    │
│  │  • User authentication                           │    │
│  │  • Billing/quota enforcement                     │    │
│  └─────────────────────────────────────────────────┘    │
│                                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │  READ-YOUR-WRITES ZONE                           │    │
│  │  (Primary after write, replica otherwise)        │    │
│  │                                                   │    │
│  │  • User's own file list                          │    │
│  │  • User's own profile                            │    │
│  │  • Storage quota display                         │    │
│  └─────────────────────────────────────────────────┘    │
│                                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │  EVENTUAL CONSISTENCY ZONE                       │    │
│  │  (Replicas + cache, stale OK)                    │    │
│  │                                                   │    │
│  │  • Download counts                               │    │
│  │  • Other users' profiles                         │    │
│  │  • Search results                                │    │
│  │  • Activity feed                                 │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## Tradeoffs

| Decision | Gain | Cost |
|----------|------|------|
| Strong for permissions | No unauthorized access | More primary DB load |
| Read-your-writes for own data | Good UX after actions | Routing complexity |
| Eventual for public data | Scalable, fast | Users may see stale counts |
| Cache invalidation on revoke | Immediate security enforcement | More write-path complexity |

---

## Why Not Just...

**"Why not make everything strongly consistent?"**
You'd route all reads to the primary database. That defeats the purpose of read replicas. Primary CPU would be back at 74%. Strong consistency everywhere means you're paying for consistency you don't need.

**"Why not just use shorter cache TTLs?"**
A 5-second TTL on share link cache means a revoked link is accessible for up to 5 seconds. For security-critical data, even 5 seconds is too long. For download counts, 60 seconds is fine.

**"Why not use a strongly consistent distributed database (Spanner/CockroachDB)?"**
They exist and work well, but add 5-10ms per write (cross-region consensus). At GhostDrop's scale, PostgreSQL with explicit consistency routing is simpler and cheaper. Consider Spanner when you need strong consistency across multiple regions.

---

## Exercise

GhostDrop adds collaborative folders. Multiple users can upload to the same folder. User A uploads a file. User B refreshes the folder view 500ms later.

1. Should User B see User A's file immediately?
2. What consistency model fits this use case?
3. How would you implement it without routing all reads to the primary?

<details>
<summary>Hint</summary>

Causal consistency. User B doesn't need to see User A's file immediately (they don't know it was uploaded). But if User A shares the folder link with User B saying "I just uploaded the report," User B expects to see it. Solution: include a "version token" in the folder. When User A shares the link, include the token. User B's request includes the token, and the system ensures the replica is at least that fresh before responding. If not, fall back to primary.
</details>

---

## Quick Reference

| Term | Definition |
|------|-----------|
| **Strong Consistency** | Every read sees the latest write |
| **Eventual Consistency** | Replicas converge over time; stale reads possible |
| **Causal Consistency** | Causally related operations seen in order |
| **Read-Your-Writes** | You always see your own recent writes |
| **CAP Theorem** | During partition: choose consistency or availability |
| **Linearizability** | Strongest form: operations appear instantaneous |
| **Stale Read** | Reading old data from a lagging replica |
| **Consistency Zone** | Group of features sharing the same consistency requirement |

---

## What Breaks Next

Consistency is understood and implemented per feature. Security-critical reads go to primary. User-facing reads use read-your-writes. Public data is eventually consistent.

The podcast is in 3 days. You need to deploy the final round of changes. But the last deploy caused a 4-minute outage — a database migration locked a table, and the new code expected a column that didn't exist yet on half the servers.

"We need safer deployments," Omar says. "Zero-downtime or we're dead on podcast day."

You need deployment strategies.

[← Ch 12](chapter-12-distributed-transactions.md) | [Ch 14 →](chapter-14-deployments.md)

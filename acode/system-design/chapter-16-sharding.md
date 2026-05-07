# Chapter 16: Database Sharding

[← Ch 15](chapter-15-observability.md) | [Ch 17 →](chapter-17-event-driven.md)

---

## The Crisis

The podcast aired. 8 million users signed up in 48 hours. The system held — barely.

**Sana** (Monday standup):
> Database primary is at 78% CPU. Read replicas handle reads fine, but writes are the problem now. Every upload writes file metadata. Every share creates a link record. Every download increments a counter. 4,200 writes/sec and growing.

**Omar**:
> We're on db.r6g.4xlarge — 16 vCPU, 128GB RAM. The next size up is 64 vCPU, 512GB — $8,000/month. And that's the ceiling.

**Amir**:
> We can't vertically scale the database anymore. What's the horizontal option?

**You**:
> Sharding. Split the database into multiple independent databases, each holding a subset of the data. Each shard handles its own writes.

---

## Architecture (Before — Single Primary)

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Server 1 │  │ Server 2 │  │ Server 3 │
└─────┬────┘  └─────┬────┘  └─────┬────┘
      │              │              │
      └──────────────┼──────────────┘
                     │  ALL writes
                     ▼
            ┌────────────────┐
            │  Primary DB     │  ← 78% CPU, 4200 writes/sec
            │  (single node)  │
            └────────────────┘
```

## Architecture (After — Sharded)

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Server 1 │  │ Server 2 │  │ Server 3 │
└─────┬────┘  └─────┬────┘  └─────┬────┘
      │              │              │
      └──────────────┼──────────────┘
                     │
              ┌──────┴──────┐
              │ Shard Router │
              └──┬───┬───┬──┘
                 │   │   │
        ┌────────┘   │   └────────┐
        ▼            ▼            ▼
┌────────────┐ ┌────────────┐ ┌────────────┐
│  Shard 0   │ │  Shard 1   │ │  Shard 2   │
│ Users A-H  │ │ Users I-P  │ │ Users Q-Z  │
│ 1400 w/s   │ │ 1400 w/s   │ │ 1400 w/s   │
└────────────┘ └────────────┘ └────────────┘
```

---

## Concept: Horizontal Partitioning (Sharding)

Sharding splits a table's rows across multiple databases. Each shard holds a subset of the data.

```
Users table (10M rows):
  Shard 0: user_id 0 - 3,333,333
  Shard 1: user_id 3,333,334 - 6,666,666
  Shard 2: user_id 6,666,667 - 9,999,999

Each shard is an independent PostgreSQL instance.
Each handles ~1/3 of the write load.
```

---

## Concept: Shard Key Selection

The shard key determines which shard a row lives on. This is the most important decision.

### Good Shard Keys

| Key | Distribution | Access Pattern |
|-----|-------------|----------------|
| `user_id` | Even (if IDs are sequential/random) | Most queries are per-user |
| `file_id` | Even | Good for file-centric queries |
| `tenant_id` | Uneven (some tenants are huge) | Good for multi-tenant SaaS |

### Bad Shard Keys

| Key | Problem |
|-----|---------|
| `created_at` | All new writes go to one shard (hot shard) |
| `country` | US shard gets 40% of traffic (uneven) |
| `file_type` | "image" shard gets 80% of data |

### GhostDrop's Choice: `user_id`

Why:
- Most queries are "get files for user X" or "check quota for user X"
- User IDs are UUIDs (evenly distributed)
- All of a user's data lives on one shard (no cross-shard joins needed)
- Users don't share data often (share links are the exception)

---

## Concept: Shard Routing

How does the app know which shard to query?

### Hash-Based Routing

```python
def get_shard(user_id: str, num_shards: int) -> int:
    """Deterministic: same user_id always maps to same shard."""
    return hash(user_id) % num_shards

# Example:
get_shard("usr_abc123", 3)  → Shard 1
get_shard("usr_def456", 3)  → Shard 0
get_shard("usr_ghi789", 3)  → Shard 2
```

### Range-Based Routing

```python
SHARD_RANGES = [
    (0, 3_333_333, "shard-0.db.ghostdrop.io"),
    (3_333_334, 6_666_666, "shard-1.db.ghostdrop.io"),
    (6_666_667, 9_999_999, "shard-2.db.ghostdrop.io"),
]

def get_shard(user_id_numeric: int) -> str:
    for start, end, host in SHARD_RANGES:
        if start <= user_id_numeric <= end:
            return host
```

### Directory-Based Routing

```python
# Lookup table: user_id → shard
# Stored in a fast lookup (Redis or small DB)
def get_shard(user_id: str) -> str:
    return redis.get(f"shard_map:{user_id}")
```

### GhostDrop's Choice: Consistent Hashing

(See below — handles resharding gracefully)

---

## Concept: Cross-Shard Queries

**Sana**: "What about share links? User A (Shard 0) shares a file with User B (Shard 2). Where does the share link live?"

### The Problem

```sql
-- This query spans shards (expensive/impossible):
SELECT f.*, s.* FROM files f
JOIN share_links s ON f.id = s.file_id
WHERE s.recipient_id = 'user_on_shard_2'
AND f.owner_id = 'user_on_shard_0';
```

### Solutions

| Approach | How | Tradeoff |
|----------|-----|----------|
| **Denormalize** | Store share link on both shards | Data duplication, sync complexity |
| **Global table** | Share links in a separate unsharded DB | That DB becomes a bottleneck |
| **Application join** | Query both shards, join in app code | Higher latency, more complex |
| **Shard by owner** | Share links live on file owner's shard | Recipient queries are cross-shard |

### GhostDrop's Approach

Share links are sharded by `file_owner_id` (same shard as the file). When a recipient views their shared files, the app queries all shards and merges results. This is acceptable because:
- Viewing shared files is read-heavy (replicas handle it)
- It's a less frequent operation than viewing own files
- Results can be cached aggressively

---

## Concept: Consistent Hashing

Regular hash-based routing breaks when you add/remove shards:

```
hash(user) % 3 = shard 1
hash(user) % 4 = shard 2  ← DIFFERENT! Must migrate data.

Adding one shard requires remapping ~75% of keys.
```

Consistent hashing minimizes remapping:

```
Ring: 0 ─────────────────────────────────── 2^32
      │    Shard 0    │    Shard 1    │    Shard 2    │
      
Add Shard 3:
      │  S0  │  S3  │    Shard 1    │    Shard 2    │
      
Only ~25% of keys move (from Shard 0 to Shard 3).
```

```python
import hashlib
from bisect import bisect_right

class ConsistentHashRing:
    def __init__(self, nodes, virtual_nodes=150):
        self.ring = {}
        self.sorted_keys = []
        
        for node in nodes:
            for i in range(virtual_nodes):
                key = self._hash(f"{node}:{i}")
                self.ring[key] = node
                self.sorted_keys.append(key)
        
        self.sorted_keys.sort()
    
    def get_node(self, key: str) -> str:
        hash_val = self._hash(key)
        idx = bisect_right(self.sorted_keys, hash_val) % len(self.sorted_keys)
        return self.ring[self.sorted_keys[idx]]
    
    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

# Usage
ring = ConsistentHashRing(["shard-0", "shard-1", "shard-2"])
shard = ring.get_node("usr_abc123")  # → "shard-1"
```

---

## Concept: Resharding

When shards get too large, you need to split them.

```
Before: 3 shards, each at 80% capacity
After:  6 shards, each at 40% capacity

Migration plan:
1. Add new shard instances
2. Set up replication from old shards to new shards
3. Update routing to send new writes to correct shard
4. Backfill/migrate existing data
5. Cut over reads to new shards
6. Decommission old shard assignments
```

**This is painful.** Avoid resharding by:
- Starting with more shards than you need (logical shards > physical shards)
- Using consistent hashing (minimizes data movement)
- Planning for 10x growth from day one

---

## GhostDrop Implementation

```python
# shard_router.py
class ShardRouter:
    def __init__(self):
        self.shards = {
            "shard-0": create_db_pool("shard-0.db.ghostdrop.io"),
            "shard-1": create_db_pool("shard-1.db.ghostdrop.io"),
            "shard-2": create_db_pool("shard-2.db.ghostdrop.io"),
        }
        self.ring = ConsistentHashRing(list(self.shards.keys()))
    
    def get_connection(self, user_id: str):
        shard_name = self.ring.get_node(user_id)
        return self.shards[shard_name]
    
    def query_all_shards(self, query: str, params: tuple):
        """For cross-shard queries (e.g., admin, analytics)."""
        results = []
        for shard_pool in self.shards.values():
            results.extend(shard_pool.execute(query, params))
        return results

# Usage in application
router = ShardRouter()

def get_user_files(user_id: str):
    conn = router.get_connection(user_id)
    return conn.execute("SELECT * FROM files WHERE owner_id = %s", (user_id,))

def get_shared_with_me(user_id: str):
    # Must query all shards (share links are on owner's shard)
    return router.query_all_shards(
        "SELECT * FROM share_links WHERE recipient_id = %s",
        (user_id,)
    )
```

### Results

| Metric | Before (1 primary) | After (3 shards) |
|--------|--------------------|--------------------|
| Write capacity | 4,200/sec (ceiling) | 12,600/sec (3x) |
| Primary CPU | 78% | 26% per shard |
| Max DB size | 500GB (one instance) | 500GB × 3 = 1.5TB |
| Cost | $1,100/mo (one big instance) | $831/mo (3 smaller) |

---

## Tradeoffs

| Decision | Gain | Cost |
|----------|------|------|
| Shard by user_id | Most queries stay on one shard | Cross-shard for shared files |
| Consistent hashing | Minimal data movement on reshard | Slightly complex routing |
| 3 shards initially | 3x write capacity | Cross-shard query complexity |
| Logical shards > physical | Easy future resharding | Routing table management |

---

## Why Not Just...

**"Why not use a distributed database (CockroachDB, Spanner)?"**
They handle sharding automatically. But they add 5-10ms write latency (consensus protocol), cost significantly more, and require expertise your team doesn't have. PostgreSQL sharding is manual but well-understood.

**"Why not shard by file_id instead of user_id?"**
Then "get all files for user X" becomes a cross-shard query (scatter-gather across all shards). Since 90% of queries are per-user, sharding by user_id keeps most queries on a single shard.

**"Why not just use read replicas for writes too?"**
Replicas are read-only by design. Writes must go to a primary. Sharding gives you multiple primaries, each handling a subset of writes.

---

## Exercise

GhostDrop has a "trending files" feature showing the most downloaded files globally. With sharding, download counts are spread across shards.

1. How do you compute a global "top 10 most downloaded" across 3 shards?
2. What's the latency impact of querying all shards?
3. How would you optimize this for a frequently-accessed page?

<details>
<summary>Hint</summary>

Option 1: Query each shard for its local top 10, merge in the application (scatter-gather). Latency = slowest shard response. Option 2: Stream download events to a centralized analytics store (Redis sorted set or dedicated analytics DB). The trending page reads from this store, not from shards. Option 3: Precompute trending every 5 minutes via a background job that queries all shards and caches the result. The page reads from cache.
</details>

---

## Quick Reference

| Term | Definition |
|------|-----------|
| **Sharding** | Splitting data across multiple database instances |
| **Shard Key** | The field that determines which shard holds a row |
| **Consistent Hashing** | Hash ring that minimizes remapping when shards change |
| **Cross-Shard Query** | Query that must touch multiple shards (expensive) |
| **Hot Shard** | One shard receiving disproportionate traffic |
| **Resharding** | Splitting or rebalancing shards as data grows |
| **Scatter-Gather** | Query all shards, merge results in application |
| **Virtual Nodes** | Multiple hash ring positions per physical shard |

---

## What Breaks Next

Sharding handles the write load. Each shard operates independently. The database is no longer a bottleneck.

But the architecture is getting complex. Services need to react to events across the system: "file uploaded" triggers scanning, thumbnails, notifications, analytics. Currently this is point-to-point (each service knows about the others). Adding a new consumer means changing the producer.

"We need a central event bus," Sana says. "Services publish events. Other services subscribe. Nobody needs to know about each other."

You need event-driven architecture.

[← Ch 15](chapter-15-observability.md) | [Ch 17 →](chapter-17-event-driven.md)

# Chapter 10: Design a Distributed Cache (Redis Cluster)

[← Payment System](./chapter-09-payments.md) | [Next: Job Scheduler →](./chapter-11-scheduler.md)

---

## The Question

> "Design a distributed caching system like Redis Cluster. It should support key-value storage across multiple nodes, handle node failures gracefully, and provide consistent hashing for data distribution. Discuss eviction policies and cache invalidation strategies."

---

## Step 1: Requirements & Scope

**Functional:**
- Key-value store with GET, SET, DELETE operations
- TTL (time-to-live) support for automatic expiration
- Support for data structures (strings, lists, hashes, sorted sets)
- Cluster mode: data distributed across multiple nodes
- Replication for fault tolerance

**Non-functional:**
- Sub-millisecond latency for reads (<1ms p99)
- 1M operations/sec per node
- 100 nodes in cluster, ~10 TB total capacity
- High availability (survive node failures without data loss)
- Horizontal scaling (add nodes without downtime)

---

## Step 2: Estimation

| Metric | Calculation | Result |
|--------|-------------|--------|
| Total ops/sec | 100 nodes × 1M ops/node | 100M ops/sec |
| Memory per node | 10 TB / 100 nodes | ~100 GB per node |
| Network per node | 1M ops × 1KB avg | ~1 GB/sec per node |
| Replication factor | 3 copies | 30 TB raw storage |

---

## Step 3: API Design

```
SET key value [EX seconds] [NX|XX]
GET key
DEL key
EXPIRE key seconds
TTL key

-- Cluster operations
CLUSTER ADDNODE node_address
CLUSTER RESHARD source target slots
CLUSTER FAILOVER
```

---

## Step 4: Data Model

**In-memory data structure per node:**

```
HashMap<String, Entry>
  where Entry = {
    value: bytes,
    ttl: Option<timestamp>,
    type: String | List | Hash | SortedSet
  }

Slot assignment table:
  slot[0..16383] → node_id
```

**Cluster metadata (gossip protocol):**

| Field | Type |
|-------|------|
| node_id | UUID |
| address | IP:PORT |
| slots_owned | BitSet(16384) |
| status | ENUM (online, failing, offline) |
| master_of / replica_of | node_id |

---

## Step 5: High-Level Architecture

```
┌──────────┐     ┌──────────────┐
│  Client  │────▶│ Client Library│ (knows slot→node mapping)
└──────────┘     └──────┬───────┘
                        │
          ┌─────────────┼─────────────────────┐
          ▼             ▼                     ▼
   ┌────────────┐ ┌────────────┐      ┌────────────┐
   │  Node A    │ │  Node B    │      │  Node C    │
   │ slots 0-5K │ │ slots 5K-10K│     │ slots 10K-16K│
   │  [Master]  │ │  [Master]  │      │  [Master]  │
   └─────┬──────┘ └─────┬──────┘      └─────┬──────┘
         │               │                    │
         ▼               ▼                    ▼
   ┌────────────┐ ┌────────────┐      ┌────────────┐
   │  Node A'   │ │  Node B'   │      │  Node C'   │
   │  [Replica] │ │  [Replica] │      │  [Replica] │
   └────────────┘ └────────────┘      └────────────┘
```

---

## Step 6: Deep Dive

### Consistent Hashing

**Problem:** Adding/removing nodes shouldn't require moving all data.

**Hash slot approach (Redis style):**
1. Key space divided into 16,384 slots
2. `slot = CRC16(key) % 16384`
3. Each node owns a range of slots
4. Adding a node: reassign some slots from existing nodes (move only affected keys)

**Virtual nodes (alternative):** Each physical node maps to multiple points on hash ring. Provides better distribution with fewer physical nodes.

### Eviction Policies

When memory is full, which keys to remove?

| Policy | Strategy | Best For |
|--------|----------|----------|
| LRU | Least Recently Used | General purpose |
| LFU | Least Frequently Used | Skewed access patterns |
| Random | Random eviction | Simple, surprisingly effective |
| TTL-based | Evict keys closest to expiry | Time-sensitive data |
| noeviction | Return error on write | When data loss is unacceptable |

**Approximate LRU (Redis approach):** Don't track all access times. Sample 5 random keys, evict the least recently used among them. O(1) vs O(n) for true LRU.

### Replication

- Each master has 1-2 replicas (async replication)
- Writes go to master, replicated to replicas
- Reads can go to replicas (eventual consistency) or master (strong)
- On master failure: replica promoted to master (automatic failover)

**Trade-off:** Async replication = possible data loss on failure (last few writes). Sync replication = higher latency. Most choose async with acceptable small window of loss.

### Cache Invalidation Strategies

| Strategy | How It Works | Trade-off |
|----------|-------------|-----------|
| Cache-aside | App checks cache, on miss reads DB, writes to cache | Simple but risk of stale data |
| Write-through | Write to cache AND DB on every write | Consistent but slower writes |
| Write-behind | Write to cache, async flush to DB | Fast writes but risk of data loss |
| TTL-based | Keys expire after N seconds | Simple but stale within TTL window |

**Cache-aside pattern (most common):**
```
read(key):
  value = cache.get(key)
  if value is None:
    value = db.get(key)
    cache.set(key, value, ttl=300)
  return value

write(key, value):
  db.set(key, value)
  cache.delete(key)  // NOT cache.set — avoids race condition
```

### Thundering Herd Problem

**Scenario:** Popular key expires → 1000 concurrent requests all miss cache → all hit DB simultaneously.

**Solutions:**
1. **Locking:** First request acquires lock, others wait for cache fill
2. **Early expiration:** Refresh cache before TTL expires (background refresh)
3. **Stale-while-revalidate:** Serve stale value while one request refreshes
4. **Never expire hot keys:** Use explicit invalidation instead of TTL

---

## Step 7: Bottlenecks & Scaling

| Bottleneck | Solution |
|-----------|----------|
| Hot key (one key gets all traffic) | Replicate hot key across nodes, client-side cache |
| Node failure | Automatic failover to replica |
| Adding nodes (resharding) | Migrate slots incrementally, redirect during migration |
| Memory fragmentation | Jemalloc allocator, periodic defrag |
| Network partition | Split-brain prevention via quorum |

**Split-brain prevention:** During network partition, only the partition with majority of nodes accepts writes. Minority partition becomes read-only or rejects requests.

---

## Key Talking Points

- Consistent hashing (or hash slots) enables horizontal scaling
- Approximate LRU is O(1) and "good enough" in practice
- Cache-aside with delete-on-write avoids race conditions
- Thundering herd is a real production problem — locking or early refresh solves it
- Async replication trades small data loss risk for performance

---

## Common Mistakes

- Using modulo hashing (adding a node moves almost all keys)
- Cache-aside with set-on-write instead of delete-on-write (race condition)
- Not discussing what happens when a node dies mid-operation
- Ignoring the thundering herd problem for popular keys
- Synchronous replication everywhere (kills latency)
- Not mentioning memory limits and eviction (cache isn't infinite)

---

[← Payment System](./chapter-09-payments.md) | [Next: Job Scheduler →](./chapter-11-scheduler.md)

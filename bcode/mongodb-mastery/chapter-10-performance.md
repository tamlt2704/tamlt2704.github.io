# Chapter 10: Performance

[← Ch 9](chapter-09-search.md) | [Ch 11 →](chapter-11-ops.md)

---

## The Problem

> **Priya:** "We're getting alerts — p99 latency spiked to 3 seconds. Some queries are scanning millions of documents. We need to find the slow queries, fix them, and set up guardrails so this doesn't happen again."

Performance tuning in MongoDB: find the slow queries, understand why they're slow, and fix them with indexes, projections, and architecture changes.

---

## The Profiler — Find Slow Queries

```javascript
// Enable profiling for queries > 100ms
db.setProfilingLevel(2, { slowms: 100 })

// Level 0: off, Level 1: slow only, Level 2: all operations
db.setProfilingLevel(1, { slowms: 200 })

// Check current level
db.getProfilingStatus()

// Query the profiler collection
db.system.profile.find({ millis: { $gt: 500 } })
  .sort({ ts: -1 })
  .limit(5)

// Find the slowest queries
db.system.profile.find({
  op: "query",
  ns: "docuflow.contracts"
}).sort({ millis: -1 }).limit(10)
```

> **Production tip:** Use level 1 (slow only) in production. Level 2 logs everything and adds overhead.

---

## explain("executionStats") — Deep Dive

```javascript
db.contracts.find({ status: "active", value: { $gt: 50000 } })
  .sort({ createdAt: -1 })
  .explain("executionStats")
```

Key metrics:

```javascript
{
  executionStats: {
    nReturned: 47,              // Documents returned
    totalKeysExamined: 47,      // Index entries scanned
    totalDocsExamined: 47,      // Documents fetched
    executionTimeMillis: 3,     // Total time
    executionStages: {
      stage: "IXSCAN",         // ✅ Using index (not COLLSCAN)
      indexName: "status_1_createdAt_-1"
    }
  }
}
```

**Red flags:**

| Symptom | Problem | Fix |
|---|---|---|
| `COLLSCAN` | No index used | Create appropriate index |
| `totalDocsExamined >> nReturned` | Index not selective | Better compound index |
| `hasSortStage: true` with no index | In-memory sort | Add sort field to index |
| Large `executionTimeMillis` | Slow query | Index + projection |

---

## Covered Queries — Zero Document Fetches

```javascript
// Index covers all fields in query AND projection
db.contracts.createIndex({ status: 1, client: 1, value: 1 })

// Covered query — totalDocsExamined: 0
db.contracts.find(
  { status: "active" },
  { client: 1, value: 1, _id: 0 }
).explain("executionStats")
```

> Must exclude `_id` from projection (unless `_id` is in the index).

---

## Projection Optimization

```javascript
// ❌ Fetches entire document (including 50KB of clauses)
db.contracts.find({ status: "active" })

// ✅ Only fetch what you need
db.contracts.find(
  { status: "active" },
  { title: 1, client: 1, value: 1, status: 1 }
)

// ✅ Exclude large fields
db.contracts.find(
  { status: "active" },
  { clauses: 0, signatures: 0, "metadata.attachments": 0 }
)
```

---

## Connection Pooling

```javascript
// mongosh — check current connections
db.serverStatus().connections
// { current: 45, available: 51155, totalCreated: 1230 }

// Node.js — configure pool size
const client = new MongoClient('mongodb://localhost:27017', {
  maxPoolSize: 50,       // Max connections in pool
  minPoolSize: 5,        // Keep minimum ready
  maxIdleTimeMS: 30000,  // Close idle after 30s
  waitQueueTimeoutMS: 5000
});
```

---

## Read/Write Concerns

```javascript
// Write concern — how many replicas must acknowledge
db.contracts.insertOne(
  { title: "Critical Contract", value: 500000 },
  { writeConcern: { w: "majority", wtimeout: 5000 } }
)

// Read concern — what data is visible
db.contracts.find({ status: "active" }).readConcern("majority")

// Read preference — where to read from
db.contracts.find().readPref("secondaryPreferred")
```

| Write Concern | Durability | Speed |
|---|---|---|
| `w: 1` | Primary acknowledged | Fast |
| `w: "majority"` | Majority of replicas | Safer |
| `w: 0` | Fire and forget | Fastest (risky) |

| Read Concern | Guarantee |
|---|---|
| `"local"` | Latest on this node (default) |
| `"majority"` | Committed to majority |
| `"snapshot"` | Point-in-time (transactions) |

---

## Sharding Concepts

When a single replica set can't handle the load, shard across multiple servers.

```javascript
// Enable sharding on database
sh.enableSharding("docuflow")

// Shard a collection by orgId (range-based)
sh.shardCollection("docuflow.contracts", { orgId: 1 })

// Or hash-based for even distribution
sh.shardCollection("docuflow.auditLogs", { _id: "hashed" })
```

**Shard key selection:**

| Strategy | Good For | Bad For |
|---|---|---|
| Range (`orgId: 1`) | Range queries on shard key | Hot spots if uneven |
| Hashed (`_id: "hashed"`) | Even distribution | Range queries |
| Compound (`orgId: 1, createdAt: 1`) | Targeted queries | Complexity |

> Choose a shard key with high cardinality that matches your query patterns.

---

## Quick Wins Checklist

```javascript
// 1. Find queries without indexes
db.contracts.find({ client: "Acme" }).explain().queryPlanner.winningPlan.stage
// If "COLLSCAN" → needs index

// 2. Check index usage
db.contracts.aggregate([{ $indexStats: {} }])
// Unused indexes waste RAM — drop them

// 3. Check collection stats
db.contracts.stats()
// Look at: size, avgObjSize, totalIndexSize

// 4. Current operations (find long-running)
db.currentOp({ "secs_running": { $gt: 5 } })

// 5. Kill a slow operation
db.killOp(opId)
```

---

## Python Example — Monitoring

```python
from pymongo import MongoClient, ReadPreference

client = MongoClient(
    "mongodb://localhost:27017",
    maxPoolSize=50,
    readPreference=ReadPreference.SECONDARY_PREFERRED
)
db = client.docuflow

# Check slow queries from profiler
slow_queries = db.system.profile.find(
    {"millis": {"$gt": 200}, "op": "query"}
).sort("millis", -1).limit(5)

for q in slow_queries:
    print(f"[{q['millis']}ms] {q['ns']} — {q.get('command', {}).get('filter')}")
```

---

## What You Learned

- Profiler (`setProfilingLevel`) captures slow queries in `system.profile`
- `explain("executionStats")` reveals COLLSCAN vs IXSCAN and doc counts
- Covered queries (totalDocsExamined: 0) are the fastest possible reads
- Projections reduce network transfer and memory usage
- Connection pooling prevents connection storms
- Write concern trades durability for speed; read concern controls consistency
- Sharding distributes data across servers when vertical scaling isn't enough
- `$indexStats` finds unused indexes wasting RAM

---

[← Ch 9: Atlas Search](chapter-09-search.md) | [Ch 11: Security & Ops →](chapter-11-ops.md)

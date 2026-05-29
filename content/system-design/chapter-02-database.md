# Chapter 2: Database Design & Scaling

[← Chapter 1: Scalability](/blog/system-design/chapter-01-scalability) | [Chapter 3: Caching →](/blog/system-design/chapter-03-caching)

---

## SQL vs NoSQL — When to Use What

This isn't a religious debate. It's about **access patterns**.

| Factor            | SQL (PostgreSQL, MySQL)                        | NoSQL (MongoDB, DynamoDB, Cassandra)                |
| ----------------- | ---------------------------------------------- | --------------------------------------------------- |
| Schema            | Fixed, enforced                                | Flexible, schema-on-read                            |
| Relationships     | Joins are cheap                                | Joins are expensive or impossible                   |
| Transactions      | ACID guaranteed                                | Usually eventual consistency                        |
| Scale writes      | Hard (single master)                           | Easy (distributed by design)                        |
| Query flexibility | Any query via SQL                              | Limited to designed access patterns                 |
| Best for          | Complex queries, relationships, financial data | High write throughput, flexible schema, time-series |

**Decision framework:**

```
Need ACID transactions?          → SQL
Need complex joins/aggregations? → SQL
Need flexible queries ad-hoc?    → SQL
Schema changes frequently?       → NoSQL
Write-heavy (>10K writes/sec)?   → NoSQL
Data is denormalized anyway?     → NoSQL
Need horizontal scale day 1?     → NoSQL
```

---

## Database Indexing

Indexes are the #1 performance tool. Understand them deeply.

### How a B-Tree Index Works

```
Without index: Full table scan O(n)
┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
│ 1 │ 5 │ 3 │ 8 │ 2 │ 9 │ 4 │ 7 │ 6 │10 │  → scan all rows
└───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘

With B-Tree index: O(log n)
              ┌───┐
              │ 5 │
              └─┬─┘
         ┌──────┴──────┐
       ┌─┴─┐         ┌─┴─┐
       │ 2 │         │ 8 │
       └─┬─┘         └─┬─┘
      ┌──┴──┐       ┌──┴──┐
    ┌─┴┐  ┌┴─┐   ┌─┴┐  ┌┴──┐
    │1 │  │3,4│   │6,7│  │9,10│
    └──┘  └───┘   └───┘  └────┘
```

### Index Types

| Type      | Use Case                         | Example                                    |
| --------- | -------------------------------- | ------------------------------------------ |
| B-Tree    | Range queries, equality, sorting | `WHERE age > 25 ORDER BY name`             |
| Hash      | Exact equality only              | `WHERE email = 'x@y.com'`                  |
| GIN       | Full-text search, arrays, JSONB  | `WHERE tags @> '{java}'`                   |
| GiST      | Geospatial, range types          | `WHERE location <@ circle`                 |
| Partial   | Index subset of rows             | `CREATE INDEX ... WHERE status = 'active'` |
| Composite | Multi-column queries             | `INDEX(user_id, created_at)`               |

### Index Pitfalls

```sql
-- BAD: Index on (a, b) won't help with WHERE b = ?
-- Composite indexes work LEFT to RIGHT only
CREATE INDEX idx ON orders(user_id, status, created_at);

-- ✓ WHERE user_id = 1
-- ✓ WHERE user_id = 1 AND status = 'ACTIVE'
-- ✓ WHERE user_id = 1 AND status = 'ACTIVE' AND created_at > '2024-01-01'
-- ✗ WHERE status = 'ACTIVE'  (skips leftmost column)
-- ✗ WHERE created_at > '2024-01-01'  (skips leftmost columns)
```

**Write cost:** Every index slows down INSERT/UPDATE/DELETE. Don't index everything.

---

## Replication

### Master-Slave (Primary-Replica)

```
         Writes
           │
           ▼
    ┌─────────────┐
    │   Primary   │
    │  (Master)   │
    └──────┬──────┘
           │ WAL / binlog replication
     ┌─────┼─────┐
     ▼     ▼     ▼
  ┌─────┐┌─────┐┌─────┐
  │Rep 1││Rep 2││Rep 3│  ← Reads
  └─────┘└─────┘└─────┘
```

**Replication lag:** Replicas may be milliseconds to seconds behind. Reading from a replica right after writing to primary may return stale data.

**Solutions for replication lag:**

- Read-your-own-writes: route user's reads to primary for N seconds after a write
- Monotonic reads: pin a user to the same replica
- Causal consistency: track write timestamps

### Master-Master (Multi-Primary)

Both nodes accept writes. Conflict resolution needed.

```
┌─────────┐  ◀──sync──▶  ┌─────────┐
│Primary A│               │Primary B│
│(US-East)│               │(EU-West)│
└─────────┘               └─────────┘
```

**Conflict strategies:**

- Last-write-wins (LWW) — simple but can lose data
- Application-level merge — complex but correct
- CRDTs — conflict-free data structures (counters, sets)

---

## Sharding (Partitioning)

When a single database can't handle the load, split data across multiple instances.

### Sharding Strategies

**1. Hash-based sharding:**

```
shard = hash(user_id) % num_shards

user_id=123 → hash(123) % 4 = 3 → Shard 3
user_id=456 → hash(456) % 4 = 0 → Shard 0
```

Pros: Even distribution. Cons: Resharding is painful (all data moves).

**2. Range-based sharding:**

```
user_id 1-1M      → Shard A
user_id 1M-2M     → Shard B
user_id 2M-3M     → Shard C
```

Pros: Range queries stay on one shard. Cons: Hot spots (new users all hit latest shard).

**3. Consistent hashing:**

```
        Shard A
       /       \
  Node 3       Node 1
      \       /
       Shard B

Ring: 0 ──── 90 ──── 180 ──── 270 ──── 360
      │       │        │        │
    Shard A  Shard B  Shard C  Shard A
```

Pros: Adding/removing nodes only moves ~1/N of data. Used by DynamoDB, Cassandra.

### Sharding Challenges

| Problem             | Description                             | Solution                           |
| ------------------- | --------------------------------------- | ---------------------------------- |
| Cross-shard queries | `JOIN` across shards is expensive       | Denormalize, or use scatter-gather |
| Transactions        | No ACID across shards                   | Saga pattern, 2PC (slow)           |
| Resharding          | Adding shards requires data migration   | Consistent hashing, virtual nodes  |
| Hot spots           | One shard gets disproportionate traffic | Better shard key, split hot shard  |

---

## Database Patterns for Scale

### Connection Pooling

Database connections are expensive (~5-10ms to establish). Pool them.

```
Application Server
┌─────────────────────────────┐
│  Request 1 ──┐              │
│  Request 2 ──┼──▶ Pool ──▶ DB (max 20 connections)
│  Request 3 ──┘   (HikariCP) │
│  Request 4 ──── waits...    │
└─────────────────────────────┘
```

**HikariCP settings (Java):**

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20 # connections per instance
      minimum-idle: 5
      connection-timeout: 30000 # wait 30s for connection
      idle-timeout: 600000 # close idle after 10min
```

**Rule:** `pool_size = num_app_instances × max_pool_size` must be < DB's `max_connections`.

### Write-Ahead Log (WAL)

Every write goes to an append-only log first, then to the actual data pages. Guarantees durability even if the server crashes mid-write.

```
1. Write to WAL (sequential, fast)
2. Acknowledge to client
3. Later: flush WAL to data pages (background)
4. Checkpoint: mark WAL entries as applied
```

### Materialized Views

Pre-computed query results stored as a table. Trade storage for read speed.

```sql
-- Expensive query that runs often:
SELECT department, COUNT(*), AVG(salary)
FROM employees GROUP BY department;

-- Materialized view (PostgreSQL):
CREATE MATERIALIZED VIEW dept_stats AS
SELECT department, COUNT(*) as cnt, AVG(salary) as avg_sal
FROM employees GROUP BY department;

-- Refresh periodically:
REFRESH MATERIALIZED VIEW CONCURRENTLY dept_stats;
```

---

## Choosing the Right Database

| Use Case            | Best Choice            | Why                                         |
| ------------------- | ---------------------- | ------------------------------------------- |
| E-commerce orders   | PostgreSQL             | ACID, complex queries, relationships        |
| User sessions       | Redis                  | Fast reads, TTL expiry, key-value           |
| Product catalog     | MongoDB                | Flexible schema, nested documents           |
| Time-series metrics | TimescaleDB / InfluxDB | Optimized for time-range queries            |
| Social graph        | Neo4j / DGraph         | Relationship traversal                      |
| Search              | Elasticsearch          | Full-text, fuzzy, aggregations              |
| Chat messages       | Cassandra              | High write throughput, partition by chat_id |
| File metadata       | DynamoDB               | Predictable latency at any scale            |

---

## Interview Tips

When discussing databases in system design:

1. **State your access patterns first** — "We need to query by user_id and date range"
2. **Justify your choice** — "PostgreSQL because we need transactions for payments"
3. **Plan for growth** — "Start with single instance, add read replicas at 5K QPS, shard at 50K QPS"
4. **Mention indexes** — "Composite index on (user_id, created_at) for the timeline query"
5. **Address consistency** — "We can tolerate 1-2 second lag for the feed, but payments need strong consistency"

---

[Chapter 3: Caching Strategies →](/blog/system-design/chapter-03-caching)

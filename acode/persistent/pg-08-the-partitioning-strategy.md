# Chapter 8: The Partitioning Strategy — "2 Billion Rows in One Table"

[← The Replication Setup](pg-07-the-replication-setup.md) | [Next: The Backup Disaster →](pg-09-the-backup-disaster.md)

---

## The Incident

Tuesday, 2:15 PM. The daily analytics report that usually takes 3 minutes hasn't finished
in 45 minutes. Grafana shows the `transactions` table at **2.1 billion rows**. The
dashboard queries are crawling. VACUUM has been running for 6 hours and isn't done.

You check the table size:

```sql
SELECT pg_size_pretty(pg_total_relation_size('transactions'));
```

```
 pg_size_pretty
----------------
 847 GB
```

Priya pings you on Slack.

> **Priya:** "I tried to add an index on `(status, created_at)` for the new fraud
> detection query. It's been running for 11 hours. Should I cancel it?"

> **Viktor:** *(walking over)* "Yes. Cancel it. That index build is holding a lock and
> it won't finish before tomorrow."

Viktor sits down and pulls up the table stats.

> **Viktor:** "Two billion rows. Even with perfect indexes from [Chapter 2](pg-02-the-index-trap.md),
> you're hitting physical limits. The B-tree is 5 levels deep now — that's 5 disk reads
> per lookup instead of 3. VACUUM has to scan 847 GB. `pg_dump` takes 4 hours. One table
> can't hold the world. Time to partition."

---

## 1. Why Partition?

Viktor draws on the whiteboard:

```
┌──────────────────────────────────────────────────┐
│  PROBLEMS WITH A 2-BILLION-ROW TABLE             │
│                                                  │
│  1. Index depth: 5+ levels = more I/O per lookup │
│  2. VACUUM: must scan the entire 847 GB table    │
│  3. pg_dump: takes 4+ hours                      │
│  4. CREATE INDEX: locks table for days            │
│  5. Bloat: harder to manage at this scale        │
└──────────────────────────────────────────────────┘
```

> **Viktor:** "Partitioning splits one logical table into many physical tables. PostgreSQL
> routes queries to only the relevant partitions. VACUUM runs on each partition
> independently. You can drop an entire month of data instantly — no DELETE, no VACUUM,
> no bloat."

> **You:** "So it's like sharding but inside one database?"

> **Viktor:** "Exactly. Same SQL, same application code. PostgreSQL handles the routing
> transparently. Three types: **range**, **list**, and **hash**. Let's start with the
> one you'll use 90% of the time."

---

## 2. Range Partitioning (by Date)

> **Viktor:** "PayFlow's transactions are time-series data. Every query filters by date.
> Range partitioning by `created_at` is the natural fit."

```sql
CREATE TABLE transactions (
    id              BIGINT NOT NULL,
    from_account_id BIGINT NOT NULL,
    to_account_id   BIGINT NOT NULL,
    amount          NUMERIC(19,4) NOT NULL,
    status          VARCHAR(20) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL
) PARTITION BY RANGE (created_at);

CREATE TABLE transactions_2026_01 PARTITION OF transactions
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
CREATE TABLE transactions_2026_02 PARTITION OF transactions
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
```

> **Viktor:** "Each partition is a regular table. It has its own indexes, its own VACUUM
> schedule, its own storage. But you query `transactions` as if it's one table —
> PostgreSQL figures out which partitions to touch."

> **You:** "What about the existing 2 billion rows?"

> **Viktor:** "You migrate them. Create the partitioned table with a new name, create
> partitions for every month going back, then `INSERT INTO ... SELECT FROM` in batches.
> It's a project — not a one-liner. But once it's done, you never have this problem again."

---

## 3. Partition Pruning — The Magic

> **Viktor:** "Here's why partitioning works. Watch the EXPLAIN."

```sql
-- ✅ PG only scans transactions_2026_04
EXPLAIN ANALYZE
SELECT * FROM transactions
WHERE created_at >= '2026-04-01'
  AND created_at < '2026-05-01';
```

```
Append (actual time=0.02..45.3 rows=8500000)
  -> Seq Scan on transactions_2026_04
       Filter: (created_at >= ... AND created_at < ...)
       Rows Removed by Filter: 0
       Actual rows: 8500000
```

> **Viktor:** "One partition. 8.5 million rows instead of 2 billion. Now watch what
> happens without a date filter."

```sql
-- ⚠️ Without date filter, PG scans ALL partitions
EXPLAIN ANALYZE
SELECT * FROM transactions
WHERE from_account_id = 42;
```

```
Append (actual time=0.03..12847.5 rows=4200)
  -> Seq Scan on transactions_2025_01 ...
  -> Seq Scan on transactions_2025_02 ...
  -> Seq Scan on transactions_2025_03 ...
  ... (24 more partitions)
  -> Seq Scan on transactions_2026_04 ...
```

> **Viktor:** "Every single partition. This is the trap — if your query doesn't include
> the partition key in the WHERE clause, PostgreSQL can't prune. It scans everything.
> **Always include the partition key in your queries.**"

> **You:** "So every query needs a date filter?"

> **Viktor:** "For a range-partitioned table, yes. If you have queries that only filter
> by `from_account_id`, you need an index on each partition for that column. Partitioning
> doesn't replace indexes — it complements them."

---

## 4. List Partitioning (by Status)

> **Viktor:** "Range isn't the only option. Sometimes you want to split by category."

```sql
CREATE TABLE transactions (
    id              BIGINT NOT NULL,
    from_account_id BIGINT NOT NULL,
    to_account_id   BIGINT NOT NULL,
    amount          NUMERIC(19,4) NOT NULL,
    status          VARCHAR(20) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL
) PARTITION BY LIST (status);

CREATE TABLE txn_pending PARTITION OF transactions
    FOR VALUES IN ('PENDING');
CREATE TABLE txn_completed PARTITION OF transactions
    FOR VALUES IN ('COMPLETED');
CREATE TABLE txn_failed PARTITION OF transactions
    FOR VALUES IN ('FAILED');
```

> **Viktor:** "Think about PayFlow's access patterns. `PENDING` transactions are tiny —
> maybe 50,000 rows at any time — but queried constantly by the payment processor.
> `COMPLETED` is 1.9 billion rows and rarely touched except for reports."

> **Viktor:** "With list partitioning, the `PENDING` partition fits entirely in memory.
> Queries against it are instant. The `COMPLETED` partition is huge but only hit by
> nightly batch jobs. Hot/cold data separation — without changing a single query."

> **You:** "Can you combine range and list?"

> **Viktor:** "Yes — sub-partitioning. Partition by status at the top level, then by
> date range within each status. But don't over-engineer it. Start simple."

---

## 5. Hash Partitioning (for Even Distribution)

> **Viktor:** "The third type. Less common, but useful when you need even distribution."

```sql
CREATE TABLE transactions (
    id              BIGINT NOT NULL,
    from_account_id BIGINT NOT NULL,
    to_account_id   BIGINT NOT NULL,
    amount          NUMERIC(19,4) NOT NULL,
    status          VARCHAR(20) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL
) PARTITION BY HASH (from_account_id);

CREATE TABLE txn_p0 PARTITION OF transactions
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE txn_p1 PARTITION OF transactions
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE txn_p2 PARTITION OF transactions
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE txn_p3 PARTITION OF transactions
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

> **Viktor:** "Hash partitioning distributes rows evenly across partitions based on a
> hash of the column value. Each partition gets roughly 25% of the data."

> **You:** "When would I use this over range?"

> **Viktor:** "When you don't have a natural range key, or when you want parallel
> operations. Four partitions means VACUUM can run on 4 partitions simultaneously.
> Index builds can run in parallel. But there's no pruning — a query on
> `from_account_id = 42` still only hits one partition (the hash determines which one),
> but a query on `created_at` hits all four."

---

## 6. Partition Maintenance

> **Viktor:** "Partitioning isn't set-and-forget. You need to create new partitions
> before data arrives, and drop old ones when they expire."

Create future partitions (run monthly via `pg_cron`):

```sql
-- Run monthly via cron or pg_cron
CREATE TABLE transactions_2026_06 PARTITION OF transactions
    FOR VALUES FROM ('2026-06-01') TO ('2026-07-01');
```

> **Viktor:** "If a row arrives and no partition exists for its date, PostgreSQL throws
> an error. Not a slow query — an error. Your inserts fail. Always create partitions
> ahead of time."

Drop old partitions (instant, no VACUUM needed):

```sql
-- Detach first (safe, non-blocking in PG 14+)
ALTER TABLE transactions
    DETACH PARTITION transactions_2024_01 CONCURRENTLY;

-- Then drop — instant, no VACUUM, no bloat
DROP TABLE transactions_2024_01;
```

> **Viktor:** "Compare that to `DELETE FROM transactions WHERE created_at < '2024-02-01'`.
> That DELETE would take hours, generate massive WAL, and leave behind dead tuples that
> VACUUM has to clean up. Dropping a partition is instant."

---

## 7. Choosing the Right Strategy

| Type | Best For | Pruning | Distribution |
|---|---|---|---|
| **Range** | Time-series data | ✅ Date ranges | Uneven (recent partitions larger) |
| **List** | Status/category | ✅ Exact match | Depends on data |
| **Hash** | Parallel operations | ❌ No pruning | Even |

> **Viktor:** "For PayFlow, range by `created_at` is the answer. 90% of queries filter
> by date. Monthly partitions give us manageable sizes — about 35 GB each instead of
> 847 GB. VACUUM finishes in minutes instead of hours. Index builds take minutes instead
> of days."

---

## Verification

After migrating to partitioned tables, confirm pruning works:

```sql
-- Confirm partition pruning is enabled
SHOW enable_partition_pruning;
```

```
 enable_partition_pruning
--------------------------
 on
```

```sql
-- Verify only 1 partition is scanned
EXPLAIN (COSTS OFF)
SELECT * FROM transactions
WHERE created_at >= '2026-04-01'
  AND created_at < '2026-05-01';
```

```
Append
  ->  Seq Scan on transactions_2026_04
        Filter: (created_at >= ... AND created_at < ...)
```

> **Viktor:** "One partition. Not 24. That's the difference between a 45-minute query
> and a 3-second query."

---

## Key Takeaways

1. **Partition when a single table gets too large** — billions of rows, VACUUM taking hours, index builds taking days.
2. **Range partitioning** is the default choice for time-series data. Monthly partitions are a good starting point.
3. **Partition pruning** only works when the partition key is in the WHERE clause. Always include it.
4. **List partitioning** separates hot and cold data — tiny `PENDING` partition in memory, huge `COMPLETED` partition on disk.
5. **Hash partitioning** gives even distribution for parallel operations, but no pruning benefit.
6. **Create partitions ahead of time** — missing partitions cause INSERT errors, not slow queries.
7. **Dropping a partition is instant** — no DELETE, no VACUUM, no bloat. This is the killer feature.

---

## What's Next

Partitioning keeps the `transactions` table manageable. Monthly partitions, fast VACUUM,
instant data retention. The 847 GB monster is now twenty-four 35 GB tables that PostgreSQL
manages transparently.

But what happens when someone drops a partition by accident? Or the disk dies — again?
You survived the last disk failure with a 6-hour-old `pg_dump` and lost transactions.
Viktor set up replication in [Chapter 7](pg-07-the-replication-setup.md), but replication
isn't a backup. If someone runs a bad DELETE, the replica faithfully replicates the DELETE.

You need real backups. And right now, you don't have any.

[Next: The Backup Disaster →](pg-09-the-backup-disaster.md)

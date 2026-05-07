# Chapter 14: "The Table Has 200 Million Rows"

[← Chapter 13: Functions & Triggers](chapter-13-functions-triggers.md) | [Chapter 15: JSONB & Full-Text Search →](chapter-15-jsonb-fulltext.md)

---

## The Incident

Six months later. DataPulse has grown. The `orders` table has 200 million rows. Queries that used to take 50ms now take 12 seconds. `VACUUM` runs for 3 hours. Index rebuilds lock the table. Silent Sasha's monitoring shows disk I/O at 95%.

Sasha breaks character and sends a full sentence: "Partition the orders table by month. Do it this weekend."

---

## Why Partition?

A 200M-row table is like a library with every book on one shelf. Finding a book from January 2024 means scanning past books from 2019, 2020, 2021...

Partitioning splits one logical table into many physical tables (partitions). Each partition holds a subset of the data.

```
Before:                          After:
┌─────────────────────┐          ┌──────────────┐
│     orders          │          │ orders_2024_01│ ← Jan 2024
│  200,000,000 rows   │          ├──────────────┤
│                     │          │ orders_2024_02│ ← Feb 2024
│  (one giant table)  │          ├──────────────┤
│                     │          │ orders_2024_03│ ← Mar 2024
└─────────────────────┘          ├──────────────┤
                                 │ ...          │
                                 └──────────────┘
                                   ~3M rows each
```

Queries that filter by date only scan relevant partitions. VACUUM runs on small partitions independently. Old data can be dropped by detaching a partition — instant, no row-by-row delete.

---

## Range Partitioning (Most Common)

```sql
-- Create the partitioned table
CREATE TABLE orders_partitioned (
    id          BIGSERIAL,
    customer_id INTEGER NOT NULL,
    order_date  DATE NOT NULL,
    status      TEXT NOT NULL DEFAULT 'pending',
    total_cents INTEGER NOT NULL,
    PRIMARY KEY (id, order_date)  -- partition key must be in PK
) PARTITION BY RANGE (order_date);

-- Create partitions for each month
CREATE TABLE orders_2024_01 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE orders_2024_02 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

CREATE TABLE orders_2024_03 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');

-- ... one per month
```

### Partition Pruning

```sql
EXPLAIN ANALYZE
SELECT * FROM orders_partitioned
WHERE order_date >= '2024-02-01' AND order_date < '2024-03-01';
```

```
 Append  (actual time=0.015..0.892 rows=15234)
   ->  Seq Scan on orders_2024_02  (actual time=0.015..0.892 rows=15234)
         Filter: (order_date >= '2024-02-01' AND order_date < '2024-03-01')
```

Only `orders_2024_02` was scanned. The other 199 million rows were never touched. That's partition pruning.

---

## List Partitioning

Partition by discrete values instead of ranges:

```sql
CREATE TABLE tickets_partitioned (
    id          BIGSERIAL,
    customer_id INTEGER NOT NULL,
    subject     TEXT NOT NULL,
    priority    TEXT NOT NULL,
    status      TEXT NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (id, status)
) PARTITION BY LIST (status);

CREATE TABLE tickets_open PARTITION OF tickets_partitioned
    FOR VALUES IN ('open', 'in_progress');

CREATE TABLE tickets_closed PARTITION OF tickets_partitioned
    FOR VALUES IN ('resolved', 'closed');
```

Queries filtering by status only scan the relevant partition. Archiving closed tickets = detach the partition.

---

## Hash Partitioning

Distribute rows evenly across N partitions (for parallel processing):

```sql
CREATE TABLE events (
    id BIGSERIAL,
    customer_id INTEGER NOT NULL,
    event_type TEXT,
    created_at TIMESTAMPTZ,
    PRIMARY KEY (id, customer_id)
) PARTITION BY HASH (customer_id);

CREATE TABLE events_p0 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE events_p1 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE events_p2 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE events_p3 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

---

## Auto-Creating Partitions

You don't want to manually create a partition every month. Automate it:

```sql
CREATE OR REPLACE PROCEDURE create_monthly_partition(table_name TEXT, target_month DATE)
LANGUAGE plpgsql AS $$
DECLARE
    partition_name TEXT;
    start_date DATE;
    end_date DATE;
BEGIN
    start_date := date_trunc('month', target_month);
    end_date := start_date + interval '1 month';
    partition_name := format('%s_%s', table_name, to_char(start_date, 'YYYY_MM'));

    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF %I FOR VALUES FROM (%L) TO (%L)',
        partition_name, table_name, start_date, end_date
    );

    RAISE NOTICE 'Created partition: %', partition_name;
END;
$$;

-- Create next month's partition
CALL create_monthly_partition('orders_partitioned', CURRENT_DATE + interval '1 month');
```

Schedule this to run monthly — always create next month's partition before you need it.

---

## Dropping Old Data: Detach and Drop

The killer feature. Deleting 50 million rows takes hours and generates massive WAL. Detaching a partition is instant:

```sql
-- Detach (instant — no row scanning)
ALTER TABLE orders_partitioned DETACH PARTITION orders_2023_01;

-- Now it's a standalone table. Archive it, back it up, or drop it:
DROP TABLE orders_2023_01;
```

Compare:
- `DELETE FROM orders WHERE order_date < '2023-02-01'` → 45 minutes, locks, WAL bloat
- `ALTER TABLE ... DETACH PARTITION` → milliseconds

---

## VACUUM and Maintenance

### What VACUUM Does

PostgreSQL uses MVCC (Multi-Version Concurrency Control). When you UPDATE a row, the old version isn't deleted — it's marked as dead. VACUUM reclaims that space.

```sql
-- Manual vacuum
VACUUM orders;

-- Vacuum with analysis (updates statistics too)
VACUUM ANALYZE orders;

-- Full vacuum (rewrites the table — locks it!)
VACUUM FULL orders;  -- ⚠️ blocks all access
```

### Autovacuum

Postgres runs autovacuum automatically. But on large tables, it might not keep up. Check:

```sql
SELECT
    relname,
    n_dead_tup,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY n_dead_tup DESC;
```

### Tuning Autovacuum for Large Tables

```sql
ALTER TABLE orders SET (
    autovacuum_vacuum_scale_factor = 0.01,    -- vacuum after 1% dead tuples (default 20%)
    autovacuum_analyze_scale_factor = 0.005   -- analyze after 0.5% changes
);
```

With partitioning, autovacuum runs on each small partition independently — much faster than vacuuming a 200M-row table.

---

## Table Bloat

Dead rows accumulate between vacuums, causing "bloat" — the table takes more disk space than the live data needs.

```sql
-- Check table size vs estimated live data
SELECT
    relname,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
    n_live_tup,
    n_dead_tup,
    round(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 1) AS dead_pct
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 10;
```

If `dead_pct` is over 20%, you have a bloat problem. Solutions:
1. Tune autovacuum (more aggressive)
2. `VACUUM FULL` (rewrites table, but locks it)
3. Use `pg_repack` extension (online rebuild, no lock)

---

## Index Maintenance

Indexes bloat too. After heavy updates/deletes:

```sql
-- Check index bloat
SELECT
    indexrelname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    idx_scan AS times_used
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;

-- Rebuild a bloated index (locks the table briefly)
REINDEX INDEX idx_orders_customer_id;

-- Rebuild without locking (PostgreSQL 12+)
REINDEX INDEX CONCURRENTLY idx_orders_customer_id;
```

---

## Quick Reference

```
────────────────────────────────────┬──────────────────────────────────────
Command                             │ What It Does
────────────────────────────────────┼──────────────────────────────────────
PARTITION BY RANGE (col)            │ Split by value ranges (dates, IDs)
PARTITION BY LIST (col)             │ Split by discrete values
PARTITION BY HASH (col)             │ Split evenly across N partitions
CREATE TABLE ... PARTITION OF ...   │ Create a partition
ALTER TABLE ... DETACH PARTITION    │ Remove partition (instant)
ALTER TABLE ... ATTACH PARTITION    │ Add existing table as partition
────────────────────────────────────┼──────────────────────────────────────
VACUUM table                        │ Reclaim dead row space
VACUUM ANALYZE table                │ Reclaim + update statistics
VACUUM FULL table                   │ Rewrite table (locks!)
REINDEX INDEX CONCURRENTLY idx      │ Rebuild index without locking
────────────────────────────────────┼──────────────────────────────────────
pg_stat_user_tables                 │ Table statistics (dead tuples, etc.)
pg_total_relation_size(table)       │ Total size including indexes
────────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Priya: "Products need flexible attributes. Some have color and size. Some have weight and dimensions. Some have custom fields the customer defines. I don't want 50 nullable columns."

JSONB. Arrays. Full-text search. PostgreSQL's secret weapons.

---

[← Chapter 13: Functions & Triggers](chapter-13-functions-triggers.md) | [Chapter 15: JSONB & Full-Text Search →](chapter-15-jsonb-fulltext.md)

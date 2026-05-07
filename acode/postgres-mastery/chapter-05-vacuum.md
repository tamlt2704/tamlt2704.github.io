# Chapter 5: VACUUM — Cleaning Up the Dead

[← Chapter 4: The Planner](chapter-04-planner.md) | [Chapter 6: Advanced Queries →](chapter-06-advanced-queries.md)

---

## The Fire

Wednesday. Ops Olga pulls up disk usage:

> "The `matches` table is 12GB on disk. But `SELECT pg_size_pretty(pg_total_relation_size('matches'))` says 12GB, while the actual live data is only 8GB. We're wasting 4GB. And it's growing."

You check:

```sql
SELECT
    relname,
    n_live_tup,
    n_dead_tup,
    round(n_dead_tup::numeric / NULLIF(n_live_tup, 0) * 100, 1) AS dead_pct,
    last_autovacuum
FROM pg_stat_user_tables
WHERE relname = 'matches';
```

```
 relname | n_live_tup | n_dead_tup | dead_pct | last_autovacuum
---------+------------+------------+----------+-----------------
 matches | 47000000   | 18800000   |   40.0   | 2024-01-15 03:22
```

**40% dead tuples.** Autovacuum hasn't run in 3 days. The table is bloated. Queries scan dead rows. Indexes point to dead rows. Everything is slower than it should be.

Marta explains:

> "Postgres never deletes data in place. It marks rows as dead and moves on. VACUUM is the janitor that cleans up. Your janitor hasn't shown up in 3 days."

---

## The Concept: MVCC and Dead Tuples

PostgreSQL uses **Multi-Version Concurrency Control (MVCC)**:

```
UPDATE players SET elo_rating = 1500 WHERE id = 42;

What actually happens:
1. The old row (elo_rating = 1200) is marked as "dead" (invisible to new transactions)
2. A new row (elo_rating = 1500) is inserted
3. The old row stays on disk until VACUUM removes it

DELETE FROM matches WHERE id = 99;

What actually happens:
1. The row is marked as "dead"
2. It still takes up space on disk
3. VACUUM will eventually reclaim the space
```

Why? Because other transactions might still need to see the old version (isolation levels). Once no transaction can see it, it's safe to clean up.

---

## The Diagnosis: Bloat Detection

### Method 1: pg_stat_user_tables

```sql
SELECT
    schemaname, relname,
    n_live_tup, n_dead_tup,
    round(n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0) * 100, 1) AS bloat_pct,
    last_autovacuum, last_autoanalyze
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;
```

### Method 2: Actual Table Size vs Expected Size

```sql
SELECT
    relname,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
    pg_size_pretty(pg_relation_size(relid)) AS table_size,
    pg_size_pretty(pg_indexes_size(relid)) AS index_size
FROM pg_stat_user_tables
WHERE relname IN ('players', 'matches', 'game_events')
ORDER BY pg_total_relation_size(relid) DESC;
```

### Method 3: pgstattuple Extension

```sql
CREATE EXTENSION IF NOT EXISTS pgstattuple;

SELECT * FROM pgstattuple('matches');
-- Shows: dead_tuple_count, dead_tuple_len, free_space, free_percent
```

---

## The Fix: VACUUM

### Manual VACUUM

```sql
-- Clean dead tuples (doesn't lock the table)
VACUUM matches;

-- Clean and update statistics
VACUUM ANALYZE matches;

-- Reclaim disk space (locks the table — use carefully!)
VACUUM FULL matches;
```

| VACUUM Type | Locks Table? | Reclaims Disk? | Use When |
|-------------|-------------|----------------|----------|
| `VACUUM` | No (concurrent) | No (marks space reusable) | Regular maintenance |
| `VACUUM ANALYZE` | No | No | After bulk changes |
| `VACUUM FULL` | Yes (exclusive lock!) | Yes (rewrites table) | Extreme bloat, maintenance window |

### Why Not Always VACUUM FULL?

`VACUUM FULL` rewrites the entire table. On a 12GB table with 47M rows:
- Takes 10-30 minutes
- Locks the table the entire time (no reads or writes!)
- Requires 12GB of free disk space (writes a new copy)

For PingPong with 24/7 traffic: **never use VACUUM FULL in production**.

---

## Autovacuum Tuning

Autovacuum runs automatically but has conservative defaults:

```sql
-- Default settings
SHOW autovacuum_vacuum_threshold;       -- 50 (minimum dead tuples)
SHOW autovacuum_vacuum_scale_factor;    -- 0.2 (20% of table must be dead)
SHOW autovacuum_naptime;                -- 1min (check interval)
SHOW autovacuum_max_workers;            -- 3
```

For a 47M row table: autovacuum triggers after **9.4 million dead tuples** (20%). That's way too late.

### Per-Table Tuning

```sql
-- Aggressive autovacuum for the matches table
ALTER TABLE matches SET (
    autovacuum_vacuum_scale_factor = 0.02,    -- Trigger at 2% dead (940K rows)
    autovacuum_vacuum_threshold = 50000,
    autovacuum_analyze_scale_factor = 0.01
);

-- Even more aggressive for game_events (high write volume)
ALTER TABLE game_events SET (
    autovacuum_vacuum_scale_factor = 0.01,    -- Trigger at 1% dead
    autovacuum_vacuum_threshold = 100000,
    autovacuum_vacuum_cost_limit = 2000       -- Let it work faster
);
```

### Global Tuning

```sql
-- Let autovacuum workers do more work per cycle
ALTER SYSTEM SET autovacuum_vacuum_cost_limit = 2000;  -- Default: 200
ALTER SYSTEM SET autovacuum_max_workers = 5;            -- Default: 3
SELECT pg_reload_conf();
```

---

## pg_repack: VACUUM FULL Without the Lock

When a table is severely bloated but you can't lock it:

```bash
# Install pg_repack
# Ubuntu: sudo apt install postgresql-16-repack
# Docker: use a postgres image with pg_repack

# Repack the matches table (no exclusive lock!)
pg_repack -d pingpong -t matches
```

`pg_repack` creates a new copy of the table in the background, applies changes via triggers, then swaps the tables atomically. No downtime.

```sql
-- Before pg_repack
SELECT pg_size_pretty(pg_relation_size('matches'));  -- 12 GB

-- After pg_repack
SELECT pg_size_pretty(pg_relation_size('matches'));  -- 8 GB
```

---

## Preventing Bloat

### Long-Running Transactions Block VACUUM

```sql
-- Find transactions that are blocking vacuum
SELECT
    pid,
    now() - xact_start AS duration,
    state,
    query
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
  AND state != 'idle'
ORDER BY xact_start ASC
LIMIT 5;
```

A transaction open for 2 hours means VACUUM can't clean any rows created after that transaction started. Kill long-running transactions:

```sql
-- Terminate a blocking session
SELECT pg_terminate_backend(12345);
```

### Monitor Autovacuum Progress

```sql
-- Is autovacuum running right now?
SELECT
    relid::regclass AS table_name,
    phase,
    heap_blks_total,
    heap_blks_scanned,
    round(heap_blks_scanned::numeric / NULLIF(heap_blks_total, 0) * 100, 1) AS pct_done
FROM pg_stat_progress_vacuum;
```

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `VACUUM tablename` | Clean dead tuples (no lock) |
| `VACUUM ANALYZE tablename` | Clean + update stats |
| `VACUUM FULL tablename` | Reclaim disk (locks table!) |
| `pg_repack -t tablename` | Reclaim disk without lock |
| `pg_stat_user_tables` | Check dead tuple counts |
| `pgstattuple('tablename')` | Detailed bloat info |

| Setting | Default | Recommended (Hot Tables) |
|---------|---------|--------------------------|
| `autovacuum_vacuum_scale_factor` | 0.2 | 0.01–0.05 |
| `autovacuum_vacuum_threshold` | 50 | 10000–100000 |
| `autovacuum_vacuum_cost_limit` | 200 | 1000–2000 |
| `autovacuum_max_workers` | 3 | 4–6 |

---

## Exercises

### Exercise 1: Create and Measure Bloat

```sql
-- 1. Create a test table
CREATE TABLE bloat_test AS SELECT generate_series(1, 1000000) AS id, 'data' AS val;

-- 2. Delete 50% of rows
DELETE FROM bloat_test WHERE id % 2 = 0;

-- 3. Check the size (still the same!)
SELECT pg_size_pretty(pg_relation_size('bloat_test'));

-- 4. VACUUM it
VACUUM bloat_test;

-- 5. Check size again. Did it shrink? Why or why not?
-- 6. Now try VACUUM FULL. What happens?
```

### Exercise 2: Autovacuum Monitoring

Write a query that shows all tables where dead tuples exceed 10% of live tuples. Sort by dead tuple percentage descending.

### Exercise 3: Transaction Bloat

1. Open a transaction: `BEGIN;`
2. In another session, delete 100,000 rows from a test table
3. Run `VACUUM` on that table
4. Check if the space was reclaimed
5. Commit the first transaction, VACUUM again. What changed?

---

## What Happens Next

The table is clean. Autovacuum is tuned. Dead tuples are under control. But Thursday brings a new challenge — Marta needs complex reports:

> "Show me each player's win streak, their rank within their ELO bracket, and a running total of matches played per week. One query."

Time to learn CTEs and advanced query patterns.

---

[← Chapter 4: The Planner](chapter-04-planner.md) | [Chapter 6: Advanced Queries →](chapter-06-advanced-queries.md)

# Chapter 1: Finding the Killer Query

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: EXPLAIN ANALYZE →](chapter-02-explain-analyze.md)

---

## The Fire

Monday, 7:42 AM. Ops Olga's message hits Slack like a brick:

> "CPU at 94%. Average query latency 1.2s. Matchmaking is timing out. Players can't start games. Revenue loss: $8,000/hour."

You open `htop` on the database server. Postgres is eating all 16 cores. But *which query*? There are 400 active connections running thousands of queries per second. You can't just guess.

Marta leans over:

> "Don't guess. Ask Postgres. It keeps a diary."

---

## The Diagnosis: pg_stat_statements

PostgreSQL tracks every query it runs — how many times, how long, how many rows. You just need to ask.

### Step 1: Enable the Extension

```sql
-- Check if it's already loaded
SELECT * FROM pg_available_extensions WHERE name = 'pg_stat_statements';

-- Enable it (requires shared_preload_libraries — already set in Ch 0)
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

### Step 2: Find the Top Offenders by Total Time

```sql
SELECT
    substring(query, 1, 80) AS short_query,
    calls,
    round(total_exec_time::numeric, 2) AS total_ms,
    round(mean_exec_time::numeric, 2) AS mean_ms,
    rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
```

Output:

```
         short_query                          | calls  | total_ms    | mean_ms | rows
---------------------------------------------+--------+-------------+---------+---------
 SELECT * FROM matches WHERE player1_id = $1 | 892341 | 4821903.21  | 5.40    | 892341
 SELECT * FROM game_events WHERE match_id... | 284102 | 3102847.55  | 10.92   | 5682040
 SELECT p.*, COUNT(m.*) FROM players p LEF... | 12847  | 1847291.03  | 143.79  | 12847
 UPDATE players SET elo_rating = $1 WHERE... | 441092 |  892041.22  | 2.02    | 441092
```

There it is. The first query — `SELECT * FROM matches WHERE player1_id = $1` — has been called **892,341 times** and takes 5.4ms each. That's 4,821 seconds of total CPU time. One query. Eating the server alive.

### Step 3: Find Queries by Mean Time (Slowest Individual Queries)

```sql
SELECT
    substring(query, 1, 80) AS short_query,
    calls,
    round(mean_exec_time::numeric, 2) AS mean_ms,
    round((100 * total_exec_time / sum(total_exec_time) OVER ())::numeric, 2) AS pct
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### Step 4: The Slow Query Log (Alternative Approach)

If `pg_stat_statements` isn't available, configure the slow query log:

```sql
-- Log queries taking more than 500ms
ALTER SYSTEM SET log_min_duration_statement = 500;
SELECT pg_reload_conf();

-- Check the log
-- Location: /var/log/postgresql/ or docker logs pg-dev
```

---

## The Fix: Identifying What to Attack First

You now have a hit list. The strategy:

```
Priority = total_exec_time (not mean_exec_time)

Why? A query that takes 200ms but runs 50,000 times/day
     is worse than one that takes 5 seconds but runs 10 times/day.

     200ms × 50,000 = 10,000 seconds of CPU
     5,000ms × 10    = 50 seconds of CPU
```

### The PingPong Hit List

```sql
-- Create a view for easy monitoring
CREATE VIEW query_hit_list AS
SELECT
    queryid,
    substring(query, 1, 100) AS short_query,
    calls,
    round(total_exec_time::numeric / 1000, 2) AS total_seconds,
    round(mean_exec_time::numeric, 2) AS mean_ms,
    rows,
    round((100 * total_exec_time / sum(total_exec_time) OVER ())::numeric, 2) AS pct_total
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat%'
ORDER BY total_exec_time DESC;
```

```sql
-- Check it
SELECT * FROM query_hit_list LIMIT 5;
```

### Reset Stats After Fixing

```sql
-- After you fix a query, reset to see fresh numbers
SELECT pg_stat_statements_reset();
```

---

## Why This Works

`pg_stat_statements` aggregates query statistics at the **statement level**. It normalizes queries by replacing literal values with `$1`, `$2`, etc., so:

```sql
SELECT * FROM matches WHERE player1_id = 42;
SELECT * FROM matches WHERE player1_id = 99;
```

Both count as the same query: `SELECT * FROM matches WHERE player1_id = $1`.

Key columns:

| Column | What It Means |
|--------|---------------|
| `calls` | How many times this query ran |
| `total_exec_time` | Total milliseconds spent executing (across all calls) |
| `mean_exec_time` | Average time per call |
| `rows` | Total rows returned (across all calls) |
| `shared_blks_hit` | Pages found in cache (good) |
| `shared_blks_read` | Pages read from disk (expensive) |

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `CREATE EXTENSION pg_stat_statements` | Enable query tracking |
| `SELECT * FROM pg_stat_statements ORDER BY total_exec_time DESC` | Find top offenders |
| `pg_stat_statements_reset()` | Clear stats (do after fixing) |
| `log_min_duration_statement = 500` | Log queries > 500ms |
| `pg_stat_statements.track = all` | Track nested queries too |
| `pg_stat_statements.max = 10000` | Track more unique queries |

---

## Common Patterns in pg_stat_statements

### Pattern: The "Called Too Often" Query

```sql
-- Queries called millions of times (even if each is fast)
SELECT substring(query, 1, 80), calls, round(mean_exec_time::numeric, 3)
FROM pg_stat_statements
WHERE calls > 100000
ORDER BY calls DESC
LIMIT 5;
```

If a query is called 500,000 times per day at 0.5ms each, that's still 250 seconds of CPU. Often these are N+1 queries from an ORM (we'll fix those in Chapter 10).

### Pattern: The "Disk Hog" Query

```sql
-- Queries reading the most data from disk
SELECT
    substring(query, 1, 80) AS short_query,
    shared_blks_read,
    shared_blks_hit,
    round(shared_blks_hit::numeric / NULLIF(shared_blks_hit + shared_blks_read, 0) * 100, 1) AS cache_pct
FROM pg_stat_statements
ORDER BY shared_blks_read DESC
LIMIT 5;
```

A query with low `cache_pct` is reading from disk instead of memory. Either the table doesn't fit in `shared_buffers`, or the query scans too many pages.

### Pattern: The "Row Explosion" Query

```sql
-- Queries that return way more rows than needed
SELECT
    substring(query, 1, 80),
    calls,
    rows,
    rows / NULLIF(calls, 0) AS rows_per_call
FROM pg_stat_statements
WHERE rows / NULLIF(calls, 0) > 10000
ORDER BY rows DESC
LIMIT 5;
```

A query returning 100,000 rows per call is probably missing a LIMIT or doing a full table dump.

---

## Exercises

### Exercise 1: Build Your Own Hit List

Connect to your local PingPong database and run:

```sql
-- Generate some load first
SELECT * FROM matches WHERE player1_id = 1;
SELECT * FROM matches WHERE player1_id = 2;
SELECT * FROM game_events WHERE match_id = 100;

-- Now find the top 5 queries by total time
-- Write the query yourself before checking the solution above
```

### Exercise 2: Percentage of Total

Write a query against `pg_stat_statements` that shows each query's percentage of total database time. Which single query is responsible for the most CPU?

### Exercise 3: Cache Hit Ratio

Using `pg_stat_statements`, calculate the cache hit ratio for the top 5 queries:

```sql
-- Formula: shared_blks_hit / (shared_blks_hit + shared_blks_read)
-- A ratio below 0.95 means the query is hitting disk too often
SELECT
    substring(query, 1, 60) AS short_query,
    calls,
    round(
        shared_blks_hit::numeric /
        NULLIF(shared_blks_hit + shared_blks_read, 0),
        3
    ) AS cache_hit_ratio
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 5;
```

---

## What Happens Next

You've found the killer: `SELECT * FROM matches WHERE player1_id = $1`. It runs nearly a million times a day with no index. But before you slap an index on it, you need to understand *why* it's slow. That means reading the query plan.

Marta says:

> "Never add an index without reading the EXPLAIN first. You might be solving the wrong problem."

Next chapter: you learn to read query plans like a detective reads a crime scene.

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: EXPLAIN ANALYZE →](chapter-02-explain-analyze.md)

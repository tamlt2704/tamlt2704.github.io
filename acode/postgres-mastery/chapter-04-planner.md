# Chapter 4: The Planner — Why Postgres Ignores Your Index

[← Chapter 3: Indexes](chapter-03-indexes.md) | [Chapter 5: VACUUM →](chapter-05-vacuum.md)

---

## The Fire

Tuesday morning. You added `idx_matches_player1_id` yesterday. The matchmaking query should be fast now. But Ops Olga shows you the EXPLAIN:

```sql
EXPLAIN ANALYZE
SELECT * FROM matches WHERE status = 'pending';
```

```
Seq Scan on matches  (cost=0.00..1284721.00 rows=9400000 width=89)
                     (actual time=0.012..6891.334 rows=47000 loops=1)
  Filter: (status = 'pending'::text)
  Rows Removed by Filter: 46953000
```

There's an index on `status`. Postgres ignores it. And look at the estimates: it expected **9.4 million rows** but got **47,000**. The planner thinks 20% of matches are pending. In reality, it's 0.1%.

Marta explains:

> "The planner uses statistics to decide. If the statistics are wrong, the plan is wrong. Garbage in, garbage out."

---

## The Diagnosis: Stale Statistics

### Check What the Planner Believes

```sql
SELECT
    attname,
    n_distinct,
    most_common_vals,
    most_common_freqs
FROM pg_stats
WHERE tablename = 'matches' AND attname = 'status';
```

```
 attname | n_distinct | most_common_vals                          | most_common_freqs
---------+------------+-------------------------------------------+---------------------------
 status  |          4 | {completed,cancelled,active,pending}      | {0.75,0.15,0.08,0.02}
```

Wait — the planner thinks `pending` is 2% of rows. But the actual data changed. A batch job completed 9 million pending matches last night. The statistics are from *before* that job ran.

### When Were Stats Last Updated?

```sql
SELECT
    relname,
    last_analyze,
    last_autoanalyze,
    n_live_tup,
    n_dead_tup
FROM pg_stat_user_tables
WHERE relname = 'matches';
```

```
 relname | last_analyze | last_autoanalyze | n_live_tup | n_dead_tup
---------+--------------+------------------+------------+------------
 matches | NULL         | 2024-01-15 03:22 | 47000000   | 9400000
```

Last autoanalyze was 3 days ago. The data has changed dramatically since then.

---

## The Fix: ANALYZE

```sql
-- Update statistics for the matches table
ANALYZE matches;

-- Now check the plan again
EXPLAIN ANALYZE
SELECT * FROM matches WHERE status = 'pending';
```

```
Index Scan using idx_matches_status on matches
    (cost=0.56..4821.23 rows=47102 width=89)
    (actual time=0.031..42.891 rows=47000 loops=1)
  Index Cond: (status = 'pending'::text)
```

The planner now knows `pending` is 0.1% of rows (47K out of 47M). An Index Scan is clearly better than a Seq Scan. From 6.8 seconds to 42ms.

---

## Why the Planner Makes Decisions

The planner's logic:

```
IF (estimated rows / total rows) > ~5-10%:
    Seq Scan is cheaper (sequential I/O is fast)
ELSE:
    Index Scan is cheaper (random I/O but fewer pages)
```

The threshold depends on `random_page_cost` vs `seq_page_cost`:

```sql
SHOW random_page_cost;  -- 4.0 (default: random I/O is 4x more expensive)
SHOW seq_page_cost;     -- 1.0

-- If your data is on SSD, random I/O is nearly as fast as sequential:
SET random_page_cost = 1.1;  -- Tell the planner "disk is fast"
```

### Selectivity

The planner calculates **selectivity** — what fraction of rows match a condition:

```
selectivity = estimated matching rows / total rows

status = 'pending':
  Old stats: 9,400,000 / 47,000,000 = 0.20 (20%) → Seq Scan
  New stats: 47,000 / 47,000,000 = 0.001 (0.1%) → Index Scan
```

### Correlation

Even with good selectivity, the planner considers **correlation** — how physically ordered the data is on disk:

```sql
SELECT attname, correlation
FROM pg_stats
WHERE tablename = 'matches' AND attname = 'started_at';
```

```
 attname    | correlation
------------+-------------
 started_at | 0.998
```

Correlation near 1.0 means the data is physically sorted by `started_at`. An index scan on `started_at` reads pages sequentially — very efficient.

Correlation near 0.0 means random order. An index scan would jump all over the disk — the planner might prefer a Seq Scan even for selective queries.

---

## Autovacuum and ANALYZE

Autovacuum runs ANALYZE automatically, but it has thresholds:

```sql
-- Default: analyze after 10% of rows change
SHOW autovacuum_analyze_threshold;      -- 50 (minimum rows)
SHOW autovacuum_analyze_scale_factor;   -- 0.1 (10% of table)
```

For a 47M row table: ANALYZE triggers after 4.7M rows change. If a batch job changes 9M rows at once, autovacuum will catch it — but maybe not for hours.

### Tune Autovacuum for Hot Tables

```sql
-- Make autovacuum more aggressive for the matches table
ALTER TABLE matches SET (
    autovacuum_analyze_scale_factor = 0.02,  -- Analyze after 2% change
    autovacuum_analyze_threshold = 10000
);
```

---

## Debugging the Planner

### Force an Index Scan (Testing Only)

```sql
-- Disable seq scan to see if the index plan is better
SET enable_seqscan = off;
EXPLAIN ANALYZE SELECT * FROM matches WHERE status = 'pending';
SET enable_seqscan = on;  -- Always turn it back on!
```

If the forced Index Scan is faster, the planner's statistics are wrong. Run ANALYZE.

If the forced Index Scan is *slower*, the planner was right to choose Seq Scan.

### Check Row Estimates

```sql
-- Compare estimated vs actual for every node
EXPLAIN ANALYZE
SELECT * FROM matches
WHERE game_mode = 'ranked'
  AND status = 'completed'
  AND started_at > '2024-01-01';
```

Look for nodes where `rows=X` (estimated) differs wildly from `actual rows=Y`. That's where statistics are wrong.

### Extended Statistics (Correlated Columns)

The planner assumes columns are independent. But `game_mode` and `status` might be correlated (ranked matches are rarely cancelled):

```sql
-- Tell Postgres these columns are correlated
CREATE STATISTICS stat_matches_mode_status (dependencies)
ON game_mode, status FROM matches;

ANALYZE matches;
```

Now the planner knows that `game_mode = 'ranked' AND status = 'cancelled'` is rarer than independence would suggest.

---

## The Complete Fix for PingPong

```sql
-- 1. Update statistics on all tables
ANALYZE players;
ANALYZE matches;
ANALYZE game_events;

-- 2. Tune autovacuum for hot tables
ALTER TABLE matches SET (autovacuum_analyze_scale_factor = 0.02);
ALTER TABLE game_events SET (autovacuum_analyze_scale_factor = 0.01);

-- 3. Adjust random_page_cost for SSD
ALTER SYSTEM SET random_page_cost = 1.1;
SELECT pg_reload_conf();

-- 4. Create extended statistics for correlated columns
CREATE STATISTICS stat_matches_mode_status (dependencies)
ON game_mode, status FROM matches;

ANALYZE matches;
```

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `ANALYZE tablename` | Update statistics for one table |
| `ANALYZE` | Update statistics for all tables |
| `pg_stats` | View current statistics per column |
| `SET enable_seqscan = off` | Force index usage (testing only!) |
| `random_page_cost` | How expensive random I/O is (lower = prefer indexes) |
| `CREATE STATISTICS ... (dependencies)` | Correlated column stats |

| Diagnostic | What to Check |
|-----------|---------------|
| `estimated rows` vs `actual rows` | If >10x off, stats are stale |
| `correlation` in pg_stats | Physical ordering of data |
| `last_autoanalyze` | When stats were last refreshed |
| `n_dead_tup` | Dead rows affecting estimates |

---

## Exercises

### Exercise 1: Stale Statistics Experiment

1. Insert 100,000 rows into `matches` with `status = 'tournament'`
2. Run EXPLAIN ANALYZE on `SELECT * FROM matches WHERE status = 'tournament'`
3. Note the estimated vs actual rows
4. Run `ANALYZE matches`
5. Re-run the EXPLAIN. How did the estimate change?

### Exercise 2: Correlation Impact

```sql
-- Check correlation for different columns
SELECT attname, correlation
FROM pg_stats
WHERE tablename = 'game_events';
```

Which column has the highest correlation? Why? How does this affect index scan efficiency?

### Exercise 3: Extended Statistics

Create a query that benefits from extended statistics on `matches(game_mode, status)`. Show the EXPLAIN before and after creating the statistics object.

---

## What Happens Next

Statistics are fresh. Indexes are being used. But Wednesday morning, Ops Olga notices something else:

> "The `matches` table is 12GB on disk but only has 8GB of actual data. What's the other 4GB?"

Dead tuples. The ghosts of deleted and updated rows that nobody cleaned up. Time to learn about VACUUM.

---

[← Chapter 3: Indexes](chapter-03-indexes.md) | [Chapter 5: VACUUM →](chapter-05-vacuum.md)

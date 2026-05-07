# Chapter 2: EXPLAIN ANALYZE — Reading the Crime Scene

[← Chapter 1: Finding the Killer](chapter-01-finding-the-killer.md) | [Chapter 3: Indexes →](chapter-03-indexes.md)

---

## The Fire

You found the killer query in Chapter 1:

```sql
SELECT * FROM matches WHERE player1_id = 42;
```

It runs 892,341 times a day. Mean time: 5.4ms. Total CPU: 4,821 seconds. But *why* is it slow? Is it missing an index? Is the table bloated? Is the planner making a bad decision?

Derek pings you:

> "The match history page loads in 12 seconds. Users are leaving. Can you just add an index?"

Marta shakes her head:

> "Don't guess. EXPLAIN it."

---

## The Diagnosis: EXPLAIN ANALYZE

`EXPLAIN` shows you what Postgres *plans* to do. `EXPLAIN ANALYZE` actually *runs* the query and shows what really happened.

### The Killer Query, Explained

```sql
EXPLAIN ANALYZE
SELECT * FROM matches WHERE player1_id = 42;
```

Output:

```
Seq Scan on matches  (cost=0.00..1284721.00 rows=20 width=89)
                     (actual time=0.847..4312.551 rows=18 loops=1)
  Filter: (player1_id = 42)
  Rows Removed by Filter: 46999982
Planning Time: 0.089 ms
Execution Time: 4312.623 ms
```

Translation: Postgres read **all 47 million rows** to find 18 matches. It scanned the entire table because there's no index on `player1_id`.

### Anatomy of a Query Plan

```
Seq Scan on matches  (cost=0.00..1284721.00 rows=20 width=89)
│                     │              │        │       │
│                     │              │        │       └─ Average row size (bytes)
│                     │              │        └─ Estimated rows returned
│                     │              └─ Total cost (arbitrary units)
│                     └─ Startup cost
└─ The operation (Seq Scan = full table scan)

(actual time=0.847..4312.551 rows=18 loops=1)
│              │       │          │       │
│              │       │          │       └─ How many times this node ran
│              │       │          └─ Actual rows returned
│              │       └─ Time to finish (ms)
│              └─ Time to first row (ms)
└─ What actually happened (vs estimate)
```

---

## Key Scan Types

| Scan Type | What It Means | When It's Good |
|-----------|---------------|----------------|
| **Seq Scan** | Reads every row in the table | Small tables, or fetching >10% of rows |
| **Index Scan** | Uses an index to find rows, then fetches from table | Selective queries (few rows) |
| **Index Only Scan** | Reads only the index, never touches the table | All needed columns are in the index |
| **Bitmap Index Scan** | Builds a bitmap of matching pages, then reads them | Medium selectivity (1-10% of rows) |

### What We Want

```sql
-- After adding an index (we'll do this in Ch 3):
EXPLAIN ANALYZE
SELECT * FROM matches WHERE player1_id = 42;
```

```
Index Scan using idx_matches_player1 on matches
    (cost=0.56..82.41 rows=20 width=89)
    (actual time=0.031..0.089 rows=18 loops=1)
  Index Cond: (player1_id = 42)
Planning Time: 0.112 ms
Execution Time: 0.118 ms
```

From 4,312ms to 0.118ms. That's a **36,000x improvement**.

---

## Reading Complex Plans

Real queries have multiple nodes. Read them **bottom-up, inside-out**:

```sql
EXPLAIN ANALYZE
SELECT p.username, COUNT(m.id) AS match_count
FROM players p
JOIN matches m ON m.player1_id = p.id OR m.player2_id = p.id
WHERE p.elo_rating > 1800
GROUP BY p.username
ORDER BY match_count DESC
LIMIT 10;
```

```
Limit  (actual time=28471.223..28471.225 rows=10)
  -> Sort  (actual time=28471.221..28471.222 rows=10)
        Sort Key: (count(m.id)) DESC
        Sort Method: top-N heapsort  Memory: 25kB
        -> HashAggregate  (actual time=28469.102..28470.891 rows=48201)
              Group Key: p.username
              -> Hash Join  (actual time=412.891..27891.445 rows=1847291)
                    Hash Cond: (m.player1_id = p.id) OR (m.player2_id = p.id)
                    -> Seq Scan on matches m  (actual time=0.012..8921.334 rows=47000000)
                    -> Hash  (actual time=401.223..401.223 rows=48201)
                          -> Seq Scan on players p  (actual time=0.011..389.445 rows=48201)
                                Filter: (elo_rating > 1800)
                                Rows Removed by Filter: 2251799
```

The bottleneck: `Seq Scan on matches` reading 47M rows. The join condition uses `OR`, which prevents simple index usage.

---

## Red Flags in Query Plans

| Red Flag | What It Means |
|----------|---------------|
| `Seq Scan` on a large table | Missing index or planner chose not to use one |
| `Rows Removed by Filter: 46999982` | Scanned millions, kept almost nothing |
| `actual rows` ≫ `estimated rows` | Stale statistics (run ANALYZE) |
| `Sort Method: external merge Disk` | Not enough work_mem, spilling to disk |
| `Nested Loop` with high `loops` count | Possible N+1 pattern |
| `Hash Join` with huge hash table | Might need more work_mem |

---

## EXPLAIN Options

```sql
-- Basic plan (doesn't run the query)
EXPLAIN SELECT ...;

-- Actually runs it (careful with INSERT/UPDATE/DELETE!)
EXPLAIN ANALYZE SELECT ...;

-- Show buffer usage (cache hits vs disk reads)
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;

-- Machine-readable output
EXPLAIN (ANALYZE, FORMAT JSON) SELECT ...;

-- Show WAL usage (for writes)
EXPLAIN (ANALYZE, WAL) INSERT INTO ...;

-- Safe ANALYZE for writes (wraps in transaction + rollback)
BEGIN;
EXPLAIN ANALYZE DELETE FROM game_events WHERE created_at < '2023-01-01';
ROLLBACK;
```

### BUFFERS Example

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM matches WHERE player1_id = 42;
```

```
Seq Scan on matches  (cost=0.00..1284721.00 rows=20 width=89)
                     (actual time=0.847..4312.551 rows=18 loops=1)
  Filter: (player1_id = 42)
  Rows Removed by Filter: 46999982
  Buffers: shared hit=128412 read=512309
Planning Time: 0.089 ms
Execution Time: 4312.623 ms
```

`shared read=512309` — that's 512,309 pages read from disk. Each page is 8KB. That's **4GB of disk I/O** for one query.

---

## The Cost Model

Postgres assigns costs using these settings:

```sql
SHOW seq_page_cost;      -- 1.0 (reading a sequential page from disk)
SHOW random_page_cost;   -- 4.0 (reading a random page — index lookup)
SHOW cpu_tuple_cost;     -- 0.01 (processing one row)
SHOW cpu_index_tuple_cost; -- 0.005 (processing one index entry)
```

The planner multiplies these by estimated rows/pages to decide: "Is a Seq Scan cheaper than an Index Scan?"

For our query:
- Seq Scan cost: 47M rows × 0.01 + pages × 1.0 = ~1,284,721
- Index Scan cost: 20 rows × 0.01 + 20 pages × 4.0 = ~80

The planner picks the lower cost. But it needs accurate row estimates to decide correctly.

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `EXPLAIN SELECT ...` | Show plan without running |
| `EXPLAIN ANALYZE SELECT ...` | Run and show actual times |
| `EXPLAIN (ANALYZE, BUFFERS) ...` | Show cache hits vs disk reads |
| `EXPLAIN (FORMAT JSON) ...` | Machine-readable output |
| `BEGIN; EXPLAIN ANALYZE ...; ROLLBACK;` | Safe ANALYZE for writes |

| Plan Node | Meaning |
|-----------|---------|
| Seq Scan | Full table scan |
| Index Scan | Index lookup + heap fetch |
| Index Only Scan | Index-only (no heap) |
| Bitmap Index Scan | Bitmap of matching pages |
| Nested Loop | For each outer row, scan inner |
| Hash Join | Build hash table, probe it |
| Merge Join | Both sides sorted, merge |

---

## Exercises

### Exercise 1: Read the Plan

Run this and interpret every line:

```sql
EXPLAIN ANALYZE
SELECT * FROM game_events
WHERE match_id = 12345
  AND event_type = 'score'
ORDER BY created_at;
```

Questions:
- What scan type is used?
- How many rows were scanned vs returned?
- What's the execution time?

### Exercise 2: Estimated vs Actual

Run `EXPLAIN ANALYZE` on a query where you expect the estimates to be wrong:

```sql
EXPLAIN ANALYZE
SELECT * FROM players WHERE elo_rating BETWEEN 1400 AND 1410;
```

Compare `rows=` (estimated) with `actual rows=`. If they differ by more than 10x, the statistics are stale.

### Exercise 3: BUFFERS Deep Dive

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM matches
WHERE status = 'active'
  AND started_at > now() - interval '1 hour';
```

Calculate: What percentage of pages came from cache vs disk? Is this query I/O-bound or CPU-bound?

---

## What Happens Next

You can now read query plans. The diagnosis is clear: `Seq Scan on matches` because there's no index on `player1_id`. Time to fix it.

But indexes aren't free. The wrong index wastes disk, slows writes, and confuses the planner. Next chapter: you learn which indexes to create, how to make them small, and how to verify they're actually being used.

---

[← Chapter 1: Finding the Killer](chapter-01-finding-the-killer.md) | [Chapter 3: Indexes →](chapter-03-indexes.md)

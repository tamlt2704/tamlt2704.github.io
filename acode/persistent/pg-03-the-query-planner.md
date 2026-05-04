# Chapter 3: The Query Planner — "Why Is PostgreSQL Ignoring My Index?"

[← The Index Trap](pg-02-the-index-trap.md) | [Next: The Vacuum Crisis →](pg-04-the-vacuum-crisis.md)

---

## The Incident

Wednesday, 2 PM. You get a Slack message from Priya:

> **Priya:** "I created an index on `status` for the pending-transactions query. It works
> on my laptop. In production, PostgreSQL does a Seq Scan. Is the index broken?"

You check. The index exists. You run the query on staging — Index Scan. You run the exact
same query on production — Seq Scan. Same table, same index, different plan.

You go to Viktor.

> **Viktor:** "The planner isn't broken. Your statistics are."

---

## 1. How the Planner Decides

> **Viktor:** "When you run a query, PostgreSQL doesn't just execute it. It first generates
> every possible execution plan — Seq Scan, Index Scan, Bitmap Scan, Hash Join, Merge Join
> — and estimates the **cost** of each one. Then it picks the cheapest."

The cost depends on **table statistics**: row count, value distribution, null fraction,
correlation between physical and logical order.

Here's the problem query:

```sql
EXPLAIN ANALYZE
SELECT * FROM transactions WHERE status = 'PENDING';
```

Production output:

```
Seq Scan on transactions
  (cost=0.00..2834210.00 rows=34000000 width=128)
  (actual time=0.019..41023.112 rows=50000 loops=1)
  Filter: (status = 'PENDING')
  Rows Removed by Filter: 84950000
```

> **Viktor:** "Look at the estimates. PG thinks **34 million rows** are PENDING. The actual
> number is **50,000**. The planner thinks 40% of the table matches — so a Seq Scan looks
> cheaper than 34 million random index lookups. It's making a rational decision based on
> **wrong data**."

---

## 2. Stale Statistics

> **Viktor:** "PostgreSQL keeps statistics about every column in `pg_statistic`. These stats
> are updated by `ANALYZE` — either manually or by autovacuum. If the data changes faster
> than autovacuum runs, the stats go stale."

Check when stats were last updated:

```sql
SELECT relname,
       last_analyze,
       last_autoanalyze,
       n_live_tup,
       n_dead_tup
FROM pg_stat_user_tables
WHERE relname = 'transactions';
```

```
 relname      | last_analyze | last_autoanalyze    | n_live_tup | n_dead_tup
--------------+--------------+---------------------+------------+-----------
 transactions | NULL         | 2026-04-15 03:12:00 | 85000000   | 12400000
```

> **Viktor:** "Last autoanalyze was two weeks ago. Since then, a batch job settled 33 million
> PENDING transactions. The stats still think 40% are PENDING. Reality: 0.06%."

The fix:

```sql
-- Force PostgreSQL to resample the table
ANALYZE transactions;
```

Now run EXPLAIN again:

```sql
EXPLAIN ANALYZE
SELECT * FROM transactions WHERE status = 'PENDING';
```

```
Index Scan using idx_txn_status on transactions
  (cost=0.56..18432.10 rows=50000 width=128)
  (actual time=0.031..12.445 rows=50000 loops=1)
  Index Cond: (status = 'PENDING')
  Buffers: shared hit=312
```

> **Viktor:** "After `ANALYZE`, PG knows only 50,000 rows are PENDING. Now an Index Scan is
> obviously cheaper. Same query, same index — different plan because the **statistics
> changed**."

---

## 3. pg_stat_statements — Viktor's Dashboard

> **Viktor:** "You can't fix what you can't see. This is the single most important
> PostgreSQL extension."

```sql
-- Enable the extension (once, requires superuser)
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

```sql
-- Top 10 queries by total execution time
SELECT substring(query, 1, 80) AS query,
       calls,
       round(total_exec_time / 1000) AS total_sec,
       round(mean_exec_time) AS avg_ms,
       rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
```

```
 query                                              | calls  | total_sec | avg_ms | rows
----------------------------------------------------+--------+-----------+--------+---------
 SELECT * FROM transactions WHERE from_account_id = | 482910 | 3842      | 8      | 24145500
 UPDATE transactions SET status = $1 WHERE id = $2  | 920100 | 2201      | 2      | 920100
 SELECT * FROM transactions WHERE status = $1       | 12304  | 1847      | 150    | 615200
 INSERT INTO transactions (...)                     | 310042 | 892       | 3      | 310042
 SELECT count(*) FROM transactions WHERE created_at | 8920   | 445       | 50     | 8920
```

> **Viktor:** "This tells you where your database spends its time. The third row — that's
> Priya's query. 12,000 calls, 150ms average, 1,847 seconds total. After the ANALYZE fix,
> watch that `avg_ms` drop."

```sql
-- Reset stats after a fix to get clean measurements
SELECT pg_stat_statements_reset();
```

---

## 4. Common Planner Mistakes

Viktor pulls up his "wall of shame" — queries that defeat the planner.

### Mistake 1: Functions on Indexed Columns

```sql
-- ⚠️ Index on created_at is USELESS here
-- PG can't use the index because EXTRACT() transforms every value
SELECT * FROM transactions
WHERE EXTRACT(YEAR FROM created_at) = 2026;
```

```
Seq Scan on transactions  (actual time=0.021..39102.331 rows=...)
  Filter: (EXTRACT(YEAR FROM created_at) = 2026)
```

```sql
-- ✅ Rewrite as a range — now PG uses the index
SELECT * FROM transactions
WHERE created_at >= '2026-01-01'
  AND created_at < '2027-01-01';
```

```
Index Scan using idx_txn_account_date on transactions
  (actual time=0.029..45.112 rows=...)
```

> **Viktor:** "The index stores `created_at` values. It does NOT store
> `EXTRACT(YEAR FROM created_at)` values. If you wrap a column in a function, the index
> can't help — unless you create an **expression index** on that function."

### Mistake 2: Implicit Type Casting

```sql
-- ⚠️ from_account_id is BIGINT, but you pass a string
EXPLAIN ANALYZE
SELECT * FROM transactions WHERE from_account_id = '42';
```

> **Viktor:** "In PostgreSQL, this actually works fine — PG casts the literal `'42'` to
> BIGINT, not the column. But watch out for the reverse:"

```sql
-- ⚠️ BUG: text_column has an index, but you pass an integer
-- PG casts EVERY row's text_column to integer → Seq Scan
SELECT * FROM accounts WHERE account_code = 42;
-- account_code is VARCHAR, 42 is integer
-- ✅ Fix: pass the correct type
SELECT * FROM accounts WHERE account_code = '42';
```

### Mistake 3: OR Conditions

```sql
-- ⚠️ OR prevents single-index use
EXPLAIN ANALYZE
SELECT * FROM transactions
WHERE from_account_id = 42 OR to_account_id = 42;
```

```
Seq Scan on transactions
  (actual time=0.020..42301.112 rows=974586 loops=1)
  Filter: ((from_account_id = 42) OR (to_account_id = 42))
```

> **Viktor:** "No single index covers both columns. PG falls back to Seq Scan."

```sql
-- ✅ Use UNION ALL — each branch uses its own index
SELECT * FROM transactions WHERE from_account_id = 42
UNION ALL
SELECT * FROM transactions WHERE to_account_id = 42;
```

```
Append  (actual time=0.031..1.204 rows=974586 loops=1)
  ->  Index Scan using idx_txn_account_date ...
  ->  Index Scan using idx_txn_to_account ...
```

> **Viktor:** "Each branch uses its own index. If you need deduplication, use `UNION`
> instead of `UNION ALL` — but that adds a sort. Only deduplicate if you need to."

---

## 5. The Planner Settings You Should Know

Viktor opens `postgresql.conf`:

> **Viktor:** "These four settings shape every plan the planner generates. Get them wrong,
> and the planner makes bad decisions all day."

| Setting | Default | What It Does |
|---------|---------|-------------|
| `random_page_cost` | 4.0 | Cost of a random I/O read. **Set to 1.1 for SSD.** |
| `effective_cache_size` | 4 GB | How much RAM PG assumes is available for caching. Set to ~75% of total RAM. |
| `work_mem` | 4 MB | RAM per sort/hash operation. Increase for complex queries with large sorts. |
| `default_statistics_target` | 100 | Number of samples per column for `ANALYZE`. Increase for skewed data. |

```sql
-- Check current values
SHOW random_page_cost;
SHOW effective_cache_size;
SHOW work_mem;
SHOW default_statistics_target;
```

> **Viktor:** "On SSD, set `random_page_cost` to **1.1**. The default 4.0 is for spinning
> disks — it tells the planner that random I/O is 4x more expensive than sequential I/O.
> On SSD, random and sequential are nearly the same. This **single change** makes the
> planner prefer index scans over Seq Scans."

```sql
-- Apply without restart (session-level for testing)
SET random_page_cost = 1.1;
SET effective_cache_size = '24GB';
```

```sql
-- For permanent changes, edit postgresql.conf and reload
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_cache_size = '24GB';
SELECT pg_reload_conf();
```

> **Viktor:** "For `work_mem`, be careful. It's per-operation, not per-query. A query with
> 5 sorts uses 5 × `work_mem`. Set it too high and you run out of RAM. Start with 16–64 MB
> and monitor."

---

## 6. Putting It All Together — The Investigation Checklist

Viktor writes this on a sticky note and puts it on your monitor:

```
┌─────────────────────────────────────────────────────┐
│  QUERY NOT USING INDEX? CHECK IN ORDER:             │
│                                                     │
│  1. Does the index exist?                           │
│     → \di in psql, or pg_indexes                    │
│                                                     │
│  2. Are statistics fresh?                           │
│     → pg_stat_user_tables → last_analyze            │
│     → Run ANALYZE if stale                          │
│                                                     │
│  3. Is a function wrapping the column?              │
│     → Rewrite as range, or create expression index  │
│                                                     │
│  4. Type mismatch?                                  │
│     → Ensure query literal matches column type      │
│                                                     │
│  5. OR condition?                                   │
│     → Rewrite as UNION ALL                          │
│                                                     │
│  6. Is random_page_cost still 4.0 on SSD?           │
│     → Set to 1.1                                    │
│                                                     │
│  7. Does the planner estimate match reality?        │
│     → Compare estimated rows vs actual rows         │
│     → Increase default_statistics_target if skewed  │
└─────────────────────────────────────────────────────┘
```

---

## Key Takeaways

1. **The planner picks the cheapest plan** based on cost estimates. Bad statistics → bad estimates → bad plans.
2. **`ANALYZE`** updates table statistics. Run it after bulk data changes.
3. **`pg_stat_statements`** is the #1 extension for finding slow queries. Install it everywhere.
4. **Functions on indexed columns** prevent index use — rewrite as ranges.
5. **OR conditions** can defeat indexes — rewrite as `UNION ALL`.
6. **`random_page_cost = 1.1`** on SSD is the single most impactful planner setting.
7. **Always compare estimated vs actual rows** in EXPLAIN ANALYZE — a big gap means stale stats.

---

## What's Next

The planner is smart now. Your indexes are lean. Queries are fast. You think you're done.

Then Viktor shows you something terrifying. He runs a query on the `transactions` table:

```sql
SELECT pg_size_pretty(pg_total_relation_size('transactions'));
-- Result: 48 GB
```

> **You:** "48 GB?! It was 8 GB last month!"
>
> **Viktor:** "Welcome to dead tuples. They're invisible to your queries, but they're eating
> your disk alive. And if we don't fix this soon, something much worse happens — transaction
> ID wraparound. The database will **stop accepting writes**."

There's a monster lurking under your tables.

[Next: The Vacuum Crisis →](pg-04-the-vacuum-crisis.md)

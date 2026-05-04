# Chapter 2: The Index Trap — "47 Indexes and Still Slow"

[← The Slow Query](pg-01-the-slow-query.md) | [Next: The Query Planner →](pg-03-the-query-planner.md)

---

## The Incident

Your Chapter 1 fix was a hit. Word spread. Now every developer at PayFlow has the same
playbook: query slow? Add an index.

Priya's team adds indexes for every slow query they find. The QA team adds indexes. Even
the intern on the reporting team adds one. Two weeks later, the `transactions` table has
**47 indexes**.

Then the alerts start again:

- INSERT throughput drops **60%**. Payment processing backs up.
- Disk usage **doubles** overnight. DevOps is paging.
- Some queries are **still slow** despite having indexes.

> **Viktor:** *(sighs)* "Indexes aren't free. Every INSERT updates *every* index. You didn't
> add 47 shortcuts — you added 47 toll booths."

---

## 1. The Cost of Too Many Indexes

Viktor shows you the damage:

```sql
-- How big are all these indexes?
SELECT indexrelname,
       pg_size_pretty(pg_relation_size(indexrelid)) AS size,
       idx_scan AS times_used
FROM pg_stat_user_indexes
WHERE relname = 'transactions'
ORDER BY pg_relation_size(indexrelid) DESC;
```

Output (abbreviated):

```
 indexrelname                    | size    | times_used
---------------------------------+---------+-----------
 idx_txn_account_date            | 2.1 GB  | 482,910
 idx_txn_created_at              | 1.8 GB  | 12,304
 idx_txn_status                  | 1.4 GB  | 89
 idx_txn_amount_range            | 1.2 GB  | 0
 idx_txn_to_account              | 1.1 GB  | 3,201
 idx_txn_currency                | 980 MB  | 0
 idx_txn_description_text        | 870 MB  | 0
 ... (40 more indexes)           | ...     | ...
---------------------------------+---------+-----------
 TOTAL                           | 12.3 GB |
```

```sql
-- Compare: how big is the table itself?
SELECT pg_size_pretty(pg_relation_size('transactions'));
-- Result: 8.1 GB
```

> **Viktor:** "Your indexes are **bigger than your data**. 12 GB of indexes on an 8 GB table.
> Every time you INSERT a row, PostgreSQL writes to the table *and* updates all 47 indexes.
> That's why your writes are slow."

---

## 2. Composite Index Order Matters

> **Viktor:** "Your index from Chapter 1 is `(from_account_id, created_at)`. What happens
> when someone queries by `created_at` alone?"

```sql
-- ⚠️ This query CANNOT use the composite index
EXPLAIN ANALYZE
SELECT * FROM transactions
WHERE created_at > '2026-04-01';
```

```
Seq Scan on transactions
  (cost=0.00..2834210.00 rows=8500000 width=128)
  (actual time=0.018..38921.445 rows=8347291 loops=1)
  Filter: (created_at > '2026-04-01')
```

Seq Scan. The composite index is useless here.

> **Viktor:** "Think of a composite index like a phone book sorted by **(last_name,
> first_name)**. You can look up 'Smith' fast. You can look up 'Smith, John' even faster.
> But you **cannot** look up everyone named 'John' — you'd have to read the entire book."

**The rule:** A composite index `(A, B)` serves queries on:
- ✅ `A` alone
- ✅ `A` and `B` together
- ❌ `B` alone — the index is sorted by A first, B is only sorted *within* each A value

> **You:** "So Priya's team created a separate index on `created_at` because the composite
> one didn't help?"
>
> **Viktor:** "Yes. And then another on `(created_at, status)`. And another on
> `(status, created_at)`. They're creating every permutation instead of thinking about
> which queries actually matter."

---

## 3. Partial Indexes — Viktor's Favorite

> **Viktor:** "Most of your queries only care about recent, non-settled transactions. Why
> index all 85 million rows?"

```sql
-- ⚠️ WASTEFUL: indexes ALL 85 million rows
-- Most are SETTLED and never queried again
CREATE INDEX idx_txn_status ON transactions (status);
```

```sql
-- ✅ Partial index — only indexes what matters
CREATE INDEX idx_txn_pending
ON transactions (from_account_id, created_at)
WHERE status = 'PENDING';
```

```sql
-- How many rows does each approach index?
SELECT status, count(*) FROM transactions GROUP BY status;
```

```
 status    | count
-----------+----------
 SETTLED   | 84250000
 PENDING   |    50000
 FAILED    |   700000
```

> **Viktor:** "The partial index covers 50,000 rows instead of 85 million. That's **1,700x
> smaller**. Faster to build, faster to scan, less disk, less maintenance."

Your query must include the WHERE clause for PG to use the partial index:

```sql
-- ✅ PG uses idx_txn_pending — WHERE clause matches
SELECT * FROM transactions
WHERE from_account_id = 42
  AND created_at > '2026-04-01'
  AND status = 'PENDING';
```

```sql
-- ❌ PG CANNOT use idx_txn_pending — no status filter
SELECT * FROM transactions
WHERE from_account_id = 42
  AND created_at > '2026-04-01';
```

---

## 4. Covering Indexes — Index-Only Scans

Priya's dashboard query only needs three columns:

```sql
SELECT from_account_id, amount, created_at
FROM transactions
WHERE from_account_id = 42
  AND created_at > '2026-04-01'
ORDER BY created_at DESC;
```

Even with the composite index, PG does an **Index Scan** — it finds the rows via the index,
then goes back to the **table heap** to fetch `amount`. That heap fetch is extra I/O.

```sql
-- ✅ INCLUDE puts extra columns in the index leaf pages
CREATE INDEX idx_txn_covering
ON transactions (from_account_id, created_at DESC)
INCLUDE (amount, status);
```

Now run EXPLAIN:

```
Index Only Scan using idx_txn_covering on transactions
  (cost=0.56..48.21 rows=50 width=48)
  (actual time=0.028..0.062 rows=50 loops=1)
  Heap Fetches: 0
```

> **Viktor:** "See that? **Index Only Scan**. `Heap Fetches: 0`. PostgreSQL got everything
> it needed from the index alone. It never touched the table."

**How it works:** The `INCLUDE` columns are stored in the leaf pages of the B-tree but are
*not* part of the sort order. PG uses the visibility map to confirm the rows are visible
to the current transaction — if they are, it skips the heap entirely.

> **Viktor:** "The visibility map tracks which table pages have only visible tuples. If a
> page is all-visible, PG trusts the index. If not, it fetches from the heap to check.
> That's why `VACUUM` matters — it updates the visibility map."

---

## 5. Finding and Fixing Index Bloat

After months of UPDATEs and DELETEs, indexes accumulate dead entries — pointers to rows
that no longer exist. The index grows but doesn't shrink.

**Find unused indexes:**

```sql
SELECT schemaname, tablename, indexname,
       pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
       idx_scan AS times_used
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
```

```
 schemaname | tablename    | indexname               | index_size | times_used
------------+--------------+-------------------------+------------+-----------
 public     | transactions | idx_txn_amount_range    | 1.2 GB     | 0
 public     | transactions | idx_txn_currency        | 980 MB     | 0
 public     | transactions | idx_txn_description_text| 870 MB     | 0
```

> **Viktor:** "If `idx_scan = 0`, the index has **never been used** since the last stats
> reset. Drop it. It's dead weight slowing down every write."

```sql
-- Drop unused indexes
DROP INDEX idx_txn_amount_range;
DROP INDEX idx_txn_currency;
DROP INDEX idx_txn_description_text;
```

**Rebuild bloated indexes** (the ones that *are* used but have grown too large):

```sql
-- CONCURRENTLY = no table lock, production-safe
REINDEX INDEX CONCURRENTLY idx_txn_account_date;
```

> **Viktor:** "Never run `REINDEX` without `CONCURRENTLY` in production. Without it,
> PostgreSQL locks the table for the entire rebuild. With it, PG builds a new index in the
> background and swaps it in atomically."

---

## 6. When NOT to Index — Viktor's Rules

| Situation | Why No Index |
|-----------|-------------|
| Table < 10,000 rows | Seq Scan is faster than the overhead of an index lookup |
| Column updated constantly | Every UPDATE rewrites the index entry (HOT updates can't help) |
| Low cardinality (boolean, status with 3 values) | Index scan reads most of the table anyway — Seq Scan is cheaper |
| Write-heavy, rarely queried | Indexes slow every INSERT for no read benefit |
| Already covered by another index | `(A, B)` already serves queries on `A` — don't add a separate index on `A` |

> **Viktor:** "The best index is the one you *don't* create. Every index is a promise:
> 'I will be maintained on every write, forever.' Make sure it's worth it."

---

## The Cleanup

You and Viktor audit all 47 indexes. You keep 6. You drop 41.

| Metric | Before (47 indexes) | After (6 indexes) |
|--------|---------------------|-------------------|
| Total index size | 12.3 GB | 3.8 GB |
| INSERT throughput | 1,200 rows/sec | 3,100 rows/sec |
| Disk usage | 20.4 GB | 11.9 GB |
| Slow queries | 12 | 0 |

> **Priya** (Slack): *"INSERTs are fast again. What did you do?"*
>
> **You:** *"Deleted 41 indexes."*
>
> **Priya:** *"...you deleted indexes to make things faster?"*
>
> **Viktor:** *(smiles)*

---

## Key Takeaways

1. **Indexes aren't free** — every index is updated on every INSERT, UPDATE, and DELETE.
2. **Composite index order matters** — `(A, B)` serves A and (A,B), but not B alone.
3. **Partial indexes** reduce size dramatically by only indexing rows that match a WHERE clause.
4. **Covering indexes** with `INCLUDE` enable Index Only Scans — zero heap fetches.
5. **Monitor `pg_stat_user_indexes`** — drop indexes with `idx_scan = 0`.
6. **`REINDEX CONCURRENTLY`** rebuilds bloated indexes without locking the table.

---

## What's Next

You now know *which* indexes to create and which to drop. But sometimes PostgreSQL
**ignores your perfect index** and does a Seq Scan anyway. You check — the index exists.
You run EXPLAIN on your laptop — it uses the index. But in production? Seq Scan.

> **Viktor:** "The planner isn't broken. Your statistics are."

That's the query planner — and it has opinions.

[Next: The Query Planner →](pg-03-the-query-planner.md)

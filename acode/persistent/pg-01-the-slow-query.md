# Chapter 1: The Slow Query — "Why Does This Take 47 Seconds?"

[← Overview](pg-00-overview.md) | [Next: The Index Trap →](pg-02-the-index-trap.md)

---

## The Incident

Monday morning, 9:07 AM. You're sipping coffee when Grafana lights up red.

The `/api/transactions` endpoint — the one that powers PayFlow's main dashboard — has a P99
latency that just jumped from **200ms to 47 seconds**. The alert channel explodes.

> **Maya** (Slack, 9:08 AM): *"The dashboard is unusable. Merchants can't see their
> transactions. Fix it NOW."*
>
> **Priya** (Slack, 9:09 AM): *"I didn't change anything. Last deploy was Friday."*

You stare at the screen. You have no idea where to start.

Viktor walks over. He doesn't look at Grafana. He opens `psql`.

> **Viktor:** "First rule of PostgreSQL — never guess. Always `EXPLAIN`."

---

## 1. The Crime Scene

Viktor pulls up the slow query from the application logs. It's the query behind the
transactions list page:

```sql
-- ⚠️ THE SLOW QUERY — found in pg_stat_activity
SELECT * FROM transactions
WHERE from_account_id = 42
  AND created_at > '2026-01-01'
ORDER BY created_at DESC
LIMIT 50;
```

Looks innocent. A simple filter on one account, recent transactions, sorted by date, limited
to 50 rows. This should be fast.

> **Viktor:** "Looks innocent. Let's see what PostgreSQL actually does with it."

---

## 2. EXPLAIN ANALYZE — "Read the Execution Plan"

Viktor types the magic words:

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM transactions
WHERE from_account_id = 42
  AND created_at > '2026-01-01'
ORDER BY created_at DESC
LIMIT 50;
```

The output:

```
Limit  (cost=2847301.12..2847301.25 rows=50 width=128)
       (actual time=47123.456..47123.470 rows=50 loops=1)
  ->  Sort  (cost=2847301.12..2848532.45 rows=492532 width=128)
           (actual time=47123.454..47123.461 rows=50 loops=1)
        Sort Key: created_at DESC
        Sort Method: top-N heapsort  Memory: 32kB
        ->  Seq Scan on transactions
              (cost=0.00..2834210.00 rows=492532 width=128)
              (actual time=0.021..46891.232 rows=487293 loops=1)
              Filter: ((from_account_id = 42)
                       AND (created_at > '2026-01-01'))
              Rows Removed by Filter: 84512707
              Buffers: shared read=1200000
Planning Time: 0.182 ms
Execution Time: 47123.551 ms
```

> **Viktor:** "Read it bottom-up. That's how PostgreSQL executes it."

Viktor grabs a whiteboard marker and breaks it down:

### Line-by-line

| Line | What It Means |
|------|---------------|
| `Seq Scan on transactions` | PostgreSQL reads **every single row** in the table. All 85 million of them. |
| `rows=492532` (estimated) vs `rows=487293` (actual) | PG expected ~493K matches. Got ~487K. Estimate is decent. |
| `Rows Removed by Filter: 84512707` | It read 85M rows and threw away 84.5M. Brutal. |
| `Buffers: shared read=1200000` | Read 1.2 million 8KB pages from disk. That's ~9.4 GB of I/O. |
| `Sort Method: top-N heapsort` | After finding all matches, it sorts them to get the top 50. |
| `actual time=47123.551 ms` | **47 seconds.** |

> **Viktor:** "A Seq Scan means PostgreSQL has no shortcut. It reads every row, checks the
> WHERE clause, and discards what doesn't match. On 85 million rows, that's a full table
> scan. It's like searching for a name in a phone book by reading every page."
>
> **You:** "Why doesn't it use an index?"
>
> **Viktor:** "Because there isn't one. Check."

```sql
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'transactions';
```

```
 indexname              | indexdef
------------------------+------------------------------------------
 transactions_pkey      | CREATE UNIQUE INDEX transactions_pkey
                        |   ON transactions USING btree (id)
```

One index. The primary key. Nothing on `from_account_id` or `created_at`.

---

## 3. The Fix: Your First Index

> **Viktor:** "The query filters on `from_account_id` and sorts by `created_at DESC`.
> We need a composite index that matches both."

```sql
CREATE INDEX idx_txn_account_date
ON transactions (from_account_id, created_at DESC);
```

This takes a few minutes on 85M rows. Viktor waits patiently. Then:

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM transactions
WHERE from_account_id = 42
  AND created_at > '2026-01-01'
ORDER BY created_at DESC
LIMIT 50;
```

New output:

```
Limit  (cost=0.56..52.30 rows=50 width=128)
       (actual time=0.031..0.089 rows=50 loops=1)
  ->  Index Scan using idx_txn_account_date on transactions
        (cost=0.56..50892.12 rows=492532 width=128)
        (actual time=0.029..0.081 rows=50 loops=1)
        Index Cond: ((from_account_id = 42)
                     AND (created_at > '2026-01-01'))
        Buffers: shared hit=4
Planning Time: 0.195 ms
Execution Time: 0.112 ms
```

> **Viktor:** *(leans back)* "0.1 milliseconds. Read 4 pages instead of 1.2 million."

---

## 4. How B-tree Works — Viktor's Whiteboard

Viktor draws on the whiteboard:

> **Viktor:** "A B-tree index is like a sorted filing cabinet with multiple levels."

```
                    [Root: account_id ranges]
                   /          |              \
          [1–1000]      [1001–2000]       [2001–3000]
          /      \         |      \          |      \
     [leaves] [leaves] [leaves] [leaves] [leaves] [leaves]
     ↑ Each leaf has (account_id, created_at) pairs, sorted
```

> **Viktor:** "Here's why the composite index `(from_account_id, created_at DESC)` works:
>
> 1. PostgreSQL walks the tree to find `account_id = 42`. That's **3 page reads** — root,
>    branch, leaf. Like opening the phone book to the 'S' section.
>
> 2. Within that leaf, entries are sorted by `created_at DESC`. So PG just walks forward
>    and picks up the first 50 rows. No sorting needed.
>
> 3. The `LIMIT 50` means PG stops after 50 rows. It never reads the other 487,243 matches.
>
> That's why it went from 1.2 million page reads to 4."

> **You:** "What if I had created the index as `(created_at, from_account_id)` instead?"
>
> **Viktor:** "Then PG would have to scan *all* dates after 2026-01-01 across *all* accounts,
> then filter for account 42. Much slower. **Column order matters.** Put the equality column
> first, the range column second."

---

## 5. Verify — Before and After

| Metric | Before | After |
|--------|--------|-------|
| Scan type | Seq Scan | Index Scan |
| Rows examined | 85,000,000 | 50 |
| Time | 47,123 ms | 0.8 ms |
| Buffers read | 1,200,000 | 4 |
| I/O | ~9.4 GB | ~32 KB |

You push the fix. Grafana goes green. Maya sends a thumbs-up emoji.

> **Priya** (Slack): *"Nice. I'm going to add indexes to all our slow queries this sprint."*
>
> **Viktor:** *(mutters)* "Oh no."

---

## Key Takeaways

1. **Never guess** — always run `EXPLAIN (ANALYZE, BUFFERS)` before and after.
2. **Seq Scan** = full table scan. Fine for small tables. Catastrophic for large ones.
3. **Composite indexes** should match your query: equality columns first, range/sort columns second.
4. **B-tree** gives you O(log n) lookups — 3 page reads to find a needle in 85 million rows.
5. **LIMIT** + a matching index = PostgreSQL stops early. Without the index, it finds *all* matches first, then sorts.

---

## What's Next

One index fixed one query. You're a hero.

But Priya's sprint is about to create a monster. Next week, the `transactions` table has
**47 indexes**. INSERT throughput drops 60%. Disk usage doubles. And some queries are
*still* slow.

> **Viktor:** "Indexes aren't free. Let me show you the cost."

[Next: The Index Trap →](pg-02-the-index-trap.md)

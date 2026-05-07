# Chapter 4: The Vacuum Crisis — "The Table Bloated to 10x Its Size"

[← The Query Planner](pg-03-the-query-planner.md) | [Next: The Connection Storm →](pg-05-the-connection-storm.md)

---

## The Incident

Thursday, 11:42 AM. A disk usage alert fires in PagerDuty. The `transactions` table is
consuming **80 GB** of disk. You checked last month — it was 8 GB. The table has the same
number of rows. Nothing changed. Except everything got slower.

Queries that used to take 50ms now take 800ms. Index scans are touching 10x more pages than
they should. You've double-checked every index from [Chapter 2](pg-02-the-index-trap.md).
They're perfect. Something else is wrong.

You go to Viktor.

> **Viktor:** "Pull up the table stats. I'll bet you a coffee the dead tuple count is
> through the roof."

You run the query. Your jaw drops.

> **Viktor:** "Welcome to MVCC hell."

---

## 1. How MVCC Works

Viktor walks to the whiteboard.

> **Viktor:** "When you `UPDATE` a row in PostgreSQL, it doesn't overwrite the old data.
> It creates a **new version** of the row and marks the old one as **dead**. `DELETE` does
> the same thing — it doesn't remove the row, it just marks it invisible. The old versions
> pile up. They're called **dead tuples**."

```
UPDATE accounts SET balance = 900 WHERE id = 1;

Before:  [id=1, balance=1000, xmin=100, xmax=∞]  ← visible
After:   [id=1, balance=1000, xmin=100, xmax=200]  ← dead (invisible to new txns)
         [id=1, balance=900,  xmin=200, xmax=∞]  ← new version (visible)
```

> **Viktor:** "Every row has two hidden columns: `xmin` (the transaction that created it)
> and `xmax` (the transaction that killed it). When `xmax` is set, the row is dead — but
> it's still physically on disk. PostgreSQL keeps it around because some older transaction
> might still need to see it. That's MVCC — Multi-Version Concurrency Control."

> **You:** "So every UPDATE doubles the storage?"

> **Viktor:** "Worse. A row that gets updated 100 times has 100 dead versions sitting on
> disk. And your indexes point to every single one of them."

---

## 2. Measuring the Damage

Viktor types:

```sql
SELECT relname,
       n_live_tup,
       n_dead_tup,
       round(n_dead_tup::numeric / greatest(n_live_tup, 1) * 100, 1) AS dead_pct,
       last_autovacuum
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 10;
```

```
    relname     | n_live_tup | n_dead_tup | dead_pct |       last_autovacuum
----------------+------------+------------+----------+------------------------------
 transactions   |   85000000 |  850000000 |   1000.0 | 2026-04-28 03:14:22.109+00
 accounts       |    2000000 |    4500000 |    225.0 | 2026-05-01 06:22:11.443+00
 audit_log      |   50000000 |   12000000 |     24.0 | 2026-05-03 01:05:33.871+00
```

> **Viktor:** "850 million dead tuples. 85 million live. A **10:1 dead-to-live ratio**.
> For every real row, there are ten ghosts taking up space."

He checks the physical size:

```sql
SELECT pg_size_pretty(pg_total_relation_size('transactions')) AS total,
       pg_size_pretty(pg_relation_size('transactions')) AS table_only,
       pg_size_pretty(pg_indexes_size('transactions')) AS indexes;
```

```
  total  | table_only | indexes
---------+------------+---------
 80 GB   | 52 GB      | 28 GB
```

> **Viktor:** "52 GB of table data, but only ~5 GB is live rows. The rest is dead tuples.
> And the indexes are 28 GB because they point to dead tuples too. Every index scan has to
> skip over corpses to find live data. That's why your queries are slow."

---

## 3. Why Autovacuum Isn't Keeping Up

> **You:** "But autovacuum is supposed to clean this up automatically, right?"

> **Viktor:** "Autovacuum IS running. Look — `last_autovacuum` was five days ago. But with
> default settings, it's like cleaning a stadium with a dustpan."

He pulls up the defaults:

| Setting | Default | Problem | Fix |
|---|---|---|---|
| `autovacuum_vacuum_cost_delay` | 2ms | Pauses 2ms after each batch — too slow for big tables | `0` (no delay) |
| `autovacuum_vacuum_cost_limit` | 200 | Tiny work budget per cycle | `2000` |
| `autovacuum_max_workers` | 3 | Not enough workers for many tables | `6` |
| `autovacuum_vacuum_scale_factor` | 0.2 | Triggers at 20% dead — too late for huge tables | `0.01` |
| `autovacuum_vacuum_threshold` | 50 | Minimum dead tuples before vacuum kicks in | `1000` |

> **Viktor:** "The scale factor is the killer. With 85 million live rows and a scale factor
> of 0.2, autovacuum won't trigger until there are **17 million** dead tuples. By then,
> you're already drowning. And when it does run, the cost delay throttles it so hard it
> can't keep up with the write rate."

He shows the per-table override:

```sql
ALTER TABLE transactions SET (
    autovacuum_vacuum_scale_factor = 0.01,
    autovacuum_vacuum_cost_delay = 0,
    autovacuum_vacuum_cost_limit = 2000
);
```

> **Viktor:** "Now autovacuum triggers at 1% dead tuples — 850,000 instead of 17 million.
> And it runs at full speed with no cost delay. Set this on every high-write table."

---

## 4. Transaction ID Wraparound — The Nuclear Option

Viktor's tone changes. He closes the door.

> **Viktor:** "Everything I've shown you so far is a performance problem. This next one is
> an **availability** problem. This is the one thing that can force PostgreSQL to **shut
> down and refuse all writes**."

> **You:** "What?"

> **Viktor:** "PostgreSQL uses 32-bit transaction IDs. That's about 4 billion total. Every
> INSERT, UPDATE, DELETE consumes a transaction ID. When VACUUM runs, it **freezes** old
> rows — it marks them as 'visible to everyone forever' so their transaction IDs can be
> recycled. If VACUUM can't keep up, you run out of transaction IDs. When you get within
> ~1 million of the limit, PostgreSQL goes into **safety shutdown**. Read-only mode. No
> writes. No inserts. Nothing."

```sql
-- Check how close you are to wraparound
SELECT datname,
       age(datfrozenxid) AS xid_age,
       2147483647 - age(datfrozenxid) AS xids_remaining
FROM pg_database
ORDER BY age(datfrozenxid) DESC;
```

```
 datname  |  xid_age   | xids_remaining
----------+------------+----------------
 payflow  |  312000000 |     1835483647
 postgres |    5000012 |     2142483635
```

> **Viktor:** "Rule of thumb: if `xid_age` crosses **1 billion**, you have a problem. If
> it crosses **2 billion**, PostgreSQL shuts down. We're at 312 million — safe for now, but
> only because I've been watching it. Without proper vacuuming, a high-write database can
> burn through a billion XIDs in weeks."

---

## 5. Manual VACUUM for Emergencies

> **Viktor:** "Autovacuum handles the steady state. But right now, we have 850 million dead
> tuples. We need to clean up manually."

```sql
-- Regular vacuum: reclaims space for reuse, doesn't shrink the file
VACUUM VERBOSE transactions;
```

```
INFO:  vacuuming "public.transactions"
INFO:  removed 850,000,000 dead row versions in 4,200,000 pages
INFO:  table "transactions": found 850000000 removable, 85000000 nonremovable row versions
DETAIL:  0 dead row versions cannot be removed yet.
```

> **Viktor:** "Regular VACUUM marks dead space as reusable. New inserts will fill those
> gaps. But the file on disk stays 52 GB — it doesn't shrink."

> **You:** "How do we actually reclaim the disk space?"

```sql
-- Full vacuum: rewrites the entire table, reclaims disk space
-- ⚠️ NEVER in production during business hours
VACUUM FULL transactions;
```

> **Viktor:** "`VACUUM FULL` rewrites the entire table to a new file, compacting it. But
> it takes an **AccessExclusiveLock** — it blocks every query, including SELECTs. On an
> 80 GB table, that could take hours. Schedule it during a maintenance window."

```sql
-- Freeze old tuples to prevent XID wraparound
VACUUM FREEZE transactions;
```

> **Viktor:** "`VACUUM FREEZE` is what prevents the wraparound apocalypse. It marks all
> tuples as frozen — visible to all transactions forever — so their XIDs can be recycled."

---

## Verification

After applying the per-table autovacuum settings and running a manual VACUUM:

```sql
SELECT relname, n_live_tup, n_dead_tup,
       round(n_dead_tup::numeric / greatest(n_live_tup, 1) * 100, 1) AS dead_pct
FROM pg_stat_user_tables
WHERE relname = 'transactions';
```

```
   relname    | n_live_tup | n_dead_tup | dead_pct
--------------+------------+------------+----------
 transactions |   85000000 |      12400 |      0.0
```

> **Viktor:** "From 850 million dead tuples to 12,400. The table is breathing again."

---

## Key Takeaways

1. **MVCC creates dead tuples** — every UPDATE and DELETE leaves invisible row versions on disk.
2. **Dead tuples bloat tables and indexes** — they waste disk space and slow down scans.
3. **Autovacuum defaults are too conservative** for high-write tables — tune per-table settings.
4. **Transaction ID wraparound** can force PostgreSQL into read-only mode — monitor `age(datfrozenxid)`.
5. **`VACUUM`** reclaims space for reuse. **`VACUUM FULL`** shrinks the file but locks the table. **`VACUUM FREEZE`** prevents XID wraparound.
6. **Never disable autovacuum.** Tune it. Never turn it off.

---

## What's Next

The table is clean. Dead tuples are under control. Disk usage is stable. You think the
crisis is over.

Then Black Friday hits. Traffic spikes 10x. Every microservice opens its own database
connections. PostgreSQL hits `max_connections` and starts rejecting requests. The entire
platform goes down.

VACUUM keeps the table healthy. But there's another resource that runs out faster than disk
space — connections.

[Next: The Connection Storm →](pg-05-the-connection-storm.md)

# Chapter 6: The Lock Investigation — "Why Is This UPDATE Hanging?"

[← The Connection Storm](pg-05-the-connection-storm.md) | [Next: The Replication Setup →](pg-07-the-replication-setup.md)

---

## The Incident

Monday, 2:17 PM. You're running a routine data fix — updating the `currency` column on a
batch of accounts:

```sql
UPDATE accounts SET currency = 'USD' WHERE currency IS NULL;
```

You press Enter. Nothing happens. No rows affected. No error. No timeout. The cursor just
blinks. One minute. Five minutes. Ten minutes.

You open a new terminal and try a simple SELECT:

```sql
SELECT * FROM accounts WHERE id = 1;
```

That hangs too.

You ping Priya.

> **Priya:** "Something is holding a lock on that table. Don't cancel your query yet — I
> want to see the lock chain. Let me show you how to investigate."

---

## 1. PostgreSQL Lock Types

> **Priya:** "PostgreSQL has multiple lock levels. They're not all equal — some coexist
> peacefully, others block everything."

| Lock | Acquired By | Conflicts With | Severity |
|---|---|---|---|
| `AccessShareLock` | `SELECT` | `AccessExclusiveLock` | Lightest |
| `RowShareLock` | `SELECT FOR UPDATE` | `ExclusiveLock` | Light |
| `RowExclusiveLock` | `INSERT`, `UPDATE`, `DELETE` | `ShareLock`, `ShareRowExclusiveLock` | Medium |
| `ShareLock` | `CREATE INDEX` | `RowExclusiveLock` | Heavy |
| `AccessExclusiveLock` | `ALTER TABLE`, `DROP`, `VACUUM FULL` | **Everything** | ☢️ Nuclear |

> **Priya:** "Most DML operations — INSERT, UPDATE, DELETE — take a `RowExclusiveLock`.
> They don't block each other (unless they touch the same row). The problem is when
> something takes an `AccessExclusiveLock`. That blocks **every other lock type**,
> including plain SELECTs."

---

## 2. Finding the Blocker

> **Priya:** "Let's find out who's holding the lock."

```sql
-- The lock detective query
SELECT blocked.pid AS blocked_pid,
       blocked.query AS blocked_query,
       blocking.pid AS blocking_pid,
       blocking.query AS blocking_query,
       now() - blocked.query_start AS waiting_time
FROM pg_stat_activity blocked
JOIN pg_locks bl ON bl.pid = blocked.pid
JOIN pg_locks lo ON lo.locktype = bl.locktype
  AND lo.relation = bl.relation
  AND lo.pid != bl.pid
JOIN pg_stat_activity blocking ON blocking.pid = lo.pid
WHERE NOT bl.granted;
```

```
 blocked_pid |            blocked_query             | blocking_pid |              blocking_query               | waiting_time
-------------+--------------------------------------+--------------+-------------------------------------------+--------------
       67890 | UPDATE accounts SET currency = 'USD' |        12345 | ALTER TABLE accounts ADD COLUMN region ... | 00:12:34
       67891 | SELECT * FROM accounts WHERE id = 1  |        12345 | ALTER TABLE accounts ADD COLUMN region ... | 00:08:17
       67892 | INSERT INTO accounts (name, ...) ... |        12345 | ALTER TABLE accounts ADD COLUMN region ... | 00:06:45
```

> **Priya:** "There it is. PID **12345** is running an `ALTER TABLE` — adding a column.
> It's blocking your UPDATE, a SELECT, and an INSERT. Three queries queued behind one DDL
> statement."

> **You:** "Who ran that ALTER TABLE?"

> **Priya:** "Let's check."

```sql
SELECT pid, usename, application_name, query,
       now() - query_start AS duration
FROM pg_stat_activity
WHERE pid = 12345;
```

```
  pid  | usename | application_name |                  query                   |  duration
-------+---------+------------------+------------------------------------------+-----------
 12345 | payflow | analytics-svc    | ALTER TABLE accounts ADD COLUMN region.. | 00:14:02
```

> **Priya:** "The analytics service ran a migration during business hours. Classic."

---

## 3. The ALTER TABLE Trap

> **Priya:** "`ALTER TABLE` takes an `AccessExclusiveLock`. It blocks **everything** — even
> SELECTs. But here's the part that surprises people: it doesn't just block queries that
> come after it. It creates a **queue**."

```
Time →

SELECT (running, holds AccessShareLock)
  │
  ├─ ALTER TABLE (waiting for AccessExclusiveLock)
  │     │
  │     ├─ SELECT (queued behind ALTER)
  │     ├─ UPDATE (queued behind ALTER)
  │     ├─ SELECT (queued behind ALTER)
  │     └─ INSERT (queued behind ALTER)
  │
Original SELECT finishes → ALTER runs → everything unblocks
```

> **Priya:** "The ALTER TABLE is waiting for the first SELECT to finish. But while it waits,
> every new query — even simple SELECTs — queues **behind** the ALTER TABLE. It's not
> first-come-first-served. The AccessExclusiveLock request poisons the queue. One long-running
> SELECT + one ALTER TABLE = total table lockout."

> **You:** "So the ALTER TABLE is waiting for one query, but blocking hundreds?"

> **Priya:** "Exactly. And if that first SELECT takes 30 minutes, everything waits 30
> minutes. I've seen this take down production."

The fix: use `lock_timeout` to prevent indefinite waiting:

```sql
SET lock_timeout = '5s';
ALTER TABLE accounts ADD COLUMN currency VARCHAR(3) DEFAULT 'USD';
-- If it can't acquire the lock in 5s, it fails instead of blocking everything
```

> **Priya:** "If the ALTER can't get the lock in 5 seconds, it fails with an error. You
> retry during a quieter moment. Much better than silently blocking the entire table."

---

## 4. Safe DDL Patterns

> **Priya:** "Not all ALTER TABLEs are equal. Some are instant. Some rewrite the entire
> table. Know the difference."

```sql
-- ⚠️ DANGEROUS: blocks all queries while rewriting table
ALTER TABLE transactions
  ADD COLUMN fee NUMERIC(19,4) DEFAULT 0;
```

> **Priya:** "Adding a column with a `DEFAULT` value used to rewrite the entire table in
> older PostgreSQL versions. In PG 11+, it's instant for most types — but adding a
> volatile default or changing a column type still triggers a full rewrite."

```sql
-- ✅ SAFE: add column as nullable first (instant, no rewrite)
ALTER TABLE transactions ADD COLUMN fee NUMERIC(19,4);

-- Then backfill in batches (no long-held locks)
UPDATE transactions SET fee = 0
WHERE fee IS NULL AND id BETWEEN 1 AND 100000;

UPDATE transactions SET fee = 0
WHERE fee IS NULL AND id BETWEEN 100001 AND 200000;
```

> **Priya:** "Add the column as nullable — that's instant, no table rewrite. Then backfill
> in small batches. Each batch takes a brief `RowExclusiveLock` on the affected rows, not
> the whole table. No downtime."

Safe DDL checklist:

```
┌─────────────────────────────────────────────────────┐
│  SAFE DDL CHECKLIST                                 │
│                                                     │
│  ✅ ADD COLUMN (nullable, no default)  → instant    │
│  ✅ ADD COLUMN (with DEFAULT, PG 11+)  → instant    │
│  ✅ DROP COLUMN                        → instant*   │
│  ✅ CREATE INDEX CONCURRENTLY          → no lock    │
│                                                     │
│  ⚠️  ALTER COLUMN TYPE                 → rewrite    │
│  ⚠️  ADD COLUMN with volatile DEFAULT  → rewrite    │
│  ⚠️  SET NOT NULL (pre-PG 12)         → full scan  │
│                                                     │
│  * DROP COLUMN only marks it invisible;             │
│    space reclaimed on next VACUUM FULL or rewrite   │
└─────────────────────────────────────────────────────┘
```

---

## 5. Advisory Locks (Application-Level)

> **Priya:** "Sometimes you need locking at the application level — not on rows or tables,
> but on abstract resources. PostgreSQL has advisory locks for that."

```sql
-- Acquire a named lock (non-blocking)
SELECT pg_try_advisory_lock(hashtext('process-monthly-report'));
-- Returns true if acquired, false if someone else has it

-- Do your work...

-- Release when done
SELECT pg_advisory_unlock(hashtext('process-monthly-report'));
```

> **Priya:** "Use case: you have a batch job that runs every hour — generating reports,
> syncing data, whatever. If two instances of the job start at the same time, they'll
> corrupt each other's output. Wrap it in an advisory lock. The second instance sees
> `false` and skips the run."

> **You:** "Why not use a `locked` column in a table?"

> **Priya:** "Because if the process crashes, the row stays locked forever. Advisory locks
> are automatically released when the session ends. Crash-safe by design."

---

## 6. Monitoring Locks in Production

> **Priya:** "You shouldn't have to run the detective query every time. Create a view."

```sql
CREATE VIEW lock_monitor AS
SELECT pid, usename,
       pg_blocking_pids(pid) AS blocked_by,
       query, state,
       now() - query_start AS duration
FROM pg_stat_activity
WHERE pg_blocking_pids(pid) != '{}'
ORDER BY query_start;
```

Now checking for blocked queries is a single command:

```sql
SELECT * FROM lock_monitor;
```

```
  pid  | usename |  blocked_by  |              query               |  state  |  duration
-------+---------+--------------+----------------------------------+---------+-----------
 67890 | payflow | {12345}      | UPDATE accounts SET currency ... | active  | 00:12:34
 67891 | payflow | {12345}      | SELECT * FROM accounts WHERE ... | active  | 00:08:17
```

> **Priya:** "If you see a blocked query that's been waiting too long, you can kill the
> blocker:"

```sql
-- Graceful: ask the backend to cancel its query
SELECT pg_cancel_backend(12345);

-- Nuclear: terminate the entire backend process
SELECT pg_terminate_backend(12345);
```

> **Priya:** "Always try `pg_cancel_backend` first. It sends a cancel signal — the query
> stops but the connection survives. `pg_terminate_backend` kills the connection entirely.
> Use it only if cancel doesn't work."

---

## Verification

After killing the blocking ALTER TABLE and setting up the lock monitor:

```sql
-- Confirm no blocked queries
SELECT * FROM lock_monitor;
```

```
(0 rows)
```

```sql
-- Confirm the original UPDATE now works
UPDATE accounts SET currency = 'USD' WHERE currency IS NULL;
-- UPDATE 34521
-- Time: 1247.332 ms
```

> **Priya:** "And add `lock_timeout` to your migration scripts. Every single one."

---

## Key Takeaways

1. **`AccessExclusiveLock`** (ALTER TABLE, DROP, VACUUM FULL) blocks everything — including SELECTs.
2. **Lock queuing** means a waiting ALTER TABLE blocks all subsequent queries, not just concurrent ones.
3. **Set `lock_timeout`** on DDL statements to fail fast instead of blocking the table indefinitely.
4. **Add columns as nullable** and backfill in batches — avoid full table rewrites.
5. **`CREATE INDEX CONCURRENTLY`** avoids locking the table during index creation.
6. **Advisory locks** are crash-safe application-level locks — use them for batch job coordination.
7. **Create a `lock_monitor` view** — you'll need it more often than you think.

---

## What's Next

Locks are under control. You've got monitoring, safe DDL patterns, and a healthy respect
for `AccessExclusiveLock`. The database is fast, clean, and well-connected.

Then at 4 AM, PagerDuty wakes you up. The primary PostgreSQL server's disk has died. There's
no replica. No failover. PayFlow is completely down. Every second of downtime is lost revenue.

What happens when the entire primary server goes down?

[Next: The Replication Setup →](pg-07-the-replication-setup.md)

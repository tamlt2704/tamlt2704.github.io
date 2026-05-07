# Chapter 16: Zero-Downtime DDL — Migrations That Don't Lock

[← Chapter 15: High Availability](chapter-15-high-availability.md) | [Chapter 17: Storage →](chapter-17-storage.md)

---

## The Fire

Saturday morning. Tournament starts in 2 hours. A developer pushes a migration:

```sql
ALTER TABLE matches ADD COLUMN tournament_id BIGINT REFERENCES tournaments(id);
```

The migration hangs. The `matches` table is locked. All queries against `matches` queue up. Matchmaking freezes. 50,000 players stare at loading screens.

You check:

```sql
SELECT pid, mode, granted, relation::regclass
FROM pg_locks
WHERE relation = 'matches'::regclass;
```

```
  pid  |        mode         | granted | relation
-------+---------------------+---------+----------
 12345 | AccessExclusiveLock | true    | matches
 12346 | AccessShareLock     | false   | matches
 12347 | AccessShareLock     | false   | matches
 ...   (4,821 waiting queries)
```

`AccessExclusiveLock` — the strongest lock. Blocks everything. The `ALTER TABLE` is waiting for all existing queries to finish, and all new queries wait for the ALTER.

Marta:

> "Kill it. Now. Then we'll do it the safe way."

```sql
SELECT pg_terminate_backend(12345);
```

---

## Why DDL Locks Are Dangerous

Most `ALTER TABLE` commands need an `AccessExclusiveLock`:

| Operation | Lock Level | Blocks Reads? | Blocks Writes? |
|-----------|-----------|---------------|----------------|
| ADD COLUMN (no default) | AccessExclusive | Yes | Yes |
| ADD COLUMN (with default, PG 11+) | AccessExclusive | Yes (briefly) | Yes (briefly) |
| DROP COLUMN | AccessExclusive | Yes | Yes |
| ALTER COLUMN TYPE | AccessExclusive | Yes (rewrites table!) | Yes |
| ADD CONSTRAINT (validated) | AccessExclusive | Yes | Yes |
| CREATE INDEX | ShareLock | No | Yes |
| CREATE INDEX CONCURRENTLY | ShareUpdateExclusive | No | No |

The lock isn't the problem — it's the **queue**. The ALTER waits for running queries to finish. While it waits, new queries queue behind it. A 2-second ALTER can cause 30 seconds of downtime if there's a long-running query ahead of it.

---

## Safe Pattern: Lock Timeout

```sql
-- Set a short lock timeout — fail fast instead of blocking
SET lock_timeout = '3s';

ALTER TABLE matches ADD COLUMN tournament_id BIGINT;

-- If it can't get the lock in 3 seconds, it fails:
-- ERROR: canceling statement due to lock timeout
-- No harm done. Retry later.
```

### Retry Loop (Application Code)

```python
import time

for attempt in range(5):
    try:
        db.execute("SET lock_timeout = '3s'")
        db.execute("ALTER TABLE matches ADD COLUMN tournament_id BIGINT")
        db.commit()
        break
    except LockTimeout:
        db.rollback()
        time.sleep(2)  # Wait and retry
```

---

## CREATE INDEX CONCURRENTLY

Regular `CREATE INDEX` blocks writes. On a 47M row table, that's minutes of write downtime:

```sql
-- ❌ Blocks writes for the entire build time
CREATE INDEX idx_matches_tournament ON matches (tournament_id);

-- ✅ Doesn't block reads OR writes
CREATE INDEX CONCURRENTLY idx_matches_tournament ON matches (tournament_id);
```

Trade-offs:
- Takes 2-3x longer (scans the table twice)
- Can't run inside a transaction
- If it fails, leaves an INVALID index (must drop and retry)

```sql
-- Check for invalid indexes after a failed CONCURRENTLY
SELECT indexrelid::regclass, indisvalid
FROM pg_index
WHERE NOT indisvalid;

-- Clean up invalid index
DROP INDEX CONCURRENTLY idx_matches_tournament;
-- Then retry
CREATE INDEX CONCURRENTLY idx_matches_tournament ON matches (tournament_id);
```

---

## Adding Columns Without Locks

### PG 11+: ADD COLUMN with DEFAULT is Fast

```sql
-- PG 11+: This is instant! (no table rewrite)
ALTER TABLE matches ADD COLUMN tournament_id BIGINT DEFAULT NULL;

-- This is also instant (default stored in catalog, not in rows)
ALTER TABLE players ADD COLUMN is_verified BOOLEAN DEFAULT false;
```

Before PG 11, `ADD COLUMN ... DEFAULT value` rewrote the entire table. Now it's metadata-only.

### Adding a NOT NULL Column Safely

```sql
-- Step 1: Add column as nullable (instant)
ALTER TABLE matches ADD COLUMN tournament_id BIGINT;

-- Step 2: Backfill in batches (no lock)
UPDATE matches SET tournament_id = 1
WHERE id BETWEEN 1 AND 1000000 AND tournament_id IS NULL;

UPDATE matches SET tournament_id = 1
WHERE id BETWEEN 1000001 AND 2000000 AND tournament_id IS NULL;
-- ... repeat in batches

-- Step 3: Add NOT NULL constraint with NOT VALID (instant, no scan)
ALTER TABLE matches ADD CONSTRAINT matches_tournament_not_null
    CHECK (tournament_id IS NOT NULL) NOT VALID;

-- Step 4: Validate the constraint (scans table but doesn't lock writes)
ALTER TABLE matches VALIDATE CONSTRAINT matches_tournament_not_null;
```

---

## NOT VALID Constraints

`NOT VALID` adds a constraint without checking existing rows:

```sql
-- Instant: only enforces on NEW rows
ALTER TABLE matches
ADD CONSTRAINT fk_matches_tournament
FOREIGN KEY (tournament_id) REFERENCES tournaments(id) NOT VALID;

-- Later: validate existing rows (ShareUpdateExclusiveLock — allows reads and writes)
ALTER TABLE matches VALIDATE CONSTRAINT fk_matches_tournament;
```

The validation scan takes time but doesn't block traffic.

---

## Backfilling Safely

Never update millions of rows in one transaction:

```sql
-- ❌ BAD: locks millions of rows, generates massive WAL, bloats table
UPDATE matches SET tournament_id = 1 WHERE tournament_id IS NULL;

-- ✅ GOOD: batch updates with pauses
DO $$
DECLARE
    batch_size INT := 50000;
    updated INT;
BEGIN
    LOOP
        UPDATE matches SET tournament_id = 1
        WHERE id IN (
            SELECT id FROM matches
            WHERE tournament_id IS NULL
            LIMIT batch_size
            FOR UPDATE SKIP LOCKED
        );

        GET DIAGNOSTICS updated = ROW_COUNT;
        EXIT WHEN updated = 0;

        RAISE NOTICE 'Updated % rows', updated;
        PERFORM pg_sleep(0.1);  -- Let other queries breathe
        COMMIT;
    END LOOP;
END $$;
```

---

## Renaming Columns/Tables Safely

```sql
-- ❌ Renaming a column breaks all queries instantly
ALTER TABLE matches RENAME COLUMN status TO match_status;

-- ✅ Safe approach: add new column, migrate, drop old
-- Step 1: Add new column
ALTER TABLE matches ADD COLUMN match_status VARCHAR(20);

-- Step 2: Backfill
UPDATE matches SET match_status = status WHERE match_status IS NULL;
-- (in batches)

-- Step 3: Add trigger to keep both in sync during transition
CREATE OR REPLACE FUNCTION sync_match_status() RETURNS trigger AS $$
BEGIN
    NEW.match_status := NEW.status;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_sync_status BEFORE INSERT OR UPDATE ON matches
FOR EACH ROW EXECUTE FUNCTION sync_match_status();

-- Step 4: Update application code to use new column
-- Step 5: Drop old column (after all code is deployed)
ALTER TABLE matches DROP COLUMN status;
```

---

## The Tournament Migration (Safe Version)

```sql
-- 1. Add column (instant, PG 11+)
SET lock_timeout = '3s';
ALTER TABLE matches ADD COLUMN tournament_id BIGINT;

-- 2. Create index concurrently (no lock)
CREATE INDEX CONCURRENTLY idx_matches_tournament_id
ON matches (tournament_id);

-- 3. Add FK constraint without validation (instant)
ALTER TABLE matches
ADD CONSTRAINT fk_matches_tournament
FOREIGN KEY (tournament_id) REFERENCES tournaments(id) NOT VALID;

-- 4. Validate FK (after tournament, during low traffic)
ALTER TABLE matches VALIDATE CONSTRAINT fk_matches_tournament;
```

Total downtime: **0 seconds**.

---

## Quick Reference

| Operation | Safe Pattern |
|-----------|-------------|
| Add column | `ADD COLUMN ... DEFAULT NULL` (instant PG 11+) |
| Add NOT NULL | Add nullable → backfill → `CHECK NOT VALID` → `VALIDATE` |
| Add index | `CREATE INDEX CONCURRENTLY` |
| Add FK | `ADD CONSTRAINT ... NOT VALID` → `VALIDATE` |
| Rename column | Add new → sync trigger → migrate code → drop old |
| Change column type | Add new column → backfill → swap |

| Safety Setting | Purpose |
|---------------|---------|
| `SET lock_timeout = '3s'` | Fail fast if lock unavailable |
| `SET statement_timeout = '30s'` | Kill long-running migrations |
| `NOT VALID` | Skip validation on existing rows |
| `CONCURRENTLY` | Non-blocking index creation |

| Lock Level | Operations |
|-----------|-----------|
| AccessExclusive | ALTER TABLE, DROP TABLE |
| ShareLock | CREATE INDEX (non-concurrent) |
| ShareUpdateExclusive | VALIDATE CONSTRAINT, CREATE INDEX CONCURRENTLY |
| RowExclusive | INSERT, UPDATE, DELETE |
| AccessShare | SELECT |

---

## Exercises

### Exercise 1: Safe Column Addition

Write a complete migration script that adds a `season_id BIGINT NOT NULL` column to the `matches` table with zero downtime. Include all steps from column creation to constraint validation.

### Exercise 2: Lock Monitoring

Write a query that shows all DDL operations currently waiting for locks, how long they've been waiting, and what's blocking them.

### Exercise 3: Batch Backfill

Write a backfill script that updates 47 million rows in batches of 100,000, with:
- Progress logging (% complete)
- 100ms pause between batches
- Ability to resume if interrupted

---

## What Happens Next

The migration is safe. The tournament column is added without downtime. But Ops Olga checks disk usage:

> "We're at 80% disk. The game_events table is 2TB. The old events from 2022 are never queried. Can we archive them?"

Time to learn about storage, compression, and archival.

---

[← Chapter 15: High Availability](chapter-15-high-availability.md) | [Chapter 17: Storage →](chapter-17-storage.md)

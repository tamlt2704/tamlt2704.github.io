# Chapter 13: Transactions — Race Conditions and Row Locking

[← Chapter 12: Connection Pooling](chapter-12-connection-pooling.md) | [Chapter 14: Replication →](chapter-14-replication.md)

---

## The Fire

Load test, Thursday night. Two requests arrive simultaneously for the same match:

```
Request A: Player 42 reports "I won match 12345"
Request B: Player 99 reports "I won match 12345"
```

Both requests read the match, see `status = 'active'`, and both update it:

```sql
-- Request A (runs at T=0ms)
SELECT * FROM matches WHERE id = 12345;  -- status = 'active'
UPDATE matches SET winner_id = 42, status = 'completed' WHERE id = 12345;
UPDATE players SET elo_rating = elo_rating + 25 WHERE id = 42;

-- Request B (runs at T=2ms, before A commits)
SELECT * FROM matches WHERE id = 12345;  -- STILL sees status = 'active'!
UPDATE matches SET winner_id = 99, status = 'completed' WHERE id = 12345;
UPDATE players SET elo_rating = elo_rating + 25 WHERE id = 99;
```

Result: Both players get +25 ELO. The match has two winners. The data is corrupt.

Marta:

> "You have a TOCTOU bug — Time Of Check to Time Of Use. You checked the status, then used it, but another transaction changed it in between. You need row locking."

---

## ACID Refresher

| Property | Meaning | Postgres Guarantee |
|----------|---------|-------------------|
| **Atomicity** | All or nothing | Transaction commits fully or rolls back |
| **Consistency** | Valid state to valid state | Constraints enforced |
| **Isolation** | Transactions don't interfere | Configurable isolation levels |
| **Durability** | Committed = permanent | WAL ensures crash recovery |

---

## Isolation Levels

```sql
-- Set isolation level for a transaction
BEGIN ISOLATION LEVEL READ COMMITTED;  -- Default
BEGIN ISOLATION LEVEL REPEATABLE READ;
BEGIN ISOLATION LEVEL SERIALIZABLE;
```

| Level | Dirty Read | Non-Repeatable Read | Phantom Read | Use Case |
|-------|-----------|--------------------|--------------|---------| 
| READ COMMITTED | No | Yes | Yes | Default, most queries |
| REPEATABLE READ | No | No | No* | Reports, consistent snapshots |
| SERIALIZABLE | No | No | No | Financial, critical correctness |

*PostgreSQL's REPEATABLE READ also prevents phantom reads (stricter than SQL standard).

### READ COMMITTED (Default)

Each statement sees the latest committed data:

```sql
-- Transaction A
BEGIN;
SELECT elo_rating FROM players WHERE id = 42;  -- 1500
-- ... time passes, Transaction B commits elo_rating = 1525 ...
SELECT elo_rating FROM players WHERE id = 42;  -- 1525 (sees B's commit!)
COMMIT;
```

### REPEATABLE READ

The transaction sees a snapshot from its start:

```sql
-- Transaction A
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT elo_rating FROM players WHERE id = 42;  -- 1500
-- ... Transaction B commits elo_rating = 1525 ...
SELECT elo_rating FROM players WHERE id = 42;  -- Still 1500!
COMMIT;
```

### SERIALIZABLE

Transactions behave as if they ran one at a time:

```sql
BEGIN ISOLATION LEVEL SERIALIZABLE;
-- If this transaction conflicts with another, one will be aborted:
-- ERROR: could not serialize access due to concurrent update
-- Your app must retry!
COMMIT;
```

---

## Row Locking: FOR UPDATE

The fix for the match race condition:

```sql
-- The correct pattern: lock the row before reading
BEGIN;

-- Lock the match row (other transactions wait here)
SELECT * FROM matches WHERE id = 12345 FOR UPDATE;

-- Now safely check and update
UPDATE matches
SET winner_id = 42, status = 'completed'
WHERE id = 12345 AND status = 'active';

-- Check if the update actually changed anything
-- (GET DIAGNOSTICS or check affected rows in your app)

UPDATE players SET elo_rating = elo_rating + 25 WHERE id = 42;
UPDATE players SET elo_rating = elo_rating - 25 WHERE id = 99;

COMMIT;
```

When Request B tries `SELECT ... FOR UPDATE`, it **waits** until Request A commits or rolls back. Then it sees `status = 'completed'` and knows not to update.

### FOR UPDATE Variants

```sql
-- FOR UPDATE: exclusive lock, blocks other FOR UPDATE and writes
SELECT * FROM matches WHERE id = 12345 FOR UPDATE;

-- FOR NO KEY UPDATE: allows concurrent inserts of FK references
SELECT * FROM matches WHERE id = 12345 FOR NO KEY UPDATE;

-- FOR SHARE: shared lock, allows other reads but blocks writes
SELECT * FROM matches WHERE id = 12345 FOR SHARE;

-- FOR KEY SHARE: weakest lock, only blocks key changes
SELECT * FROM matches WHERE id = 12345 FOR KEY SHARE;

-- NOWAIT: fail immediately instead of waiting
SELECT * FROM matches WHERE id = 12345 FOR UPDATE NOWAIT;
-- ERROR: could not obtain lock on row

-- SKIP LOCKED: skip locked rows (great for job queues)
SELECT * FROM matches WHERE status = 'pending'
ORDER BY created_at LIMIT 1 FOR UPDATE SKIP LOCKED;
```

---

## Deadlocks

Two transactions lock rows in opposite order:

```sql
-- Transaction A                    -- Transaction B
BEGIN;                              BEGIN;
UPDATE players SET ... WHERE id=42; UPDATE players SET ... WHERE id=99;
-- A holds lock on player 42        -- B holds lock on player 99
UPDATE players SET ... WHERE id=99; UPDATE players SET ... WHERE id=42;
-- A waits for B's lock on 99       -- B waits for A's lock on 42
-- DEADLOCK! Postgres kills one.
```

```
ERROR: deadlock detected
DETAIL: Process 12345 waits for ShareLock on transaction 67890;
        blocked by process 67891.
```

### Preventing Deadlocks

```sql
-- Rule: Always lock rows in a consistent order (e.g., by ID)
BEGIN;
-- Lock both players in ID order
SELECT * FROM players WHERE id IN (42, 99) ORDER BY id FOR UPDATE;
-- Now safely update both
UPDATE players SET elo_rating = elo_rating + 25 WHERE id = 42;
UPDATE players SET elo_rating = elo_rating - 25 WHERE id = 99;
COMMIT;
```

### Detecting Deadlocks

```sql
-- Check for blocked queries
SELECT
    blocked.pid AS blocked_pid,
    blocked.query AS blocked_query,
    blocking.pid AS blocking_pid,
    blocking.query AS blocking_query,
    now() - blocked.query_start AS wait_time
FROM pg_stat_activity blocked
JOIN pg_locks bl ON bl.pid = blocked.pid AND NOT bl.granted
JOIN pg_locks gl ON gl.locktype = bl.locktype
    AND gl.database = bl.database
    AND gl.relation = bl.relation
    AND gl.page = bl.page
    AND gl.tuple = bl.tuple
    AND gl.granted
JOIN pg_stat_activity blocking ON blocking.pid = gl.pid
WHERE blocked.pid != blocking.pid;
```

---

## Advisory Locks

Application-level locks that don't lock any table row:

```sql
-- Lock a "resource" by arbitrary ID (e.g., match_id)
SELECT pg_advisory_lock(12345);  -- Blocks until acquired

-- Do work...
UPDATE matches SET status = 'completed' WHERE id = 12345;

-- Release
SELECT pg_advisory_unlock(12345);

-- Try without blocking
SELECT pg_try_advisory_lock(12345);  -- Returns true/false immediately
```

### Use Case: Matchmaking Queue

```sql
-- Only one worker processes matchmaking at a time
BEGIN;
SELECT pg_advisory_xact_lock(hashtext('matchmaking'));
-- Process the queue...
-- Lock auto-releases on COMMIT
COMMIT;
```

`pg_advisory_xact_lock` auto-releases when the transaction ends (safer than manual unlock).

---

## The Complete Match Resolution Pattern

```sql
CREATE OR REPLACE FUNCTION resolve_match(
    p_match_id BIGINT,
    p_winner_id BIGINT
) RETURNS BOOLEAN AS $$
DECLARE
    v_match RECORD;
    v_loser_id BIGINT;
BEGIN
    -- Lock the match row
    SELECT * INTO v_match FROM matches
    WHERE id = p_match_id FOR UPDATE;

    -- Check if already resolved
    IF v_match.status != 'active' THEN
        RETURN FALSE;
    END IF;

    -- Determine loser
    v_loser_id := CASE
        WHEN v_match.player1_id = p_winner_id THEN v_match.player2_id
        ELSE v_match.player1_id
    END;

    -- Update match
    UPDATE matches SET
        winner_id = p_winner_id,
        status = 'completed',
        ended_at = now()
    WHERE id = p_match_id;

    -- Update ELO (lock in consistent order)
    PERFORM * FROM players
    WHERE id IN (p_winner_id, v_loser_id)
    ORDER BY id FOR UPDATE;

    UPDATE players SET elo_rating = elo_rating + 25 WHERE id = p_winner_id;
    UPDATE players SET elo_rating = elo_rating - 25 WHERE id = v_loser_id;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;
```

```sql
-- Usage (atomic, race-condition-free)
SELECT resolve_match(12345, 42);
```

---

## Quick Reference

| Lock Type | Syntax | Behavior |
|-----------|--------|----------|
| FOR UPDATE | `SELECT ... FOR UPDATE` | Exclusive row lock |
| FOR SHARE | `SELECT ... FOR SHARE` | Shared row lock |
| NOWAIT | `FOR UPDATE NOWAIT` | Fail instead of wait |
| SKIP LOCKED | `FOR UPDATE SKIP LOCKED` | Skip locked rows |
| Advisory | `pg_advisory_lock(id)` | App-level lock |

| Isolation Level | Snapshot | Retry Needed? |
|----------------|----------|---------------|
| READ COMMITTED | Per-statement | No |
| REPEATABLE READ | Per-transaction | Yes (serialization failure) |
| SERIALIZABLE | Per-transaction | Yes (serialization failure) |

| Deadlock Prevention | Strategy |
|--------------------|----------|
| Consistent ordering | Lock rows by ID ascending |
| Short transactions | Minimize lock hold time |
| NOWAIT | Fail fast, retry in app |
| Advisory locks | Coarse-grained coordination |

---

## Exercises

### Exercise 1: Race Condition Simulation

Open two `psql` sessions. Simulate the match race condition:
1. Both read the same match
2. Both try to update it
3. Observe what happens without FOR UPDATE
4. Add FOR UPDATE and observe the difference

### Exercise 2: Job Queue with SKIP LOCKED

Implement a simple job queue using `SKIP LOCKED`:

```sql
-- Create a queue table
CREATE TABLE match_queue (id SERIAL, match_id BIGINT, status TEXT DEFAULT 'pending');

-- Worker picks up a job (without blocking other workers)
-- Write the SELECT ... FOR UPDATE SKIP LOCKED pattern
```

### Exercise 3: Deadlock Detection

Create a deliberate deadlock between two transactions. Observe the error message. Then fix it using consistent lock ordering.

---

## What Happens Next

Transactions are safe. Race conditions are fixed. But the tournament needs more read capacity:

> "The leaderboard is read 10,000 times per second during the tournament. One server can't handle that."

Time to add read replicas.

---

[← Chapter 12: Connection Pooling](chapter-12-connection-pooling.md) | [Chapter 14: Replication →](chapter-14-replication.md)

# Chapter 5: Transactions

[← Ch 4](chapter-04-joins-relations.md) | [Ch 6 →](chapter-06-performance.md)

---

## Lena's Request

> "When a user creates a note with tags and tasks, ALL of it saves or NONE of it. If the app crashes mid-write, I can't have orphaned data. Also — the UI reads while background sync writes. Can SQLite handle that?"

---

## What Is a Transaction?

A transaction groups statements into one atomic unit:

```sql
BEGIN TRANSACTION;
INSERT INTO notes (title, content, folder_id) VALUES ('Sprint Plan', 'Week 3 goals', 3);
INSERT INTO tasks (note_id, description, priority) VALUES (last_insert_rowid(), 'Write API spec', 2);
INSERT INTO tasks (note_id, description, priority) VALUES (last_insert_rowid(), 'Review PRs', 1);
COMMIT;
```

If anything fails, roll back:

```sql
BEGIN TRANSACTION;
INSERT INTO notes (title) VALUES ('Test');
ROLLBACK;  -- Nothing saved
```

---

## Implicit Transactions and Performance

Every statement runs in its own transaction by default. Each transaction does a disk sync (fsync). This matters enormously:

```sql
-- SLOW: 1000 fsyncs (~50 rows/second)
INSERT INTO notes (title) VALUES ('Note 1');
INSERT INTO notes (title) VALUES ('Note 2');
-- ...

-- FAST: 1 fsync (~100,000+ rows/second)
BEGIN;
INSERT INTO notes (title) VALUES ('Note 1');
INSERT INTO notes (title) VALUES ('Note 2');
-- ...
COMMIT;
```

> **This is the single biggest SQLite performance tip.** Batch writes in transactions.

---

## Journal Modes

### DELETE Mode (Default)

Before modifying a page, copies the original to a journal file. On commit, deletes the journal. On crash, rolls back from the journal.

### WAL Mode (Write-Ahead Logging)

```sql
PRAGMA journal_mode = WAL;  -- Set once, persists in the file
```

Writes go to a separate WAL file. Readers see a consistent snapshot from the main file.

| Feature | DELETE Mode | WAL Mode |
|---------|------------|----------|
| Readers during write | ❌ Blocked | ✅ Unlimited |
| Write performance | Good | Better |
| Database files | 1 + temp journal | 3 (db + wal + shm) |

**WAL mode is essential for Jotter** — the UI thread reads while background writes happen without blocking.

---

## PRAGMA synchronous

```sql
PRAGMA synchronous = NORMAL;  -- Safe with WAL, fast (recommended)
PRAGMA synchronous = FULL;    -- Safest, slower
PRAGMA synchronous = OFF;     -- Fastest, risk of data loss on crash
```

---

## Savepoints (Nested Transactions)

```sql
BEGIN;
INSERT INTO notes (title) VALUES ('Parent note');
SAVEPOINT add_tasks;
INSERT INTO tasks (note_id, description) VALUES (last_insert_rowid(), 'Task 1');
ROLLBACK TO add_tasks;  -- Undo just the tasks
COMMIT;                 -- Note saved, tasks discarded
```

---

## Concurrency and Locking

- **Multiple readers:** Unlimited (WAL mode)
- **One writer at a time:** Others get SQLITE_BUSY
- **Busy timeout:** Retry instead of failing

```sql
PRAGMA busy_timeout = 5000;  -- Wait up to 5 seconds for lock
```

---

## The Connection Setup Recipe

Run these on every connection open:

```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA foreign_keys = ON;
PRAGMA busy_timeout = 5000;
PRAGMA cache_size = -20000;  -- 20MB cache (negative = KB)
```

---

## Common Mistakes

| Mistake | Why It Happens | Fix |
|---------|---------------|-----|
| Inserting in a loop without BEGIN/COMMIT | Each insert = separate transaction | Wrap bulk inserts in one transaction |
| Not handling SQLITE_BUSY | Another thread writing | Set `busy_timeout` or retry in code |
| Using DELETE mode with concurrent access | Readers block during writes | Switch to WAL |
| Setting `synchronous = OFF` for user data | Chasing benchmarks | NORMAL with WAL is fast enough |
| Long-running transactions | Holds write lock | Keep transactions short |
| Copying .db without .wal file | Incomplete backup | Copy all 3 files, or checkpoint first |

---

## Exercise

1. Time the difference: insert 1000 rows individually vs. in one transaction (`.timer on`)
2. Set WAL mode and verify with `PRAGMA journal_mode;`
3. Open two sqlite3 sessions. In session 1, BEGIN + INSERT (don't COMMIT). In session 2, try to INSERT — observe BUSY. Set busy_timeout and retry.
4. Write a transaction creating a note with 3 tasks and 2 tags atomically
5. Use SAVEPOINT to insert tasks, rollback just the tasks, then commit the note
6. Check your settings: `PRAGMA journal_mode; PRAGMA synchronous;`

---

## Quick Reference

| Command | What It Does |
|---------|-------------|
| `BEGIN;` | Start transaction |
| `COMMIT;` | Save changes |
| `ROLLBACK;` | Undo since BEGIN |
| `SAVEPOINT name;` | Nested checkpoint |
| `ROLLBACK TO name;` | Undo to savepoint |
| `RELEASE name;` | Commit savepoint |
| `PRAGMA journal_mode = WAL;` | Enable WAL |
| `PRAGMA synchronous = NORMAL;` | Safe + fast |
| `PRAGMA busy_timeout = 5000;` | Wait for locks |

---

[← Ch 4](chapter-04-joins-relations.md) | [Ch 6: Performance →](chapter-06-performance.md)

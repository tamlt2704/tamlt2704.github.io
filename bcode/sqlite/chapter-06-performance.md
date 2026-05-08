# Chapter 6: Performance

[← Ch 5](chapter-05-transactions.md) | [Ch 7 →](chapter-07-fts.md)

---

## Lena's Request

> "The notes list loads fine with 50 notes. But with 10,000 it takes 800ms. I need the main list under 50ms. How do I find what's slow and fix it?"

---

## EXPLAIN QUERY PLAN

```sql
EXPLAIN QUERY PLAN
SELECT * FROM notes WHERE folder_id = 3 ORDER BY created_at DESC;
```

Without index: `SCAN notes` — reads every row. With index: `SEARCH notes USING INDEX` — jumps to matches.

| Term | Meaning | Speed |
|------|---------|-------|
| `SCAN` | Full table scan | 🐌 Slow |
| `SEARCH` | Uses index | 🚀 Fast |
| `USING COVERING INDEX` | All data in index | ⚡ Fastest |
| `USE TEMP B-TREE` | Sorting without index | Moderate |

---

## How Indexes Work

SQLite uses B-trees. The table is a B-tree keyed by rowid. Each index is a separate B-tree:

```
Index B-tree: folder_id → rowid
Lookup: O(log n) instead of O(n)
10,000 rows: ~14 page reads vs 10,000 row scans
```

```sql
CREATE INDEX idx_notes_folder ON notes(folder_id);
```

---

## Composite Indexes

Column order matters. Leftmost columns must appear in WHERE:

```sql
-- Serves both WHERE and ORDER BY
CREATE INDEX idx_notes_pinned_date ON notes(is_pinned, created_at DESC);

-- ✅ Uses index (leftmost column)
SELECT * FROM notes WHERE is_pinned = 1;

-- ✅ Uses index (both columns)
SELECT * FROM notes WHERE is_pinned = 1 ORDER BY created_at DESC;

-- ❌ Cannot use this index (skips leftmost)
SELECT * FROM notes WHERE created_at > '2024-01-01';
```

---

## Covering Indexes

Contains ALL columns the query needs — no table lookup:

```sql
CREATE INDEX idx_notes_list ON notes(is_pinned, updated_at DESC, title);

-- EXPLAIN shows: USING COVERING INDEX
SELECT title, updated_at FROM notes WHERE is_pinned = 1 ORDER BY updated_at DESC;
```

Trade-off: larger index, but fastest possible reads for hot queries.

---

## Partial Indexes

Index only rows you care about:

```sql
-- Only 5% of notes are pinned, but queried constantly
CREATE INDEX idx_pinned ON notes(created_at DESC) WHERE is_pinned = 1;

-- Only incomplete tasks
CREATE INDEX idx_tasks_pending ON tasks(due_date, priority) WHERE is_done = 0;
```

Tiny index, perfect for the query. Supported since SQLite 3.8.0.

---

## ANALYZE

Helps the query planner make better decisions:

```sql
ANALYZE;  -- Collect statistics about all tables
SELECT * FROM sqlite_stat1;  -- See what it collected
```

Run after bulk inserts or significant data changes.

---

## Patterns That Prevent Index Use

```sql
-- ❌ Function on indexed column
SELECT * FROM notes WHERE DATE(created_at) = '2024-01-15';
-- ✅ Rewrite as range
SELECT * FROM notes WHERE created_at >= '2024-01-15' AND created_at < '2024-01-16';

-- ❌ Leading wildcard
SELECT * FROM notes WHERE title LIKE '%meeting%';
-- ✅ Use FTS5 (Chapter 7)

-- ❌ Type mismatch
SELECT * FROM tasks WHERE is_done = '0';
-- ✅ Match stored type
SELECT * FROM tasks WHERE is_done = 0;
```

---

## Jotter's Index Strategy

```sql
-- Main list (hot path — every app launch)
CREATE INDEX idx_notes_list ON notes(is_pinned DESC, updated_at DESC);
CREATE INDEX idx_notes_folder ON notes(folder_id);

-- Task dashboard
CREATE INDEX idx_tasks_pending ON tasks(is_done, due_date, priority) WHERE is_done = 0;
CREATE INDEX idx_tasks_note ON tasks(note_id);

-- Tag lookups
CREATE INDEX idx_note_tags_tag ON note_tags(tag_id);
```

---

## Measuring

```sql
.timer on
SELECT COUNT(*) FROM notes;
-- Run Time: real 0.001 user 0.000 sys 0.000
```

> **SQLite-specific:** Unlike Postgres, SQLite indexes don't bloat over time. No periodic REINDEX needed unless you suspect corruption.

---

## Common Mistakes

| Mistake | Why It Happens | Fix |
|---------|---------------|-----|
| No index on FK columns | Assumes auto-indexing | SQLite doesn't — add manually |
| Too many indexes | "Index everything!" | Only index columns in frequent WHERE/ORDER BY |
| Wrong composite order | Doesn't understand leftmost prefix | Equality columns first, range/sort last |
| Function on indexed column | `WHERE LOWER(title) = 'x'` | Expression index or restructure |
| Not running ANALYZE | Planner makes bad choices | Run after bulk data changes |
| Indexing low-cardinality alone | `is_done` has 2 values | Combine with other columns or use partial index |

---

## Exercise

1. Insert 10,000 notes in a transaction
2. Run EXPLAIN QUERY PLAN on: `SELECT * FROM notes WHERE folder_id = 3 ORDER BY created_at DESC LIMIT 20`
3. Add an index and confirm SEARCH in the plan
4. Create a covering index for the notes list and confirm COVERING INDEX
5. Use `.timer on` to measure before/after
6. Run ANALYZE and check `sqlite_stat1`

---

## Quick Reference

| Command | What It Does |
|---------|-------------|
| `EXPLAIN QUERY PLAN ...` | Show execution plan |
| `CREATE INDEX name ON t(cols)` | B-tree index |
| `CREATE INDEX ... WHERE cond` | Partial index |
| `.timer on` | Show query time |
| `ANALYZE` | Collect statistics |
| `REINDEX` | Rebuild indexes |
| `DROP INDEX name` | Remove index |

---

[← Ch 5](chapter-05-transactions.md) | [Ch 7: Full-Text Search →](chapter-07-fts.md)

# Chapter 2: Queries

[← Ch 1](chapter-01-first-database.md) | [Ch 3 →](chapter-03-schema-design.md)

---

## Lena's Request

> "Users need to search notes, sort by date, filter by pinned status, and see stats like 'how many notes this week.' Give me the query patterns for the UI."

---

## Setup Data

```sql
INSERT INTO notes (title, content, is_pinned, created_at) VALUES
    ('Meeting Notes', 'Discussed Q1 roadmap and hiring plan', 1, '2024-01-15 09:00:00'),
    ('Shopping List', 'Milk, eggs, coffee, bread', 0, '2024-01-14 18:30:00'),
    ('Project Ideas', 'Habit tracker, recipe app, budget tool', 1, '2024-01-13 14:00:00'),
    ('Book Notes: DDIA', 'Chapter on replication was excellent', 0, '2024-01-12 20:00:00'),
    ('Workout Plan', 'Mon chest, Wed back, Fri legs', 0, '2024-01-11 07:00:00'),
    ('Recipe: Carbonara', 'Eggs, pecorino, guanciale, pepper', 0, '2024-01-10 19:00:00'),
    ('Sprint Retro', 'What went well: deployment pipeline', 1, '2024-01-08 16:00:00'),
    ('Daily Journal', 'Shipped the auth module today.', 0, '2024-01-06 21:00:00');
```

---

## WHERE Clauses

```sql
SELECT title FROM notes WHERE is_pinned = 1;
SELECT title, created_at FROM notes WHERE created_at > '2024-01-12';
SELECT title FROM notes WHERE created_at BETWEEN '2024-01-10' AND '2024-01-14';
SELECT title FROM notes WHERE id IN (1, 3, 5);
```

### NULL Handling

```sql
SELECT title FROM notes WHERE content IS NULL;      -- Correct
SELECT title FROM notes WHERE content IS NOT NULL;  -- Correct
SELECT title FROM notes WHERE content = NULL;       -- WRONG: always empty
```

---

## Pattern Matching: LIKE and GLOB

```sql
-- LIKE: case-insensitive, % = any chars, _ = one char
SELECT title FROM notes WHERE title LIKE '%list%';
SELECT title FROM notes WHERE title LIKE 'Book%';

-- GLOB: case-sensitive, Unix-style wildcards
SELECT title FROM notes WHERE title GLOB '*List*';   -- Capital L
SELECT title FROM notes WHERE title GLOB '[A-M]*';   -- Starts with A-M
```

| | LIKE | GLOB |
|---|------|------|
| Case | Insensitive (ASCII) | Sensitive |
| Any chars | `%` | `*` |
| One char | `_` | `?` |
| Ranges | No | `[a-z]` |

---

## ORDER BY and LIMIT

```sql
-- Newest first
SELECT title, created_at FROM notes ORDER BY created_at DESC;

-- Pinned first, then by date (Lena's main list pattern)
SELECT title FROM notes ORDER BY is_pinned DESC, created_at DESC;

-- Pagination
SELECT title FROM notes ORDER BY created_at DESC LIMIT 5;
SELECT title FROM notes ORDER BY created_at DESC LIMIT 5 OFFSET 5;
```

> **Performance:** OFFSET gets slower as it grows. For large datasets, use keyset pagination: `WHERE created_at < :last_seen ORDER BY created_at DESC LIMIT 5`.

---

## Aggregate Functions

```sql
SELECT COUNT(*) AS total FROM notes;
SELECT COUNT(*) AS pinned FROM notes WHERE is_pinned = 1;
SELECT MIN(created_at) AS oldest, MAX(created_at) AS newest FROM notes;
SELECT AVG(LENGTH(title)) AS avg_title_length FROM notes;
SELECT SUM(LENGTH(content)) AS total_bytes FROM notes;
```

### GROUP BY

```sql
-- Notes per day
SELECT DATE(created_at) AS day, COUNT(*) AS n
FROM notes GROUP BY day ORDER BY day DESC;

-- Pinned vs unpinned
SELECT
    CASE is_pinned WHEN 1 THEN 'Pinned' ELSE 'Regular' END AS type,
    COUNT(*) AS count
FROM notes GROUP BY is_pinned;
```

### HAVING

```sql
SELECT DATE(created_at) AS day, COUNT(*) AS n
FROM notes GROUP BY day HAVING n > 1;
```

---

## Combining Conditions

```sql
SELECT title FROM notes
WHERE is_pinned = 1 AND created_at > datetime('now', '-7 days');

SELECT title FROM notes
WHERE is_pinned = 1 OR title LIKE '%project%';

-- Use parentheses to clarify precedence
SELECT title FROM notes
WHERE (is_pinned = 1 OR title LIKE '%project%') AND content IS NOT NULL;
```

---

## Date/Time Functions

```sql
SELECT datetime('now');                        -- Current timestamp
SELECT datetime('now', '-7 days');             -- One week ago
SELECT datetime('now', 'start of month');      -- First of month
SELECT strftime('%Y', created_at) AS year FROM notes;

-- Notes created today
SELECT title FROM notes WHERE DATE(created_at) = DATE('now');
```

> **SQLite-specific:** No date type — these functions operate on TEXT strings in ISO 8601 format. They're fast and flexible.

---

## Common Mistakes

| Mistake | Why It Happens | Fix |
|---------|---------------|-----|
| `WHERE content = NULL` | Treating NULL like a value | Use `IS NULL` |
| `LIKE` without `%` | Expects exact match | `LIKE '%term%'` for contains |
| `ORDER BY` without `LIMIT` for "most recent" | Sorting entire table | Add `LIMIT 1` |
| Mixing AND/OR without parens | Precedence confusion | Always use parentheses |
| `GROUP BY` without aggregate | Undefined row returned | Pair with COUNT/MAX/etc. |

---

## Exercise

1. Find all notes whose title contains "Notes" (case-insensitive)
2. Get the 3 most recent unpinned notes
3. Count notes created before January 12
4. Find the longest note by content length — show title and length
5. Group notes by pinned status with count and average content length
6. Find notes created on a weekend (hint: `strftime('%w', created_at)` — 0=Sunday, 6=Saturday)

---

## Quick Reference

| Pattern | Example |
|---------|---------|
| Filter | `WHERE col = value` |
| Pattern | `WHERE col LIKE '%text%'` |
| Null check | `WHERE col IS NULL` |
| Range | `WHERE col BETWEEN a AND b` |
| Set | `WHERE col IN (1, 2, 3)` |
| Sort | `ORDER BY col DESC` |
| Paginate | `LIMIT 10 OFFSET 20` |
| Count | `COUNT(*)` |
| Group | `GROUP BY col HAVING cond` |
| Current time | `datetime('now')` |
| Date math | `datetime('now', '-7 days')` |

---

[← Ch 1](chapter-01-first-database.md) | [Ch 3: Schema Design →](chapter-03-schema-design.md)

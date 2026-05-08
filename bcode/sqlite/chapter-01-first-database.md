# Chapter 1: Your First Database

[← Ch 0](chapter-00-overview.md) | [Ch 2 →](chapter-02-queries.md)

---

## Lena's Request

> "I need a `notes` table. Each note has a title, content, a pinned flag, and timestamps. Let me insert a few test notes and query them back."

---

## Creating the Database

```bash
sqlite3 jotter.db
```

That's it. If `jotter.db` doesn't exist, SQLite creates it. No `CREATE DATABASE` command. No connection strings.

---

## Your First Table

```sql
CREATE TABLE notes (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    is_pinned INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
```

### SQLite-Specific Details

- **INTEGER PRIMARY KEY** is an alias for the internal `rowid` — auto-increments automatically, lookups are extremely fast (it's the B-tree key itself). No `SERIAL` or `AUTO_INCREMENT` needed.
- **No BOOLEAN type** — use INTEGER with 0/1. `is_pinned INTEGER DEFAULT 0` stores false.
- **No DATETIME type** — store ISO 8601 strings in TEXT. `datetime('now')` returns `'2024-01-15 09:30:00'`.
- **Expression defaults** require parentheses: `DEFAULT (datetime('now'))`.

---

## Inserting Data

```sql
INSERT INTO notes (title, content) VALUES
    ('Meeting Notes', 'Discussed Q1 roadmap with the team');

INSERT INTO notes (title, content, is_pinned) VALUES
    ('Shopping List', '- Milk\n- Eggs\n- Coffee', 0),
    ('Project Ideas', 'Build a habit tracker app', 1),
    ('Book Notes', 'Chapter 5 was about distributed systems', 0);
```

We didn't specify `id`, `created_at`, or `updated_at` — they fill in automatically.

---

## Querying Data

```sql
SELECT * FROM notes;
SELECT title, created_at FROM notes;
SELECT title FROM notes WHERE is_pinned = 1;
SELECT COUNT(*) FROM notes;
```

---

## Dynamic Typing (Type Affinity)

This shocks Postgres developers:

```sql
INSERT INTO notes (title, content, is_pinned) VALUES ('Weird', 'Testing', 'yes');
```

This *works*. SQLite stored the string `'yes'` in an INTEGER column. SQLite uses **type affinity**, not strict types.

| Storage Class | Description |
|--------------|-------------|
| NULL | Null value |
| INTEGER | Signed integer (1-8 bytes) |
| REAL | 8-byte floating point |
| TEXT | UTF-8 string |
| BLOB | Raw binary |

Check what's stored: `SELECT title, typeof(is_pinned) FROM notes;`

> **Strict mode (3.37+):** `CREATE TABLE notes (...) STRICT;` enforces types like Postgres.

---

## Useful Dot-Commands

```sql
.tables              -- List all tables
.schema notes        -- Show CREATE statement
.mode column         -- Aligned columns
.headers on          -- Show column headers
.mode csv            -- CSV output
.mode json           -- JSON output
```

> **Pro tip:** Create `~/.sqliterc` with `.mode column` and `.headers on` for persistent defaults.

---

## Updating and Deleting

```sql
UPDATE notes SET is_pinned = 1, updated_at = datetime('now') WHERE id = 1;
DELETE FROM notes WHERE id = 4;
```

> **Common mistake:** Forgetting WHERE on UPDATE/DELETE. SQLite won't ask "are you sure?"

---

## The Database File

```bash
ls -la jotter.db
```

One file. You can copy it (`cp jotter.db backup.db`), move it, email it, or delete it. That's the entire backup/uninstall process.

---

## Common Mistakes

| Mistake | Why It Happens | Fix |
|---------|---------------|-----|
| Using `AUTOINCREMENT` keyword | Thinks it's required | `INTEGER PRIMARY KEY` auto-increments without it (and is faster) |
| Storing dates as Unix timestamps | Habit from other systems | Use TEXT with ISO 8601 — SQLite's date functions expect it |
| Using `SELECT *` in app code | Lazy habit | Name columns — schema changes won't break your app |
| Forgetting `NOT NULL` on title | Allows empty notes | Always constrain required fields |

---

## Exercise

1. Create a `tasks` table: `id`, `description` (TEXT NOT NULL), `is_done` (INTEGER DEFAULT 0), `due_date` (TEXT), `created_at` (TEXT with default)
2. Insert 5 tasks with different due dates
3. Query only incomplete tasks
4. Mark one task as done
5. Try inserting a string in `is_done` — observe SQLite allows it
6. Use `.schema` to verify your table structure

---

## Quick Reference

| SQL | What It Does |
|-----|-------------|
| `CREATE TABLE t (...)` | Create a new table |
| `INSERT INTO t (cols) VALUES (vals)` | Add a row |
| `SELECT cols FROM t` | Query rows |
| `UPDATE t SET col=val WHERE ...` | Modify rows |
| `DELETE FROM t WHERE ...` | Remove rows |
| `DROP TABLE t` | Delete entire table |
| `.tables` | List all tables |
| `.schema t` | Show CREATE statement |
| `.quit` | Exit sqlite3 |

---

[← Ch 0](chapter-00-overview.md) | [Ch 2: Queries →](chapter-02-queries.md)

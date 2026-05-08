# Chapter 10: Migrations

[← Ch 9](chapter-09-triggers-views.md) | [Ch 11 →](chapter-11-backup-integrity.md)

---

## Lena's Request

> "We shipped v1. Now v2 needs a `color` column, a `reminders` table, and we want to rename `is_pinned` to `pinned`. How do I evolve the schema without losing user data?"

---

## ALTER TABLE: What SQLite Supports

| Operation | Supported | Since |
|-----------|-----------|-------|
| ADD COLUMN | ✅ | Always |
| RENAME TABLE | ✅ | Always |
| RENAME COLUMN | ✅ | 3.25.0 (2018) |
| DROP COLUMN | ✅ | 3.35.0 (2021) |
| ALTER COLUMN type | ❌ | — |
| ADD/DROP CONSTRAINT | ❌ | — |

```sql
ALTER TABLE notes ADD COLUMN color TEXT DEFAULT '#FFFFFF';
ALTER TABLE notes RENAME COLUMN is_pinned TO pinned;
ALTER TABLE notes DROP COLUMN color;  -- 3.35+ only
```

---

## The 12-Step Migration Process

When ALTER TABLE can't do what you need (change types, add constraints):

```sql
PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

-- 1. Create new table with desired schema
CREATE TABLE notes_new (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    folder_id INTEGER NOT NULL DEFAULT 1 REFERENCES folders(id),
    pinned INTEGER DEFAULT 0 CHECK (pinned IN (0, 1)),
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    metadata TEXT
);

-- 2. Copy data (transform as needed)
INSERT INTO notes_new (id, title, content, folder_id, pinned, created_at, updated_at, metadata)
SELECT id, title, content, COALESCE(folder_id, 1), is_pinned, created_at, updated_at, metadata
FROM notes;

-- 3. Drop old, rename new
DROP TABLE notes;
ALTER TABLE notes_new RENAME TO notes;

-- 4. Recreate indexes
CREATE INDEX idx_notes_folder ON notes(folder_id);
CREATE INDEX idx_notes_created ON notes(created_at DESC);

-- 5. Recreate triggers
CREATE TRIGGER notes_update_timestamp AFTER UPDATE ON notes
FOR EACH ROW WHEN old.updated_at = new.updated_at
BEGIN UPDATE notes SET updated_at = datetime('now') WHERE id = new.id; END;

-- 6. Verify and commit
PRAGMA integrity_check;
PRAGMA foreign_key_check;
COMMIT;
PRAGMA foreign_keys = ON;
```

> Every SQLite migration tool (Room, Core Data, Flyway) uses this pattern internally.

---

## Tracking Versions: user_version

```sql
PRAGMA user_version;      -- Returns 0 for new databases
PRAGMA user_version = 3;  -- Set after migration
```

App startup: check version → run pending migrations → update version.

---

## Migration Scripts

```sql
-- migration_001_initial.sql
CREATE TABLE IF NOT EXISTS folders (...);
CREATE TABLE IF NOT EXISTS notes (...);
CREATE TABLE IF NOT EXISTS tags (...);
CREATE TABLE IF NOT EXISTS note_tags (...);
CREATE TABLE IF NOT EXISTS tasks (...);
PRAGMA user_version = 1;

-- migration_002_add_color.sql
ALTER TABLE notes ADD COLUMN color TEXT DEFAULT '#FFFFFF';
PRAGMA user_version = 2;

-- migration_003_add_reminders.sql
CREATE TABLE reminders (
    id INTEGER PRIMARY KEY,
    note_id INTEGER REFERENCES notes(id) ON DELETE CASCADE,
    remind_at TEXT NOT NULL,
    is_fired INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX idx_reminders_pending ON reminders(remind_at) WHERE is_fired = 0;
PRAGMA user_version = 3;

-- migration_004_restructure_tasks.sql (12-step)
PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;
CREATE TABLE tasks_new (...);
INSERT INTO tasks_new SELECT ... FROM tasks;
DROP TABLE tasks;
ALTER TABLE tasks_new RENAME TO tasks;
CREATE INDEX idx_tasks_note ON tasks(note_id);
COMMIT;
PRAGMA foreign_keys = ON;
PRAGMA user_version = 4;
```

---

## Running Migrations in Code

```python
import sqlite3

MIGRATIONS = [
    (1, "migration_001_initial.sql"),
    (2, "migration_002_add_color.sql"),
    (3, "migration_003_add_reminders.sql"),
    (4, "migration_004_restructure_tasks.sql"),
]

def migrate(db_path):
    conn = sqlite3.connect(db_path)
    current = conn.execute("PRAGMA user_version").fetchone()[0]
    for version, filename in MIGRATIONS:
        if current < version:
            with open(filename) as f:
                conn.executescript(f.read())
    conn.close()
```

---

## Backward Compatibility Rules

1. **Never remove columns old code reads** — add new ones instead
2. **Use DEFAULT values** — old rows get sensible defaults
3. **ADD COLUMN is always safe** — doesn't rewrite the table
4. **Test with old data** — create v1 database, run migrations, verify

### ADD COLUMN Limitations

- Cannot have PRIMARY KEY or UNIQUE
- If NOT NULL, MUST have a non-NULL default
- Cannot be a generated column

```sql
ALTER TABLE notes ADD COLUMN archived INTEGER DEFAULT 0;       -- ✅
ALTER TABLE notes ADD COLUMN category TEXT NOT NULL;            -- ❌ No default
ALTER TABLE notes ADD COLUMN category TEXT NOT NULL DEFAULT ''; -- ✅
```

---

## Common Mistakes

| Mistake | Why It Happens | Fix |
|---------|---------------|-----|
| Forgetting `PRAGMA foreign_keys = OFF` | FK check fails during 12-step | Disable, migrate, re-enable |
| No transaction wrapper | Crash = corrupt state | Always BEGIN/COMMIT |
| Forgetting to recreate indexes | Queries slow after migration | Include all indexes in script |
| Forgetting to recreate triggers | Automation breaks | Include all triggers |
| Not testing with real data | Works empty, fails with data | Test with production-like data |
| Using IF NOT EXISTS without version check | Partial migrations | Use user_version as gate |

---

## Exercise

1. Create a v1 database with test data
2. Write a migration adding a `color` column
3. Write a migration adding a `reminders` table
4. Write a 12-step migration adding CHECK to `tasks.priority`
5. Implement version checking: read user_version, run pending, update
6. Verify with `PRAGMA integrity_check` after each migration

---

## Quick Reference

| Command | What It Does |
|---------|-------------|
| `ALTER TABLE t ADD COLUMN c TYPE DEFAULT v` | Add column |
| `ALTER TABLE t RENAME COLUMN old TO new` | Rename (3.25+) |
| `ALTER TABLE t DROP COLUMN c` | Drop (3.35+) |
| `PRAGMA user_version` | Get schema version |
| `PRAGMA user_version = N` | Set schema version |
| `PRAGMA foreign_keys = OFF` | Disable for migration |
| `PRAGMA integrity_check` | Verify integrity |
| `PRAGMA foreign_key_check` | Check FK consistency |

---

[← Ch 9](chapter-09-triggers-views.md) | [Ch 11: Backup & Integrity →](chapter-11-backup-integrity.md)

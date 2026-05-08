# Chapter 9: Triggers & Views

[← Ch 8](chapter-08-json.md) | [Ch 10 →](chapter-10-migrations.md)

---

## Lena's Request

> "Every time a note is edited, `updated_at` should refresh automatically. I want an audit trail of changes. And a 'dashboard view' that avoids rewriting that giant JOIN every time."

---

## Views: Saved Queries

A view is a named query — no data stored, runs on every SELECT:

```sql
CREATE VIEW notes_dashboard AS
SELECT
    n.id, n.title, n.is_pinned, n.created_at, n.updated_at,
    f.name AS folder_name, f.icon AS folder_icon,
    (SELECT COUNT(*) FROM tasks t WHERE t.note_id = n.id) AS task_count,
    (SELECT SUM(is_done) FROM tasks t WHERE t.note_id = n.id) AS tasks_done,
    GROUP_CONCAT(DISTINCT tg.name) AS tags
FROM notes n
LEFT JOIN folders f ON n.folder_id = f.id
LEFT JOIN note_tags nt ON n.id = nt.note_id
LEFT JOIN tags tg ON nt.tag_id = tg.id
GROUP BY n.id;

-- Now Lena's code is simple:
SELECT * FROM notes_dashboard ORDER BY is_pinned DESC, updated_at DESC LIMIT 50;
```

```sql
CREATE VIEW pending_tasks AS
SELECT t.id, t.description, t.priority, t.due_date,
    n.title AS note_title, f.name AS folder_name
FROM tasks t
INNER JOIN notes n ON t.note_id = n.id
LEFT JOIN folders f ON n.folder_id = f.id
WHERE t.is_done = 0;

CREATE VIEW overdue_tasks AS
SELECT * FROM pending_tasks WHERE due_date < date('now') AND due_date IS NOT NULL;
```

### Managing Views

```sql
SELECT name FROM sqlite_master WHERE type = 'view';
DROP VIEW IF EXISTS notes_dashboard;
```

> **SQLite-specific:** No `CREATE OR REPLACE VIEW`. Must DROP then CREATE. Views are read-only — no INSERT/UPDATE through views.

---

## Triggers: Automatic Actions

### Auto-Updating Timestamps

```sql
CREATE TRIGGER notes_update_timestamp
AFTER UPDATE ON notes
FOR EACH ROW
WHEN old.updated_at = new.updated_at
BEGIN
    UPDATE notes SET updated_at = datetime('now') WHERE id = new.id;
END;
```

The WHEN clause prevents infinite recursion (the trigger's UPDATE would fire itself).

### Trigger Timing

| Timing | Use Case |
|--------|----------|
| `BEFORE INSERT` | Validation, defaults |
| `AFTER INSERT` | Logging, FTS sync |
| `BEFORE UPDATE` | Prevent changes |
| `AFTER UPDATE` | Timestamps, audit |
| `BEFORE DELETE` | Archive, prevent |
| `AFTER DELETE` | Cleanup, logging |

---

## Audit Trail

```sql
CREATE TABLE notes_audit (
    id INTEGER PRIMARY KEY,
    note_id INTEGER,
    action TEXT NOT NULL,
    field_name TEXT,
    old_value TEXT,
    new_value TEXT,
    changed_at TEXT DEFAULT (datetime('now'))
);

CREATE TRIGGER notes_audit_insert AFTER INSERT ON notes BEGIN
    INSERT INTO notes_audit (note_id, action, new_value)
    VALUES (new.id, 'INSERT', new.title);
END;

CREATE TRIGGER notes_audit_title AFTER UPDATE OF title ON notes BEGIN
    INSERT INTO notes_audit (note_id, action, field_name, old_value, new_value)
    VALUES (new.id, 'UPDATE', 'title', old.title, new.title);
END;

CREATE TRIGGER notes_audit_delete BEFORE DELETE ON notes BEGIN
    INSERT INTO notes_audit (note_id, action, old_value)
    VALUES (old.id, 'DELETE', old.title);
END;
```

> **SQLite-specific:** `AFTER UPDATE OF column` fires only when that specific column changes.

---

## Validation Triggers

```sql
CREATE TRIGGER notes_validate_title BEFORE INSERT ON notes BEGIN
    SELECT RAISE(ABORT, 'Title cannot be empty')
    WHERE TRIM(new.title) = '';
END;

CREATE TRIGGER tasks_limit BEFORE INSERT ON tasks BEGIN
    SELECT RAISE(ABORT, 'Maximum 100 tasks per note')
    WHERE (SELECT COUNT(*) FROM tasks WHERE note_id = new.note_id) >= 100;
END;

CREATE TRIGGER notes_protect_pinned BEFORE DELETE ON notes
WHEN old.is_pinned = 1 BEGIN
    SELECT RAISE(ABORT, 'Cannot delete pinned note. Unpin first.');
END;
```

| RAISE Function | Behavior |
|----------------|----------|
| `RAISE(ABORT, msg)` | Abort statement, rollback its changes |
| `RAISE(ROLLBACK, msg)` | Rollback entire transaction |
| `RAISE(FAIL, msg)` | Abort but keep prior changes |
| `RAISE(IGNORE)` | Silently skip row |

---

## Auto-Sort Tasks

```sql
CREATE TRIGGER tasks_auto_sort AFTER INSERT ON tasks
WHEN new.sort_order = 0 BEGIN
    UPDATE tasks SET sort_order = (
        SELECT COALESCE(MAX(sort_order), 0) + 1
        FROM tasks WHERE note_id = new.note_id AND id != new.id
    ) WHERE id = new.id;
END;
```

---

## Managing Triggers

```sql
SELECT name, tbl_name FROM sqlite_master WHERE type = 'trigger';
SELECT sql FROM sqlite_master WHERE type = 'trigger' AND name = 'notes_update_timestamp';
DROP TRIGGER IF EXISTS notes_update_timestamp;
```

> No `DISABLE TRIGGER` in SQLite. To skip triggers temporarily, drop and recreate them.

---

## Common Mistakes

| Mistake | Why It Happens | Fix |
|---------|---------------|-----|
| Trigger infinite recursion | UPDATE trigger fires itself | Add WHEN clause |
| View is slow | Complex JOINs every query | Index joined columns |
| Forgetting views are read-only | Tries INSERT into view | Views are SELECT-only |
| Too many triggers | "Automate everything!" | Triggers hide logic; keep minimal |
| Audit table grows forever | No cleanup | Periodic DELETE of old rows |

---

## Exercise

1. Create `notes_dashboard` view and query with filters
2. Create the timestamp trigger — update a note and verify
3. Create audit table + triggers — insert, update, delete, then query the log
4. Create a validation trigger preventing empty task descriptions
5. Create a `weekly_summary` view: notes this week, tasks done this week
6. Drop and recreate a trigger with a modification

---

## Quick Reference

| Command | What It Does |
|---------|-------------|
| `CREATE VIEW name AS SELECT ...` | Named query |
| `DROP VIEW IF EXISTS name` | Remove view |
| `CREATE TRIGGER name AFTER INSERT ON t` | Auto-action |
| `DROP TRIGGER IF EXISTS name` | Remove trigger |
| `new.column` / `old.column` | New/old values |
| `WHEN condition` | Conditional trigger |
| `RAISE(ABORT, 'msg')` | Abort with error |
| `AFTER UPDATE OF col` | Column-specific |

---

[← Ch 8](chapter-08-json.md) | [Ch 10: Migrations →](chapter-10-migrations.md)

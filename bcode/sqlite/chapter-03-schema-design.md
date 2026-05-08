# Chapter 3: Schema Design

[← Ch 2](chapter-02-queries.md) | [Ch 4 →](chapter-04-joins-relations.md)

---

## Lena's Request

> "Jotter needs folders, tags, tasks, and maybe attachments later. Design a schema that's fast, correct, and won't fall apart when we add features."

---

## The Full Jotter Schema

```sql
PRAGMA foreign_keys = ON;  -- OFF by default in SQLite!

CREATE TABLE folders (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    parent_id INTEGER REFERENCES folders(id),
    icon TEXT DEFAULT '📁'
);

CREATE TABLE notes (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    folder_id INTEGER REFERENCES folders(id),
    is_pinned INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    metadata TEXT  -- JSON blob for flexible fields
);

CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    color TEXT DEFAULT '#888888'
);

CREATE TABLE note_tags (
    note_id INTEGER REFERENCES notes(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (note_id, tag_id)
);

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    note_id INTEGER REFERENCES notes(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    is_done INTEGER DEFAULT 0,
    due_date TEXT,
    priority INTEGER DEFAULT 0,
    sort_order INTEGER DEFAULT 0
);
```

---

## Foreign Keys: The Most Important PRAGMA

```sql
PRAGMA foreign_keys = ON;  -- Must set on EVERY connection
```

Without this, you can insert `folder_id = 999` even if no such folder exists. SQLite disables FK enforcement by default for backward compatibility.

---

## Constraints

```sql
title TEXT NOT NULL                              -- Required field
name TEXT UNIQUE NOT NULL                        -- No duplicates (auto-creates index)
is_done INTEGER DEFAULT 0 CHECK (is_done IN (0, 1))  -- Validation
created_at TEXT DEFAULT (datetime('now'))        -- Expression default (needs parens!)
```

### ON DELETE Options

| Action | Behavior |
|--------|----------|
| `CASCADE` | Delete children too |
| `SET NULL` | Set FK to NULL |
| `RESTRICT` | Block deletion if children exist |
| `NO ACTION` | Same as RESTRICT (default) |

---

## Self-Referencing Folders (Tree Structure)

```sql
INSERT INTO folders (id, name, parent_id) VALUES
    (1, 'Work', NULL), (2, 'Personal', NULL),
    (3, 'Projects', 1), (4, 'Meetings', 1), (5, 'Recipes', 2);
```

```
📁 Work (parent_id=NULL)
├── 📁 Projects (parent_id=1)
└── 📁 Meetings (parent_id=1)
📁 Personal (parent_id=NULL)
└── 📁 Recipes (parent_id=2)
```

---

## Junction Table: Many-to-Many

The `note_tags` table connects notes and tags. The composite primary key `(note_id, tag_id)` prevents duplicates and provides fast lookups:

```sql
INSERT INTO note_tags (note_id, tag_id) VALUES (1, 3);  -- Tag a note
DELETE FROM note_tags WHERE note_id = 1 AND tag_id = 3; -- Untag
```

---

## Indexes

```sql
CREATE INDEX idx_notes_folder ON notes(folder_id);
CREATE INDEX idx_notes_created ON notes(created_at DESC);
CREATE INDEX idx_tasks_note ON tasks(note_id);
CREATE INDEX idx_tasks_done ON tasks(is_done);
CREATE INDEX idx_note_tags_tag ON note_tags(tag_id);
```

> **SQLite-specific:** The primary key IS the table's B-tree. Additional indexes are separate B-trees pointing to rowid. Unlike MySQL, SQLite does NOT auto-index foreign key columns.

---

## Normalization vs. Denormalization

For embedded databases, the tradeoffs shift from server databases:

| Approach | Pros | Cons |
|----------|------|------|
| Normalized | No duplication, easy updates | More JOINs |
| Denormalized | Faster reads, simpler queries | Duplication, harder updates |

Jotter uses **mostly normalized** with one strategic denormalization: the `metadata` JSON column for rarely-used optional fields (word count, source URL, custom colors) instead of a separate table per field.

---

## Why Not AUTOINCREMENT?

`INTEGER PRIMARY KEY` reuses deleted IDs. `AUTOINCREMENT` guarantees always-increasing IDs but requires an extra internal table and is slightly slower. You rarely need it.

---

## Common Mistakes

| Mistake | Why It Happens | Fix |
|---------|---------------|-----|
| Forgetting `PRAGMA foreign_keys = ON` | Off by default | Set on every connection |
| No index on FK columns | Assumes auto-indexing | SQLite doesn't — add manually |
| Using AUTOINCREMENT | Thinks it's required | INTEGER PRIMARY KEY is sufficient |
| Storing booleans as TEXT | 'true'/'false' strings | Use INTEGER 0/1 |
| No ON DELETE clause | Orphaned rows | Use CASCADE or RESTRICT explicitly |

---

## Exercise

1. Create the full Jotter schema in a new database
2. Add CHECK constraints: `priority BETWEEN 0 AND 3`, `is_done IN (0, 1)`
3. Try inserting a note with non-existent `folder_id` — confirm FK error
4. Try inserting a duplicate tag name — confirm UNIQUE error
5. Delete a note with tasks — confirm CASCADE deletes tasks
6. Design an `attachments` table: id, note_id (FK), filename, mime_type, size_bytes, created_at

---

## Quick Reference

| Concept | Syntax |
|---------|--------|
| Enable FKs | `PRAGMA foreign_keys = ON;` |
| Foreign key | `col INTEGER REFERENCES other(id)` |
| Cascade delete | `ON DELETE CASCADE` |
| Unique | `col TEXT UNIQUE` |
| Check | `CHECK (col BETWEEN 0 AND 3)` |
| Default expr | `DEFAULT (datetime('now'))` |
| Composite PK | `PRIMARY KEY (col1, col2)` |
| Create index | `CREATE INDEX name ON table(col)` |

---

[← Ch 2](chapter-02-queries.md) | [Ch 4: Joins & Relations →](chapter-04-joins-relations.md)

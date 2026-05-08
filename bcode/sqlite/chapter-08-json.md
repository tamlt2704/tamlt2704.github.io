# Chapter 8: JSON Support

[← Ch 7](chapter-07-fts.md) | [Ch 9 →](chapter-09-triggers-views.md)

---

## Lena's Request

> "Some notes have extra metadata — word count, reading time, source URL, custom color. I don't want a column for every possible field. Can I store flexible data as JSON and still query it?"

---

## The metadata Column

Our notes table has `metadata TEXT` — a regular TEXT column. SQLite's JSON functions treat it as structured data:

```sql
UPDATE notes SET metadata = json('{
    "word_count": 342,
    "reading_time_min": 2,
    "source_url": "https://example.com/article",
    "color": "#FF6B6B"
}') WHERE id = 1;

-- json() validates and minifies. Invalid JSON raises an error.
SELECT json('not json');  -- Error: malformed JSON
```

> **SQLite-specific:** JSON1 is built into SQLite since 3.9.0 (2015). Test with `SELECT json('{}');`.

---

## Extracting Values

```sql
SELECT json_extract(metadata, '$.word_count') FROM notes WHERE id = 1;  -- 342
SELECT json_extract(metadata, '$.color') FROM notes WHERE id = 1;       -- #FF6B6B

-- Use in WHERE
SELECT title FROM notes WHERE json_extract(metadata, '$.word_count') > 200;

-- The ->> operator (SQLite 3.38+): extracts as SQL value
SELECT metadata->>'$.word_count' FROM notes WHERE id = 1;
```

| Path | Meaning |
|------|---------|
| `$` | Root |
| `$.key` | Property |
| `$.a.b` | Nested |
| `$[0]` | Array element |

---

## Modifying JSON

```sql
-- Add or update
UPDATE notes SET metadata = json_set(metadata, '$.word_count', 500) WHERE id = 1;

-- Add new field
UPDATE notes SET metadata = json_set(metadata, '$.exported_at', datetime('now')) WHERE id = 1;

-- Replace only if exists
UPDATE notes SET metadata = json_replace(metadata, '$.word_count', 600) WHERE id = 1;

-- Remove a field
UPDATE notes SET metadata = json_remove(metadata, '$.source_url') WHERE id = 1;

-- Multiple fields at once
UPDATE notes SET metadata = json_set(metadata, '$.word_count', 750, '$.reading_time_min', 4) WHERE id = 1;
```

| Function | Behavior |
|----------|----------|
| `json_set()` | Create or replace |
| `json_replace()` | Replace only (no-op if missing) |
| `json_insert()` | Create only (no-op if exists) |
| `json_remove()` | Delete path |

---

## Arrays and json_each()

```sql
-- Store an array
UPDATE notes SET metadata = json_set(metadata, '$.labels', json_array('draft', 'review', 'final')) WHERE id = 1;

-- Expand array into rows
SELECT value FROM notes, json_each(notes.metadata, '$.labels') WHERE notes.id = 1;
-- draft / review / final

-- Array length
SELECT json_array_length(metadata, '$.labels') FROM notes WHERE id = 1;  -- 3
```

---

## Aggregating as JSON

```sql
-- Build JSON array from query results
SELECT json_group_array(title) FROM notes WHERE is_pinned = 1;
-- ["Q1 Roadmap","Habit Tracker Idea"]

-- Note with tasks as nested JSON (for app data layer)
SELECT n.title, json_group_array(json_object(
    'id', t.id, 'description', t.description,
    'is_done', t.is_done, 'priority', t.priority
)) AS tasks_json
FROM notes n LEFT JOIN tasks t ON n.id = t.note_id
WHERE n.id = 1 GROUP BY n.id;
```

---

## Indexing JSON Fields

```sql
-- Expression index on a JSON path
CREATE INDEX idx_notes_word_count ON notes(json_extract(metadata, '$.word_count'));

-- Now this uses the index:
SELECT title FROM notes WHERE json_extract(metadata, '$.word_count') > 500;
```

### Generated Columns (SQLite 3.31+)

```sql
ALTER TABLE notes ADD COLUMN word_count INTEGER
    GENERATED ALWAYS AS (json_extract(metadata, '$.word_count')) VIRTUAL;

CREATE INDEX idx_notes_wc ON notes(word_count);
SELECT title FROM notes WHERE word_count > 500;  -- Uses index
```

> VIRTUAL = computed on read (no storage). STORED = computed on write (takes space).

---

## When JSON vs. Columns

| Use JSON | Use Columns |
|----------|-------------|
| Fields vary per row | Every row has it |
| Schema changes often | Schema is stable |
| Rarely filtered/sorted | Frequently filtered |
| Optional metadata | Core data |

For Jotter: columns for title, content, folder_id, is_pinned (queried constantly). JSON for word_count, source_url, custom colors (varies, queried occasionally).

---

## Validation

```sql
SELECT json_valid('{"ok": true}');  -- 1
SELECT json_valid('broken');         -- 0

-- CHECK constraint
CREATE TABLE settings (
    id INTEGER PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,
    value TEXT CHECK (json_valid(value))
);
```

---

## Common Mistakes

| Mistake | Why It Happens | Fix |
|---------|---------------|-----|
| Storing everything as JSON | "Schema-less is easier" | Columns for core data, JSON for extras |
| Not validating on insert | Trusts app code | Use `json()` or CHECK constraint |
| Querying JSON without index | Assumes it's fast | Expression index on hot paths |
| Using `->` when needing `->>` | Confusion | `->` = JSON type, `->>` = SQL value |
| Deep nesting | Over-structuring | Keep JSON flat |
| Forgetting NULL metadata | `json_extract(NULL, ...)` = NULL | Check for NULL first |

---

## Exercise

1. Add metadata to 5 notes with varying fields
2. Query notes where word_count > 200
3. Use `json_each()` to expand a JSON array
4. Create an expression index on word_count
5. Use `json_group_array()` to return a note with nested tasks
6. Add a CHECK constraint validating metadata is JSON or NULL
7. Use `json_set()` to add a field without overwriting others

---

## Quick Reference

| Function | What It Does |
|----------|-------------|
| `json(text)` | Validate/minify |
| `json_extract(j, path)` | Get value |
| `j->>path` | Extract as SQL value |
| `json_set(j, path, val)` | Set/create |
| `json_replace(j, path, val)` | Update existing |
| `json_remove(j, path)` | Delete field |
| `json_each(j, path)` | Expand to rows |
| `json_group_array(val)` | Aggregate to array |
| `json_object(k, v, ...)` | Create object |
| `json_valid(text)` | Check validity |

---

[← Ch 7](chapter-07-fts.md) | [Ch 9: Triggers & Views →](chapter-09-triggers-views.md)

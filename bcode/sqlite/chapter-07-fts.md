# Chapter 7: Full-Text Search

[← Ch 6](chapter-06-performance.md) | [Ch 8 →](chapter-08-json.md)

---

## Lena's Request

> "Users type in a search box and expect instant results across all notes — titles AND content. LIKE '%keyword%' is too slow and can't rank results. I need real search with ranking and snippets."

---

## Why Not LIKE?

`LIKE '%kubernetes%'` does a full table scan, has no ranking, no word boundaries (`'%the%'` matches "other"), and no snippets. SQLite's answer: **FTS5**.

---

## Creating an FTS5 Virtual Table

```sql
CREATE VIRTUAL TABLE notes_fts USING fts5(
    title,
    content,
    content=notes,
    content_rowid=id
);

-- Populate from existing data
INSERT INTO notes_fts(rowid, title, content)
SELECT id, title, content FROM notes;
```

> Check availability: `PRAGMA compile_options;` — look for `ENABLE_FTS5`.

---

## MATCH Queries

```sql
SELECT title FROM notes_fts WHERE notes_fts MATCH 'kubernetes';
SELECT title FROM notes_fts WHERE title MATCH 'roadmap';
SELECT title FROM notes_fts WHERE notes_fts MATCH 'project plan';       -- AND
SELECT title FROM notes_fts WHERE notes_fts MATCH 'recipe OR cooking';  -- OR
SELECT title FROM notes_fts WHERE notes_fts MATCH '"sprint retro"';     -- Phrase
SELECT title FROM notes_fts WHERE notes_fts MATCH 'kube*';              -- Prefix
SELECT title FROM notes_fts WHERE notes_fts MATCH 'project NOT personal'; -- NOT
```

| Syntax | Meaning |
|--------|---------|
| `word` | Contains word |
| `word1 word2` | Both (AND) |
| `word1 OR word2` | Either |
| `"exact phrase"` | Exact sequence |
| `word*` | Prefix match |
| `NOT word` | Exclude |
| `NEAR(w1 w2, N)` | Within N tokens |
| `col:word` | Specific column |

---

## Ranking with bm25()

```sql
SELECT title, bm25(notes_fts) AS rank
FROM notes_fts WHERE notes_fts MATCH 'project'
ORDER BY rank;  -- Lower = better match

-- Weight title 10x more than content
SELECT title, bm25(notes_fts, 10.0, 1.0) AS rank
FROM notes_fts WHERE notes_fts MATCH 'project'
ORDER BY rank;
```

---

## Snippets and Highlighting

```sql
-- snippet(table, col_index, before, after, ellipsis, max_tokens)
SELECT title, snippet(notes_fts, 1, '<b>', '</b>', '...', 32) AS preview
FROM notes_fts WHERE notes_fts MATCH 'roadmap';

-- highlight all matches
SELECT highlight(notes_fts, 0, '[', ']') AS title
FROM notes_fts WHERE notes_fts MATCH 'sprint';
```

---

## Joining FTS with Main Table

```sql
SELECT n.id, n.title, n.is_pinned, n.updated_at,
    snippet(notes_fts, 1, '**', '**', '...', 40) AS preview,
    bm25(notes_fts, 5.0, 1.0) AS relevance
FROM notes_fts
INNER JOIN notes n ON n.id = notes_fts.rowid
WHERE notes_fts MATCH ?
ORDER BY relevance LIMIT 20;
```

---

## Keeping FTS in Sync

```sql
CREATE TRIGGER notes_ai AFTER INSERT ON notes BEGIN
    INSERT INTO notes_fts(rowid, title, content) VALUES (new.id, new.title, new.content);
END;

CREATE TRIGGER notes_au AFTER UPDATE ON notes BEGIN
    INSERT INTO notes_fts(notes_fts, rowid, title, content)
    VALUES ('delete', old.id, old.title, old.content);
    INSERT INTO notes_fts(rowid, title, content) VALUES (new.id, new.title, new.content);
END;

CREATE TRIGGER notes_ad AFTER DELETE ON notes BEGIN
    INSERT INTO notes_fts(notes_fts, rowid, title, content)
    VALUES ('delete', old.id, old.title, old.content);
END;
```

> **SQLite-specific:** FTS5 deletes use special syntax: `INSERT INTO fts(fts, ...) VALUES ('delete', ...)`.

---

## Tokenizers

```sql
-- Porter stemmer: "running" matches "run"
CREATE VIRTUAL TABLE t USING fts5(col, tokenize='porter unicode61');

-- Trigram: substring matching (fast LIKE alternative)
CREATE VIRTUAL TABLE t USING fts5(col, tokenize='trigram');
```

| Tokenizer | Behavior | Use Case |
|-----------|----------|----------|
| `unicode61` | Unicode splitting + case folding | Default |
| `porter` | English stemming | Better recall |
| `trigram` | 3-char substrings | Substring search |
| `ascii` | ASCII-only | English, faster |

---

## Maintenance

```sql
INSERT INTO notes_fts(notes_fts) VALUES ('rebuild');    -- Rebuild index
INSERT INTO notes_fts(notes_fts) VALUES ('optimize');   -- Merge segments
INSERT INTO notes_fts(notes_fts) VALUES ('integrity-check');
```

---

## Common Mistakes

| Mistake | Why It Happens | Fix |
|---------|---------------|-----|
| Using LIKE for search | Doesn't know FTS5 | Use MATCH |
| Forgetting sync triggers | FTS gets stale | Add INSERT/UPDATE/DELETE triggers |
| Not weighting title higher | Title matches buried | `bm25(fts, 10.0, 1.0)` |
| Storing all columns in FTS | Wastes space | Only index searchable text; JOIN for rest |
| Using `=` instead of MATCH | Wrong operator | FTS5 requires MATCH |
| Empty search string | MATCH errors on empty | Validate in app code |

---

## Exercise

1. Create `notes_fts` with porter stemmer
2. Populate from existing notes
3. Search for "project" with bm25 ranking
4. Use snippet() for highlighted previews
5. Create the three sync triggers
6. Insert a new note and verify it appears in search
7. Try prefix search: "spr*" should match "sprint"

---

## Quick Reference

| Command | What It Does |
|---------|-------------|
| `CREATE VIRTUAL TABLE t USING fts5(cols)` | Create FTS index |
| `WHERE t MATCH 'query'` | Full-text search |
| `bm25(t, weights...)` | Relevance ranking |
| `snippet(t, col, pre, post, ellip, n)` | Context snippet |
| `highlight(t, col, pre, post)` | Highlight matches |
| `INSERT INTO t(t) VALUES ('rebuild')` | Rebuild index |
| `tokenize='porter unicode61'` | English stemming |

---

[← Ch 6](chapter-06-performance.md) | [Ch 8: JSON Support →](chapter-08-json.md)

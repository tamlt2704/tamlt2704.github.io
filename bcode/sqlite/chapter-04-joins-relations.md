# Chapter 4: Joins & Relations

[← Ch 3](chapter-03-schema-design.md) | [Ch 5 →](chapter-05-transactions.md)

---

## Lena's Request

> "I need to show a note with its tags as colored chips, the folder breadcrumb, and a 'notes with open tasks' view. Show me how to pull related data together in one query."

---

## JOIN Types

```sql
-- INNER JOIN: only notes that HAVE a folder
SELECT n.title, f.name AS folder FROM notes n
INNER JOIN folders f ON n.folder_id = f.id;

-- LEFT JOIN: ALL notes, folder name if available (NULL otherwise)
SELECT n.title, f.name AS folder FROM notes n
LEFT JOIN folders f ON n.folder_id = f.id;
```

> **Lena's pattern:** LEFT JOIN for the notes list — show all notes, display folder when available.

---

## Many-to-Many: Notes ↔ Tags

```sql
-- Tags for a specific note
SELECT t.name, t.color FROM tags t
INNER JOIN note_tags nt ON t.id = nt.tag_id
WHERE nt.note_id = 1;

-- Notes with a specific tag
SELECT n.title FROM notes n
INNER JOIN note_tags nt ON n.id = nt.note_id
INNER JOIN tags t ON nt.tag_id = t.id
WHERE t.name = 'urgent';

-- Each note with comma-separated tags
SELECT n.title, GROUP_CONCAT(t.name, ', ') AS tags
FROM notes n
LEFT JOIN note_tags nt ON n.id = nt.note_id
LEFT JOIN tags t ON nt.tag_id = t.id
GROUP BY n.id;
```

> **SQLite-specific:** `GROUP_CONCAT` is SQLite's equivalent of PostgreSQL's `STRING_AGG`.

---

## One-to-Many: Notes → Tasks

```sql
-- Notes with task progress
SELECT n.title, COUNT(t.id) AS tasks, SUM(t.is_done) AS done
FROM notes n
LEFT JOIN tasks t ON n.id = t.note_id
GROUP BY n.id;

-- Notes with incomplete tasks
SELECT DISTINCT n.title FROM notes n
INNER JOIN tasks t ON n.id = t.note_id
WHERE t.is_done = 0;
```

---

## Self-Joins: Folder Tree

```sql
-- Folders with parent name
SELECT f.name AS folder, p.name AS parent
FROM folders f LEFT JOIN folders p ON f.parent_id = p.id;
```

### Recursive CTE: Full Path

```sql
WITH RECURSIVE folder_path AS (
    SELECT id, name, parent_id, name AS path FROM folders WHERE id = 3
    UNION ALL
    SELECT f.id, f.name, f.parent_id, f.name || ' > ' || fp.path
    FROM folders f INNER JOIN folder_path fp ON f.id = fp.parent_id
)
SELECT path FROM folder_path WHERE parent_id IS NULL;
-- Result: 'Work > Projects'
```

---

## Subqueries and EXISTS

```sql
-- Scalar subquery
SELECT title FROM notes
WHERE folder_id = (SELECT folder_id FROM notes WHERE title = 'Q1 Roadmap');

-- IN subquery
SELECT title FROM notes WHERE id IN (
    SELECT nt.note_id FROM note_tags nt
    INNER JOIN tags t ON nt.tag_id = t.id WHERE t.name = 'urgent'
);

-- EXISTS (stops at first match — efficient)
SELECT n.title FROM notes n
WHERE EXISTS (SELECT 1 FROM tasks t WHERE t.note_id = n.id);

-- NOT EXISTS
SELECT n.title FROM notes n
WHERE NOT EXISTS (SELECT 1 FROM tasks t WHERE t.note_id = n.id);
```

---

## The Complete Notes List View

Lena's main screen in one query:

```sql
SELECT
    n.id, n.title, n.is_pinned, n.created_at,
    f.name AS folder_name,
    GROUP_CONCAT(DISTINCT t.name) AS tags,
    (SELECT COUNT(*) FROM tasks WHERE note_id = n.id) AS task_count,
    (SELECT SUM(is_done) FROM tasks WHERE note_id = n.id) AS tasks_done
FROM notes n
LEFT JOIN folders f ON n.folder_id = f.id
LEFT JOIN note_tags nt ON n.id = nt.note_id
LEFT JOIN tags t ON nt.tag_id = t.id
GROUP BY n.id
ORDER BY n.is_pinned DESC, n.updated_at DESC;
```

No N+1 problem. No multiple round-trips.

---

## Common Mistakes

| Mistake | Why It Happens | Fix |
|---------|---------------|-----|
| INNER JOIN when LEFT needed | Excludes untagged notes | LEFT JOIN for "all, with extras if available" |
| Missing GROUP BY | Wrong results with aggregates | GROUP BY non-aggregated columns |
| N+1 in app code | Fetching tags per note in a loop | JOIN + GROUP_CONCAT in one query |
| Forgetting DISTINCT in GROUP_CONCAT | Duplicates from multiple JOINs | `GROUP_CONCAT(DISTINCT t.name)` |
| Recursive CTE without base case | Infinite loop | Always start with non-recursive SELECT |

---

## Exercise

1. Show each tag with its note count
2. Find notes with MORE than 2 tasks
3. Get the full folder path for every note (recursive CTE)
4. Find tags not used by any note (orphan tags)
5. Write "Today's Tasks": incomplete tasks with note title, sorted by priority DESC
6. Find notes sharing at least one tag with note id=1 (related notes)

---

## Quick Reference

| Pattern | SQL |
|---------|-----|
| Inner join | `FROM a INNER JOIN b ON a.id = b.a_id` |
| Left join | `FROM a LEFT JOIN b ON a.id = b.a_id` |
| Many-to-many | `FROM a JOIN junction ON ... JOIN b ON ...` |
| Self-join | `FROM t child JOIN t parent ON child.parent_id = parent.id` |
| Aggregate strings | `GROUP_CONCAT(col, ', ')` |
| Existence check | `WHERE EXISTS (SELECT 1 FROM ...)` |
| Recursive CTE | `WITH RECURSIVE name AS (base UNION ALL step)` |

---

[← Ch 3](chapter-03-schema-design.md) | [Ch 5: Transactions →](chapter-05-transactions.md)

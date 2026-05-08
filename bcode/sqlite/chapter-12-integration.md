# Chapter 12: Integration

[← Ch 11](chapter-11-backup-integrity.md)

---

## Lena's Request

> "I know the SQL. Now show me how to use it from real code — Python for tooling, Node.js for the desktop app, and mobile frameworks. Connection management, prepared statements, no SQL injection."

---

## Python: sqlite3 (Standard Library)

```python
import sqlite3

conn = sqlite3.connect('jotter.db')
conn.execute("PRAGMA journal_mode = WAL")
conn.execute("PRAGMA synchronous = NORMAL")
conn.execute("PRAGMA foreign_keys = ON")
conn.execute("PRAGMA busy_timeout = 5000")
conn.row_factory = sqlite3.Row  # Dict-like access

# INSERT (parameterized — prevents SQL injection)
def create_note(conn, title, content, folder_id=None):
    cur = conn.execute(
        "INSERT INTO notes (title, content, folder_id) VALUES (?, ?, ?)",
        (title, content, folder_id))
    conn.commit()
    return cur.lastrowid

# SELECT
def get_notes(conn, limit=50):
    return conn.execute("""
        SELECT id, title, is_pinned, updated_at FROM notes
        ORDER BY is_pinned DESC, updated_at DESC LIMIT ?
    """, (limit,)).fetchall()

# Transaction
def create_note_with_tasks(conn, title, content, tasks):
    try:
        cur = conn.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
        note_id = cur.lastrowid
        conn.executemany(
            "INSERT INTO tasks (note_id, description, sort_order) VALUES (?, ?, ?)",
            [(note_id, t, i) for i, t in enumerate(tasks)])
        conn.commit()
        return note_id
    except:
        conn.rollback()
        raise
```

---

## Node.js: better-sqlite3

Synchronous API — faster than async for embedded use:

```bash
npm install better-sqlite3
```

```javascript
const Database = require('better-sqlite3');
const db = new Database('jotter.db');

db.pragma('journal_mode = WAL');
db.pragma('synchronous = NORMAL');
db.pragma('foreign_keys = ON');
db.pragma('busy_timeout = 5000');

// Prepared statements (safe + fast)
const insertNote = db.prepare(
    'INSERT INTO notes (title, content, folder_id) VALUES (@title, @content, @folderId)');
const listNotes = db.prepare(
    'SELECT id, title, is_pinned, updated_at FROM notes ORDER BY is_pinned DESC, updated_at DESC LIMIT ?');

insertNote.run({ title: 'New Note', content: 'Hello', folderId: 1 });
const notes = listNotes.all(50);

// Transaction (auto BEGIN/COMMIT, rollback on throw)
const createNoteWithTasks = db.transaction((title, content, tasks) => {
    const { lastInsertRowid: noteId } = insertNote.run({ title, content, folderId: null });
    const insertTask = db.prepare('INSERT INTO tasks (note_id, description, sort_order) VALUES (?, ?, ?)');
    tasks.forEach((t, i) => insertTask.run(noteId, t, i));
    return noteId;
});

const id = createNoteWithTasks('Sprint', 'Goals', ['Write spec', 'Review PRs']);
```

---

## Mobile: Android (Room) / iOS (GRDB)

**Android** — Room provides type-safe SQLite with compile-time query verification:

```kotlin
@Entity(tableName = "notes")
data class Note(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val title: String, val content: String?,
    @ColumnInfo(name = "is_pinned") val isPinned: Boolean = false
)

@Dao
interface NoteDao {
    @Query("SELECT * FROM notes ORDER BY is_pinned DESC, updated_at DESC LIMIT :limit")
    fun getNotes(limit: Int = 50): List<Note>
    @Insert fun insert(note: Note): Long
}
// Room handles WAL, foreign keys, and migrations automatically
```

**iOS** — GRDB.swift provides type-safe records:

```swift
struct Note: Codable, FetchableRecord, PersistableRecord {
    var id: Int64?; var title: String; var content: String?
    static let databaseTableName = "notes"
}
let dbQueue = try DatabaseQueue(path: dbPath)
let notes = try dbQueue.read { db in
    try Note.order(Column("is_pinned").desc).limit(50).fetchAll(db)
}
```

---

## Preventing SQL Injection

```python
# ❌ DANGEROUS
query = f"SELECT * FROM notes WHERE title = '{user_input}'"
# user_input = "'; DROP TABLE notes; --" → disaster

# ✅ SAFE — parameterized
conn.execute("SELECT * FROM notes WHERE title = ?", (user_input,))
```

```javascript
// ❌ DANGEROUS
db.prepare(`SELECT * FROM notes WHERE title = '${input}'`).all();

// ✅ SAFE
db.prepare('SELECT * FROM notes WHERE title = ?').all(input);
```

**Rules:** Always use `?` placeholders. Never concatenate user input. Validate LIKE patterns (escape `%` and `_`).

---

## Connection Management

- **Single-threaded:** One connection for the app lifetime
- **Multi-threaded:** One write connection (serialized with a lock), multiple read connections (WAL allows concurrent reads)
- **Always set PRAGMAs** immediately after opening any connection

---

## Common Mistakes

| Mistake | Why It Happens | Fix |
|---------|---------------|-----|
| String concatenation | Doesn't know parameterization | Always use ? params |
| Connection per query | Server DB habit | Reuse connections |
| Forgetting PRAGMAs | Per-connection settings | Set immediately after connect |
| Async sqlite3 in Node | Thinks async = faster | better-sqlite3 sync is faster for embedded |
| Not closing connections | Memory leak | Context managers or explicit close |
| Ignoring errors | "It'll be fine" | Log, rollback, handle gracefully |

---

## Exercise

1. Write a Python script: create DB, set PRAGMAs, insert 100 notes in a transaction
2. Implement `search_notes()` with FTS5 and parameterized queries
3. Write a Node.js script: create note with tasks in a transaction
4. Demonstrate SQL injection: vulnerable query → exploit → fix
5. Implement a connection wrapper that sets PRAGMAs on every open
6. Benchmark: 10,000 inserts with individual commits vs. one transaction

---

## Quick Reference

| Language | Library | Notes |
|----------|---------|-------|
| Python | `sqlite3` | Standard library |
| Node.js | `better-sqlite3` | Sync, fast |
| Android | Room | ORM, compile-time checks |
| iOS | GRDB.swift | Type-safe |
| Rust | `rusqlite` | Safe bindings |
| Go | `modernc.org/sqlite` | Pure Go |

### Connection Setup (Every Open)

```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA foreign_keys = ON;
PRAGMA busy_timeout = 5000;
PRAGMA cache_size = -20000;
```

---

## Course Complete

You've built Jotter's entire database layer: schema, queries, JOINs, transactions, WAL mode, indexes, FTS5, JSON, triggers, migrations, backups, and integration. SQLite isn't a toy — it's the most deployed database engine on Earth, running on 3 trillion devices. Ship it.

---

[← Ch 11](chapter-11-backup-integrity.md)

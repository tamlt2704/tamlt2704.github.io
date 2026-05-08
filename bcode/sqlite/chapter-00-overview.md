# Chapter 0: What Is SQLite?

[Chapter 1 →](chapter-01-first-database.md)

---

## Lena's Request

> "I need a database for Jotter that works offline, starts instantly, and doesn't require the user to install anything. No server process. No configuration wizard. Just open the app and it works."

That's SQLite's entire pitch.

---

## The Story

You're building **Jotter** — a note-taking and task management app that runs entirely on the user's device. Desktop, tablet, phone. No internet required. No account creation. No cloud dependency.

Lena is the mobile developer. She's built the UI — a clean note editor with folders, tags, and inline task lists. Now she needs a database layer underneath. Her requirements:

1. Works offline (always)
2. Zero setup for the end user
3. Fast reads (notes list must load in <50ms)
4. Handles thousands of notes without slowing down
5. Supports full-text search
6. Single file she can back up or export

Every single one of these points to SQLite.

---

## What SQLite Actually Is

SQLite is an **embedded** database engine. That means:

| Client-Server DB (Postgres, MySQL) | Embedded DB (SQLite) |
|------------------------------------|----------------------|
| Separate server process | Library linked into your app |
| Communicates over TCP/IP or sockets | Direct function calls |
| Requires installation and config | Zero configuration |
| Multiple files, WAL, tablespaces | Single file on disk |
| Managed by a DBA | Managed by your app |
| Multi-user, network-accessible | Single-application |

SQLite is not a stripped-down MySQL. It's a fundamentally different architecture. There's no server. The database engine runs *inside* your application process. Reading a row is a function call, not a network round-trip.

```
┌─────────────────────────────┐
│       Your Application      │
│                             │
│  ┌───────────────────────┐  │
│  │   SQLite Library      │  │
│  │   (linked in-process) │  │
│  └──────────┬────────────┘  │
│             │               │
└─────────────┼───────────────┘
              │
              ▼
     ┌─────────────────┐
     │  jotter.db      │  ← single file
     │  (your data)    │
     └─────────────────┘
```

---

## When to Use SQLite

**Great fit:**

- Mobile apps (iOS, Android) — every phone already has SQLite
- Desktop apps (Electron, Tauri, native)
- IoT and embedded devices
- Application file formats (think `.sketch`, `.pages`)
- Test databases (spin up in-memory, tear down instantly)
- Small-to-medium websites (< 100K requests/day)
- Data analysis and prototyping
- Edge computing and local caches

**Not the right tool:**

- High write concurrency (many writers simultaneously)
- Multi-server deployments (no network access to the DB)
- Very large datasets (>1 TB — though SQLite handles up to 281 TB theoretically)
- Client-server architectures where multiple apps share one DB

The rule of thumb: if your app is the *only* thing talking to the database, SQLite is probably the right choice. If multiple services or servers need concurrent write access, use Postgres.

---

## SQLite vs. The World

| Feature | SQLite | PostgreSQL | MySQL |
|---------|--------|-----------|-------|
| Architecture | Embedded (in-process) | Client-server | Client-server |
| Setup time | 0 seconds | 5-30 minutes | 5-30 minutes |
| Configuration | None needed | postgresql.conf, pg_hba.conf | my.cnf |
| Database file | Single file | Directory of files | Directory of files |
| Concurrent readers | Unlimited (WAL mode) | Unlimited | Unlimited |
| Concurrent writers | 1 at a time | Many | Many |
| Max DB size | 281 TB | Unlimited | Unlimited |
| Typing | Dynamic (flexible) | Static (strict) | Static (strict) |
| Full-text search | FTS5 (built-in) | tsvector/GIN | FULLTEXT index |
| JSON support | JSON1 (built-in) | JSONB (native) | JSON (native) |
| Backup | Copy the file | pg_dump / pg_basebackup | mysqldump |

---

## Quick Verify: Do You Have SQLite?

Open a terminal and type:

```bash
sqlite3 --version
```

You should see something like:

```
3.39.5 2022-10-14 20:58:05
```

If you're on macOS or Linux, it's almost certainly already installed. On Windows, download the precompiled binary from [sqlite.org/download.html](https://sqlite.org/download.html) and add it to your PATH.

Let's create a throwaway database to confirm everything works:

```bash
sqlite3 :memory: "SELECT 'SQLite works!' AS status;"
```

Output:

```
SQLite works!
```

The `:memory:` argument creates a temporary in-memory database that disappears when the command exits. We'll use real files starting in Chapter 1.

---

## SQLite-Specific Angle

Things that surprise developers coming from Postgres/MySQL:

1. **No server to start or stop.** There's no `systemctl start sqlite`. It's a library.
2. **No users or permissions.** Access control is your OS file permissions.
3. **Dynamic typing.** You can store a string in an INTEGER column. SQLite won't stop you (we'll cover type affinity later).
4. **No BOOLEAN or DATETIME types.** You use INTEGER (0/1) and TEXT (ISO 8601 strings).
5. **Foreign keys are OFF by default.** You must run `PRAGMA foreign_keys = ON` every connection.
6. **Single-writer model.** Only one write transaction at a time (but unlimited concurrent readers in WAL mode).

---

## Common Mistakes

| Mistake | Why It Happens | Fix |
|---------|---------------|-----|
| Treating SQLite like a toy | "It's just for prototyping" | It powers every smartphone on Earth |
| Using it for multi-server apps | Wrong architecture | Use Postgres for shared databases |
| Forgetting `PRAGMA foreign_keys = ON` | Off by default for backward compat | Set it on every connection open |
| Not using WAL mode | Default journal mode blocks readers | `PRAGMA journal_mode = WAL;` |
| Storing the DB on a network drive | File locking doesn't work over NFS | Always use local storage |

---

## Exercise

1. Open a terminal and confirm `sqlite3 --version` works
2. Run `sqlite3 :memory: "SELECT sqlite_version();"` — note the version
3. Run `sqlite3 :memory: "PRAGMA compile_options;"` — see what extensions are compiled in (look for `ENABLE_FTS5` and `ENABLE_JSON1`)
4. Create a file-based database: `sqlite3 test.db "SELECT 1;"` — confirm a `test.db` file appears
5. Delete it: `rm test.db` — that's the entire "uninstall" process

---

## Quick Reference

| Command | What It Does |
|---------|-------------|
| `sqlite3 mydb.db` | Open (or create) a database |
| `sqlite3 :memory:` | Create an in-memory database |
| `sqlite3 --version` | Show SQLite version |
| `.quit` or `.exit` | Exit the CLI |
| `.help` | Show all dot-commands |
| `PRAGMA compile_options;` | List compiled features |
| `SELECT sqlite_version();` | Version as SQL query |

---

## What's Next

In Chapter 1, we'll create Jotter's actual database file, define our first table, insert some notes, and learn how SQLite's dynamic typing works (and why it's actually a feature, not a bug).

---

[Chapter 1: Your First Database →](chapter-01-first-database.md)

# SQLite: The Embedded Database

Build a complete offline-first app with the most deployed database engine on Earth.

## The Story

You're building **Jotter** — a personal productivity app (notes + tasks) that runs entirely offline on the user's device. No server. No cloud sync. No network round-trips. Just SQLite embedded in the app.

Your colleague **Lena** is the mobile developer. She needs the database layer to be fast, reliable, and capable of handling complex queries — full-text search across thousands of notes, JSON metadata, concurrent reads while the UI thread stays responsive. She's counting on you to design a schema and query layer that "just works" without a DBA on call.

SQLite isn't "MySQL lite." It's a different tool for a different job. Over 3 *trillion* active SQLite databases exist in the wild. It's in every iPhone, every Android phone, every Mac, every Windows 10 machine, every Firefox and Chrome browser, every Skype, every iTunes, every Dropbox client. It's the most widely deployed database engine — and probably the most deployed *software component* — in history.

This course treats SQLite as what it is: a serious, production-grade embedded database with unique strengths that no client-server database can match.

## Chapters

| # | Chapter | What You Build |
|---|---------|----------------|
| 00 | [Overview](chapter-00-overview.md) | Story setup, what SQLite is, when to use it |
| 01 | [First Database](chapter-01-first-database.md) | Create Jotter's database, first tables and rows |
| 02 | [Queries](chapter-02-queries.md) | Find, filter, and aggregate notes and tasks |
| 03 | [Schema Design](chapter-03-schema-design.md) | Design Jotter's full schema with constraints |
| 04 | [Joins & Relations](chapter-04-joins-relations.md) | Connect notes, tags, tasks, and folders |
| 05 | [Transactions](chapter-05-transactions.md) | ACID guarantees and WAL mode |
| 06 | [Performance](chapter-06-performance.md) | Indexes, EXPLAIN, and avoiding full scans |
| 07 | [Full-Text Search](chapter-07-fts.md) | FTS5 for searching note content |
| 08 | [JSON Support](chapter-08-json.md) | Flexible metadata with JSON1 |
| 09 | [Triggers & Views](chapter-09-triggers-views.md) | Automation and computed data |
| 10 | [Migrations](chapter-10-migrations.md) | Evolving the schema safely |
| 11 | [Backup & Integrity](chapter-11-backup-integrity.md) | Protecting user data |
| 12 | [Integration](chapter-12-integration.md) | Using SQLite from Python, Node.js, and mobile |

## Prerequisites

- The `sqlite3` CLI (comes pre-installed on macOS and most Linux distros; [download for Windows](https://sqlite.org/download.html))
- A terminal
- That's it. No server to install. No configuration. No users to create.

## Why SQLite

- **3+ trillion** active databases worldwide
- **Zero configuration** — no setup, no daemon, no permissions
- **Single file** — your entire database is one file you can copy, email, or back up with `cp`
- **Cross-platform** — same file works on macOS, Linux, Windows, iOS, Android
- **Incredibly reliable** — aviation-grade testing (100% branch coverage, billions of test cases)
- **Fast** — often faster than client-server databases for read-heavy embedded workloads (no network overhead, no IPC)

## The Jotter Schema (Preview)

```sql
-- The core tables we'll build across this course
notes       -- Title, content, folder, timestamps, JSON metadata
tags        -- Named labels with colors
note_tags   -- Many-to-many junction table
tasks       -- Checklist items attached to notes
folders     -- Hierarchical organization (self-referencing)
```

## How to Use This Course

Each chapter follows the same pattern:

1. **Lena's request** — what the app needs next
2. **The concept** — what SQLite provides and how it differs from Postgres/MySQL
3. **Hands-on SQL** — run it yourself in `sqlite3`
4. **Common mistakes** — what trips people up
5. **Exercise** — build something yourself
6. **Quick reference** — copy-paste cheat sheet

Open a terminal, type `sqlite3 jotter.db`, and follow along.

---

*"SQLite is not a replacement for Oracle. It is a replacement for `fopen()`."*
— D. Richard Hipp, creator of SQLite

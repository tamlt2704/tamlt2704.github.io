# Chapter 11: Backup & Integrity

[← Ch 10](chapter-10-migrations.md) | [Ch 12 →](chapter-12-integration.md)

---

## Lena's Request

> "Jotter has no server. If the device dies, notes are gone forever. I need backup that works offline, corruption detection, and guarantees the file stays healthy even if the app crashes mid-write."

---

## Backup Methods

### .backup Command (Best)

```bash
sqlite3 jotter.db ".backup jotter-backup.db"
```

Safe during active use — acquires a shared lock, copies pages atomically.

### VACUUM INTO (SQLite 3.27+)

```sql
VACUUM INTO 'jotter-backup.db';
```

Like .backup but also defragments and compacts. Produces a clean single file even in WAL mode.

### File Copy (Risky)

```bash
# Only safe if NO connections are open
cp jotter.db jotter-backup.db

# WAL mode: MUST copy all three files
cp jotter.db jotter-backup.db
cp jotter.db-wal jotter-backup.db-wal
cp jotter.db-shm jotter-backup.db-shm

# Or checkpoint first, then copy just .db:
sqlite3 jotter.db "PRAGMA wal_checkpoint(TRUNCATE);"
cp jotter.db jotter-backup.db
```

---

## VACUUM: Reclaiming Space

Deleted rows leave free pages. VACUUM rebuilds the entire database:

```sql
VACUUM;  -- Compact in-place (needs 2x disk space temporarily)
```

```sql
-- Auto-vacuum: reclaim on demand
PRAGMA auto_vacuum = INCREMENTAL;  -- Set before creating tables
PRAGMA incremental_vacuum(100);    -- Free up to 100 pages
```

| Mode | When to Use |
|------|-------------|
| `VACUUM` | Periodic maintenance (weekly) |
| `auto_vacuum = FULL` | Small databases |
| `auto_vacuum = INCREMENTAL` | Large databases, controlled timing |

---

## Integrity Checking

```sql
-- Full check (reads every page — slow but thorough)
PRAGMA integrity_check;
-- Returns "ok" or describes corruption

-- Fast check (skips index cross-referencing)
PRAGMA quick_check;

-- Foreign key consistency
PRAGMA foreign_key_check;
-- Returns nothing if valid, or rows describing violations
```

### When to Run

- **Every app open:** `PRAGMA quick_check;` (fast sanity check)
- **Weekly:** `PRAGMA integrity_check;` (full deep check)
- **After migration:** Both integrity_check and foreign_key_check

---

## Corruption Prevention

| Cause | Prevention |
|-------|-----------|
| App crash during write | WAL mode handles automatically |
| Power loss | `PRAGMA synchronous = NORMAL` (or FULL) |
| Network filesystem | **Never** use NFS/SMB — locking is unreliable |
| Multiple processes without locking | WAL mode + busy_timeout |
| Incomplete file copy | Use .backup or VACUUM INTO |
| Disk full | SQLite handles gracefully; monitor space |

### Golden Rules

1. Never put SQLite on a network filesystem
2. Always use WAL mode
3. Never delete `-wal` or `-shm` files while DB is open
4. Use `.backup` for copies, not `cp` on a live database

---

## WAL Checkpointing

WAL accumulates writes. Checkpointing merges them back:

```sql
PRAGMA wal_checkpoint(PASSIVE);   -- Best effort, doesn't block
PRAGMA wal_checkpoint(FULL);      -- Waits for readers
PRAGMA wal_checkpoint(TRUNCATE);  -- Full + deletes WAL file
```

Auto-checkpoint triggers at 1000 pages (~4MB):

```sql
PRAGMA wal_autocheckpoint = 2000;  -- Raise threshold
PRAGMA wal_autocheckpoint = 0;     -- Manual only
```

> **Lena's pattern:** Let auto-checkpoint handle normal use. Run TRUNCATE before backup for a clean single file.

---

## The .dump Command: SQL Export

```bash
sqlite3 jotter.db .dump > jotter-export.sql   # Export
sqlite3 jotter-new.db < jotter-export.sql      # Restore
```

Produces CREATE TABLE + INSERT statements. Useful for version control, migration to other engines, or disaster recovery.

---

## Lena's Backup Strategy

```
On app close:     PRAGMA wal_checkpoint(PASSIVE);
Daily:            VACUUM INTO 'backups/jotter-YYYY-MM-DD.db';
On app open:      PRAGMA quick_check;
Weekly:           PRAGMA integrity_check; delete backups > 30 days
Export feature:   VACUUM INTO user-chosen-path;
```

---

## Common Mistakes

| Mistake | Why It Happens | Fix |
|---------|---------------|-----|
| Copying .db without .wal | Doesn't know about WAL files | Use .backup or checkpoint first |
| VACUUM on every write | "Keep it clean!" | Expensive — run weekly |
| DB on iCloud/Dropbox folder | Wants cloud backup | Sync the VACUUM INTO backup, not live DB |
| Ignoring integrity_check | "Probably fine" | Non-"ok" = corruption — restore from backup |
| Deleting -wal file | Thinks it's temp | Contains uncommitted data — never delete |
| No backup strategy | "Just a local app" | Users lose years of notes without backups |

---

## Exercise

1. Create a database with test data, use `.backup` to copy it
2. Run `PRAGMA integrity_check` on both original and backup
3. Enable WAL, insert data, check for the `-wal` file
4. Run `PRAGMA wal_checkpoint(TRUNCATE)` — verify WAL is gone
5. Use `VACUUM INTO` — compare file sizes with original
6. Export with `.dump`, delete DB, restore from dump
7. Hex-edit a byte in a test database — observe what integrity_check reports

---

## Quick Reference

| Command | What It Does |
|---------|-------------|
| `.backup filename` | Consistent backup |
| `VACUUM INTO 'file'` | Compacted backup |
| `VACUUM` | Rebuild in-place |
| `PRAGMA integrity_check` | Full check |
| `PRAGMA quick_check` | Fast check |
| `PRAGMA foreign_key_check` | FK verification |
| `PRAGMA wal_checkpoint(MODE)` | Merge WAL |
| `.dump` | SQL text export |
| `PRAGMA auto_vacuum = INCREMENTAL` | Auto-reclaim |

---

[← Ch 10](chapter-10-migrations.md) | [Ch 12: Integration →](chapter-12-integration.md)

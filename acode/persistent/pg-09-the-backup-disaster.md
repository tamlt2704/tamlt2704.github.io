# Chapter 9: The Backup Disaster — "Restore From Backup" — "What Backup?"

[← The Partitioning Strategy](pg-08-the-partitioning-strategy.md) | [Next: The Production Checklist →](pg-10-the-production-checklist.md)

---

## The Incident

Wednesday, 2:47 PM. A junior dev on the fraud team is cleaning up stale pending
transactions. They run this:

```sql
DELETE FROM transactions WHERE status = 'PENDING';
```

No date filter. No LIMIT. No transaction wrapper. Just a naked DELETE against the
`txn_pending` partition. 12 million rows — every pending transaction in the system —
gone in 8 seconds.

The payment processor starts rejecting requests. Merchants can't check out. The Slack
channel erupts.

> **Maya:** "What happened to the pending transactions?"

> **You:** "Someone deleted them. All of them."

> **Maya:** "Restore from backup."

Viktor checks. He checks again. He opens every backup directory on every server.

> **Viktor:** "There is no backup."

The silence in the room is deafening. Maya stares at the screen. Priya puts her head
in her hands.

> **Maya:** "What do you mean there is no backup?"

> **Viktor:** "We have replication. The replica faithfully replicated the DELETE. We have
> no `pg_dump`. No `pg_basebackup`. No WAL archive. Replication is not a backup."

The next 14 hours are a nightmare. Viktor reconstructs transactions from payment processor
API logs, application audit tables, and Kafka event streams. Some transactions are
unrecoverable. The finance team spends the next two weeks reconciling.

Viktor, the next morning, exhausted:

> **Viktor:** "This never happens again. We're setting up backups today. Right now."

---

## 1. pg_dump — Logical Backup

> **Viktor:** "The simplest backup tool. It reads the database and writes SQL (or a
> custom binary format) that can recreate it."

```bash
# Full database dump (custom format — compressed, parallel-friendly)
pg_dump -U payflow -d payflow \
  -F custom -f payflow_$(date +%Y%m%d).dump

# Dump a specific table only
pg_dump -U payflow -d payflow \
  -t transactions -F custom -f txn_backup.dump

# Restore from dump
pg_restore -U payflow -d payflow \
  -F custom payflow_20260504.dump
```

> **You:** "Why not just use this for everything?"

> **Viktor:** "Because it's slow. Watch."

| Aspect | pg_dump |
|---|---|
| **Speed** | Slow for large DBs (hours for 100GB+) |
| **Locks** | Takes `AccessShareLock` (reads OK, writes OK) |
| **Point-in-time** | ❌ Snapshot at dump time only |
| **Cross-version** | ✅ Works across PG major versions |
| **Granularity** | ✅ Can dump specific tables/schemas |

> **Viktor:** "For PayFlow's 847 GB database, `pg_dump` takes about 4 hours. That means
> your backup is always 4+ hours stale. If the bad DELETE happens 3 hours after the dump,
> you lose 3 hours of data. We need something better."

---

## 2. pg_basebackup — Physical Backup

> **Viktor:** "Physical backup copies the actual data files — the binary representation
> of the database. Much faster than `pg_dump` because it doesn't have to parse and
> serialize every row."

```bash
# Full binary backup (faster than pg_dump for large DBs)
pg_basebackup -h localhost -U replicator \
  -D /backups/base_$(date +%Y%m%d) \
  -Ft -z -P -X stream
```

> **Viktor:** "`-Ft` outputs a tar file. `-z` compresses it. `-P` shows progress. `-X stream`
> includes WAL generated during the backup so it's self-consistent."

| Aspect | pg_basebackup |
|---|---|
| **Speed** | Fast (copies files directly) |
| **Size** | Full cluster size (can't pick individual tables) |
| **Point-in-time** | ✅ With WAL archiving |
| **Cross-version** | ❌ Same major version only |

> **You:** "So `pg_basebackup` is faster but gives us the whole cluster. `pg_dump` is
> slower but lets us pick specific tables. Which do we use?"

> **Viktor:** "Both. But neither solves the real problem — point-in-time recovery. The
> bad DELETE happened at 2:47 PM. Even if we had a `pg_basebackup` from this morning,
> we'd lose everything from midnight to 2:47 PM. We need WAL archiving."

---

## 3. WAL Archiving — Every Change, Saved

> **Viktor:** "You remember WAL from [Chapter 7](pg-07-the-replication-setup.md) —
> the Write-Ahead Log. Every change to the database is written to WAL first.
> `pg_basebackup` gives you a snapshot. WAL archiving gives you every change since
> that snapshot. Together, you can restore to any point in time."

`postgresql.conf`:

```
archive_mode = on
archive_command = 'cp %p /backups/wal_archive/%f'
```

> **Viktor:** "`archive_mode = on` tells PostgreSQL to archive WAL segments after they're
> full. `archive_command` is the shell command that copies each segment to your archive
> location. In production, you'd use `pgBackRest` or `wal-g` to compress and ship WAL
> to S3. For now, a local copy is fine."

> **Viktor:** "This requires a restart — `archive_mode` can't be changed with a reload."

```bash
pg_ctl restart -D /var/lib/postgresql/data
```

> **You:** "How much space does WAL archiving use?"

> **Viktor:** "Depends on write volume. PayFlow generates about 2 GB of WAL per hour.
> That's 48 GB per day. You keep 7 days of WAL, that's 336 GB. Worth it for the ability
> to restore to any second."

---

## 4. Point-in-Time Recovery (PITR) — The Holy Grail

> **Viktor:** "This is what would have saved us today. PITR lets you restore the database
> to the exact second before the bad DELETE — 2:46:59 PM."

Step 1 — Stop PostgreSQL:

```bash
pg_ctl stop -D /var/lib/postgresql/data
```

Step 2 — Replace data directory with base backup:

```bash
rm -rf /var/lib/postgresql/data/*
tar -xzf /backups/base_20260504.tar.gz \
  -C /var/lib/postgresql/data/
```

Step 3 — Configure recovery target in `postgresql.conf` (PG 12+):

```
restore_command = 'cp /backups/wal_archive/%f %p'
recovery_target_time = '2026-05-04 14:46:59'
recovery_target_action = 'promote'
```

Step 4 — Create recovery signal and start:

```bash
touch /var/lib/postgresql/data/recovery.signal
pg_ctl start -D /var/lib/postgresql/data
```

> **Viktor:** "PostgreSQL starts in recovery mode. It reads the base backup (from this
> morning), then replays every WAL segment from the archive — every INSERT, UPDATE,
> DELETE, every DDL change — up to exactly 14:46:59. One second before the bad DELETE.
> Then it promotes to a normal primary."

> **Viktor:** "The database is now in the exact state it was at 2:46:59 PM. The 12 million
> pending transactions are back. The bad DELETE never happened."

> **You:** "That's... incredible."

> **Viktor:** "That's why we're setting this up today. If we'd had this yesterday, the
> recovery would have taken 30 minutes instead of 14 hours. And we wouldn't have lost
> any data."

---

## 5. The Backup Strategy

Viktor writes on the whiteboard:

```
┌──────────────────────────────────────────────────┐
│  VIKTOR'S BACKUP RULES                           │
│                                                  │
│  Daily:      pg_basebackup (full binary snapshot)│
│  Continuous: WAL archiving (every change)        │
│  Weekly:     pg_dump (logical, cross-version)    │
│  Always:     Test your restores                  │
│                                                  │
│  A backup you haven't tested is not a backup.    │
└──────────────────────────────────────────────────┘
```

> **Viktor:** "Daily `pg_basebackup` gives you a recent starting point. Continuous WAL
> archiving gives you every change since that backup. Together, you can restore to any
> second of any day. Weekly `pg_dump` gives you a logical backup that works across
> PostgreSQL major versions — useful for upgrades."

> **You:** "Why not just WAL archiving without `pg_basebackup`?"

> **Viktor:** "Because WAL replay needs a starting point. You can't replay WAL from
> scratch — you need a base backup to start from. The older the base backup, the more
> WAL you have to replay, and the longer recovery takes. Daily base backups keep recovery
> time under an hour."

---

## 6. Testing Backups

> **Viktor:** "The most important step. A backup you haven't tested is not a backup.
> I've seen companies discover their backups were corrupt during an actual disaster.
> Don't be that company."

```bash
# Restore to a test instance
pg_restore -U payflow -d payflow_test \
  -F custom payflow_20260504.dump

# Verify row counts match production
psql -U payflow -d payflow_test \
  -c "SELECT count(*) FROM transactions;"
```

> **Viktor:** "Run this weekly. Automate it. If the count doesn't match, your backup
> is broken and you need to know now — not during the next incident."

```bash
# For PITR testing: restore to a test server and verify
# the target time is correct
psql -U payflow -d payflow_test \
  -c "SELECT max(created_at) FROM transactions;"
```

> **Viktor:** "The max `created_at` should be just before your recovery target time.
> If it's hours earlier, your WAL archive has gaps."

---

## Verification

Confirm backups are working:

```bash
# Check WAL archiving is active
psql -U payflow -d payflow -c \
  "SELECT last_archived_wal, last_archived_time
   FROM pg_stat_archiver;"
```

```
     last_archived_wal      |     last_archived_time
----------------------------+----------------------------
 00000001000000030000005A   | 2026-05-04 14:50:00+00
```

```bash
# Check base backup exists
ls -lh /backups/base_20260504/
```

```
total 52G
-rw------- 1 postgres postgres 52G May  4 03:00 base.tar.gz
```

> **Viktor:** "WAL is archiving. Base backup exists. If the bad DELETE happens again
> tomorrow, we restore in 30 minutes with zero data loss. That's the difference between
> a 14-hour nightmare and a 30-minute inconvenience."

---

## Key Takeaways

1. **Replication is not a backup** — a bad DELETE replicates to the replica instantly. You need independent backups.
2. **`pg_dump`** is simple and cross-version, but slow for large databases and only gives you a point-in-time snapshot.
3. **`pg_basebackup`** is fast and copies the full cluster, but requires the same PG major version.
4. **WAL archiving** captures every change continuously — the key ingredient for point-in-time recovery.
5. **PITR** combines a base backup + WAL archive to restore to any second. This is the gold standard.
6. **Test your restores weekly** — a backup you haven't tested is not a backup.
7. **Automate everything** — `pg_cron` for `pg_dump`, cron for `pg_basebackup`, `archive_command` for WAL.

---

## What's Next

Backups are in place. Replication is running from [Chapter 7](pg-07-the-replication-setup.md).
Indexes are tuned from [Chapter 2](pg-02-the-index-trap.md). VACUUM is healthy from
[Chapter 4](pg-04-the-vacuum-crisis.md). Partitioning keeps the table manageable from
[Chapter 8](pg-08-the-partitioning-strategy.md). You've survived every incident PayFlow
has thrown at you.

Time for Viktor's final review — the production checklist. Everything you've learned,
distilled into the settings, queries, and architecture that keep a PostgreSQL database
alive at scale.

[Next: The Production Checklist →](pg-10-the-production-checklist.md)

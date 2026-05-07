# Chapter 18: "The Database Crashed at 3 AM"

[← Chapter 17: Schema Migrations](chapter-17-migrations.md) | [Chapter 19: Audit & CDC →](chapter-19-audit-cdc.md)

---

## The Incident

3:17 AM. Your phone buzzes. Silent Sasha's message: "Disk full. DB crashed. Recovering."

You check Slack history. The last backup was 3 days ago. Three days of orders, customer signups, and MRR events — potentially gone.

Sasha recovers the database from WAL files. Nothing is lost. But it takes 4 hours, and Priya is not happy.

"Set up proper backups. And a replica. If the primary dies, we switch to the replica in under a minute."

---

## Backup Strategies

### pg_dump: Logical Backup

Creates a SQL file (or custom format) of your entire database:

```bash
# Plain SQL dump
pg_dump -h localhost -U postgres -d datapulse > backup_2024_09_16.sql

# Custom format (compressed, supports parallel restore)
pg_dump -h localhost -U postgres -d datapulse -Fc -f backup_2024_09_16.dump

# Dump specific tables only
pg_dump -h localhost -U postgres -d datapulse -t customers -t orders > partial.sql

# Dump schema only (no data)
pg_dump -h localhost -U postgres -d datapulse --schema-only > schema.sql
```

### Restore from pg_dump

```bash
# From plain SQL
psql -h localhost -U postgres -d datapulse_restored < backup_2024_09_16.sql

# From custom format (parallel restore with 4 jobs)
pg_restore -h localhost -U postgres -d datapulse_restored -j 4 backup_2024_09_16.dump
```

### pg_dumpall: Everything

```bash
# All databases, roles, tablespaces
pg_dumpall -h localhost -U postgres > full_cluster_backup.sql
```

### Limitations of Logical Backups

| Pros | Cons |
|---|---|
| Portable (restore to different PG version) | Slow for large databases |
| Selective (specific tables) | Point-in-time = when dump ran |
| Human-readable (SQL format) | Locks tables briefly during dump |

For a 200GB database, `pg_dump` takes hours. You need something faster.

---

## Physical Backups: pg_basebackup

Copies the raw data files. Fast. Supports point-in-time recovery.

```bash
# Take a base backup
pg_basebackup -h localhost -U postgres -D /backups/base_2024_09_16 \
  --checkpoint=fast --wal-method=stream -P
```

| Flag | Purpose |
|---|---|
| `-D` | Destination directory |
| `--checkpoint=fast` | Start backup immediately (don't wait for next checkpoint) |
| `--wal-method=stream` | Include WAL files needed for consistency |
| `-P` | Show progress |

---

## WAL: Write-Ahead Log

Every change to the database is first written to the WAL (Write-Ahead Log) before being applied to data files. This is how Postgres guarantees durability.

```
Client → SQL → WAL (disk) → Data files (disk)
                 │
                 └─ If crash happens here, replay WAL on recovery
```

WAL files are the key to point-in-time recovery. If you have:
1. A base backup from Monday
2. All WAL files since Monday

You can restore to any point in time between Monday and now.

### WAL Archiving

```
# postgresql.conf
archive_mode = on
archive_command = 'cp %p /archive/wal/%f'
```

Every completed WAL file is copied to your archive. Combined with a base backup, this gives you continuous backup.

---

## Point-in-Time Recovery (PITR)

"Hank deleted all enterprise customers at 2:47 PM. Restore to 2:46 PM."

```bash
# 1. Stop PostgreSQL
pg_ctl stop -D /var/lib/postgresql/data

# 2. Move current data aside
mv /var/lib/postgresql/data /var/lib/postgresql/data_broken

# 3. Restore base backup
cp -r /backups/base_2024_09_16 /var/lib/postgresql/data

# 4. Create recovery configuration
cat > /var/lib/postgresql/data/recovery.signal << EOF
EOF

cat >> /var/lib/postgresql/data/postgresql.conf << EOF
restore_command = 'cp /archive/wal/%f %p'
recovery_target_time = '2024-09-16 14:46:00'
EOF

# 5. Start PostgreSQL — it replays WAL up to the target time
pg_ctl start -D /var/lib/postgresql/data
```

The database comes up as it was at 2:46 PM. Hank's delete never happened.

---

## Streaming Replication

A replica continuously receives WAL from the primary and applies it. If the primary dies, promote the replica.

### Setup

**On the primary** (`postgresql.conf`):

```
wal_level = replica
max_wal_senders = 5
```

**Create a replication user:**

```sql
CREATE USER replicator WITH REPLICATION PASSWORD 'rep_secure_pass';
```

**On the replica:**

```bash
# Bootstrap from primary
pg_basebackup -h primary-host -U replicator -D /var/lib/postgresql/data \
  --checkpoint=fast --wal-method=stream -P

# Configure as standby
cat > /var/lib/postgresql/data/standby.signal << EOF
EOF

cat >> /var/lib/postgresql/data/postgresql.conf << EOF
primary_conninfo = 'host=primary-host user=replicator password=rep_secure_pass'
EOF

# Start the replica
pg_ctl start -D /var/lib/postgresql/data
```

The replica is now a hot standby — it accepts read queries while continuously applying changes from the primary.

### Failover

If the primary dies:

```bash
# On the replica: promote to primary
pg_ctl promote -D /var/lib/postgresql/data
```

The replica becomes the new primary. Point your application at it. Total downtime: seconds.

### Monitoring Replication Lag

```sql
-- On the primary: check connected replicas
SELECT
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    pg_wal_lsn_diff(sent_lsn, replay_lsn) AS lag_bytes
FROM pg_stat_replication;
```

If `lag_bytes` grows, the replica is falling behind. Investigate network or disk I/O.

---

## Backup Schedule

| Frequency | What | Retention |
|---|---|---|
| Continuous | WAL archiving | 7 days |
| Daily | pg_basebackup | 7 days |
| Weekly | pg_dump (logical) | 30 days |
| Monthly | pg_dump to offsite storage | 1 year |

### Automated with Cron

```bash
# Daily base backup at 1 AM
0 1 * * * pg_basebackup -h localhost -U postgres -D /backups/base_$(date +\%Y\%m\%d) --checkpoint=fast --wal-method=stream

# Weekly logical backup on Sunday
0 3 * * 0 pg_dump -h localhost -U postgres -d datapulse -Fc -f /backups/weekly_$(date +\%Y\%m\%d).dump

# Clean backups older than 7 days
0 4 * * * find /backups/base_* -mtime +7 -exec rm -rf {} \;
```

---

## Testing Backups

A backup you've never tested is not a backup. It's a hope.

```bash
# Restore to a test database monthly
createdb datapulse_test
pg_restore -d datapulse_test /backups/weekly_latest.dump

# Verify data integrity
psql -d datapulse_test -c "SELECT count(*) FROM customers;"
psql -d datapulse_test -c "SELECT count(*) FROM orders;"

# Clean up
dropdb datapulse_test
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Tool                            │ What It Does
────────────────────────────────┼──────────────────────────────────────
pg_dump                         │ Logical backup (SQL/custom format)
pg_restore                      │ Restore from custom format dump
pg_dumpall                      │ Backup all databases + roles
pg_basebackup                   │ Physical backup (file copy)
────────────────────────────────┼──────────────────────────────────────
WAL archiving                   │ Continuous backup of changes
PITR                            │ Restore to any point in time
recovery_target_time            │ "Restore to this exact moment"
────────────────────────────────┼──────────────────────────────────────
Streaming replication           │ Real-time copy to standby
pg_ctl promote                  │ Make replica the new primary
pg_stat_replication             │ Monitor replication lag
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Priya: "Who deleted those customers? When? From which IP? I need a complete audit trail of every change to every table."

Audit logging. Logical replication. Change data capture.

---

[← Chapter 17: Schema Migrations](chapter-17-migrations.md) | [Chapter 19: Audit & CDC →](chapter-19-audit-cdc.md)

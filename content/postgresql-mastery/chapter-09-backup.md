[prev: Security](chapter-08-security.md) | [next: Replication & Clustering](chapter-10-replication.md)

# Chapter 9: Backup & Recovery

## pg_dump / pg_restore

### Plain SQL dump

```bash
# Dump entire database
pg_dump -U postgres myapp > myapp_backup.sql

# Dump specific table
pg_dump -U postgres -t orders myapp > orders_backup.sql

# Dump schema only
pg_dump -U postgres --schema-only myapp > schema.sql

# Dump data only
pg_dump -U postgres --data-only myapp > data.sql
```

### Custom format (compressed, supports parallel restore)

```bash
# Dump in custom format
pg_dump -U postgres -Fc myapp > myapp.dump

# Restore
pg_restore -U postgres -d myapp_new myapp.dump

# Restore specific table
pg_restore -U postgres -d myapp_new -t orders myapp.dump

# Parallel restore (4 jobs)
pg_restore -U postgres -d myapp_new -j 4 myapp.dump

# List contents of dump
pg_restore -l myapp.dump
```

### pg_dumpall (all databases + globals)

```bash
# Dump everything including roles and tablespaces
pg_dumpall -U postgres > full_cluster.sql

# Globals only (roles, tablespaces)
pg_dumpall -U postgres --globals-only > globals.sql
```

## Continuous Archiving (WAL)

WAL (Write-Ahead Log) records every change. Archiving WAL files enables point-in-time recovery.

### Enable WAL archiving

In `postgresql.conf`:

```
wal_level = replica
archive_mode = on
archive_command = 'cp %p /var/lib/postgresql/wal_archive/%f'
```

`%p` = path to WAL file, `%f` = filename.

Restart PostgreSQL after changing these.

Verify:

```sql
SHOW wal_level;
SHOW archive_mode;
SELECT * FROM pg_stat_archiver;
```

## Point-in-Time Recovery (PITR)

PITR lets you restore to any moment in time using a base backup + WAL files.

### Step 1: Take a base backup

```bash
pg_basebackup -U postgres -D /backups/base -Ft -z -P
```

Flags:

- `-Ft` — tar format
- `-z` — compress
- `-P` — show progress

### Step 2: Simulate disaster

```sql
-- Note the time before disaster
SELECT now();  -- 2024-01-15 14:30:00

-- Oops, someone drops a table
DROP TABLE orders;
```

### Step 3: Restore to point in time

```bash
# Stop PostgreSQL
pg_ctl stop -D /var/lib/postgresql/data

# Clear data directory
rm -rf /var/lib/postgresql/data/*

# Extract base backup
tar xzf /backups/base/base.tar.gz -C /var/lib/postgresql/data/

# Create recovery signal
touch /var/lib/postgresql/data/recovery.signal
```

In `postgresql.conf`:

```
restore_command = 'cp /var/lib/postgresql/wal_archive/%f %p'
recovery_target_time = '2024-01-15 14:29:59'
recovery_target_action = 'promote'
```

```bash
# Start PostgreSQL — it replays WAL up to target time
pg_ctl start -D /var/lib/postgresql/data
```

After recovery completes, the `recovery.signal` file is removed automatically.

## pg_basebackup

The standard tool for physical backups:

```bash
# Basic backup
pg_basebackup -U replicator -h localhost -D /backups/base_20240115

# With WAL files included (standalone backup)
pg_basebackup -U replicator -h localhost -D /backups/base \
  --wal-method=stream --checkpoint=fast

# Compressed tar format
pg_basebackup -U replicator -h localhost -D /backups/ \
  -Ft -z -P --wal-method=stream
```

### Automating with cron

```bash
# Daily base backup at 2 AM
0 2 * * * pg_basebackup -U replicator -h localhost -D /backups/base_$(date +\%Y\%m\%d) -Ft -z --wal-method=stream
```

## Logical Replication Slots

Replication slots ensure WAL segments are retained until consumed by a subscriber.

```sql
-- Create a logical replication slot
SELECT pg_create_logical_replication_slot('my_slot', 'pgoutput');

-- Check existing slots
SELECT slot_name, slot_type, active, restart_lsn
FROM pg_replication_slots;

-- Peek at changes (without consuming)
SELECT * FROM pg_logical_slot_peek_changes('my_slot', NULL, NULL);

-- Consume changes
SELECT * FROM pg_logical_slot_get_changes('my_slot', NULL, NULL);

-- Drop a slot (important! uncleaned slots prevent WAL cleanup)
SELECT pg_drop_replication_slot('my_slot');
```

### Publication/Subscription model

On publisher:

```sql
CREATE PUBLICATION my_pub FOR TABLE orders, customers;

-- Or all tables
CREATE PUBLICATION all_tables FOR ALL TABLES;
```

On subscriber:

```sql
CREATE SUBSCRIPTION my_sub
CONNECTION 'host=publisher port=5432 dbname=myapp user=replicator'
PUBLICATION my_pub;
```

## Backup Strategy Summary

| Method                | Use Case                                | RPO       |
| --------------------- | --------------------------------------- | --------- |
| `pg_dump`             | Dev/small DBs, logical backup           | Last dump |
| `pg_basebackup` + WAL | Production, PITR needed                 | Seconds   |
| Logical replication   | Zero-downtime migration, selective sync | Near-zero |

RPO = Recovery Point Objective (how much data you can afford to lose).

## Exercises

1. Take a `pg_dump` in custom format and restore to a new database

2. Enable WAL archiving and verify files appear in the archive directory

3. Perform a `pg_basebackup` and restore it to a separate data directory

4. Set up PITR: insert data, note the time, delete data, recover to before deletion

5. Create a logical replication slot and observe changes with `pg_logical_slot_peek_changes`

6. Set up a publication on one database and subscription on another

# Chapter 17: Storage — TOAST, Compression, and Archiving

[← Chapter 16: Zero-Downtime DDL](chapter-16-zero-downtime-ddl.md) | [Chapter 18: Audit Trails →](chapter-18-audit-trails.md)

---

## The Fire

Saturday morning, 1 hour before the tournament. Ops Olga:

> "Disk is at 80%. We have 400GB free. The game_events table is 2TB. It grows 15GB per day. At this rate, we run out of disk in 26 days. And the tournament will generate 3x normal traffic."

You check:

```sql
SELECT
    relname,
    pg_size_pretty(pg_total_relation_size(relid)) AS total,
    pg_size_pretty(pg_relation_size(relid)) AS table,
    pg_size_pretty(pg_indexes_size(relid)) AS indexes,
    pg_size_pretty(pg_total_relation_size(relid) - pg_relation_size(relid) - pg_indexes_size(relid)) AS toast
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 5;
```

```
    relname    | total  | table  | indexes | toast
---------------+--------+--------+---------+-------
 game_events   | 2.1 TB | 1.4 TB | 580 GB  | 120 GB
 matches       | 12 GB  | 8 GB   | 3.8 GB  | 200 MB
 players       | 1.8 GB | 1.2 GB | 480 MB  | 120 MB
```

The `game_events` table is 2.1TB. The TOAST column (JSONB payloads) is 120GB. Events from 2022 and early 2023 are never queried.

---

## TOAST: How Postgres Stores Large Values

TOAST (The Oversized-Attribute Storage Technique) handles values larger than ~2KB:

```sql
-- Check TOAST storage for a table
SELECT
    a.attname,
    pg_size_pretty(sum(pg_column_size(a.attname::text))) AS col_size
FROM pg_attribute a
WHERE a.attrelid = 'game_events'::regclass
  AND a.attnum > 0
GROUP BY a.attname;
```

### How TOAST Works

```
Row data (main table):
┌──────┬──────────┬───────────┬──────────────┬────────────────────┐
│ id   │ match_id │ player_id │ event_type   │ payload (pointer)  │
└──────┴──────────┴───────────┴──────────────┴────────────────────┘
                                                      │
                                                      ▼
                                              TOAST table:
                                              ┌─────────────────┐
                                              │ compressed JSONB │
                                              │ (chunked)       │
                                              └─────────────────┘
```

Values > 2KB are compressed and/or moved to a separate TOAST table.

### TOAST Strategies

```sql
-- Check current strategy
SELECT attname, attstorage
FROM pg_attribute
WHERE attrelid = 'game_events'::regclass AND attnum > 0;
```

| Strategy | Code | Behavior |
|----------|------|----------|
| PLAIN | p | No TOAST (fixed-size types like INT) |
| EXTENDED | x | Compress first, then move to TOAST (default for JSONB) |
| EXTERNAL | e | Move to TOAST without compression |
| MAIN | m | Try to keep in main table, compress if needed |

```sql
-- Force a column to always compress
ALTER TABLE game_events ALTER COLUMN payload SET STORAGE EXTENDED;

-- Force external storage (faster reads, more disk)
ALTER TABLE game_events ALTER COLUMN payload SET STORAGE EXTERNAL;
```

---

## Column Compression (PG 14+)

PostgreSQL 14 added LZ4 compression (faster than the default pglz):

```sql
-- Check current compression
SELECT attname, attcompression
FROM pg_attribute
WHERE attrelid = 'game_events'::regclass AND attname = 'payload';

-- Set LZ4 compression (faster compress/decompress, slightly larger)
ALTER TABLE game_events ALTER COLUMN payload SET COMPRESSION lz4;

-- Set for new tables
CREATE TABLE game_events_new (
    id BIGSERIAL,
    payload JSONB COMPRESSION lz4
);
```

| Compression | Speed | Ratio | Use Case |
|-------------|-------|-------|----------|
| pglz (default) | Slower | Better | Archival, cold data |
| lz4 | Faster | Slightly worse | Hot data, frequent reads |

---

## Measuring Column Sizes

```sql
-- Size of each column in a sample of rows
SELECT
    pg_column_size(id) AS id_bytes,
    pg_column_size(match_id) AS match_id_bytes,
    pg_column_size(event_type) AS event_type_bytes,
    pg_column_size(payload) AS payload_bytes,
    pg_column_size(created_at) AS created_at_bytes,
    pg_column_size(ROW(id, match_id, player_id, event_type, payload, created_at)) AS row_bytes
FROM game_events
LIMIT 5;
```

```sql
-- Average row size and compression ratio
SELECT
    avg(pg_column_size(payload)) AS avg_payload_bytes,
    avg(octet_length(payload::text)) AS avg_uncompressed_bytes,
    round(avg(pg_column_size(payload))::numeric / avg(octet_length(payload::text)) * 100, 1) AS compression_pct
FROM game_events
TABLESAMPLE SYSTEM(0.01);  -- Sample 0.01% of rows
```

---

## Archiving Old Data

### Strategy 1: Partition Detach + Archive

If the table is already partitioned (Chapter 11):

```sql
-- Detach the old partition (instant, no lock on parent)
ALTER TABLE game_events_partitioned DETACH PARTITION game_events_2022_01;

-- Export to compressed file
COPY game_events_2022_01 TO PROGRAM 'gzip > /archive/game_events_2022_01.csv.gz'
WITH (FORMAT csv, HEADER);

-- Or dump as SQL
pg_dump -t game_events_2022_01 pingpong | gzip > /archive/game_events_2022_01.sql.gz

-- Drop the partition (reclaims disk immediately)
DROP TABLE game_events_2022_01;
```

### Strategy 2: Move to Archive Table

For non-partitioned tables:

```sql
-- Create an archive table (same structure, different storage)
CREATE TABLE game_events_archive (LIKE game_events INCLUDING ALL);

-- Move old data in batches
INSERT INTO game_events_archive
SELECT * FROM game_events
WHERE created_at < '2023-01-01'
LIMIT 1000000;

DELETE FROM game_events
WHERE id IN (
    SELECT id FROM game_events
    WHERE created_at < '2023-01-01'
    LIMIT 1000000
);

-- Repeat until done, then VACUUM
VACUUM game_events;
```

### Strategy 3: Table Inheritance for Archival

```sql
-- Parent table (current data)
-- Child table (archived data, maybe on slower storage)
CREATE TABLE game_events_cold (
    CHECK (created_at < '2023-01-01')
) INHERITS (game_events);

-- Move data
INSERT INTO game_events_cold
SELECT * FROM ONLY game_events  -- ONLY = don't include children
WHERE created_at < '2023-01-01';

DELETE FROM ONLY game_events
WHERE created_at < '2023-01-01';
```

---

## Disk Space Monitoring

```sql
-- Database size
SELECT pg_size_pretty(pg_database_size('pingpong'));

-- Table sizes with bloat estimate
SELECT
    schemaname || '.' || relname AS table_name,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
    pg_size_pretty(pg_relation_size(relid)) AS data_size,
    pg_size_pretty(pg_indexes_size(relid)) AS index_size,
    n_live_tup AS live_rows,
    n_dead_tup AS dead_rows
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 10;

-- Tablespace usage
SELECT
    spcname,
    pg_size_pretty(pg_tablespace_size(spcname)) AS size
FROM pg_tablespace;
```

### Growth Rate

```sql
-- Track daily growth (run this daily via cron)
CREATE TABLE disk_usage_log (
    logged_at TIMESTAMP DEFAULT now(),
    table_name TEXT,
    total_bytes BIGINT
);

INSERT INTO disk_usage_log (table_name, total_bytes)
SELECT relname, pg_total_relation_size(relid)
FROM pg_stat_user_tables;

-- Query growth rate
SELECT
    table_name,
    pg_size_pretty(total_bytes) AS current_size,
    pg_size_pretty(total_bytes - lag(total_bytes) OVER (PARTITION BY table_name ORDER BY logged_at)) AS daily_growth
FROM disk_usage_log
WHERE logged_at > now() - interval '7 days'
ORDER BY table_name, logged_at DESC;
```

---

## The Tournament Storage Plan

```sql
-- 1. Archive events older than 6 months (saves ~1.5TB)
ALTER TABLE game_events_partitioned DETACH PARTITION game_events_2023_01;
ALTER TABLE game_events_partitioned DETACH PARTITION game_events_2023_02;
-- ... (archive and drop each)

-- 2. Enable LZ4 compression for new events
ALTER TABLE game_events_partitioned ALTER COLUMN payload SET COMPRESSION lz4;

-- 3. Set up monitoring alert at 85% disk
-- (See Chapter 19 for alerting)

-- 4. Create next month's partition with compression
CREATE TABLE game_events_2024_04 PARTITION OF game_events_partitioned
    FOR VALUES FROM ('2024-04-01') TO ('2024-05-01');
```

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `pg_total_relation_size(table)` | Total size (table + indexes + TOAST) |
| `pg_relation_size(table)` | Table data only |
| `pg_indexes_size(table)` | All indexes on table |
| `pg_column_size(value)` | Size of a specific value |
| `pg_database_size(db)` | Entire database size |
| `ALTER COLUMN SET COMPRESSION lz4` | Use LZ4 compression (PG 14+) |
| `ALTER COLUMN SET STORAGE EXTENDED` | Compress + TOAST |
| `DETACH PARTITION` | Remove partition (instant) |

| Storage Strategy | Disk | Speed | Use Case |
|-----------------|------|-------|----------|
| Keep in main table | More | Faster reads | Hot, frequently accessed |
| TOAST (EXTENDED) | Less | Slightly slower | Large JSONB, TEXT |
| LZ4 compression | Less | Fast decompress | Hot data with large values |
| pglz compression | Least | Slower decompress | Cold/archival data |
| Archive + drop | Reclaimed | N/A | Data older than retention period |

---

## Exercises

### Exercise 1: Storage Audit

Write a query that shows:
- Each table's total size, data size, index size, and TOAST size
- The percentage of total database size each table represents
- Sort by total size descending

### Exercise 2: Compression Comparison

1. Create two copies of `game_events` (1000 rows each)
2. One with default pglz compression, one with lz4
3. Compare sizes with `pg_total_relation_size`
4. Benchmark read speed on both

### Exercise 3: Archival Script

Write a complete archival script that:
1. Exports old partitions to CSV (compressed)
2. Verifies the export row count matches
3. Detaches and drops the partition
4. Logs the operation

---

## What Happens Next

Disk is under control. Old data is archived. But during the tournament, CEO Chad asks:

> "A player claims their ELO was wrong after a match. Who changed it? When? What was the old value?"

You have no audit trail. No history. No way to answer. Time to build one.

---

[← Chapter 16: Zero-Downtime DDL](chapter-16-zero-downtime-ddl.md) | [Chapter 18: Audit Trails →](chapter-18-audit-trails.md)

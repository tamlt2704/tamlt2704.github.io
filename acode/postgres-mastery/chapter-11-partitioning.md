# Chapter 11: Partitioning — Taming the 890 Million Row Table

[← Chapter 10: JOINs & ORM](chapter-10-joins-orm.md) | [Chapter 12: Connection Pooling →](chapter-12-connection-pooling.md)

---

## The Fire

Week two. The `game_events` table has 890 million rows. It grows 3 million per day. Every query — even ones that only need yesterday's events — scans the entire table:

```sql
EXPLAIN ANALYZE
SELECT * FROM game_events
WHERE created_at > now() - interval '1 day'
  AND event_type = 'match_end';
```

```
Seq Scan on game_events  (cost=0.00..28941021.00 rows=312000 width=142)
                         (actual time=0.045..142891.334 rows=28412 loops=1)
  Filter: ((created_at > ...) AND (event_type = 'match_end'))
  Rows Removed by Filter: 889971588
```

142 seconds. To find 28,000 rows from today. Because Postgres scans all 890 million rows.

Ops Olga:

> "We can't index our way out of this. The table is too big. Even the indexes are 40GB."

Marta:

> "Partition it. Split the table by time. Queries that ask for 'today' only scan today's partition."

---

## Range Partitioning (By Date)

### Step 1: Create the Partitioned Table

```sql
-- Create the new partitioned table structure
CREATE TABLE game_events_partitioned (
    id BIGSERIAL,
    match_id BIGINT REFERENCES matches(id),
    player_id BIGINT REFERENCES players(id),
    event_type VARCHAR(50),
    payload JSONB,
    created_at TIMESTAMP DEFAULT now(),
    PRIMARY KEY (id, created_at)  -- Partition key must be in PK
) PARTITION BY RANGE (created_at);
```

### Step 2: Create Partitions

```sql
-- Monthly partitions
CREATE TABLE game_events_2024_01 PARTITION OF game_events_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE game_events_2024_02 PARTITION OF game_events_partitioned
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

CREATE TABLE game_events_2024_03 PARTITION OF game_events_partitioned
    FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');

-- Create a default partition for anything that doesn't match
CREATE TABLE game_events_default PARTITION OF game_events_partitioned
    DEFAULT;
```

### Step 3: Migrate Data

```sql
-- Migrate in batches (don't lock the table for hours)
INSERT INTO game_events_partitioned
SELECT * FROM game_events
WHERE created_at >= '2024-01-01' AND created_at < '2024-02-01';

-- Repeat for each month...
```

### Step 4: Verify Partition Pruning

```sql
EXPLAIN ANALYZE
SELECT * FROM game_events_partitioned
WHERE created_at > now() - interval '1 day'
  AND event_type = 'match_end';
```

```
Append  (actual time=0.028..89.445 rows=28412)
  -> Index Scan using game_events_2024_03_created_at_idx on game_events_2024_03
        (actual time=0.026..89.112 rows=28412)
        Index Cond: (created_at > ...)
        Filter: (event_type = 'match_end')
```

Only the current month's partition is scanned. From 142 seconds to 89ms.

---

## Partition Pruning

The planner eliminates partitions that can't contain matching rows:

```sql
-- This only scans January's partition
SELECT COUNT(*) FROM game_events_partitioned
WHERE created_at BETWEEN '2024-01-15' AND '2024-01-20';

-- Verify with EXPLAIN
EXPLAIN SELECT COUNT(*) FROM game_events_partitioned
WHERE created_at BETWEEN '2024-01-15' AND '2024-01-20';
```

```
Aggregate
  -> Seq Scan on game_events_2024_01 game_events_partitioned
        Filter: (created_at >= '2024-01-15' AND created_at <= '2024-01-20')
```

Only `game_events_2024_01` is scanned. All other partitions are pruned.

**Important**: Partition pruning only works if the WHERE clause uses the partition key directly. Functions on the partition key break pruning:

```sql
-- ❌ BAD: function on partition key prevents pruning
WHERE EXTRACT(MONTH FROM created_at) = 1

-- ✅ GOOD: direct comparison enables pruning
WHERE created_at >= '2024-01-01' AND created_at < '2024-02-01'
```

---

## List Partitioning

For the `matches` table, partition by game mode:

```sql
CREATE TABLE matches_by_mode (
    id BIGSERIAL,
    player1_id BIGINT,
    player2_id BIGINT,
    winner_id BIGINT,
    status VARCHAR(20),
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    game_mode VARCHAR(30),
    PRIMARY KEY (id, game_mode)
) PARTITION BY LIST (game_mode);

CREATE TABLE matches_ranked PARTITION OF matches_by_mode
    FOR VALUES IN ('ranked');

CREATE TABLE matches_casual PARTITION OF matches_by_mode
    FOR VALUES IN ('casual');

CREATE TABLE matches_tournament PARTITION OF matches_by_mode
    FOR VALUES IN ('tournament');

CREATE TABLE matches_other PARTITION OF matches_by_mode
    DEFAULT;
```

---

## Hash Partitioning

When there's no natural range or list, distribute evenly:

```sql
-- Partition players by hash of ID (for parallel processing)
CREATE TABLE players_hash (
    id BIGSERIAL,
    username VARCHAR(50),
    email VARCHAR(255),
    elo_rating INTEGER,
    created_at TIMESTAMP,
    profile JSONB,
    PRIMARY KEY (id)
) PARTITION BY HASH (id);

CREATE TABLE players_hash_0 PARTITION OF players_hash
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE players_hash_1 PARTITION OF players_hash
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE players_hash_2 PARTITION OF players_hash
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE players_hash_3 PARTITION OF players_hash
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

Hash partitioning is useful for parallel scans but doesn't support pruning on range queries.

---

## Partition Maintenance

### Automating Partition Creation

```sql
-- Create next month's partition automatically
CREATE OR REPLACE FUNCTION create_monthly_partition()
RETURNS void AS $$
DECLARE
    next_month DATE := date_trunc('month', now() + interval '1 month');
    partition_name TEXT;
    start_date TEXT;
    end_date TEXT;
BEGIN
    partition_name := 'game_events_' || to_char(next_month, 'YYYY_MM');
    start_date := to_char(next_month, 'YYYY-MM-DD');
    end_date := to_char(next_month + interval '1 month', 'YYYY-MM-DD');

    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF game_events_partitioned
         FOR VALUES FROM (%L) TO (%L)',
        partition_name, start_date, end_date
    );
END;
$$ LANGUAGE plpgsql;

-- Run monthly via pg_cron or cron job
SELECT create_monthly_partition();
```

### Dropping Old Partitions (Archival)

```sql
-- Detach old partition (instant, no lock on parent)
ALTER TABLE game_events_partitioned
    DETACH PARTITION game_events_2023_01;

-- Archive it (dump to S3, etc.)
-- Then drop it
DROP TABLE game_events_2023_01;
```

Detaching is instant. No need to DELETE 100 million rows (which would create dead tuples and bloat).

### Indexes on Partitions

```sql
-- Create index on the parent — automatically applies to all partitions
CREATE INDEX idx_game_events_part_match_id
ON game_events_partitioned (match_id);

CREATE INDEX idx_game_events_part_event_type
ON game_events_partitioned (event_type, created_at);
```

---

## Quick Reference

| Partition Type | Syntax | Use Case |
|---------------|--------|----------|
| Range | `PARTITION BY RANGE (col)` | Time-series data (dates) |
| List | `PARTITION BY LIST (col)` | Categorical data (status, mode) |
| Hash | `PARTITION BY HASH (col)` | Even distribution, parallel scans |

| Operation | Command |
|-----------|---------|
| Create partition | `CREATE TABLE p PARTITION OF parent FOR VALUES ...` |
| Detach partition | `ALTER TABLE parent DETACH PARTITION p` |
| Attach partition | `ALTER TABLE parent ATTACH PARTITION p FOR VALUES ...` |
| Default partition | `CREATE TABLE p PARTITION OF parent DEFAULT` |

| Gotcha | Solution |
|--------|----------|
| PK must include partition key | Add partition column to PRIMARY KEY |
| Functions break pruning | Use direct comparisons on partition key |
| No cross-partition unique constraints | Use application-level uniqueness |
| Foreign keys to partitioned tables | Supported since PG 12 |

---

## Exercises

### Exercise 1: Monthly Partitions

Create a partitioned version of `game_events` with monthly partitions for the last 6 months. Verify partition pruning works with EXPLAIN.

### Exercise 2: Partition Size Monitoring

Write a query that shows the size of each partition:

```sql
-- Hint: use pg_inherits and pg_relation_size
SELECT ...
```

### Exercise 3: Archival Strategy

Design a partition maintenance strategy:
1. Create partitions 2 months ahead
2. Keep 12 months online
3. Archive and drop partitions older than 12 months

Write the SQL for each step.

---

## What Happens Next

The table is partitioned. Queries on recent data are fast. Old data can be archived. But the tournament is Saturday — 50,000 concurrent players. Ops Olga runs a load test:

> "We hit max_connections at 200. PgBouncer isn't configured. The app opens a new connection per request."

Time to set up connection pooling.

---

[← Chapter 10: JOINs & ORM](chapter-10-joins-orm.md) | [Chapter 12: Connection Pooling →](chapter-12-connection-pooling.md)

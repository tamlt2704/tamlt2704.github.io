# Chapter 14: Replication — Read Replicas for the Leaderboard

[← Chapter 13: Transactions](chapter-13-transactions.md) | [Chapter 15: High Availability →](chapter-15-high-availability.md)

---

## The Fire

Friday morning. The tournament is tomorrow. Ops Olga runs the final load test:

> "The leaderboard endpoint gets 10,000 requests per second during peak. The primary database CPU hits 100%. Writes start queuing. Matchmaking breaks."

The leaderboard is a read-only query. It doesn't need to hit the primary. If you could send reads to a replica...

Marta:

> "Set up streaming replication. The replica gets a copy of every write within milliseconds. Route leaderboard queries there. The primary handles writes only."

---

## Streaming Replication

The primary streams its WAL (Write-Ahead Log) to replicas in real-time:

```
Primary (writes) ──WAL stream──→ Replica 1 (reads)
                 ──WAL stream──→ Replica 2 (reads)
```

### Step 1: Configure the Primary

```sql
-- postgresql.conf on primary
ALTER SYSTEM SET wal_level = 'replica';
ALTER SYSTEM SET max_wal_senders = 5;        -- Max replication connections
ALTER SYSTEM SET wal_keep_size = '1GB';      -- Keep WAL for slow replicas
ALTER SYSTEM SET hot_standby = on;           -- Allow queries on replicas
-- Restart required
```

```sql
-- Create a replication user
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'rep_secret';
```

```
-- pg_hba.conf: allow replication connections
host replication replicator 10.0.0.0/24 md5
```

### Step 2: Create the Replica (pg_basebackup)

```bash
# On the replica server: take a base backup from primary
pg_basebackup -h pg-primary -U replicator -D /var/lib/postgresql/data \
    --checkpoint=fast --wal-method=stream -P

# Create standby signal file
touch /var/lib/postgresql/data/standby.signal
```

```ini
# postgresql.conf on replica
primary_conninfo = 'host=pg-primary port=5432 user=replicator password=rep_secret'
hot_standby = on
```

```bash
# Start the replica
pg_ctl start -D /var/lib/postgresql/data
```

### Step 3: Verify Replication

```sql
-- On primary: check connected replicas
SELECT
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    replay_lag
FROM pg_stat_replication;
```

```
 client_addr | state     | sent_lsn    | replay_lsn  | replay_lag
-------------+-----------+-------------+-------------+------------
 10.0.0.12   | streaming | 0/5A000060  | 0/5A000060  | 00:00:00.002
```

`replay_lag` of 2ms means the replica is 2ms behind the primary. Good enough for leaderboards.

---

## Read Routing

### Application-Level Routing

```python
# Route reads to replica, writes to primary
import psycopg2

primary = psycopg2.connect("host=pg-primary dbname=pingpong")
replica = psycopg2.connect("host=pg-replica dbname=pingpong")

def get_leaderboard():
    """Read-only: use replica"""
    with replica.cursor() as cur:
        cur.execute("""
            SELECT username, elo_rating
            FROM players ORDER BY elo_rating DESC LIMIT 100
        """)
        return cur.fetchall()

def resolve_match(match_id, winner_id):
    """Write: use primary"""
    with primary.cursor() as cur:
        cur.execute("SELECT resolve_match(%s, %s)", (match_id, winner_id))
        primary.commit()
```

### PgBouncer with Multiple Databases

```ini
; pgbouncer.ini
[databases]
pingpong = host=pg-primary port=5432 dbname=pingpong
pingpong_ro = host=pg-replica port=5432 dbname=pingpong

[pgbouncer]
pool_mode = transaction
default_pool_size = 40
```

App connects to `pingpong` for writes, `pingpong_ro` for reads.

---

## Replication Lag

Replicas are **eventually consistent**. There's always some lag:

```sql
-- On replica: check how far behind we are
SELECT
    now() - pg_last_xact_replay_timestamp() AS replication_lag;
```

```
 replication_lag
-----------------
 00:00:00.003
```

### When Lag Matters

```
Player wins match → writes to primary → reads leaderboard from replica
                                         ↑
                                         Might not see their new rank yet!
```

Solutions:
1. **Read-your-writes**: After a write, read from primary for that user (for a few seconds)
2. **Synchronous replication**: Replica confirms before primary commits (slower writes)
3. **Accept it**: Leaderboard updates in 1-2 seconds. Players won't notice.

### Synchronous Replication (When You Need It)

```sql
-- On primary: wait for replica to confirm
ALTER SYSTEM SET synchronous_standby_names = 'replica1';
SELECT pg_reload_conf();
```

Now every COMMIT waits for the replica to write the WAL. Slower writes, but zero data loss on failover.

---

## Logical Replication

Streaming replication copies everything. Logical replication copies specific tables:

```sql
-- On primary: create a publication
CREATE PUBLICATION leaderboard_pub FOR TABLE players, matches;

-- On replica: create a subscription
CREATE SUBSCRIPTION leaderboard_sub
    CONNECTION 'host=pg-primary dbname=pingpong user=replicator password=rep_secret'
    PUBLICATION leaderboard_pub;
```

### Streaming vs Logical

| Feature | Streaming | Logical |
|---------|-----------|---------|
| Copies | Entire database | Selected tables |
| Replica writable? | No (read-only) | Yes |
| Cross-version? | Same major version | Different versions OK |
| Use case | HA failover, read scaling | Selective sync, upgrades |
| Setup complexity | Lower | Higher |

### Logical Replication Use Cases at PingPong

```sql
-- Replicate only the leaderboard data to an analytics server
CREATE PUBLICATION analytics_pub FOR TABLE players, matches
    WITH (publish = 'insert, update, delete');

-- The analytics server can have its own indexes, materialized views, etc.
```

---

## Monitoring Replication

```sql
-- Primary: replication status
SELECT
    application_name,
    client_addr,
    state,
    pg_wal_lsn_diff(sent_lsn, replay_lsn) AS bytes_behind,
    replay_lag
FROM pg_stat_replication;

-- Replica: am I in recovery mode?
SELECT pg_is_in_recovery();  -- true = replica

-- Replica: replication lag in seconds
SELECT
    CASE WHEN pg_last_wal_receive_lsn() = pg_last_wal_replay_lsn()
        THEN 0
        ELSE EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()))
    END AS lag_seconds;
```

### Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| `replay_lag` | > 5 seconds | > 30 seconds |
| `bytes_behind` | > 100MB | > 1GB |
| Replica disconnected | > 1 minute | > 5 minutes |

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `pg_basebackup` | Create replica from primary |
| `pg_stat_replication` | Monitor replicas from primary |
| `pg_is_in_recovery()` | Check if current server is a replica |
| `pg_last_xact_replay_timestamp()` | Last replayed transaction time |
| `CREATE PUBLICATION` | Define what to replicate (logical) |
| `CREATE SUBSCRIPTION` | Subscribe to a publication (logical) |

| Configuration | Primary | Replica |
|--------------|---------|---------|
| `wal_level` | replica | — |
| `max_wal_senders` | 5+ | — |
| `hot_standby` | on | on |
| `primary_conninfo` | — | connection string to primary |
| `standby.signal` | — | file exists = replica mode |

---

## Exercises

### Exercise 1: Set Up Replication (Docker)

Using Docker Compose, create a primary and replica:

```yaml
# docker-compose.yml
services:
  primary:
    image: postgres:16
    # Configure for replication...
  replica:
    image: postgres:16
    # Configure as standby...
```

Verify data written to primary appears on replica.

### Exercise 2: Measure Replication Lag

1. Write a loop that inserts rows into the primary every 100ms
2. On the replica, query for the latest row
3. Measure the delay between insert and visibility

### Exercise 3: Read Routing Logic

Write application code that:
- Sends all SELECT queries to the replica
- Sends INSERT/UPDATE/DELETE to the primary
- After a write, reads from primary for 5 seconds (read-your-writes)

---

## What Happens Next

You have a replica for reads. But what if the primary dies?

Ops Olga:

> "If the primary crashes during the tournament, we need automatic failover. Manual intervention means 10+ minutes of downtime. That's 50,000 angry players."

Next chapter: high availability and automatic failover.

---

[← Chapter 13: Transactions](chapter-13-transactions.md) | [Chapter 15: High Availability →](chapter-15-high-availability.md)

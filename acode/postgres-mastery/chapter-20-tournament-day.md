# Chapter 20: Tournament Day — The Production Checklist

[← Chapter 19: Monitoring](chapter-19-monitoring.md)

---

## The Fire

Saturday, 11:00 AM. One hour until the tournament. 50,000 players are logging in. CEO Chad is pacing:

> "This is it. $2 million sponsorship deal. Live-streamed. If the database goes down, we're done."

Ops Olga has the monitoring dashboard on three screens. Marta is on standby. Derek's frontend is ready. You've spent the entire week tuning this database.

Time for the final checklist.

---

## Load Testing with pgbench

Before going live, simulate the tournament load:

### Built-in pgbench

```bash
# Initialize pgbench tables (for baseline testing)
pgbench -i -s 100 pingpong

# Run a simple load test: 50 clients, 4 threads, 60 seconds
pgbench -c 50 -j 4 -T 60 pingpong
```

### Custom pgbench Scripts

```sql
-- matchmaking.sql: simulate matchmaking queries
\set player_id random(1, 2300000)
SELECT * FROM matches
WHERE (player1_id = :player_id OR player2_id = :player_id)
  AND status = 'active';
```

```sql
-- leaderboard.sql: simulate leaderboard reads
SELECT username, elo_rating
FROM players
ORDER BY elo_rating DESC
LIMIT 100;
```

```sql
-- resolve_match.sql: simulate match completion
\set match_id random(1, 47000000)
\set winner_id random(1, 2300000)
BEGIN;
SELECT * FROM matches WHERE id = :match_id FOR UPDATE;
UPDATE matches SET winner_id = :winner_id, status = 'completed', ended_at = now()
WHERE id = :match_id AND status = 'active';
COMMIT;
```

```bash
# Run custom scripts with tournament-level load
pgbench -c 200 -j 8 -T 300 -f matchmaking.sql -f leaderboard.sql -f resolve_match.sql pingpong
```

### Interpreting Results

```
transaction type: Custom
scaling factor: 1
query mode: simple
number of clients: 200
number of threads: 8
duration: 300 s
number of transactions actually processed: 1847291
latency average = 32.5 ms
latency stddev = 18.2 ms
tps = 6157.637 (including connections establishing)
tps = 6158.012 (excluding connections establishing)
```

**Target metrics for the tournament:**
- p99 latency < 100ms
- TPS > 5,000
- No errors
- CPU < 70% (headroom for spikes)

---

## The Query Budget

Every endpoint has a time budget:

| Endpoint | Budget | Queries | Target |
|----------|--------|---------|--------|
| Matchmaking | 50ms | 2-3 | < 15ms each |
| Leaderboard | 100ms | 1 | < 50ms |
| Match result | 75ms | 3-4 | < 20ms each |
| Player profile | 50ms | 1-2 | < 25ms each |
| Game events | 30ms | 1 | < 20ms |

```sql
-- Verify all critical queries meet budget
EXPLAIN ANALYZE SELECT * FROM matches
WHERE (player1_id = 42 OR player2_id = 42) AND status = 'active';
-- Must be < 15ms ✓

EXPLAIN ANALYZE SELECT username, elo_rating
FROM players ORDER BY elo_rating DESC LIMIT 100;
-- Must be < 50ms ✓
```

---

## Connection Limits

```sql
-- Verify PgBouncer is handling connections
-- Connect to PgBouncer admin
SHOW POOLS;
```

```
 database | user         | cl_active | cl_waiting | sv_active | sv_idle
----------+--------------+-----------+------------+-----------+---------
 pingpong | pingpong_app |       847 |          0 |        32 |       8
```

**Green flags:**
- `cl_waiting = 0` (no clients queuing)
- `sv_active < default_pool_size` (pool not exhausted)

**Red flags:**
- `cl_waiting > 0` for more than 5 seconds
- `sv_active = default_pool_size` (pool exhausted, increase it)

### Emergency Connection Settings

```sql
-- If connections spike during tournament
-- PgBouncer: increase pool temporarily
-- Edit pgbouncer.ini and RELOAD
-- Or via admin console:
SET default_pool_size = 60;
RELOAD;
```

---

## The Production Checklist

### Before Tournament (T-1 hour)

```sql
-- 1. Fresh statistics
ANALYZE;

-- 2. Check for bloat
SELECT relname, n_dead_tup, n_live_tup,
    round(n_dead_tup::numeric / NULLIF(n_live_tup, 0) * 100, 1) AS dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY dead_pct DESC;

-- 3. VACUUM if needed
VACUUM ANALYZE matches;
VACUUM ANALYZE players;

-- 4. Verify indexes exist and are valid
SELECT indexrelid::regclass, indisvalid
FROM pg_index WHERE NOT indisvalid;

-- 5. Check replication lag
SELECT application_name, replay_lag FROM pg_stat_replication;

-- 6. Verify connection pool
-- (PgBouncer SHOW POOLS)

-- 7. Reset pg_stat_statements for clean monitoring
SELECT pg_stat_statements_reset();

-- 8. Check disk space
SELECT pg_size_pretty(pg_database_size('pingpong'));
-- Ensure > 20% free disk

-- 9. Verify no pending migrations or locks
SELECT * FROM pg_locks WHERE NOT granted;

-- 10. Test failover (if time permits)
-- patronictl switchover --leader pg-node-1 --candidate pg-node-2
-- Then switch back
```

### During Tournament (Monitoring)

```sql
-- Run every 30 seconds
SELECT
    (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') AS active,
    (SELECT count(*) FROM pg_stat_activity WHERE wait_event_type = 'Lock') AS locked,
    (SELECT max(now() - query_start) FROM pg_stat_activity
     WHERE state = 'active' AND pid != pg_backend_pid()) AS longest,
    (SELECT round(mean_exec_time::numeric, 1)
     FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 1) AS slowest_avg_ms;
```

### Emergency Procedures

```sql
-- Kill a runaway query
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'active'
  AND now() - query_start > interval '30 seconds'
  AND query NOT LIKE '%pg_stat%';

-- Kill all idle-in-transaction sessions
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle in transaction'
  AND now() - state_change > interval '5 minutes';

-- Emergency: reduce query timeout
ALTER SYSTEM SET statement_timeout = '10s';
SELECT pg_reload_conf();

-- Emergency: disable a problematic index (force seq scan for testing)
-- UPDATE pg_index SET indisvalid = false WHERE indexrelid = 'idx_name'::regclass;
-- (DANGEROUS — only as last resort)
```

---

## What We Built This Week

```
Monday:    Found the killer query (pg_stat_statements)
           Read query plans (EXPLAIN ANALYZE)
           Added missing indexes
           Fixed stale statistics

Tuesday:   Tuned autovacuum
           Cleaned 40% dead tuples
           Wrote CTEs and window functions

Wednesday: Added JSONB indexes
           Built full-text search
           Fixed N+1 queries

Thursday:  Partitioned game_events (890M rows)
           Set up PgBouncer (50K connections)
           Fixed race conditions (FOR UPDATE)
           Set up streaming replication

Friday:    Configured Patroni (automatic failover)
           Zero-downtime migrations
           Archived old data
           Built audit trail
           Set up monitoring

Saturday:  TOURNAMENT DAY 🏓
```

---

## The Architecture (Final State)

```
                         ┌─────────────────┐
                         │    HAProxy      │
                         │  :5432 (write)  │
                         │  :5433 (read)   │
                         └────────┬────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
        ┌─────┴─────┐      ┌─────┴─────┐      ┌─────┴─────┐
        │ PgBouncer │      │ PgBouncer │      │ PgBouncer │
        │  Primary  │      │ Replica 1 │      │ Replica 2 │
        └─────┬─────┘      └─────┬─────┘      └─────┬─────┘
              │                   │                   │
        ┌─────┴─────┐      ┌─────┴─────┐      ┌─────┴─────┐
        │  Patroni  │      │  Patroni  │      │  Patroni  │
        │  Primary  │─WAL─→│  Replica  │      │  Replica  │
        │  PG 16    │─WAL─→│  PG 16    │      │  PG 16    │
        └───────────┘      └───────────┘      └───────────┘
              │
        ┌─────┴─────┐
        │   etcd    │ (consensus)
        └───────────┘
```

### Database State

| Table | Rows | Partitioned? | Indexes | Autovacuum |
|-------|------|-------------|---------|------------|
| players | 2.3M | No | 5 (incl. GIN, FTS) | scale_factor=0.05 |
| matches | 47M | By game_mode | 6 (incl. partial) | scale_factor=0.02 |
| game_events | 890M | By month (range) | 3 per partition | scale_factor=0.01 |

---

## The Tournament: Results

```
12:00 PM - Tournament starts. 48,291 concurrent players.
12:05 PM - Peak: 8,421 queries/second. p99 latency: 42ms. ✓
12:30 PM - Matchmaking spike: 12,000 match creations/minute. ✓
 1:15 PM - Leaderboard refresh storm: 15,000 reads/second on replica. ✓
 2:00 PM - Replica 2 briefly lags 3 seconds (network blip). Self-recovers. ✓
 3:30 PM - Autovacuum runs on matches table. No impact. ✓
 4:00 PM - Tournament ends. Zero downtime. Zero data loss.

CEO Chad: "The investors are in. Series B confirmed."
Ops Olga: "First Saturday I haven't been paged in 6 months."
Derek: "The leaderboard loaded in 200ms. During peak. I'm impressed."
Marta: "You're not an accidental DBA anymore. You're just a DBA."
```

---

## Quick Reference: The Complete Toolkit

| Category | Tools |
|----------|-------|
| **Find problems** | pg_stat_statements, EXPLAIN ANALYZE, pg_stat_activity |
| **Fix queries** | Indexes (B-tree, GIN, partial), CTEs, window functions |
| **Fix tables** | VACUUM, partitioning, archival |
| **Fix connections** | PgBouncer, pool sizing |
| **Fix correctness** | FOR UPDATE, isolation levels, advisory locks |
| **Fix availability** | Replication, Patroni, HAProxy |
| **Fix operations** | CONCURRENTLY, NOT VALID, lock_timeout |
| **Fix visibility** | Monitoring, alerting, audit trails |

---

## Exercises

### Exercise 1: Full Load Test

Set up a complete load test that simulates:
- 1,000 concurrent matchmaking queries
- 500 concurrent leaderboard reads
- 200 concurrent match resolutions
- Run for 5 minutes

Report: p50, p95, p99 latency, TPS, error rate.

### Exercise 2: Chaos Engineering

With your HA cluster running:
1. Kill the primary during a load test
2. Measure failover time
3. Verify zero data loss
4. Verify the old primary rejoins as replica

### Exercise 3: The Production Runbook

Write a complete runbook document that covers:
1. Pre-deployment checklist (before any release)
2. Monitoring dashboard queries
3. Emergency procedures (high CPU, disk full, deadlocks, replication lag)
4. Scaling procedures (add replica, increase pool, partition new table)

---

## What's Next

You survived the tournament. The database is healthy. But the learning doesn't stop:

- **PostgreSQL 17** brings incremental backup, new JSON functions
- **Citus** for horizontal sharding when you outgrow a single node
- **TimescaleDB** for time-series workloads (game analytics)
- **pg_stat_monitor** for better query insights
- **pgvector** for AI/ML similarity search (player recommendations)

The fires will keep coming. But now you know how to read the smoke.

---

[← Chapter 19: Monitoring](chapter-19-monitoring.md)

# Chapter 19: Monitoring — Seeing Everything Before It Breaks

[← Chapter 18: Audit Trails](chapter-18-audit-trails.md) | [Chapter 20: Tournament Day →](chapter-20-tournament-day.md)

---

## The Fire

Tournament day, 11 AM. Everything seems fine. Then at 11:47 AM, latency spikes. By 11:52 AM, the matchmaking service is timing out. By 11:55 AM, Ops Olga is paged.

> "Why didn't we know 5 minutes earlier? We need alerts BEFORE things break, not after."

You had no monitoring. No dashboards. No alerts. You were flying blind.

Marta:

> "PostgreSQL exposes everything through `pg_stat_*` views. You just need to look."

---

## The Essential pg_stat Views

### pg_stat_activity — What's Running Right Now

```sql
SELECT
    pid,
    usename,
    state,
    wait_event_type,
    wait_event,
    now() - query_start AS duration,
    substring(query, 1, 80) AS query
FROM pg_stat_activity
WHERE state != 'idle'
  AND pid != pg_backend_pid()
ORDER BY query_start;
```

```
  pid  | usename      | state  | wait_event_type | wait_event | duration | query
-------+--------------+--------+-----------------+------------+----------+-------
 12345 | pingpong_app | active | NULL            | NULL       | 00:00:00 | SELECT...
 12346 | pingpong_app | active | Lock            | relation   | 00:02:31 | ALTER...
 12347 | pingpong_app | active | IO              | DataFileRead | 00:00:03 | SELECT...
```

**Red flags:**
- `state = 'active'` with `wait_event_type = 'Lock'` → blocked by another query
- `duration > 30s` → long-running query (might block vacuum)
- `state = 'idle in transaction'` → holding locks without doing anything

### pg_stat_user_tables — Table Health

```sql
SELECT
    relname,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch,
    n_tup_ins,
    n_tup_upd,
    n_tup_del,
    n_live_tup,
    n_dead_tup,
    last_autovacuum,
    last_autoanalyze
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;
```

**Key metrics:**
- `seq_scan` high + `idx_scan` low → missing indexes
- `n_dead_tup / n_live_tup > 0.1` → needs vacuum
- `last_autovacuum` is NULL or old → autovacuum isn't keeping up

### pg_stat_user_indexes — Index Health

```sql
SELECT
    schemaname, relname, indexrelname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC
LIMIT 20;
```

Indexes with `idx_scan = 0` are unused — wasting disk and slowing writes.

---

## Wait Events — Where Time Goes

```sql
-- What are queries waiting on?
SELECT
    wait_event_type,
    wait_event,
    COUNT(*) AS sessions
FROM pg_stat_activity
WHERE state = 'active' AND wait_event IS NOT NULL
GROUP BY wait_event_type, wait_event
ORDER BY sessions DESC;
```

| Wait Type | Common Events | Meaning |
|-----------|--------------|---------|
| **Lock** | relation, transactionid | Waiting for a lock |
| **IO** | DataFileRead, WALWrite | Waiting for disk I/O |
| **LWLock** | BufferMapping, WALInsert | Internal lightweight locks |
| **Client** | ClientRead | Waiting for client to send data |
| **Activity** | AutoVacuumMain | Background worker idle |

---

## Lock Monitoring

```sql
-- Find blocked queries and what's blocking them
SELECT
    blocked.pid AS blocked_pid,
    blocked.query AS blocked_query,
    now() - blocked.query_start AS blocked_duration,
    blocking.pid AS blocking_pid,
    blocking.query AS blocking_query,
    now() - blocking.query_start AS blocking_duration
FROM pg_stat_activity blocked
JOIN pg_locks bl ON bl.pid = blocked.pid AND NOT bl.granted
JOIN pg_locks gl ON gl.locktype = bl.locktype
    AND gl.database IS NOT DISTINCT FROM bl.database
    AND gl.relation IS NOT DISTINCT FROM bl.relation
    AND gl.page IS NOT DISTINCT FROM bl.page
    AND gl.tuple IS NOT DISTINCT FROM bl.tuple
    AND gl.virtualxid IS NOT DISTINCT FROM bl.virtualxid
    AND gl.transactionid IS NOT DISTINCT FROM bl.transactionid
    AND gl.classid IS NOT DISTINCT FROM bl.classid
    AND gl.objid IS NOT DISTINCT FROM bl.objid
    AND gl.objsubid IS NOT DISTINCT FROM bl.objsubid
    AND gl.pid != bl.pid
    AND gl.granted
JOIN pg_stat_activity blocking ON blocking.pid = gl.pid
WHERE blocked.state = 'active';
```

---

## pg_stat_bgwriter — Background Writer Stats

```sql
SELECT
    checkpoints_timed,
    checkpoints_req,
    buffers_checkpoint,
    buffers_clean,
    buffers_backend,
    buffers_alloc
FROM pg_stat_bgwriter;
```

| Metric | Healthy | Problem |
|--------|---------|---------|
| `checkpoints_req` | Low | High = too many forced checkpoints |
| `buffers_backend` | Low | High = backends doing their own writes (slow) |
| `buffers_clean` | Moderate | Low = bgwriter not keeping up |

---

## Cache Hit Ratio

```sql
-- Overall cache hit ratio (should be > 99%)
SELECT
    sum(heap_blks_hit) AS cache_hits,
    sum(heap_blks_read) AS disk_reads,
    round(
        sum(heap_blks_hit)::numeric /
        NULLIF(sum(heap_blks_hit) + sum(heap_blks_read), 0) * 100,
        2
    ) AS hit_ratio_pct
FROM pg_statio_user_tables;
```

```
 cache_hits  | disk_reads | hit_ratio_pct
-------------+------------+---------------
 89421334521 | 412891     | 99.99
```

If hit ratio drops below 95%, you need more `shared_buffers` or your working set doesn't fit in memory.

### Per-Table Cache Hit Ratio

```sql
SELECT
    relname,
    heap_blks_hit,
    heap_blks_read,
    round(
        heap_blks_hit::numeric /
        NULLIF(heap_blks_hit + heap_blks_read, 0) * 100,
        2
    ) AS hit_ratio
FROM pg_statio_user_tables
WHERE heap_blks_hit + heap_blks_read > 0
ORDER BY hit_ratio ASC
LIMIT 10;
```

---

## Replication Lag Monitoring

```sql
-- On primary
SELECT
    application_name,
    client_addr,
    state,
    pg_wal_lsn_diff(sent_lsn, replay_lsn) AS bytes_lag,
    replay_lag
FROM pg_stat_replication;

-- On replica
SELECT
    now() - pg_last_xact_replay_timestamp() AS replication_delay;
```

---

## Building a Monitoring Dashboard

### The PingPong Health Check Query

```sql
-- Single query that returns all critical metrics
SELECT
    (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') AS active_queries,
    (SELECT count(*) FROM pg_stat_activity WHERE state = 'idle in transaction') AS idle_in_txn,
    (SELECT count(*) FROM pg_stat_activity WHERE wait_event_type = 'Lock') AS lock_waiters,
    (SELECT max(now() - query_start) FROM pg_stat_activity WHERE state = 'active' AND pid != pg_backend_pid()) AS longest_query,
    (SELECT round(sum(heap_blks_hit)::numeric / NULLIF(sum(heap_blks_hit + heap_blks_read), 0) * 100, 2) FROM pg_statio_user_tables) AS cache_hit_pct,
    (SELECT sum(n_dead_tup) FROM pg_stat_user_tables) AS total_dead_tuples,
    (SELECT pg_size_pretty(pg_database_size('pingpong'))) AS db_size,
    (SELECT count(*) FROM pg_stat_replication) AS replicas_connected;
```

---

## Alerting Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Active connections | > 80% of max | > 95% of max | Check for connection leaks |
| Cache hit ratio | < 99% | < 95% | Increase shared_buffers |
| Dead tuples (any table) | > 10% of live | > 20% of live | Check autovacuum |
| Replication lag | > 5s | > 30s | Check network/disk on replica |
| Lock waiters | > 5 | > 20 | Find and kill blocking query |
| Longest query | > 60s | > 300s | Kill or optimize |
| Idle in transaction | > 5 min | > 30 min | Kill and fix app code |
| Disk usage | > 80% | > 90% | Archive old data |
| Checkpoints requested | > 50% of total | > 80% | Increase checkpoint_timeout |

### Automated Alerting (Example with pg_cron)

```sql
-- Install pg_cron
CREATE EXTENSION pg_cron;

-- Check every minute for long-running queries
SELECT cron.schedule('kill-long-queries', '* * * * *', $$
    SELECT pg_terminate_backend(pid)
    FROM pg_stat_activity
    WHERE state = 'active'
      AND now() - query_start > interval '5 minutes'
      AND usename != 'postgres'
      AND query NOT LIKE '%pg_stat%';
$$);

-- Alert on high dead tuple count
SELECT cron.schedule('vacuum-alert', '*/5 * * * *', $$
    INSERT INTO alerts (message, severity, created_at)
    SELECT
        format('Table %s has %s%% dead tuples', relname, round(n_dead_tup::numeric / NULLIF(n_live_tup, 0) * 100, 1)),
        'warning',
        now()
    FROM pg_stat_user_tables
    WHERE n_dead_tup::numeric / NULLIF(n_live_tup, 0) > 0.1;
$$);
```

---

## Quick Reference

| View | What It Shows |
|------|--------------|
| `pg_stat_activity` | Current sessions and queries |
| `pg_stat_user_tables` | Table-level stats (scans, tuples, vacuum) |
| `pg_stat_user_indexes` | Index usage stats |
| `pg_statio_user_tables` | Table I/O (cache hits vs disk) |
| `pg_stat_bgwriter` | Background writer/checkpoint stats |
| `pg_stat_replication` | Replication status |
| `pg_locks` | Current locks |
| `pg_stat_progress_vacuum` | Vacuum progress |
| `pg_stat_statements` | Query performance (extension) |

| Key Metric | Healthy Value |
|-----------|---------------|
| Cache hit ratio | > 99% |
| Dead tuple ratio | < 5% |
| Replication lag | < 1s |
| Idle in transaction | 0 |
| Lock waiters | 0 |
| Seq scans on large tables | Decreasing over time |

---

## Exercises

### Exercise 1: Health Dashboard

Create a view called `db_health` that returns all critical metrics in one row. Include: active connections, cache hit ratio, dead tuples, replication lag, and database size.

### Exercise 2: Lock Detective

Write a query that shows the full "lock chain" — if A blocks B and B blocks C, show the entire chain from root blocker to final waiter.

### Exercise 3: Historical Metrics

Create a table that stores hourly snapshots of key metrics. Write a query that shows the trend over the last 24 hours (connections, cache hit ratio, dead tuples). Identify any anomalies.

---

## What Happens Next

Monitoring is live. Alerts are configured. You can see everything. And now it's time — the tournament starts in 1 hour. 50,000 players. The database is tuned, partitioned, replicated, monitored, and ready.

One last chapter: the production checklist, load testing, and the moment of truth.

---

[← Chapter 18: Audit Trails](chapter-18-audit-trails.md) | [Chapter 20: Tournament Day →](chapter-20-tournament-day.md)

# Chapter 10: The Production Checklist — Viktor's Final Review

[← The Backup Disaster](pg-09-the-backup-disaster.md) | [Back to Overview →](pg-00-overview.md)

---

## The Meeting

Friday afternoon. Viktor sends a calendar invite: "Conference Room B — 3:00 PM — Final
Review." No description. No agenda.

You walk in. Viktor is standing at the whiteboard. Maya is sitting in the corner — you
didn't expect the CTO. Priya is there too.

> **Viktor:** "You've survived 9 incidents. The slow query. The index trap. The planner
> mystery. The VACUUM crisis. The connection storm. The lock investigation. The replication
> failure. The partitioning migration. The backup disaster."

He pauses.

> **Viktor:** "Before I trust you with production unsupervised, let's review everything.
> If you can answer my questions, you're ready."

He picks up a marker.

---

## 1. postgresql.conf — The Essential Settings

> **Viktor:** "First question. You're setting up a new production PostgreSQL server.
> 16 GB RAM, SSD storage. What do you configure?"

You write on the whiteboard. Viktor corrects as you go.

```
# Memory
shared_buffers = '4GB'              # 25% of RAM
effective_cache_size = '12GB'       # 75% of RAM
work_mem = '64MB'                   # Per sort/hash operation
maintenance_work_mem = '1GB'        # For VACUUM, CREATE INDEX

# WAL
wal_level = replica
max_wal_senders = 5
max_replication_slots = 5
wal_buffers = '64MB'
checkpoint_completion_target = 0.9

# Query Planner
random_page_cost = 1.1              # SSD (default 4.0 is for HDD)
effective_io_concurrency = 200      # SSD

# Connections
max_connections = 100               # Use PgBouncer, not more connections
idle_in_transaction_session_timeout = '30s'
```

> **Maya:** "Why only 100 connections? We have 200 app servers."

> **Viktor:** *(nods at you)*

> **You:** "Because each connection costs ~10 MB of RAM and a process slot. 200 connections
> means 2 GB just for connection overhead. PgBouncer multiplexes hundreds of app connections
> into 20–30 actual database connections. We covered this in [Chapter 5](pg-05-the-connection-storm.md)."

> **Maya:** *(to Viktor)* "Okay, I'm impressed."

> **Viktor:** "Why `random_page_cost = 1.1` instead of the default 4.0?"

> **You:** "The default assumes spinning disks where random reads are 4x slower than
> sequential reads. On SSDs, random and sequential reads are nearly the same speed. If
> we leave it at 4.0, the planner avoids index scans when it shouldn't — the exact
> problem from [Chapter 3](pg-03-the-query-planner.md)."

---

## 2. Monitoring Queries — Viktor's Dashboard

> **Viktor:** "Good. Now — the database is running. How do you know it's healthy?"

> **Viktor:** "Three queries. Memorize them."

**Slow queries** (requires `pg_stat_statements` extension):

```sql
SELECT query, calls, mean_exec_time AS avg_ms,
       total_exec_time / 1000 AS total_sec
FROM pg_stat_statements
ORDER BY mean_exec_time DESC LIMIT 10;
```

> **Viktor:** "This tells you which queries are slowest on average. The ones at the top
> are your optimization targets. Don't guess — measure."

**Table health** (dead tuples and VACUUM status):

```sql
SELECT relname, n_live_tup, n_dead_tup,
       last_autovacuum, last_autoanalyze
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC LIMIT 10;
```

> **Viktor:** "If `n_dead_tup` is growing and `last_autovacuum` is NULL or days ago,
> you have a VACUUM problem. Go back to [Chapter 4](pg-04-the-vacuum-crisis.md)."

**Cache hit ratio**:

```sql
SELECT sum(heap_blks_hit) /
       (sum(heap_blks_hit) + sum(heap_blks_read)) AS ratio
FROM pg_statio_user_tables;
-- Should be > 0.99. If not, increase shared_buffers.
```

> **Viktor:** "If this number drops below 0.99, PostgreSQL is reading from disk instead
> of the buffer cache. Either your `shared_buffers` is too small or your working set
> is larger than memory. For PayFlow, 0.997 is our target."

> **Priya:** "What about replication lag?"

> **Viktor:** "Good catch."

```sql
-- On the primary
SELECT client_addr, state,
       pg_wal_lsn_diff(sent_lsn, replay_lsn) AS lag_bytes
FROM pg_stat_replication;
```

> **Viktor:** "If `lag_bytes` is climbing, the replica is falling behind. Check disk I/O
> on the replica and network between primary and replica."

---

## 3. The Final Architecture

> **Viktor:** "Let's draw the full picture. Everything we've built over 9 chapters."

```
┌───────────────────────────────────────────────────────┐
│                    Application Layer                   │
│  Spring Boot + JPA + HikariCP (20 connections)         │
└─────────────────────────┬─────────────────────────────┘
                          │
                ┌─────────┴─────────┐
                │     PgBouncer       │
                │  (transaction mode)  │
                └─────────┬─────────┘
                          │
              ┌───────────┼───────────┐
              │                       │
     ┌────────┴────────┐   ┌─────────┴───────┐
     │   PG Primary    │   │   PG Replica     │
     │   (writes)      │──▶│   (reads)        │
     │   Partitioned   │   │   Partitioned    │
     │   Autovacuum on │   │   hot_standby    │
     └────────┬────────┘   └─────────┬───────┘
              │                       │
     ┌────────┴────────┐   ┌─────────┴───────┐
     │  WAL Archiving   │   │  pg_basebackup  │
     │  (continuous)    │   │  (daily)        │
     └─────────────────┘   └─────────────────┘
```

> **Viktor:** "Application connects through PgBouncer — connection pooling from
> [Chapter 5](pg-05-the-connection-storm.md). Writes go to the primary. Reads can go to
> the replica — streaming replication from [Chapter 7](pg-07-the-replication-setup.md).
> Both primary and replica use partitioned tables from [Chapter 8](pg-08-the-partitioning-strategy.md).
> WAL archiving runs continuously. `pg_basebackup` runs daily. PITR is ready if we need
> it — [Chapter 9](pg-09-the-backup-disaster.md)."

> **Maya:** "What's the recovery time if the primary dies?"

> **You:** "Promote the replica — under 5 seconds. Zero data loss with synchronous
> replication. Then set up a new replica from the promoted primary."

> **Maya:** "And if someone runs a bad DELETE again?"

> **You:** "PITR. Restore from the latest base backup, replay WAL to the second before
> the DELETE. 30 minutes, zero data loss."

---

## 4. The Cheat Sheet

Viktor flips the whiteboard. On the back, he's already written this:

| Problem | Wrong Approach | Right Approach |
|---|---|---|
| Slow query | Add random indexes | `EXPLAIN ANALYZE` first, then targeted index |
| Too many indexes | Index every column | Audit with `pg_stat_user_indexes`, drop unused |
| Planner ignores index | `SET enable_seqscan=off` | Fix statistics (`ANALYZE`), fix `random_page_cost` |
| Table bloat | `VACUUM FULL` in production | Tune autovacuum per-table, monitor dead tuples |
| XID wraparound | Ignore warnings | Monitor `age(datfrozenxid)`, `VACUUM FREEZE` |
| Connection exhaustion | `max_connections = 1000` | PgBouncer + connection formula |
| Locks blocking queries | Kill random PIDs | Lock detective query, `lock_timeout`, safe DDL |
| No failover | Single server | Streaming replication + Patroni |
| Huge table | Pray | Partition by range (date) |
| No backups | "It won't happen to us" | `pg_basebackup` daily + WAL archiving + test restores |
| Slow on SSD | Default config | `random_page_cost=1.1`, `effective_io_concurrency=200` |
| Low cache hit ratio | Buy more RAM | Increase `shared_buffers` to 25% of RAM |

> **Viktor:** "Print this. Tape it to your monitor. Every production incident I've seen
> in 20 years falls into one of these categories."

---

## 5. The Graduation

Viktor puts down the marker. He looks at Maya. She nods.

> **Viktor:** "You came in as an intern who didn't know what `EXPLAIN` does. You've
> debugged a 47-second query. You've survived the index trap, the VACUUM crisis, the
> connection storm, the lock investigation. You set up replication, partitioned a
> 2-billion-row table, and built a backup strategy from scratch."

He extends his hand.

> **Viktor:** "You're not an intern anymore. You understand PostgreSQL — not just the
> SQL, but the engine underneath. The planner, the executor, the storage layer, the
> WAL, the vacuum daemon, the lock manager. You know how to read an execution plan,
> how to diagnose a slow query, how to keep a database alive at scale."

> **Viktor:** "Go build something that doesn't break at 3 AM."

> **Priya:** *(grinning)* "Welcome to the team. For real this time."

> **Maya:** "I'm promoting you to junior database engineer. Effective Monday. Don't
> make me regret it."

You walk out of the conference room. Your phone buzzes — a Grafana alert. P99 latency
spike on the `/api/reports` endpoint.

You smile. You open `psql`.

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) ...
```

You know exactly where to start.

---

## Quick Reference — All Chapters

| Chapter | Incident | Key Concept |
|---|---|---|
| [1. The Slow Query](pg-01-the-slow-query.md) | 47-second query | `EXPLAIN ANALYZE`, composite indexes |
| [2. The Index Trap](pg-02-the-index-trap.md) | 47 indexes, INSERT slowdown | Index overhead, unused index audit |
| [3. The Query Planner](pg-03-the-query-planner.md) | Planner ignores index | Statistics, `random_page_cost`, cost model |
| [4. The VACUUM Crisis](pg-04-the-vacuum-crisis.md) | XID wraparound warning | Autovacuum tuning, dead tuples, `FREEZE` |
| [5. The Connection Storm](pg-05-the-connection-storm.md) | 500 connections, OOM | PgBouncer, connection pooling |
| [6. The Lock Investigation](pg-06-the-lock-investigation.md) | DDL blocks all queries | Lock types, `lock_timeout`, safe migrations |
| [7. The Replication Setup](pg-07-the-replication-setup.md) | Primary disk dies | Streaming replication, failover |
| [8. The Partitioning Strategy](pg-08-the-partitioning-strategy.md) | 2B rows, slow everything | Range/list/hash partitioning, pruning |
| [9. The Backup Disaster](pg-09-the-backup-disaster.md) | Bad DELETE, no backup | `pg_dump`, `pg_basebackup`, WAL archiving, PITR |
| [10. The Production Checklist](pg-10-the-production-checklist.md) | Final review | Config tuning, monitoring, architecture |

---

[← The Backup Disaster](pg-09-the-backup-disaster.md) | [Back to Overview →](pg-00-overview.md)

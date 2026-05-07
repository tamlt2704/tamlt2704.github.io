# PostgreSQL Mastery

Your database is on fire. The DBA quit. The tournament is Saturday. Fix it.

## The Story

You're at **PingPong** — a real-time multiplayer gaming platform with 2.3 million players, 47 million matches, and 890 million game events. The database CPU is at 94%. Queries are doing full table scans. Autovacuum is 3 days behind. You have until Friday.

## Chapters

### Part 1: Stop the Bleeding

| # | The Fire | What You Learn |
|---|----------|----------------|
| 01 | Which query is killing us? | pg_stat_statements, slow query log |
| 02 | Full table scan on 47M rows | EXPLAIN ANALYZE, cost model |
| 03 | Leaderboard takes 12 seconds | Indexes — B-tree, composite, covering |
| 04 | Index exists but ignored | Query planner, statistics, ANALYZE |
| 05 | 40% dead tuples | VACUUM, autovacuum tuning, bloat |

### Part 2: Make It Fast

| # | The Fire | What You Learn |
|---|----------|----------------|
| 06 | Complex reports are slow | CTEs, window functions, lateral joins |
| 07 | Rank, percentile, streaks | Window functions deep dive |
| 08 | Flexible player profiles | JSONB — operators, indexing |
| 09 | Search 2M player names | Full-text search, tsvector, GIN |
| 10 | N+1 queries from the ORM | JOINs, subqueries, ORM traps |

### Part 3: Make It Survive

| # | The Fire | What You Learn |
|---|----------|----------------|
| 11 | 890M row table | Partitioning — range, list, hash |
| 12 | 50K concurrent connections | Connection pooling, PgBouncer |
| 13 | Two players claim same match | Transactions, isolation, deadlocks |
| 14 | Read replicas for leaderboard | Streaming & logical replication |
| 15 | What if the primary dies? | HA — failover, patroni |

### Part 4: Make It Bulletproof

| # | The Fire | What You Learn |
|---|----------|----------------|
| 16 | Migration locks table 10 min | Zero-downtime DDL |
| 17 | Disk 80% full | TOAST, compression, archiving |
| 18 | Who changed that row? | Audit trails, triggers, CDC |
| 19 | What to monitor | pg_stat_*, wait events, alerting |
| 20 | Tournament day: 50K players | Load testing, production checklist |

## Prerequisites

```bash
docker run -d --name pg-dev -p 5432:5432 \
  -e POSTGRES_DB=pingpong -e POSTGRES_PASSWORD=pingpong \
  postgres:16-alpine
```

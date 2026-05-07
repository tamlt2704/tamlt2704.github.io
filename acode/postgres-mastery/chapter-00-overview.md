# PostgreSQL Mastery: A Performance Survival Story

You're back at **PingPong** — the real-time multiplayer gaming platform from the Redis series. Redis handles caching and queues now. But the source of truth is still PostgreSQL. And it's dying.

Monday morning. Ops Olga pages you at 7:42 AM:

> "The database CPU is at 94%. Average query time is 1.2 seconds. The matchmaking endpoint is timing out. Players can't start games. We're losing $8,000/hour in revenue."

You check the dashboard. The `matches` table has 47 million rows. The `players` table has 2.3 million. The `game_events` table has 890 million rows and grows by 3 million per day.

Marta, the tech lead, pulls you aside:

> "Our DBA quit last month. Nobody's touched the database since. There are queries doing full table scans on 47 million rows. There are no indexes on half the foreign keys. The autovacuum is backed up by 3 days. Someone added a `SELECT *` in a loop. Fix it. You have until Friday or we lose the tournament contract."

You open `psql`. The cursor blinks.

---

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Backend Dev (now accidental DBA) | "I know SELECT and JOIN. That counts, right?" |
| **Marta** | Tech Lead | "The query planner is your friend. Read the EXPLAIN." |
| **Ops Olga** | SRE | "CPU at 94%. Do something." Sleeps with PagerDuty. |
| **Derek** | Frontend Lead | "The leaderboard page takes 12 seconds." |
| **CEO Chad** | Founder | "The tournament is Saturday. 50,000 concurrent players." |
| **The Seq Scan** | That one query | Reads 47 million rows to find one match. Every. Single. Time. |
| **The Dead Tuples** | Autovacuum backlog | 40% of the table is dead rows nobody cleaned up. |

---

## The Stack

| Tool | What It Does |
|---|---|
| **PostgreSQL 16** | The database |
| **psql** | CLI client |
| **pgAdmin / DBeaver** | GUI (optional) |
| **pg_stat_statements** | Query performance tracking |
| **EXPLAIN ANALYZE** | Query plan visualization |
| **Docker** | Runs Postgres locally |

---

## How to Read This

Every chapter follows the same loop:

```
  📋 Something is slow, broken, or about to explode
   │
   ▼
  🤔 You identify the problem (EXPLAIN ANALYZE, pg_stat)
   │
   ▼
  ⌨️  You learn the Postgres concept that fixes it
   │
   ▼
  💥 The fix creates a new problem (lock contention, bloat, wrong index)
   │
   ▼
  🧠 You understand WHY and fix it properly
   │
   ▼
  📋 Next fire
```

No concept shows up before you need it. You won't hear about partial indexes until a full index is too big. You won't touch partitioning until a single table hits a billion rows. You won't learn about connection pooling until the server runs out of connections during the tournament.

The fires come first. The SQL follows.

---

## The Roadmap

### Part 1: Foundations — "Stop the Bleeding"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Fire                               │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 01 │ "Which query is killing us?"           │ pg_stat_statements, slow query log, top offenders
────┼────────────────────────────────────────┼──────────────────────────────────────
 02 │ Full table scan on 47M rows            │ EXPLAIN ANALYZE, seq scan vs index scan, cost model
────┼────────────────────────────────────────┼──────────────────────────────────────
 03 │ Leaderboard query takes 12 seconds     │ Indexes — B-tree, creation, composite, covering
────┼────────────────────────────────────────┼──────────────────────────────────────
 04 │ Index exists but Postgres ignores it   │ Query planner decisions, statistics, ANALYZE
────┼────────────────────────────────────────┼──────────────────────────────────────
 05 │ Table is 40% dead tuples               │ VACUUM, autovacuum tuning, bloat, pg_repack
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 2: Query Power — "Make It Fast"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Fire                               │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 06 │ Complex reports are slow               │ CTEs, window functions, lateral joins
────┼────────────────────────────────────────┼──────────────────────────────────────
 07 │ "Show rank, percentile, streaks"       │ Window functions deep dive — ROW_NUMBER,
    │                                        │ RANK, LAG, LEAD, running totals
────┼────────────────────────────────────────┼──────────────────────────────────────
 08 │ Flexible player profiles (JSON fields) │ JSONB — operators, indexing, when to use vs normalize
────┼────────────────────────────────────────┼──────────────────────────────────────
 09 │ Search across 2M player names          │ Full-text search — tsvector, tsquery, GIN indexes
────┼────────────────────────────────────────┼──────────────────────────────────────
 10 │ N+1 queries from the ORM              │ JOINs revisited, subqueries, EXISTS vs IN, ORM traps
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 3: Scale — "Make It Survive"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Fire                               │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 11 │ game_events table: 890M rows           │ Table partitioning — range, list, hash
────┼────────────────────────────────────────┼──────────────────────────────────────
 12 │ Tournament: 50K concurrent connections │ Connection pooling (PgBouncer), pool modes
────┼────────────────────────────────────────┼──────────────────────────────────────
 13 │ Two players claim the same match       │ Transactions, isolation levels, row locking, deadlocks
────┼────────────────────────────────────────┼──────────────────────────────────────
 14 │ Read replicas for the leaderboard      │ Replication — streaming, logical, read routing
────┼────────────────────────────────────────┼──────────────────────────────────────
 15 │ "What if the primary dies?"            │ High availability — failover, pg_basebackup, patroni
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 4: Production — "Make It Bulletproof"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Fire                               │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 16 │ Migration locks the table for 10 min   │ Zero-downtime migrations, lock-safe DDL
────┼────────────────────────────────────────┼──────────────────────────────────────
 17 │ Disk is 80% full                       │ Storage — TOAST, compression, archiving old data
────┼────────────────────────────────────────┼──────────────────────────────────────
 18 │ "Who changed that row?"                │ Audit trails — triggers, logical decoding, CDC
────┼────────────────────────────────────────┼──────────────────────────────────────
 19 │ Monitoring: what to watch              │ pg_stat_*, wait events, lock monitoring, alerting
────┼────────────────────────────────────────┼──────────────────────────────────────
 20 │ The tournament: 50K players, Saturday  │ Load testing, query budget, the production checklist
────┴────────────────────────────────────────┴──────────────────────────────────────
```

---

## The Database: What You Inherit

```sql
-- The schema (simplified)
CREATE TABLE players (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(255),
    elo_rating INTEGER DEFAULT 1200,
    created_at TIMESTAMP DEFAULT now(),
    profile JSONB DEFAULT '{}'
);  -- 2.3 million rows

CREATE TABLE matches (
    id BIGSERIAL PRIMARY KEY,
    player1_id BIGINT REFERENCES players(id),
    player2_id BIGINT REFERENCES players(id),
    winner_id BIGINT REFERENCES players(id),
    status VARCHAR(20),  -- 'pending', 'active', 'completed', 'cancelled'
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    game_mode VARCHAR(30)
);  -- 47 million rows, NO INDEX on player1_id, player2_id, status 😱

CREATE TABLE game_events (
    id BIGSERIAL PRIMARY KEY,
    match_id BIGINT REFERENCES matches(id),
    player_id BIGINT REFERENCES players(id),
    event_type VARCHAR(50),
    payload JSONB,
    created_at TIMESTAMP DEFAULT now()
);  -- 890 million rows, grows 3M/day, never partitioned, never archived
```

No indexes on foreign keys. No partitioning on the event log. Autovacuum can't keep up. The query planner is making bad decisions because statistics are stale.

By Chapter 20, this will be a tuned, partitioned, replicated, monitored database handling 50,000 concurrent players. But first — you need to find which query is killing the server.

---

## Prerequisites

### PostgreSQL 16

```bash
docker run -d --name pg-dev \
  -p 5432:5432 \
  -e POSTGRES_DB=pingpong \
  -e POSTGRES_PASSWORD=pingpong \
  -v pgdata:/var/lib/postgresql/data \
  postgres:16-alpine
```

### psql

```bash
# Connect
docker exec -it pg-dev psql -U postgres -d pingpong

# Or install locally
# macOS: brew install libpq && brew link --force libpq
# Ubuntu: sudo apt install postgresql-client
```

### Seed Data

We'll generate realistic data in Chapter 1, but verify your setup:

```sql
SELECT version();
-- PostgreSQL 16.x ...

SELECT 1 + 1 AS sanity_check;
-- 2
```

If you see the version, you're ready.

### Enable pg_stat_statements

```sql
-- In postgresql.conf (or via Docker env)
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
-- Restart required, then:
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

This tracks every query's execution time, call count, and rows. Essential for Chapter 1.

---

## Why PostgreSQL?

Marta explains it on the whiteboard:

```
MySQL:                          PostgreSQL:
─────                           ──────────
Good enough for CRUD            Advanced query planner
Limited window functions        Full window function support
No JSONB (well, sort of)        First-class JSONB
Partitioning is newer           Mature partitioning
No CTEs until recently          CTEs since forever
Replication is simpler          More replication options
```

> "Postgres isn't just a database. It's a query engine that happens to store data." — Marta

---

[Next: Chapter 1 — Finding the Killer Query →](chapter-01-finding-the-killer.md)

# PostgreSQL Internals — The PayFlow Incident Files

> *A story-driven guide to PostgreSQL performance, internals, and operations.*

---

## The Story So Far

You've been at **PayFlow** for six months now. You joined as a backend intern, survived the
[JPA series](../jpa-00-overview.md), and earned a full-time offer. Life is good. You understand
Spring Boot, entity mappings, and transaction boundaries. You think you know databases.

You don't.

It's a Tuesday afternoon when Maya, the CTO, pulls you into a meeting room. Priya is already
there, arms crossed, staring at a Grafana dashboard that looks like a heart attack.

> **Maya:** "Our database is on fire. Response times are through the roof. The payments team
> is screaming. Priya's team can't ship because every migration takes hours."
>
> **You:** "Should I look at the JPA queries? Maybe we need to tune the fetch strategy—"
>
> **Maya:** "No. We're past JPA. We need someone who understands PostgreSQL *internals*, not
> just the ORM sitting on top of it. I'm pairing you with Viktor."

Viktor is the DBA lead. He's been running PostgreSQL in production since version 8.4. He
doesn't use an ORM. He doesn't use a GUI. He has a terminal with `psql` open at all times,
and his desktop wallpaper is an EXPLAIN ANALYZE output.

He looks at you over his glasses.

> **Viktor:** "You know how to write SQL. That's nice. Now I'm going to teach you what
> happens *after* you press Enter."

---

## How to Read This Series

Every chapter follows the same loop — the way real incidents work:

```
  ┌─────────────────────────────────────────────────┐
  │                                                 │
  │   🔥 Something breaks in production             │
  │         │                                       │
  │         ▼                                       │
  │   🔍 Investigate with SQL                       │
  │         │                                       │
  │         ▼                                       │
  │   🧠 Understand WHY it broke                    │
  │         │                                       │
  │         ▼                                       │
  │   🔧 Fix it                                     │
  │         │                                       │
  │         ▼                                       │
  │   ✅ Verify the fix                              │
  │         │                                       │
  │         ▼                                       │
  │   💡 Learn the deeper concept                   │
  │         │                                       │
  │         └──────── next incident ─────────┐      │
  │                                          │      │
  └──────────────────────────────────────────┘      │
                                                    │
```

You'll see the **wrong approach first** — marked with ⚠️ — because that's how you learn.
The wrong approach breaks. Then you investigate, understand, and fix.

---

## Roadmap

```
────┬────────────────────────────────────┬────────────────────────────────────────────────
Part│The Incident                        │What You Learn
────┼────────────────────────────────────┼────────────────────────────────────────────────
 01 │ A query takes 47 seconds           │ EXPLAIN ANALYZE, seq scan vs index, B-tree
────┼────────────────────────────────────┼────────────────────────────────────────────────
 02 │ 47 indexes and still slow          │ Composite, partial, covering indexes, bloat
────┼────────────────────────────────────┼────────────────────────────────────────────────
 03 │ The planner picks the wrong plan   │ Statistics, pg_stat_statements, plan mistakes
────┼────────────────────────────────────┼────────────────────────────────────────────────
 04 │ Table bloats to 10x its size       │ MVCC, dead tuples, autovacuum, XID wraparound
────┼────────────────────────────────────┼────────────────────────────────────────────────
 05 │ 500 connections, 0 available       │ Connection overhead, pgbouncer, pooling modes
────┼────────────────────────────────────┼────────────────────────────────────────────────
 06 │ UPDATE hangs for 10 minutes        │ Row/table/advisory locks, pg_locks, monitoring
────┼────────────────────────────────────┼────────────────────────────────────────────────
 07 │ The primary goes down at 4 AM      │ Streaming replication, WAL, failover
────┼────────────────────────────────────┼────────────────────────────────────────────────
 08 │ 2 billion rows in one table        │ Range/list/hash partitioning, pruning
────┼────────────────────────────────────┼────────────────────────────────────────────────
 09 │ 'Restore from backup' — 'What backup?' │ pg_dump, pg_basebackup, PITR, WAL archiving
────┼────────────────────────────────────┼────────────────────────────────────────────────
 10 │ Viktor's production checklist      │ Config tuning, monitoring, architecture
────┴────────────────────────────────────┴────────────────────────────────────────────────
```

---

## Prerequisites

| Tool | Version | Why |
|------|---------|-----|
| PostgreSQL | 16+ | We use PG 16 features throughout |
| `psql` | (bundled with PG) | Viktor's tool of choice. You'll live in it. |
| Docker | 20+ | Spin up disposable PG instances for experiments |

Quick start:

```bash
docker run --name payflow-pg \
  -e POSTGRES_PASSWORD=payflow \
  -e POSTGRES_DB=payflow \
  -p 5432:5432 \
  -d postgres:16

psql -h localhost -U postgres -d payflow
```

---

## Characters

| Name | Role | Personality |
|------|------|-------------|
| **You** | DBA intern, former backend intern | Eager, knows JPA, about to learn the hard way |
| **Viktor** | DBA lead | Old-school. Loves `EXPLAIN ANALYZE`. Speaks in SQL. |
| **Maya** | CTO | Same Maya from the JPA series. Pragmatic, impatient, results-driven. |
| **Priya** | Senior dev | Same Priya from the JPA series. Ships fast, sometimes too fast. |

---

> **Viktor:** "Ready? Good. Because your first incident is already waiting."

[Next: The Slow Query →](pg-01-the-slow-query.md)

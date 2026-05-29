# PostgreSQL Mastery

A comprehensive guide to PostgreSQL — from basics to production clusters.

## Chapters

1. [Setup & Installation](chapter-01-setup.md) — Docker, psql, pgAdmin, configuration
2. [SQL Basics](chapter-02-sql-basics.md) — Tables, data types, CRUD operations
3. [Intermediate Queries](chapter-03-queries.md) — JOINs, CTEs, window functions
4. [Indexes](chapter-04-indexes.md) — B-tree, GIN, GiST, EXPLAIN ANALYZE
5. [Advanced Features](chapter-05-advanced-features.md) — Views, procedures, partitioning, triggers
6. [JSONB](chapter-06-jsonb.md) — Storing, querying, indexing JSON data
7. [Performance Tuning](chapter-07-performance.md) — Configuration, VACUUM, query optimization
8. [Security](chapter-08-security.md) — Roles, RLS, SSL, audit logging
9. [Backup & Recovery](chapter-09-backup.md) — pg_dump, WAL archiving, PITR
10. [Replication & Clustering](chapter-10-replication.md) — Streaming replication, Patroni, failover

## Who This Is For

- Developers who want to go beyond basic SELECT statements
- Backend engineers building data-intensive applications
- DevOps/SREs managing PostgreSQL in production

## Prerequisites

- Basic command-line familiarity
- Docker installed (for the setup chapter)
- A text editor and terminal

## Convention

All SQL examples are runnable directly in `psql`. Output examples are shown where helpful. Each chapter ends with practical exercises.

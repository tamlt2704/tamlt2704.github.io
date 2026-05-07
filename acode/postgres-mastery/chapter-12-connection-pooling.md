# Chapter 12: Connection Pooling — Surviving 50,000 Players

[← Chapter 11: Partitioning](chapter-11-partitioning.md) | [Chapter 13: Transactions →](chapter-13-transactions.md)

---

## The Fire

Thursday. The tournament is Saturday. Ops Olga runs a load test simulating 50,000 concurrent players:

```
[ERROR] FATAL: too many connections for role "pingpong_app"
[ERROR] FATAL: remaining connection slots are reserved for non-replication superuser connections
[ERROR] sorry, too many clients already
```

You check:

```sql
SHOW max_connections;  -- 200

SELECT count(*) FROM pg_stat_activity;  -- 198
```

200 connections. The app opens one per request. 50,000 players = 50,000 connections needed. Postgres can't handle that.

Marta:

> "Postgres forks a process per connection. 200 connections = 200 processes. Each uses ~10MB of RAM. 50,000 connections would need 500GB of RAM. You need a connection pooler."

---

## Why max_connections Can't Scale

Each Postgres connection:
- Forks a new OS process (~10MB RAM)
- Maintains its own query cache
- Competes for CPU context switches
- Holds locks and transaction state

```sql
-- Current connection usage
SELECT
    usename,
    state,
    COUNT(*) AS connections
FROM pg_stat_activity
GROUP BY usename, state
ORDER BY connections DESC;
```

```
 usename      | state  | connections
--------------+--------+-------------
 pingpong_app | idle   | 142
 pingpong_app | active | 38
 postgres     | active | 2
```

142 connections are **idle** — doing nothing but holding resources. The app opens a connection, runs one query, then holds it open.

---

## PgBouncer: The Connection Multiplexer

PgBouncer sits between your app and Postgres. It maintains a small pool of real connections and multiplexes thousands of client connections through them:

```
App (50,000 connections) → PgBouncer (pool of 50) → Postgres (50 connections)
```

### Installation

```bash
# Ubuntu
sudo apt install pgbouncer

# Docker
docker run -d --name pgbouncer \
  -p 6432:6432 \
  -e DATABASE_URL="postgres://postgres:pingpong@pg-dev:5432/pingpong" \
  edoburu/pgbouncer
```

### Configuration (pgbouncer.ini)

```ini
[databases]
pingpong = host=127.0.0.1 port=5432 dbname=pingpong

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt

; Pool settings
pool_mode = transaction
default_pool_size = 50
max_client_conn = 10000
min_pool_size = 10
reserve_pool_size = 5
reserve_pool_timeout = 3

; Timeouts
server_idle_timeout = 300
client_idle_timeout = 0
query_timeout = 30
```

### User Authentication (userlist.txt)

```
"pingpong_app" "md5hash_of_password"
"postgres" "md5hash_of_password"
```

---

## Pool Modes

| Mode | How It Works | Limitations | Use Case |
|------|-------------|-------------|----------|
| **Transaction** | Connection returned after each transaction | No session-level features | Web apps (recommended) |
| **Session** | Connection held for entire client session | Limited pooling benefit | Apps needing session state |
| **Statement** | Connection returned after each statement | No multi-statement transactions! | Simple read-only queries |

### Transaction Mode (Recommended)

```ini
pool_mode = transaction
```

The connection is assigned when a transaction starts and returned when it commits/rolls back. Between transactions, the connection is available for other clients.

**Limitations in transaction mode:**
- No `SET` commands (session-level)
- No `LISTEN/NOTIFY`
- No prepared statements (by default)
- No `DECLARE CURSOR` outside transactions

```sql
-- ❌ Won't work in transaction mode
SET search_path TO myschema;
SELECT * FROM mytable;  -- Different connection, search_path is reset!

-- ✅ Works: use SET LOCAL inside a transaction
BEGIN;
SET LOCAL search_path TO myschema;
SELECT * FROM mytable;
COMMIT;
```

### Session Mode

```ini
pool_mode = session
```

Client gets a dedicated connection for the entire session. Less efficient but supports all Postgres features.

---

## Sizing the Pool

**Formula:**

```
pool_size = number_of_CPU_cores * 2 + number_of_disks

Example: 8 cores, 1 SSD
pool_size = 8 * 2 + 1 = 17 (round to 20)
```

More connections ≠ more throughput. After a point, connections compete for CPU and locks:

```
Connections:  10   20   50   100   200   500
Throughput:   ↑    ↑    ↑    →     ↓     ↓↓
```

### PingPong Configuration

```ini
; 16-core server, SSD storage
default_pool_size = 40        ; Real connections to Postgres
max_client_conn = 50000       ; Client connections PgBouncer accepts
min_pool_size = 10            ; Keep warm connections ready
reserve_pool_size = 10        ; Extra connections for spikes
reserve_pool_timeout = 3      ; Wait 3s before using reserve
```

```sql
-- Reduce Postgres max_connections (PgBouncer handles the rest)
ALTER SYSTEM SET max_connections = 60;  -- 40 pool + 10 reserve + 10 admin
-- Restart required
```

---

## Monitoring PgBouncer

```sql
-- Connect to PgBouncer's admin console
psql -h 127.0.0.1 -p 6432 -U pgbouncer pgbouncer

-- Show pool status
SHOW POOLS;
```

```
 database | user         | cl_active | cl_waiting | sv_active | sv_idle | pool_mode
----------+--------------+-----------+------------+-----------+---------+-----------
 pingpong | pingpong_app |      4821 |         12 |        38 |      12 | transaction
```

| Column | Meaning |
|--------|---------|
| `cl_active` | Client connections with active queries |
| `cl_waiting` | Clients waiting for a server connection |
| `sv_active` | Server connections running queries |
| `sv_idle` | Server connections available |

```sql
-- Show stats
SHOW STATS;

-- Show current client connections
SHOW CLIENTS;

-- Show server connections
SHOW SERVERS;
```

**Alert if `cl_waiting > 0` for more than 5 seconds** — clients are queuing.

---

## Application-Level Pooling

Most frameworks also have connection pools. Use both:

```
App Pool (per instance) → PgBouncer (shared) → Postgres

App Instance 1: pool_size=5  ─┐
App Instance 2: pool_size=5  ─┼─→ PgBouncer (pool=40) → Postgres (max=60)
App Instance 3: pool_size=5  ─┤
...                           │
App Instance 10: pool_size=5 ─┘
```

```python
# Python (SQLAlchemy)
engine = create_engine(
    "postgresql://user:pass@pgbouncer:6432/pingpong",
    pool_size=5,           # Connections per app instance
    max_overflow=10,       # Extra connections under load
    pool_timeout=30,       # Wait time for a connection
    pool_recycle=300,      # Recycle connections every 5 min
    pool_pre_ping=True     # Verify connection is alive
)
```

---

## The Tournament Configuration

```ini
; pgbouncer.ini for tournament day
[databases]
pingpong = host=pg-primary port=5432 dbname=pingpong
pingpong_readonly = host=pg-replica port=5432 dbname=pingpong

[pgbouncer]
pool_mode = transaction
default_pool_size = 40
max_client_conn = 50000
min_pool_size = 20
reserve_pool_size = 10
server_idle_timeout = 60
client_idle_timeout = 300
query_timeout = 10          ; Kill queries over 10s during tournament
```

---

## Quick Reference

| Setting | Default | Tournament |
|---------|---------|------------|
| `pool_mode` | session | transaction |
| `default_pool_size` | 20 | 40 |
| `max_client_conn` | 100 | 50000 |
| `min_pool_size` | 0 | 20 |
| `reserve_pool_size` | 0 | 10 |
| `query_timeout` | 0 | 10 |

| PgBouncer Command | Purpose |
|-------------------|---------|
| `SHOW POOLS` | Pool status and waiting clients |
| `SHOW STATS` | Query counts and durations |
| `SHOW CLIENTS` | Connected clients |
| `SHOW SERVERS` | Backend connections |
| `PAUSE db` | Pause a database (for maintenance) |
| `RESUME db` | Resume after pause |
| `RELOAD` | Reload config without restart |

---

## Exercises

### Exercise 1: Pool Sizing

Your server has 8 CPU cores and NVMe storage. You have 20 app instances, each with a pool of 3 connections. Calculate:
1. The optimal `default_pool_size` for PgBouncer
2. The `max_connections` for Postgres
3. Whether you need `reserve_pool_size`

### Exercise 2: Monitoring Query

Write a monitoring query that alerts when:
- `cl_waiting` > 0 for more than 5 seconds
- `sv_active` = `default_pool_size` (pool exhausted)
- Average query time exceeds 100ms

### Exercise 3: Transaction Mode Gotchas

Identify which of these patterns will break in transaction pool mode:
1. `SET statement_timeout = '5s'; SELECT ...;`
2. `BEGIN; SELECT ...; UPDATE ...; COMMIT;`
3. `PREPARE stmt AS SELECT ...; EXECUTE stmt;`
4. `LISTEN new_match; -- wait for notification`

---

## What Happens Next

Connection pooling is configured. 50,000 clients can connect through 40 real connections. But the load test reveals a new problem:

> "Two players both claim they won the same match. The ELO update ran twice. We have a race condition."

Time to learn about transactions, isolation levels, and row locking.

---

[← Chapter 11: Partitioning](chapter-11-partitioning.md) | [Chapter 13: Transactions →](chapter-13-transactions.md)

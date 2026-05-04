# Chapter 5: The Connection Storm — "500 Connections, 0 Available"

[← The Vacuum Crisis](pg-04-the-vacuum-crisis.md) | [Next: The Lock Investigation →](pg-06-the-lock-investigation.md)

---

## The Incident

Black Friday. 6:02 AM. Traffic spikes 10x before the team is even awake.

Every microservice — payments, notifications, analytics, fraud detection — opens its own
connection pool to PostgreSQL. Each pool is configured for 50 connections. Ten services.
That's 500 connections. PostgreSQL's `max_connections` is set to 100 (the default).

The first error hits at 6:03 AM:

```
FATAL: too many connections for role "payflow"
FATAL: sorry, too many clients already
```

New requests can't connect. Existing connections start timing out because the server is
thrashing. The cascade begins: health checks fail, Kubernetes restarts pods, restarted pods
try to reconnect, making it worse.

> **Maya** (Slack, 6:14 AM): *"The entire platform is down. Merchants can't process
> payments. This is a P0."*

Viktor is already in the war room.

> **Viktor:** "How many connections do we actually need? Let me show you something."

---

## 1. Why Connections Are Expensive

> **Viktor:** "Each PostgreSQL connection is a full **OS process**. Not a thread — a
> process. Every connection forks a new backend process that consumes about **10 MB of RAM**,
> has its own memory context, and competes for CPU time."

He runs:

```sql
SELECT count(*) AS total,
       count(*) FILTER (WHERE state = 'active') AS active,
       count(*) FILTER (WHERE state = 'idle') AS idle,
       count(*) FILTER (WHERE state = 'idle in transaction') AS idle_in_txn
FROM pg_stat_activity
WHERE backend_type = 'client backend';
```

```
 total | active | idle | idle_in_txn
-------+--------+------+-------------
   487 |     23 |  412 |          52
```

> **Viktor:** "487 connections. 23 are actually doing work. **412 connections doing
> NOTHING.** Each one eating 10 MB of RAM and a process slot. That's 4 GB of RAM wasted
> on idle connections. And 52 are 'idle in transaction' — those are even worse."

> **You:** "Can't we just increase `max_connections` to 1000?"

> **Viktor:** "That's like widening a highway to fix a traffic jam caused by parked cars.
> You don't need more lanes. You need to tow the parked cars."

---

## 2. The Real Problem: Idle in Transaction

> **Viktor:** "See those 52 'idle in transaction' connections? Someone opened a `BEGIN`,
> ran a query, and then... nothing. No `COMMIT`. No `ROLLBACK`. The transaction is just
> sitting there, holding locks, preventing VACUUM from cleaning dead tuples, and wasting
> a connection slot."

```sql
-- Find the worst offenders
SELECT pid, usename, application_name,
       state, query,
       now() - state_change AS idle_duration
FROM pg_stat_activity
WHERE state = 'idle in transaction'
ORDER BY state_change
LIMIT 10;
```

```
  pid  | usename | application_name |        state        |          query           | idle_duration
-------+---------+------------------+---------------------+--------------------------+---------------
 14023 | payflow | fraud-service    | idle in transaction | SELECT * FROM accounts.. | 02:34:17
 14089 | payflow | notif-service    | idle in transaction | UPDATE notifications ... | 01:12:44
 14102 | payflow | analytics        | idle in transaction | SELECT count(*) FROM ... | 00:45:22
```

> **Viktor:** "The fraud service has been sitting in an open transaction for **two and a
> half hours**. That's a bug in the application — probably a missing `finally` block or a
> connection that was borrowed from the pool and never returned."

The fix is a safety net in `postgresql.conf`:

```
idle_in_transaction_session_timeout = '30s'
```

> **Viktor:** "After 30 seconds of idle-in-transaction, PostgreSQL kills the session. The
> application gets an error, which is better than silently holding locks for hours."

---

## 3. PgBouncer to the Rescue

> **Viktor:** "The real fix isn't tuning PostgreSQL's connection limit. It's putting a
> **connection pooler** in front of it. Meet PgBouncer."

He draws the architecture:

```
App (100 connections) → PgBouncer (100 → 20) → PostgreSQL (20 connections)
App (100 connections) → PgBouncer              ↑
App (100 connections) → PgBouncer              ↑
                         300 app connections share 20 PG connections
```

> **Viktor:** "Your 10 microservices think they each have 50 connections. But PgBouncer
> multiplexes all of them down to 20 real PostgreSQL connections. The apps don't know the
> difference. PgBouncer hands out a real connection when a transaction starts and takes it
> back when the transaction ends."

PgBouncer config (`pgbouncer.ini`):

```ini
[databases]
payflow = host=localhost port=5432 dbname=payflow

[pgbouncer]
listen_port = 6432
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
reserve_pool_size = 5
reserve_pool_timeout = 3
```

> **Viktor:** "`max_client_conn = 1000` — PgBouncer accepts up to 1000 app connections.
> `default_pool_size = 20` — it only opens 20 real connections to PostgreSQL. The reserve
> pool is for burst traffic — 5 extra connections that activate if all 20 are busy for
> more than 3 seconds."

---

## 4. Pool Modes Explained

> **You:** "What's `pool_mode = transaction`?"

| Mode | How It Works | Pros | Cons |
|---|---|---|---|
| `session` | 1 PG conn per client session | Full PG feature support | No multiplexing — defeats the purpose |
| `transaction` | PG conn assigned per transaction | Best balance of safety and efficiency | No session-level features (`LISTEN/NOTIFY`, prepared statements) |
| `statement` | PG conn assigned per statement | Maximum multiplexing | No multi-statement transactions — breaks most apps |

> **Viktor:** "Use **transaction mode**. Always. Session mode is pointless — you get no
> multiplexing. Statement mode breaks any code that uses `BEGIN`/`COMMIT`. Transaction
> mode is the sweet spot: your app gets a real PG connection for the duration of each
> transaction, then it goes back to the pool."

> **You:** "What about prepared statements? Our ORM uses them."

> **Viktor:** "In transaction mode, prepared statements don't survive across transactions.
> Most ORMs handle this fine — they re-prepare automatically. If yours doesn't, check the
> ORM docs for PgBouncer compatibility settings."

---

## 5. The Connection Formula

> **Viktor:** "Here's the formula I've used for 15 years:"

```
max PG connections = (CPU cores × 2) + effective_spindle_count
```

> **Viktor:** "For an 8-core server with SSD: `(8 × 2) + 1 = 17`. Round up to **20**.
> That's it. Twenty connections."

> **You:** "Twenty?! We had 487!"

> **Viktor:** "And 412 of them were idle. More connections means more context switching,
> more lock contention, more memory pressure. I've seen databases go from **500 connections
> to 20 and get 3x faster**. The bottleneck is never the number of connections — it's the
> number of CPU cores doing actual work."

He draws it out:

```
┌──────────────────────────────────────────────────┐
│  500 connections, 8 cores:                       │
│  → 492 processes waiting for CPU                 │
│  → Constant context switching                    │
│  → Lock contention on shared buffers             │
│  → Result: SLOWER                                │
│                                                  │
│  20 connections, 8 cores:                        │
│  → 12 processes waiting for CPU (manageable)     │
│  → Minimal context switching                     │
│  → Less lock contention                          │
│  → Result: 3x FASTER                             │
└──────────────────────────────────────────────────┘
```

---

## 6. Docker Compose with PgBouncer

Viktor sets up the stack:

```yaml
pgbouncer:
  image: edoburu/pgbouncer:latest
  ports:
    - "6432:6432"
  environment:
    DATABASE_URL: "postgres://payflow:payflow@postgres:5432/payflow"
    POOL_MODE: transaction
    MAX_CLIENT_CONN: 1000
    DEFAULT_POOL_SIZE: 20
  depends_on:
    - postgres
```

> **Viktor:** "Your application connects to port **6432** (PgBouncer) instead of 5432
> (PostgreSQL directly). That's the only change. Update the connection string and deploy."

```
# Before (direct to PG)
DATABASE_URL=postgres://payflow:payflow@db:5432/payflow

# After (through PgBouncer)
DATABASE_URL=postgres://payflow:payflow@db:6432/payflow
```

---

## Verification

After deploying PgBouncer and restarting all services:

```sql
SELECT count(*) AS total,
       count(*) FILTER (WHERE state = 'active') AS active,
       count(*) FILTER (WHERE state = 'idle') AS idle
FROM pg_stat_activity
WHERE backend_type = 'client backend';
```

```
 total | active | idle
-------+--------+------
    20 |     11 |    9
```

> **Viktor:** "From 487 to 20. Same traffic. Same throughput. P99 latency dropped from
> 1200ms to 180ms because the server isn't drowning in context switches anymore."

---

## Key Takeaways

1. **Each PG connection is an OS process** — ~10 MB RAM, real CPU overhead. More connections ≠ more throughput.
2. **`idle in transaction`** is the silent killer — it holds locks, blocks VACUUM, and wastes slots. Set `idle_in_transaction_session_timeout`.
3. **PgBouncer** multiplexes hundreds of app connections into a small pool of real PG connections.
4. **Transaction pool mode** is the right default — session mode defeats the purpose, statement mode breaks transactions.
5. **The connection formula**: `(CPU cores × 2) + spindle_count`. For most servers, 20–30 real connections is optimal.
6. **Don't increase `max_connections`** to fix connection exhaustion — add a pooler instead.

---

## What's Next

Connections are under control. PgBouncer is humming along. The platform survived Black
Friday. You think the worst is behind you.

Then on Monday, a developer runs an `UPDATE` on the `accounts` table. It hangs. For 10
minutes. No error, no timeout, just... waiting. The cursor blinks. Nothing happens.

Welcome to lock hell.

[Next: The Lock Investigation →](pg-06-the-lock-investigation.md)

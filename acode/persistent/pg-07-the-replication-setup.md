# Chapter 7: The Replication Setup — "The Primary Goes Down at 4 AM"

[← The Lock Investigation](pg-06-the-lock-investigation.md) | [Next: The Partitioning Strategy →](pg-08-the-partitioning-strategy.md)

---

## The Incident

4:03 AM. PagerDuty. Your phone screams.

```
🔴 CRITICAL: PostgreSQL primary — disk I/O errors
🔴 CRITICAL: PayFlow API — connection refused to database
🔴 CRITICAL: Payment processing — 100% failure rate
```

The primary PostgreSQL server's disk has died. Not degraded — dead. The RAID controller
gave up. Every query returns `FATAL: could not open file "base/16384/..."`. PayFlow is
completely down. Merchants can't process payments. Every second is lost revenue.

Maya is on the call within minutes.

> **Maya:** "How do we not have a replica?"

Silence.

> **Maya:** "How long to restore from backup?"

> **Viktor:** "The last `pg_dump` was 6 hours ago. It's 200 GB. Restore will take 2–3
> hours. We'll lose 6 hours of transactions."

> **Maya:** "That's unacceptable. Fix the server. Then make sure this never happens again."

Three hours later, the database is restored from backup. Six hours of transactions are gone.
The finance team spends the next week reconciling with payment processors.

Viktor pulls you aside the next morning.

> **Viktor:** "We're setting up streaming replication today. Right now. No more single
> points of failure."

---

## 1. How Streaming Replication Works

Viktor draws on the whiteboard:

```
Primary                          Replica
┌─────────────────────┐  WAL stream  ┌─────────────────────┐
│ Client writes       │ ──────────→  │ Replays WAL         │
│ → WAL generated     │              │ → Data updated       │
│ → Data updated      │              │ → Read-only queries  │
└─────────────────────┘              └─────────────────────┘
```

> **Viktor:** "Every write in PostgreSQL — INSERT, UPDATE, DELETE, DDL — generates a
> **WAL record** (Write-Ahead Log). The WAL is PostgreSQL's transaction log. It's how
> crash recovery works: replay the WAL to reconstruct the database state."

> **Viktor:** "Streaming replication sends these WAL records to a replica server **in real
> time**. The replica replays them continuously. It's an exact copy of the primary, always
> catching up. If the primary dies, you promote the replica and you're back online in
> seconds instead of hours."

> **You:** "Can we read from the replica?"

> **Viktor:** "Yes. With `hot_standby = on`, the replica accepts read-only queries. You
> can point your analytics dashboards and reporting queries at the replica to offload the
> primary. But no writes — only the primary accepts writes."

---

## 2. Setting Up the Primary

> **Viktor:** "First, configure the primary to send WAL to replicas."

Primary's `postgresql.conf`:

```
wal_level = replica
max_wal_senders = 5
max_replication_slots = 5
hot_standby = on
```

> **Viktor:** "`wal_level = replica` tells PostgreSQL to include enough information in the
> WAL for a replica to reconstruct the data. `max_wal_senders = 5` allows up to 5 replicas
> to stream simultaneously. Replication slots ensure the primary keeps WAL segments until
> the replica has consumed them — no data loss if the replica falls behind."

Create a replication user and slot:

```sql
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'rep_secret';
SELECT pg_create_physical_replication_slot('replica_1');
```

Add the replica to `pg_hba.conf` (authentication):

```
host replication replicator replica_ip/32 scram-sha-256
```

> **Viktor:** "Reload the config — no restart needed for `pg_hba.conf`:"

```sql
SELECT pg_reload_conf();
```

---

## 3. Setting Up the Replica

> **Viktor:** "Now we clone the primary onto the replica server."

```bash
# Take a base backup from the primary
pg_basebackup -h primary_ip -U replicator \
  -D /var/lib/postgresql/data \
  -S replica_1 -X stream -P
```

> **Viktor:** "`pg_basebackup` copies the entire data directory from the primary. The `-S`
> flag tells it to use our replication slot. `-X stream` streams WAL during the backup so
> we don't miss any changes. `-P` shows progress."

Configure the replica's `postgresql.conf`:

```
primary_conninfo = 'host=primary_ip user=replicator password=rep_secret'
primary_slot_name = 'replica_1'
hot_standby = on
```

Create the standby signal file:

```bash
touch /var/lib/postgresql/data/standby.signal
```

> **Viktor:** "The `standby.signal` file tells PostgreSQL 'you are a replica.' When it
> starts, it connects to the primary using `primary_conninfo` and starts streaming WAL.
> That's it. Start PostgreSQL on the replica and replication begins."

```bash
pg_ctl start -D /var/lib/postgresql/data
```

---

## 4. Sync vs Async Replication

> **You:** "What if the primary crashes right after a write but before the WAL reaches the
> replica? Do we lose that transaction?"

> **Viktor:** "Good question. That depends on the replication mode."

| Mode | Data Safety | Latency | Config |
|---|---|---|---|
| **Async** (default) | Replica can lag behind — possible data loss on failover | Lowest | `synchronous_commit = on` (default) |
| **Sync** | Zero data loss — primary waits for replica confirmation | Higher (waits for replica ACK) | `synchronous_standby_names = 'replica_1'` |

> **Viktor:** "With async replication, the primary doesn't wait for the replica. Writes are
> fast, but if the primary crashes, the last few milliseconds of transactions might not have
> reached the replica yet."

> **Viktor:** "With synchronous replication, the primary waits until the replica confirms
> it received and flushed the WAL. Zero data loss — but every write is now limited by
> network latency to the replica."

> **Viktor:** "**For money, use synchronous.** PayFlow processes payments — we can't lose
> transactions. For analytics replicas or read replicas in another region, async is fine."

```sql
-- On the primary, enable synchronous replication
ALTER SYSTEM SET synchronous_standby_names = 'replica_1';
SELECT pg_reload_conf();
```

---

## 5. Monitoring Replication Lag

> **Viktor:** "Replication is running. Now we need to monitor it. If the replica falls too
> far behind, failover means data loss (async) or write stalls (sync)."

On the **primary**:

```sql
SELECT client_addr,
       state,
       sent_lsn,
       write_lsn,
       flush_lsn,
       replay_lsn,
       pg_wal_lsn_diff(sent_lsn, replay_lsn) AS replay_lag_bytes
FROM pg_stat_replication;
```

```
 client_addr  |   state   |  sent_lsn   | write_lsn   | flush_lsn   | replay_lsn  | replay_lag_bytes
--------------+-----------+-------------+-------------+-------------+-------------+------------------
 10.0.1.52    | streaming | 3/A5001000  | 3/A5001000  | 3/A5001000  | 3/A5000F80  |              128
```

> **Viktor:** "128 bytes behind. That's essentially zero lag — the replica is keeping up
> perfectly."

On the **replica**:

```sql
SELECT now() - pg_last_xact_replay_timestamp() AS replay_lag;
```

```
  replay_lag
--------------
 00:00:00.003
```

> **Viktor:** "3 milliseconds. If this number starts climbing — seconds, minutes — the
> replica is falling behind. Common causes: slow disk on the replica, network issues, or
> heavy write load on the primary."

---

## 6. Failover

> **Viktor:** "The moment we've been preparing for. The primary dies. What do you do?"

> **You:** "Promote the replica?"

> **Viktor:** "Exactly."

```bash
# On the replica — promote to primary
pg_ctl promote -D /var/lib/postgresql/data
```

Or from SQL (if you can connect):

```sql
SELECT pg_promote();
```

> **Viktor:** "The replica removes `standby.signal`, stops replaying WAL, and starts
> accepting writes. It's now the new primary. Total promotion time: under 5 seconds."

> **Viktor:** "Then update your application's connection string to point to the new primary.
> In production, you don't do this manually. Use **Patroni** or **pg_auto_failover** for
> automatic failover — they detect the primary going down, promote the replica, and update
> the connection endpoint automatically."

```
┌──────────────────────────────────────────────────┐
│  FAILOVER CHECKLIST                              │
│                                                  │
│  1. Confirm primary is truly down (not network)  │
│  2. Check replica lag — how much data is lost?   │
│  3. Promote replica: pg_ctl promote              │
│  4. Update DNS / connection string               │
│  5. Verify writes work on new primary            │
│  6. Set up a new replica ASAP                    │
│  7. Post-mortem: why did the primary fail?       │
└──────────────────────────────────────────────────┘
```

---

## 7. Docker Compose for Primary + Replica

Viktor sets up a local environment for testing:

```yaml
services:
  pg-primary:
    image: postgres:16-alpine
    ports: ["5432:5432"]
    environment:
      POSTGRES_DB: payflow
      POSTGRES_USER: payflow
      POSTGRES_PASSWORD: payflow
    command: >
      postgres
      -c wal_level=replica
      -c max_wal_senders=5
      -c max_replication_slots=5
      -c hot_standby=on
```

> **Viktor:** "This gets the primary running with replication enabled. For a full
> primary + replica Docker setup, you'd add an init script that creates the replication
> user and slot, then a replica container that runs `pg_basebackup` on startup."

> **You:** "Can we test failover locally?"

> **Viktor:** "Yes. Stop the primary container, exec into the replica, run `pg_promote()`,
> and verify writes work. Practice it until it's muscle memory. The 4 AM incident is not
> the time to read documentation."

---

## Verification

Confirm replication is working:

```sql
-- On the primary: check replica is connected
SELECT client_addr, state, sync_state
FROM pg_stat_replication;
```

```
 client_addr |   state   | sync_state
-------------+-----------+------------
 10.0.1.52   | streaming | sync
```

```sql
-- On the replica: confirm it's in recovery mode
SELECT pg_is_in_recovery();
```

```
 pg_is_in_recovery
-------------------
 t
```

```sql
-- Write test: this should FAIL on the replica
INSERT INTO accounts (name) VALUES ('test');
-- ERROR: cannot execute INSERT in a read-only transaction
```

> **Viktor:** "Replica is streaming, synchronous, and read-only. If the primary dies
> tonight, we promote and we're back in 5 seconds. Not 3 hours."

---

## Key Takeaways

1. **Streaming replication** sends WAL records from primary to replica in real time — the replica is an always-up-to-date copy.
2. **`pg_basebackup`** clones the primary to initialize a replica — no downtime required.
3. **Synchronous replication** guarantees zero data loss but adds write latency. Use it for financial data.
4. **Async replication** is faster but can lose the last few milliseconds of transactions on failover.
5. **Monitor replication lag** — `pg_stat_replication` on the primary, `pg_last_xact_replay_timestamp()` on the replica.
6. **Failover is fast** — `pg_ctl promote` takes seconds. The hard part is automation. Use Patroni or pg_auto_failover.
7. **Practice failover** before you need it. The 4 AM incident is not the time to learn.

---

## What's Next

Replication keeps you alive when hardware fails. The primary goes down, the replica takes
over, and PayFlow keeps processing payments. You sleep better at night.

But the `transactions` table just hit **2 billion rows**. Even with perfect indexes from
[Chapter 2](pg-02-the-index-trap.md) and a well-tuned planner from [Chapter 3](pg-03-the-query-planner.md),
queries are slowing down. The B-tree is too deep. Sequential scans on date ranges touch
too many pages. The table is simply too big.

Time to split the table.

[Next: The Partitioning Strategy →](pg-08-the-partitioning-strategy.md)

# Chapter 15: High Availability — What If the Primary Dies?

[← Chapter 14: Replication](chapter-14-replication.md) | [Chapter 16: Zero-Downtime DDL →](chapter-16-zero-downtime-ddl.md)

---

## The Fire

Friday night. 12 hours before the tournament. Ops Olga runs a chaos test — she kills the primary database:

```bash
docker stop pg-primary
```

Result:
- All writes fail immediately
- The replica is still serving reads (leaderboard works)
- Matchmaking is dead (needs writes)
- Players can't start games

Time to recover: **14 minutes** (manual intervention — Olga had to SSH in, promote the replica, update DNS, restart the app).

CEO Chad:

> "14 minutes of downtime during the tournament = $18,000 lost revenue and a PR disaster. Make it automatic. Under 30 seconds."

---

## Manual Failover (The Baseline)

### Promoting a Replica

```sql
-- On the replica: promote to primary
SELECT pg_promote();
-- Or from command line:
-- pg_ctl promote -D /var/lib/postgresql/data
```

After promotion:
- The replica stops receiving WAL from the old primary
- It becomes a read-write server
- The `standby.signal` file is removed
- Applications must reconnect to the new primary

### The Manual Process

```
1. Detect primary is down (monitoring alert)     ~1-2 min
2. SSH into replica                              ~1 min
3. Verify primary is truly dead (not split-brain) ~2 min
4. Promote replica: pg_promote()                  ~5 sec
5. Update DNS/connection strings                  ~5-10 min
6. Restart application servers                    ~2 min
                                          Total: ~14 min
```

---

## Automatic Failover with Patroni

Patroni is the industry standard for PostgreSQL HA. It uses a distributed consensus store (etcd) to coordinate failover:

```
                    ┌─────────┐
                    │  etcd   │ (consensus store)
                    └────┬────┘
                         │
            ┌────────────┼────────────┐
            │            │            │
      ┌─────┴─────┐ ┌───┴───┐ ┌─────┴─────┐
      │  Patroni  │ │Patroni│ │  Patroni  │
      │  Primary  │ │Replica│ │  Replica  │
      └───────────┘ └───────┘ └───────────┘
```

### How Patroni Works

1. Each Postgres node runs a Patroni agent
2. Patroni agents communicate via etcd (distributed key-value store)
3. The primary holds a "leader lock" in etcd
4. If the primary fails, the lock expires
5. Patroni promotes the most up-to-date replica
6. Applications connect via a virtual IP or HAProxy

### Patroni Configuration

```yaml
# patroni.yml
scope: pingpong-cluster
name: pg-node-1

restapi:
  listen: 0.0.0.0:8008
  connect_address: 10.0.0.11:8008

etcd3:
  hosts: 10.0.0.20:2379,10.0.0.21:2379,10.0.0.22:2379

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576  # 1MB max lag for promotion
    postgresql:
      use_pg_rewind: true
      parameters:
        wal_level: replica
        max_wal_senders: 5
        max_replication_slots: 5
        hot_standby: on
        wal_log_hints: on

  initdb:
    - encoding: UTF8
    - data-checksums

postgresql:
  listen: 0.0.0.0:5432
  connect_address: 10.0.0.11:5432
  data_dir: /var/lib/postgresql/data
  authentication:
    superuser:
      username: postgres
      password: secret
    replication:
      username: replicator
      password: rep_secret
```

### Starting Patroni

```bash
# On each node
patroni /etc/patroni/patroni.yml

# Check cluster status
patronictl -c /etc/patroni/patroni.yml list
```

```
+ Cluster: pingpong-cluster ----+---------+---------+----+-----------+
| Member    | Host       | Role    | State   | TL | Lag in MB |
+-----------+------------+---------+---------+----+-----------+
| pg-node-1 | 10.0.0.11  | Leader  | running |  3 |           |
| pg-node-2 | 10.0.0.12  | Replica | running |  3 |       0.0 |
| pg-node-3 | 10.0.0.13  | Replica | running |  3 |       0.0 |
+-----------+------------+---------+---------+----+-----------+
```

---

## Split-Brain Prevention

The worst scenario: both nodes think they're the primary. Both accept writes. Data diverges.

Patroni prevents this with:

1. **Leader lock in etcd**: Only one node holds the lock
2. **Fencing**: The old primary is shut down before promoting a new one
3. **pg_rewind**: After recovery, the old primary rewinds to the fork point and follows the new primary

```yaml
# patroni.yml - fencing configuration
postgresql:
  use_pg_rewind: true  # Allows old primary to rejoin as replica
  parameters:
    wal_log_hints: on   # Required for pg_rewind
```

### What Happens During Failover

```
T=0s:   Primary crashes
T=10s:  Patroni detects missing heartbeat (loop_wait)
T=20s:  Leader lock expires in etcd (ttl=30)
T=21s:  Replica with least lag acquires leader lock
T=22s:  Patroni promotes the replica
T=23s:  HAProxy health check detects new primary
T=25s:  Traffic routes to new primary
                                    Total: ~25 seconds
```

---

## HAProxy for Connection Routing

```
App → HAProxy → Primary (writes)
            └→ Replica (reads)
```

```
# haproxy.cfg
global
    maxconn 1000

defaults
    mode tcp
    timeout connect 5s
    timeout client 30s
    timeout server 30s

# Write traffic → primary only
frontend pg_write
    bind *:5432
    default_backend pg_primary

backend pg_primary
    option httpchk GET /primary
    http-check expect status 200
    server pg-node-1 10.0.0.11:5432 check port 8008
    server pg-node-2 10.0.0.12:5432 check port 8008
    server pg-node-3 10.0.0.13:5432 check port 8008

# Read traffic → all replicas
frontend pg_read
    bind *:5433
    default_backend pg_replicas

backend pg_replicas
    option httpchk GET /replica
    http-check expect status 200
    balance roundrobin
    server pg-node-2 10.0.0.12:5432 check port 8008
    server pg-node-3 10.0.0.13:5432 check port 8008
```

Patroni exposes REST endpoints:
- `/primary` returns 200 on the current primary
- `/replica` returns 200 on replicas

HAProxy routes based on these health checks.

---

## Testing Failover

```bash
# Simulate primary failure
patronictl -c /etc/patroni/patroni.yml failover

# Or switchover (planned, graceful)
patronictl -c /etc/patroni/patroni.yml switchover --leader pg-node-1 --candidate pg-node-2

# Check new cluster state
patronictl -c /etc/patroni/patroni.yml list
```

---

## The Tournament HA Setup

```
                    ┌──────────────┐
                    │   HAProxy    │
                    │ :5432 write  │
                    │ :5433 read   │
                    └──────┬───────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
   ┌─────┴─────┐    ┌─────┴─────┐    ┌─────┴─────┐
   │ pg-node-1 │    │ pg-node-2 │    │ pg-node-3 │
   │  Primary  │    │  Replica  │    │  Replica  │
   │ + Patroni │    │ + Patroni │    │ + Patroni │
   └───────────┘    └───────────┘    └───────────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                    ┌──────┴───────┐
                    │  etcd (3x)   │
                    └──────────────┘
```

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `pg_promote()` | Promote replica to primary |
| `pg_rewind` | Rewind old primary to rejoin as replica |
| `patronictl list` | Show cluster status |
| `patronictl failover` | Trigger manual failover |
| `patronictl switchover` | Planned primary switch |
| `patronictl restart` | Restart a node |

| Patroni Setting | Purpose | Recommended |
|----------------|---------|-------------|
| `ttl` | Leader lock timeout | 30s |
| `loop_wait` | Health check interval | 10s |
| `maximum_lag_on_failover` | Max lag for promotion | 1MB |
| `use_pg_rewind` | Allow old primary to rejoin | true |

| HA Component | Role |
|-------------|------|
| Patroni | Manages failover logic |
| etcd | Distributed consensus (leader election) |
| HAProxy | Routes traffic to current primary/replicas |
| pg_rewind | Resyncs old primary after failover |

---

## Exercises

### Exercise 1: Docker HA Cluster

Set up a 3-node Patroni cluster using Docker Compose with etcd. Verify:
1. Writes go to the primary
2. Reads work on replicas
3. Killing the primary triggers automatic failover

### Exercise 2: Failover Timing

Measure the actual failover time:
1. Start a loop that writes to the primary every 100ms
2. Kill the primary container
3. Measure how long until writes succeed again

### Exercise 3: Split-Brain Scenario

Simulate a network partition (disconnect the primary from etcd but not from the app). Verify that Patroni:
1. Detects the primary lost its leader lock
2. Demotes the old primary
3. Promotes a replica
4. No split-brain occurs

---

## What Happens Next

HA is configured. Failover is automatic. The tournament can survive a server crash. But Saturday morning, a developer pushes a migration:

> "ALTER TABLE matches ADD COLUMN tournament_id BIGINT..."

The migration locks the `matches` table. For 10 minutes. During the tournament. 50,000 players can't start matches.

Next chapter: zero-downtime DDL.

---

[← Chapter 14: Replication](chapter-14-replication.md) | [Chapter 16: Zero-Downtime DDL →](chapter-16-zero-downtime-ddl.md)

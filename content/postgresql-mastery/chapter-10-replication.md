[prev: Backup & Recovery](chapter-09-backup.md) | [next: None — you've completed the series!]

# Chapter 10: Replication & Clustering

## Streaming Replication (Primary/Standby)

Physical replication — the standby is an exact copy of the primary.

### Configure the Primary

In `postgresql.conf`:

```
wal_level = replica
max_wal_senders = 5
wal_keep_size = 1GB
```

Create a replication user:

```sql
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'repl_pass';
```

In `pg_hba.conf`:

```
host  replication  replicator  10.0.0.0/8  scram-sha-256
```

Reload:

```sql
SELECT pg_reload_conf();
```

### Set Up the Standby

```bash
# Take base backup from primary
pg_basebackup -h primary-host -U replicator -D /var/lib/postgresql/data \
  --wal-method=stream --checkpoint=fast -P

# Create standby signal
touch /var/lib/postgresql/data/standby.signal
```

In `postgresql.conf` on standby:

```
primary_conninfo = 'host=primary-host port=5432 user=replicator password=repl_pass'
hot_standby = on
```

Start the standby — it connects to primary and streams WAL continuously.

### Verify Replication

On primary:

```sql
SELECT client_addr, state, sent_lsn, write_lsn, flush_lsn, replay_lsn
FROM pg_stat_replication;
```

On standby:

```sql
SELECT pg_is_in_recovery();  -- should return true
SELECT pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn();
```

## Synchronous vs Asynchronous Replication

### Asynchronous (default)

Primary doesn't wait for standby to confirm. Small risk of data loss on failover.

### Synchronous

Primary waits for standby to confirm write. Zero data loss but higher latency.

On primary `postgresql.conf`:

```
synchronous_standby_names = 'standby1'
synchronous_commit = on
```

On standby, set application name in `primary_conninfo`:

```
primary_conninfo = 'host=primary-host port=5432 user=replicator password=repl_pass application_name=standby1'
```

Check sync state:

```sql
SELECT application_name, sync_state FROM pg_stat_replication;
-- sync_state: 'sync' or 'async'
```

## Read Replicas

Standbys with `hot_standby = on` accept read-only queries:

```sql
-- On standby: reads work
SELECT * FROM orders WHERE customer_id = 42;

-- Writes fail
INSERT INTO orders (customer_id, status, total) VALUES (1, 'pending', 50);
-- ERROR: cannot execute INSERT in a read-only transaction
```

Route reads to replicas in your application connection string or load balancer.

## Failover with pg_promote

When the primary fails, promote a standby:

```sql
-- On the standby
SELECT pg_promote();
```

Or from command line:

```bash
pg_ctl promote -D /var/lib/postgresql/data
```

After promotion:

- The standby becomes a new primary (read-write)
- `standby.signal` is removed
- Other standbys must be reconfigured to follow the new primary

## Patroni for High Availability

Patroni automates failover using a distributed consensus store (etcd, ZooKeeper, or Consul).

### Architecture

```
                    ┌─────────┐
                    │  etcd   │
                    └────┬────┘
           ┌─────────────┼─────────────┐
      ┌────┴────┐   ┌────┴────┐   ┌────┴────┐
      │ Patroni │   │ Patroni │   │ Patroni │
      │ Node 1  │   │ Node 2  │   │ Node 3  │
      │(primary)│   │(standby)│   │(standby)│
      └─────────┘   └─────────┘   └─────────┘
```

### Patroni config (`patroni.yml`)

```yaml
scope: pg-cluster
name: node1

restapi:
  listen: 0.0.0.0:8008

etcd3:
  hosts: etcd1:2379,etcd2:2379,etcd3:2379

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    maximum_lag_on_failover: 1048576
    synchronous_mode: true
    postgresql:
      parameters:
        max_connections: 200
        shared_buffers: 4GB

postgresql:
  listen: 0.0.0.0:5432
  data_dir: /var/lib/postgresql/data
  authentication:
    superuser:
      username: postgres
      password: secret
    replication:
      username: replicator
      password: repl_pass
```

### Patroni commands

```bash
# Check cluster status
patronictl -c /etc/patroni.yml list

# Manual switchover (planned)
patronictl -c /etc/patroni.yml switchover

# Manual failover (emergency)
patronictl -c /etc/patroni.yml failover
```

## Connection Routing

### HAProxy

Route writes to primary, reads to replicas:

```
frontend pg_write
    bind *:5432
    default_backend pg_primary

frontend pg_read
    bind *:5433
    default_backend pg_replicas

backend pg_primary
    option httpchk GET /primary
    http-check expect status 200
    server node1 10.0.0.1:5432 check port 8008
    server node2 10.0.0.2:5432 check port 8008
    server node3 10.0.0.3:5432 check port 8008

backend pg_replicas
    option httpchk GET /replica
    http-check expect status 200
    balance roundrobin
    server node1 10.0.0.1:5432 check port 8008
    server node2 10.0.0.2:5432 check port 8008
    server node3 10.0.0.3:5432 check port 8008
```

Patroni exposes HTTP endpoints (`/primary`, `/replica`) for health checks.

### PgPool-II

Built-in read/write splitting:

```
backend_hostname0 = 'primary-host'
backend_port0 = 5432
backend_weight0 = 1
backend_flag0 = 'ALWAYS_PRIMARY'

backend_hostname1 = 'standby-host'
backend_port1 = 5432
backend_weight1 = 1

load_balance_mode = on
```

## Logical Replication for Zero-Downtime Migrations

Logical replication replicates at the row level — allows different PostgreSQL versions, selective tables, and schema changes.

### Use case: upgrade from PG 14 to PG 16

On old server (PG 14):

```sql
-- Create publication
CREATE PUBLICATION migration_pub FOR ALL TABLES;
```

On new server (PG 16):

```sql
-- Create tables (same schema)
-- Then subscribe
CREATE SUBSCRIPTION migration_sub
CONNECTION 'host=old-server port=5432 dbname=myapp user=replicator password=repl_pass'
PUBLICATION migration_pub;
```

Monitor progress:

```sql
SELECT * FROM pg_stat_subscription;

-- Check replication lag
SELECT
    slot_name,
    confirmed_flush_lsn,
    pg_current_wal_lsn(),
    pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) AS lag_bytes
FROM pg_replication_slots;
```

### Cutover steps

1. Stop writes to old server
2. Wait for replication lag to reach zero
3. Drop subscription on new server: `ALTER SUBSCRIPTION migration_sub DISABLE;`
4. Point application to new server
5. Drop publication on old server

## Exercises

1. Set up streaming replication between two PostgreSQL containers

2. Verify replication lag using `pg_stat_replication`

3. Promote a standby with `pg_promote()` and confirm it accepts writes

4. Configure synchronous replication and measure the latency impact

5. Set up logical replication between two databases and replicate a single table

6. Design an HA architecture diagram for a 3-node Patroni cluster with HAProxy

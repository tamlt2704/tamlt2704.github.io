# Chapter 4: Database Separation

[← Ch 3](chapter-03-object-storage.md) | [Ch 5 →](chapter-05-caching.md)

---

## The Crisis

It's Thursday. Files are on S3. CDN is serving downloads. App servers are stateless. You're feeling good.

Then at 6:47 PM:

**Omar** (Slack, 6:47 PM):
> PostgreSQL just OOM-killed on the original server. Database is down. App is returning 500s.

**Sana**:
> The database is still running on Server 1 alongside the Django app. When traffic spiked, both fought for the same 64GB of RAM. Postgres lost.

**Amir**:
> How long to recover?

**Omar**:
> It's restarting. But the WAL is 12GB behind. Recovery will take 8-10 minutes.

**Mia** (Slack, 6:52 PM):
> We've been down for 5 minutes. Twitter is noticing.

Eight minutes later, Postgres finishes recovery. But you know this will happen again.

---

## Architecture (Before)

```
┌──────────────────────────────────────────┐
│           Server 1 (original box)         │
│                                           │
│  ┌──────────┐       ┌──────────────┐    │
│  │  Django   │       │  PostgreSQL   │    │
│  │ (app)     │       │  (database)   │    │
│  │           │       │               │    │
│  │ Uses 24GB │       │  Uses 38GB    │    │
│  └──────────┘       └──────────────┘    │
│                                           │
│         Total RAM: 64GB (62GB used)       │
│         CPU: App + DB fighting for cores  │
└──────────────────────────────────────────┘
```

## Architecture (After)

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Server 1 │     │ Server 2 │     │ Server 3 │
│ (app only)│    │ (app only)│    │ (app only)│
└─────┬────┘     └─────┬────┘     └─────┬────┘
      │                 │                 │
      └────────────┬────┴────────────────┘
                   │
                   ▼
          ┌────────────────┐
          │   RDS Postgres  │
          │  (db.r6g.xlarge)│
          │  4 vCPU, 32GB   │
          │  Multi-AZ       │
          └────────────────┘
                   │
                   ▼
          ┌────────────────┐
          │  Standby (AZ-b) │
          │  (auto-failover)│
          └────────────────┘
```

---

## Concept: Why Separate the Database?

| Problem | With DB on App Server | With Dedicated DB |
|---------|----------------------|-------------------|
| Resource contention | App and DB fight for CPU/RAM | Each gets dedicated resources |
| Scaling | Can't scale app without scaling DB | Scale independently |
| Failure blast radius | App crash can corrupt DB | Isolated failure domains |
| Backups | Must coordinate with app | Independent backup schedule |
| Maintenance | DB upgrade = app downtime | Patch DB without touching app |

---

## Concept: Managed vs Self-Managed Database

### Self-Managed (PostgreSQL on EC2)

You handle: installation, patching, backups, replication, failover, monitoring, security updates, disk management.

### Managed (AWS RDS / GCP Cloud SQL)

Provider handles: patching, backups, replication, failover, monitoring, encryption at rest.

You handle: schema design, query optimization, connection management, capacity planning.

### Cost Comparison

| | Self-Managed (EC2) | Managed (RDS) |
|---|---|---|
| Instance (r6g.xlarge) | $0.201/hr | $0.38/hr |
| Ops engineer time | 10-20 hrs/mo | 2-4 hrs/mo |
| 3 AM pages | Yes | Rare |
| Automated failover | You build it | Built in |
| Point-in-time recovery | You build it | Built in |

**GhostDrop's choice**: RDS. We have 3 weeks and no DBA. The 89% price premium buys us sleep.

---

## Concept: Connection Pooling

**Sana**: "With 3 app servers × 4 workers × 2 threads = 24 potential database connections. Is that a problem?"

Not yet. But at 10 servers × 8 workers × 2 threads = 160 connections. PostgreSQL handles each connection as a separate OS process. At 160+, you're burning RAM and context-switching.

### The Solution: PgBouncer

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Server 1 │     │ Server 2 │     │ Server 3 │
│ 24 conns │     │ 24 conns │     │ 24 conns │
└─────┬────┘     └─────┬────┘     └─────┬────┘
      │                 │                 │
      └────────────┬────┴────────────────┘
                   │  72 app connections
                   ▼
          ┌────────────────┐
          │   PgBouncer     │
          │  (connection    │
          │   pooler)       │
          └───────┬────────┘
                  │  20 actual DB connections
                  ▼
          ┌────────────────┐
          │   PostgreSQL    │
          └────────────────┘
```

### Pooling Modes

| Mode | Behavior | Use Case |
|------|----------|----------|
| **Session** | One pool conn per client session | Need session-level features (LISTEN/NOTIFY) |
| **Transaction** | Conn returned after each transaction | Most web apps (GhostDrop) |
| **Statement** | Conn returned after each statement | Simple queries, no transactions |

```ini
# pgbouncer.ini
[databases]
ghostdrop = host=ghostdrop-db.rds.amazonaws.com port=5432 dbname=ghostdrop

[pgbouncer]
pool_mode = transaction
max_client_conn = 200
default_pool_size = 20
min_pool_size = 5
reserve_pool_size = 5
```

---

## Concept: Right-Sizing the Database

### How to Choose Instance Size

```
Current metrics:
  - Active connections: 24
  - Database size: 45GB
  - Peak queries/sec: 2,800
  - Working set (hot data): ~8GB
  - Write throughput: 500 writes/sec

Rule of thumb:
  - RAM should be 2-3x your working set
  - CPU cores ≈ peak connections / 4
  - IOPS = write throughput × 2 (WAL + data)
```

### GhostDrop's Choice

```
db.r6g.xlarge:
  - 4 vCPU (handles 24 connections easily)
  - 32GB RAM (4x the 8GB working set)
  - 3000 baseline IOPS (gp3)
  - $0.38/hr = ~$277/mo

Headroom for 10M users:
  - Can scale to db.r6g.4xlarge (16 vCPU, 128GB) without migration
  - Can add read replicas later (Chapter 7)
```

---

## Concept: Backup Strategy

**Omar**: "What's our RPO and RTO?"

| Term | Meaning | GhostDrop Target |
|------|---------|-----------------|
| **RPO** (Recovery Point Objective) | Max data loss you accept | 5 minutes |
| **RTO** (Recovery Time Objective) | Max downtime you accept | 2 minutes |

### RDS Backup Configuration

```yaml
# Automated backups
backup_retention_period: 7        # Keep 7 days of backups
backup_window: "03:00-04:00"      # Run at 3 AM UTC
copy_tags_to_snapshot: true

# Point-in-time recovery
# RDS continuously backs up transaction logs
# Can restore to any second within retention period

# Multi-AZ (synchronous replication)
multi_az: true
# Automatic failover in 60-120 seconds
```

### Backup Layers

```
Layer 1: Multi-AZ synchronous replica (RTO: ~60s, RPO: 0)
Layer 2: Continuous WAL archiving (RPO: ~5 min for PITR)
Layer 3: Daily automated snapshots (RPO: 24 hours)
Layer 4: Manual snapshots before migrations (RPO: on-demand)
```

---

## The Migration Plan

Zero-downtime database migration from local Postgres to RDS:

```
Step 1: Create RDS instance, set up as replica of local Postgres
        (uses logical replication)

Step 2: Wait for replica to catch up (replication lag → 0)

Step 3: Enable maintenance mode (read-only for 30 seconds)

Step 4: Verify replica is fully caught up

Step 5: Update app server connection strings to point to RDS

Step 6: Disable maintenance mode

Step 7: Verify everything works

Step 8: Decommission local Postgres

Total downtime: ~30 seconds (Step 3-6)
```

```python
# settings.py — the switch
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.environ.get('DB_HOST'),  # Changed from localhost to RDS endpoint
        'PORT': 5432,
        'NAME': 'ghostdrop',
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'CONN_MAX_AGE': 600,  # Connection reuse
        'OPTIONS': {
            'sslmode': 'require',
        }
    }
}
```

---

## Tradeoffs

| Decision | Gain | Cost |
|----------|------|------|
| Managed DB (RDS) | No ops burden, automated failover | 89% price premium over EC2 |
| Multi-AZ | Zero RPO, ~60s RTO | 2x the instance cost |
| Connection pooling | Handle 200+ app connections with 20 DB connections | Another component (PgBouncer) |
| Separate DB server | Independent scaling, isolated failures | ~1ms network latency per query |

---

## Why Not Just...

**"Why not just give the server more RAM?"**
You'd delay the problem by a week. And you still have a single point of failure with no automated failover.

**"Why not use Aurora instead of RDS PostgreSQL?"**
Aurora is great but costs 20-40% more. At GhostDrop's current scale, standard RDS is sufficient. Aurora shines at very high write throughput and when you need 15 read replicas.

**"Why not use a NoSQL database?"**
GhostDrop's data is relational (users have files, files have shares, shares have permissions). PostgreSQL handles this naturally. NoSQL would mean denormalizing everything and losing ACID transactions.

**"Why add PgBouncer? Django has CONN_MAX_AGE."**
CONN_MAX_AGE reuses connections within a single worker process. It doesn't pool across workers or servers. At 10 servers × 8 workers, you'd still open 80 persistent connections. PgBouncer multiplexes them down to 20.

---

## Exercise

GhostDrop's database is 45GB today. At the current growth rate, it'll be 200GB in 6 months. The working set (frequently accessed data) is only 8GB.

1. What happens when the working set exceeds available RAM?
2. How would you keep the working set small? (Hint: archiving, partitioning)
3. At what point would you consider read replicas vs a bigger instance?

<details>
<summary>Hint</summary>

When working set > RAM, PostgreSQL starts reading from disk instead of the buffer cache. Query latency jumps from microseconds to milliseconds. Solutions: (1) Partition tables by date, archive old data to cold storage. (2) Add read replicas when read traffic is 5-10x write traffic. (3) Scale up RAM when the working set grows but is still actively needed.
</details>

---

## Quick Reference

| Term | Definition |
|------|-----------|
| **Managed Database** | Cloud provider handles ops (patching, backups, failover) |
| **Connection Pooling** | Multiplex many app connections into fewer DB connections |
| **Multi-AZ** | Synchronous replica in another availability zone |
| **RPO** | Recovery Point Objective — max acceptable data loss |
| **RTO** | Recovery Time Objective — max acceptable downtime |
| **Working Set** | The subset of data frequently accessed (should fit in RAM) |
| **WAL** | Write-Ahead Log — Postgres's transaction journal |
| **PITR** | Point-In-Time Recovery — restore to any second |

---

## What Breaks Next

Database is on RDS. Multi-AZ. Automated backups. Connection pooling in place. The app servers are truly stateless now.

Monday morning, traffic spikes. Every page load hits the database: user profile, file list, share permissions, storage quota. 2,800 queries/second. The database CPU hits 80%.

Sana: "80% of these queries return the same data. User profiles don't change every second. Why are we hitting the database every time?"

You need caching.

[← Ch 3](chapter-03-object-storage.md) | [Ch 5 →](chapter-05-caching.md)

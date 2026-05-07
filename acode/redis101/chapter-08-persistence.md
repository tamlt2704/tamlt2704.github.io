# Chapter 8: The Server Crashes — Persistence

[← Chapter 7: Distributed Locks](chapter-07-distributed-locks.md) | [Chapter 9: Replication →](chapter-09-replication.md)

---

## The Problem

3 AM. The Redis server runs out of memory. OOM killer terminates the process. When it restarts, the leaderboard is empty. 2 million player scores — gone. The matchmaking queue — gone. Rate limit counters — gone.

Ops Olga: "I told you. RAM is volatile. We need persistence."

CEO Chad, the next morning: "Players are furious. The leaderboard reset. Fix this. Today."

## The Two Persistence Mechanisms

Redis has two ways to survive a restart:

1. **RDB (Redis Database)** — periodic point-in-time snapshots
2. **AOF (Append-Only File)** — log of every write operation

They solve different problems. Most production deployments use both.

## RDB: Snapshots

RDB saves the entire dataset to a binary file (`dump.rdb`) at configured intervals. Like taking a photo of your data every N minutes.

### Configuration

```
# redis.conf
save 900 1      # Save if at least 1 key changed in 900 seconds (15 min)
save 300 10     # Save if at least 10 keys changed in 300 seconds (5 min)
save 60 10000   # Save if at least 10,000 keys changed in 60 seconds (1 min)

dbfilename dump.rdb
dir /data/redis/
```

### How It Works

1. Redis forks the process (copy-on-write)
2. The child process writes the entire dataset to a temp file
3. When done, it atomically replaces the old `dump.rdb`
4. The parent continues serving requests — zero downtime

```redis
# Trigger a manual snapshot
BGSAVE
# Background saving started

# Check last save time
LASTSAVE
# (integer) 1705312800

# Blocking save (DON'T use in production — freezes the server)
SAVE
```

### RDB Pros and Cons

| Pros | Cons |
|---|---|
| Compact binary file | Data loss between snapshots |
| Fast restart (just load the file) | Fork can be slow with large datasets |
| Perfect for backups | Not suitable for zero-data-loss |
| Low runtime overhead | Child process doubles memory briefly |

**Data loss window:** If Redis crashes 4 minutes after the last snapshot (with `save 300 10`), you lose 4 minutes of writes. For the leaderboard, that's 4 minutes of score updates gone.

### RDB for Backups

```bash
# Copy the RDB file for backup (safe — Redis writes atomically)
cp /data/redis/dump.rdb /backups/redis-$(date +%Y%m%d-%H%M%S).rdb

# Restore from backup
docker stop redis-dev
cp /backups/redis-20240115-030000.rdb /data/redis/dump.rdb
docker start redis-dev
# Redis loads the RDB on startup
```

## AOF: Append-Only File

AOF logs every write command to a file. On restart, Redis replays the log to reconstruct the dataset. Like a transaction log.

### Configuration

```
# redis.conf
appendonly yes
appendfilename "appendonly.aof"
appenddirname "appendonlydir"

# Sync policy:
# appendfsync always    — fsync after every write (safest, slowest)
# appendfsync everysec  — fsync once per second (good compromise)
# appendfsync no        — let the OS decide (fastest, riskiest)
appendfsync everysec
```

### How It Works

Every write command is appended to the AOF:

```
*3\r\n$3\r\nSET\r\n$5\r\nhello\r\n$5\r\nworld\r\n
*3\r\n$4\r\nINCR\r\n$7\r\ncounter\r\n
*4\r\n$4\r\nZADD\r\n$11\r\nleaderboard\r\n$4\r\n1500\r\n$5\r\nalice\r\n
```

On restart, Redis replays these commands in order. The dataset is reconstructed exactly.

### fsync Policies

| Policy | Data Loss | Performance | Use Case |
|---|---|---|---|
| `always` | Zero (every write fsynced) | Slowest (~1000 ops/s) | Financial data |
| `everysec` | Up to 1 second | Good (~100K ops/s) | Most applications |
| `no` | Up to 30 seconds (OS buffer) | Fastest | Ephemeral data |

For PingPong: `everysec`. Losing 1 second of leaderboard updates is acceptable. Losing 15 minutes (RDB only) is not.

### AOF Rewrite

The AOF grows forever. After 1 million INCRs on the same key, the file has 1 million lines — but the current value is just one number. AOF rewrite compacts it:

```redis
BGREWRITEAOF
# Rewrites the AOF with the minimal set of commands to reproduce current state
```

Auto-rewrite configuration:

```
# Rewrite when AOF is 100% larger than last rewrite
auto-aof-rewrite-percentage 100
# Don't rewrite if AOF is smaller than 64MB
auto-aof-rewrite-min-size 64mb
```

After rewrite: 1 million INCRs become one `SET counter 1000000`. File shrinks dramatically.

### AOF Pros and Cons

| Pros | Cons |
|---|---|
| Minimal data loss (1 second with everysec) | Larger file than RDB |
| Human-readable (it's just commands) | Slower restart (replays commands) |
| Append-only (no corruption from partial writes) | Higher I/O during operation |
| Can be repaired if corrupted | AOF rewrite uses memory |

## Hybrid: RDB + AOF (Recommended)

Use both. AOF for durability (minimal data loss). RDB for fast restarts and backups.

```
# redis.conf — production configuration
save 900 1
save 300 10
save 60 10000

appendonly yes
appendfsync everysec
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Use RDB preamble in AOF (Redis 7 default)
aof-use-rdb-preamble yes
```

`aof-use-rdb-preamble yes` means the AOF file starts with an RDB snapshot, followed by the commands since that snapshot. Restart is fast (load RDB portion) and data loss is minimal (replay recent commands).

### Restart Priority

When both RDB and AOF exist, Redis loads the AOF (it's more complete). The RDB is used for backups and as the preamble inside the AOF.

## Docker Configuration

```bash
# Create a persistent Redis container
docker run -d --name redis-prod \
  -p 6379:6379 \
  -v redis-data:/data \
  redis:7-alpine \
  redis-server --appendonly yes --appendfsync everysec \
  --save 900 1 --save 300 10 --save 60 10000
```

The `-v redis-data:/data` mounts a Docker volume. Data survives container restarts.

### Verify Persistence

```bash
# Write some data
docker exec -it redis-prod redis-cli SET test:persistence "it works"

# Kill the container (simulates crash)
docker kill redis-prod

# Restart
docker start redis-prod

# Check if data survived
docker exec -it redis-prod redis-cli GET test:persistence
# "it works" ← survived the crash
```

## Memory Management

Redis lives in RAM. When memory runs out, bad things happen. Configure limits:

```
# redis.conf
maxmemory 4gb

# What to do when memory is full:
# maxmemory-policy noeviction     — reject writes (safest)
# maxmemory-policy allkeys-lru    — evict least recently used keys
# maxmemory-policy volatile-lru   — evict LRU keys WITH an expiry set
# maxmemory-policy allkeys-lfu    — evict least frequently used keys
# maxmemory-policy volatile-ttl   — evict keys closest to expiry
maxmemory-policy allkeys-lfu
```

### Eviction Policies for PingPong

| Data | Policy | Reasoning |
|---|---|---|
| Cache (profiles, configs) | `volatile-lru` | Evict cached data first (has TTL) |
| Leaderboard (sorted sets) | `noeviction` | Never evict — this IS the data |
| Rate limit counters | `volatile-ttl` | Evict counters closest to expiry |

If you mix critical data (leaderboard) with cache (profiles) in the same instance, use `volatile-lru` — it only evicts keys with a TTL set. Your leaderboard (no TTL) is safe. Your cached profiles (with TTL) get evicted when memory is tight.

Better approach: separate Redis instances for different purposes.

## Monitoring Persistence

```redis
INFO persistence
# rdb_last_save_time:1705312800
# rdb_last_bgsave_status:ok
# rdb_last_bgsave_time_sec:2
# aof_enabled:1
# aof_last_rewrite_time_sec:1
# aof_last_write_status:ok
# aof_current_size:52428800
# aof_base_size:26214400

INFO memory
# used_memory_human:2.1G
# maxmemory_human:4G
# mem_fragmentation_ratio:1.05
```

Set up alerts for:
- `rdb_last_bgsave_status` != ok
- `aof_last_write_status` != ok
- `used_memory` > 80% of `maxmemory`
- `rdb_last_save_time` older than expected

## Disaster Recovery Checklist

1. **RDB backups** — copy to remote storage (S3, GCS) every hour
2. **AOF enabled** — with `everysec` fsync
3. **Memory limit** — set `maxmemory` below physical RAM
4. **Eviction policy** — appropriate for your data mix
5. **Monitoring** — alert on persistence failures
6. **Test restores** — regularly verify backups actually work

```bash
# Backup script (run via cron every hour)
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
docker exec redis-prod redis-cli BGSAVE
sleep 5  # Wait for save to complete
docker cp redis-prod:/data/dump.rdb /backups/redis-${TIMESTAMP}.rdb
aws s3 cp /backups/redis-${TIMESTAMP}.rdb s3://pingpong-backups/redis/
# Keep only last 24 local backups
ls -t /backups/redis-*.rdb | tail -n +25 | xargs rm -f
```

## What You Learned

- **RDB** — periodic snapshots (fast restart, data loss between saves)
- **AOF** — append-only log (minimal data loss, slower restart)
- **Hybrid** — RDB + AOF with RDB preamble (best of both)
- **fsync policies** — always/everysec/no (durability vs performance)
- **AOF rewrite** — compact the log file
- **maxmemory** — prevent OOM kills
- **Eviction policies** — what to delete when memory is full
- **Backup strategy** — RDB to remote storage

The leaderboard survives crashes now. 1 second of data loss maximum. Ops Olga sleeps slightly better.

But she has another concern: "One Redis server is a single point of failure. If it dies, the entire platform is down until it restarts and loads the AOF. We need redundancy."

That's Chapter 9.

---

[← Chapter 7: Distributed Locks](chapter-07-distributed-locks.md) | [Chapter 9: Replication →](chapter-09-replication.md)

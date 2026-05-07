# Chapter 9: One Server Isn't Enough — Replication and Sentinel

[← Chapter 8: Persistence](chapter-08-persistence.md) | [Chapter 10: Clustering →](chapter-10-clustering.md)

---

## The Problem

Tuesday, 2 PM. The Redis server's SSD fails. The process dies. AOF is on the dead disk. RDB backup is 45 minutes old. It takes 20 minutes to provision a new server, restore the backup, and replay the AOF from the remote copy.

For 20 minutes, PingPong is completely down. No leaderboard. No matchmaking. No chat. 200,000 players see error screens.

Ops Olga: "One server is a single point of failure. We need replicas. And we need automatic failover."

## Replication: Read Replicas

Redis replication is simple: one primary (master) handles all writes. One or more replicas (slaves) receive a copy of every write and serve read traffic.

```
         Writes                    Reads
           │                    ┌────────┐
           ▼                    │        ▼
      ┌─────────┐         ┌─────────┐  ┌─────────┐
      │ Primary │────────►│Replica 1│  │Replica 2│
      │ (write) │────────►│ (read)  │  │ (read)  │
      └─────────┘         └─────────┘  └─────────┘
```

### Setting Up Replication

```bash
# Start primary
docker run -d --name redis-primary -p 6379:6379 \
  -v redis-primary-data:/data \
  redis:7-alpine redis-server --appendonly yes

# Start replica 1
docker run -d --name redis-replica1 -p 6380:6379 \
  redis:7-alpine redis-server --replicaof redis-primary 6379

# Start replica 2
docker run -d --name redis-replica2 -p 6381:6379 \
  redis:7-alpine redis-server --replicaof redis-primary 6379
```

Or with Docker Compose:

```yaml
# docker-compose.yml
services:
  redis-primary:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    ports:
      - "6379:6379"
    volumes:
      - redis-primary-data:/data

  redis-replica1:
    image: redis:7-alpine
    command: redis-server --replicaof redis-primary 6379
    ports:
      - "6380:6379"
    depends_on:
      - redis-primary

  redis-replica2:
    image: redis:7-alpine
    command: redis-server --replicaof redis-primary 6379
    ports:
      - "6381:6379"
    depends_on:
      - redis-primary

volumes:
  redis-primary-data:
```

### Verify Replication

```bash
# Write to primary
docker exec redis-primary redis-cli SET test:replication "hello from primary"

# Read from replica
docker exec redis-replica1 redis-cli GET test:replication
# "hello from primary" ← replicated!

# Check replication status
docker exec redis-primary redis-cli INFO replication
# role:master
# connected_slaves:2
# slave0:ip=172.18.0.3,port=6379,state=online,offset=1234,lag=0
# slave1:ip=172.18.0.4,port=6379,state=online,offset=1234,lag=0
```

### How Replication Works

1. Replica connects to primary and sends `REPLICAOF`
2. Primary starts a BGSAVE (RDB snapshot)
3. Primary sends the RDB to the replica (full sync)
4. From then on, primary streams every write command to replicas (partial sync)
5. If connection drops briefly, replica requests only the missed commands (partial resync)
6. If too much was missed, full resync happens again

### Read Scaling

Route read traffic to replicas, writes to primary:

```python
from redis import Redis
from redis.sentinel import Sentinel
import random

primary = Redis(host='redis-primary', port=6379)
replicas = [
    Redis(host='redis-replica1', port=6379),
    Redis(host='redis-replica2', port=6379),
]

def write(key, value, **kwargs):
    """All writes go to primary."""
    return primary.set(key, value, **kwargs)

def read(key):
    """Reads are distributed across replicas."""
    replica = random.choice(replicas)
    return replica.get(key)
```

For PingPong's leaderboard: writes (score updates) go to primary. Reads (viewing the leaderboard) go to replicas. With 2 replicas, you triple your read capacity.

### Replication Lag

Replication is asynchronous by default. There's a small delay (usually <1ms on the same network) between a write on the primary and its appearance on replicas.

```redis
# On primary
INFO replication
# slave0:...,lag=0   ← lag in seconds (0 = caught up)
```

This means: a player scores, then immediately checks the leaderboard on a replica — they might not see their new score for a few milliseconds. For PingPong, this is fine. For banking, it's not.

### Read-After-Write Consistency

If a player must see their own writes immediately:

```python
def update_and_read_score(player_id: str, points: int):
    # Write to primary
    primary.zincrby("leaderboard:global", points, player_id)

    # Read from PRIMARY (not replica) for this specific request
    return primary.zscore("leaderboard:global", player_id)
```

Route the user's own data reads to primary. Route everyone else's reads to replicas.

## Sentinel: Automatic Failover

Replicas are great for reads, but if the primary dies, you're stuck. Writes fail. You need someone to promote a replica to primary automatically.

Redis Sentinel monitors your Redis instances and performs automatic failover:

1. Detects when the primary is down
2. Promotes a replica to primary
3. Reconfigures other replicas to follow the new primary
4. Notifies clients of the topology change

### Setting Up Sentinel

```bash
# sentinel.conf
port 26379
sentinel monitor pingpong-redis redis-primary 6379 2
sentinel down-after-milliseconds pingpong-redis 5000
sentinel failover-timeout pingpong-redis 10000
sentinel parallel-syncs pingpong-redis 1
```

- `monitor pingpong-redis redis-primary 6379 2` — monitor this primary, need 2 sentinels to agree it's down
- `down-after-milliseconds 5000` — consider it down after 5s of no response
- `failover-timeout 10000` — failover must complete within 10s
- `parallel-syncs 1` — only 1 replica resyncs at a time (reduces load)

Run 3 Sentinel instances (odd number for quorum):

```yaml
# docker-compose.yml (add to previous)
  sentinel1:
    image: redis:7-alpine
    command: redis-sentinel /etc/redis/sentinel.conf
    volumes:
      - ./sentinel.conf:/etc/redis/sentinel.conf
    depends_on:
      - redis-primary
      - redis-replica1
      - redis-replica2

  sentinel2:
    image: redis:7-alpine
    command: redis-sentinel /etc/redis/sentinel.conf
    volumes:
      - ./sentinel.conf:/etc/redis/sentinel.conf

  sentinel3:
    image: redis:7-alpine
    command: redis-sentinel /etc/redis/sentinel.conf
    volumes:
      - ./sentinel.conf:/etc/redis/sentinel.conf
```

### Connecting Through Sentinel

Clients don't connect to Redis directly. They ask Sentinel "who is the current primary?"

```python
from redis.sentinel import Sentinel

sentinel = Sentinel([
    ('sentinel1', 26379),
    ('sentinel2', 26379),
    ('sentinel3', 26379),
], socket_timeout=0.5)

# Get a connection to the current primary
primary = sentinel.master_for('pingpong-redis', socket_timeout=0.5)
primary.set("key", "value")

# Get a connection to a replica (for reads)
replica = sentinel.slave_for('pingpong-redis', socket_timeout=0.5)
replica.get("key")
```

If the primary fails, Sentinel promotes a replica. The `master_for()` connection automatically discovers the new primary. Your application doesn't need to change anything.

### Simulating Failover

```bash
# Kill the primary
docker stop redis-primary

# Watch Sentinel logs
docker logs -f sentinel1
# +sdown master pingpong-redis 172.18.0.2 6379
# +odown master pingpong-redis 172.18.0.2 6379 #quorum 2/2
# +try-failover master pingpong-redis 172.18.0.2 6379
# +elected-leader master pingpong-redis 172.18.0.2 6379
# +promoted-slave slave 172.18.0.3:6379 172.18.0.3 6379
# +switch-master pingpong-redis 172.18.0.2 6379 172.18.0.3 6379

# Replica 1 is now the primary!
docker exec redis-replica1 redis-cli INFO replication
# role:master
# connected_slaves:1
```

Failover takes ~5-10 seconds. During that window, writes fail. Your application should retry with backoff.

### Handling Failover in Application Code

```python
from redis.exceptions import ConnectionError, ReadOnlyError
import time

def write_with_retry(key: str, value: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            primary = sentinel.master_for('pingpong-redis')
            primary.set(key, value)
            return True
        except (ConnectionError, ReadOnlyError):
            # Primary is down or we connected to a stale primary
            time.sleep(1 * (attempt + 1))  # Linear backoff
    return False
```

`ReadOnlyError` happens when you write to what you think is the primary, but it's been demoted to a replica. The Sentinel client will rediscover the new primary on the next attempt.

## Replication Topology Decisions

| Setup | Replicas | Sentinels | Use Case |
|---|---|---|---|
| 1 primary, 0 replicas | 0 | 0 | Development only |
| 1 primary, 1 replica | 1 | 3 | Small production |
| 1 primary, 2 replicas | 2 | 3 | Standard production |
| 1 primary, N replicas | N | 3-5 | Read-heavy workloads |

For PingPong: 1 primary + 2 replicas + 3 sentinels. Reads scale to 3x. Automatic failover in <10 seconds.

## What You Learned

- **Replication** — primary handles writes, replicas serve reads
- **Async replication** — small lag between primary and replicas
- **Read scaling** — distribute reads across replicas
- **Read-after-write** — route own-data reads to primary
- **Sentinel** — automatic failover when primary dies
- **Quorum** — majority of sentinels must agree before failover
- **Client discovery** — `master_for()` / `slave_for()` auto-routing
- **Failover handling** — retry with backoff on ConnectionError

PingPong now survives a server failure with <10 seconds of downtime. Reads scale across replicas. Ops Olga is cautiously optimistic.

But CEO Chad just announced: "We're launching in Asia next month. 10 million users. The current setup maxes out at 16GB of RAM." One primary can't hold all the data. You need to split it across multiple nodes.

That's Chapter 10.

---

[← Chapter 8: Persistence](chapter-08-persistence.md) | [Chapter 10: Clustering →](chapter-10-clustering.md)

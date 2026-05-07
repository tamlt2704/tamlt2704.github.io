# Chapter 12: Black Friday — Production Tuning

[← Chapter 11: Operational Safety](chapter-11-operational-safety.md)

---

## The Problem

CEO Chad's Asia launch is in 3 days. Expected load: 10 million users, 100,000 operations per second at peak. Current setup handles 45,000 ops/sec before latency spikes.

Ops Olga: "We need to squeeze every bit of performance out of this cluster. Connection pooling, pipeline optimization, memory tuning, the works."

Marta: "And we need to know when things go wrong before the players do."

## Connection Pooling

Every Redis command needs a TCP connection. Opening a new connection per request is expensive (~1ms handshake). Connection pools maintain a set of open connections and reuse them.

```python
import redis

# BAD: new connection per request
def get_score_bad(player_id):
    r = redis.Redis(host='redis-primary', port=6379)  # New connection!
    return r.zscore("leaderboard:global", player_id)
    # Connection closed when r goes out of scope

# GOOD: shared connection pool
pool = redis.ConnectionPool(
    host='redis-primary',
    port=6379,
    max_connections=50,        # Max 50 concurrent connections
    socket_timeout=5,          # Timeout for operations
    socket_connect_timeout=2,  # Timeout for connecting
    retry_on_timeout=True,     # Auto-retry on timeout
    decode_responses=True
)

r = redis.Redis(connection_pool=pool)

def get_score_good(player_id):
    return r.zscore("leaderboard:global", player_id)
    # Connection returned to pool, not closed
```

### Pool Sizing

```
Optimal pool size = (number of concurrent requests) / (average Redis call duration)
```

If your API handles 1,000 concurrent requests and each Redis call takes 0.5ms:
- Each connection handles ~2,000 ops/sec
- You need ~50 connections to handle 100,000 ops/sec

Too few connections: requests queue waiting for a connection.
Too many connections: Redis `maxclients` limit hit, memory wasted on idle connections.

```
# redis.conf
maxclients 10000
# Default is 10,000. Each connection uses ~10KB of memory.
```

### Connection Pool per Service

```python
# Separate pools for different access patterns
write_pool = redis.ConnectionPool(host='redis-primary', port=6379, max_connections=20)
read_pool = redis.ConnectionPool(host='redis-replica1', port=6379, max_connections=100)

writer = redis.Redis(connection_pool=write_pool)
reader = redis.Redis(connection_pool=read_pool)
```

Reads are more frequent (leaderboard views) — give them more connections. Writes are less frequent but latency-sensitive — fewer connections, dedicated pool.

## Pipeline Optimization

You already know pipelines reduce round-trips. But there's a sweet spot:

```python
# Too many commands in one pipeline can block the server
# Rule of thumb: 100-1000 commands per pipeline

def bulk_update_scores(updates: list[tuple[str, int]]):
    """Update scores in batches of 500."""
    BATCH_SIZE = 500
    for i in range(0, len(updates), BATCH_SIZE):
        batch = updates[i:i + BATCH_SIZE]
        pipe = r.pipeline(transaction=False)  # No MULTI/EXEC overhead
        for player_id, score_delta in batch:
            pipe.zincrby("leaderboard:global", score_delta, player_id)
        pipe.execute()
```

`transaction=False` skips the MULTI/EXEC wrapper. You don't need atomicity for independent score updates — and skipping it is faster.

### Pipeline vs Transaction

| Feature | Pipeline (`transaction=False`) | Transaction (`transaction=True`) |
|---|---|---|
| Atomicity | No | Yes (all-or-nothing) |
| Performance | Faster (no MULTI/EXEC) | Slightly slower |
| Use case | Independent operations | Operations that must succeed together |

## Memory Optimization

### Key Naming: Shorter Is Cheaper

Every key name is stored in memory. With 10 million keys, naming matters:

```python
# BAD: verbose keys (wastes memory)
"player:profile:username:alice:score:current"  # 47 bytes per key name

# GOOD: compact keys
"p:42:s"  # 6 bytes per key name
# p = player, 42 = ID, s = score
```

With 10 million keys: 47 bytes × 10M = 470MB just for key names vs 6 bytes × 10M = 60MB. That's 410MB saved.

**Tradeoff:** Readability. Use a mapping document and consistent conventions.

### Value Encoding: Use the Right Type

```redis
# BAD: storing a number as a long string
SET player:42:score "one thousand five hundred"

# GOOD: store as integer (Redis optimizes small integers)
SET player:42:score 1500
# Redis internally shares integer objects for values 0-9999
```

### Hash Compression

Small hashes (< 128 fields, values < 64 bytes) use `listpack` encoding — significantly more memory-efficient than the hash table encoding.

```
# redis.conf
hash-max-listpack-entries 128
hash-max-listpack-value 64

# For sorted sets
zset-max-listpack-entries 128
zset-max-listpack-value 64

# For lists
list-max-listpack-size -2  # 8KB per node
```

### Memory Analysis

```redis
MEMORY USAGE player:42
# (integer) 256  — bytes used by this key

MEMORY DOCTOR
# Reports memory issues and recommendations

INFO memory
# used_memory_human:8.2G
# used_memory_rss_human:8.8G
# mem_fragmentation_ratio:1.07  — healthy (< 1.5)
# mem_allocator:jemalloc-5.3.0
```

### Defragmentation

Over time, memory becomes fragmented (small gaps between allocations). Redis 4+ has active defragmentation:

```
# redis.conf
activedefrag yes
active-defrag-ignore-bytes 100mb
active-defrag-threshold-lower 10    # Start when fragmentation > 10%
active-defrag-threshold-upper 100   # Max effort when fragmentation > 100%
active-defrag-cycle-min 1           # Min CPU % for defrag
active-defrag-cycle-max 25          # Max CPU % for defrag
```

## Latency Optimization

### Disable Transparent Huge Pages (Linux)

THP causes latency spikes during fork (RDB save, AOF rewrite):

```bash
echo never > /sys/kernel/mm/transparent_hugepage/enabled
echo never > /sys/kernel/mm/transparent_hugepage/defrag
```

### TCP Backlog

```
# redis.conf
tcp-backlog 511
# Increase if you see connection refused under load
```

```bash
# Linux kernel setting (must match or exceed Redis setting)
sysctl -w net.core.somaxconn=511
```

### Lazy Freeing

When deleting large keys, do it in the background:

```
# redis.conf
lazyfree-lazy-eviction yes
lazyfree-lazy-expire yes
lazyfree-lazy-server-del yes
replica-lazy-flush yes
```

Large key deletion (a sorted set with 1 million members) happens in a background thread instead of blocking the main event loop.

### IO Threads (Redis 6+)

Redis is single-threaded for command execution, but can use multiple threads for I/O (reading from sockets, writing responses):

```
# redis.conf
io-threads 4              # Use 4 threads for I/O
io-threads-do-reads yes   # Also use threads for reading
```

This helps when the bottleneck is network I/O, not command execution. Typical improvement: 2-3x throughput for simple commands.

## Benchmarking

### redis-benchmark

```bash
# Basic benchmark
redis-benchmark -h redis-primary -p 6379 -c 50 -n 100000
# 50 concurrent clients, 100,000 requests

# Specific commands
redis-benchmark -h redis-primary -p 6379 -c 100 -n 1000000 -t set,get,zadd,zrange
# Results:
# SET: 125,000 ops/sec
# GET: 145,000 ops/sec
# ZADD: 110,000 ops/sec
# ZRANGE (top 10): 95,000 ops/sec

# Pipeline benchmark
redis-benchmark -h redis-primary -p 6379 -c 50 -n 1000000 -P 16
# Pipeline 16 commands per round-trip
# SET: 850,000 ops/sec (7x improvement!)
```

### Custom Benchmark for PingPong

```python
import time
import redis
from concurrent.futures import ThreadPoolExecutor

r = redis.Redis(host='redis-primary', port=6379, decode_responses=True)

def benchmark_leaderboard_read(iterations=10000):
    start = time.time()
    for _ in range(iterations):
        r.zrange("leaderboard:global", 0, 9, desc=True, withscores=True)
    elapsed = time.time() - start
    print(f"Leaderboard reads: {iterations/elapsed:.0f} ops/sec, avg {elapsed/iterations*1000:.2f}ms")

def benchmark_score_update(iterations=10000):
    start = time.time()
    pipe = r.pipeline(transaction=False)
    for i in range(iterations):
        pipe.zincrby("leaderboard:global", 1, f"player_{i % 1000}")
        if i % 100 == 0:
            pipe.execute()
            pipe = r.pipeline(transaction=False)
    pipe.execute()
    elapsed = time.time() - start
    print(f"Score updates: {iterations/elapsed:.0f} ops/sec, avg {elapsed/iterations*1000:.2f}ms")

def benchmark_concurrent(num_threads=50, ops_per_thread=1000):
    start = time.time()
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(benchmark_leaderboard_read, ops_per_thread)
                   for _ in range(num_threads)]
        for f in futures:
            f.result()
    elapsed = time.time() - start
    total_ops = num_threads * ops_per_thread
    print(f"Concurrent: {total_ops/elapsed:.0f} ops/sec across {num_threads} threads")
```

## Production Configuration: The Full redis.conf

```
# Network
bind 10.0.1.0
port 6379
tcp-backlog 511
timeout 300
tcp-keepalive 60

# Security
requirepass YourProductionPassword
aclfile /etc/redis/users.acl
rename-command FLUSHALL ""
rename-command FLUSHDB ""
rename-command KEYS ""
rename-command DEBUG ""

# Memory
maxmemory 12gb
maxmemory-policy allkeys-lfu
activedefrag yes

# Persistence
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec
aof-use-rdb-preamble yes
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Performance
io-threads 4
io-threads-do-reads yes
lazyfree-lazy-eviction yes
lazyfree-lazy-expire yes
lazyfree-lazy-server-del yes

# Logging
loglevel notice
logfile /var/log/redis/redis.log
slowlog-log-slower-than 10000
slowlog-max-len 128

# Clients
maxclients 10000
```

## Observability Stack

### Prometheus + Grafana

Export Redis metrics to Prometheus using `redis_exporter`:

```yaml
# docker-compose addition
  redis-exporter:
    image: oliver006/redis_exporter:latest
    environment:
      - REDIS_ADDR=redis://redis-primary:6379
      - REDIS_PASSWORD=YourProductionPassword
    ports:
      - "9121:9121"
```

Key Grafana dashboards:
- Operations per second (by command type)
- Memory usage and fragmentation
- Connected clients
- Hit rate (hits / (hits + misses))
- Replication lag
- Slowlog entries per minute

### Health Check Endpoint

```python
@app.route("/health/redis")
def redis_health():
    try:
        start = time.time()
        r.ping()
        latency = (time.time() - start) * 1000

        info = r.info(section="memory")
        memory_pct = info["used_memory"] / info.get("maxmemory", float("inf")) * 100

        return jsonify({
            "status": "healthy" if latency < 10 else "degraded",
            "latency_ms": round(latency, 2),
            "memory_used_pct": round(memory_pct, 1),
            "connected_clients": r.info("clients")["connected_clients"]
        })
    except redis.ConnectionError:
        return jsonify({"status": "down"}), 503
```

## Load Testing Results

After all optimizations, PingPong's Redis cluster handles:

| Operation | Throughput | P50 Latency | P99 Latency |
|---|---|---|---|
| GET (cached profile) | 180,000 ops/sec | 0.2ms | 0.8ms |
| ZRANGE (top 10) | 120,000 ops/sec | 0.3ms | 1.2ms |
| ZINCRBY (score update) | 150,000 ops/sec | 0.2ms | 0.9ms |
| XADD (chat message) | 130,000 ops/sec | 0.3ms | 1.0ms |
| Pipeline (10 cmds) | 500,000 ops/sec | 0.5ms | 2.0ms |

100,000 ops/sec target: achieved with headroom.

## The Launch

Asia launch day. 10 million users come online over 6 hours. The Redis cluster handles it without a single alert. Leaderboard loads in 2ms. Matchmaking pairs players in under 1 second. Chat messages arrive instantly.

Ops Olga, for the first time in months: "Everything is green."

CEO Chad: "See? I told you we could do it."

Marta, to you: "Nice work. Now let's talk about Redis 8 features..."

## The Complete Redis Toolkit

| Chapter | Problem | Solution |
|---|---|---|
| 1 | Slow queries | SET/GET, TTL, caching |
| 2 | Ranking | Sorted sets (ZADD, ZRANGE, ZREVRANK) |
| 3 | Structured data | Hashes, caching patterns |
| 4 | Queue processing | Lists, BRPOP, reliable queues |
| 5 | Message delivery | Pub/Sub, Streams, consumer groups |
| 6 | Abuse prevention | Rate limiting, Lua scripts |
| 7 | Coordination | Distributed locks, Redlock |
| 8 | Data durability | RDB, AOF, hybrid persistence |
| 9 | High availability | Replication, Sentinel, failover |
| 10 | Horizontal scaling | Clustering, hash slots, resharding |
| 11 | Security | ACLs, network security, monitoring |
| 12 | Performance | Connection pools, pipelines, tuning |

## What You Learned

- **Connection pooling** — reuse connections, size pools correctly
- **Pipeline batching** — 100-1000 commands per pipeline
- **Memory optimization** — compact keys, correct encodings, defragmentation
- **Latency tuning** — THP disabled, lazy freeing, IO threads
- **Benchmarking** — redis-benchmark and custom load tests
- **Production config** — the complete redis.conf for production
- **Observability** — Prometheus, Grafana, health checks
- **Capacity planning** — measure, project, provision

You started with a leaderboard that took 8 seconds to load. You ended with a production Redis cluster handling 100,000+ operations per second across multiple nodes with automatic failover, persistence, security, and full observability.

Every concept was introduced because something broke, was too slow, or was about to fall over. The problems came first. The theory followed.

Now go build something.

---

[← Chapter 11: Operational Safety](chapter-11-operational-safety.md)

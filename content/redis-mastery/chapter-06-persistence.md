# Chapter 6: Persistence & High Availability

[← Distributed Patterns](./chapter-05-distributed.md) | [Next: Performance →](./chapter-07-performance.md)

---

## 6.1 RDB Snapshots

Point-in-time snapshots of the dataset written to disk.

**redis.conf**

```
# Save after 3600s if at least 1 key changed
save 3600 1
# Save after 300s if at least 100 keys changed
save 300 100
# Save after 60s if at least 10000 keys changed
save 60 10000

dbfilename dump.rdb
dir /var/lib/redis
```

```bash
# Manual snapshot
redis-cli BGSAVE

# Check last save time
redis-cli LASTSAVE

# Check RDB status
redis-cli INFO persistence
```

**Pros:** Compact, fast restarts, good for backups.
**Cons:** Data loss between snapshots (up to last save interval).

## 6.2 AOF (Append Only File)

Logs every write operation for full durability.

**redis.conf**

```
appendonly yes
appendfilename "appendonly.aof"

# fsync policy
# always    - fsync after every write (safest, slowest)
# everysec  - fsync every second (good balance)
# no        - let OS decide (fastest, least safe)
appendfsync everysec

# AOF rewrite triggers
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
```

```bash
# Trigger AOF rewrite manually
redis-cli BGREWRITEAOF

# Check AOF status
redis-cli INFO persistence
```

**Pros:** Minimal data loss (at most 1 second with everysec). **Cons:** Larger files, slower restarts.

## 6.3 Hybrid Persistence (RDB + AOF)

```
# Enable both - Redis uses AOF for recovery (more complete)
save 3600 1
appendonly yes
aof-use-rdb-preamble yes
```

With `aof-use-rdb-preamble yes`, AOF rewrite produces a file with RDB header + AOF tail for fast loading with minimal data loss.

## 6.4 Redis Sentinel

Automatic failover and monitoring for Redis master-replica setups.

**sentinel.conf**

```
sentinel monitor mymaster 127.0.0.1 6379 2
sentinel down-after-milliseconds mymaster 5000
sentinel failover-timeout mymaster 60000
sentinel parallel-syncs mymaster 1
```

```bash
# Start sentinel
redis-sentinel /etc/redis/sentinel.conf

# Check master
redis-cli -p 26379 SENTINEL get-master-addr-by-name mymaster

# List replicas
redis-cli -p 26379 SENTINEL replicas mymaster
```

**Spring Boot Sentinel Configuration**

```yaml
spring:
  data:
    redis:
      sentinel:
        master: mymaster
        nodes:
          - localhost:26379
          - localhost:26380
          - localhost:26381
```

## 6.5 Redis Cluster

Horizontal scaling with automatic sharding across multiple nodes.

```bash
# Create cluster (3 masters, 3 replicas)
redis-cli --cluster create \
  127.0.0.1:7000 127.0.0.1:7001 127.0.0.1:7002 \
  127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 \
  --cluster-replicas 1

# Check cluster status
redis-cli -c -p 7000 CLUSTER INFO
redis-cli -c -p 7000 CLUSTER NODES

# Cluster operations (use -c flag for auto-redirect)
redis-cli -c -p 7000 SET mykey "value"
redis-cli -c -p 7000 GET mykey
```

**Spring Boot Cluster Configuration**

```yaml
spring:
  data:
    redis:
      cluster:
        nodes:
          - localhost:7000
          - localhost:7001
          - localhost:7002
        max-redirects: 3
```

## 6.6 Memory Management

```bash
# Check memory usage
redis-cli INFO memory

# Memory usage of a specific key
redis-cli MEMORY USAGE mykey

# Set max memory
redis-cli CONFIG SET maxmemory 256mb

# Set eviction policy
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

**Eviction policies:**

| Policy         | Description                             |
| -------------- | --------------------------------------- |
| noeviction     | Return error on writes when memory full |
| allkeys-lru    | Evict least recently used keys          |
| allkeys-lfu    | Evict least frequently used keys        |
| volatile-lru   | Evict LRU keys with TTL set             |
| volatile-ttl   | Evict keys with shortest TTL            |
| allkeys-random | Evict random keys                       |

**redis.conf**

```
maxmemory 512mb
maxmemory-policy allkeys-lfu
```

## Exercises

1. Configure RDB with custom save intervals. Trigger BGSAVE and verify the dump file.
2. Enable AOF with everysec. Write data, kill Redis, restart, and verify recovery.
3. Set up a 3-node Sentinel deployment with Docker Compose. Simulate master failure.
4. Configure maxmemory with allkeys-lru. Fill memory and observe eviction behavior.
5. Set up a 6-node Redis Cluster. Verify key distribution across slots.

---

[← Distributed Patterns](./chapter-05-distributed.md) | [Next: Performance →](./chapter-07-performance.md)

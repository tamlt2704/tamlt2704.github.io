# Chapter 7: Performance & Optimization

[← Persistence & HA](./chapter-06-persistence.md) | [Overview →](./chapter-00-overview.md)

---

## 7.1 Pipelining

Batch multiple commands in a single round trip to reduce network latency.

```java
@Service
@RequiredArgsConstructor
public class PipelineService {

    private final StringRedisTemplate redisTemplate;

    public void batchInsert(Map<String, String> entries) {
        redisTemplate.executePipelined((RedisCallback<Object>) connection -> {
            StringRedisConnection stringConn = (StringRedisConnection) connection;
            entries.forEach((key, value) -> stringConn.set(key, value));
            return null;
        });
    }

    public List<Object> batchGet(List<String> keys) {
        return redisTemplate.executePipelined((RedisCallback<Object>) connection -> {
            StringRedisConnection stringConn = (StringRedisConnection) connection;
            keys.forEach(stringConn::get);
            return null;
        });
    }
}
```

```bash
# redis-cli pipeline (using --pipe)
printf "SET key1 val1\r\nSET key2 val2\r\nSET key3 val3\r\n" | redis-cli --pipe

# Measure latency without pipelining
redis-cli --latency
```

## 7.2 Lua Scripting

Execute atomic operations server-side. No race conditions between commands.

```java
@Service
@RequiredArgsConstructor
public class LuaScriptService {

    private final StringRedisTemplate redisTemplate;

    // Atomic compare-and-delete
    private static final RedisScript<Long> DELETE_IF_MATCH = new DefaultRedisScript<>(
        "if redis.call('get', KEYS[1]) == ARGV[1] then " +
        "  return redis.call('del', KEYS[1]) " +
        "else return 0 end", Long.class);

    public boolean deleteIfMatch(String key, String expectedValue) {
        Long result = redisTemplate.execute(DELETE_IF_MATCH, List.of(key), expectedValue);
        return result != null && result == 1;
    }

    // Atomic rate limiter
    private static final RedisScript<Long> RATE_LIMIT = new DefaultRedisScript<>(
        "local current = redis.call('incr', KEYS[1]) " +
        "if current == 1 then redis.call('expire', KEYS[1], ARGV[1]) end " +
        "return current", Long.class);

    public boolean checkRateLimit(String key, int windowSeconds, int maxRequests) {
        Long count = redisTemplate.execute(RATE_LIMIT, List.of(key), String.valueOf(windowSeconds));
        return count != null && count <= maxRequests;
    }
}
```

```bash
# redis-cli Lua
redis-cli EVAL "return redis.call('get', KEYS[1])" 1 mykey

# Atomic increment with ceiling
redis-cli EVAL "local val = redis.call('incr', KEYS[1]) if val > tonumber(ARGV[1]) then redis.call('set', KEYS[1], ARGV[1]) return tonumber(ARGV[1]) end return val" 1 counter 100
```

## 7.3 Memory Optimization

```bash
# Analyze key space
redis-cli --bigkeys
redis-cli --memkeys

# Memory usage per key
redis-cli MEMORY USAGE user:1

# Memory doctor
redis-cli MEMORY DOCTOR
```

**Optimization techniques:**

```java
// Use hashes for small objects (ziplist encoding)
// Redis uses ziplist for hashes with fewer than 128 fields and values under 64 bytes
redisTemplate.opsForHash().put("user:1", "name", "Alice");

// Use short key names in high-volume scenarios
// "u:1:n" instead of "user:1:name"

// Use EXPIRE to auto-cleanup
redisTemplate.expire("temp:data", Duration.ofHours(1));

// Use UNLINK instead of DEL for large keys (non-blocking)
redisTemplate.unlink("large:key");
```

**redis.conf tuning:**

```
# Ziplist thresholds (memory-efficient for small collections)
hash-max-ziplist-entries 128
hash-max-ziplist-value 64
list-max-ziplist-size -2
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
```

## 7.4 Monitoring

```bash
# Server info
redis-cli INFO all

# Key sections
redis-cli INFO server
redis-cli INFO memory
redis-cli INFO stats
redis-cli INFO clients
redis-cli INFO keyspace

# Slow log - commands exceeding threshold
redis-cli CONFIG SET slowlog-log-slower-than 10000  # microseconds
redis-cli CONFIG SET slowlog-max-len 128
redis-cli SLOWLOG GET 10
redis-cli SLOWLOG LEN
redis-cli SLOWLOG RESET

# Real-time monitoring
redis-cli MONITOR

# Client list
redis-cli CLIENT LIST

# Latency monitoring
redis-cli --latency
redis-cli --latency-history
redis-cli LATENCY LATEST
```

**Spring Boot Actuator integration:**

```groovy
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-actuator'
}
```

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,metrics
  health:
    redis:
      enabled: true
```

## 7.5 Benchmarking

```bash
# Built-in benchmark tool
redis-benchmark -h localhost -p 6379 -c 50 -n 100000

# Specific commands
redis-benchmark -t set,get -n 100000 -q

# Pipeline benchmark
redis-benchmark -t set -n 100000 -P 16 -q

# With specific data size
redis-benchmark -t set -n 100000 -d 1024 -q
```

**Sample output interpretation:**

```
SET: 125000.00 requests per second
GET: 142857.14 requests per second
INCR: 166666.67 requests per second
```

## 7.6 Production Checklist

- Set `maxmemory` and `maxmemory-policy`
- Enable `slowlog` with appropriate threshold
- Use connection pooling (Lettuce pool or Jedis pool)
- Monitor with INFO stats: `instantaneous_ops_per_sec`, `used_memory`, `connected_clients`
- Avoid KEYS command in production (use SCAN)
- Use pipelining for batch operations
- Set appropriate timeouts on connections
- Enable persistence (AOF everysec for durability)

## Exercises

1. Implement a batch insert of 10,000 keys with pipelining. Compare time vs individual SETs.
2. Write a Lua script for atomic transfer between two keys (decrement one, increment other).
3. Run redis-benchmark and identify throughput for SET/GET with different pipeline sizes.
4. Configure SLOWLOG and identify slow commands in your application.
5. Use `--bigkeys` to find memory-heavy keys and optimize their structure.

---

[← Persistence & HA](./chapter-06-persistence.md) | [Overview →](./chapter-00-overview.md)

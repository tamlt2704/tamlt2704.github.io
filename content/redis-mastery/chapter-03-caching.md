# Chapter 3: Caching Patterns

[← Spring Data Redis](./chapter-02-spring-redis.md) | [Next: Pub/Sub & Streams →](./chapter-04-pubsub.md)

---

## 3.1 Cache-Aside (Lazy Loading)

Application checks cache first. On miss, loads from DB and populates cache.

```java
@Service
@RequiredArgsConstructor
public class CacheAsideService {

    private final RedisTemplate<String, Object> redisTemplate;
    private final ProductRepository productRepository;

    public Product getProduct(Long id) {
        String key = "product:" + id;
        Product cached = (Product) redisTemplate.opsForValue().get(key);
        if (cached != null) return cached;

        Product product = productRepository.findById(id).orElseThrow();
        redisTemplate.opsForValue().set(key, product, Duration.ofMinutes(10));
        return product;
    }

    public void updateProduct(Product product) {
        productRepository.save(product);
        redisTemplate.delete("product:" + product.getId());
    }
}
```

**Pros:** Only requested data is cached. **Cons:** Cache miss penalty, possible stale data.

## 3.2 Write-Through

Data written to cache and database simultaneously.

```java
@Service
@RequiredArgsConstructor
public class WriteThroughService {

    private final RedisTemplate<String, Object> redisTemplate;
    private final ProductRepository productRepository;

    public Product save(Product product) {
        Product saved = productRepository.save(product);
        redisTemplate.opsForValue().set("product:" + saved.getId(), saved, Duration.ofMinutes(30));
        return saved;
    }
}
```

**Pros:** Cache always consistent. **Cons:** Write latency increases.

## 3.3 Write-Behind (Write-Back)

Writes go to cache immediately; DB updated asynchronously.

```java
@Service
@RequiredArgsConstructor
public class WriteBehindService {

    private final RedisTemplate<String, Object> redisTemplate;
    private final ProductRepository productRepository;

    public void save(Product product) {
        redisTemplate.opsForValue().set("product:" + product.getId(), product, Duration.ofMinutes(30));
        redisTemplate.opsForList().leftPush("write:queue", product);
    }

    @Scheduled(fixedDelay = 5000)
    public void flushToDatabase() {
        Object item;
        while ((item = redisTemplate.opsForList().rightPop("write:queue")) != null) {
            productRepository.save((Product) item);
        }
    }
}
```

**Pros:** Fast writes, batching. **Cons:** Data loss risk if Redis crashes before flush.

## 3.4 TTL Strategies

```java
// Fixed TTL
redis.opsForValue().set(key, value, Duration.ofMinutes(10));

// Sliding TTL - reset on each access
Object val = redis.opsForValue().get(key);
if (val != null) redis.expire(key, Duration.ofMinutes(10));

// Jittered TTL - prevent thundering herd
int jitter = ThreadLocalRandom.current().nextInt(0, 60);
redis.opsForValue().set(key, value, Duration.ofSeconds(600 + jitter));
```

## 3.5 Cache Invalidation

```java
// Direct invalidation
redisTemplate.delete("product:1");

// Pattern-based (use SCAN in production, not KEYS)
Set<String> keys = redisTemplate.keys("product:*");
if (keys != null && !keys.isEmpty()) redisTemplate.delete(keys);

// Event-driven via pub/sub
redisTemplate.convertAndSend("cache:invalidation", "product:1");
```

```bash
# redis-cli
redis-cli DEL product:1
redis-cli --scan --pattern "product:*" | xargs redis-cli DEL
redis-cli SCAN 0 MATCH "product:*" COUNT 100
```

## 3.6 Cache Stampede Protection

```java
public Product getWithLock(Long id) {
    String key = "product:" + id;
    Product cached = (Product) redisTemplate.opsForValue().get(key);
    if (cached != null) return cached;

    String lockKey = "lock:" + key;
    Boolean acquired = redisTemplate.opsForValue().setIfAbsent(lockKey, "1", Duration.ofSeconds(5));
    if (Boolean.TRUE.equals(acquired)) {
        try {
            Product product = productRepository.findById(id).orElseThrow();
            redisTemplate.opsForValue().set(key, product, Duration.ofMinutes(10));
            return product;
        } finally {
            redisTemplate.delete(lockKey);
        }
    }
    // Wait and retry
    Thread.sleep(50);
    return getWithLock(id);
}
```

## Exercises

1. Implement cache-aside for a User entity. Verify with redis-cli that cache populates on first access.
2. Add jittered TTL to prevent thundering herd. Verify different keys have different TTLs.
3. Implement write-behind with a scheduled flush. Simulate Redis crash and observe data loss.
4. Build pattern-based invalidation using SCAN (not KEYS) for production safety.
5. Implement cache stampede protection with a mutex lock.

---

[← Spring Data Redis](./chapter-02-spring-redis.md) | [Next: Pub/Sub & Streams →](./chapter-04-pubsub.md)

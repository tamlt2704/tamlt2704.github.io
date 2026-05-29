# Chapter 5: Distributed Patterns

[← Pub/Sub & Streams](./chapter-04-pubsub.md) | [Next: Persistence & HA →](./chapter-06-persistence.md)

---

## 5.1 Distributed Locks with Redisson

**build.gradle**

```groovy
dependencies {
    implementation 'org.redisson:redisson-spring-boot-starter:3.27.0'
}
```

**Configuration**

```java
@Configuration
public class RedissonConfig {

    @Bean
    public RedissonClient redissonClient() {
        Config config = new Config();
        config.useSingleServer().setAddress("redis://localhost:6379");
        return Redisson.create(config);
    }
}
```

**Using distributed locks**

```java
@Service
@RequiredArgsConstructor
public class InventoryService {

    private final RedissonClient redissonClient;
    private final ProductRepository productRepository;

    public void decrementStock(Long productId, int quantity) {
        RLock lock = redissonClient.getLock("lock:product:" + productId);
        try {
            // Wait up to 10s to acquire, auto-release after 30s
            if (lock.tryLock(10, 30, TimeUnit.SECONDS)) {
                try {
                    Product product = productRepository.findById(productId).orElseThrow();
                    if (product.getStock() < quantity) {
                        throw new IllegalStateException("Insufficient stock");
                    }
                    product.setStock(product.getStock() - quantity);
                    productRepository.save(product);
                } finally {
                    lock.unlock();
                }
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
```

**redis-cli lock equivalent**

```bash
# Acquire lock (SET with NX and EX)
redis-cli SET lock:product:1 "owner-abc" NX EX 30

# Release lock (only if owner matches - use Lua for atomicity)
redis-cli EVAL "if redis.call('get',KEYS[1]) == ARGV[1] then return redis.call('del',KEYS[1]) else return 0 end" 1 lock:product:1 "owner-abc"
```

## 5.2 Rate Limiting

**Sliding window rate limiter**

```java
@Service
@RequiredArgsConstructor
public class RateLimiterService {

    private final StringRedisTemplate redisTemplate;

    public boolean isAllowed(String clientId, int maxRequests, Duration window) {
        String key = "ratelimit:" + clientId;
        long now = System.currentTimeMillis();
        long windowStart = now - window.toMillis();

        // Remove old entries, add current, count
        redisTemplate.opsForZSet().removeRangeByScore(key, 0, windowStart);
        redisTemplate.opsForZSet().add(key, String.valueOf(now), now);
        redisTemplate.expire(key, window);

        Long count = redisTemplate.opsForZSet().zCard(key);
        return count != null && count <= maxRequests;
    }
}
```

**Fixed window counter (simpler)**

```java
public boolean isAllowedFixedWindow(String clientId, int maxRequests, Duration window) {
    String key = "ratelimit:fixed:" + clientId;
    Long count = redisTemplate.opsForValue().increment(key);
    if (count == 1) {
        redisTemplate.expire(key, window);
    }
    return count <= maxRequests;
}
```

```bash
# redis-cli: simple rate limit check
redis-cli INCR ratelimit:user:1
redis-cli EXPIRE ratelimit:user:1 60
redis-cli GET ratelimit:user:1
```

## 5.3 Session Storage

```java
@Configuration
@EnableRedisHttpSession(maxInactiveIntervalInSeconds = 1800)
public class SessionConfig {
}
```

**build.gradle**

```groovy
dependencies {
    implementation 'org.springframework.session:spring-session-data-redis'
}
```

**Using sessions in a controller**

```java
@RestController
public class SessionController {

    @GetMapping("/login")
    public String login(HttpSession session, @RequestParam String username) {
        session.setAttribute("user", username);
        return "Logged in as " + username;
    }

    @GetMapping("/profile")
    public String profile(HttpSession session) {
        String user = (String) session.getAttribute("user");
        return user != null ? "Hello " + user : "Not logged in";
    }
}
```

```bash
# Inspect session in Redis
redis-cli KEYS "spring:session:*"
redis-cli HGETALL "spring:session:sessions:<session-id>"
```

## 5.4 Leaderboards with Sorted Sets

```java
@Service
@RequiredArgsConstructor
public class LeaderboardService {

    private final StringRedisTemplate redisTemplate;
    private static final String KEY = "game:leaderboard";

    public void addScore(String player, double score) {
        redisTemplate.opsForZSet().add(KEY, player, score);
    }

    public void incrementScore(String player, double delta) {
        redisTemplate.opsForZSet().incrementScore(KEY, player, delta);
    }

    public Set<ZSetOperations.TypedTuple<String>> getTopPlayers(int count) {
        return redisTemplate.opsForZSet().reverseRangeWithScores(KEY, 0, count - 1);
    }

    public Long getPlayerRank(String player) {
        return redisTemplate.opsForZSet().reverseRank(KEY, player);
    }

    public Double getPlayerScore(String player) {
        return redisTemplate.opsForZSet().score(KEY, player);
    }
}
```

```bash
# redis-cli leaderboard
redis-cli ZADD game:leaderboard 1500 "alice" 1200 "bob" 1800 "charlie"
redis-cli ZREVRANGE game:leaderboard 0 2 WITHSCORES
redis-cli ZREVRANK game:leaderboard "alice"
redis-cli ZINCRBY game:leaderboard 100 "bob"
```

## Exercises

1. Implement a distributed lock for a payment processing service. Test with concurrent requests.
2. Build a sliding window rate limiter that allows 100 requests per minute per user.
3. Configure Spring Session with Redis. Verify session data persists across server restarts.
4. Build a real-time leaderboard with endpoints for adding scores, getting top-N, and player rank.

---

[← Pub/Sub & Streams](./chapter-04-pubsub.md) | [Next: Persistence & HA →](./chapter-06-persistence.md)

# Chapter 16: Rate Limiting

[← Chapter 15: Multi-Tenancy](/blog/spring-job-engine/chapter-15-multi-tenancy) | [Overview](/blog/spring-job-engine/chapter-00-overview)

---

## The Story

A junior dev writes a script that submits 10,000 jobs in a loop. The queue explodes, Redis fills up, and everyone else's jobs are stuck. You need rate limiting — per-user and per-tenant caps on how fast jobs can be submitted.

## Rate Limiting Algorithms

| Algorithm          | How it works                                                                   | Best for                                   |
| ------------------ | ------------------------------------------------------------------------------ | ------------------------------------------ |
| **Fixed Window**   | Count requests in a time window (e.g., 100/minute). Resets at window boundary. | Simple, but allows bursts at window edges  |
| **Sliding Window** | Weighted average of current + previous window                                  | Smoother than fixed, slightly more complex |
| **Token Bucket**   | Bucket fills with tokens at a fixed rate. Each request consumes one.           | Allows controlled bursts                   |
| **Leaky Bucket**   | Requests enter a queue that drains at a fixed rate                             | Strict constant rate output                |

For a job engine, **sliding window** (for submission limits) + **token bucket** (for burst tolerance) is a good combination.

## Step 1: Redis Sliding Window

```java
// service/RateLimiter.java
@Service
@RequiredArgsConstructor
public class RateLimiter {

    private final StringRedisTemplate redis;

    /**
     * Sliding window rate limit.
     * @param key     unique identifier (e.g., "rate:user:alice@co.com")
     * @param limit   max requests allowed in the window
     * @param window  time window duration
     * @return true if allowed, false if rate limited
     */
    public boolean isAllowed(String key, int limit, Duration window) {
        long now = Instant.now().toEpochMilli();
        long windowStart = now - window.toMillis();

        // Use a sorted set: score = timestamp, value = unique request ID
        redis.opsForZSet().removeRangeByScore(key, 0, windowStart);  // remove expired
        Long count = redis.opsForZSet().zCard(key);                   // count remaining

        if (count != null && count >= limit) {
            return false;  // rate limited
        }

        // Add this request
        redis.opsForZSet().add(key, now + ":" + UUID.randomUUID(), now);
        redis.expire(key, window.plusSeconds(1));  // auto-cleanup
        return true;
    }
}
```

### How It Works

```
Window: 1 minute, Limit: 10

Sorted Set "rate:user:alice":
  Score (timestamp)    Value
  1706000001000       "1706000001000:uuid1"
  1706000005000       "1706000005000:uuid2"
  1706000030000       "1706000030000:uuid3"
  ... (7 more)

New request at 1706000061000:
  1. Remove entries with score < (now - 60000) → clears old ones
  2. Count remaining → 8
  3. 8 < 10 → allowed, add entry
```

## Step 2: Apply to Job Submission

```java
@RestController
@RequiredArgsConstructor
public class JobController {

    private final RateLimiter rateLimiter;
    private final JobService jobService;
    private final JobGateway jobGateway;

    @PostMapping("/api/jobs")
    public ResponseEntity<?> submitJob(@RequestBody JobRequest request) {
        String user = SecurityContextHolder.getContext().getAuthentication().getName();
        String tenant = TenantContext.getTenant();

        // Per-user limit: 20 jobs per minute
        if (!rateLimiter.isAllowed("rate:user:" + user, 20, Duration.ofMinutes(1))) {
            return ResponseEntity.status(429)
                .body(Map.of("error", "Rate limit exceeded", "retryAfter", "60s"));
        }

        // Per-tenant limit: 100 jobs per minute
        if (!rateLimiter.isAllowed("rate:tenant:" + tenant, 100, Duration.ofMinutes(1))) {
            return ResponseEntity.status(429)
                .body(Map.of("error", "Tenant rate limit exceeded"));
        }

        Job job = jobService.create(request);
        jobGateway.submit(job);
        return ResponseEntity.status(201).body(job);
    }
}
```

## Step 3: Rate Limit as a Filter (Reusable)

Instead of checking in every controller, use a servlet filter:

```java
// security/RateLimitFilter.java
@Component
public class RateLimitFilter extends OncePerRequestFilter {

    private final RateLimiter rateLimiter;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                     HttpServletResponse response,
                                     FilterChain chain) throws ServletException, IOException {
        String user = SecurityContextHolder.getContext().getAuthentication() != null
            ? SecurityContextHolder.getContext().getAuthentication().getName()
            : request.getRemoteAddr();

        if (!rateLimiter.isAllowed("rate:api:" + user, 60, Duration.ofMinutes(1))) {
            response.setStatus(429);
            response.setHeader("Retry-After", "60");
            response.getWriter().write("{\"error\":\"Too many requests\"}");
            return;
        }

        chain.doFilter(request, response);
    }

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        // Don't rate-limit health checks or auth endpoints
        String path = request.getRequestURI();
        return path.startsWith("/api/health") || path.startsWith("/api/auth");
    }
}
```

## Step 4: Token Bucket (Burst-Tolerant)

The sliding window is strict. A token bucket allows short bursts while maintaining an average rate:

```java
// service/TokenBucketLimiter.java
@Service
@RequiredArgsConstructor
public class TokenBucketLimiter {

    private final StringRedisTemplate redis;

    /**
     * Token bucket rate limiter.
     * @param key        unique identifier
     * @param capacity   max tokens (burst size)
     * @param refillRate tokens added per second
     * @return true if allowed
     */
    public boolean tryConsume(String key, int capacity, double refillRate) {
        String tokensKey = key + ":tokens";
        String timestampKey = key + ":ts";

        String tokensStr = redis.opsForValue().get(tokensKey);
        String tsStr = redis.opsForValue().get(timestampKey);

        double tokens = tokensStr != null ? Double.parseDouble(tokensStr) : capacity;
        long lastRefill = tsStr != null ? Long.parseLong(tsStr) : System.currentTimeMillis();

        // Refill tokens based on elapsed time
        long now = System.currentTimeMillis();
        double elapsed = (now - lastRefill) / 1000.0;
        tokens = Math.min(capacity, tokens + elapsed * refillRate);

        if (tokens < 1) {
            return false;  // no tokens available
        }

        // Consume one token
        tokens -= 1;
        redis.opsForValue().set(tokensKey, String.valueOf(tokens));
        redis.opsForValue().set(timestampKey, String.valueOf(now));
        redis.expire(tokensKey, Duration.ofMinutes(5));
        redis.expire(timestampKey, Duration.ofMinutes(5));
        return true;
    }
}
```

### Token Bucket Visualized

```
Capacity: 10 tokens, Refill: 2 tokens/sec

Time 0s:  [██████████] 10 tokens — user submits 5 jobs instantly → allowed
Time 0s:  [█████     ]  5 tokens remaining
Time 1s:  [███████   ]  7 tokens (refilled 2)
Time 2s:  [█████████ ]  9 tokens (refilled 2)
Time 2s:  user submits 9 jobs → allowed, 0 remaining
Time 2s:  [          ]  0 tokens
Time 2.5s: user submits 1 job → DENIED (only 1 token refilled, need to wait)
Time 3s:  [██        ]  2 tokens available again
```

## Step 5: Lua Script (Atomic Redis Operations)

The token bucket above has a race condition — two requests can read the same token count. Use a Lua script for atomicity:

```java
// service/AtomicRateLimiter.java
@Service
public class AtomicRateLimiter {

    private final StringRedisTemplate redis;

    private static final String LUA_SCRIPT = """
        local key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local refillRate = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])

        local data = redis.call('HMGET', key, 'tokens', 'ts')
        local tokens = tonumber(data[1]) or capacity
        local lastRefill = tonumber(data[2]) or now

        local elapsed = (now - lastRefill) / 1000
        tokens = math.min(capacity, tokens + elapsed * refillRate)

        if tokens < 1 then
            return 0
        end

        tokens = tokens - 1
        redis.call('HMSET', key, 'tokens', tokens, 'ts', now)
        redis.call('EXPIRE', key, 300)
        return 1
    """;

    private final RedisScript<Long> script = new DefaultRedisScript<>(LUA_SCRIPT, Long.class);

    public boolean tryConsume(String key, int capacity, double refillRate) {
        Long result = redis.execute(script,
            List.of(key),
            String.valueOf(capacity),
            String.valueOf(refillRate),
            String.valueOf(System.currentTimeMillis()));
        return result != null && result == 1;
    }
}
```

### Why Lua?

Redis executes Lua scripts **atomically** — no other command can interleave. This eliminates the read-then-write race condition without distributed locks.

## Step 6: Response Headers

Good rate limiting tells the client their remaining quota:

```java
@PostMapping("/api/jobs")
public ResponseEntity<?> submitJob(@RequestBody JobRequest request) {
    String user = getUser();
    String key = "rate:user:" + user;
    int limit = 20;
    Duration window = Duration.ofMinutes(1);

    if (!rateLimiter.isAllowed(key, limit, window)) {
        return ResponseEntity.status(429)
            .header("X-RateLimit-Limit", String.valueOf(limit))
            .header("X-RateLimit-Remaining", "0")
            .header("Retry-After", "60")
            .body(Map.of("error", "Rate limit exceeded"));
    }

    Long remaining = redis.opsForZSet().zCard(key);
    Job job = jobService.create(request);
    jobGateway.submit(job);

    return ResponseEntity.status(201)
        .header("X-RateLimit-Limit", String.valueOf(limit))
        .header("X-RateLimit-Remaining", String.valueOf(limit - remaining))
        .body(job);
}
```

## Step 7: Configurable Limits per Role/Tenant

```yaml
# application.yml
rate-limits:
  default:
    per-user: 20
    per-tenant: 100
    window: 60s
  admin:
    per-user: 200
    per-tenant: 1000
    window: 60s
```

```java
@ConfigurationProperties(prefix = "rate-limits")
public record RateLimitConfig(
    LimitTier defaultLimits,
    LimitTier admin
) {
    public record LimitTier(int perUser, int perTenant, Duration window) {}
}
```

## Summary

| Layer           | What                                | Algorithm      |
| --------------- | ----------------------------------- | -------------- |
| API-wide        | 60 req/min per user (all endpoints) | Sliding window |
| Job submission  | 20 jobs/min per user                | Sliding window |
| Tenant cap      | 100 jobs/min per org                | Sliding window |
| Burst tolerance | 10 burst + 2/sec refill             | Token bucket   |

```
Request → RateLimitFilter (API-wide) → Controller (per-endpoint) → Job submitted
              ↓ 429                         ↓ 429
         "Too many requests"          "Job rate limit exceeded"
```

---

You now have a complete job engine with real-time updates, scheduling, dependencies, multi-tenancy, and rate limiting. 🚀

[← Overview](/blog/spring-job-engine/chapter-00-overview)

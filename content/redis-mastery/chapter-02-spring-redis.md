# Chapter 2: Spring Data Redis

[← Basics](./chapter-01-basics.md) | [Next: Caching Patterns →](./chapter-03-caching.md)

---

## 2.1 Connection Configuration

**build.gradle**

```groovy
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-data-redis'
    implementation 'org.apache.commons:commons-pool2'
}
```

**application.yml**

```yaml
spring:
  data:
    redis:
      host: localhost
      port: 6379
      password: ""
      timeout: 2000ms
      lettuce:
        pool:
          max-active: 8
          max-idle: 8
          min-idle: 2
          max-wait: -1ms
```

**Redis Configuration Class**

```java
@Configuration
public class RedisConfig {

    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory connectionFactory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(connectionFactory);
        template.setKeySerializer(new StringRedisSerializer());
        template.setValueSerializer(new GenericJackson2JsonRedisSerializer());
        template.setHashKeySerializer(new StringRedisSerializer());
        template.setHashValueSerializer(new GenericJackson2JsonRedisSerializer());
        template.afterPropertiesSet();
        return template;
    }
}
```

## 2.2 RedisTemplate Operations

```java
@Service
@RequiredArgsConstructor
public class UserRedisService {

    private final RedisTemplate<String, Object> redisTemplate;

    public void saveUser(String id, User user) {
        redisTemplate.opsForValue().set("user:" + id, user, Duration.ofHours(1));
    }

    public User getUser(String id) {
        return (User) redisTemplate.opsForValue().get("user:" + id);
    }

    public void saveUserAsHash(String id, User user) {
        String key = "user:hash:" + id;
        redisTemplate.opsForHash().put(key, "name", user.getName());
        redisTemplate.opsForHash().put(key, "email", user.getEmail());
        redisTemplate.expire(key, Duration.ofHours(1));
    }

    public void addToQueue(String task) {
        redisTemplate.opsForList().leftPush("task:queue", task);
    }

    public Object pollFromQueue() {
        return redisTemplate.opsForList().rightPop("task:queue");
    }

    public void addScore(String player, double score) {
        redisTemplate.opsForZSet().add("leaderboard", player, score);
    }
}
```

## 2.3 StringRedisTemplate

```java
@Service
@RequiredArgsConstructor
public class SessionService {

    private final StringRedisTemplate stringRedisTemplate;

    public void createSession(String sessionId, String userId) {
        stringRedisTemplate.opsForValue().set(
            "session:" + sessionId, userId, Duration.ofMinutes(30));
    }

    public String getUserId(String sessionId) {
        return stringRedisTemplate.opsForValue().get("session:" + sessionId);
    }

    public Long incrementCounter(String name) {
        return stringRedisTemplate.opsForValue().increment("counter:" + name);
    }
}
```

## 2.4 Spring Cache Annotations

**Enable caching**

```java
@Configuration
@EnableCaching
public class CacheConfig {

    @Bean
    public RedisCacheManager cacheManager(RedisConnectionFactory connectionFactory) {
        RedisCacheConfiguration config = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(10))
            .serializeKeysWith(
                RedisSerializationContext.SerializationPair.fromSerializer(new StringRedisSerializer()))
            .serializeValuesWith(
                RedisSerializationContext.SerializationPair.fromSerializer(
                    new GenericJackson2JsonRedisSerializer()));

        return RedisCacheManager.builder(connectionFactory)
            .cacheDefaults(config)
            .withCacheConfiguration("products",
                RedisCacheConfiguration.defaultCacheConfig().entryTtl(Duration.ofMinutes(5)))
            .build();
    }
}
```

**Service with caching annotations**

```java
@Service
@RequiredArgsConstructor
public class ProductService {

    private final ProductRepository productRepository;

    @Cacheable(value = "products", key = "#id")
    public Product findById(Long id) {
        return productRepository.findById(id).orElseThrow();
    }

    @CachePut(value = "products", key = "#product.id")
    public Product update(Product product) {
        return productRepository.save(product);
    }

    @CacheEvict(value = "products", key = "#id")
    public void delete(Long id) {
        productRepository.deleteById(id);
    }

    @CacheEvict(value = "products", allEntries = true)
    public void clearCache() {
    }
}
```

## 2.5 Verify with redis-cli

```bash
# After calling findById(1)
redis-cli GET "products::1"

# Check TTL
redis-cli TTL "products::1"

# Monitor commands in real-time
redis-cli MONITOR
```

## Exercises

1. Configure RedisTemplate with Jackson serialization. Save and retrieve a Java object.
2. Implement a service using @Cacheable with a custom cache name and TTL.
3. Use StringRedisTemplate to implement a page-view counter.
4. Use MONITOR to observe what commands Spring sends to Redis when @Cacheable triggers.

---

[← Basics](./chapter-01-basics.md) | [Next: Caching Patterns →](./chapter-03-caching.md)

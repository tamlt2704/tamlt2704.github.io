# Chapter 6: Caching — Stop Hitting the Database for the Same Data

[← Chapter 5: Async](chapter-05-async.md) | [Chapter 7: Testing →](chapter-07-testing.md)

---

## The Problem

"The product catalog endpoint gets 10k requests/minute but the data changes once per hour. I'm hammering the database for no reason."

## Enable Caching

```java
@SpringBootApplication
@EnableCaching
public class MyApp { }
```

## @Cacheable — Cache Method Results

```java
@Service
public class ProductService {

    // Result cached by id — second call skips the method entirely
    @Cacheable(value = "products", key = "#id")
    public Product getProduct(Long id) {
        log.info("DB hit for product {}", id);  // Only logs on cache miss
        return productRepository.findById(id)
            .orElseThrow(() -> new NotFoundException("Product", id));
    }

    // Composite key
    @Cacheable(value = "product-search", key = "#category + '-' + #page")
    public Page<Product> search(String category, int page) {
        return productRepository.findByCategory(category, PageRequest.of(page, 20));
    }

    // Conditional — only cache if result is non-null
    @Cacheable(value = "products", key = "#id", unless = "#result == null")
    public Product findProductOrNull(Long id) {
        return productRepository.findById(id).orElse(null);
    }
}
```

## @CacheEvict and @CachePut

```java
@Service
public class ProductService {

    // Update cache with new value (doesn't skip method)
    @CachePut(value = "products", key = "#product.id")
    public Product updateProduct(Product product) {
        return productRepository.save(product);
    }

    // Remove from cache
    @CacheEvict(value = "products", key = "#id")
    public void deleteProduct(Long id) {
        productRepository.deleteById(id);
    }

    // Clear entire cache
    @CacheEvict(value = "products", allEntries = true)
    public void refreshCatalog() {
        log.info("Product cache cleared");
    }
}
```

## Cache Managers — In-Memory with Caffeine

```xml
<!-- pom.xml -->
<dependency>
    <groupId>com.github.ben-manes.caffeine</groupId>
    <artifactId>caffeine</artifactId>
</dependency>
```

```yaml
# application.yml
spring:
  cache:
    type: caffeine
    caffeine:
      spec: maximumSize=1000,expireAfterWrite=10m
```

Per-cache TTL configuration:

```java
@Configuration
public class CacheConfig {

    @Bean
    public CacheManager cacheManager() {
        var manager = new SimpleCacheManager();
        manager.setCaches(List.of(
            buildCache("products", 500, Duration.ofMinutes(30)),
            buildCache("users", 200, Duration.ofMinutes(5)),
            buildCache("config", 50, Duration.ofHours(1))
        ));
        return manager;
    }

    private CaffeineCache buildCache(String name, int maxSize, Duration ttl) {
        return new CaffeineCache(name, Caffeine.newBuilder()
            .maximumSize(maxSize)
            .expireAfterWrite(ttl)
            .recordStats()
            .build());
    }
}
```

## Redis Cache — Distributed Caching

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

```yaml
spring:
  data:
    redis:
      host: ${REDIS_HOST:localhost}
      port: 6379
  cache:
    type: redis
    redis:
      time-to-live: 600000  # 10 minutes in ms
      key-prefix: "myapp:"
      use-key-prefix: true
```

Custom Redis TTL per cache:

```java
@Configuration
public class RedisCacheConfig {

    @Bean
    public RedisCacheManager cacheManager(RedisConnectionFactory factory) {
        var defaultConfig = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(10))
            .serializeValuesWith(SerializationPair.fromSerializer(
                new GenericJackson2JsonRedisSerializer()));

        return RedisCacheManager.builder(factory)
            .cacheDefaults(defaultConfig)
            .withCacheConfiguration("sessions",
                defaultConfig.entryTtl(Duration.ofMinutes(30)))
            .withCacheConfiguration("static-data",
                defaultConfig.entryTtl(Duration.ofHours(24)))
            .build();
    }
}
```

## Cache Warming on Startup

```java
@Component
@RequiredArgsConstructor
@Slf4j
public class CacheWarmer implements ApplicationRunner {
    private final ProductService productService;
    private final CategoryRepository categoryRepository;

    @Override
    public void run(ApplicationArguments args) {
        log.info("Warming caches...");
        categoryRepository.findAll().forEach(cat ->
            productService.search(cat.getName(), 0)  // Triggers @Cacheable
        );
        log.info("Cache warming complete");
    }
}
```

## What You Learned

- **@Cacheable** — cache method results by key, skip method on hit
- **@CacheEvict** — invalidate on write, `allEntries` for full clear
- **@CachePut** — update cache without skipping the method
- **Caffeine** — in-memory cache with TTL, max size, stats
- **Redis** — distributed cache with JSON serialization
- **Per-cache TTL** — different expiration per cache name
- **Cache warming** — `ApplicationRunner` to pre-populate on startup

---

[← Chapter 5: Async](chapter-05-async.md) | [Chapter 7: Testing →](chapter-07-testing.md)

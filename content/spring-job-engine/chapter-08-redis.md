# Chapter 8: Redis Caching

[← Chapter 7: Audit](/blog/spring-job-engine/chapter-07-audit) | [Chapter 9: Kafka →](/blog/spring-job-engine/chapter-09-kafka)

---

## The Story

Users keep hitting "refresh" to check job status. Each request hits the database. With 1000 active jobs and impatient users, the DB is sweating. Redis to the rescue — cache hot data in memory.

## Step 1: Redis Configuration

```java
@Configuration
@EnableCaching
public class RedisConfig {

    @Bean
    public RedisCacheManager cacheManager(RedisConnectionFactory factory) {
        RedisCacheConfiguration config = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofSeconds(30))  // cache for 30s
            .serializeValuesWith(
                SerializationPair.fromSerializer(new GenericJackson2JsonRedisSerializer())
            );

        return RedisCacheManager.builder(factory)
            .cacheDefaults(config)
            .withCacheConfiguration("jobs",
                config.entryTtl(Duration.ofSeconds(5)))  // job status: 5s TTL
            .withCacheConfiguration("results",
                config.entryTtl(Duration.ofMinutes(30)))  // results: 30min TTL
            .build();
    }
}
```

## Step 2: Caching Job Status

```java
@Service
public class JobService {

    @Cacheable(value = "jobs", key = "#id")
    public Job getJob(String id) {
        return repo.findById(id).orElseThrow();
    }

    @CacheEvict(value = "jobs", key = "#id")
    public Job transition(String id, JobStatus target) {
        Job job = repo.findById(id).orElseThrow();
        stateMachine.transition(job, target);
        return repo.save(job);
    }

    @CachePut(value = "jobs", key = "#id")
    public Job updateProgress(String id, int progress) {
        Job job = repo.findById(id).orElseThrow();
        job.setProgress(progress);
        return repo.save(job);
    }
}
```

| Annotation    | Behavior                                              |
| ------------- | ----------------------------------------------------- |
| `@Cacheable`  | Return cached value if exists, else execute and cache |
| `@CacheEvict` | Remove from cache (on state change)                   |
| `@CachePut`   | Always execute and update cache                       |

## Step 3: Caching Job Results

Completed job results rarely change — cache them longer:

```java
@Cacheable(value = "results", key = "#id", condition = "#result.status == 'COMPLETED'")
public JobResult getResult(String id) {
    Job job = repo.findById(id).orElseThrow();
    return new JobResult(job.getId(), job.getResult(), job.getCompletedAt());
}
```

## Step 4: Redis for Real-Time Job State

Beyond caching, use Redis as a live state store for progress:

```java
@Service
public class JobProgressStore {

    private final StringRedisTemplate redis;

    public void updateProgress(String jobId, int progress) {
        redis.opsForValue().set("job:progress:" + jobId, String.valueOf(progress),
            Duration.ofMinutes(5));
    }

    public int getProgress(String jobId) {
        String val = redis.opsForValue().get("job:progress:" + jobId);
        return val != null ? Integer.parseInt(val) : 0;
    }

    public void setRunning(String jobId) {
        redis.opsForSet().add("jobs:running", jobId);
    }

    public void removeRunning(String jobId) {
        redis.opsForSet().remove("jobs:running", jobId);
    }

    public Set<String> getRunningJobs() {
        return redis.opsForSet().members("jobs:running");
    }
}
```

This gives you:

- **Real-time progress** without DB writes every second
- **Running job set** — O(1) lookup for "is this job running?"
- **Auto-expiry** — stale data cleans itself up

## Step 5: Distributed Locking

Prevent two instances from picking the same job:

```java
@Service
public class JobLockService {

    private final StringRedisTemplate redis;

    public boolean acquireLock(String jobId, Duration timeout) {
        Boolean acquired = redis.opsForValue()
            .setIfAbsent("lock:job:" + jobId, "locked", timeout);
        return Boolean.TRUE.equals(acquired);
    }

    public void releaseLock(String jobId) {
        redis.delete("lock:job:" + jobId);
    }
}

// In the scheduler:
public void pollAndExecute() {
    List<Job> jobs = jobService.getQueuedJobs(10);
    for (Job job : jobs) {
        if (lockService.acquireLock(job.getId(), Duration.ofMinutes(5))) {
            jobExecutor.execute(job);
        }
        // else: another instance grabbed it
    }
}
```

## Cache Strategy Summary

```
Request → Redis Cache (5s TTL)
              │
              ├── HIT → return immediately (no DB)
              │
              └── MISS → PostgreSQL → cache result → return
```

---

[Chapter 9: Kafka Event Streaming →](/blog/spring-job-engine/chapter-09-kafka)

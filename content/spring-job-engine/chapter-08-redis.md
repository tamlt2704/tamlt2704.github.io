# Chapter 8: Redis Caching

[← Chapter 7: Audit](/blog/spring-job-engine/chapter-07-audit) | [Chapter 9: Kafka →](/blog/spring-job-engine/chapter-09-kafka)

---

## The Story

Users keep hitting "refresh" to check job status. Each request hits the database. With 1000 active jobs and impatient users, the DB is sweating. Redis to the rescue — cache hot data in memory.

## Step 1: Redis Configuration

```java
// config/RedisConfig.java
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

> **Note:** Add these annotations to the existing `JobService` from Chapter 2. This shows how the same methods gain caching behavior.

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
// service/JobProgressStore.java
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

### Why Is This Needed?

With a single instance, Spring Integration's in-memory channels guarantee one consumer per message. But when you scale to multiple instances (e.g., 2 pods in Kubernetes), each has its own channels and both poll the **same database**:

```
Instance A: SELECT * FROM jobs WHERE status = 'QUEUED' → gets job-7a3f
Instance B: SELECT * FROM jobs WHERE status = 'QUEUED' → also gets job-7a3f
                                                          ↑ race condition!
```

Spring Integration can't help here — its channels are local to each JVM. The database is the shared state.

### Solutions Compared

| Approach                           | How                                                           | Tradeoff                                     |
| ---------------------------------- | ------------------------------------------------------------- | -------------------------------------------- |
| **Redis lock** (below)             | `SETNX` — first one wins                                      | Fast, but lock can expire while job runs     |
| **DB optimistic lock**             | `UPDATE ... WHERE status='QUEUED'` — only one UPDATE succeeds | No extra infra, but DB contention under load |
| **Kafka partitioning** (Chapter 9) | Each job goes to one partition → one consumer                 | Best for scale, but adds Kafka dependency    |

Redis lock is the middle ground — lightweight, fast, works across instances without changing the DB query pattern.

### Implementation

Prevent two instances from picking the same job:

```java
// service/JobLockService.java
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

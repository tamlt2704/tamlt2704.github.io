# Chapter 3: Java Multithreading & Thread Pools

[← Chapter 2: Job Model](/blog/spring-job-engine/chapter-02-job-model) | [Chapter 4: Spring Integration →](/blog/spring-job-engine/chapter-04-spring-integration)

---

## The Story

You have jobs in a queue. But running them one-by-one is too slow. The system needs to process 4, 8, 16 jobs simultaneously. You need a thread pool — a team of workers picking tasks from a shared queue.

## The Concepts

```
┌─────────────────────────────────────────────┐
│              ThreadPoolExecutor              │
│                                             │
│  Queue: [Job5] [Job6] [Job7] [Job8] ...    │
│                                             │
│  Workers:                                   │
│    Thread-1: ████████░░ Job1 (80%)          │
│    Thread-2: ███░░░░░░░ Job2 (30%)          │
│    Thread-3: █████████░ Job3 (90%)          │
│    Thread-4: ░░░░░░░░░░ idle                │
│                                             │
│  Core: 4 | Max: 16 | Queue: 100            │
└─────────────────────────────────────────────┘
```

## Step 1: Thread Pool Configuration

```java
@Configuration
public class ThreadPoolConfig {

    @Value("${job-engine.thread-pool.core-size:4}")
    private int coreSize;

    @Value("${job-engine.thread-pool.max-size:16}")
    private int maxSize;

    @Value("${job-engine.thread-pool.queue-capacity:100}")
    private int queueCapacity;

    @Bean("jobExecutor")
    public ThreadPoolTaskExecutor jobExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(coreSize);
        executor.setMaxPoolSize(maxSize);
        executor.setQueueCapacity(queueCapacity);
        executor.setThreadNamePrefix("job-worker-");
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.setWaitForTasksToCompleteOnShutdown(true);
        executor.setAwaitTerminationSeconds(30);
        executor.initialize();
        return executor;
    }
}
```

Key settings:

- **coreSize** — always-alive threads (even when idle)
- **maxSize** — maximum threads under load
- **queueCapacity** — jobs waiting when all threads are busy
- **CallerRunsPolicy** — if queue is full, the submitting thread runs the job (backpressure)
- **WaitForTasksToComplete** — graceful shutdown waits for running jobs

## Step 2: The Job Executor

```java
@Service
public class JobExecutor {

    private final ThreadPoolTaskExecutor executor;
    private final JobService jobService;
    private final Map<String, Future<?>> runningJobs = new ConcurrentHashMap<>();

    public JobExecutor(@Qualifier("jobExecutor") ThreadPoolTaskExecutor executor,
                       JobService jobService) {
        this.executor = executor;
        this.jobService = jobService;
    }

    public void execute(Job job) {
        Future<?> future = executor.submit(() -> {
            Thread.currentThread().setName("job-" + job.getId());
            try {
                jobService.transition(job.getId(), JobStatus.RUNNING);
                doWork(job);
                jobService.transition(job.getId(), JobStatus.COMPLETED);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                jobService.transition(job.getId(), JobStatus.CANCELLED);
            } catch (Exception e) {
                job.setResult(e.getMessage());
                jobService.transition(job.getId(), JobStatus.FAILED);
            } finally {
                runningJobs.remove(job.getId());
            }
        });
        runningJobs.put(job.getId(), future);
    }

    public boolean cancel(String jobId) {
        Future<?> future = runningJobs.get(jobId);
        if (future != null) {
            return future.cancel(true);  // interrupt the thread
        }
        return false;
    }

    private void doWork(Job job) throws InterruptedException {
        // Simulate work with progress updates
        for (int i = 0; i <= 100; i += 10) {
            if (Thread.currentThread().isInterrupted()) {
                throw new InterruptedException("Job cancelled");
            }
            job.setProgress(i);
            jobService.updateProgress(job.getId(), i);
            Thread.sleep(500);  // simulate processing
        }
    }
}
```

## Step 3: Understanding Thread Safety

Multiple threads access shared state. Here's what can go wrong and how we prevent it:

```java
// WRONG — race condition
private int activeJobs = 0;
activeJobs++;  // not atomic!

// RIGHT — atomic operations
private final AtomicInteger activeJobs = new AtomicInteger(0);
activeJobs.incrementAndGet();

// WRONG — shared mutable map
private Map<String, Future<?>> jobs = new HashMap<>();  // not thread-safe!

// RIGHT — concurrent map
private final Map<String, Future<?>> jobs = new ConcurrentHashMap<>();
```

## Step 4: The Scheduler (Polling for Jobs)

```java
@Component
public class JobScheduler {

    private final JobService jobService;
    private final JobExecutor jobExecutor;
    private final ThreadPoolTaskExecutor executor;

    @Scheduled(fixedDelay = 1000)  // check every second
    public void pollAndExecute() {
        int available = executor.getMaxPoolSize() - executor.getActiveCount();
        if (available <= 0) return;  // all workers busy

        List<Job> jobs = jobService.getQueuedJobs(available);
        jobs.forEach(jobExecutor::execute);
    }
}
```

This is the heartbeat — every second, it checks for capacity and fills it with queued jobs.

## Step 5: Virtual Threads (Java 21)

For I/O-heavy jobs (HTTP calls, DB queries), virtual threads are game-changing:

```java
@Bean("virtualExecutor")
public ExecutorService virtualExecutor() {
    return Executors.newVirtualThreadPerTaskExecutor();
}
```

Virtual threads are lightweight — you can have millions. Use them for jobs that wait on I/O. Use platform threads (ThreadPoolExecutor) for CPU-bound work.

```java
// Choose executor based on job type
public void execute(Job job) {
    Executor exec = job.getType().endsWith("_IO")
        ? virtualExecutor
        : platformExecutor;

    exec.execute(() -> doWork(job));
}
```

## Step 6: Monitoring the Pool

```java
@RestController
@RequestMapping("/api/engine")
public class EngineController {

    private final ThreadPoolTaskExecutor executor;

    @GetMapping("/status")
    public Map<String, Object> status() {
        return Map.of(
            "activeThreads", executor.getActiveCount(),
            "poolSize", executor.getPoolSize(),
            "queueSize", executor.getThreadPoolExecutor().getQueue().size(),
            "completedTasks", executor.getThreadPoolExecutor().getCompletedTaskCount()
        );
    }
}
```

## Key Concepts Summary

| Concept             | What                | Why                                       |
| ------------------- | ------------------- | ----------------------------------------- |
| ThreadPoolExecutor  | Reuses threads      | Creating threads is expensive             |
| ConcurrentHashMap   | Thread-safe map     | Multiple threads read/write job state     |
| AtomicInteger       | Lock-free counter   | Track active jobs without synchronization |
| Future.cancel(true) | Interrupt a thread  | Allows job cancellation                   |
| CallerRunsPolicy    | Backpressure        | Prevents OOM when queue is full           |
| Virtual Threads     | Lightweight threads | Scale I/O-bound work to millions          |

## Next

We'll wire this into Spring Integration — channels, routers, and message-driven flows that orchestrate the entire pipeline.

[Chapter 4: Spring Integration Flows →](/blog/spring-job-engine/chapter-04-spring-integration)

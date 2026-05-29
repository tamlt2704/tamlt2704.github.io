# Chapter 5: Priority, Pause & Resume

[← Chapter 4: Spring Integration](/blog/spring-job-engine/chapter-04-spring-integration) | [Chapter 6: JWT Auth →](/blog/spring-job-engine/chapter-06-jwt-auth)

---

## The Story

The system is running. Spring Integration routes jobs by priority into separate channels (Chapter 4). But you need more control:

- **Dynamic reprioritization** — a job is already queued as LOW, but the CEO wants it NOW
- **Pause/Resume** — a runaway job is eating CPU; pause it without losing progress
- **Cancellation** — kill a job cleanly, not by restarting the server

Chapter 4 handles _initial_ priority routing. This chapter handles _runtime_ control over jobs that are already in-flight or queued.

## Step 1: Priority Queue (Runtime Reprioritization)

Spring Integration's `PriorityChannel` sorts on insertion, but doesn't support changing priority after the fact. For dynamic reprioritization, we use a `PriorityBlockingQueue` wrapper:

```java
// service/PriorityJobQueue.java
@Component
public class PriorityJobQueue {

    private final PriorityBlockingQueue<Job> queue = new PriorityBlockingQueue<>(
        100,
        Comparator.comparingInt((Job j) -> -j.getPriority().getWeight())
            .thenComparing(Job::getSubmittedAt)
    );

    public void enqueue(Job job) {
        queue.offer(job);
    }

    public Job poll() {
        return queue.poll();
    }

    public int size() {
        return queue.size();
    }

    public boolean reprioritize(String jobId, JobPriority newPriority) {
        // Remove and re-insert with new priority
        Iterator<Job> it = queue.iterator();
        while (it.hasNext()) {
            Job j = it.next();
            if (j.getId().equals(jobId)) {
                it.remove();
                j.setPriority(newPriority);
                queue.offer(j);
                return true;
            }
        }
        return false;
    }
}
```

`PriorityBlockingQueue` — thread-safe, sorted by priority weight (descending), then by submission time (FIFO within same priority).

### Wiring It In

The `PriorityJobQueue` replaces the database polling from Chapter 3's `JobScheduler`. Jobs enter here after Spring Integration routes them:

```java
// In JobIntegrationFlow — route normal jobs into the priority queue instead of executing directly
.handle(m -> priorityJobQueue.enqueue((Job) m.getPayload()))
```

The scheduler now pulls from this in-memory queue:

```java
@Scheduled(fixedDelay = 500)
public void drainQueue() {
    int available = executor.getMaxPoolSize() - executor.getActiveCount();
    while (available-- > 0) {
        Job job = priorityJobQueue.poll();
        if (job == null) break;
        jobExecutor.execute(job);
    }
}
```

## Step 2: Pause & Resume with Cooperative Cancellation

Jobs must check a flag periodically:

```java
// model/PausableJob.java
public abstract class PausableJob implements Runnable {

    private volatile boolean paused = false;
    private volatile boolean cancelled = false;
    private final Object pauseLock = new Object();

    protected void checkPausePoint() throws InterruptedException {
        if (cancelled) throw new InterruptedException("Job cancelled");
        synchronized (pauseLock) {
            while (paused) {
                pauseLock.wait();  // block until resumed
            }
        }
    }

    public void pause() {
        paused = true;
    }

    public void resume() {
        synchronized (pauseLock) {
            paused = false;
            pauseLock.notifyAll();  // wake up the waiting thread
        }
    }

    public void cancel() {
        cancelled = true;
        resume();  // unblock if paused, so it can exit
    }
}
```

## Step 3: Integrating Pause into Job Execution

```java
public class ReportJob extends PausableJob {

    private final Job jobEntity;

    @Override
    public void run() {
        for (int i = 0; i < 100; i++) {
            checkPausePoint();  // ← cooperative pause point
            processChunk(i);
            jobEntity.setProgress(i);
        }
    }
}
```

The job checks `checkPausePoint()` at natural boundaries. If paused, the thread sleeps (not spinning). If cancelled, it throws and exits cleanly.

## Step 4: The Controller

```java
// controller/JobController.java (add these endpoints to the existing JobController)
@PostMapping("/api/jobs/{id}/pause")
public Job pauseJob(@PathVariable String id) {
    jobExecutor.pause(id);
    return jobService.transition(id, JobStatus.PAUSED);
}

@PostMapping("/api/jobs/{id}/resume")
public Job resumeJob(@PathVariable String id) {
    jobExecutor.resume(id);
    return jobService.transition(id, JobStatus.RUNNING);
}

@PostMapping("/api/jobs/{id}/cancel")
public Job cancelJob(@PathVariable String id) {
    jobExecutor.cancel(id);
    return jobService.transition(id, JobStatus.CANCELLED);
}

@PatchMapping("/api/jobs/{id}/priority")
public Job reprioritize(@PathVariable String id, @RequestBody Map<String, String> body) {
    JobPriority newPriority = JobPriority.valueOf(body.get("priority"));
    priorityQueue.reprioritize(id, newPriority);
    return jobService.updatePriority(id, newPriority);
}
```

```java
// Add to service/JobService.java
// Add to JobService in chapter 2
public Job updatePriority(String id, JobPriority priority) {
    Job job = getJob(id);
    job.setPriority(priority);
    return repo.save(job);
}
```

## Step 5: Tracking Pausable Jobs

```java
@Service
public class JobExecutor {

    private final Map<String, PausableJob> activeJobs = new ConcurrentHashMap<>();

    // Create the appropriate PausableJob based on job type
    public void execute(Job job) {
        PausableJob runnable = createPausableJob(job);
        activeJobs.put(job.getId(), runnable);
        executor.submit(() -> {
            try {
                runnable.run();
            } finally {
                activeJobs.remove(job.getId());
            }
        });
    }

    private PausableJob createPausableJob(Job job) {
        // Factory method — extend for different job types
        return new ReportJob(job);
    }

    public void pause(String jobId) {
        PausableJob job = activeJobs.get(jobId);
        if (job != null) job.pause();
    }

    public void resume(String jobId) {
        PausableJob job = activeJobs.get(jobId);
        if (job != null) job.resume();
    }
}
```

## Key Insight: Cooperative vs Preemptive

| Approach             | How                    | Tradeoff                         |
| -------------------- | ---------------------- | -------------------------------- |
| `Thread.interrupt()` | Preemptive             | Can corrupt state if not handled |
| `volatile flag`      | Cooperative            | Job must check periodically      |
| `wait/notify`        | Cooperative + blocking | Thread sleeps (no CPU waste)     |

We use cooperative (wait/notify) because it's safe — the job pauses at known-good points.

---

[Chapter 6: JWT Authentication →](/blog/spring-job-engine/chapter-06-jwt-auth)

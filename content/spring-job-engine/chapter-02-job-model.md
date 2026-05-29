# Chapter 2: The Job Model

[← Chapter 1: Spring Boot](/blog/spring-job-engine/chapter-01-spring-boot) | [Chapter 3: Threading →](/blog/spring-job-engine/chapter-03-threading)

---

## The Story

Before you can run jobs, you need to define what a job _is_. The PM asks: "What states can a job be in? Can it fail? Can it be retried?" You sketch on a whiteboard.

## The State Machine

```
                    ┌─────────┐
         submit     │ QUEUED  │
        ────────▶   └────┬────┘
                         │ pick up
                         ▼
                    ┌─────────┐
         pause      │ RUNNING │──────▶ COMPLETED
        ◀──────    └────┬────┘
        │                │
        ▼                ▼
   ┌─────────┐     ┌─────────┐
   │ PAUSED  │     │ FAILED  │
   └────┬────┘     └────┬────┘
        │ resume        │ retry
        ▼               ▼
   ┌─────────┐     ┌─────────┐
   │ RUNNING │     │ QUEUED  │
   └─────────┘     └─────────┘

   Any state ──cancel──▶ CANCELLED
```

## Step 1: The Status Enum

```java
// model/JobStatus.java
public enum JobStatus {
    QUEUED,
    RUNNING,
    PAUSED,
    COMPLETED,
    FAILED,
    CANCELLED;

    public boolean isTerminal() {
        return this == COMPLETED || this == FAILED || this == CANCELLED;
    }
}
```

## Step 2: The Priority Enum

```java
// model/JobPriority.java
public enum JobPriority {
    LOW(1),
    MEDIUM(5),
    HIGH(10),
    CRITICAL(20);

    private final int weight;

    JobPriority(int weight) { this.weight = weight; }
    public int getWeight() { return weight; }
}
```

## Step 3: The Job Entity

```java
// model/Job.java
@Entity
@Table(name = "jobs")
public class Job {

    @Id
    private String id;

    @Column(nullable = false)
    private String type;  // e.g. "RISK_REPORT", "DATA_EXPORT"

    @Enumerated(EnumType.STRING)
    private JobStatus status = JobStatus.QUEUED;

    @Enumerated(EnumType.STRING)
    private JobPriority priority = JobPriority.MEDIUM;

    @Column(columnDefinition = "jsonb")
    private String params;  // JSON payload

    private String submittedBy;  // user email from JWT
    private String result;       // output or error message
    private int progress;        // 0-100

    private Instant submittedAt;
    private Instant startedAt;
    private Instant completedAt;

    @Version
    private Long version;  // optimistic locking

    @PrePersist
    void onCreate() {
        if (id == null) id = "job-" + UUID.randomUUID().toString().substring(0, 8);
        if (submittedAt == null) submittedAt = Instant.now();
    }

    // Getters, setters, builder pattern...
}
```

Key design decisions:

- **`@Version`** — optimistic locking prevents two threads from updating the same job
- **`params` as JSON** — flexible payload without schema changes
- **`progress`** — jobs can report 0-100% completion

## Step 4: The Repository

```java
// repository/JobRepository.java
public interface JobRepository extends JpaRepository<Job, String> {

    List<Job> findByStatusOrderByPriorityDesc(JobStatus status);

    List<Job> findBySubmittedBy(String user);

    @Query("SELECT j FROM Job j WHERE j.status = 'QUEUED' ORDER BY j.priority DESC, j.submittedAt ASC")
    List<Job> findNextJobs(Pageable pageable);
}
```

The `findNextJobs` query is the heart of the scheduler — it picks the highest priority, oldest job first.

## Step 5: State Transitions

Not every transition is valid. Enforce it:

```java
// service/JobStateMachine.java
@Service
public class JobStateMachine {

    private static final Map<JobStatus, Set<JobStatus>> TRANSITIONS = Map.of(
        JobStatus.QUEUED, Set.of(JobStatus.RUNNING, JobStatus.CANCELLED),
        JobStatus.RUNNING, Set.of(JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.PAUSED, JobStatus.CANCELLED),
        JobStatus.PAUSED, Set.of(JobStatus.RUNNING, JobStatus.CANCELLED),
        JobStatus.FAILED, Set.of(JobStatus.QUEUED),  // retry
        JobStatus.COMPLETED, Set.of(),
        JobStatus.CANCELLED, Set.of()
    );

    public void transition(Job job, JobStatus target) {
        Set<JobStatus> allowed = TRANSITIONS.getOrDefault(job.getStatus(), Set.of());
        if (!allowed.contains(target)) {
            throw new IllegalStateException(
                "Cannot transition from " + job.getStatus() + " to " + target
            );
        }
        job.setStatus(target);
    }
}
```

## Step 6: The Job Service

```java
// service/JobService.java
@Service
@Transactional
public class JobService {

    private final JobRepository repo;
    private final JobStateMachine stateMachine;

    public Job submit(String type, JobPriority priority, String params, String user) {
        Job job = new Job();
        job.setType(type);
        job.setPriority(priority);
        job.setParams(params);
        job.setSubmittedBy(user);
        return repo.save(job);
    }

    // JobRequest is defined in Chapter 4
    public Job create(JobRequest request) {
        return submit(request.type(), request.priority(), request.params(), null);
    }

    public Job getJob(String id) {
        return repo.findById(id)
            .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND));
    }

    public Job transition(String id, JobStatus target) {
        Job job = getJob(id);
        stateMachine.transition(job, target);
        return repo.save(job);
    }

    public List<Job> getQueuedJobs(int limit) {
        return repo.findNextJobs(PageRequest.of(0, limit));
    }

    public void updateProgress(String id, int progress) {
        Job job = getJob(id);
        job.setProgress(progress);
        repo.save(job);
    }
}
```

## What We Have

- Job entity with states, priority, progress, timestamps
- State machine enforcing valid transitions
- Repository with priority-based querying
- Service layer for business logic

## The Pattern

```
Controller → Service → StateMachine → Repository → Database
                                          ↓
                                    Optimistic Lock
                                    (prevents race conditions)
```

## Next

We'll build the engine that actually _runs_ these jobs — thread pools, executors, and concurrent processing.

[Chapter 3: Java Multithreading & Thread Pools →](/blog/spring-job-engine/chapter-03-threading)

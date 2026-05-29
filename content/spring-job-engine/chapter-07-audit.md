# Chapter 7: Audit Trail

[← Chapter 6: JWT Auth](/blog/spring-job-engine/chapter-06-jwt-auth) | [Chapter 8: Redis →](/blog/spring-job-engine/chapter-08-redis)

---

## The Story

Compliance asks: "Who submitted that job? When was it cancelled? Who changed the priority?" You need an immutable audit log — every action recorded with who, what, when.

## Step 1: The Audit Entity

```java
// model/AuditLog.java
@Entity
@Table(name = "audit_logs")
public class AuditLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String jobId;
    private String action;      // SUBMITTED, STARTED, PAUSED, RESUMED, COMPLETED, FAILED, CANCELLED
    private String performedBy;  // user email or "system"
    private String details;      // extra context (e.g. "priority changed from LOW to HIGH")
    private Instant timestamp;

    @PrePersist
    void onCreate() {
        if (timestamp == null) timestamp = Instant.now();
    }
}
```

```java
// repository/AuditRepository.java
public interface AuditRepository extends JpaRepository<AuditLog, Long> {
    List<AuditLog> findByJobIdOrderByTimestampAsc(String jobId);
    List<AuditLog> findByPerformedBy(String user);
    List<AuditLog> findTop100ByOrderByTimestampDesc();
}
```

## Step 2: The Audit Service

```java
// service/AuditService.java
@Service
public class AuditService {

    private final AuditRepository repo;
    private final ApplicationEventPublisher publisher;

    @Async
    public void log(String jobId, String action, String performedBy, String details) {
        AuditLog entry = new AuditLog();
        entry.setJobId(jobId);
        entry.setAction(action);
        entry.setPerformedBy(performedBy);
        entry.setDetails(details);
        repo.save(entry);
    }

    public List<AuditLog> getHistory(String jobId) {
        return repo.findByJobIdOrderByTimestampAsc(jobId);
    }
}
```

`@Async` — audit logging happens on a separate thread. It never slows down the main job flow.

## Step 3: JPA Event Listener (Automatic Auditing)

### JPA Lifecycle Callbacks

JPA fires events at specific points in an entity's lifecycle. You annotate methods to hook into them:

| Annotation        | When it fires                             |
| ----------------- | ----------------------------------------- |
| `@PrePersist`     | Before `INSERT` (entity first saved)      |
| `@PostPersist`    | After `INSERT` completes                  |
| `@PreUpdate`      | Before `UPDATE` (entity modified + flush) |
| **`@PostUpdate`** | **After `UPDATE` completes successfully** |
| `@PreRemove`      | Before `DELETE`                           |
| `@PostRemove`     | After `DELETE` completes                  |
| `@PostLoad`       | After entity is loaded from DB            |

**How `@PostUpdate` works:**

```
jobService.transition(id, RUNNING)
    → job.setStatus(RUNNING)
    → repo.save(job)
        → Hibernate detects dirty field (status changed)
        → executes UPDATE SQL
        → UPDATE succeeds
        → fires @PostUpdate → onUpdate(job) ← your audit code runs here
```

Key points:

- It fires **after** the SQL update, but **within the same transaction** — if the transaction rolls back, the audit entry is also lost
- It fires on **any field change**, not just status — your listener receives the entity in its new state
- It does **not** give you the old value — if you need "changed from X to Y", you must track it yourself (e.g., `@Transient` field or Hibernate Envers)

```java
// model/JobEntityListener.java
@Component
public class JobEntityListener {

    private static AuditService auditService;

    @Autowired
    public void setAuditService(AuditService service) {
        JobEntityListener.auditService = service;
    }

    @PostUpdate
    public void onUpdate(Job job) {
        // Detect status changes
        auditService.log(
            job.getId(),
            job.getStatus().name(),
            getCurrentUser(),
            "Status changed to " + job.getStatus()
        );
    }

    private String getCurrentUser() {
        var auth = SecurityContextHolder.getContext().getAuthentication();
        return auth != null ? auth.getName() : "system";
    }
}
```

Add `@EntityListeners(JobEntityListener.class)` to the Job entity. Every status change is automatically audited.

## Step 4: Spring AOP for Method-Level Auditing

### What is AOP?

**Aspect-Oriented Programming** lets you inject behavior (logging, auditing, security) into methods _without modifying them_. Instead of adding audit code inside every service method, you define it once in an Aspect and declare _where_ it applies.

```
Without AOP:                          With AOP:
┌──────────────────────┐              ┌──────────────────────┐
│ reprioritize() {     │              │ reprioritize() {     │
│   auditLog(...)  ←── │ duplicated   │   // just business   │
│   // business logic  │ everywhere   │   // logic           │
│ }                    │              │ }                    │
│                      │              │                      │
│ cancel() {           │              │ @Audited ← one       │
│   auditLog(...)  ←── │              │ annotation triggers  │
│   // business logic  │              │ the aspect           │
│ }                    │              └──────────────────────┘
└──────────────────────┘
```

### Key AOP Concepts

| Term          | Meaning                                                                           |
| ------------- | --------------------------------------------------------------------------------- |
| **Aspect**    | The class containing cross-cutting logic (`@Aspect`)                              |
| **Advice**    | When to run: `@Before`, `@After`, `@AfterReturning`, `@AfterThrowing`, `@Around`  |
| **Pointcut**  | Where to apply: which methods match (e.g., `@annotation(Audited)`)                |
| **JoinPoint** | The actual method being intercepted — gives you access to args, method name, etc. |

### How it executes

```
Client calls reprioritize("job-7a3f", HIGH)
    │
    ▼
Spring Proxy intercepts (because @Audited is present)
    │
    ▼
Original method runs → returns result
    │
    ▼
@AfterReturning fires → AuditAspect.audit() logs the action
```

> **Important:** AOP only works on Spring-managed beans called from _outside_ the class. If `methodA()` calls `methodB()` within the same class, the proxy is bypassed and `@Audited` on `methodB` won't fire.

### Custom annotation + Aspect

```java
// audit/Audited.java
// The annotation — marks methods that should be audited
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface Audited {
    String action();  // e.g. "PRIORITY_CHANGED", "JOB_CANCELLED"
}
```

```java
// audit/AuditAspect.java
@Aspect
@Component
public class AuditAspect {

    private final AuditService auditService;

    // returning = "result" binds the intercepted method's return value
    // to the parameter named "result" below. The name must match exactly.
    // e.g., if reprioritize() returns a Job, then result = that Job object
    @AfterReturning(pointcut = "@annotation(Audited)", returning = "result")
    public void audit(JoinPoint jp, Object result) {
        Audited annotation = ((MethodSignature) jp.getSignature())
            .getMethod().getAnnotation(Audited.class);

        String user = SecurityContextHolder.getContext().getAuthentication().getName();
        String action = annotation.action();
        String jobId = extractJobId(jp.getArgs());

        auditService.log(jobId, action, user, null);
    }

    private String extractJobId(Object[] args) {
        if (args.length > 0 && args[0] instanceof String) {
            return (String) args[0];  // first arg is jobId by convention
        }
        return "unknown";
    }
}

// Usage:
@Audited(action = "PRIORITY_CHANGED")
public Job reprioritize(String id, JobPriority priority) { ... }
```

### All Audit Actions in This System

| Action             | When                           | Triggered by | Captured via        |
| ------------------ | ------------------------------ | ------------ | ------------------- |
| `SUBMITTED`        | Job created via POST /api/jobs | User         | `@Audited`          |
| `STARTED`          | Job picked up by executor      | System       | `@PostUpdate` (JPA) |
| `COMPLETED`        | Job finishes successfully      | System       | `@PostUpdate` (JPA) |
| `FAILED`           | Job throws exception           | System       | `@PostUpdate` (JPA) |
| `PAUSED`           | User pauses a running job      | User         | `@Audited`          |
| `RESUMED`          | User resumes a paused job      | User         | `@Audited`          |
| `CANCELLED`        | User or system cancels a job   | User/System  | `@Audited`          |
| `PRIORITY_CHANGED` | Job reprioritized              | User (admin) | `@Audited`          |
| `RETRIED`          | Failed job resubmitted         | User         | `@Audited`          |

User-initiated actions use `@Audited` (AOP) because they come through service methods. System-initiated actions (`STARTED`, `COMPLETED`, `FAILED`) use the `@PostUpdate` JPA listener because they happen inside the executor with no user-facing method call.

```java
// Full @Audited usage across the service layer:
@Audited(action = "SUBMITTED")
public Job create(JobRequest request) { ... }

@Audited(action = "CANCELLED")
public Job cancel(String id) { ... }

@Audited(action = "PAUSED")
public Job pause(String id) { ... }

@Audited(action = "RESUMED")
public Job resume(String id) { ... }

@Audited(action = "RETRIED")
public Job retry(String id) { ... }
```

## Step 5: Query the Audit Trail

```java
// controller/AuditController.java
@RestController
@RequiredArgsConstructor
public class AuditController {

    private final AuditService auditService;
    private final AuditRepository auditRepo;

    @GetMapping("/api/audit")
    public List<AuditLog> getAudit(
        @RequestParam(required = false) String jobId,
        @RequestParam(required = false) String user,
        @RequestParam(required = false) String action) {

        if (jobId != null) return auditService.getHistory(jobId);
        if (user != null) return auditRepo.findByPerformedBy(user);
        return auditRepo.findTop100ByOrderByTimestampDesc();
    }
}
```

```bash
curl /api/audit?jobId=job-7a3f
[
  {"action":"SUBMITTED","performedBy":"alice@co.com","timestamp":"10:30:00"},
  {"action":"STARTED","performedBy":"system","timestamp":"10:30:01"},
  {"action":"PAUSED","performedBy":"alice@co.com","timestamp":"10:31:15"},
  {"action":"RESUMED","performedBy":"bob@co.com","timestamp":"10:32:00"},
  {"action":"COMPLETED","performedBy":"system","timestamp":"10:35:22"}
]
```

## The Pattern

```
User Action → Controller → Service → State Change
                                          │
                              ┌───────────┼───────────┐
                              ▼           ▼           ▼
                         JPA Listener  AOP Aspect  Manual log
                              │           │           │
                              └───────────┼───────────┘
                                          ▼
                                    AuditRepository
                                          │
                                          ▼
                                    audit_logs table
```

---

[Chapter 8: Redis Caching →](/blog/spring-job-engine/chapter-08-redis)

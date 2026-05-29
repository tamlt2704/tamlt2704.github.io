# Chapter 7: Audit Trail

[← Chapter 6: JWT Auth](/blog/spring-job-engine/chapter-06-jwt-auth) | [Chapter 8: Redis →](/blog/spring-job-engine/chapter-08-redis)

---

## The Story

Compliance asks: "Who submitted that job? When was it cancelled? Who changed the priority?" You need an immutable audit log — every action recorded with who, what, when.

## Step 1: The Audit Entity

```java
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

## Step 2: The Audit Service

```java
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

```java
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

```java
@Aspect
@Component
public class AuditAspect {

    private final AuditService auditService;

    @AfterReturning(pointcut = "@annotation(Audited)", returning = "result")
    public void audit(JoinPoint jp, Object result) {
        Audited annotation = ((MethodSignature) jp.getSignature())
            .getMethod().getAnnotation(Audited.class);

        String user = SecurityContextHolder.getContext().getAuthentication().getName();
        String action = annotation.action();
        String jobId = extractJobId(jp.getArgs());

        auditService.log(jobId, action, user, null);
    }
}

// Usage:
@Audited(action = "PRIORITY_CHANGED")
public Job reprioritize(String id, JobPriority priority) { ... }
```

## Step 5: Query the Audit Trail

```java
@GetMapping("/api/audit")
public List<AuditLog> getAudit(
    @RequestParam(required = false) String jobId,
    @RequestParam(required = false) String user,
    @RequestParam(required = false) String action) {

    if (jobId != null) return auditService.getHistory(jobId);
    if (user != null) return auditRepo.findByPerformedBy(user);
    return auditRepo.findTop100ByOrderByTimestampDesc();
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

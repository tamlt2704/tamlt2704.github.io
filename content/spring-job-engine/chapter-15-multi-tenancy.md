# Chapter 15: Multi-Tenancy

[← Chapter 14: Job Dependencies](/blog/spring-job-engine/chapter-14-job-dependencies) | [Chapter 16: Rate Limiting →](/blog/spring-job-engine/chapter-16-rate-limiting)

---

## The Story

Your job engine is a hit. Three different teams want to use it — Risk, Compliance, and Data Engineering. But they shouldn't see each other's jobs. And when Risk submits 500 jobs, it shouldn't starve Compliance's queue. You need multi-tenancy.

## Multi-Tenancy Strategies

| Strategy                     | How                                                 | Tradeoff                             |
| ---------------------------- | --------------------------------------------------- | ------------------------------------ |
| **Shared DB, tenant column** | All tenants in same tables, filtered by `tenant_id` | Simple, but one bad query leaks data |
| **Schema per tenant**        | Same DB, separate schemas                           | Good isolation, moderate complexity  |
| **Database per tenant**      | Completely separate DBs                             | Best isolation, hardest to manage    |

For a job engine, **shared DB with tenant column** is the sweet spot — simple, performant, and the data isn't sensitive enough to warrant full isolation.

## Step 1: Add Tenant to the Model

```java
// In Job.java — add tenant field
@Column(nullable = false)
private String tenantId;  // "risk-team", "compliance", "data-eng"
```

```java
// In JobSchedule.java, Workflow.java, AuditLog.java — same field
@Column(nullable = false)
private String tenantId;
```

## Step 2: Tenant Context (ThreadLocal)

Like `SecurityContextHolder`, we need a way to know the current tenant anywhere in the code:

```java
// context/TenantContext.java
public class TenantContext {

    private static final ThreadLocal<String> currentTenant = new ThreadLocal<>();

    public static String getTenant() {
        return currentTenant.get();
    }

    public static void setTenant(String tenantId) {
        currentTenant.set(tenantId);
    }

    public static void clear() {
        currentTenant.remove();
    }
}
```

## Step 3: Extract Tenant from JWT

Add `tenantId` as a claim in the token:

```java
// In JwtTokenProvider — add tenant claim
public String generateToken(String email, String role, String tenantId) {
    return Jwts.builder()
        .subject(email)
        .claim("role", role)
        .claim("tenant", tenantId)
        .issuedAt(new Date())
        .expiration(new Date(System.currentTimeMillis() + expiration))
        .signWith(Keys.hmacShaKeyFor(secret.getBytes()))
        .compact();
}
```

Set the tenant context in the auth filter:

```java
// In JwtAuthFilter — after parsing claims
String tenantId = claims.get("tenant", String.class);
TenantContext.setTenant(tenantId);

// Clear after request completes (add a filter that runs last)
```

```java
// security/TenantCleanupFilter.java
@Component
@Order(Ordered.LOWEST_PRECEDENCE)
public class TenantCleanupFilter extends OncePerRequestFilter {
    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                     HttpServletResponse response,
                                     FilterChain chain) throws ServletException, IOException {
        try {
            chain.doFilter(request, response);
        } finally {
            TenantContext.clear();
        }
    }
}
```

## Step 4: Automatic Tenant Filtering (Hibernate Filter)

Instead of adding `WHERE tenant_id = ?` to every query manually, use Hibernate's `@Filter`:

```java
@Entity
@Table(name = "jobs")
@FilterDef(name = "tenantFilter", parameters = @ParamDef(name = "tenantId", type = String.class))
@Filter(name = "tenantFilter", condition = "tenant_id = :tenantId")
public class Job {
    // ... existing fields
}
```

Enable the filter on every request:

```java
// aspect/TenantFilterAspect.java
@Component
@RequiredArgsConstructor
public class TenantFilterAspect {

    private final EntityManager entityManager;

    @Around("execution(* com.company.jobengine.repository.*.*(..))")
    public Object applyTenantFilter(ProceedingJoinPoint jp) throws Throwable {
        Session session = entityManager.unwrap(Session.class);
        session.enableFilter("tenantFilter")
            .setParameter("tenantId", TenantContext.getTenant());
        try {
            return jp.proceed();
        } finally {
            session.disableFilter("tenantFilter");
        }
    }
}
```

Now every repository query automatically filters by tenant — no code changes needed in services.

## Step 5: Auto-Set Tenant on Create

Use a JPA listener to stamp the tenant on new entities:

```java
// model/TenantEntityListener.java
public class TenantEntityListener {

    @PrePersist
    public void setTenant(Object entity) {
        if (entity instanceof TenantAware ta) {
            ta.setTenantId(TenantContext.getTenant());
        }
    }
}

// Interface for tenant-aware entities
public interface TenantAware {
    void setTenantId(String tenantId);
    String getTenantId();
}
```

```java
// Job implements TenantAware
@Entity
@EntityListeners(TenantEntityListener.class)
public class Job implements TenantAware {
    // ...
}
```

## Step 6: Tenant-Isolated Thread Pools

Prevent one tenant from starving others:

```java
@Configuration
public class TenantThreadPoolConfig {

    @Bean
    public Map<String, ThreadPoolTaskExecutor> tenantExecutors(
            @Value("${job-engine.tenants}") List<String> tenants) {

        Map<String, ThreadPoolTaskExecutor> executors = new HashMap<>();
        for (String tenant : tenants) {
            ThreadPoolTaskExecutor exec = new ThreadPoolTaskExecutor();
            exec.setCorePoolSize(4);
            exec.setMaxPoolSize(8);
            exec.setQueueCapacity(50);
            exec.setThreadNamePrefix("job-" + tenant + "-");
            exec.initialize();
            executors.put(tenant, exec);
        }
        return executors;
    }
}
```

```java
// In JobExecutor — route to tenant's pool
public void execute(Job job) {
    ThreadPoolTaskExecutor exec = tenantExecutors.get(job.getTenantId());
    exec.submit(() -> doWork(job));
}
```

```yaml
# application.yml
job-engine:
  tenants:
    - risk-team
    - compliance
    - data-eng
```

## Step 7: Tenant-Aware Kafka Topics

Option A — shared topic, filter by tenant header:

```java
kafka.send("job.submitted", job.getId(), job)
    .headers(h -> h.add("tenant", job.getTenantId().getBytes()));
```

Option B — topic per tenant (stronger isolation):

```java
kafka.send("job.submitted." + job.getTenantId(), job.getId(), job);
// Topics: job.submitted.risk-team, job.submitted.compliance, etc.
```

## Step 8: Admin Cross-Tenant View

Admins need to see all tenants. Bypass the filter for admin endpoints:

```java
@GetMapping("/api/admin/jobs")
@PreAuthorize("hasRole('SUPER_ADMIN')")
public List<Job> allJobs() {
    // Disable tenant filter for this query
    Session session = entityManager.unwrap(Session.class);
    session.disableFilter("tenantFilter");
    return jobRepo.findAll();
}
```

## Architecture Summary

```
Request → JwtAuthFilter (extract tenant) → TenantContext.set()
                                                │
    ┌───────────────────────────────────────────┼──────────────┐
    │                                           ▼              │
    │  Repository queries ← Hibernate @Filter (auto-applied)   │
    │  New entities ← @PrePersist (auto-stamped)               │
    │  Thread pool ← tenant-specific executor                  │
    │  Kafka ← tenant header or topic                          │
    │                                                          │
    └──────────────────────────────────────────────────────────┘
                                                │
Response ← TenantCleanupFilter (clear context) ←┘
```

---

[Chapter 16: Rate Limiting →](/blog/spring-job-engine/chapter-16-rate-limiting)

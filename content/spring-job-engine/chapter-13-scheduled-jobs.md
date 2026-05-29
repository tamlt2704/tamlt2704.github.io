# Chapter 13: Scheduled & Recurring Jobs

[← Chapter 12: WebSocket](/blog/spring-job-engine/chapter-12-websocket) | [Chapter 14: Job Dependencies →](/blog/spring-job-engine/chapter-14-job-dependencies)

---

## The Story

The compliance team needs a risk report every day at 6 AM. The data team wants hourly exports. Right now, someone manually submits these jobs every morning. You need a scheduler — define once, run forever.

## The Options

| Approach                      | Best for                      | Limitation                      |
| ----------------------------- | ----------------------------- | ------------------------------- |
| `@Scheduled`                  | Simple fixed-rate/delay tasks | No persistence, lost on restart |
| Spring Integration Poller     | Message-driven periodic work  | Tied to channels                |
| **Database-backed scheduler** | Production cron jobs          | You build it (or use Quartz)    |
| Quartz Scheduler              | Enterprise-grade, clustered   | Heavy, complex config           |

For a job engine, we need **persistence** (survives restarts) and **cluster-safety** (only one instance fires the schedule). We'll build a lightweight DB-backed scheduler, then show Quartz as an alternative.

## Step 1: The Schedule Entity

```java
// model/JobSchedule.java
@Entity
@Table(name = "job_schedules")
public class JobSchedule {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;           // "Daily Risk Report"
    private String cronExpression; // "0 0 6 * * *" = 6 AM daily
    private String jobType;        // "RISK_REPORT"

    @Enumerated(EnumType.STRING)
    private JobPriority priority;

    private String params;         // JSON payload
    private String createdBy;      // who set this up
    private boolean enabled;       // toggle on/off

    private Instant lastFiredAt;
    private Instant nextFireAt;

    // getters, setters
}
```

## Step 2: Cron Expression Primer

```
┌───────── second (0-59)
│ ┌─────── minute (0-59)
│ │ ┌───── hour (0-23)
│ │ │ ┌─── day of month (1-31)
│ │ │ │ ┌─ month (1-12)
│ │ │ │ │ ┌─ day of week (0-7, 0=Sun)
│ │ │ │ │ │
* * * * * *
```

| Expression             | Meaning                              |
| ---------------------- | ------------------------------------ |
| `0 0 6 * * *`          | Every day at 6:00 AM                 |
| `0 0 * * * *`          | Every hour on the hour               |
| `0 */15 * * * *`       | Every 15 minutes                     |
| `0 0 9-17 * * MON-FRI` | Every hour 9 AM–5 PM, weekdays only  |
| `0 0 0 1 * *`          | First day of every month at midnight |

Spring uses `CronExpression` to parse and compute the next fire time:

```java
CronExpression cron = CronExpression.parse("0 0 6 * * *");
LocalDateTime next = cron.next(LocalDateTime.now());
// → tomorrow at 06:00:00
```

## Step 3: The Scheduler Service

```java
// service/JobSchedulerService.java
@Service
@RequiredArgsConstructor
public class JobSchedulerService {

    private final JobScheduleRepository scheduleRepo;
    private final JobService jobService;
    private final JobGateway jobGateway;

    // Runs every minute — checks which schedules are due
    @Scheduled(fixedRate = 60_000)
    public void fireScheduledJobs() {
        List<JobSchedule> due = scheduleRepo
            .findByEnabledTrueAndNextFireAtBefore(Instant.now());

        for (JobSchedule schedule : due) {
            // Submit the job
            Job job = jobService.submit(
                schedule.getJobType(),
                schedule.getPriority(),
                schedule.getParams(),
                schedule.getCreatedBy()
            );
            jobGateway.submit(job);

            // Compute next fire time
            CronExpression cron = CronExpression.parse(schedule.getCronExpression());
            LocalDateTime next = cron.next(LocalDateTime.now());
            schedule.setLastFiredAt(Instant.now());
            schedule.setNextFireAt(next.toInstant(ZoneOffset.UTC));
            scheduleRepo.save(schedule);
        }
    }
}
```

## Step 4: Cluster Safety (Only One Instance Fires)

Without protection, all instances fire the same schedule. Use a database lock:

```java
@Scheduled(fixedRate = 60_000)
@Transactional
public void fireScheduledJobs() {
    // Pessimistic lock — only one instance gets the row
    List<JobSchedule> due = scheduleRepo.findDueWithLock(Instant.now());
    // ... same logic
}
```

```java
// Repository with pessimistic locking
public interface JobScheduleRepository extends JpaRepository<JobSchedule, Long> {

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT s FROM JobSchedule s WHERE s.enabled = true AND s.nextFireAt < :now")
    List<JobSchedule> findDueWithLock(@Param("now") Instant now);
}
```

Or use the Redis lock from Chapter 8:

```java
if (lockService.acquireLock("scheduler-tick", Duration.ofSeconds(55))) {
    try {
        fireScheduledJobs();
    } finally {
        lockService.releaseLock("scheduler-tick");
    }
}
```

## Step 5: REST API for Managing Schedules

```java
// controller/ScheduleController.java
@RestController
@RequestMapping("/api/schedules")
@RequiredArgsConstructor
public class ScheduleController {

    private final JobScheduleRepository repo;

    @PostMapping
    @PreAuthorize("hasRole('ADMIN')")
    public JobSchedule create(@RequestBody CreateScheduleRequest request) {
        CronExpression cron = CronExpression.parse(request.cronExpression());
        LocalDateTime next = cron.next(LocalDateTime.now());

        JobSchedule schedule = new JobSchedule();
        schedule.setName(request.name());
        schedule.setCronExpression(request.cronExpression());
        schedule.setJobType(request.jobType());
        schedule.setPriority(request.priority());
        schedule.setParams(request.params());
        schedule.setCreatedBy(SecurityContextHolder.getContext().getAuthentication().getName());
        schedule.setEnabled(true);
        schedule.setNextFireAt(next.toInstant(ZoneOffset.UTC));
        return repo.save(schedule);
    }

    @GetMapping
    public List<JobSchedule> list() {
        return repo.findAll();
    }

    @PatchMapping("/{id}/toggle")
    @PreAuthorize("hasRole('ADMIN')")
    public JobSchedule toggle(@PathVariable Long id) {
        JobSchedule s = repo.findById(id).orElseThrow();
        s.setEnabled(!s.isEnabled());
        return repo.save(s);
    }
}
```

```java
public record CreateScheduleRequest(
    String name,
    String cronExpression,
    String jobType,
    JobPriority priority,
    String params
) {}
```

## Step 6: Quartz Alternative

For enterprise features (misfired job handling, complex triggers, persistent job data), use Quartz:

```kotlin
// build.gradle.kts
implementation("org.springframework.boot:spring-boot-starter-quartz")
```

```java
// Define a Quartz job
public class ReportQuartzJob implements org.quartz.Job {
    @Override
    public void execute(JobExecutionContext context) {
        String jobType = context.getMergedJobDataMap().getString("jobType");
        // delegate to your existing JobService
    }
}

// Schedule it
@Bean
public JobDetail reportJobDetail() {
    return JobBuilder.newJob(ReportQuartzJob.class)
        .withIdentity("dailyReport")
        .usingJobData("jobType", "RISK_REPORT")
        .storeDurably()
        .build();
}

@Bean
public Trigger reportTrigger() {
    return TriggerBuilder.newTrigger()
        .forJob(reportJobDetail())
        .withSchedule(CronScheduleBuilder.cronSchedule("0 0 6 * * ?"))
        .build();
}
```

```yaml
# application.yml — Quartz with JDBC store (cluster-safe)
spring:
  quartz:
    job-store-type: jdbc
    properties:
      org.quartz.jobStore.isClustered: true
      org.quartz.jobStore.clusterCheckinInterval: 20000
```

### When to Use What

| Feature           | Custom (our approach)            | Quartz               |
| ----------------- | -------------------------------- | -------------------- |
| Simplicity        | ✅ Simple, you control it        | ❌ Heavy config      |
| Cluster-safe      | Manual (DB lock / Redis)         | ✅ Built-in          |
| Misfire handling  | You build it                     | ✅ Built-in policies |
| Dynamic schedules | ✅ REST API + DB                 | Possible but verbose |
| Dependencies      | Your job engine already has this | Separate concept     |

---

[Chapter 14: Job Dependencies →](/blog/spring-job-engine/chapter-14-job-dependencies)

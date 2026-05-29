# Chapter 14: Job Dependencies (DAG)

[← Chapter 13: Scheduled Jobs](/blog/spring-job-engine/chapter-13-scheduled-jobs) | [Chapter 15: Multi-Tenancy →](/blog/spring-job-engine/chapter-15-multi-tenancy)

---

## The Story

The data pipeline team says: "We can't run the Risk Report until the Market Data Import finishes. And the Final Summary needs both the Risk Report AND the Compliance Check to complete first." You need job dependencies — a DAG (Directed Acyclic Graph).

## What's a DAG?

```
┌──────────────┐
│ Market Data  │
│   Import     │
└──────┬───────┘
       │ completes
       ▼
┌──────────────┐     ┌──────────────┐
│ Risk Report  │     │  Compliance  │
│              │     │    Check     │
└──────┬───────┘     └──────┬───────┘
       │                     │
       └──────────┬──────────┘
                  │ both complete
                  ▼
          ┌──────────────┐
          │   Final      │
          │   Summary    │
          └──────────────┘
```

- **Directed** — edges have direction (A must finish before B)
- **Acyclic** — no circular dependencies (A→B→A is invalid)
- **Graph** — nodes (jobs) connected by edges (dependencies)

## Step 1: Model Dependencies

```java
// model/JobDependency.java
@Entity
@Table(name = "job_dependencies")
public class JobDependency {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String jobId;          // the job that waits
    private String dependsOnJobId; // the job it waits for
    private boolean satisfied;     // true when dependsOn completes

    // getters, setters
}
```

Add to the Job entity:

```java
// In Job.java
@OneToMany(mappedBy = "jobId", cascade = CascadeType.ALL)
private List<JobDependency> dependencies = new ArrayList<>();

private String parentWorkflowId;  // groups related jobs together
```

## Step 2: The Workflow (Job Group)

A workflow is a collection of jobs with dependencies:

```java
// model/Workflow.java
@Entity
@Table(name = "workflows")
public class Workflow {

    @Id
    private String id;

    private String name;           // "Daily Pipeline"
    private String createdBy;

    @Enumerated(EnumType.STRING)
    private WorkflowStatus status; // PENDING, RUNNING, COMPLETED, FAILED

    private Instant createdAt;
    private Instant completedAt;
}

public enum WorkflowStatus {
    PENDING, RUNNING, COMPLETED, FAILED
}
```

## Step 3: Submitting a Workflow

```java
public record WorkflowRequest(
    String name,
    List<WorkflowStep> steps
) {}

public record WorkflowStep(
    String id,              // local reference: "step-1"
    String jobType,
    String params,
    List<String> dependsOn  // ["step-0"] — references other steps
) {}
```

```java
// service/WorkflowService.java
@Service
@RequiredArgsConstructor
public class WorkflowService {

    private final JobService jobService;
    private final JobDependencyRepository depRepo;
    private final WorkflowRepository workflowRepo;

    @Transactional
    public Workflow submit(WorkflowRequest request, String user) {
        Workflow workflow = new Workflow();
        workflow.setId("wf-" + UUID.randomUUID().toString().substring(0, 8));
        workflow.setName(request.name());
        workflow.setCreatedBy(user);
        workflow.setStatus(WorkflowStatus.PENDING);
        workflow.setCreatedAt(Instant.now());
        workflowRepo.save(workflow);

        // Create all jobs, map step IDs to real job IDs
        Map<String, String> stepToJobId = new HashMap<>();
        for (WorkflowStep step : request.steps()) {
            Job job = jobService.submit(step.jobType(), JobPriority.MEDIUM, step.params(), user);
            job.setParentWorkflowId(workflow.getId());
            // Jobs with dependencies start as WAITING (not QUEUED)
            if (!step.dependsOn().isEmpty()) {
                job.setStatus(JobStatus.WAITING);
            }
            stepToJobId.put(step.id(), job.getId());
        }

        // Wire dependencies
        for (WorkflowStep step : request.steps()) {
            String jobId = stepToJobId.get(step.id());
            for (String dep : step.dependsOn()) {
                JobDependency dependency = new JobDependency();
                dependency.setJobId(jobId);
                dependency.setDependsOnJobId(stepToJobId.get(dep));
                dependency.setSatisfied(false);
                depRepo.save(dependency);
            }
        }

        // Start jobs with no dependencies
        workflow.setStatus(WorkflowStatus.RUNNING);
        workflowRepo.save(workflow);
        triggerReady(workflow.getId());

        return workflow;
    }
}
```

## Step 4: Triggering Downstream Jobs

When a job completes, check if any waiting jobs are now unblocked:

```java
// service/DependencyResolver.java
@Service
@RequiredArgsConstructor
public class DependencyResolver {

    private final JobDependencyRepository depRepo;
    private final JobService jobService;
    private final JobGateway jobGateway;
    private final WorkflowRepository workflowRepo;

    // Called when any job completes
    public void onJobCompleted(String completedJobId) {
        // Mark this dependency as satisfied everywhere it appears
        List<JobDependency> deps = depRepo.findByDependsOnJobId(completedJobId);
        for (JobDependency dep : deps) {
            dep.setSatisfied(true);
            depRepo.save(dep);
        }

        // Find jobs whose ALL dependencies are now satisfied
        List<String> unblockedJobIds = depRepo.findFullySatisfiedJobs();
        for (String jobId : unblockedJobIds) {
            Job job = jobService.getJob(jobId);
            if (job.getStatus() == JobStatus.WAITING) {
                jobService.transition(jobId, JobStatus.QUEUED);
                jobGateway.submit(job);
            }
        }

        // Check if workflow is complete
        checkWorkflowCompletion(completedJobId);
    }

    public void onJobFailed(String failedJobId) {
        // Fail all downstream jobs that depend on this one
        List<JobDependency> downstream = depRepo.findByDependsOnJobId(failedJobId);
        for (JobDependency dep : downstream) {
            jobService.transition(dep.getJobId(), JobStatus.FAILED);
            // Cascade: fail their dependents too
            onJobFailed(dep.getJobId());
        }

        // Mark workflow as failed
        Job failed = jobService.getJob(failedJobId);
        if (failed.getParentWorkflowId() != null) {
            Workflow wf = workflowRepo.findById(failed.getParentWorkflowId()).orElseThrow();
            wf.setStatus(WorkflowStatus.FAILED);
            workflowRepo.save(wf);
        }
    }

    private void checkWorkflowCompletion(String jobId) {
        Job job = jobService.getJob(jobId);
        if (job.getParentWorkflowId() == null) return;

        List<Job> workflowJobs = jobService.getByWorkflow(job.getParentWorkflowId());
        boolean allDone = workflowJobs.stream()
            .allMatch(j -> j.getStatus().isTerminal());

        if (allDone) {
            Workflow wf = workflowRepo.findById(job.getParentWorkflowId()).orElseThrow();
            wf.setStatus(WorkflowStatus.COMPLETED);
            wf.setCompletedAt(Instant.now());
            workflowRepo.save(wf);
        }
    }
}
```

## Step 5: Repository Queries

```java
// Add to service/JobService.java
public List<Job> getByWorkflow(String workflowId) {
    return repo.findByParentWorkflowId(workflowId);
}
```

```java
// Add to repository/JobRepository.java
List<Job> findByParentWorkflowId(String workflowId);
```

```java
public interface JobDependencyRepository extends JpaRepository<JobDependency, Long> {

    List<JobDependency> findByDependsOnJobId(String dependsOnJobId);

    List<JobDependency> findByJobId(String jobId);

    // Jobs where ALL dependencies are satisfied
    @Query("""
        SELECT d.jobId FROM JobDependency d
        GROUP BY d.jobId
        HAVING COUNT(CASE WHEN d.satisfied = false THEN 1 END) = 0
    """)
    List<String> findFullySatisfiedJobs();
}
```

## Step 6: Hook into Job Completion

Wire the resolver into the existing executor flow:

```java
// In JobExecutor — after job completes
jobService.transition(job.getId(), JobStatus.COMPLETED);
dependencyResolver.onJobCompleted(job.getId());

// After job fails
jobService.transition(job.getId(), JobStatus.FAILED);
dependencyResolver.onJobFailed(job.getId());
```

Or via Spring Integration:

```java
@Bean
public IntegrationFlow completionFlow() {
    return IntegrationFlow
        .from("jobCompletionChannel")
        .handle(message -> {
            Job job = (Job) message.getPayload();
            if (job.getStatus() == JobStatus.COMPLETED) {
                dependencyResolver.onJobCompleted(job.getId());
            } else if (job.getStatus() == JobStatus.FAILED) {
                dependencyResolver.onJobFailed(job.getId());
            }
        })
        .get();
}
```

## Step 7: DAG Validation (Cycle Detection)

Prevent circular dependencies at submission time:

```java
public void validateNoCycles(List<WorkflowStep> steps) {
    Map<String, List<String>> graph = new HashMap<>();
    for (WorkflowStep step : steps) {
        graph.put(step.id(), step.dependsOn());
    }

    Set<String> visited = new HashSet<>();
    Set<String> inStack = new HashSet<>();

    for (String node : graph.keySet()) {
        if (hasCycle(node, graph, visited, inStack)) {
            throw new IllegalArgumentException("Circular dependency detected");
        }
    }
}

private boolean hasCycle(String node, Map<String, List<String>> graph,
                         Set<String> visited, Set<String> inStack) {
    if (inStack.contains(node)) return true;  // back edge = cycle
    if (visited.contains(node)) return false;

    visited.add(node);
    inStack.add(node);

    for (String dep : graph.getOrDefault(node, List.of())) {
        if (hasCycle(dep, graph, visited, inStack)) return true;
    }

    inStack.remove(node);
    return false;
}
```

## Step 8: REST API

```java
@PostMapping("/api/workflows")
public Workflow submitWorkflow(@RequestBody WorkflowRequest request) {
    workflowService.validateNoCycles(request.steps());
    String user = SecurityContextHolder.getContext().getAuthentication().getName();
    return workflowService.submit(request, user);
}

@GetMapping("/api/workflows/{id}")
public Map<String, Object> getWorkflow(@PathVariable String id) {
    Workflow wf = workflowRepo.findById(id).orElseThrow();
    List<Job> jobs = jobService.getByWorkflow(id);
    return Map.of("workflow", wf, "jobs", jobs);
}
```

### Example Request

```bash
curl -X POST /api/workflows \
  -H "Authorization: Bearer <jwt>" \
  -d '{
    "name": "Daily Pipeline",
    "steps": [
      {"id": "import", "jobType": "MARKET_DATA_IMPORT", "params": "{}", "dependsOn": []},
      {"id": "risk", "jobType": "RISK_REPORT", "params": "{}", "dependsOn": ["import"]},
      {"id": "compliance", "jobType": "COMPLIANCE_CHECK", "params": "{}", "dependsOn": ["import"]},
      {"id": "summary", "jobType": "FINAL_SUMMARY", "params": "{}", "dependsOn": ["risk", "compliance"]}
    ]
  }'
```

## New Job Status: WAITING

Add to the `JobStatus` enum:

```java
public enum JobStatus {
    WAITING,    // has unmet dependencies
    QUEUED,     // ready to run
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

Update the state machine to allow `WAITING → QUEUED` transition.

---

[Chapter 15: Multi-Tenancy →](/blog/spring-job-engine/chapter-15-multi-tenancy)

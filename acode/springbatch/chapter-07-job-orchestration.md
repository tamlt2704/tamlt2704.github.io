# Chapter 7: The Pipeline — Job Orchestration and Flows

[← Chapter 6: The Deadline](chapter-06-partitioning.md) | [Chapter 8: The Dashboard →](chapter-08-monitoring.md)

---

## The Incident

Month-end. Director Compliance has a checklist:

1. Reconcile all transactions (must succeed)
2. Calculate end-of-day positions (must succeed)
3. Generate regulatory report (if it has warnings, alert compliance but continue)
4. Archive processed files (always run, even if report failed)
5. Send completion notification (only if everything succeeded)

Right now, these are 5 separate jobs triggered by 5 separate cron entries. Last month, the position calculation ran before reconciliation finished. The report used stale data. The auditors noticed.

Director Compliance: "I need these to run in order. With conditions. As one unit. Can you do that?"

You can. Spring Batch flows let you orchestrate steps with conditional logic, branching, and decision points.

## Flows: Sequential and Conditional

A **Flow** is a sequence of steps with transitions between them. Transitions can be conditional — based on the exit status of the previous step.

```
┌─────────────────────────────────────────────────────────────┐
│ Month-End Job                                                │
│                                                               │
│  reconcileStep ──── COMPLETED ────► positionStep             │
│       │                                  │                    │
│       │                             COMPLETED                 │
│    FAILED                                │                    │
│       │                                  ▼                    │
│       ▼                           reportStep                  │
│    STOP JOB                              │                    │
│                              ┌───────────┼───────────┐       │
│                              │           │           │       │
│                         COMPLETED   WITH_WARNINGS  FAILED    │
│                              │           │           │       │
│                              ▼           ▼           ▼       │
│                          archiveStep  alertStep   archiveStep │
│                              │           │           │       │
│                              ▼           ▼           │       │
│                          notifyStep  archiveStep     │       │
│                                          │           │       │
│                                          ▼           │       │
│                                      notifyStep      │       │
│                                                      ▼       │
│                                                   STOP JOB   │
└─────────────────────────────────────────────────────────────┘
```

## Building the Flow

```java
// src/main/java/com/megabank/config/MonthEndJobConfig.java
package com.megabank.config;

import org.springframework.batch.core.Job;
import org.springframework.batch.core.Step;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class MonthEndJobConfig {

    @Bean
    public Job monthEndJob(JobRepository jobRepository,
                            Step reconcileStep,
                            Step positionStep,
                            Step reportStep,
                            Step alertStep,
                            Step archiveStep,
                            Step notifyStep) {
        return new JobBuilder("monthEndJob", jobRepository)
            .start(reconcileStep)
                .on("FAILED").fail()              // reconciliation fails → job fails
            .from(reconcileStep)
                .on("*").to(positionStep)         // any other status → continue
            .from(positionStep)
                .on("FAILED").fail()
            .from(positionStep)
                .on("*").to(reportStep)
            .from(reportStep)
                .on("COMPLETED_WITH_WARNINGS").to(alertStep)
            .from(reportStep)
                .on("FAILED").to(archiveStep)     // archive even on failure
            .from(reportStep)
                .on("*").to(archiveStep)
            .from(alertStep)
                .on("*").to(archiveStep)
            .from(archiveStep)
                .on("*").to(notifyStep)
            .end()
            .build();
    }
}
```

### Transition Rules

| Pattern | Meaning |
|---|---|
| `.on("COMPLETED")` | Exact match on exit status |
| `.on("FAILED")` | Exact match on FAILED |
| `.on("*")` | Wildcard — matches anything |
| `.on("COMPLETED*")` | Prefix match (COMPLETED, COMPLETED_WITH_WARNINGS) |
| `.fail()` | Stop the job with FAILED status |
| `.stop()` | Stop the job with STOPPED status (restartable) |
| `.end()` | Stop the job with COMPLETED status |

## Custom Exit Status: The Report Step

The report step needs to return `COMPLETED_WITH_WARNINGS` when there are data quality issues:

```java
// src/main/java/com/megabank/listener/ReportStepListener.java
package com.megabank.listener;

import org.springframework.batch.core.ExitStatus;
import org.springframework.batch.core.StepExecution;
import org.springframework.batch.core.StepExecutionListener;

public class ReportStepListener implements StepExecutionListener {

    @Override
    public ExitStatus afterStep(StepExecution stepExecution) {
        long skipCount = stepExecution.getSkipCount();
        long readCount = stepExecution.getReadCount();

        if (skipCount > 0) {
            double skipPercentage = (double) skipCount / readCount * 100;
            if (skipPercentage > 1.0) {
                return new ExitStatus("COMPLETED_WITH_WARNINGS")
                    .addExitDescription(
                        String.format("%.1f%% of records had issues", skipPercentage));
            }
        }

        return stepExecution.getExitStatus(); // default
    }
}
```

## JobExecutionDecider: Complex Branching

For more complex decisions that don't map to exit statuses, use a `JobExecutionDecider`:

```java
// src/main/java/com/megabank/decider/BusinessDayDecider.java
package com.megabank.decider;

import org.springframework.batch.core.JobExecution;
import org.springframework.batch.core.StepExecution;
import org.springframework.batch.core.job.flow.FlowExecutionStatus;
import org.springframework.batch.core.job.flow.JobExecutionDecider;

import java.time.DayOfWeek;
import java.time.LocalDate;

public class BusinessDayDecider implements JobExecutionDecider {

    @Override
    public FlowExecutionStatus decide(JobExecution jobExecution, StepExecution stepExecution) {
        LocalDate today = LocalDate.now();

        if (today.getDayOfWeek() == DayOfWeek.SATURDAY
                || today.getDayOfWeek() == DayOfWeek.SUNDAY) {
            return new FlowExecutionStatus("WEEKEND");
        }

        if (isLastBusinessDay(today)) {
            return new FlowExecutionStatus("MONTH_END");
        }

        return new FlowExecutionStatus("NORMAL_DAY");
    }

    private boolean isLastBusinessDay(LocalDate date) {
        LocalDate lastDay = date.withDayOfMonth(date.lengthOfMonth());
        while (lastDay.getDayOfWeek() == DayOfWeek.SATURDAY
                || lastDay.getDayOfWeek() == DayOfWeek.SUNDAY) {
            lastDay = lastDay.minusDays(1);
        }
        return date.equals(lastDay);
    }
}
```

Use it in the job:

```java
@Bean
public Job dailyJob(JobRepository jobRepository,
                     JobExecutionDecider businessDayDecider,
                     Step dailyReconcileStep,
                     Step monthEndReportStep,
                     Step weekendMaintenanceStep) {
    return new JobBuilder("dailyJob", jobRepository)
        .start(dailyReconcileStep)
        .next(businessDayDecider)
            .on("MONTH_END").to(monthEndReportStep)
        .from(businessDayDecider)
            .on("WEEKEND").to(weekendMaintenanceStep)
        .from(businessDayDecider)
            .on("NORMAL_DAY").end()
        .end()
        .build();
}
```

Monday through Thursday: reconcile and stop. Last business day: reconcile + month-end report. Weekend: reconcile + maintenance.

## Nested Jobs: Job-within-a-Job

For complex pipelines, you can nest entire jobs as steps:

```java
@Bean
public Step reconciliationJobStep(JobRepository jobRepository,
                                    JobLauncher jobLauncher,
                                    Job reconciliationJob) {
    return new StepBuilder("reconciliationJobStep", jobRepository)
        .job(reconciliationJob)
        .parametersExtractor(new DefaultJobParametersExtractor())
        .build();
}

@Bean
public Job masterPipelineJob(JobRepository jobRepository,
                              Step reconciliationJobStep,
                              Step positionJobStep,
                              Step reportJobStep) {
    return new JobBuilder("masterPipelineJob", jobRepository)
        .start(reconciliationJobStep)
        .next(positionJobStep)
        .next(reportJobStep)
        .build();
}
```

Each nested job has its own execution metadata, its own restartability, its own step history. The master job orchestrates them.

## Stop and Restart: Graceful Pause

Sometimes you need to stop a running pipeline and restart it later (deploy a fix, wait for data):

```java
@Bean
public Job stoppableJob(JobRepository jobRepository,
                         Step step1,
                         Step step2,
                         Step step3) {
    return new JobBuilder("stoppableJob", jobRepository)
        .start(step1)
            .on("COMPLETED").to(step2)
        .from(step1)
            .on("STOPPED").stop()  // ← stop here, restartable
        .from(step2)
            .on("*").to(step3)
        .end()
        .build();
}
```

To stop a running job programmatically:

```java
@PostMapping("/jobs/{executionId}/stop")
public String stopJob(@PathVariable Long executionId) throws Exception {
    jobOperator.stop(executionId);
    return "Stop signal sent";
}
```

The job finishes its current chunk, then stops with status STOPPED. On restart, it resumes from step2.

## The Test: Conditional Flow

```java
@Test
void monthEndJob_shouldRunAllSteps_whenReconciliationSucceeds() throws Exception {
    JobExecution execution = jobLauncherTestUtils.launchJob(defaultParams());

    assertThat(execution.getStatus()).isEqualTo(BatchStatus.COMPLETED);
    assertThat(stepNames(execution)).containsExactly(
        "reconcileStep", "positionStep", "reportStep", "archiveStep", "notifyStep");
}

@Test
void monthEndJob_shouldStop_whenReconciliationFails() throws Exception {
    reconcileProcessor.setAlwaysFail(true);

    JobExecution execution = jobLauncherTestUtils.launchJob(defaultParams());

    assertThat(execution.getStatus()).isEqualTo(BatchStatus.FAILED);
    assertThat(stepNames(execution)).containsExactly("reconcileStep");
    // positionStep never ran
}

@Test
void monthEndJob_shouldAlert_whenReportHasWarnings() throws Exception {
    // Inject data that causes >1% skip rate in report step
    injectBadData(200); // out of 10,000 = 2%

    JobExecution execution = jobLauncherTestUtils.launchJob(defaultParams());

    assertThat(execution.getStatus()).isEqualTo(BatchStatus.COMPLETED);
    assertThat(stepNames(execution)).contains("alertStep");
}

@Test
void monthEndJob_shouldArchive_evenWhenReportFails() throws Exception {
    reportProcessor.setAlwaysFail(true);

    JobExecution execution = jobLauncherTestUtils.launchJob(defaultParams());

    // Report failed, but archive still ran
    assertThat(stepNames(execution)).contains("archiveStep");
}

private List<String> stepNames(JobExecution execution) {
    return execution.getStepExecutions().stream()
        .map(StepExecution::getStepName)
        .toList();
}
```

## Scheduling: Cron Triggers

Wire the job to a schedule:

```java
// src/main/java/com/megabank/scheduler/BatchScheduler.java
package com.megabank.scheduler;

import org.springframework.batch.core.Job;
import org.springframework.batch.core.JobParameters;
import org.springframework.batch.core.JobParametersBuilder;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.time.LocalDate;

@Component
@EnableScheduling
public class BatchScheduler {

    private final JobLauncher jobLauncher;
    private final Job reconciliationJob;
    private final Job monthEndJob;

    public BatchScheduler(JobLauncher jobLauncher,
                           Job reconciliationJob,
                           Job monthEndJob) {
        this.jobLauncher = jobLauncher;
        this.reconciliationJob = reconciliationJob;
        this.monthEndJob = monthEndJob;
    }

    @Scheduled(cron = "0 0 5 * * MON-FRI") // 5:00 AM weekdays
    public void runDailyReconciliation() throws Exception {
        JobParameters params = new JobParametersBuilder()
            .addString("date", LocalDate.now().minusDays(1).toString())
            .toJobParameters();
        jobLauncher.run(reconciliationJob, params);
    }

    @Scheduled(cron = "0 0 4 L * ?") // 4:00 AM last day of month
    public void runMonthEnd() throws Exception {
        JobParameters params = new JobParametersBuilder()
            .addString("month", LocalDate.now().toString().substring(0, 7))
            .toJobParameters();
        jobLauncher.run(monthEndJob, params);
    }
}
```

## What You Learned

- **Conditional transitions** — `.on("STATUS").to(step)` for branching logic
- **Custom exit statuses** — `COMPLETED_WITH_WARNINGS`, `NEEDS_REVIEW`, etc.
- **`JobExecutionDecider`** — complex branching without modifying step logic
- **`.fail()`** — stop job with FAILED status
- **`.stop()`** — stop job with STOPPED status (restartable from this point)
- **`.end()`** — stop job with COMPLETED status
- **Parallel flows** — `split(executor).add(flows)` for independent steps
- **Nested jobs** — orchestrate entire jobs as steps in a master pipeline
- **Programmatic stop** — `jobOperator.stop(executionId)` for graceful pause
- **Scheduling** — `@Scheduled(cron = "...")` for automated triggers

The month-end pipeline now runs as one coordinated unit. Reconciliation must succeed before positions are calculated. Reports with warnings trigger alerts. Archives always run. Director Compliance has his ordered, auditable pipeline.

But Admiral Uptime asks: "How do I know if last night's jobs succeeded without checking logs at 6 AM?"

He wants a dashboard. Metrics. Alerts. That's Chapter 8.

---

[← Chapter 6: The Deadline](chapter-06-partitioning.md) | [Chapter 8: The Dashboard →](chapter-08-monitoring.md)

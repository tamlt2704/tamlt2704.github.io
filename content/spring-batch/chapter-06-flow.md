# Chapter 6: Job Flow Control

[prev: Writers](chapter-05-writers.md) | [next: Error Handling](chapter-07-error-handling.md)

## Sequential Steps

The simplest flow — steps execute one after another.

```java
@Bean
public Job sequentialJob(JobRepository jobRepository,
                         Step extractStep, Step transformStep, Step loadStep) {
    return new JobBuilder("etlJob", jobRepository)
            .start(extractStep)
            .next(transformStep)
            .next(loadStep)
            .build();
}
```

## Conditional Flow

Route to different steps based on the exit status of the previous step.

```java
@Bean
public Job conditionalJob(JobRepository jobRepository,
                          Step validateStep, Step processStep,
                          Step errorStep, Step reportStep) {
    return new JobBuilder("conditionalJob", jobRepository)
            .start(validateStep)
                .on("FAILED").to(errorStep)
                .on("*").to(processStep)
            .from(processStep)
                .on("*").to(reportStep)
            .end()
            .build();
}
```

### Custom Exit Status

Set a custom exit status from within a step:

```java
@Bean
public Step validateStep(JobRepository jobRepository,
                         PlatformTransactionManager transactionManager) {
    return new StepBuilder("validateStep", jobRepository)
            .tasklet((contribution, chunkContext) -> {
                boolean valid = performValidation();
                if (!valid) {
                    contribution.setExitStatus(new ExitStatus("INVALID"));
                }
                return RepeatStatus.FINISHED;
            }, transactionManager)
            .build();
}
```

Then route on it:

```java
.start(validateStep)
    .on("INVALID").to(rejectStep)
    .on("*").to(processStep)
```

## Split (Parallel Steps)

Execute multiple steps in parallel using a `TaskExecutor`.

```java
@Bean
public Job parallelJob(JobRepository jobRepository,
                       Step loadCustomers, Step loadOrders, Step loadProducts,
                       Step mergeStep) {
    Flow customerFlow = new FlowBuilder<SimpleFlow>("customerFlow")
            .start(loadCustomers).build();
    Flow orderFlow = new FlowBuilder<SimpleFlow>("orderFlow")
            .start(loadOrders).build();
    Flow productFlow = new FlowBuilder<SimpleFlow>("productFlow")
            .start(loadProducts).build();

    Flow parallelFlow = new FlowBuilder<SimpleFlow>("parallelFlow")
            .split(new SimpleAsyncTaskExecutor())
            .add(customerFlow, orderFlow, productFlow)
            .build();

    return new JobBuilder("parallelJob", jobRepository)
            .start(parallelFlow)
            .next(mergeStep)
            .end()
            .build();
}
```

## JobExecutionDecider

Programmatic flow decisions without relying on step exit status.

```java
public class FileExistsDecider implements JobExecutionDecider {

    private final String filePath;

    public FileExistsDecider(String filePath) {
        this.filePath = filePath;
    }

    @Override
    public FlowExecutionStatus decide(JobExecution jobExecution, StepExecution stepExecution) {
        if (Files.exists(Path.of(filePath))) {
            return new FlowExecutionStatus("FILE_FOUND");
        }
        return new FlowExecutionStatus("NO_FILE");
    }
}
```

Use in job definition:

```java
@Bean
public JobExecutionDecider fileDecider() {
    return new FileExistsDecider("/data/input.csv");
}

@Bean
public Job deciderJob(JobRepository jobRepository,
                      JobExecutionDecider fileDecider,
                      Step processFileStep, Step generateFileStep, Step reportStep) {
    return new JobBuilder("deciderJob", jobRepository)
            .start(fileDecider)
                .on("FILE_FOUND").to(processFileStep)
                .on("NO_FILE").to(generateFileStep)
            .from(processFileStep).on("*").to(reportStep)
            .from(generateFileStep).on("*").to(reportStep)
            .end()
            .build();
}
```

## Nested Jobs (Job within a Job)

Launch a job as a step within another job using `JobStep`.

```java
@Bean
public Step nestedJobStep(JobRepository jobRepository, JobLauncher jobLauncher, Job childJob) {
    return new StepBuilder("nestedJobStep", jobRepository)
            .job(childJob)
            .launcher(jobLauncher)
            .build();
}

@Bean
public Job parentJob(JobRepository jobRepository, Step setupStep, Step nestedJobStep, Step cleanupStep) {
    return new JobBuilder("parentJob", jobRepository)
            .start(setupStep)
            .next(nestedJobStep)
            .next(cleanupStep)
            .build();
}
```

## Step Listeners

Execute logic before and after a step.

### Using Annotations

```java
@Component
public class StepTimingListener {

    private long startTime;

    @BeforeStep
    public void beforeStep(StepExecution stepExecution) {
        startTime = System.currentTimeMillis();
        System.out.println("Starting step: " + stepExecution.getStepName());
    }

    @AfterStep
    public ExitStatus afterStep(StepExecution stepExecution) {
        long duration = System.currentTimeMillis() - startTime;
        System.out.println("Step completed in " + duration + "ms. " +
                "Read: " + stepExecution.getReadCount() +
                ", Written: " + stepExecution.getWriteCount() +
                ", Skipped: " + stepExecution.getSkipCount());
        return stepExecution.getExitStatus();
    }
}
```

Register on the step:

```java
@Bean
public Step importStep(JobRepository jobRepository,
                       PlatformTransactionManager transactionManager,
                       ItemReader<Person> reader,
                       ItemWriter<Person> writer,
                       StepTimingListener listener) {
    return new StepBuilder("importStep", jobRepository)
            .<Person, Person>chunk(500, transactionManager)
            .reader(reader)
            .writer(writer)
            .listener(listener)
            .build();
}
```

### Using Interface

```java
public class PromotionListener implements StepExecutionListener {

    @Override
    public void beforeStep(StepExecution stepExecution) {
        // access ExecutionContext to pass data between steps
    }

    @Override
    public ExitStatus afterStep(StepExecution stepExecution) {
        // promote data to job execution context
        stepExecution.getJobExecution().getExecutionContext()
                .putInt("processedCount", (int) stepExecution.getWriteCount());
        return stepExecution.getExitStatus();
    }
}
```

## Job Listeners

Execute logic before and after the entire job.

```java
@Component
public class JobCompletionListener implements JobExecutionListener {

    @Override
    public void beforeJob(JobExecution jobExecution) {
        System.out.println("Job " + jobExecution.getJobInstance().getJobName() + " starting");
    }

    @Override
    public void afterJob(JobExecution jobExecution) {
        if (jobExecution.getStatus() == BatchStatus.COMPLETED) {
            System.out.println("Job completed successfully");
        } else if (jobExecution.getStatus() == BatchStatus.FAILED) {
            System.out.println("Job FAILED: " +
                    jobExecution.getAllFailureExceptions().stream()
                            .map(Throwable::getMessage)
                            .collect(Collectors.joining(", ")));
        }
    }
}
```

Register on the job:

```java
@Bean
public Job importJob(JobRepository jobRepository, Step importStep,
                     JobCompletionListener listener) {
    return new JobBuilder("importJob", jobRepository)
            .listener(listener)
            .start(importStep)
            .build();
}
```

## Exercises

1. Build a job with conditional flow: validate a file, process it if valid, send an error notification if invalid.
2. Create a parallel job that loads data from 3 different CSV files simultaneously, then merges results in a final step.
3. Implement a `JobExecutionDecider` that checks if today is a weekday and routes to different processing logic on weekends.
4. Use step listeners to pass the count of processed records from step 1 to step 2 via the job ExecutionContext.

# Chapter 5: Scheduling & Async — Background Work Done Right

[← Chapter 4: Errors](chapter-04-errors.md) | [Chapter 6: Caching →](chapter-06-caching.md)

---

## The Problem

"I need a job that runs every night at 2am. I need to send emails without blocking the HTTP response. My async methods silently swallow exceptions."

## @Scheduled — Recurring Tasks

Enable scheduling first:

```java
@SpringBootApplication
@EnableScheduling
public class MyApp { }
```

```java
@Component
@Slf4j
public class ScheduledTasks {

    // Fixed rate — every 5 minutes regardless of execution time
    @Scheduled(fixedRate = 300_000)
    public void pollExternalApi() {
        log.info("Polling external API...");
    }

    // Fixed delay — 5 minutes AFTER the last execution finishes
    @Scheduled(fixedDelay = 300_000, initialDelay = 10_000)
    public void processQueue() {
        log.info("Processing queue...");
    }

    // Cron — every weekday at 2:00 AM
    @Scheduled(cron = "0 0 2 * * MON-FRI")
    public void generateDailyReport() {
        log.info("Generating daily report...");
    }

    // Cron from properties (externalize schedule)
    @Scheduled(cron = "${app.cleanup.cron:0 0 3 * * *}")
    public void cleanupExpiredSessions() {
        log.info("Cleaning up expired sessions...");
    }
}
```

Cron cheat sheet: `second minute hour day-of-month month day-of-week`

## @Async — Non-Blocking Method Calls

Enable async:

```java
@SpringBootApplication
@EnableAsync
public class MyApp { }
```

```java
@Service
@Slf4j
public class NotificationService {

    // Fire-and-forget — caller doesn't wait
    @Async
    public void sendWelcomeEmail(String email) {
        // This runs on a separate thread
        emailClient.send(email, "Welcome!", buildTemplate());
        log.info("Welcome email sent to {}", email);
    }

    // Return a future — caller can optionally wait
    @Async
    public CompletableFuture<PricingResult> fetchPricing(String productId) {
        PricingResult result = pricingApi.getPrice(productId);
        return CompletableFuture.completedFuture(result);
    }
}
```

Usage — parallel API calls:

```java
@RestController
@RequiredArgsConstructor
public class ProductController {
    private final NotificationService notifications;
    private final PricingService pricing;

    @PostMapping("/api/orders")
    public Order createOrder(@RequestBody OrderRequest req) {
        Order order = orderService.create(req);
        notifications.sendWelcomeEmail(order.email());  // Non-blocking
        return order;
    }

    @GetMapping("/api/compare")
    public CompletableFuture<CompareResult> compare(@RequestParam List<String> ids) {
        // Parallel fetches
        List<CompletableFuture<PricingResult>> futures = ids.stream()
            .map(pricing::fetchPricing)
            .toList();

        return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
            .thenApply(v -> futures.stream()
                .map(CompletableFuture::join)
                .toList())
            .thenApply(CompareResult::from);
    }
}
```

## Custom Executor — Control Your Thread Pool

```java
@Configuration
public class AsyncConfig {

    @Bean("emailExecutor")
    public TaskExecutor emailExecutor() {
        var executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(2);
        executor.setMaxPoolSize(5);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("email-");
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.initialize();
        return executor;
    }
}

@Service
public class NotificationService {
    @Async("emailExecutor")  // Use specific executor
    public void sendEmail(String to, String subject) { }
}
```

## Virtual Threads — Spring Boot 3.2+

One property enables virtual threads for all web requests:

```yaml
# application.yml
spring:
  threads:
    virtual:
      enabled: true
```

That's it. Every request now runs on a virtual thread. For async tasks:

```java
@Bean("virtualExecutor")
public TaskExecutor virtualExecutor() {
    return new TaskExecutorAdapter(Executors.newVirtualThreadPerTaskExecutor());
}
```

## Error Handling in Async Methods

Async exceptions are lost by default. Catch them:

```java
@Configuration
public class AsyncExceptionConfig implements AsyncConfigurer {

    @Override
    public AsyncUncaughtExceptionHandler getAsyncUncaughtExceptionHandler() {
        return (throwable, method, params) -> {
            log.error("Async error in {}: {}", method.getName(), throwable.getMessage(), throwable);
            // Alert, metric, dead-letter queue, etc.
        };
    }
}
```

For `CompletableFuture` returns, use `.exceptionally()`:

```java
@Async
public CompletableFuture<Result> riskyOperation() {
    return CompletableFuture.supplyAsync(() -> {
        // work
        return result;
    }).exceptionally(ex -> {
        log.error("Operation failed", ex);
        return Result.empty();
    });
}
```

## What You Learned

- **@Scheduled** — cron, fixedRate, fixedDelay for recurring tasks
- **@Async** — fire-and-forget or CompletableFuture for parallel work
- **Custom executors** — control pool size, naming, rejection policy
- **Virtual threads** — one property in Spring Boot 3.2+ for massive concurrency
- **Error handling** — `AsyncUncaughtExceptionHandler` for void methods, `.exceptionally()` for futures
- **Externalized cron** — `${app.cron}` in properties for ops-friendly scheduling

---

[← Chapter 4: Errors](chapter-04-errors.md) | [Chapter 6: Caching →](chapter-06-caching.md)

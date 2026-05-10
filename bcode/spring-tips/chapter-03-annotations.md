# Chapter 3: Custom Annotations — Build Your Own Spring Magic

[← Chapter 2: Profiles](chapter-02-profiles.md) | [Chapter 4: Errors →](chapter-04-errors.md)

---

## The Problem

"I'm copy-pasting the same `@Transactional @Cacheable @PreAuthorize` stack on every service method. I want logging on every controller but don't want to add it manually. I need a `@Timed` annotation that measures execution."

## Meta-Annotations — Compose Multiple Annotations

Spring annotations are composable. Create one annotation that combines several:

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@Transactional
@Cacheable("products")
@PreAuthorize("hasRole('ADMIN')")
public @interface AdminCachedTransaction {
}

// Usage — one annotation replaces three
@Service
public class ProductService {

    @AdminCachedTransaction
    public Product updateProduct(Long id, ProductDto dto) {
        // Transactional + cached + admin-only
        return productRepository.save(map(dto));
    }
}
```

Stereotype meta-annotation:

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@RestController
@RequestMapping("/api/v1")
@CrossOrigin(origins = "${app.cors.allowed-origins}")
public @interface ApiController {
}

// Usage
@ApiController
@RequestMapping("/users")  // Appends to /api/v1
public class UserController { }
```

## @Aspect — Cross-Cutting Concerns with AOP

Add `spring-boot-starter-aop` to your dependencies.

### The @Timed Annotation — Log Method Execution Time

Step 1: Define the annotation:

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Timed {
    String value() default "";  // Optional label
}
```

Step 2: Create the aspect:

```java
@Aspect
@Component
@Slf4j
public class TimedAspect {

    @Around("@annotation(timed)")
    public Object measureTime(ProceedingJoinPoint joinPoint, Timed timed) throws Throwable {
        String label = timed.value().isEmpty()
            ? joinPoint.getSignature().toShortString()
            : timed.value();

        long start = System.nanoTime();
        try {
            return joinPoint.proceed();
        } finally {
            long elapsed = (System.nanoTime() - start) / 1_000_000;
            log.info("[TIMED] {} took {} ms", label, elapsed);
        }
    }
}
```

Step 3: Use it anywhere:

```java
@Service
public class ReportService {

    @Timed("monthly-report-generation")
    public Report generateMonthlyReport(YearMonth month) {
        // This method's execution time is automatically logged
        return buildReport(month);
    }
}
```

Output: `[TIMED] monthly-report-generation took 342 ms`

## Retry Aspect — Automatic Retries

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Retryable {
    int maxAttempts() default 3;
    long delayMs() default 1000;
    Class<? extends Throwable>[] retryOn() default {Exception.class};
}

@Aspect
@Component
@Slf4j
public class RetryAspect {

    @Around("@annotation(retryable)")
    public Object retry(ProceedingJoinPoint joinPoint, Retryable retryable) throws Throwable {
        int attempts = 0;
        Throwable lastException = null;

        while (attempts < retryable.maxAttempts()) {
            try {
                return joinPoint.proceed();
            } catch (Throwable e) {
                lastException = e;
                attempts++;
                if (attempts < retryable.maxAttempts() && isRetryable(e, retryable.retryOn())) {
                    log.warn("Attempt {}/{} failed: {}", attempts, retryable.maxAttempts(), e.getMessage());
                    Thread.sleep(retryable.delayMs());
                }
            }
        }
        throw lastException;
    }

    private boolean isRetryable(Throwable e, Class<? extends Throwable>[] retryOn) {
        for (Class<? extends Throwable> clazz : retryOn) {
            if (clazz.isInstance(e)) return true;
        }
        return false;
    }
}
```

## Custom Validation Annotation

```java
@Target({ElementType.FIELD, ElementType.PARAMETER})
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = NoProfanityValidator.class)
public @interface NoProfanity {
    String message() default "Content contains prohibited words";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}

public class NoProfanityValidator implements ConstraintValidator<NoProfanity, String> {
    private static final Set<String> BLOCKED = Set.of("spam", "scam");

    @Override
    public boolean isValid(String value, ConstraintValidatorContext ctx) {
        if (value == null) return true;
        String lower = value.toLowerCase();
        return BLOCKED.stream().noneMatch(lower::contains);
    }
}

// Usage
public record CreatePostRequest(
    @NotBlank String title,
    @NoProfanity @Size(max = 5000) String body
) {}
```

## Logging Aspect — Log All Controller Calls

```java
@Aspect
@Component
@Slf4j
public class ControllerLoggingAspect {

    @Before("within(@org.springframework.web.bind.annotation.RestController *)")
    public void logRequest(JoinPoint joinPoint) {
        log.info("→ {}.{}({})",
            joinPoint.getTarget().getClass().getSimpleName(),
            joinPoint.getSignature().getName(),
            Arrays.toString(joinPoint.getArgs()));
    }
}
```

## What You Learned

- **Meta-annotations** — compose multiple Spring annotations into one
- **@Aspect + @Around** — intercept method calls for cross-cutting logic
- **Custom @Timed** — measure and log execution time automatically
- **@Retryable** — automatic retry with configurable attempts and delay
- **Custom validators** — `@Constraint` + `ConstraintValidator` for domain rules
- **Pointcut expressions** — `@annotation()`, `within()`, `execution()` to target methods

---

[← Chapter 2: Profiles](chapter-02-profiles.md) | [Chapter 4: Errors →](chapter-04-errors.md)

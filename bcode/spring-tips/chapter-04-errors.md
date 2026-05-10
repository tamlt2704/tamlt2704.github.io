# Chapter 4: Error Handling — Stop Leaking Stack Traces

[← Chapter 3: Annotations](chapter-03-annotations.md) | [Chapter 5: Async →](chapter-05-async.md)

---

## The Problem

"My API returns raw 500 errors with full stack traces. Different controllers handle errors differently. Clients can't parse my error responses because they're inconsistent."

## Custom Exception Hierarchy

Define domain exceptions that map cleanly to HTTP status codes:

```java
public abstract class AppException extends RuntimeException {
    private final HttpStatus status;

    protected AppException(String message, HttpStatus status) {
        super(message);
        this.status = status;
    }

    public HttpStatus getStatus() { return status; }
}

public class NotFoundException extends AppException {
    public NotFoundException(String resource, Object id) {
        super("%s with id '%s' not found".formatted(resource, id), HttpStatus.NOT_FOUND);
    }
}

public class ConflictException extends AppException {
    public ConflictException(String message) {
        super(message, HttpStatus.CONFLICT);
    }
}

public class BadRequestException extends AppException {
    public BadRequestException(String message) {
        super(message, HttpStatus.BAD_REQUEST);
    }
}
```

Usage in services — throw and forget:

```java
@Service
public class UserService {
    public User getUser(Long id) {
        return userRepository.findById(id)
            .orElseThrow(() -> new NotFoundException("User", id));
    }

    public User createUser(CreateUserRequest req) {
        if (userRepository.existsByEmail(req.email())) {
            throw new ConflictException("Email already registered");
        }
        return userRepository.save(new User(req.email(), req.name()));
    }
}
```

## @ControllerAdvice — Global Exception Handler

One class handles ALL exceptions across every controller:

```java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    // Handle your custom exceptions
    @ExceptionHandler(AppException.class)
    public ProblemDetail handleAppException(AppException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
            ex.getStatus(), ex.getMessage());
        problem.setTitle(ex.getStatus().getReasonPhrase());
        problem.setProperty("timestamp", Instant.now());
        return problem;
    }

    // Handle validation errors (@Valid failures)
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ProblemDetail handleValidation(MethodArgumentNotValidException ex) {
        ProblemDetail problem = ProblemDetail.forStatus(HttpStatus.BAD_REQUEST);
        problem.setTitle("Validation Failed");

        Map<String, String> errors = ex.getBindingResult().getFieldErrors().stream()
            .collect(Collectors.toMap(
                FieldError::getField,
                fe -> fe.getDefaultMessage() != null ? fe.getDefaultMessage() : "invalid",
                (a, b) -> a  // Keep first if duplicate field
            ));

        problem.setProperty("errors", errors);
        return problem;
    }

    // Handle missing path variables / request params
    @ExceptionHandler(MissingServletRequestParameterException.class)
    public ProblemDetail handleMissingParam(MissingServletRequestParameterException ex) {
        ProblemDetail problem = ProblemDetail.forStatus(HttpStatus.BAD_REQUEST);
        problem.setDetail("Required parameter '%s' is missing".formatted(ex.getParameterName()));
        return problem;
    }

    // Catch-all for unexpected errors
    @ExceptionHandler(Exception.class)
    public ProblemDetail handleUnexpected(Exception ex) {
        log.error("Unexpected error", ex);  // Log full trace server-side
        ProblemDetail problem = ProblemDetail.forStatus(HttpStatus.INTERNAL_SERVER_ERROR);
        problem.setTitle("Internal Server Error");
        problem.setDetail("An unexpected error occurred");  // Don't leak details
        return problem;
    }
}
```

## ProblemDetail — RFC 7807 Standard Responses

Spring Boot 3.x natively supports RFC 7807. Enable it:

```yaml
# application.yml
spring:
  mvc:
    problemdetails:
      enabled: true
```

Every error response now looks like:

```json
{
  "type": "about:blank",
  "title": "Not Found",
  "status": 404,
  "detail": "User with id '42' not found",
  "instance": "/api/users/42",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

Custom type URIs for documentation:

```java
@ExceptionHandler(NotFoundException.class)
public ProblemDetail handleNotFound(NotFoundException ex, HttpServletRequest request) {
    ProblemDetail problem = ProblemDetail.forStatusAndDetail(
        HttpStatus.NOT_FOUND, ex.getMessage());
    problem.setType(URI.create("https://api.myapp.com/errors/not-found"));
    problem.setInstance(URI.create(request.getRequestURI()));
    return problem;
}
```

## Validation Error Response Example

Request:
```json
POST /api/users
{ "email": "not-an-email", "name": "" }
```

Response:
```json
{
  "type": "about:blank",
  "title": "Validation Failed",
  "status": 400,
  "detail": null,
  "errors": {
    "email": "must be a well-formed email address",
    "name": "must not be blank"
  }
}
```

## What You Learned

- **Exception hierarchy** — domain exceptions with HTTP status mapping
- **@RestControllerAdvice** — single global handler for all controllers
- **ProblemDetail** — RFC 7807 standard error format (Spring Boot 3.x native)
- **Validation errors** — extract field-level messages from `MethodArgumentNotValidException`
- **Catch-all** — log server-side, return generic message to client
- **Custom properties** — `problem.setProperty()` for extra context

---

[← Chapter 3: Annotations](chapter-03-annotations.md) | [Chapter 5: Async →](chapter-05-async.md)

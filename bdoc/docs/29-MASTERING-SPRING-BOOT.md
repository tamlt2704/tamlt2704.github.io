# Chapter 29: Mastering Spring Boot — Build a Production-Ready API

## What you'll learn

- Spring Boot auto-configuration and how the magic works
- Dependency injection and the IoC container
- Building REST APIs: controllers, services, repositories
- Data access with Spring Data JPA (PostgreSQL)
- Validation, error handling, and global exception handling
- Security with Spring Security + JWT
- Testing: unit, integration, and slice tests
- Configuration profiles (dev, staging, prod)
- Actuator: health checks, metrics, monitoring
- Build: a complete task management API from scratch

---

## PART 1: Spring Boot Foundations

## 29.1 What Spring Boot actually does

Spring Boot = Spring Framework + auto-configuration + embedded server + opinionated defaults.

Without Boot, a Spring project requires:
- XML or Java config for every bean
- Servlet container setup (Tomcat WAR deployment)
- Manual dependency version management
- DataSource configuration, transaction manager setup

Spring Boot eliminates all of this. It scans your classpath and auto-configures sensible defaults:

```
You add: spring-boot-starter-data-jpa + postgresql driver
Boot gives you: DataSource, EntityManagerFactory, TransactionManager, HikariCP pool
              — all configured from application.yml properties
```

## 29.2 Project structure

```
src/
├── main/
│   ├── java/com/example/taskapi/
│   │   ├── TaskApiApplication.java         ← Entry point (@SpringBootApplication)
│   │   ├── config/                         ← Configuration classes
│   │   │   ├── SecurityConfig.java
│   │   │   └── WebConfig.java
│   │   ├── controller/                     ← REST endpoints (HTTP layer)
│   │   │   ├── TaskController.java
│   │   │   └── AuthController.java
│   │   ├── service/                        ← Business logic
│   │   │   ├── TaskService.java
│   │   │   └── UserService.java
│   │   ├── repository/                     ← Data access (JPA)
│   │   │   ├── TaskRepository.java
│   │   │   └── UserRepository.java
│   │   ├── entity/                         ← JPA entities (DB tables)
│   │   │   ├── Task.java
│   │   │   └── User.java
│   │   ├── dto/                            ← Request/Response objects
│   │   │   ├── CreateTaskRequest.java
│   │   │   ├── TaskResponse.java
│   │   │   └── PageResponse.java
│   │   ├── exception/                      ← Custom exceptions + handler
│   │   │   ├── ResourceNotFoundException.java
│   │   │   └── GlobalExceptionHandler.java
│   │   └── mapper/                         ← Entity ↔ DTO conversion
│   │       └── TaskMapper.java
│   └── resources/
│       ├── application.yml                 ← Main config
│       ├── application-dev.yml             ← Dev overrides
│       └── application-prod.yml            ← Prod overrides
└── test/
    └── java/com/example/taskapi/
        ├── controller/TaskControllerTest.java
        ├── service/TaskServiceTest.java
        └── repository/TaskRepositoryTest.java
```

**Layer architecture:**
```
HTTP Request → Controller → Service → Repository → Database
              (validate)   (logic)    (query)
HTTP Response ← Controller ← Service ← Repository ← Database
              (format DTO)  (transform) (map entity)
```

## 29.3 Dependency injection — the core concept

Spring manages object creation and wiring. You declare dependencies, Spring provides them.

```java
// ❌ Without DI — tight coupling, hard to test
public class TaskService {
    private final TaskRepository repo = new TaskRepository(); // creates its own dependency
}

// ✅ With DI — Spring provides the dependency
@Service
public class TaskService {
    private final TaskRepository repo;

    // Constructor injection (preferred — immutable, testable)
    public TaskService(TaskRepository repo) {
        this.repo = repo;
    }
}
```

**Spring annotations for bean registration:**
| Annotation | Layer | Purpose |
|-----------|-------|---------|
| `@Component` | Any | Generic Spring-managed bean |
| `@Service` | Business | Business logic (same as @Component, semantic only) |
| `@Repository` | Data | Data access (adds exception translation) |
| `@Controller` / `@RestController` | Web | HTTP endpoint handler |
| `@Configuration` | Config | Declares @Bean methods |

## 29.4 The application entry point

```java
@SpringBootApplication  // = @Configuration + @EnableAutoConfiguration + @ComponentScan
public class TaskApiApplication {
    public static void main(String[] args) {
        SpringApplication.run(TaskApiApplication.class, args);
    }
}
```

`@SpringBootApplication` does three things:
1. `@Configuration` — this class can define beans
2. `@EnableAutoConfiguration` — activate auto-config magic
3. `@ComponentScan` — scan this package + sub-packages for @Component, @Service, etc.

---

## PART 2: Building the REST API

## 29.5 Entity (JPA)

```java
@Entity
@Table(name = "tasks")
public class Task {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 200)
    private String title;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private TaskStatus status = TaskStatus.TODO;

    @Enumerated(EnumType.STRING)
    private Priority priority = Priority.MEDIUM;

    @Column(name = "due_date")
    private LocalDate dueDate;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "assigned_to")
    private User assignedTo;

    @CreationTimestamp
    private Instant createdAt;

    @UpdateTimestamp
    private Instant updatedAt;

    // Constructors, getters, setters (or use Lombok @Data)
}

public enum TaskStatus { TODO, IN_PROGRESS, DONE, CANCELLED }
public enum Priority { LOW, MEDIUM, HIGH, CRITICAL }
```

## 29.6 Repository (Data Access)

```java
public interface TaskRepository extends JpaRepository<Task, Long> {

    // Spring Data generates the query from method name!
    List<Task> findByStatus(TaskStatus status);

    List<Task> findByAssignedToIdAndStatusNot(Long userId, TaskStatus status);

    Page<Task> findByStatusIn(List<TaskStatus> statuses, Pageable pageable);

    // Custom JPQL query
    @Query("SELECT t FROM Task t WHERE t.dueDate < :date AND t.status != 'DONE'")
    List<Task> findOverdueTasks(@Param("date") LocalDate date);

    // Native SQL (when JPQL isn't enough)
    @Query(value = "SELECT status, COUNT(*) FROM tasks GROUP BY status", nativeQuery = true)
    List<Object[]> countByStatus();

    // Exists check (returns boolean — faster than fetching entity)
    boolean existsByTitleIgnoreCase(String title);
}
```

**Spring Data JPA magic:** You define an interface, Spring generates the implementation at runtime. Method names are parsed into queries:

```
findByStatusAndPriorityOrderByDueDateAsc
  → SELECT * FROM tasks WHERE status = ? AND priority = ? ORDER BY due_date ASC
```

## 29.7 DTOs (Data Transfer Objects)

```java
// Request DTO — what the client sends
public record CreateTaskRequest(
    @NotBlank(message = "Title is required")
    @Size(max = 200, message = "Title must be under 200 characters")
    String title,

    String description,

    @NotNull(message = "Priority is required")
    Priority priority,

    LocalDate dueDate,

    Long assignedToId
) {}

public record UpdateTaskRequest(
    @Size(max = 200) String title,
    String description,
    Priority priority,
    TaskStatus status,
    LocalDate dueDate,
    Long assignedToId
) {}

// Response DTO — what the client receives
public record TaskResponse(
    Long id,
    String title,
    String description,
    TaskStatus status,
    Priority priority,
    LocalDate dueDate,
    String assignedToName,
    Instant createdAt,
    Instant updatedAt
) {
    public static TaskResponse from(Task task) {
        return new TaskResponse(
            task.getId(),
            task.getTitle(),
            task.getDescription(),
            task.getStatus(),
            task.getPriority(),
            task.getDueDate(),
            task.getAssignedTo() != null ? task.getAssignedTo().getName() : null,
            task.getCreatedAt(),
            task.getUpdatedAt()
        );
    }
}
```

> **Why DTOs?** Never expose entities directly — they leak database structure, cause lazy-loading issues in JSON serialization, and can't evolve independently of the schema.

## 29.8 Service (Business Logic)

```java
@Service
@Transactional(readOnly = true)
public class TaskService {

    private final TaskRepository taskRepository;
    private final UserRepository userRepository;

    public TaskService(TaskRepository taskRepository, UserRepository userRepository) {
        this.taskRepository = taskRepository;
        this.userRepository = userRepository;
    }

    public Page<TaskResponse> getTasks(TaskStatus status, Pageable pageable) {
        Page<Task> tasks = (status != null)
            ? taskRepository.findByStatusIn(List.of(status), pageable)
            : taskRepository.findAll(pageable);
        return tasks.map(TaskResponse::from);
    }

    public TaskResponse getTask(Long id) {
        Task task = taskRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Task", id));
        return TaskResponse.from(task);
    }

    @Transactional
    public TaskResponse createTask(CreateTaskRequest request) {
        Task task = new Task();
        task.setTitle(request.title());
        task.setDescription(request.description());
        task.setPriority(request.priority());
        task.setDueDate(request.dueDate());

        if (request.assignedToId() != null) {
            User user = userRepository.findById(request.assignedToId())
                .orElseThrow(() -> new ResourceNotFoundException("User", request.assignedToId()));
            task.setAssignedTo(user);
        }

        Task saved = taskRepository.save(task);
        return TaskResponse.from(saved);
    }

    @Transactional
    public TaskResponse updateTask(Long id, UpdateTaskRequest request) {
        Task task = taskRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Task", id));

        if (request.title() != null) task.setTitle(request.title());
        if (request.description() != null) task.setDescription(request.description());
        if (request.priority() != null) task.setPriority(request.priority());
        if (request.status() != null) task.setStatus(request.status());
        if (request.dueDate() != null) task.setDueDate(request.dueDate());

        Task saved = taskRepository.save(task);
        return TaskResponse.from(saved);
    }

    @Transactional
    public void deleteTask(Long id) {
        if (!taskRepository.existsById(id)) {
            throw new ResourceNotFoundException("Task", id);
        }
        taskRepository.deleteById(id);
    }
}
```

**`@Transactional` rules:**
- Class-level `readOnly = true` — optimizes read queries (no dirty checking)
- Method-level `@Transactional` on writes — overrides to read-write
- If exception is thrown, transaction rolls back automatically

## 29.9 Controller (HTTP Layer)

```java
@RestController
@RequestMapping("/api/tasks")
public class TaskController {

    private final TaskService taskService;

    public TaskController(TaskService taskService) {
        this.taskService = taskService;
    }

    @GetMapping
    public Page<TaskResponse> getTasks(
            @RequestParam(required = false) TaskStatus status,
            @PageableDefault(size = 20, sort = "createdAt", direction = Sort.Direction.DESC) Pageable pageable
    ) {
        return taskService.getTasks(status, pageable);
    }

    @GetMapping("/{id}")
    public TaskResponse getTask(@PathVariable Long id) {
        return taskService.getTask(id);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public TaskResponse createTask(@RequestBody @Valid CreateTaskRequest request) {
        return taskService.createTask(request);
    }

    @PutMapping("/{id}")
    public TaskResponse updateTask(@PathVariable Long id, @RequestBody @Valid UpdateTaskRequest request) {
        return taskService.updateTask(id, request);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deleteTask(@PathVariable Long id) {
        taskService.deleteTask(id);
    }
}
```

**Key patterns:**
- `@Valid` triggers bean validation on request DTOs
- `@PageableDefault` provides default pagination (page=0, size=20)
- `@ResponseStatus(CREATED)` returns 201 instead of 200
- `@ResponseStatus(NO_CONTENT)` returns 204 for delete

## 29.10 Global exception handling

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ErrorResponse handleNotFound(ResourceNotFoundException ex) {
        return new ErrorResponse("NOT_FOUND", ex.getMessage());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ErrorResponse handleValidation(MethodArgumentNotValidException ex) {
        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getFieldErrors().forEach(
            error -> errors.put(error.getField(), error.getDefaultMessage())
        );
        return new ErrorResponse("VALIDATION_FAILED", "Invalid request", errors);
    }

    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ErrorResponse handleGeneral(Exception ex) {
        log.error("Unexpected error", ex);
        return new ErrorResponse("INTERNAL_ERROR", "An unexpected error occurred");
    }
}

public record ErrorResponse(String code, String message, Map<String, String> details) {
    public ErrorResponse(String code, String message) {
        this(code, message, null);
    }
}

public class ResourceNotFoundException extends RuntimeException {
    public ResourceNotFoundException(String resource, Long id) {
        super(resource + " not found with id: " + id);
    }
}
```



---

## PART 3: Configuration & Profiles

## 29.11 application.yml

```yaml
# application.yml (base — applies to all profiles)
spring:
  application:
    name: task-api
  jpa:
    open-in-view: false  # ← IMPORTANT: disable lazy loading in views (performance trap)
    hibernate:
      ddl-auto: validate  # production: validate only (use Flyway for migrations)
    properties:
      hibernate:
        format_sql: true
        default_batch_fetch_size: 20  # prevent N+1 queries

server:
  port: 8080
  shutdown: graceful  # wait for requests to complete on shutdown

management:
  endpoints:
    web:
      exposure:
        include: health, info, metrics, prometheus
  endpoint:
    health:
      show-details: when-authorized

logging:
  level:
    com.example.taskapi: INFO
    org.springframework.web: INFO
    org.hibernate.SQL: WARN
```

```yaml
# application-dev.yml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/taskapi_dev
    username: dev
    password: dev
  jpa:
    hibernate:
      ddl-auto: create-drop  # recreate schema on startup (dev only!)
    show-sql: true

logging:
  level:
    com.example.taskapi: DEBUG
    org.hibernate.SQL: DEBUG
```

```yaml
# application-prod.yml
spring:
  datasource:
    url: ${DATABASE_URL}         # from environment variable
    username: ${DATABASE_USER}
    password: ${DATABASE_PASS}
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000
  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: false

server:
  port: ${PORT:8080}

logging:
  level:
    root: WARN
    com.example.taskapi: INFO
```

**Activate profiles:**
```bash
# Environment variable
SPRING_PROFILES_ACTIVE=prod java -jar app.jar

# Command line
java -jar app.jar --spring.profiles.active=prod

# IntelliJ: Run Configuration → Active Profiles: dev
```

## 29.12 Database migrations with Flyway

```xml
<dependency>
    <groupId>org.flywaydb</groupId>
    <artifactId>flyway-core</artifactId>
</dependency>
```

```sql
-- src/main/resources/db/migration/V1__create_users_table.sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'USER',
    created_at TIMESTAMP DEFAULT NOW()
);

-- src/main/resources/db/migration/V2__create_tasks_table.sql
CREATE TABLE tasks (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'TODO',
    priority VARCHAR(50) DEFAULT 'MEDIUM',
    due_date DATE,
    assigned_to BIGINT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_assigned ON tasks(assigned_to);
```

**Flyway naming:** `V{version}__{description}.sql` — versions applied in order, never re-run.

---

## PART 4: Testing

## 29.13 Unit tests (Service layer)

```java
@ExtendWith(MockitoExtension.class)
class TaskServiceTest {

    @Mock
    private TaskRepository taskRepository;

    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private TaskService taskService;

    @Test
    void createTask_shouldSaveAndReturnResponse() {
        // Arrange
        var request = new CreateTaskRequest("Write tests", null, Priority.HIGH, null, null);
        var savedTask = new Task();
        savedTask.setId(1L);
        savedTask.setTitle("Write tests");
        savedTask.setPriority(Priority.HIGH);
        savedTask.setStatus(TaskStatus.TODO);

        when(taskRepository.save(any(Task.class))).thenReturn(savedTask);

        // Act
        TaskResponse response = taskService.createTask(request);

        // Assert
        assertThat(response.id()).isEqualTo(1L);
        assertThat(response.title()).isEqualTo("Write tests");
        assertThat(response.priority()).isEqualTo(Priority.HIGH);
        assertThat(response.status()).isEqualTo(TaskStatus.TODO);

        verify(taskRepository).save(any(Task.class));
    }

    @Test
    void getTask_whenNotFound_shouldThrowException() {
        when(taskRepository.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> taskService.getTask(99L))
            .isInstanceOf(ResourceNotFoundException.class)
            .hasMessageContaining("99");
    }
}
```

## 29.14 Integration tests (Controller layer)

```java
@SpringBootTest
@AutoConfigureMockMvc
@Transactional  // rolls back after each test
class TaskControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private TaskRepository taskRepository;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void createTask_shouldReturn201() throws Exception {
        var request = new CreateTaskRequest("Integration test task", "desc", Priority.HIGH, null, null);

        mockMvc.perform(post("/api/tasks")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.title").value("Integration test task"))
            .andExpect(jsonPath("$.status").value("TODO"))
            .andExpect(jsonPath("$.id").isNumber());

        assertThat(taskRepository.count()).isEqualTo(1);
    }

    @Test
    void createTask_withBlankTitle_shouldReturn400() throws Exception {
        var request = new CreateTaskRequest("", null, Priority.HIGH, null, null);

        mockMvc.perform(post("/api/tasks")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.code").value("VALIDATION_FAILED"))
            .andExpect(jsonPath("$.details.title").exists());
    }

    @Test
    void getTasks_shouldReturnPaginated() throws Exception {
        // Seed data
        for (int i = 0; i < 25; i++) {
            Task task = new Task();
            task.setTitle("Task " + i);
            task.setPriority(Priority.MEDIUM);
            taskRepository.save(task);
        }

        mockMvc.perform(get("/api/tasks?page=0&size=10"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.content.length()").value(10))
            .andExpect(jsonPath("$.totalElements").value(25))
            .andExpect(jsonPath("$.totalPages").value(3));
    }
}
```

## 29.15 Repository tests (Slice test)

```java
@DataJpaTest  // only loads JPA-related beans (fast!)
class TaskRepositoryTest {

    @Autowired
    private TaskRepository taskRepository;

    @Autowired
    private TestEntityManager entityManager;

    @Test
    void findOverdueTasks_shouldReturnOnlyOverdue() {
        Task overdue = new Task();
        overdue.setTitle("Overdue");
        overdue.setDueDate(LocalDate.now().minusDays(5));
        overdue.setStatus(TaskStatus.TODO);
        entityManager.persist(overdue);

        Task onTime = new Task();
        onTime.setTitle("On time");
        onTime.setDueDate(LocalDate.now().plusDays(5));
        onTime.setStatus(TaskStatus.TODO);
        entityManager.persist(onTime);

        Task done = new Task();
        done.setTitle("Done but overdue");
        done.setDueDate(LocalDate.now().minusDays(5));
        done.setStatus(TaskStatus.DONE);
        entityManager.persist(done);

        entityManager.flush();

        List<Task> result = taskRepository.findOverdueTasks(LocalDate.now());

        assertThat(result).hasSize(1);
        assertThat(result.get(0).getTitle()).isEqualTo("Overdue");
    }
}
```

---

## PART 5: Production Patterns

## 29.16 Actuator — health and metrics

```yaml
# Already in application.yml:
management:
  endpoints:
    web:
      exposure:
        include: health, info, metrics, prometheus
```

```bash
# Health check (for load balancers / Kubernetes probes)
GET /actuator/health
{ "status": "UP", "components": { "db": { "status": "UP" }, "diskSpace": { "status": "UP" } } }

# Metrics
GET /actuator/metrics/http.server.requests
GET /actuator/metrics/jvm.memory.used
GET /actuator/prometheus  ← Prometheus scrape endpoint
```

**Custom health indicator:**
```java
@Component
public class TaskQueueHealthIndicator implements HealthIndicator {
    @Override
    public Health health() {
        int queueSize = getQueueSize();
        if (queueSize > 1000) {
            return Health.down().withDetail("queue_size", queueSize).build();
        }
        return Health.up().withDetail("queue_size", queueSize).build();
    }
}
```

## 29.17 Caching with Spring Cache

```java
@Configuration
@EnableCaching
public class CacheConfig {
    @Bean
    public CacheManager cacheManager() {
        CaffeineCacheManager manager = new CaffeineCacheManager("tasks", "users");
        manager.setCaffeine(Caffeine.newBuilder()
            .maximumSize(500)
            .expireAfterWrite(Duration.ofMinutes(10)));
        return manager;
    }
}

@Service
public class TaskService {

    @Cacheable(value = "tasks", key = "#id")
    public TaskResponse getTask(Long id) {
        // Only hits DB on cache miss
        return TaskResponse.from(taskRepository.findById(id).orElseThrow(...));
    }

    @CacheEvict(value = "tasks", key = "#id")
    @Transactional
    public TaskResponse updateTask(Long id, UpdateTaskRequest request) {
        // Evicts cache entry when task is updated
    }

    @CacheEvict(value = "tasks", allEntries = true)
    @Transactional
    public void deleteTask(Long id) {
        // Clear all task cache entries
    }
}
```

## 29.18 Async operations

```java
@Configuration
@EnableAsync
public class AsyncConfig {
    @Bean
    public Executor taskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(4);
        executor.setMaxPoolSize(8);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("async-");
        executor.initialize();
        return executor;
    }
}

@Service
public class NotificationService {

    @Async
    public CompletableFuture<Void> sendTaskAssignedEmail(Task task, User assignee) {
        // Runs in background thread — doesn't block the HTTP response
        emailService.send(assignee.getEmail(), "Task assigned: " + task.getTitle());
        return CompletableFuture.completedFuture(null);
    }
}
```

## 29.19 Rate limiting

```java
@Component
public class RateLimitFilter extends OncePerRequestFilter {

    private final Map<String, Bucket> buckets = new ConcurrentHashMap<>();

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response,
                                     FilterChain chain) throws ServletException, IOException {
        String clientIp = request.getRemoteAddr();
        Bucket bucket = buckets.computeIfAbsent(clientIp, k -> createBucket());

        if (bucket.tryConsume(1)) {
            chain.doFilter(request, response);
        } else {
            response.setStatus(429);
            response.getWriter().write("{\"error\": \"Too many requests\"}");
        }
    }

    private Bucket createBucket() {
        return Bucket.builder()
            .addLimit(Bandwidth.classic(100, Refill.intervally(100, Duration.ofMinutes(1))))
            .build();
    }
}
```

## 29.20 Scheduled tasks

```java
@Configuration
@EnableScheduling
public class SchedulerConfig {}

@Service
public class TaskCleanupService {

    @Scheduled(cron = "0 0 2 * * *") // Every day at 2 AM
    public void archiveOldTasks() {
        LocalDate cutoff = LocalDate.now().minusDays(90);
        int archived = taskRepository.archiveTasksCompletedBefore(cutoff);
        log.info("Archived {} tasks older than {}", archived, cutoff);
    }

    @Scheduled(fixedRate = 60_000) // Every 60 seconds
    public void checkOverdueTasks() {
        List<Task> overdue = taskRepository.findOverdueTasks(LocalDate.now());
        overdue.forEach(task -> notificationService.sendOverdueReminder(task));
    }
}
```

## 29.21 API versioning

```java
// Option 1: URL path versioning (most common)
@RestController
@RequestMapping("/api/v1/tasks")
public class TaskControllerV1 { ... }

@RestController
@RequestMapping("/api/v2/tasks")
public class TaskControllerV2 { ... }

// Option 2: Header versioning
@GetMapping(value = "/api/tasks", headers = "X-API-Version=2")
public Page<TaskResponseV2> getTasksV2(...) { ... }
```

## 29.22 Docker deployment

```dockerfile
# Multi-stage build
FROM eclipse-temurin:21-jdk-alpine AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN ./mvnw package -DskipTests

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

```yaml
# docker-compose.yml
services:
  app:
    build: .
    ports: ["8080:8080"]
    environment:
      SPRING_PROFILES_ACTIVE: prod
      DATABASE_URL: jdbc:postgresql://db:5432/taskapi
      DATABASE_USER: postgres
      DATABASE_PASS: secret
    depends_on: [db]

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: taskapi
      POSTGRES_PASSWORD: secret
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]

volumes:
  pgdata:
```

---

## Summary

✅ Spring Boot auto-configuration: how it works, what it provides
✅ Layer architecture: Controller → Service → Repository with DTOs
✅ JPA entities, Spring Data repositories, derived query methods
✅ Bean validation (`@Valid`, `@NotBlank`, `@Size`)
✅ Global exception handling (`@RestControllerAdvice`)
✅ Configuration profiles (dev/prod), externalized config, environment variables
✅ Database migrations with Flyway
✅ Testing: unit (Mockito), integration (MockMvc), slice (@DataJpaTest)
✅ Actuator: health checks, metrics, Prometheus endpoint
✅ Caching, async operations, rate limiting, scheduled tasks
✅ Docker multi-stage build + docker-compose

## Key takeaways

**Spring Boot is opinionated so you can focus on business logic.** It configures sensible defaults for everything — you override only what's different. Don't fight the framework; learn its conventions and you'll be productive immediately.

**The layer pattern is non-negotiable.** Controller (HTTP) → Service (business logic) → Repository (data). Each layer has one responsibility. DTOs cross the boundaries, never entities.

**Testing at the right level:** Unit tests for logic (fast, mocked dependencies). Integration tests for API contracts (slow, full context). Slice tests for specific layers (moderate, partial context). Aim for: many unit, some integration, few e2e.

**Production readiness = config + health + metrics + graceful shutdown.** Spring Boot Actuator gives you all of this with minimal configuration. Expose `/actuator/health` for Kubernetes probes, `/actuator/prometheus` for monitoring.

---

→ [Back to Chapter 28: Pandas Titanic](./28-PANDAS-TITANIC-CLEANING.md)

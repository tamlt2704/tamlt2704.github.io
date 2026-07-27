# Java on AWS — Building Cloud-Native Java Applications

---

## The Big Picture

```
Level 1: Running Java on AWS (deployment options)
    ↓
Level 2: Spring Boot + AWS (the standard stack)
    ↓
Level 3: AWS SDK for Java (talk to AWS services)
    ↓
Level 4: Database Access (RDS, DynamoDB)
    ↓
Level 5: Messaging & Events (SQS, SNS, EventBridge)
    ↓
Level 6: Observability (logging, metrics, tracing)
    ↓
Level 7: CI/CD Pipeline (build → test → deploy)
```

---

## Level 1: Where Does Java Run on AWS?

| Option | What it is | Startup | Best for |
|--------|-----------|---------|----------|
| **ECS Fargate** | Docker container, AWS manages servers | 10-30s | Most web apps ✓ |
| **EKS** | Kubernetes, you manage clusters | 10-30s | Large orgs, many services |
| **EC2** | Full VM, you manage everything | Always on | Legacy, specific OS needs |
| **Lambda** | Single function, no server | 1-10s cold start | Event-driven, low traffic |
| **Elastic Beanstalk** | Deploy a JAR, AWS handles the rest | 30-60s | Quick start, less control |

**For most Java apps: ECS Fargate** — you package a Docker container, AWS runs it. No server management, auto-scales.

### Java on ECS Fargate — The Flow

```
Your code → Build JAR → Docker image → Push to ECR → Deploy to ECS → ALB routes traffic
```

```dockerfile
# Dockerfile
FROM eclipse-temurin:21-jre-alpine
COPY target/app.jar /app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app.jar"]
```

### Java on Lambda — The Tradeoff

```
Pro: No server, pay per invocation, scales to zero
Con: Cold starts (2-8s for Java), 15-min max, 256MB-10GB RAM
```

**Cold start mitigations:**
- Use GraalVM native image (startup < 200ms, but complex build)
- Use SnapStart (Lambda snapshots memory after init — ~500ms cold start)
- Use Provisioned Concurrency (keep N instances warm — costs money)

---

## Level 2: Spring Boot + AWS

### The Standard Stack

```
Spring Boot (web framework)
├── Spring Web (REST APIs)
├── Spring Data JPA (database access)
├── Spring Security (auth)
├── Spring Cloud AWS (AWS service integration)
└── Spring Actuator (health checks, metrics)
```

### Minimal Spring Boot App

```java
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}

@RestController
@RequestMapping("/api")
public class DataController {

    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of("status", "UP");
    }

    @GetMapping("/data")
    public List<DataItem> getData() {
        return dataService.findAll();
    }
}
```

### Spring Cloud AWS — Access AWS Services Naturally

```xml
<!-- pom.xml -->
<dependency>
    <groupId>io.awspring.cloud</groupId>
    <artifactId>spring-cloud-aws-starter</artifactId>
</dependency>
<dependency>
    <groupId>io.awspring.cloud</groupId>
    <artifactId>spring-cloud-aws-starter-s3</artifactId>
</dependency>
<dependency>
    <groupId>io.awspring.cloud</groupId>
    <artifactId>spring-cloud-aws-starter-sqs</artifactId>
</dependency>
```

Now S3, SQS, etc. work like any other Spring bean — inject and use:

```java
@Service
public class FileService {
    private final S3Client s3;

    public FileService(S3Client s3) {
        this.s3 = s3;  // auto-configured by Spring Cloud AWS
    }

    public void upload(String key, byte[] content) {
        s3.putObject(
            PutObjectRequest.builder().bucket("my-bucket").key(key).build(),
            RequestBody.fromBytes(content)
        );
    }
}
```

### Configuration — Externalize Everything

```yaml
# application.yml
spring:
  application:
    name: my-service

  datasource:
    url: ${DB_URL}          # from environment variable
    username: ${DB_USER}
    password: ${DB_PASS}

  cloud:
    aws:
      region:
        static: eu-west-1

server:
  port: 8080
```

**In AWS, set environment variables via:**
- ECS Task Definition → environment
- Lambda → environment variables
- Systems Manager Parameter Store → `spring.config.import=aws-parameterstore:`
- Secrets Manager → `spring.config.import=aws-secretsmanager:`

---

## Level 3: AWS SDK for Java

### Setup

```xml
<!-- AWS SDK v2 (BOM manages versions) -->
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>software.amazon.awssdk</groupId>
            <artifactId>bom</artifactId>
            <version>2.25.0</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<!-- Add individual services as needed -->
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>s3</artifactId>
</dependency>
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>dynamodb-enhanced</artifactId>
</dependency>
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>sqs</artifactId>
</dependency>
```

### S3 — File Storage

```java
S3Client s3 = S3Client.builder().region(Region.EU_WEST_1).build();

// Upload
s3.putObject(
    PutObjectRequest.builder()
        .bucket("my-bucket")
        .key("data/report.csv")
        .contentType("text/csv")
        .build(),
    RequestBody.fromFile(Path.of("report.csv"))
);

// Download
ResponseBytes<GetObjectResponse> response = s3.getObjectAsBytes(
    GetObjectRequest.builder()
        .bucket("my-bucket")
        .key("data/report.csv")
        .build()
);
byte[] content = response.asByteArray();

// Generate pre-signed URL (temporary access link)
S3Presigner presigner = S3Presigner.builder().region(Region.EU_WEST_1).build();
URL url = presigner.presignGetObject(r -> r
    .getObjectRequest(g -> g.bucket("my-bucket").key("data/report.csv"))
    .signatureDuration(Duration.ofMinutes(15))
).url();
```

### SQS — Message Queue

```java
SqsClient sqs = SqsClient.builder().region(Region.EU_WEST_1).build();

// Send a message
sqs.sendMessage(SendMessageRequest.builder()
    .queueUrl("https://sqs.eu-west-1.amazonaws.com/123456789/my-queue")
    .messageBody("{\"orderId\": 123, \"action\": \"process\"}")
    .build()
);

// Receive messages
List<Message> messages = sqs.receiveMessage(r -> r
    .queueUrl(queueUrl)
    .maxNumberOfMessages(10)
    .waitTimeSeconds(20)  // long polling — cheaper than short polling
).messages();

for (Message msg : messages) {
    process(msg.body());

    // Delete after successful processing
    sqs.deleteMessage(r -> r.queueUrl(queueUrl).receiptHandle(msg.receiptHandle()));
}
```

### Secrets Manager — Retrieve Secrets

```java
SecretsManagerClient secrets = SecretsManagerClient.builder().build();

String dbPassword = secrets.getSecretValue(r -> r.secretId("prod/db/credentials"))
    .secretString();
```

---

## Level 4: Database Access

### RDS with Spring Data JPA

```java
// Entity
@Entity
@Table(name = "users")
public class User {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;
    private String email;

    @Column(name = "created_at")
    private LocalDateTime createdAt;
}

// Repository — Spring generates SQL for you
public interface UserRepository extends JpaRepository<User, Long> {
    List<User> findByNameContaining(String name);
    Optional<User> findByEmail(String email);

    @Query("SELECT u FROM User u WHERE u.createdAt > :since")
    List<User> findRecentUsers(@Param("since") LocalDateTime since);
}

// Service
@Service
public class UserService {
    private final UserRepository repo;

    public UserService(UserRepository repo) {
        this.repo = repo;
    }

    public User createUser(String name, String email) {
        var user = new User();
        user.setName(name);
        user.setEmail(email);
        user.setCreatedAt(LocalDateTime.now());
        return repo.save(user);
    }
}
```

### DynamoDB with Enhanced Client

```java
// Define your table mapping
@DynamoDbBean
public class GameScore {
    private String playerId;
    private String gameId;
    private int score;
    private Instant timestamp;

    @DynamoDbPartitionKey
    public String getPlayerId() { return playerId; }

    @DynamoDbSortKey
    public String getGameId() { return gameId; }

    // getters/setters...
}

// Use it
DynamoDbEnhancedClient enhancedClient = DynamoDbEnhancedClient.builder()
    .dynamoDbClient(DynamoDbClient.create())
    .build();

DynamoDbTable<GameScore> table = enhancedClient.table("GameScores", TableSchema.fromBean(GameScore.class));

// Put item
table.putItem(score);

// Query by partition key
List<GameScore> scores = table.query(r -> r.queryConditional(
    QueryConditional.keyEqualTo(Key.builder().partitionValue("player-123").build())
)).items().stream().toList();
```

**RDS vs DynamoDB decision:**

| Use RDS when | Use DynamoDB when |
|-------------|-----------------|
| Complex queries (JOINs, aggregations) | Simple key-value lookups |
| Strong consistency required everywhere | Eventually consistent is OK |
| Data is highly relational | Access patterns are known upfront |
| Reporting / analytics | High throughput, low latency |
| Team knows SQL | Serverless architecture (Lambda) |

---

## Level 5: Messaging & Events

### SQS — Decouple Services

```
Order Service → [SQS Queue] → Payment Service
                             → Inventory Service
                             → Email Service
```

**Why a queue?**
- Order Service doesn't wait for Payment to finish
- If Payment Service crashes, messages stay in queue (retry later)
- Scale consumers independently

### With Spring Cloud AWS:

```java
@SqsListener("order-events")
public void handleOrderEvent(String message) {
    OrderEvent event = objectMapper.readValue(message, OrderEvent.class);
    paymentService.processPayment(event.orderId(), event.amount());
}
```

That's it. Spring polls the queue and calls your method.

### SNS — Fan-Out (One Event → Many Consumers)

```
Order placed → SNS Topic "order-placed"
                ├── SQS → Payment Service
                ├── SQS → Inventory Service
                ├── SQS → Email Service
                └── Lambda → Analytics
```

```java
SnsClient sns = SnsClient.create();

sns.publish(PublishRequest.builder()
    .topicArn("arn:aws:sns:eu-west-1:123456789:order-placed")
    .message("{\"orderId\": 123}")
    .build()
);
```

### EventBridge — Event Bus (Rules-Based Routing)

```java
// Publish event
EventBridgeClient eventBridge = EventBridgeClient.create();

eventBridge.putEvents(PutEventsRequest.builder()
    .entries(PutEventsRequestEntry.builder()
        .source("com.myapp.orders")
        .detailType("OrderPlaced")
        .detail("{\"orderId\": 123, \"amount\": 99.99}")
        .build())
    .build()
);
```

EventBridge rules route events to targets based on patterns — no hardcoded queue URLs.

### When to Use What

| Pattern | Service | Example |
|---------|---------|---------|
| Point-to-point | SQS | One producer, one consumer |
| Fan-out | SNS + SQS | One event, many consumers |
| Event bus | EventBridge | Decoupled, rules-based routing |
| Streaming | Kinesis | High-volume continuous data (clicks, logs) |

---

## Level 6: Observability

### Three Pillars

```
Logs    — What happened? (text records of events)
Metrics — How much? (numbers over time: CPU, request count, latency)
Traces  — Where did time go? (follow a request across services)
```

### Structured Logging (JSON)

```java
// Use SLF4J + Logback with JSON output
@Slf4j
@RestController
public class OrderController {

    @PostMapping("/orders")
    public Order createOrder(@RequestBody OrderRequest request) {
        log.info("Creating order", kv("customerId", request.customerId()), kv("amount", request.amount()));

        Order order = orderService.create(request);

        log.info("Order created", kv("orderId", order.id()), kv("status", order.status()));
        return order;
    }
}
```

Output (goes to CloudWatch Logs):
```json
{"timestamp":"2024-01-15T10:30:00Z","level":"INFO","message":"Order created","orderId":"abc-123","status":"PENDING"}
```

### CloudWatch Metrics

```java
CloudWatchClient cw = CloudWatchClient.create();

cw.putMetricData(PutMetricDataRequest.builder()
    .namespace("MyApp")
    .metricData(MetricDatum.builder()
        .metricName("OrderProcessingTime")
        .value(235.0)
        .unit(StandardUnit.MILLISECONDS)
        .dimensions(Dimension.builder().name("Service").value("OrderService").build())
        .build())
    .build()
);
```

**Better: Use Micrometer (Spring Boot's metrics library):**

```java
@Service
public class OrderService {
    private final MeterRegistry metrics;

    public OrderService(MeterRegistry metrics) {
        this.metrics = metrics;
    }

    public Order processOrder(OrderRequest request) {
        return metrics.timer("order.processing").record(() -> {
            // ... actual processing
            return createOrder(request);
        });
    }
}
```

Spring Boot Actuator + CloudWatch exporter sends metrics automatically.

### Distributed Tracing (X-Ray or OpenTelemetry)

Follow a request across services:

```
User → API Gateway → Order Service → Payment Service → Database
       [Trace ID: abc-123]
       ├── Span 1: API Gateway (5ms)
       ├── Span 2: Order Service (120ms)
       │   ├── Span 3: Validate (10ms)
       │   └── Span 4: Call Payment (100ms)
       │       └── Span 5: Payment Service (80ms)
       │           └── Span 6: DB write (20ms)
       └── Total: 125ms
```

With Spring Boot + OpenTelemetry:

```xml
<dependency>
    <groupId>io.opentelemetry.instrumentation</groupId>
    <artifactId>opentelemetry-spring-boot-starter</artifactId>
</dependency>
```

Most frameworks (Spring Web, JDBC, HTTP clients) get traced automatically — no code changes.

---

## Level 7: CI/CD Pipeline

### The Pipeline

```
Push to Git
    ↓
Build (compile + test)
    ↓
Docker Image (package)
    ↓
Push to ECR (container registry)
    ↓
Deploy to ECS (run containers)
    ↓
Health check passes → done ✓
Health check fails → rollback ✗
```

### GitHub Actions Example

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          java-version: 21
          distribution: temurin
          cache: maven

      - name: Build & Test
        run: mvn clean verify

      - name: Configure AWS
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: eu-west-1

      - name: Login to ECR
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build & Push Docker Image
        run: |
          docker build -t my-app .
          docker tag my-app:latest 123456789.dkr.ecr.eu-west-1.amazonaws.com/my-app:${{ github.sha }}
          docker push 123456789.dkr.ecr.eu-west-1.amazonaws.com/my-app:${{ github.sha }}

      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster my-cluster \
            --service my-service \
            --force-new-deployment
```

### Blue/Green Deployment

```
Before:  ALB → [v1] [v1] [v1]  (blue — current)
During:  ALB → [v1] [v1] [v1]  (blue)
              [v2] [v2] [v2]  (green — new, testing)
Switch:  ALB → [v2] [v2] [v2]  (green — now live)
              [v1] [v1] [v1]  (blue — standby for rollback)
```

AWS CodeDeploy handles this for ECS automatically.

---

## Putting It Together — Typical Java Microservice

```
┌─── API Layer ────────────────────────┐
│  Spring Web Controllers              │
│  Input validation (Bean Validation)  │
│  Authentication (Spring Security)    │
└───────────────┬──────────────────────┘
                ↓
┌─── Service Layer ────────────────────┐
│  Business logic                      │
│  Transaction management              │
│  Event publishing (SQS/SNS)          │
└───────────────┬──────────────────────┘
                ↓
┌─── Data Layer ───────────────────────┐
│  Spring Data JPA (RDS)               │
│  DynamoDB Enhanced Client            │
│  S3 Client (file storage)            │
│  Redis (ElastiCache — caching)       │
└──────────────────────────────────────┘
```

**Deployed as:**

```
ECR (Docker image)
    → ECS Fargate (runs containers)
        → ALB (load balancer, HTTPS)
            → Route 53 (DNS: api.myapp.com)

Connected to:
    → RDS PostgreSQL (private subnet)
    → ElastiCache Redis (private subnet)
    → S3 (file storage)
    → SQS (async processing)
    → CloudWatch (logs + metrics)
    → Secrets Manager (credentials)
```

---

## Java-Specific AWS Tips

| Topic | Tip |
|-------|-----|
| **Cold starts** | Use `-XX:+TieredCompilation -XX:TieredStopAtLevel=1` for faster Lambda startup |
| **Memory** | Set container memory = JVM max heap + 256MB (for non-heap: metaspace, threads) |
| **GC** | Use G1GC for containers. ZGC for low-latency. Shenandoah for large heaps. |
| **Docker image size** | Use `eclipse-temurin:21-jre-alpine` (not full JDK) — ~80MB vs ~400MB |
| **Health checks** | Spring Actuator `/actuator/health` → ALB health check path |
| **Graceful shutdown** | `server.shutdown=graceful` — finish in-flight requests before stopping |
| **Native image** | GraalVM native-image for Lambda — 50ms startup, but build complexity |

---

## Resources

| Resource | What | Free? |
|----------|------|-------|
| [Spring Cloud AWS docs](https://docs.awspring.io) | Official integration guide | ✅ |
| [AWS SDK Java v2 docs](https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/) | SDK reference | ✅ |
| [AWS Samples (GitHub)](https://github.com/aws-samples) | Example projects | ✅ |
| [Baeldung AWS](https://baeldung.com/aws) | Practical Java + AWS tutorials | ✅ |
| [Spring Boot on AWS (book)](https://stratospheric.dev) | Full book: Spring Boot + AWS | 💰 |
| [AWS re:Invent Java talks](https://youtube.com/@AWSEventsChannel) | Deep dives | ✅ |

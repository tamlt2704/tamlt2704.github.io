# Chapter 15: Ship It

[← Chapter 14: Auth & Multi-tenancy](chapter-14-auth.md)

---

## Goal

Package and deploy FlowCraft as a production-ready application. Docker images, health checks, observability, and deployment options. By the end: you have a deployable product.

## Step 1: Dockerize the Backend

**flowcraft-engine/Dockerfile:**
```dockerfile
# Build stage
FROM eclipse-temurin:21-jdk AS build
WORKDIR /app
COPY gradle/ gradle/
COPY gradlew build.gradle.kts settings.gradle.kts ./
RUN ./gradlew dependencies --no-daemon
COPY src/ src/
RUN ./gradlew bootJar --no-daemon

# Runtime stage
FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=build /app/build/libs/*.jar app.jar

# Non-root user
RUN addgroup --system app && adduser --system --ingroup app app
USER app

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8080/actuator/health || exit 1

ENTRYPOINT ["java", "-jar", "app.jar"]
```

## Step 2: Dockerize the Frontend

**flowcraft-ui/Dockerfile:**
```dockerfile
# Build stage
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Runtime stage (nginx)
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

**flowcraft-ui/nginx.conf:**
```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API to backend
    location /api/ {
        proxy_pass http://engine:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Proxy WebSocket
    location /ws {
        proxy_pass http://engine:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Step 3: Docker Compose (Production)

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  ui:
    build: ./flowcraft-ui
    ports:
      - "80:80"
    depends_on:
      - engine

  engine:
    build: ./flowcraft-engine
    ports:
      - "8080:8080"
    environment:
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/flowcraft
      SPRING_DATASOURCE_USERNAME: flowcraft
      SPRING_DATASOURCE_PASSWORD: ${DB_PASSWORD}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      JAVA_OPTS: "-Xmx512m -Xms256m"
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/actuator/health"]
      interval: 30s
      timeout: 5s
      retries: 3

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: flowcraft
      POSTGRES_USER: flowcraft
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U flowcraft"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  pgdata:
```

## Step 4: Health & Readiness

**application.yml:**
```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: when-authorized
      probes:
        enabled: true  # Kubernetes liveness/readiness probes

  health:
    db:
      enabled: true
    diskSpace:
      enabled: true
```

Custom health indicator for deployed flows:

```kotlin
@Component
class FlowHealthIndicator(
    private val flowRuntime: FlowRuntime,
) : HealthIndicator {

    override fun health(): Health {
        val deployed = flowRuntime.listDeployed()
        val running = deployed.count { it.status == FlowState.RUNNING }
        val errors = deployed.count { it.status == FlowState.ERROR }

        return if (errors == 0) {
            Health.up()
                .withDetail("flows.running", running)
                .withDetail("flows.total", deployed.size)
                .build()
        } else {
            Health.down()
                .withDetail("flows.errors", errors)
                .withDetail("flows.running", running)
                .build()
        }
    }
}
```

## Step 5: Observability

### Metrics (Prometheus + Grafana)

```kotlin
@Component
class FlowMetrics(private val meterRegistry: MeterRegistry) {

    fun recordMessageProcessed(flowId: String, nodeId: String, durationMs: Long) {
        meterRegistry.counter("flowcraft.messages.processed",
            "flow_id", flowId,
            "node_id", nodeId
        ).increment()

        meterRegistry.timer("flowcraft.node.duration",
            "flow_id", flowId,
            "node_id", nodeId
        ).record(java.time.Duration.ofMillis(durationMs))
    }

    fun recordError(flowId: String, nodeId: String) {
        meterRegistry.counter("flowcraft.messages.errors",
            "flow_id", flowId,
            "node_id", nodeId
        ).increment()
    }
}
```

### Structured Logging

```kotlin
// logback-spring.xml for JSON logs in production
// application.yml:
logging:
  pattern:
    console: "%d{ISO8601} [%thread] %-5level %logger{36} - %msg%n"
  level:
    com.flowcraft: INFO
    org.springframework.integration: WARN
```

## Step 6: Graceful Shutdown

When the server stops, drain in-flight messages:

```yaml
server:
  shutdown: graceful

spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s
```

```kotlin
@Component
class GracefulShutdown(
    private val flowRuntime: FlowRuntime,
) {
    @PreDestroy
    fun onShutdown() {
        // Stop accepting new messages, let in-flight complete
        flowRuntime.listDeployed()
            .filter { it.status == FlowState.RUNNING }
            .forEach { flow ->
                flowRuntime.undeploy(flow.id)
            }
    }
}
```

## Step 7: Environment Configuration

**.env.example:**
```env
DB_PASSWORD=change-me-in-production
OPENAI_API_KEY=sk-...
JWT_SECRET=your-256-bit-secret
```

## Deployment Options

### Option A: Single Server (Docker Compose)
- Good for: small teams, self-hosted, < 100 flows
- Just `docker compose up -d`

### Option B: Kubernetes
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flowcraft-engine
spec:
  replicas: 2
  selector:
    matchLabels:
      app: flowcraft-engine
  template:
    spec:
      containers:
        - name: engine
          image: flowcraft/engine:latest
          ports:
            - containerPort: 8080
          livenessProbe:
            httpGet:
              path: /actuator/health/liveness
              port: 8080
            initialDelaySeconds: 30
          readinessProbe:
            httpGet:
              path: /actuator/health/readiness
              port: 8080
            initialDelaySeconds: 10
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
```

### Option C: Cloud PaaS
- AWS: ECS/Fargate + RDS PostgreSQL
- GCP: Cloud Run + Cloud SQL
- Azure: Container Apps + Azure Database

## The Final Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Load Balancer                              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
    ┌─────────▼─────────┐     ┌──────────▼──────────┐
    │   UI (nginx)       │     │   UI (nginx)        │
    │   Static + Proxy   │     │   Static + Proxy    │
    └─────────┬─────────┘     └──────────┬──────────┘
              │                           │
              └─────────────┬─────────────┘
                            │
              ┌─────────────▼─────────────┐
              │   Engine (Spring Boot)     │
              │   × 2 replicas            │
              │                           │
              │   ┌─────────────────┐     │
              │   │ Flow Runtime    │     │
              │   │ (per instance)  │     │
              │   └─────────────────┘     │
              └─────────────┬─────────────┘
                            │
              ┌─────────────▼─────────────┐
              │   PostgreSQL               │
              │   (flow definitions)       │
              └───────────────────────────┘
```

## What You've Built

| Feature | Status |
|---|---|
| Visual flow editor (React Flow) | ✅ |
| Drag-and-drop node palette | ✅ |
| Connection validation | ✅ |
| Node configuration panel | ✅ |
| Spring Integration engine | ✅ |
| Flow compiler (JSON → DSL) | ✅ |
| Dynamic deploy/undeploy | ✅ |
| HTTP, Timer, File adapters | ✅ |
| Transform, Filter, Script | ✅ |
| LLM/AI node (Spring AI) | ✅ |
| Database read/write | ✅ |
| Live monitoring (WebSocket) | ✅ |
| Error handling & retry | ✅ |
| Dead letter queue | ✅ |
| Auth & multi-tenancy | ✅ |
| Docker deployment | ✅ |
| Health checks & metrics | ✅ |

## What's Next (Beyond This Course)

| Feature | Effort | Impact |
|---|---|---|
| Kafka/AMQP adapters | Medium | Enterprise messaging |
| Flow versioning (Git-like) | Medium | Audit trail |
| Collaborative editing | High | Team workflows |
| Marketplace (share nodes) | High | Community growth |
| Visual debugger (step-through) | High | Developer experience |
| Auto-scaling per flow | High | Enterprise scale |
| GraalVM native image | Medium | Faster startup |
| Scheduled flows (cron UI) | Low | Common use case |
| Webhook testing UI | Low | Developer experience |
| Import from n8n/Node-RED | Medium | Migration path |

## The Product Pitch (Final)

> **FlowCraft** — Build integrations visually, run them at enterprise scale.
>
> Drag Input, Processing, and Output blocks onto a canvas. Connect them. Deploy with one click. Monitor in real-time.
>
> Powered by Spring Integration — transactions, retry, clustering, and the entire Java ecosystem. For teams that need more than Zapier but less than custom code.

---

You've built a product. Ship it. 🚀

[← Chapter 14: Auth & Multi-tenancy](chapter-14-auth.md)

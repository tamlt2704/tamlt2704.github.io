# Chapter 30: Docker — Containerise Everything

## What you'll learn

- What containers are (and how they differ from VMs)
- Docker images, layers, and the build cache
- Writing Dockerfiles: from basic to production-optimised
- Docker Compose for multi-service development
- Networking: how containers talk to each other
- Volumes: persistent data that survives container restarts
- Multi-stage builds for minimal production images
- Docker for your full stack: Next.js + Spring Boot + PostgreSQL + Redis
- Security best practices and common mistakes
- Container orchestration concepts (Kubernetes intro)

---

## PART 1: Docker Fundamentals

## 30.1 Containers vs VMs

```
Virtual Machine:                    Container:

┌───────────────────────┐          ┌───────────────────────┐
│ Your App              │          │ Your App              │
├───────────────────────┤          ├───────────────────────┤
│ Libraries/Deps        │          │ Libraries/Deps        │
├───────────────────────┤          ├───────────────────────┤
│ Guest OS (full Linux) │          │ (shares host kernel)  │
├───────────────────────┤          └───────────┬───────────┘
│ Hypervisor            │                      │
├───────────────────────┤          ┌───────────┴───────────┐
│ Host OS               │          │ Docker Engine         │
├───────────────────────┤          ├───────────────────────┤
│ Hardware              │          │ Host OS               │
└───────────────────────┘          ├───────────────────────┤
                                   │ Hardware              │
Size: ~GB, boot: minutes           └───────────────────────┘
                                   Size: ~MB, boot: seconds
```

**Containers are:**
- Isolated processes (not virtual machines)
- Sharing the host kernel (no separate OS)
- Lightweight (MB not GB, start in seconds not minutes)
- Portable (same image runs on any machine with Docker)
- Reproducible (defined in code, built deterministically)

## 30.2 Key concepts

| Concept | Analogy | What it is |
|---------|---------|------------|
| **Image** | A class | Blueprint: read-only template with OS, libs, code |
| **Container** | An instance | Running process created from an image |
| **Dockerfile** | Source code | Instructions to build an image |
| **Registry** | Package repo (npm, Maven) | Stores and distributes images (Docker Hub, ECR, GCR) |
| **Volume** | External hard drive | Persistent storage that outlives containers |
| **Network** | Private LAN | Virtual network for container-to-container communication |

## 30.3 Essential commands

```bash
# Images
docker build -t myapp:1.0 .           # Build image from Dockerfile in current dir
docker images                           # List local images
docker pull nginx:alpine               # Download image from registry
docker push myuser/myapp:1.0           # Upload image to registry
docker rmi myapp:1.0                   # Remove image

# Containers
docker run -d -p 8080:8080 myapp:1.0  # Run container (detached, port mapped)
docker ps                               # List running containers
docker ps -a                            # List ALL containers (including stopped)
docker logs <container-id>             # View container output
docker logs -f <container-id>          # Follow logs (like tail -f)
docker exec -it <container-id> sh      # Open shell inside container
docker stop <container-id>             # Graceful stop (SIGTERM → SIGKILL after 10s)
docker rm <container-id>               # Remove stopped container

# Cleanup
docker system prune                     # Remove unused images, containers, networks
docker system prune -a                  # Remove ALL unused images (reclaim disk space)
```

**`docker run` flags:**
| Flag | Purpose | Example |
|------|---------|---------|
| `-d` | Detached (background) | `docker run -d nginx` |
| `-p host:container` | Port mapping | `-p 3000:3000` |
| `-v host:container` | Volume mount | `-v ./data:/app/data` |
| `-e KEY=VAL` | Environment variable | `-e DATABASE_URL=...` |
| `--name` | Container name | `--name my-api` |
| `--rm` | Remove container when it stops | `docker run --rm ...` |
| `-it` | Interactive terminal | `docker exec -it ... sh` |
| `--network` | Connect to network | `--network my-net` |

## 30.4 Your first Dockerfile

```dockerfile
# Every Dockerfile starts with a base image
FROM node:20-alpine

# Set working directory inside the container
WORKDIR /app

# Copy dependency files first (for cache efficiency)
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy the rest of the application
COPY . .

# Build the application
RUN npm run build

# Expose port (documentation — doesn't actually publish)
EXPOSE 3000

# Command to run when container starts
CMD ["npm", "start"]
```

**Build and run:**
```bash
docker build -t my-nextjs-app .
docker run -p 3000:3000 my-nextjs-app
# Visit http://localhost:3000
```

## 30.5 Understanding layers and the build cache

Each Dockerfile instruction creates a **layer**. Docker caches layers — unchanged layers are reused.

```dockerfile
FROM node:20-alpine          # Layer 1: base OS + Node (cached from registry)
WORKDIR /app                 # Layer 2: set working dir
COPY package.json ./         # Layer 3: copy package.json
RUN npm ci                   # Layer 4: install deps (SLOW — only re-runs if package.json changed)
COPY . .                     # Layer 5: copy source code (changes often)
RUN npm run build            # Layer 6: build (re-runs if source changed)
```

**Why COPY package.json before COPY source:**
```
Change source code → layers 5, 6 re-run (fast — deps already installed)
Change dependencies → layers 3, 4, 5, 6 re-run (slow — npm install)
```

If you did `COPY . .` first, EVERY code change would re-install all dependencies.

> **Rule: Put things that change LEAST at the top, things that change MOST at the bottom.** This maximises cache hits.

---

## PART 2: Production Dockerfiles

## 30.6 Multi-stage build (Next.js)

```dockerfile
# Stage 1: Install dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Stage 2: Build the application
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Stage 3: Production image (minimal)
FROM node:20-alpine AS runner
WORKDIR /app

# Don't run as root
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy only what's needed to run
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

**Why multi-stage?**
- Build stage has devDependencies, source code, build tools — hundreds of MB
- Production stage has only the runtime output — ~50-100MB
- Smaller image = faster deploy, less attack surface, less storage cost

> **For Next.js standalone output**, add to `next.config.ts`:
> ```ts
> const nextConfig = { output: "standalone" };
> ```
> This creates a minimal self-contained server in `.next/standalone`.

## 30.7 Multi-stage build (Spring Boot)

```dockerfile
# Stage 1: Build with Maven
FROM eclipse-temurin:21-jdk-alpine AS build
WORKDIR /app
COPY pom.xml .
COPY .mvn .mvn
COPY mvnw .
RUN chmod +x mvnw

# Download dependencies first (cached separately from source)
RUN ./mvnw dependency:go-offline -B

# Copy source and build
COPY src ./src
RUN ./mvnw package -DskipTests -B

# Stage 2: Production runtime
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app

# Non-root user
RUN addgroup -S spring && adduser -S spring -G spring
USER spring

# Copy JAR from build stage
COPY --from=build /app/target/*.jar app.jar

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

**Size comparison:**
```
JDK image (build):  ~400MB
JRE image (runtime): ~180MB
With jlink (custom JRE): ~80MB
```

## 30.8 Multi-stage build (Python)

```dockerfile
FROM python:3.12-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Non-root user
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

---

## PART 3: Docker Compose — Multi-Service Development

## 30.9 What Docker Compose does

Docker Compose runs multiple containers as a single service. One `docker-compose.yml` defines your entire stack.

```yaml
# docker-compose.yml
services:
  # Next.js frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8080
    depends_on:
      - api
    volumes:
      - ./frontend/app:/app/app  # hot reload in dev

  # Spring Boot API
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=dev
      - DATABASE_URL=jdbc:postgresql://db:5432/myapp
      - DATABASE_USER=postgres
      - DATABASE_PASS=secret
      - REDIS_HOST=redis
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started

  # PostgreSQL database
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: secret
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  # Redis cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data

  # Kafka (for messaging)
  kafka:
    image: confluentinc/cp-kafka:7.5.0
    ports:
      - "9092:9092"
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka:29093
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:29093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1

volumes:
  pgdata:
  redisdata:
```

## 30.10 Compose commands

```bash
# Start everything
docker compose up                    # foreground (see all logs)
docker compose up -d                 # detached (background)

# Build and start
docker compose up --build            # rebuild images before starting

# Stop
docker compose down                  # stop and remove containers
docker compose down -v               # also remove volumes (WARNING: deletes data!)

# Individual services
docker compose up -d db redis        # start only specific services
docker compose logs api              # logs for one service
docker compose logs -f api           # follow logs

# Rebuild one service
docker compose build api
docker compose up -d api             # restart with new image

# Run one-off command
docker compose exec api sh           # shell into running container
docker compose run api ./mvnw test   # run command in new container
```

## 30.11 Networking in Compose

Docker Compose creates a **default network** for all services. Containers reference each other by **service name**:

```
frontend  → http://api:8080/api/tasks     (service name = hostname)
api       → jdbc:postgresql://db:5432/myapp
api       → redis://redis:6379
```

No `localhost` — use the service name. Docker's internal DNS resolves it.

```yaml
# Custom networks (for isolation):
services:
  frontend:
    networks: [frontend-net]
  api:
    networks: [frontend-net, backend-net]  # api can talk to both
  db:
    networks: [backend-net]                # db only reachable from api

networks:
  frontend-net:
  backend-net:
```

## 30.12 Volumes — persistent data

```yaml
volumes:
  pgdata:  # Named volume — Docker manages the location

services:
  db:
    volumes:
      - pgdata:/var/lib/postgresql/data    # Named volume (persists across restarts)
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql  # Bind mount (for seed data)
```

| Volume type | Syntax | Persists? | Use case |
|-------------|--------|-----------|----------|
| Named volume | `pgdata:/var/lib/...` | Yes (managed by Docker) | Database data, Redis data |
| Bind mount | `./local:/container` | Yes (on your filesystem) | Source code (dev), config files |
| tmpfs | `tmpfs: /tmp` | No (in memory) | Temp files, secrets at runtime |

---

## PART 4: Development Workflow

## 30.13 Dev vs Prod Dockerfiles

**Development (with hot reload):**
```dockerfile
# Dockerfile.dev
FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
# Don't copy source — mount as volume for hot reload
EXPOSE 3000
CMD ["npm", "run", "dev"]
```

```yaml
# docker-compose.dev.yml
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    volumes:
      - ./frontend:/app          # source code mounted (hot reload)
      - /app/node_modules        # anonymous volume (don't overwrite node_modules)
    ports:
      - "3000:3000"
```

**The `/app/node_modules` trick:** Without it, the bind mount of `./frontend:/app` would overwrite the container's `node_modules` (installed during build). The anonymous volume preserves the container's node_modules.

## 30.14 .dockerignore

Like `.gitignore` but for Docker builds. Prevents sending unnecessary files to the build context:

```
# .dockerignore
node_modules
.next
.git
*.md
.env*
.DS_Store
coverage
dist
.idea
.vscode
```

**Why it matters:** Without this, `COPY . .` sends your entire `node_modules` (hundreds of MB) to the Docker daemon, even though you're about to `npm ci` anyway. Builds go from 30 seconds to 5 seconds with a good `.dockerignore`.

## 30.15 Environment variables and secrets

```yaml
services:
  api:
    environment:
      # Inline (visible in docker-compose.yml — OK for dev)
      - SPRING_PROFILES_ACTIVE=dev
      - APP_NAME=task-api

    env_file:
      # From .env file (gitignored — better for secrets)
      - .env

    secrets:
      - db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt  # or use Docker Swarm / external secret manager
```

```bash
# .env (gitignored!)
DATABASE_URL=jdbc:postgresql://db:5432/myapp
DATABASE_USER=postgres
DATABASE_PASS=supersecret
JWT_SECRET=my-256-bit-secret
```

> **Never bake secrets into images.** Use environment variables or secret management (AWS Secrets Manager, HashiCorp Vault). Secrets in images end up in layer history — anyone with the image can extract them.

---

## PART 5: Security & Best Practices

## 30.16 Security checklist

```
□ Use specific image tags (node:20-alpine, NOT node:latest)
□ Run as non-root user (USER appuser)
□ Use multi-stage builds (no build tools in production image)
□ Scan images for vulnerabilities (docker scout cves, Trivy, Snyk)
□ Don't store secrets in images or Dockerfiles
□ Use .dockerignore (don't leak .env, .git, node_modules)
□ Pin dependency versions (npm ci with lockfile, not npm install)
□ Use minimal base images (alpine, slim, distroless)
□ Set read-only filesystem where possible (--read-only)
□ Limit container resources (--memory, --cpus)
```

## 30.17 Image size optimisation

| Base image | Size | Includes |
|-----------|------|----------|
| `node:20` | ~1GB | Full Debian, build tools, everything |
| `node:20-slim` | ~200MB | Minimal Debian, no build tools |
| `node:20-alpine` | ~130MB | Alpine Linux (musl libc) |
| `gcr.io/distroless/nodejs20` | ~50MB | Just the runtime, no shell, no package manager |

**Production strategy:**
```
Build stage: use full image (need npm, compilers, etc.)
Runtime stage: use alpine or distroless (minimal attack surface)
```

## 30.18 Health checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:8080/actuator/health || exit 1
```

```yaml
# In docker-compose.yml
services:
  api:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/actuator/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

Health checks let Docker (and orchestrators like Kubernetes) know if your container is actually working — not just running.

## 30.19 Debugging containers

```bash
# View logs
docker logs <container> --tail 100

# Shell into running container
docker exec -it <container> sh

# Inspect container config/state
docker inspect <container>

# See resource usage
docker stats

# See what's inside an image (without running it)
docker run --rm -it <image> sh

# Copy files out of a container
docker cp <container>:/app/logs/error.log ./error.log

# See build history (what each layer added)
docker history <image>
```

---

## PART 6: Beyond Docker — Orchestration

## 30.20 When you need more than Docker Compose

Docker Compose is for **development** and **single-server deployment**. When you need:
- Multiple servers (horizontal scaling)
- Auto-restart on crash
- Rolling deployments (zero downtime)
- Service discovery
- Load balancing across instances
- Auto-scaling based on CPU/memory

You need an orchestrator: **Kubernetes** (or ECS, Docker Swarm, Nomad).

## 30.21 Kubernetes in 60 seconds

```yaml
# deployment.yaml — "run 3 copies of my API"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: task-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: task-api
  template:
    metadata:
      labels:
        app: task-api
    spec:
      containers:
        - name: api
          image: myregistry/task-api:1.0.0
          ports:
            - containerPort: 8080
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: url
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          readinessProbe:
            httpGet:
              path: /actuator/health
              port: 8080
            initialDelaySeconds: 30
---
# service.yaml — "load balance traffic to the 3 copies"
apiVersion: v1
kind: Service
metadata:
  name: task-api
spec:
  selector:
    app: task-api
  ports:
    - port: 80
      targetPort: 8080
  type: LoadBalancer
```

**Kubernetes concepts:**
| Concept | What it does |
|---------|-------------|
| Pod | Smallest unit — one or more containers running together |
| Deployment | Manages pod replicas, rolling updates, rollbacks |
| Service | Stable network endpoint + load balancing across pods |
| Ingress | External HTTP routing (like nginx reverse proxy) |
| ConfigMap | Non-secret configuration (env vars, config files) |
| Secret | Sensitive data (passwords, tokens) |
| PersistentVolumeClaim | Storage that outlives pods |

---

## Summary

✅ Containers vs VMs: isolated processes sharing host kernel, not full virtual machines
✅ Dockerfile: FROM, WORKDIR, COPY, RUN, EXPOSE, CMD — layers and cache optimisation
✅ Multi-stage builds: separate build tools from production runtime (smaller, safer images)
✅ Docker Compose: define multi-service stacks (frontend + API + DB + Redis + Kafka)
✅ Networking: containers reference each other by service name, custom networks for isolation
✅ Volumes: named volumes for data persistence, bind mounts for dev hot reload
✅ Dev workflow: Dockerfile.dev with volume mounts, .dockerignore, env_file
✅ Security: non-root user, minimal base images, no secrets in images, vulnerability scanning
✅ Health checks: Docker and Kubernetes know if your app is actually working
✅ Kubernetes intro: Deployment (replicas), Service (load balancing), scaling

## Key takeaways

**Docker makes "works on my machine" impossible.** The Dockerfile IS the environment. If it builds, it runs the same everywhere — dev, CI, staging, production.

**Layer order matters.** Put things that change rarely at the top (base image, dependencies) and things that change often at the bottom (source code). This maximises cache hits and makes rebuilds fast.

**Multi-stage builds are non-negotiable for production.** Your build image has compilers, dev tools, and source code. Your production image should have only the compiled output and runtime. This reduces image size by 5-10×.

**Docker Compose is your local development superpower.** `docker compose up` starts your entire stack — database, cache, message queue, API, frontend — in seconds. New team member? Clone repo, run one command, done.

---

→ [Back to Chapter 29: Mastering Spring Boot](./29-MASTERING-SPRING-BOOT.md)

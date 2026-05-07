# Docker 101 — From Zero to Production

> A story-driven guide. You're a developer who just got hired. Your app works on your laptop. Now you need to ship it to the world.

---

## Chapter 0: The Problem Docker Solves

### The Scene

It's your first week. You've built a Flask app on your laptop — Python 3.11, numpy, Flask, everything works perfectly. You push it to the production server. It crashes.

The server has Python 3.9. It's missing numpy. The OS libraries are wrong. Your manager walks over:

> "Works on my machine" 🤷

This is the problem Docker solves.

### The Old Way: Virtual Machines

Before Docker, the answer was VMs. Each VM runs a full guest operating system on top of a hypervisor. You get strong isolation, but:

| Metric | VM |
|--------|-----|
| Size | 1–10 GB |
| Boot time | Minutes |
| OS | Full guest OS per VM |
| Density | ~10 per host |

You're shipping an entire operating system just to run a 5 MB app.

### The Docker Way: Containers

Docker replaces the hypervisor with the **Docker Engine**. Containers share the host kernel — no guest OS needed.

| Metric | VM | Container |
|--------|-----|-----------|
| Size | 1–10 GB | 10–100 MB |
| Boot | Minutes | Seconds |
| OS | Full Guest OS | Shares Host |
| Isolation | Strong | Process-level |
| Density | ~10 per host | ~100s per host |

A container is your app + its dependencies, packaged together. Same environment everywhere — your laptop, CI, staging, production.

```
Your Laptop        →  deploy  →  Production Server
[Python 3.11]                    [Python 3.11]
[Flask + numpy]                  [Flask + numpy]
[Ubuntu 22.04]                   [Ubuntu 22.04]
     ✓ Works!                         ✓ Works!
```

The container IS the environment.

---

## Chapter 1: Images & Containers

### What is an Image?

An image is a **read-only template** — a blueprint containing everything your app needs:

- Base OS (Ubuntu, Alpine)
- Runtime (Python, Node)
- Libraries (Flask, numpy)
- Your application code

Think of it like a class definition. You don't run the class — you instantiate it.

### Images Are Made of Layers

Images aren't monolithic blobs. They're stacked layers, like a cake:

```
┌─────────────────────────┐
│ CMD python app.py       │  ← Layer 5
├─────────────────────────┤
│ COPY app.py /app/       │  ← Layer 4
├─────────────────────────┤
│ pip install flask        │  ← Layer 3
├─────────────────────────┤
│ apt install python3      │  ← Layer 2
├─────────────────────────┤
│ Ubuntu 22.04 (base)      │  ← Layer 1
└─────────────────────────┘
```

Each layer is cached. Change your app code? Only layers 4 and 5 rebuild. The base OS and dependencies stay cached.

### Image → Container

```
Image (read-only)  ──docker run──→  Container (running)
```

A container is an image + a **writable layer** + a running process. The image stays untouched. The container gets its own filesystem on top.

One image can spawn many containers — each independent, each with its own state:

```
                    ┌── web-1 (container)
nginx image ───────┼── web-2 (container)
                    └── web-3 (container)
```

### Essential Commands

```bash
$ docker pull nginx          # Download an image from Docker Hub
$ docker run nginx           # Create + start a container
$ docker ps                  # List running containers
$ docker stop <id>           # Stop a running container
$ docker rm <id>             # Remove a stopped container
$ docker images              # List downloaded images
```

---

## Chapter 2: The Dockerfile

### Recipe → Cake. Dockerfile → Image.

A Dockerfile is a text file with instructions to build an image. Each line becomes a layer.

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

What each instruction does:

| Instruction | Purpose |
|-------------|---------|
| `FROM` | Base image to start from |
| `WORKDIR` | Set the working directory inside the container |
| `COPY` | Copy files from your machine into the image |
| `RUN` | Execute a command during build (install deps, compile) |
| `CMD` | Default command when the container starts |

### Building the Image

```bash
$ docker build -t myapp .
```

- `-t myapp` → name (tag) the image
- `.` → build context (current directory)

Docker reads the Dockerfile, executes each instruction, and produces a tagged image.

### Layer Caching: Why Order Matters

```
┌─────────────────────────┐
│ CMD python app.py       │  ← REBUILD (above changed layer)
├─────────────────────────┤
│ COPY app code           │  ← REBUILD (you edited app.py)
├─────────────────────────┤
│ RUN pip install         │  ← CACHED ✓
├─────────────────────────┤
│ COPY requirements.txt   │  ← CACHED ✓
├─────────────────────────┤
│ FROM python:3.11-slim   │  ← CACHED ✓
└─────────────────────────┘
```

When a layer changes, everything above it rebuilds. That's why you copy `requirements.txt` first and install dependencies *before* copying your app code. Dependencies change rarely; code changes constantly.

### Best Practices

- ✓ Use slim/alpine base images (smaller)
- ✓ COPY requirements first, then code (cache-friendly)
- ✓ Combine RUN commands (fewer layers)
- ✗ Don't COPY unnecessary files (use `.dockerignore`)
- ✗ Don't run as root (use `USER`)

---

## Chapter 3: Volumes

### The Problem: Data Disappears

Containers are ephemeral. When a container is removed, its writable layer is gone — along with any data written inside it.

```bash
$ docker rm postgres
# 💥 All your database files? Gone. Forever.
```

### Volumes: Data That Survives

A volume is storage that lives **outside** the container. The container can die, be removed, be replaced — the volume persists.

```
┌─────────────────┐
│   postgres      │  ← container (ephemeral)
│   container     │
└────────┬────────┘
         │ mount
┌────────┴────────┐
│   pgdata        │  ← volume (persistent)
│   /var/lib/...  │
└─────────────────┘
```

Container removed? Start a new one, mount the same volume — all your data is still there.

### Named Volumes

```bash
$ docker run -v pgdata:/var/lib/postgresql/data postgres
```

Breaking it down:

```
-v  pgdata  :  /var/lib/postgresql/data
     │                    │
     │                    └── path inside container
     └── volume name (Docker manages storage)
```

Docker stores the volume in `/var/lib/docker/volumes/`. You don't need to know where — Docker handles it.

### Bind Mounts (for Development)

```bash
$ docker run -v $(pwd):/app myapp
```

A bind mount maps a folder on your laptop directly into the container. Edit code on your machine → changes appear in the container instantly. Perfect for development.

```
┌─────────────┐         ┌─────────────┐
│ Your Laptop │ ←live→  │  Container  │
│   ./src/    │  sync   │   /app/     │
└─────────────┘         └─────────────┘
```

### When to Use What

| Type | Use Case |
|------|----------|
| Named volume | Database data, persistent state |
| Bind mount | Development (live code reload) |

---

## Chapter 4: Networking

### The Problem: Containers Are Isolated

By default, containers can't see each other. Your web server can't reach your API. Your API can't reach your database.

```
[web] ──✗──→ [api] ──✗──→ [db]
```

### Bridge Network

A bridge network is a virtual road connecting containers. Containers on the same network can communicate by name.

```bash
$ docker network create my-net
$ docker run --network my-net --name web nginx
$ docker run --network my-net --name api node
```

Now `web` can reach `api` at `http://api:3000` — by container name, not IP address.

```
┌─────────────────────────────────────────┐
│         bridge network (my-net)          │
├─────────────────────────────────────────┤
│                                         │
│  [web] ──────── [api] ──────── [db]     │
│                                         │
└─────────────────────────────────────────┘
```

### Port Mapping: Exposing to the Outside

Containers live in their own network. To let the outside world reach them, you map a host port to a container port:

```bash
$ docker run -p 8080:80 nginx
```

```
Browser                Host Machine
localhost:8080  ──→    port 8080  ──→  container port 80
                                       (nginx)
```

`-p host:container` — the left side is what you type in your browser, the right side is what the container listens on.

---

## Chapter 5: Docker Compose

### The Problem: Too Many Commands

A real app has multiple services. Without Compose, you're typing this every time:

```bash
$ docker network create app-net
$ docker run -d --name db --network app-net -v pgdata:/data postgres
$ docker run -d --name redis --network app-net redis
$ docker run -d --name api --network app-net -p 8080:8080 myapi
$ docker run -d --name web --network app-net -p 3000:80 nginx
```

Five commands. In the right order. Hope you don't typo.

### One File to Rule Them All

```yaml
# docker-compose.yml
services:
  web:
    image: nginx
    ports: ['3000:80']
  api:
    build: ./api
    ports: ['8080:8080']
  db:
    image: postgres
    volumes: ['pgdata:/data']
  redis:
    image: redis

volumes:
  pgdata:
```

One file defines everything. One command runs it all.

### Starting and Stopping

```bash
$ docker compose up -d       # Start all services (detached)
$ docker compose down        # Stop and remove all
$ docker compose logs -f     # Follow logs from all services
$ docker compose ps          # List running services
```

### depends_on: Start Order

```yaml
services:
  api:
    depends_on:
      - db
      - redis
  web:
    depends_on:
      - api
```

Start order: `db` → `redis` → `api` → `web`. Docker Compose handles the sequencing.

Networks and volumes are auto-created — no manual `docker network create` needed.

---

## Chapter 6: Multi-stage Builds

### The Problem: Fat Images

A naive Dockerfile includes everything — build tools, compilers, dev dependencies:

```
Ubuntu 22.04        80 MB
gcc, make, cmake   400 MB
npm install        300 MB
npm run build        5 MB
Your app             2 MB
─────────────────────────
Total:            ~787 MB 😱
```

You're shipping 785 MB of build tools you don't need at runtime.

### The Solution: Build, Then Copy

Multi-stage builds use two (or more) `FROM` statements. Build in one stage, copy only the output to a minimal runtime stage.

```dockerfile
# Stage 1: Build
FROM node:22 AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Runtime
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
```

Stage 1 has Node, npm, all your dev dependencies — it compiles your app. Stage 2 starts fresh from `nginx:alpine` and copies only the built output.

### The Result

```
Single stage:  ████████████████████████████████████  787 MB
Multi-stage:   █                                      25 MB
```

**97% smaller.** Faster deploys, smaller attack surface, less bandwidth.

### Key Instruction

```dockerfile
COPY --from=build /app/dist /usr/share/nginx/html
```

`--from=build` reaches back into the build stage and grabs files. The build stage is discarded — it never ships.

---

## Chapter 7: Docker Hub & Registry

### Docker Hub = App Store for Images

Docker Hub (`hub.docker.com`) is a public registry with thousands of pre-built images: nginx, postgres, redis, node, python, ubuntu — ready to pull and run.

```bash
$ docker pull nginx          # Download from Docker Hub
$ docker push myuser/myapp   # Upload your image
```

### Tags = Versions

Tags let you pin specific versions:

```
python:3.11          ← Specific version
python:3.11-slim     ← Smaller variant
python:3.11-alpine   ← Smallest (~50 MB)
python:latest        ← Most recent (risky!)
```

⚠ **Always pin versions.** Never use `:latest` in production. Today's `latest` is tomorrow's breaking change.

### Private Registries

For proprietary code, use a private registry:

- Docker Hub (private repos)
- AWS ECR
- Google Artifact Registry
- GitHub Container Registry
- Self-hosted (Harbor, etc.)

```bash
$ docker tag myapp registry.example.com/myapp:1.2.0
$ docker push registry.example.com/myapp:1.2.0
```

---

## Chapter 8: Health Checks & Logs

### Health Checks

A running container isn't necessarily a *healthy* container. The process might be up but deadlocked, or the app might have lost its database connection.

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
```

Docker pings your health endpoint every 30 seconds. Three failures in a row → container marked `unhealthy`.

Status indicators:
- `healthy` ✓ — endpoint responds
- `unhealthy` ✗ — endpoint failing
- `starting` ◌ — grace period after boot

### Logs

```bash
$ docker logs api            # Show all logs
$ docker logs -f api         # Follow (live stream, like tail -f)
$ docker logs --tail 50 api  # Last 50 lines
```

Containers write to stdout/stderr. Docker captures it all. In production, you'd pipe these to a log aggregator (ELK, Datadog, CloudWatch).

### Restart Policies

What happens when a container crashes at 3 AM?

```bash
$ docker run --restart=on-failure myapp
```

| Policy | Behavior |
|--------|----------|
| `no` | Never restart (default) |
| `on-failure` | Restart only if exit code ≠ 0 |
| `always` | Always restart (even after manual stop) |
| `unless-stopped` | Always, except if manually stopped |

Container crashes → Docker restarts it automatically. No pager duty for a simple OOM.

---

## Chapter 9: Docker in Production

### Stage 1: One Container

You start simple. One server, one container:

```bash
$ docker run -d -p 8080:8080 --restart=unless-stopped myapi
```

Works for small traffic. But what happens when 10,000 users hit it simultaneously?

### Stage 2: Scale Up

```bash
$ docker compose up --scale api=3
```

Three copies of the same container. But who routes traffic to them?

### Stage 3: Load Balancer

Put nginx (or Traefik, or HAProxy) in front. It distributes requests across your containers:

```
                    ┌── api-1
Users → nginx(LB) ─┼── api-2
                    └── api-3
```

The load balancer health-checks each container and routes traffic only to healthy ones.

### Stage 4: Orchestration

One server isn't enough. You need containers spread across multiple machines, auto-healing, auto-scaling.

Enter **orchestrators**:

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Server 1   │  │  Server 2   │  │  Server 3   │
│ [api] [api] │  │ [api] [api] │  │ [api] [api] │
└─────────────┘  └─────────────┘  └─────────────┘
         │              │              │
         └──────── Kubernetes ─────────┘
```

Kubernetes (or Docker Swarm) manages containers across servers automatically:
- Container crashes? Restart it.
- Server dies? Reschedule containers elsewhere.
- Traffic spikes? Scale up. Traffic drops? Scale down.

### The Journey

```
1 container → 3 containers → + load balancer → orchestration
```

You don't need Kubernetes on day one. Start with a single container, add complexity only when traffic demands it.

---

## The Full Path

| Chapter | Concept | Key Takeaway |
|---------|---------|--------------|
| 0 | What is Docker | Containers = app + deps, no guest OS |
| 1 | Images & Containers | Image = blueprint, Container = running instance |
| 2 | Dockerfile | Recipe for building images, layers, caching |
| 3 | Volumes | Persistent data that survives container death |
| 4 | Networking | Bridge networks, port mapping, DNS by name |
| 5 | Docker Compose | Multi-service apps in one YAML file |
| 6 | Multi-stage Builds | Ship only what you need (97% smaller) |
| 7 | Registry | Push/pull images, pin versions |
| 8 | Health & Logs | Monitor, stream logs, auto-restart |
| 9 | Production | Scale → load balance → orchestrate |

---

## Quick Reference

```bash
# Images
docker build -t myapp .
docker images
docker pull nginx:1.25
docker push myuser/myapp:1.0.0

# Containers
docker run -d -p 8080:80 --name web nginx
docker ps
docker stop web
docker rm web
docker logs -f web

# Volumes
docker run -v pgdata:/var/lib/postgresql/data postgres
docker volume ls

# Networks
docker network create my-net
docker run --network my-net --name api myapp

# Compose
docker compose up -d
docker compose down
docker compose logs -f
docker compose ps

# Cleanup
docker system prune -a    # Remove all unused images/containers
```

---

*Based on the [acode/docker101](.) animated series — visual explanations of Docker concepts rendered with Manim.*

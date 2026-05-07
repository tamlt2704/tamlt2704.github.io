# Docker 101 — Practical Labs (Chapter by Chapter)

Hands-on exercises for each episode. Each lab builds on the previous one. By the end, you'll have deployed a multi-container application with persistent data, networking, and health checks.

**Prerequisites:**
- Docker Desktop installed (`docker --version` shows 20+)
- A terminal
- A text editor
- Basic command-line comfort

**The Project:** You'll build and containerize **TaskAPI** — a simple REST API with a database, step by step across all episodes.

---

## Episode 00: What Is Docker?

### Lab 0.1: Prove the Problem

Run a Python script that requires a specific library — without installing it on your machine:

```bash
# This would fail without requests installed:
# python3 -c "import requests; print(requests.get('https://httpbin.org/ip').json())"

# But with Docker, it works instantly:
docker run --rm python:3.11-slim python -c "
import urllib.request, json
print(json.loads(urllib.request.urlopen('https://httpbin.org/ip').read()))
"
```

### Lab 0.2: Container vs Your Machine

```bash
# Check your OS
cat /etc/os-release  # (or: sw_vers on macOS)

# Now check what's INSIDE a container
docker run --rm ubuntu:22.04 cat /etc/os-release
docker run --rm alpine:3.19 cat /etc/os-release

# Different OS, running on YOUR machine, isolated
```

### Lab 0.3: Containers Are Ephemeral

```bash
# Create a file inside a container
docker run --rm ubuntu:22.04 bash -c "echo 'hello' > /tmp/test.txt && cat /tmp/test.txt"
# Output: hello

# Run it again — the file is GONE
docker run --rm ubuntu:22.04 bash -c "cat /tmp/test.txt"
# Output: cat: /tmp/test.txt: No such file or directory
```

**Takeaway:** Containers are disposable. They start fresh every time. This is a feature, not a bug.

---

## Episode 01: Images & Containers

### Lab 1.1: Pull and Inspect

```bash
# Pull an image
docker pull nginx:alpine

# See what you have
docker images

# Inspect the image (see layers, size, config)
docker inspect nginx:alpine | head -50

# See the image history (each layer)
docker history nginx:alpine
```

### Lab 1.2: Run, List, Stop, Remove

```bash
# Run nginx in the background
docker run -d --name my-nginx -p 8080:80 nginx:alpine

# Verify it's running
docker ps

# Visit http://localhost:8080 in your browser (you should see "Welcome to nginx!")

# Check logs
docker logs my-nginx

# Stop it
docker stop my-nginx

# It's stopped but still exists
docker ps -a

# Remove it
docker rm my-nginx

# Now it's gone
docker ps -a
```

### Lab 1.3: Interactive Container

```bash
# Run Ubuntu interactively (like SSH-ing into a machine)
docker run -it --rm ubuntu:22.04 bash

# Inside the container:
whoami          # root
hostname        # random container ID
ls /            # standard Linux filesystem
apt update && apt install -y curl
curl https://httpbin.org/ip
exit            # container is destroyed (--rm)
```

### Lab 1.4: The Difference Between Image and Container

```bash
# One image, three containers:
docker run -d --name web1 -p 8081:80 nginx:alpine
docker run -d --name web2 -p 8082:80 nginx:alpine
docker run -d --name web3 -p 8083:80 nginx:alpine

# Three separate instances, same image
docker ps

# Each has its own filesystem, process space, network
# Visit :8081, :8082, :8083 — all serve nginx independently

# Clean up
docker stop web1 web2 web3
docker rm web1 web2 web3
```

---

## Episode 02: The Dockerfile

### Lab 2.1: Your First Dockerfile

Create a project directory:

```bash
mkdir -p ~/docker-labs/taskapi && cd ~/docker-labs/taskapi
```

Create `app.py`:

```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

tasks = [
    {"id": 1, "title": "Learn Docker", "done": False},
    {"id": 2, "title": "Build an API", "done": False},
]

class TaskHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(tasks).encode())

    def log_message(self, format, *args):
        print(f"[TaskAPI] {args[0]}")

server = HTTPServer(("0.0.0.0", 8000), TaskHandler)
print("TaskAPI running on port 8000")
server.serve_forever()
```

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY app.py .

EXPOSE 8000

CMD ["python", "app.py"]
```

Build and run:

```bash
docker build -t taskapi:v1 .
docker run -d --name taskapi -p 8000:8000 taskapi:v1

# Test it
curl http://localhost:8000
# [{"id": 1, "title": "Learn Docker", "done": false}, ...]

# Clean up
docker stop taskapi && docker rm taskapi
```

### Lab 2.2: Layer Caching

Add a `requirements.txt`:

```
flask==3.0.0
```

Update `Dockerfile` to demonstrate layer caching:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies FIRST (this layer is cached if requirements.txt doesn't change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code SECOND (this layer rebuilds when code changes)
COPY app.py .

EXPOSE 8000
CMD ["python", "app.py"]
```

```bash
# First build (slow — installs Flask)
docker build -t taskapi:v2 .

# Change app.py (add a comment)
echo "# updated" >> app.py

# Second build (fast — pip install is cached!)
docker build -t taskapi:v2 .
# Notice: "Using cache" for the pip install layer
```

### Lab 2.3: .dockerignore

Create `.dockerignore`:

```
__pycache__
*.pyc
.git
.env
node_modules
venv
```

```bash
# Check image size before and after .dockerignore
docker build -t taskapi:v2 .
docker images taskapi
```

---

## Episode 03: Volumes

### Lab 3.1: Data Disappears Without Volumes

```bash
# Run a container, create data inside it
docker run -d --name db-test postgres:16-alpine \
  -e POSTGRES_PASSWORD=secret

# Wait for it to start
sleep 3

# Create a table
docker exec db-test psql -U postgres -c "CREATE TABLE test (id serial, name text);"
docker exec db-test psql -U postgres -c "INSERT INTO test (name) VALUES ('hello');"
docker exec db-test psql -U postgres -c "SELECT * FROM test;"
# Output: 1 | hello

# Remove and recreate the container
docker stop db-test && docker rm db-test
docker run -d --name db-test postgres:16-alpine \
  -e POSTGRES_PASSWORD=secret
sleep 3

# Data is GONE
docker exec db-test psql -U postgres -c "SELECT * FROM test;"
# ERROR: relation "test" does not exist

docker stop db-test && docker rm db-test
```

### Lab 3.2: Named Volumes (Persist Data)

```bash
# Create a named volume
docker volume create taskapi-data

# Run postgres WITH the volume
docker run -d --name db \
  -e POSTGRES_PASSWORD=secret \
  -v taskapi-data:/var/lib/postgresql/data \
  postgres:16-alpine

sleep 3

# Create data
docker exec db psql -U postgres -c "CREATE TABLE tasks (id serial, title text, done boolean);"
docker exec db psql -U postgres -c "INSERT INTO tasks (title, done) VALUES ('Learn volumes', true);"

# Destroy the container
docker stop db && docker rm db

# Run a NEW container with the SAME volume
docker run -d --name db \
  -e POSTGRES_PASSWORD=secret \
  -v taskapi-data:/var/lib/postgresql/data \
  postgres:16-alpine

sleep 3

# Data survives!
docker exec db psql -U postgres -c "SELECT * FROM tasks;"
# Output: 1 | Learn volumes | t

docker stop db && docker rm db
```

### Lab 3.3: Bind Mounts (Live Code Reload)

```bash
cd ~/docker-labs/taskapi

# Mount your local code INTO the container
docker run -d --name taskapi-dev \
  -p 8000:8000 \
  -v $(pwd):/app \
  python:3.11-slim \
  python /app/app.py

# Test it
curl http://localhost:8000

# Now edit app.py on your HOST machine (add a new task)
# Restart the container to pick up changes:
docker restart taskapi-dev

# Or use a framework with auto-reload (Flask, FastAPI with --reload)

docker stop taskapi-dev && docker rm taskapi-dev
```

---

## Episode 04: Networking

### Lab 4.1: Port Mapping

```bash
# Container port 80 → Host port 9090
docker run -d --name web -p 9090:80 nginx:alpine

curl http://localhost:9090
# You get the nginx welcome page

# Multiple ports
docker run -d --name multi -p 8080:80 -p 8443:443 nginx:alpine

docker stop web multi && docker rm web multi
```

### Lab 4.2: Container-to-Container Communication

```bash
# Create a network
docker network create tasknet

# Run postgres on the network
docker run -d --name db \
  --network tasknet \
  -e POSTGRES_PASSWORD=secret \
  postgres:16-alpine

# Run another container on the same network — it can reach "db" by name
docker run --rm --network tasknet postgres:16-alpine \
  psql -h db -U postgres -c "SELECT 1 as connected;"
# Output: 1 (it connected using the container name as hostname!)

# Containers on different networks CANNOT talk to each other
docker run --rm postgres:16-alpine \
  psql -h db -U postgres -c "SELECT 1;"
# This FAILS — not on the same network

docker stop db && docker rm db
docker network rm tasknet
```

### Lab 4.3: TaskAPI + Database

Create `app_db.py`:

```python
import psycopg2
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import time

def get_connection():
    for attempt in range(10):
        try:
            return psycopg2.connect(
                host=os.environ.get("DB_HOST", "db"),
                dbname=os.environ.get("DB_NAME", "postgres"),
                user=os.environ.get("DB_USER", "postgres"),
                password=os.environ.get("DB_PASS", "secret"),
            )
        except psycopg2.OperationalError:
            print(f"Waiting for database (attempt {attempt + 1})...")
            time.sleep(2)
    raise Exception("Could not connect to database")

conn = get_connection()
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS tasks (id serial PRIMARY KEY, title text, done boolean DEFAULT false)")
conn.commit()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        cur.execute("SELECT id, title, done FROM tasks")
        tasks = [{"id": r[0], "title": r[1], "done": r[2]} for r in cur.fetchall()]
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(tasks).encode())

print("TaskAPI (with DB) running on port 8000")
HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
```

Update `requirements.txt`:

```
psycopg2-binary==2.9.9
```

Update `Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app_db.py ./app.py
EXPOSE 8000
CMD ["python", "app.py"]
```

Run both containers on the same network:

```bash
docker build -t taskapi:v3 .

docker network create tasknet

docker run -d --name db \
  --network tasknet \
  -e POSTGRES_PASSWORD=secret \
  -v taskapi-data:/var/lib/postgresql/data \
  postgres:16-alpine

docker run -d --name taskapi \
  --network tasknet \
  -p 8000:8000 \
  -e DB_HOST=db \
  -e DB_PASS=secret \
  taskapi:v3

# Test
curl http://localhost:8000
# [] (empty — no tasks yet, but it's connected to the DB!)

# Clean up
docker stop taskapi db && docker rm taskapi db
docker network rm tasknet
```

---

## Episode 05: Docker Compose

### Lab 5.1: Replace All Those Commands with One File

Create `docker-compose.yml`:

```yaml
version: "3.9"

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: secret
    volumes:
      - taskapi-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DB_HOST: db
      DB_PASS: secret
    depends_on:
      db:
        condition: service_healthy

volumes:
  taskapi-data:
```

```bash
# Start everything with ONE command
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f api

# Test
curl http://localhost:8000

# Stop everything
docker compose down

# Stop AND delete volumes (fresh start)
docker compose down -v
```

### Lab 5.2: Add a Frontend

Create `frontend/index.html`:

```html
<!DOCTYPE html>
<html>
<head><title>TaskAPI</title></head>
<body>
  <h1>Tasks</h1>
  <div id="tasks">Loading...</div>
  <script>
    fetch('/api/')
      .then(r => r.json())
      .then(tasks => {
        document.getElementById('tasks').innerHTML =
          tasks.map(t => `<p>${t.done ? '✅' : '⬜'} ${t.title}</p>`).join('');
      });
  </script>
</body>
</html>
```

Create `frontend/nginx.conf`:

```nginx
server {
    listen 80;
    location / {
        root /usr/share/nginx/html;
        index index.html;
    }
    location /api/ {
        proxy_pass http://api:8000/;
    }
}
```

Update `docker-compose.yml` — add the frontend service:

```yaml
  frontend:
    image: nginx:alpine
    ports:
      - "3000:80"
    volumes:
      - ./frontend/index.html:/usr/share/nginx/html/index.html
      - ./frontend/nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - api
```

```bash
docker compose up -d
# Visit http://localhost:3000 — full stack app!
```

### Lab 5.3: Development vs Production Compose

Create `docker-compose.override.yml` (auto-loaded in dev):

```yaml
version: "3.9"

services:
  api:
    volumes:
      - .:/app  # live code reload in dev
    environment:
      DEBUG: "true"
```

```bash
# Dev (uses override automatically)
docker compose up -d

# Production (explicit file, no override)
docker compose -f docker-compose.yml up -d
```

---

## Episode 06: Multi-Stage Builds

### Lab 6.1: The Fat Image Problem

```bash
# Check your current image size
docker images taskapi
# Probably 200-400MB (full Python + pip + build tools)
```

### Lab 6.2: Multi-Stage Dockerfile

Create `Dockerfile.multistage`:

```dockerfile
# ── Stage 1: Build ──────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/app/deps -r requirements.txt

# ── Stage 2: Runtime ────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Copy ONLY the installed packages (not pip, not build tools)
COPY --from=builder /app/deps /app/deps
ENV PYTHONPATH=/app/deps

COPY app_db.py ./app.py

EXPOSE 8000
CMD ["python", "app.py"]
```

```bash
# Build with multi-stage
docker build -f Dockerfile.multistage -t taskapi:slim .

# Compare sizes
docker images | grep taskapi
# taskapi:v3    ~350MB
# taskapi:slim  ~150MB (or less)
```

### Lab 6.3: Go App (Extreme Multi-Stage)

Create `hello.go`:

```go
package main

import (
    "fmt"
    "net/http"
)

func main() {
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "Hello from Go in Docker!")
    })
    fmt.Println("Listening on :8080")
    http.ListenAndServe(":8080", nil)
}
```

Create `Dockerfile.go`:

```dockerfile
# Build stage: full Go SDK (1GB+)
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY hello.go .
RUN go build -o server hello.go

# Runtime stage: just the binary (< 15MB!)
FROM alpine:3.19
COPY --from=builder /app/server /server
EXPOSE 8080
CMD ["/server"]
```

```bash
docker build -f Dockerfile.go -t hello-go .
docker images hello-go
# ~15MB total! (vs 1GB+ if you used the full Go image)

docker run --rm -p 8080:8080 hello-go
curl http://localhost:8080
```

---

## Episode 07: Docker Hub & Registry

### Lab 7.1: Push to Docker Hub

```bash
# Login
docker login

# Tag your image (replace YOUR_USERNAME)
docker tag taskapi:slim YOUR_USERNAME/taskapi:latest
docker tag taskapi:slim YOUR_USERNAME/taskapi:v1.0

# Push
docker push YOUR_USERNAME/taskapi:latest
docker push YOUR_USERNAME/taskapi:v1.0

# Now anyone can pull it:
# docker pull YOUR_USERNAME/taskapi:latest
```

### Lab 7.2: Tagging Strategy

```bash
# Semantic versioning
docker tag taskapi:slim YOUR_USERNAME/taskapi:1.0.0
docker tag taskapi:slim YOUR_USERNAME/taskapi:1.0
docker tag taskapi:slim YOUR_USERNAME/taskapi:1
docker tag taskapi:slim YOUR_USERNAME/taskapi:latest

# Git SHA tags (for CI/CD)
GIT_SHA=$(git rev-parse --short HEAD)
docker tag taskapi:slim YOUR_USERNAME/taskapi:$GIT_SHA
```

### Lab 7.3: Local Registry (No Docker Hub Needed)

```bash
# Run a private registry locally
docker run -d -p 5000:5000 --name registry registry:2

# Tag and push to local registry
docker tag taskapi:slim localhost:5000/taskapi:latest
docker push localhost:5000/taskapi:latest

# Pull from local registry (simulates another machine)
docker rmi localhost:5000/taskapi:latest
docker pull localhost:5000/taskapi:latest

docker stop registry && docker rm registry
```

---

## Episode 08: Health Checks & Logs

### Lab 8.1: Add a Health Check

Update `Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app_db.py ./app.py
EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000')" || exit 1

CMD ["python", "app.py"]
```

```bash
docker compose up -d

# Watch health status
docker ps
# STATUS: Up 5s (health: starting)
# ... wait 30 seconds ...
# STATUS: Up 35s (healthy)

# If the app crashes, Docker knows:
docker inspect --format='{{.State.Health.Status}}' taskapi-api-1
```

### Lab 8.2: Structured Logging

Update your app to output JSON logs:

```python
import json, sys

def log(level, message, **kwargs):
    entry = {"level": level, "message": message, **kwargs}
    print(json.dumps(entry), file=sys.stdout, flush=True)

log("info", "Server starting", port=8000)
```

```bash
# View logs
docker compose logs api

# Follow logs in real-time
docker compose logs -f api

# Filter with jq (if logs are JSON)
docker compose logs api --no-log-prefix | jq '.message'
```

### Lab 8.3: Restart Policies

Update `docker-compose.yml`:

```yaml
services:
  api:
    # ...
    restart: unless-stopped
    # Options: no, always, on-failure, unless-stopped
```

```bash
# Simulate a crash
docker exec taskapi-api-1 kill 1

# Watch it restart automatically
docker compose ps
# STATUS: Restarting (0) 2 seconds ago
# ... then ...
# STATUS: Up 3 seconds (healthy)
```

---

## Episode 09: Docker in Production

### Lab 9.1: Resource Limits

```yaml
services:
  api:
    # ...
    deploy:
      resources:
        limits:
          cpus: "0.5"      # max 50% of one CPU
          memory: 256M     # max 256MB RAM
        reservations:
          cpus: "0.25"
          memory: 128M
```

```bash
docker compose up -d

# Check resource usage
docker stats
```

### Lab 9.2: Scaling

```bash
# Run 3 instances of the API
docker compose up -d --scale api=3

# Check — 3 containers running
docker compose ps

# Note: you'll need to remove the fixed port mapping (8000:8000)
# and use a load balancer (nginx) in front
```

### Lab 9.3: The Full Production Stack

Final `docker-compose.prod.yml`:

```yaml
version: "3.9"

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    volumes:
      - pgdata:/var/lib/postgresql/data
    secrets:
      - db_password
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M

  api:
    build:
      context: .
      dockerfile: Dockerfile.multistage
    environment:
      DB_HOST: db
      DB_PASS_FILE: /run/secrets/db_password
    secrets:
      - db_password
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000')"]
      interval: 10s
      timeout: 3s
      retries: 3
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 256M

  frontend:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./frontend/index.html:/usr/share/nginx/html/index.html
      - ./frontend/nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - api
    restart: unless-stopped

volumes:
  pgdata:

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

```bash
# Create secrets
mkdir -p secrets
echo "super-secret-password-123" > secrets/db_password.txt

# Run production stack
docker compose -f docker-compose.prod.yml up -d

# Verify everything is healthy
docker compose -f docker-compose.prod.yml ps

# View resource usage
docker stats --no-stream
```

---

## Final Challenge: Deploy TaskAPI End-to-End

Combine everything you've learned. Starting from scratch:

1. ☐ Write the app (`app.py` with database connection)
2. ☐ Write the Dockerfile (multi-stage, health check)
3. ☐ Write `docker-compose.yml` (api + db + frontend)
4. ☐ Add volumes for database persistence
5. ☐ Add a custom network
6. ☐ Add health checks for both api and db
7. ☐ Add restart policies
8. ☐ Add resource limits
9. ☐ Push the image to Docker Hub (or local registry)
10. ☐ Run `docker compose up -d` and verify everything works
11. ☐ Kill the database container — verify it restarts and data persists
12. ☐ Scale the API to 3 instances

**Time target:**
- Under 30 minutes: Docker pro
- Under 60 minutes: Solid practitioner
- Finished at all: You know Docker better than most developers

---

## Quick Reference

```bash
# Images
docker build -t name:tag .
docker images
docker rmi image_name
docker pull image:tag
docker push image:tag

# Containers
docker run -d --name X -p host:container image
docker ps                    # running
docker ps -a                 # all (including stopped)
docker stop X
docker rm X
docker logs X
docker exec -it X bash

# Volumes
docker volume create name
docker volume ls
docker volume rm name

# Networks
docker network create name
docker network ls
docker network rm name

# Compose
docker compose up -d
docker compose down
docker compose ps
docker compose logs -f
docker compose build
docker compose down -v       # remove volumes too

# Cleanup
docker system prune          # remove unused stuff
docker system prune -a       # remove EVERYTHING unused
```

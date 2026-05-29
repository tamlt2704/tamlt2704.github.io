# Chapter 7: Production Best Practices

[← Registries](./chapter-06-registry.md) | [Next: Real Projects →](./chapter-08-projects.md)

---

## Health Checks

Health checks let Docker (and orchestrators) know if your app is actually working.

### In Dockerfile

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY . .
RUN npm ci --only=production

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

CMD ["node", "server.js"]
```

### In Docker Compose

```yaml
services:
  api:
    build: .
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

### Check health status

```bash
docker inspect --format='{{.State.Health.Status}}' my-container
docker ps  # Shows health status in STATUS column
```

## Resource Limits

Prevent containers from consuming all host resources.

```bash
# Limit memory and CPU
docker run -d \
  --memory=512m \
  --cpus=1.5 \
  --name api \
  my-app

# Memory with swap limit
docker run -d \
  --memory=512m \
  --memory-swap=1g \
  my-app
```

### In Docker Compose

```yaml
services:
  api:
    build: .
    deploy:
      resources:
        limits:
          cpus: "1.5"
          memory: 512M
        reservations:
          cpus: "0.5"
          memory: 256M
```

## Logging

### View logs

```bash
# Default logging
docker logs my-container

# Follow with timestamps
docker logs -f --timestamps my-container

# Last 100 lines
docker logs --tail 100 my-container
```

### Configure logging driver

```bash
# Use json-file with rotation
docker run -d \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  my-app
```

### In Docker Compose

```yaml
services:
  api:
    build: .
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

## Security

### Run as non-root user

```dockerfile
FROM node:20-alpine

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app
COPY --chown=appuser:appgroup . .
RUN npm ci --only=production

USER appuser
EXPOSE 3000
CMD ["node", "server.js"]
```

### Read-only filesystem

```bash
docker run -d \
  --read-only \
  --tmpfs /tmp \
  --tmpfs /app/cache \
  my-app
```

```yaml
# In Compose
services:
  api:
    build: .
    read_only: true
    tmpfs:
      - /tmp
      - /app/cache
```

### Docker secrets (Compose)

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

### Security scanning with Docker Scout

```bash
# Analyze image for vulnerabilities
docker scout cves my-app:1.0

# Quick overview
docker scout quickview my-app:1.0

# Recommendations
docker scout recommendations my-app:1.0
```

### Additional security practices

```bash
# Drop all capabilities, add only what's needed
docker run -d \
  --cap-drop ALL \
  --cap-add NET_BIND_SERVICE \
  my-app

# No new privileges
docker run -d \
  --security-opt no-new-privileges \
  my-app
```

## Slim Images

Smaller images mean faster pulls, less attack surface, and lower storage costs.

### Image size comparison

| Base image                 | Size   |
| -------------------------- | ------ |
| ubuntu:22.04               | ~77MB  |
| node:20                    | ~1.1GB |
| node:20-slim               | ~200MB |
| node:20-alpine             | ~130MB |
| gcr.io/distroless/nodejs20 | ~130MB |
| scratch                    | 0MB    |

### Alpine-based images

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production
COPY . .
CMD ["node", "server.js"]
```

### Distroless images

Distroless images contain only your app and its runtime — no shell, no package manager.

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production
COPY . .

FROM gcr.io/distroless/nodejs20-debian12
WORKDIR /app
COPY --from=builder /app .
CMD ["server.js"]
```

### Scratch (for static binaries)

```dockerfile
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 go build -o server .

FROM scratch
COPY --from=builder /app/server /server
EXPOSE 8080
CMD ["/server"]
```

## Production Checklist

- Use specific image tags (never `latest` in production)
- Run as non-root user
- Set resource limits (memory and CPU)
- Add health checks
- Configure log rotation
- Use read-only filesystem where possible
- Scan images for vulnerabilities
- Use multi-stage builds for smaller images
- Set restart policies (`unless-stopped` or `always`)
- Use secrets management (not env vars for sensitive data)

## Exercises

1. Add a health check to a Node.js Dockerfile and verify it works with `docker inspect`
2. Run a container with memory and CPU limits, then stress-test it
3. Create a Dockerfile that runs as a non-root user and verify with `docker exec whoami`
4. Run a container with `--read-only` and verify writes fail except to tmpfs mounts
5. Compare image sizes: build the same app with `node:20`, `node:20-alpine`, and distroless

---

[← Registries](./chapter-06-registry.md) | [Next: Real Projects →](./chapter-08-projects.md)

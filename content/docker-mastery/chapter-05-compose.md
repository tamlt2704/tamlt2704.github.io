# Chapter 5: Docker Compose

[← Networking](./chapter-04-networking.md) | [Next: Registries →](./chapter-06-registry.md)

---

## What is Docker Compose?

Docker Compose defines and runs multi-container applications using a single YAML file. Instead of running multiple `docker run` commands, you declare your entire stack in `docker-compose.yml`.

## Basic Structure

```yaml
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    depends_on:
      - db
      - redis

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secret
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

volumes:
  pgdata:
```

## Key Compose Commands

```bash
# Start all services (detached)
docker compose up -d

# Start and rebuild images
docker compose up -d --build

# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v

# View logs
docker compose logs

# Follow logs for a specific service
docker compose logs -f app

# List running services
docker compose ps

# Execute a command in a running service
docker compose exec app sh

# Scale a service
docker compose up -d --scale worker=3
```

## Services Configuration

### Build from Dockerfile

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.prod
      args:
        NODE_ENV: production
```

### Environment variables

```yaml
services:
  app:
    environment:
      - DATABASE_URL=postgres://admin:secret@db:5432/myapp
      - REDIS_URL=redis://redis:6379
    # Or from a file
    env_file:
      - .env
```

### Volumes

```yaml
services:
  app:
    volumes:
      - ./src:/app/src # bind mount for development
      - node_modules:/app/node_modules # named volume

volumes:
  node_modules:
```

### Networks

```yaml
services:
  app:
    networks:
      - frontend
      - backend
  db:
    networks:
      - backend

networks:
  frontend:
  backend:
```

### depends_on with health checks

```yaml
services:
  app:
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin"]
      interval: 5s
      timeout: 5s
      retries: 5
```

### Restart policies

```yaml
services:
  app:
    restart: unless-stopped
    # Options: no, always, on-failure, unless-stopped
```

## Multi-Container App Example

A full-stack application with Node.js API, PostgreSQL, and Redis:

```yaml
services:
  api:
    build: ./api
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgres://admin:secret@db:5432/myapp
      REDIS_URL: redis://cache:6379
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
    volumes:
      - ./api/src:/app/src

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secret
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin"]
      interval: 5s
      timeout: 5s
      retries: 5

  cache:
    image: redis:7-alpine

  adminer:
    image: adminer
    ports:
      - "8080:8080"

volumes:
  pgdata:
```

## Profiles

Profiles let you selectively start services.

```yaml
services:
  app:
    build: .
    ports:
      - "3000:3000"

  db:
    image: postgres:16

  adminer:
    image: adminer
    ports:
      - "8080:8080"
    profiles:
      - debug

  prometheus:
    image: prom/prometheus
    profiles:
      - monitoring
```

```bash
# Start only core services (no profiles)
docker compose up -d

# Start with debug tools
docker compose --profile debug up -d

# Start with multiple profiles
docker compose --profile debug --profile monitoring up -d
```

## Override Files

**docker-compose.yml** (base):

```yaml
services:
  app:
    build: .
    ports:
      - "3000:3000"
```

**docker-compose.override.yml** (auto-loaded in dev):

```yaml
services:
  app:
    volumes:
      - ./src:/app/src
    environment:
      - DEBUG=true
```

```bash
# Development (auto-loads override)
docker compose up -d

# Production (explicit file)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Exercises

1. Create a `docker-compose.yml` with nginx and a custom HTML page served via bind mount
2. Build a three-service stack (Node.js app + PostgreSQL + Redis) and verify they communicate
3. Add a health check to PostgreSQL and make the app wait with `depends_on` conditions
4. Use profiles to add an optional Adminer service for database management
5. Create a base compose file and an override file for development with bind mounts

---

[← Networking](./chapter-04-networking.md) | [Next: Registries →](./chapter-06-registry.md)

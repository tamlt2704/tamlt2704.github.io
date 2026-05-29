# Chapter 8: Real Projects

[← Production](./chapter-07-production.md) | [Overview](./chapter-00-overview.md)

---

## Project 1: Dockerize a Spring Boot App

### Dockerfile

```dockerfile
FROM eclipse-temurin:21-jdk-alpine AS builder
WORKDIR /app
COPY gradle/ gradle/
COPY gradlew build.gradle.kts settings.gradle.kts ./
RUN ./gradlew dependencies --no-daemon
COPY src/ src/
RUN ./gradlew bootJar --no-daemon

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
RUN addgroup -S spring && adduser -S spring -G spring
COPY --from=builder /app/build/libs/*.jar app.jar
USER spring
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/actuator/health || exit 1
CMD ["java", "-jar", "app.jar"]
```

### .dockerignore

```
.gradle
build
.idea
*.iml
.git
```

### Build and run

```bash
docker build -t spring-app:1.0 .
docker run -d -p 8080:8080 --name spring-app spring-app:1.0
curl http://localhost:8080/actuator/health
```

---

## Project 2: Dockerize a Next.js App

### Dockerfile

```dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

RUN addgroup -S nextjs && adduser -S nextjs -G nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nextjs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nextjs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

HEALTHCHECK --interval=30s --timeout=5s \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

CMD ["node", "server.js"]
```

### next.config.js requirement

```javascript
// next.config.js — enable standalone output
const nextConfig = {
  output: "standalone",
};
module.exports = nextConfig;
```

### .dockerignore

```
node_modules
.next
.git
*.md
```

### Build and run

```bash
docker build -t nextjs-app:1.0 .
docker run -d -p 3000:3000 --name nextjs-app nextjs-app:1.0
curl http://localhost:3000
```

---

## Project 3: Full-Stack Compose

A complete stack with React frontend, Node.js backend, PostgreSQL, and Redis.

### Directory structure

```
project/
  frontend/
    Dockerfile
    src/
    package.json
  backend/
    Dockerfile
    src/
    package.json
  docker-compose.yml
  .env
```

### backend/Dockerfile

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production
COPY . .
USER node
EXPOSE 4000
CMD ["node", "src/index.js"]
```

### frontend/Dockerfile

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

### docker-compose.yml

```yaml
services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "4000:4000"
    environment:
      DATABASE_URL: postgres://admin:secret@db:5432/myapp
      REDIS_URL: redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secret
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data

volumes:
  pgdata:
  redis-data:
```

### Run the full stack

```bash
# Start everything
docker compose up -d --build

# Check status
docker compose ps

# View backend logs
docker compose logs -f backend

# Stop everything
docker compose down

# Stop and remove all data
docker compose down -v
```

---

## Project 4: CI/CD with GitHub Actions

### .github/workflows/docker.yml

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: github.repository

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GHCR
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: github.actor
          password: secrets.GITHUB_TOKEN

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/github.repository
          tags: |
            type=sha
            type=ref,event=branch
            type=semver,pattern=vversion

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: github.event_name != 'pull_request'
          tags: steps.meta.outputs.tags
          labels: steps.meta.outputs.labels
          cache-from: type=gha
          cache-to: type=gha,mode=max

  test:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - uses: actions/checkout@v4

      - name: Run tests with Compose
        run: |
          docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
          docker compose -f docker-compose.test.yml down -v
```

### docker-compose.test.yml

```yaml
services:
  test:
    build:
      context: .
      dockerfile: Dockerfile
    command: npm test
    environment:
      DATABASE_URL: postgres://admin:secret@db:5432/testdb
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: testdb
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secret
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin"]
      interval: 2s
      timeout: 5s
      retries: 5
```

---

## Exercises

1. Dockerize a Spring Boot application with a multi-stage build and verify the health endpoint works
2. Dockerize a Next.js app using standalone output and multi-stage build — compare the final image size to a naive single-stage build
3. Create a full-stack docker-compose.yml with frontend, backend, PostgreSQL, and Redis — verify all services communicate
4. Set up a GitHub Actions workflow that builds and pushes your image to GHCR on every push to main
5. Create a `docker-compose.test.yml` that runs your test suite against a real database in CI

---

[← Production](./chapter-07-production.md) | [Overview](./chapter-00-overview.md)

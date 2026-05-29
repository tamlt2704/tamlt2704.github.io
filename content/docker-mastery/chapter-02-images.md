# Chapter 2: Docker Images

[← Basics](./chapter-01-basics.md) | [Next: Volumes →](./chapter-03-volumes.md)

---

## What is a Docker Image?

An image is a read-only template containing your application code, runtime, libraries, and configuration. Containers are running instances of images.

## Dockerfile Instructions

A `Dockerfile` is a text file with instructions to build an image.

### FROM — Base image

```dockerfile
FROM node:20-alpine
```

Every Dockerfile starts with FROM. Use specific tags (not `latest`) for reproducibility.

### WORKDIR — Set working directory

```dockerfile
WORKDIR /app
```

All subsequent commands run from this directory. Creates it if it doesn't exist.

### COPY — Copy files into the image

```dockerfile
COPY package.json package-lock.json ./
COPY src/ ./src/
```

### RUN — Execute commands during build

```dockerfile
RUN npm ci --only=production
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
```

Each RUN creates a new layer. Combine commands with `&&` to reduce layers.

### ENV — Set environment variables

```dockerfile
ENV NODE_ENV=production
ENV PORT=3000
```

### EXPOSE — Document the port

```dockerfile
EXPOSE 3000
```

This is documentation only — you still need `-p` when running the container.

### CMD — Default command when container starts

```dockerfile
CMD ["node", "server.js"]
```

Use exec form (JSON array) over shell form for proper signal handling.

## Complete Dockerfile Example

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production
COPY . .
ENV NODE_ENV=production
EXPOSE 3000
CMD ["node", "server.js"]
```

## Building Images

```bash
# Build with a tag
docker build -t my-app:1.0 .

# Build with a specific Dockerfile
docker build -f Dockerfile.prod -t my-app:prod .

# Build with build arguments
docker build --build-arg VERSION=1.0 -t my-app .
```

## .dockerignore

Create a `.dockerignore` file to exclude files from the build context:

```
node_modules
.git
.env
*.log
dist
.next
coverage
```

This speeds up builds and prevents sensitive files from entering the image.

## Layer Caching

Docker caches each layer. If a layer hasn't changed, Docker reuses the cache.

**Bad — cache busts on every code change:**

```dockerfile
COPY . .
RUN npm ci
```

**Good — dependencies cached separately:**

```dockerfile
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
```

Since `package.json` changes less often than source code, the `npm ci` layer stays cached.

### Cache tips

- Order instructions from least-changing to most-changing
- Separate dependency installation from code copying
- Use `--no-cache` to force a fresh build: `docker build --no-cache -t my-app .`

## Multi-Stage Builds

Multi-stage builds produce smaller final images by separating build and runtime environments.

### Node.js example

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production
FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
ENV NODE_ENV=production
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

### Go example

```dockerfile
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o server .

FROM scratch
COPY --from=builder /app/server /server
EXPOSE 8080
CMD ["/server"]
```

The final Go image contains only the binary — no OS, no shell, just a few MBs.

## Inspecting Images

```bash
# View image layers and sizes
docker history my-app:1.0

# Inspect image metadata
docker inspect my-app:1.0

# Check image size
docker images my-app
```

## Exercises

1. Write a Dockerfile for a simple Python Flask app and build it
2. Create a `.dockerignore` that excludes `__pycache__`, `.git`, and `.env`
3. Build twice — change only source code and observe which layers are cached
4. Convert a single-stage Node.js Dockerfile into a multi-stage build and compare image sizes
5. Build the same app with `node:20` vs `node:20-alpine` and compare sizes

---

[← Basics](./chapter-01-basics.md) | [Next: Volumes →](./chapter-03-volumes.md)

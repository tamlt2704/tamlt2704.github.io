# Chapter 12: Ship It — Production Build & Deploy

[← Chapter 11: GraphQL](chapter-11-graphql.md)

---

## The Problem

The dashboard runs on `localhost:5173`. Captain Deadline wants it on a real URL. "I want to open it from home. On my phone. At 3 AM. Because I will."

## What You'll Build

- **Production build** — `npm run build`, analyze the output, optimize bundle size
- **Environment config** — `.env.production` for API URL, feature flags
- **Docker** — multi-stage Dockerfile: build with Node, serve with Nginx
- **Docker Compose** — frontend + backend + Postgres + Redis in one `docker compose up`
- **CI/CD** — GitHub Actions: lint → test → build → deploy on every push
- **E2E tests** — Playwright tests that run against the real backend in CI

## Key Concepts

- **Static build** — React compiles to HTML/CSS/JS files, served by any web server
- **Nginx** — serve static files, proxy `/api` to the backend, gzip compression
- **Multi-stage Docker** — small final image (~25MB) with just Nginx + built files
- **Environment variables** — `VITE_API_URL` baked in at build time
- **Cache busting** — Vite adds content hashes to filenames automatically
- **Health checks** — Docker health check on the Nginx container
- **CI pipeline** — lint → type-check → unit test → build → e2e test → deploy

```dockerfile
# Dockerfile
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

```yaml
# docker-compose.yml — the full stack
services:
  frontend:
    build: ./frontend
    ports: ["3000:80"]
  backend:
    build: ./backend
    ports: ["8080:8080"]
  postgres:
    image: postgres:16
  redis:
    image: redis:7
```

`docker compose up` — the entire ShopZilla Job Engine, frontend and backend, in one command.

Captain Deadline opens it from home. On his phone. At 3 AM. He's satisfied.

---

[← Chapter 11: GraphQL](chapter-11-graphql.md) | [Back to README](./README.md)

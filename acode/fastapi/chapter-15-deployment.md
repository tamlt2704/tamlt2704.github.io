# Chapter 15: Deployment — Docker & Production

[← Chapter 14: Middleware](chapter-14-middleware.md)

---

## The Task

Nia: "Containerize it. Health check. Production ASGI server. Environment variables for secrets. I want `docker compose up` and everything works."

---

## Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run with production server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

---

## Docker Compose

```yaml
# docker-compose.yml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:pulseboard@db:5432/pulseboard
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: pulseboard
      POSTGRES_PASSWORD: pulseboard
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  pgdata:
```

```bash
docker compose up --build
```

---

## Production Configuration

```python
# app/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    environment: str = "development"
    allowed_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env"}


settings = Settings()
```

```bash
# .env (never commit this)
DATABASE_URL=postgresql+asyncpg://postgres:pulseboard@localhost:5432/pulseboard
SECRET_KEY=change-this-to-a-random-string
ENVIRONMENT=production
ALLOWED_ORIGINS=["https://pulseboard.app"]
```

---

## Health Check Endpoint

```python
@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "disconnected"},
        )
```

---

## Production Checklist

```
✅ Dockerfile with multi-stage build
✅ docker-compose.yml with health checks
✅ Environment variables for all secrets
✅ CORS configured for production domains
✅ Rate limiting on auth endpoints
✅ Security headers middleware
✅ Health check endpoint
✅ Structured logging (JSON)
✅ Database migrations run on startup
✅ No DEBUG mode in production
✅ Tests pass in CI
```

---

## The Architecture (Final)

```
┌─────────────────────────────────────────────────────────────┐
│                      PulseBoard API                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  FastAPI App (uvicorn, 4 workers)                           │
│  ├── /auth (register, login, JWT)                           │
│  ├── /projects (CRUD, pagination, filtering)                │
│  ├── /tasks (CRUD, assignment, status updates)              │
│  ├── /upload (file attachments)                             │
│  ├── /ws/projects/{id} (real-time updates)                  │
│  └── /health (monitoring)                                   │
│                                                              │
│  Middleware Stack:                                           │
│  ├── CORS                                                   │
│  ├── Rate Limiting                                          │
│  ├── Request Logging                                        │
│  └── Security Headers                                       │
│                                                              │
│  Dependencies:                                               │
│  ├── get_db (async session)                                 │
│  ├── get_current_user (JWT validation)                      │
│  └── Pydantic (validation on every request)                 │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL (async via asyncpg)                              │
│  Alembic (migrations)                                       │
│  Redis (rate limiting, Celery broker)                        │
└─────────────────────────────────────────────────────────────┘
```

---

## What You Built (The Full Journey)

| Chapter | What You Learned |
|---|---|
| 1 | Routes, methods, uvicorn, auto-docs |
| 2 | Pydantic models, validation, serialization |
| 3 | Path/query/body params, enums, constraints |
| 4 | Full CRUD pattern, status codes, routers |
| 5 | SQLAlchemy async, sessions, Alembic migrations |
| 6 | JWT auth, OAuth2, dependency injection |
| 7 | Relationships, eager loading, nested responses |
| 8 | Pagination, filtering, sorting, search |
| 9 | File uploads, validation, static serving |
| 10 | Custom exceptions, global handlers, consistent errors |
| 11 | Background tasks, Celery, async notifications |
| 12 | WebSockets, connection management, broadcasting |
| 13 | TestClient, fixtures, async testing |
| 14 | CORS, middleware, rate limiting, security headers |
| 15 | Docker, compose, env vars, production config |

---

## Friday Demo

Dani opens `/docs`. Every endpoint is documented. She clicks "Authorize," logs in, and tests the full flow from the browser.

Marcus generates a TypeScript client from `/openapi.json` in 10 seconds. Type-safe frontend calls. No more guessing.

Nia runs `docker compose up`. Everything starts. Health check passes. She pushes to production.

The Old Flask App is retired. No one mourns it.

You close your laptop. Two weeks. One framework. Production-ready.

---

[← Chapter 14: Middleware](chapter-14-middleware.md)

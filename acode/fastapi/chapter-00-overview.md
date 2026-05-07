# FastAPI Mastery: A Backend Survival Story

You just joined **PulseBoard** — a startup building a real-time project management tool. Think Linear meets Notion. Teams create projects, track tasks, assign members, and get live updates.

Day one, the CTO — **Dani** — pulls you into a standup.

> "Our backend is a Flask app held together with duct tape. No type safety. No docs. No validation. The frontend team guesses what the API returns. Every deploy breaks something. We're rewriting it in FastAPI. You're leading it."

She slides a napkin across the table with the API surface scrawled on it:

> Users. Projects. Tasks. Comments. Real-time notifications. Auth. File uploads. Background jobs. Go.

You open your terminal. The cursor blinks.

---

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Backend Engineer | "I know Python. How different can FastAPI be?" |
| **Dani** | CTO | Draws system diagrams on napkins. Hates untyped code. |
| **Marcus** | Frontend Lead | "Give me OpenAPI docs or give me death." |
| **Nia** | DevOps | Runs everything in Docker. Speaks in YAML. |
| **The Old Flask App** | Legacy system | No types. No docs. `return jsonify(stuff)` everywhere. |
| **The 500 Error** | That one bug | Happens every Tuesday. Nobody knows why. |

---

## The Stack

| Tool | What It Does |
|---|---|
| **FastAPI** | Web framework (async, typed, fast) |
| **Pydantic v2** | Data validation & serialization |
| **SQLAlchemy 2.0** | Database ORM (async) |
| **PostgreSQL** | Database |
| **Alembic** | Database migrations |
| **uvicorn** | ASGI server |
| **Docker** | Containerization |

---

## How to Read This

Every chapter follows the same loop:

```
  📋 Marcus needs an endpoint
   │
   ▼
  🤔 You learn the FastAPI concept needed
   │
   ▼
  ⌨️  You build it
   │
   ▼
  💥 Something breaks — validation fails, types are wrong, it's slow
   │
   ▼
  🧠 You understand WHY and fix it
   │
   ▼
  📋 Next endpoint
```

No concept shows up before you need it. You won't hear about dependency injection until you need auth on every route. You won't touch WebSockets until Marcus wants live updates. You won't learn about background tasks until a notification takes 10 seconds to send.

---

## The Roadmap

### Part 1: Foundations — "Make It Work"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Feature                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 01 │ First endpoint, auto-docs              │ Routes, methods, uvicorn, /docs
────┼────────────────────────────────────────┼──────────────────────────────────────
 02 │ Request & response models              │ Pydantic, validation, serialization
────┼────────────────────────────────────────┼──────────────────────────────────────
 03 │ Path params, query params, body        │ Parameter types, defaults, enums
────┼────────────────────────────────────────┼──────────────────────────────────────
 04 │ CRUD for projects                      │ POST, GET, PUT, DELETE, status codes
────┼────────────────────────────────────────┼──────────────────────────────────────
 05 │ Database with SQLAlchemy               │ Models, sessions, async queries
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 2: Real Features — "Make It Useful"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Feature                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 06 │ Authentication (JWT)                   │ OAuth2, dependencies, security
────┼────────────────────────────────────────┼──────────────────────────────────────
 07 │ Relationships & nested data            │ Foreign keys, joins, nested responses
────┼────────────────────────────────────────┼──────────────────────────────────────
 08 │ Pagination, filtering, sorting         │ Query params, dynamic queries
────┼────────────────────────────────────────┼──────────────────────────────────────
 09 │ File uploads                           │ UploadFile, storage, validation
────┼────────────────────────────────────────┼──────────────────────────────────────
 10 │ Error handling & custom exceptions     │ HTTPException, handlers, problem details
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 3: Production — "Make It Fast & Ship It"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Feature                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 11 │ Background tasks & notifications       │ BackgroundTasks, Celery, async
────┼────────────────────────────────────────┼──────────────────────────────────────
 12 │ WebSockets (live updates)              │ Real-time, connection management
────┼────────────────────────────────────────┼──────────────────────────────────────
 13 │ Testing                                │ TestClient, fixtures, mocking DB
────┼────────────────────────────────────────┼──────────────────────────────────────
 14 │ Middleware, CORS, rate limiting        │ Request lifecycle, security headers
────┼────────────────────────────────────────┼──────────────────────────────────────
 15 │ Deployment (Docker + production)       │ Dockerfile, Gunicorn, health checks
────┴────────────────────────────────────────┴──────────────────────────────────────
```

---

## Prerequisites

- **Python 3.11+**
- **A terminal**
- **Docker** (for PostgreSQL)
- **Any code editor** (VS Code with Pylance recommended)

```bash
python --version  # 3.11+
```

---

## Why FastAPI?

Dani explains it on the whiteboard:

```
Flask (old):                    FastAPI (new):
─────────────────               ─────────────────
No type hints                   Full type hints
No auto-validation              Pydantic validation
No auto-docs                    OpenAPI docs free
Sync only                       Async native
Manual serialization            Auto serialization
Runtime errors                  Editor catches bugs
```

Marcus adds: "Flask gives me a JSON blob and I pray the fields exist. FastAPI gives me a typed schema I can generate a TypeScript client from. Automatically."

---

## The API We're Building

```
POST   /auth/register           → create account
POST   /auth/login              → get JWT token

GET    /projects                → list user's projects
POST   /projects                → create project
GET    /projects/{id}           → project detail
PUT    /projects/{id}           → update project
DELETE /projects/{id}           → delete project

GET    /projects/{id}/tasks     → list tasks
POST   /projects/{id}/tasks     → create task
PATCH  /tasks/{id}              → update task (status, assignee)
DELETE /tasks/{id}              → delete task

POST   /tasks/{id}/comments     → add comment
GET    /tasks/{id}/comments     → list comments

POST   /upload                  → upload file
WS     /ws/projects/{id}        → real-time task updates
```

---

[Next: Chapter 1 — Your First Endpoint →](chapter-01-first-endpoint.md)

# Chapter 1: Your First Endpoint — Hello, Auto-Docs

[← Overview](chapter-00-overview.md) | [Chapter 2: Pydantic Models →](chapter-02-pydantic.md)

---

## The Task

Dani: "Prove it works. One endpoint. Auto-generated docs. Show Marcus by lunch."

---

## Setup

```bash
mkdir pulseboard && cd pulseboard
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install fastapi uvicorn[standard]
```

That's it. Two packages. FastAPI for the framework, uvicorn to run it.

---

## Your First App

```python
# main.py
from fastapi import FastAPI

app = FastAPI(
    title="PulseBoard API",
    description="Real-time project management",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "PulseBoard API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}
```

Run it:

```bash
uvicorn main:app --reload
```

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Started reloader process
```

---

## The Magic: Auto-Generated Docs

Open `http://localhost:8000/docs` in your browser.

You see a full interactive API documentation page — Swagger UI. Every endpoint listed. You can click "Try it out" and call the API directly from the browser.

Open `http://localhost:8000/redoc` for an alternative docs view.

Open `http://localhost:8000/openapi.json` for the raw OpenAPI schema — Marcus can use this to auto-generate a TypeScript client.

You wrote zero documentation. FastAPI generated it from your code.

Marcus: "Wait, this is automatic? I can generate types from this?"

You: "Yes."

Marcus: "I love you."

---

## HTTP Methods

```python
@app.get("/projects")
def list_projects():
    return [{"id": 1, "name": "PulseBoard v2"}]


@app.post("/projects")
def create_project():
    return {"id": 2, "name": "New Project"}


@app.put("/projects/{project_id}")
def update_project(project_id: int):
    return {"id": project_id, "name": "Updated"}


@app.delete("/projects/{project_id}")
def delete_project(project_id: int):
    return {"deleted": True}
```

Each decorator maps to an HTTP method. The function name is just for your code — the route and method define the endpoint.

---

## Path Parameters

```python
@app.get("/projects/{project_id}")
def get_project(project_id: int):
    return {"id": project_id, "name": f"Project {project_id}"}
```

`{project_id}` in the path becomes a function parameter. The type hint `int` means FastAPI:
1. Validates it's an integer (returns 422 if not)
2. Converts it from string to int automatically
3. Documents it in the OpenAPI schema

```bash
curl http://localhost:8000/projects/42
# → {"id": 42, "name": "Project 42"}

curl http://localhost:8000/projects/abc
# → {"detail": [{"type": "int_parsing", "msg": "Input should be a valid integer"}]}
```

Free validation. No `try: int(project_id)` boilerplate.

---

## Query Parameters

```python
@app.get("/projects")
def list_projects(skip: int = 0, limit: int = 10, status: str | None = None):
    return {
        "skip": skip,
        "limit": limit,
        "status": status,
        "projects": []
    }
```

Parameters not in the path are automatically query parameters:

```bash
curl "http://localhost:8000/projects?skip=20&limit=5&status=active"
# → {"skip": 20, "limit": 5, "status": "active", "projects": []}

curl "http://localhost:8000/projects"
# → {"skip": 0, "limit": 10, "status": null, "projects": []}  (defaults used)
```

- `skip: int = 0` → optional, defaults to 0
- `limit: int = 10` → optional, defaults to 10
- `status: str | None = None` → optional, can be omitted

---

## Request Body (Preview)

```python
from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None


@app.post("/projects", status_code=201)
def create_project(project: ProjectCreate):
    return {"id": 1, "name": project.name, "description": project.description}
```

```bash
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "PulseBoard v2", "description": "The rewrite"}'
# → {"id": 1, "name": "PulseBoard v2", "description": "The rewrite"}

curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{"description": "Missing name"}'
# → 422: {"detail": [{"loc": ["body", "name"], "msg": "Field required"}]}
```

`name` is required (no default). `description` is optional. FastAPI validates the JSON body against the Pydantic model and returns a clear error if it's wrong.

We'll dive deep into Pydantic in Chapter 2.

---

## Status Codes

```python
from fastapi import status

@app.post("/projects", status_code=status.HTTP_201_CREATED)
def create_project(project: ProjectCreate):
    return {"id": 1, **project.model_dump()}


@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int):
    return None  # 204 = no body
```

---

## Project Structure (What We'll Build)

```
pulseboard/
├── main.py                  ← app entry point
├── app/
│   ├── __init__.py
│   ├── config.py            ← settings, env vars
│   ├── database.py          ← SQLAlchemy setup
│   ├── models/              ← database models
│   │   ├── user.py
│   │   ├── project.py
│   │   └── task.py
│   ├── schemas/             ← Pydantic models (request/response)
│   │   ├── user.py
│   │   ├── project.py
│   │   └── task.py
│   ├── routers/             ← route handlers (controllers)
│   │   ├── auth.py
│   │   ├── projects.py
│   │   └── tasks.py
│   ├── services/            ← business logic
│   ├── dependencies.py      ← shared dependencies (auth, db)
│   └── exceptions.py        ← custom error handlers
├── alembic/                 ← database migrations
├── tests/
├── requirements.txt
└── Dockerfile
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
@app.get("/path")               │ Handle GET requests
@app.post("/path")              │ Handle POST requests
@app.put / @app.patch / @app.delete │ Other HTTP methods
{param} in path                 │ Path parameter (auto-validated)
param: int = 0                  │ Query parameter with default
param: Type (in function body)  │ Request body (Pydantic model)
status_code=201                 │ Set response status code
/docs                           │ Auto-generated Swagger UI
/openapi.json                   │ OpenAPI schema (for codegen)
uvicorn main:app --reload       │ Run with hot-reload
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Marcus: "The response is just a dict. I need to know EXACTLY what fields come back. And I need validation on what goes IN. No more guessing."

Pydantic models. The type system that makes FastAPI powerful.

---

[← Overview](chapter-00-overview.md) | [Chapter 2: Pydantic Models →](chapter-02-pydantic.md)

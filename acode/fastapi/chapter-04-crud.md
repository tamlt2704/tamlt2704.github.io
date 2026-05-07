# Chapter 4: Full CRUD — Projects Endpoint

[← Chapter 3: Parameters](chapter-03-parameters.md) | [Chapter 5: Database →](chapter-05-database.md)

---

## The Task

Dani: "Full CRUD for projects. Create, list, get by ID, update, delete. Proper status codes. Proper error handling. This is the pattern every other resource will follow."

For now we'll use an in-memory list. Chapter 5 adds the real database.

---

## The Router

```python
# app/routers/projects.py
from fastapi import APIRouter, HTTPException, status
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["Projects"])

# In-memory store (replaced with DB in Chapter 5)
projects_db: dict[int, dict] = {}
next_id = 1


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project: ProjectCreate):
    global next_id
    db_project = {
        "id": next_id,
        "name": project.name,
        "description": project.description,
        "color": project.color,
        "created_at": datetime.now(UTC),
        "owner_id": 1,  # hardcoded until auth (Chapter 6)
    }
    projects_db[next_id] = db_project
    next_id += 1
    return db_project


@router.get("/", response_model=list[ProjectResponse])
def list_projects(skip: int = 0, limit: int = 20):
    projects = list(projects_db.values())
    return projects[skip : skip + limit]


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int):
    if project_id not in projects_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    return projects_db[project_id]


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project: ProjectUpdate):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    stored = projects_db[project_id]
    update_data = project.model_dump(exclude_unset=True)  # only fields that were sent
    stored.update(update_data)
    return stored


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    del projects_db[project_id]
```

---

## Register the Router

```python
# main.py
from fastapi import FastAPI
from app.routers import projects

app = FastAPI(title="PulseBoard API")
app.include_router(projects.router)
```

Now all project endpoints are available under `/projects`.

---

## Key Patterns

### Partial Updates with `exclude_unset`

```python
update_data = project.model_dump(exclude_unset=True)
```

If the client sends `{"name": "New Name"}` (no description), only `name` is updated. `description` stays unchanged. Without `exclude_unset`, omitted fields would be set to `None`.

### HTTPException for Errors

```python
from fastapi import HTTPException

raise HTTPException(status_code=404, detail="Project not found")
```

FastAPI catches this and returns:

```json
{ "detail": "Project not found" }
```

With the correct HTTP status code. No try/except in the route — just raise and FastAPI handles the response.

### Status Codes

| Operation | Code | Meaning |
|---|---|---|
| POST (create) | 201 | Created |
| GET (read) | 200 | OK (default) |
| PUT/PATCH (update) | 200 | OK |
| DELETE | 204 | No Content (empty body) |
| Not found | 404 | Resource doesn't exist |
| Validation error | 422 | Bad input (auto from Pydantic) |

---

## Tags & Organization

```python
router = APIRouter(prefix="/projects", tags=["Projects"])
```

`tags=["Projects"]` groups these endpoints in the Swagger docs. Marcus sees a clean, organized API.

---

## Testing with curl

```bash
# Create
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "PulseBoard v2", "description": "The rewrite"}'
# → 201: {"id": 1, "name": "PulseBoard v2", ...}

# List
curl http://localhost:8000/projects
# → 200: [{"id": 1, "name": "PulseBoard v2", ...}]

# Get one
curl http://localhost:8000/projects/1
# → 200: {"id": 1, "name": "PulseBoard v2", ...}

# Update
curl -X PUT http://localhost:8000/projects/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "PulseBoard v3"}'
# → 200: {"id": 1, "name": "PulseBoard v3", ...}

# Delete
curl -X DELETE http://localhost:8000/projects/1
# → 204 (no body)

# Not found
curl http://localhost:8000/projects/999
# → 404: {"detail": "Project 999 not found"}
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Pattern                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
APIRouter(prefix, tags)         │ Group related endpoints
app.include_router(router)      │ Register router with app
HTTPException(status, detail)   │ Return error response
model_dump(exclude_unset=True)  │ Only include fields client sent
response_model=X                │ Filter/validate response
status_code=201                 │ Set success status code
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Dani: "In-memory data dies when the server restarts. Wire it to PostgreSQL. Use SQLAlchemy. Make it async."

---

[← Chapter 3: Parameters](chapter-03-parameters.md) | [Chapter 5: Database →](chapter-05-database.md)

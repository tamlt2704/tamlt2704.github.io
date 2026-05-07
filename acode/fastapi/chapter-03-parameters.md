# Chapter 3: Parameters — Path, Query, Body, Headers

[← Chapter 2: Pydantic](chapter-02-pydantic.md) | [Chapter 4: CRUD →](chapter-04-crud.md)

---

## The Task

Marcus: "I need to filter tasks by status, sort by priority, search by title, and paginate. Some endpoints need a path param AND query params AND a body. Show me how it all fits together."

---

## Path Parameters: Identifying Resources

```python
@app.get("/projects/{project_id}/tasks/{task_id}")
def get_task(project_id: int, task_id: int):
    return {"project_id": project_id, "task_id": task_id}
```

Path params identify WHICH resource. They're always required. Type-validated automatically.

### Path Validation with `Path()`

```python
from fastapi import Path

@app.get("/projects/{project_id}")
def get_project(
    project_id: int = Path(gt=0, description="The project's unique ID")
):
    return {"id": project_id}
```

`gt=0` — must be greater than 0. Negative IDs return 422.

---

## Query Parameters: Filtering & Options

```python
from fastapi import Query
from enum import Enum


class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class SortField(str, Enum):
    created_at = "created_at"
    priority = "priority"
    title = "title"


@app.get("/projects/{project_id}/tasks")
def list_tasks(
    project_id: int,
    status: TaskStatus | None = None,
    assignee_id: int | None = None,
    search: str | None = Query(default=None, min_length=2, max_length=100),
    sort_by: SortField = SortField.created_at,
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    return {
        "project_id": project_id,
        "filters": {"status": status, "assignee_id": assignee_id, "search": search},
        "sort": {"by": sort_by, "order": sort_order},
        "pagination": {"skip": skip, "limit": limit},
    }
```

```bash
curl "http://localhost:8000/projects/1/tasks?status=in_progress&sort_by=priority&limit=5"
```

### Rules

- No default → required query param
- `= None` → optional
- `= value` → optional with default
- `Query(...)` → add validation (min/max, pattern, description)
- Enum type → only allowed values (auto-documented in /docs)

---

## Request Body: Complex Input

```python
from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: int = 3
    assignee_id: int | None = None


@app.post("/projects/{project_id}/tasks", status_code=201)
def create_task(project_id: int, task: TaskCreate):
    return {"project_id": project_id, **task.model_dump()}
```

FastAPI knows: `project_id` is from the path (it's in `{}`), `task` is from the body (it's a Pydantic model).

---

## Combining All Three

```python
@app.put("/projects/{project_id}/tasks/{task_id}")
def update_task(
    project_id: int,                    # path param
    task_id: int,                       # path param
    task: TaskUpdate,                   # request body
    notify: bool = Query(default=True), # query param
):
    # project_id and task_id from URL
    # task from JSON body
    # notify from ?notify=true/false
    return {"updated": task_id, "notified": notify}
```

```bash
curl -X PUT "http://localhost:8000/projects/1/tasks/42?notify=false" \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'
```

---

## Headers

```python
from fastapi import Header

@app.get("/projects")
def list_projects(
    x_request_id: str | None = Header(default=None),
    user_agent: str | None = Header(default=None),
):
    return {"request_id": x_request_id, "user_agent": user_agent}
```

Header names are converted: `X-Request-Id` → `x_request_id` (lowercase, underscores).

---

## Cookies

```python
from fastapi import Cookie

@app.get("/me")
def get_current_user(session_id: str | None = Cookie(default=None)):
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"session": session_id}
```

---

## Multiple Body Parameters

```python
from fastapi import Body

@app.post("/projects/{project_id}/tasks/{task_id}/assign")
def assign_task(
    project_id: int,
    task_id: int,
    assignee_id: int = Body(embed=True),
    note: str | None = Body(default=None, embed=True),
):
    return {"task": task_id, "assigned_to": assignee_id, "note": note}
```

```json
// Request body:
{ "assignee_id": 5, "note": "You're on this now" }
```

`Body(embed=True)` wraps simple values in a JSON object instead of expecting a raw value.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Source                          │ How FastAPI Identifies It
────────────────────────────────┼──────────────────────────────────────
Path parameter                  │ Name matches {placeholder} in route
Query parameter                 │ Simple type (str, int) not in path
Request body                    │ Pydantic BaseModel type
Header                          │ Annotated with Header()
Cookie                          │ Annotated with Cookie()
────────────────────────────────┼──────────────────────────────────────
Query() / Path() / Body()       │ Add validation, description, examples
Enum type                       │ Restricts to allowed values
ge, le, gt, lt                  │ Number bounds
min_length, max_length          │ String bounds
pattern                         │ Regex validation
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Dani: "Stop returning fake data. Wire it to a real database. I want full CRUD — create, read, update, delete — for projects. With proper status codes."

---

[← Chapter 2: Pydantic](chapter-02-pydantic.md) | [Chapter 4: CRUD →](chapter-04-crud.md)

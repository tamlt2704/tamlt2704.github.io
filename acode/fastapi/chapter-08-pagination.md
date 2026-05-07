# Chapter 8: Pagination, Filtering & Sorting

[← Chapter 7: Relationships](chapter-07-relationships.md) | [Chapter 9: File Uploads →](chapter-09-uploads.md)

---

## The Task

Marcus: "The project has 2,000 tasks. I can't load them all. I need: pagination (page/size), filtering (by status, assignee), sorting (by priority, date), and search (by title). Return total count so I can show page numbers."

---

## Paginated Response Schema

```python
# app/schemas/common.py
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int
```

---

## The Endpoint

```python
@router.get("/projects/{project_id}/tasks", response_model=PaginatedResponse[TaskResponse])
async def list_tasks(
    project_id: int,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    status: TaskStatus | None = None,
    assignee_id: int | None = None,
    search: str | None = Query(default=None, min_length=2),
    sort_by: str = Query(default="created_at", pattern="^(created_at|priority|title)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    query = select(Task).where(Task.project_id == project_id)

    # Apply filters
    if status:
        query = query.where(Task.status == status)
    if assignee_id:
        query = query.where(Task.assignee_id == assignee_id)
    if search:
        query = query.where(Task.title.ilike(f"%{search}%"))

    # Count total (before pagination)
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # Apply sorting
    sort_column = getattr(Task, sort_by)
    query = query.order_by(sort_column.desc() if sort_order == "desc" else sort_column.asc())

    # Apply pagination
    query = query.offset((page - 1) * size).limit(size)
    query = query.options(selectinload(Task.assignee))

    result = await db.execute(query)
    tasks = result.scalars().all()

    return PaginatedResponse(
        items=tasks,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )
```

```bash
curl "http://localhost:8000/projects/1/tasks?page=2&size=10&status=in_progress&sort_by=priority&sort_order=asc"
```

```json
{
  "items": [...],
  "total": 47,
  "page": 2,
  "size": 10,
  "pages": 5
}
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Pattern                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
.offset((page-1)*size).limit()  │ Pagination
.where(col == val)              │ Filter
.where(col.ilike(f"%{q}%"))    │ Search (case-insensitive)
.order_by(col.desc())           │ Sort
func.count() + subquery         │ Total count for pagination
Generic[T] response model       │ Reusable paginated wrapper
────────────────────────────────┴──────────────────────────────────────
```

---

[← Chapter 7: Relationships](chapter-07-relationships.md) | [Chapter 9: File Uploads →](chapter-09-uploads.md)

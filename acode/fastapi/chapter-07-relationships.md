# Chapter 7: Relationships & Nested Data

[← Chapter 6: Auth](chapter-06-auth.md) | [Chapter 8: Pagination & Filtering →](chapter-08-pagination.md)

---

## The Task

Marcus: "When I fetch a project, I need its tasks included. When I fetch a task, I need the assignee's name. Nested objects, not just IDs."

This chapter covers: SQLAlchemy relationships, eager/lazy loading, nested Pydantic responses, and avoiding N+1 queries.

---

## SQLAlchemy Relationships

```python
# app/models/task.py
class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20), default="todo")
    priority: Mapped[int] = mapped_column(default=3)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

    project: Mapped["Project"] = relationship(back_populates="tasks")
    assignee: Mapped["User | None"] = relationship()
    comments: Mapped[list["Comment"]] = relationship(back_populates="task")
```

---

## Nested Response Schemas

```python
# app/schemas/task.py
class AssigneeResponse(BaseModel):
    id: int
    name: str
    avatar_url: str | None
    model_config = {"from_attributes": True}

class TaskResponse(BaseModel):
    id: int
    title: str
    status: str
    priority: int
    assignee: AssigneeResponse | None
    created_at: datetime
    model_config = {"from_attributes": True}

class ProjectDetailResponse(BaseModel):
    id: int
    name: str
    description: str | None
    tasks: list[TaskResponse]
    model_config = {"from_attributes": True}
```

---

## Eager Loading (Avoid N+1)

```python
from sqlalchemy.orm import selectinload

@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project_detail(project_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .options(
            selectinload(Project.tasks).selectinload(Task.assignee)
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
```

`selectinload` fetches related objects in a single extra query (not one per task). Without it: 1 query for the project + N queries for N tasks = N+1 problem.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Pattern                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
relationship(back_populates)    │ Define ORM relationship
ForeignKey("table.id")          │ Database-level foreign key
selectinload(Model.relation)    │ Eager load in one extra query
joinedload(Model.relation)      │ Eager load via JOIN
Nested Pydantic model           │ Serialize related objects
────────────────────────────────┴──────────────────────────────────────
```

---

[← Chapter 6: Auth](chapter-06-auth.md) | [Chapter 8: Pagination & Filtering →](chapter-08-pagination.md)

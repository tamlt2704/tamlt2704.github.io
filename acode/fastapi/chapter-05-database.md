# Chapter 5: Database — SQLAlchemy + PostgreSQL

[← Chapter 4: CRUD](chapter-04-crud.md) | [Chapter 6: Authentication →](chapter-06-auth.md)

---

## The Task

Dani: "In-memory data dies on restart. Wire it to Postgres. Use SQLAlchemy 2.0 with async. And set up Alembic for migrations — I don't want manual `CREATE TABLE` scripts."

---

## Setup

```bash
pip install sqlalchemy[asyncio] asyncpg alembic
```

```bash
docker run -d --name pulseboard-db -p 5432:5432 \
  -e POSTGRES_DB=pulseboard -e POSTGRES_PASSWORD=pulseboard \
  postgres:16
```

---

## Database Configuration

```python
# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "postgresql+asyncpg://postgres:pulseboard@localhost:5432/pulseboard"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

---

## SQLAlchemy Models

```python
# app/models/project.py
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, UTC
from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    color: Mapped[str] = mapped_column(String(7), default="#6366f1")
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    # Relationships
    owner: Mapped["User"] = relationship(back_populates="projects")
    tasks: Mapped[list["Task"]] = relationship(back_populates="project", cascade="all, delete-orphan")
```

---

## Async CRUD Operations

```python
# app/routers/projects.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(project: ProjectCreate, db: AsyncSession = Depends(get_db)):
    db_project = Project(**project.model_dump(), owner_id=1)
    db.add(db_project)
    await db.flush()
    await db.refresh(db_project)
    return db_project


@router.get("/", response_model=list[ProjectResponse])
async def list_projects(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Project).offset(skip).limit(limit).order_by(Project.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db)):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await db.delete(project)
```

---

## Dependency Injection: `Depends(get_db)`

```python
async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
```

`Depends(get_db)` tells FastAPI: "Before running this route, call `get_db()`, pass the result as `db`, and clean up after." This is FastAPI's dependency injection — we'll use it heavily for auth in Chapter 6.

---

## Alembic Migrations

```bash
alembic init alembic
```

Edit `alembic/env.py` to use your models and async engine. Then:

```bash
alembic revision --autogenerate -m "create projects table"
alembic upgrade head
```

Alembic detects your SQLAlchemy models and generates migration scripts. No manual SQL.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
create_async_engine()           │ Async database connection
async_sessionmaker()            │ Creates sessions for queries
Depends(get_db)                 │ Inject DB session into routes
await db.execute(select(...))   │ Run a query
await db.get(Model, id)         │ Get by primary key
db.add(obj)                     │ Insert new row
await db.flush()                │ Write to DB (within transaction)
await db.refresh(obj)           │ Reload from DB (get generated fields)
await db.delete(obj)            │ Delete a row
Mapped[type]                    │ SQLAlchemy 2.0 typed columns
alembic revision --autogenerate │ Generate migration from models
alembic upgrade head            │ Apply migrations
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Marcus: "Anyone can create projects right now. I need login. JWT tokens. Protected endpoints."

---

[← Chapter 4: CRUD](chapter-04-crud.md) | [Chapter 6: Authentication →](chapter-06-auth.md)

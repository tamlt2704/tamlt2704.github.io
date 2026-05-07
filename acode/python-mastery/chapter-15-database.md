# Chapter 15: "Talk to the Database"

[← Chapter 14: CLI](chapter-14-cli.md) | [Chapter 16: API →](chapter-16-api.md)

---

## The Problem

Rina, Monday standup:

> "The bot restarted over the weekend and lost all ticket data. 47 tickets — gone. Users are furious. We need a real database. PostgreSQL. Store tickets, messages, user preferences. If the bot restarts, nothing should be lost."

Leo: "And use SQLAlchemy. I don't want raw SQL strings scattered everywhere."

---

## SQLAlchemy: The ORM

```bash
pip install sqlalchemy psycopg2-binary alembic
```

### Defining Models

```python
# models.py
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="reporter")
    
    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r})"


class Ticket(Base):
    __tablename__ = "tickets"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(String(20), default="open")
    reporter_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relationships
    reporter: Mapped["User"] = relationship(back_populates="tickets")
    messages: Mapped[list["Message"]] = relationship(back_populates="ticket")
    
    def __repr__(self) -> str:
        return f"Ticket(id={self.id}, title={self.title!r}, status={self.status!r})"


class Message(Base):
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(Text)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    ticket_id: Mapped[int | None] = mapped_column(ForeignKey("tickets.id"), nullable=True)
    channel: Mapped[str] = mapped_column(String(100))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    ticket: Mapped["Ticket | None"] = relationship(back_populates="messages")
```

---

## Engine and Sessions

```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Connection string
DATABASE_URL = "postgresql://pulsebot:secret@localhost:5432/pulsebot"

# Engine — manages the connection pool
engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # max connections in pool
    max_overflow=20,       # extra connections when pool is full
    pool_timeout=30,       # wait time for a connection
    pool_recycle=3600,     # recycle connections after 1 hour
    echo=False,            # set True to log SQL queries
)

# Session factory
SessionLocal = sessionmaker(bind=engine)


# Create all tables (for development)
def init_db():
    Base.metadata.create_all(engine)


# Session context manager
from contextlib import contextmanager

@contextmanager
def get_session() -> Session:
    """Get a database session with automatic cleanup."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

---

## CRUD Operations

### Create

```python
def create_ticket(title: str, reporter_id: str, priority: str = "medium") -> Ticket:
    with get_session() as session:
        ticket = Ticket(
            title=title,
            reporter_id=reporter_id,
            priority=priority,
        )
        session.add(ticket)
        session.flush()  # get the auto-generated ID
        ticket_id = ticket.id
        session.commit()
    return ticket


def create_tickets_bulk(tickets_data: list[dict]) -> int:
    """Create many tickets at once."""
    with get_session() as session:
        tickets = [Ticket(**data) for data in tickets_data]
        session.add_all(tickets)
    return len(tickets)
```

### Read

```python
from sqlalchemy import select, func


def get_ticket(ticket_id: int) -> Ticket | None:
    with get_session() as session:
        return session.get(Ticket, ticket_id)


def list_tickets(
    priority: str | None = None,
    status: str = "open",
    limit: int = 20,
) -> list[Ticket]:
    with get_session() as session:
        query = select(Ticket).where(Ticket.status == status)
        
        if priority:
            query = query.where(Ticket.priority == priority)
        
        query = query.order_by(Ticket.created_at.desc()).limit(limit)
        
        result = session.execute(query)
        return list(result.scalars().all())


def search_tickets(keyword: str) -> list[Ticket]:
    with get_session() as session:
        query = select(Ticket).where(
            Ticket.title.ilike(f"%{keyword}%")
        )
        result = session.execute(query)
        return list(result.scalars().all())


def count_by_priority() -> dict[str, int]:
    with get_session() as session:
        query = (
            select(Ticket.priority, func.count(Ticket.id))
            .group_by(Ticket.priority)
        )
        result = session.execute(query)
        return dict(result.all())
```

### Update

```python
def update_ticket(ticket_id: int, **kwargs) -> Ticket | None:
    with get_session() as session:
        ticket = session.get(Ticket, ticket_id)
        if ticket is None:
            return None
        
        for key, value in kwargs.items():
            setattr(ticket, key, value)
        
        return ticket


def close_ticket(ticket_id: int) -> bool:
    with get_session() as session:
        ticket = session.get(Ticket, ticket_id)
        if ticket is None:
            return False
        ticket.status = "closed"
        return True
```

### Delete

```python
def delete_ticket(ticket_id: int) -> bool:
    with get_session() as session:
        ticket = session.get(Ticket, ticket_id)
        if ticket is None:
            return False
        session.delete(ticket)
        return True
```

---

## Queries: Joins and Relationships

```python
from sqlalchemy import select
from sqlalchemy.orm import joinedload


# Eager loading — fetch ticket + reporter in one query
def get_ticket_with_reporter(ticket_id: int) -> Ticket | None:
    with get_session() as session:
        query = (
            select(Ticket)
            .options(joinedload(Ticket.reporter))
            .where(Ticket.id == ticket_id)
        )
        result = session.execute(query)
        return result.scalar_one_or_none()


# Join query — tickets with their reporters
def get_tickets_by_user(user_id: str) -> list[Ticket]:
    with get_session() as session:
        query = (
            select(Ticket)
            .join(User)
            .where(User.id == user_id)
            .order_by(Ticket.created_at.desc())
        )
        result = session.execute(query)
        return list(result.scalars().all())


# Aggregate query
def get_user_stats(user_id: str) -> dict:
    with get_session() as session:
        query = (
            select(
                func.count(Ticket.id).label("total"),
                func.count(Ticket.id).filter(Ticket.status == "open").label("open"),
                func.count(Ticket.id).filter(Ticket.status == "closed").label("closed"),
            )
            .where(Ticket.reporter_id == user_id)
        )
        result = session.execute(query).one()
        return {"total": result.total, "open": result.open, "closed": result.closed}
```

---

## Migrations with Alembic

Alembic tracks database schema changes over time.

```bash
# Initialize alembic
alembic init alembic

# Edit alembic/env.py to point to your models
# Set sqlalchemy.url in alembic.ini
```

```python
# alembic/env.py (key part)
from models import Base
target_metadata = Base.metadata
```

```bash
# Create a migration after changing models
alembic revision --autogenerate -m "add priority column to tickets"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1

# See current version
alembic current

# See migration history
alembic history
```

### Generated Migration Example

```python
# alembic/versions/001_add_priority_column.py
"""add priority column to tickets"""

from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None


def upgrade():
    op.add_column("tickets", sa.Column("priority", sa.String(20), default="medium"))
    op.create_index("ix_tickets_priority", "tickets", ["priority"])


def downgrade():
    op.drop_index("ix_tickets_priority", "tickets")
    op.drop_column("tickets", "priority")
```

---

## Connection Pooling

```python
from sqlalchemy import create_engine, event


engine = create_engine(
    DATABASE_URL,
    pool_size=10,        # 10 persistent connections
    max_overflow=20,     # up to 30 total under load
    pool_timeout=30,     # wait 30s for a connection
    pool_pre_ping=True,  # verify connections are alive
)


# Monitor pool health
@event.listens_for(engine, "checkout")
def on_checkout(dbapi_conn, connection_rec, connection_proxy):
    """Log when a connection is checked out from the pool."""
    pass  # add monitoring here


# Pool status
def get_pool_status() -> dict:
    pool = engine.pool
    return {
        "size": pool.size(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
    }
```

---

## The Bot with Database

```python
# handlers/ticket_handler.py
from dataclasses import dataclass
from database import get_session
from models import Ticket, User


@dataclass
class TicketHandler:
    """Handle ticket commands with database persistence."""
    
    def handle(self, msg: dict) -> str:
        parts = msg["text"].split()
        action = parts[1] if len(parts) > 1 else "list"
        
        match action:
            case "create":
                return self._create(msg)
            case "list":
                return self._list(msg)
            case "close":
                return self._close(msg, parts)
            case _:
                return f"Unknown ticket action: {action}"
    
    def _create(self, msg: dict) -> str:
        title = " ".join(msg["text"].split()[2:])
        if not title:
            return "Usage: ticket create <title>"
        
        with get_session() as session:
            ticket = Ticket(title=title, reporter_id=msg["user"])
            session.add(ticket)
            session.flush()
            return f"🎫 Created ticket #{ticket.id}: {title}"
    
    def _list(self, msg: dict) -> str:
        with get_session() as session:
            tickets = (
                session.execute(
                    select(Ticket)
                    .where(Ticket.status == "open")
                    .order_by(Ticket.created_at.desc())
                    .limit(10)
                )
                .scalars()
                .all()
            )
            
            if not tickets:
                return "No open tickets 🎉"
            
            lines = ["📋 Open tickets:"]
            for t in tickets:
                lines.append(f"  #{t.id} [{t.priority}] {t.title}")
            return "\n".join(lines)
    
    def _close(self, msg: dict, parts: list[str]) -> str:
        if len(parts) < 3:
            return "Usage: ticket close <id>"
        
        ticket_id = int(parts[2].lstrip("#"))
        with get_session() as session:
            ticket = session.get(Ticket, ticket_id)
            if ticket is None:
                return f"Ticket #{ticket_id} not found"
            ticket.status = "closed"
            return f"✅ Closed ticket #{ticket_id}: {ticket.title}"
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ Code
────────────────────────────────┼──────────────────────────────────────
Define model                    │ class X(Base): __tablename__ = "x"
Column                          │ x: Mapped[str] = mapped_column(...)
Relationship                    │ items: Mapped[list["Y"]] = relationship()
Foreign key                     │ ForeignKey("table.column")
────────────────────────────────┼──────────────────────────────────────
Create engine                   │ create_engine(url, pool_size=10)
Create session                  │ SessionLocal = sessionmaker(bind=engine)
────────────────────────────────┼──────────────────────────────────────
Insert                          │ session.add(obj)
Query                           │ session.execute(select(Model).where(...))
Update                          │ obj.field = new_value (then commit)
Delete                          │ session.delete(obj)
────────────────────────────────┼──────────────────────────────────────
Eager load                      │ .options(joinedload(Model.rel))
Filter                          │ .where(Model.col == value)
Order                           │ .order_by(Model.col.desc())
Limit                           │ .limit(n)
Aggregate                       │ func.count(), func.sum()
────────────────────────────────┼──────────────────────────────────────
alembic revision --autogenerate │ Create migration
alembic upgrade head            │ Apply migrations
alembic downgrade -1            │ Rollback one step
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The data is safe. Tickets survive restarts. The database handles concurrent access. Then Rina comes back: "Now I want a web dashboard. An API that the frontend can call. Ticket list, create, update — all over HTTP." Time to build an API with FastAPI.

---

[← Chapter 14: CLI](chapter-14-cli.md) | [Chapter 16: API →](chapter-16-api.md)

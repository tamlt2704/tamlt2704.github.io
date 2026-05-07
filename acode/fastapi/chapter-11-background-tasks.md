# Chapter 11: Background Tasks & Notifications

[← Chapter 10: Errors](chapter-10-errors.md) | [Chapter 12: WebSockets →](chapter-12-websockets.md)

---

## The Problem

When a task is assigned, the assignee should get an email notification. But sending email takes 2-3 seconds. The API response shouldn't wait for it.

---

## FastAPI BackgroundTasks

```python
from fastapi import BackgroundTasks

def send_notification_email(email: str, task_title: str, assigner_name: str):
    # Simulate slow email sending
    import time; time.sleep(2)
    print(f"Email sent to {email}: You were assigned '{task_title}' by {assigner_name}")


@router.patch("/{task_id}")
async def update_task(
    task_id: int,
    update: TaskUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await db.get(Task, task_id)
    if not task:
        raise NotFoundError("Task", task_id)

    # Apply updates
    if update.assignee_id and update.assignee_id != task.assignee_id:
        assignee = await db.get(User, update.assignee_id)
        # Send notification AFTER response (non-blocking)
        background_tasks.add_task(
            send_notification_email,
            assignee.email,
            task.title,
            current_user.name,
        )

    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    await db.flush()
    await db.refresh(task)
    return task
```

The API responds immediately (200ms). The email sends in the background (2 seconds later). The user doesn't wait.

---

## When BackgroundTasks Isn't Enough

BackgroundTasks runs in the same process. If the server crashes mid-email, the task is lost. For critical tasks, use a proper task queue:

```bash
pip install celery redis
```

```python
# app/worker.py
from celery import Celery

celery_app = Celery("pulseboard", broker="redis://localhost:6379/0")

@celery_app.task
def send_notification_email(email: str, task_title: str, assigner_name: str):
    # This runs in a separate worker process
    # Retries automatically on failure
    ...
```

```python
# In your route:
from app.worker import send_notification_email

send_notification_email.delay(assignee.email, task.title, current_user.name)
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Tool                            │ Use When
────────────────────────────────┼──────────────────────────────────────
BackgroundTasks                 │ Simple, non-critical (logging, emails)
Celery + Redis                  │ Critical, retryable, distributed
background_tasks.add_task(fn)   │ Schedule after response
task.delay(args)                │ Send to Celery worker
────────────────────────────────┴──────────────────────────────────────
```

---

[← Chapter 10: Errors](chapter-10-errors.md) | [Chapter 12: WebSockets →](chapter-12-websockets.md)

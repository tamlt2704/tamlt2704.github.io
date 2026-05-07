# Chapter 10: Error Handling & Custom Exceptions

[← Chapter 9: Uploads](chapter-09-uploads.md) | [Chapter 11: Background Tasks →](chapter-11-background-tasks.md)

---

## The Problem

Marcus: "When something goes wrong, I get different error formats from different endpoints. Sometimes `{detail: ...}`, sometimes `{error: ...}`, sometimes a raw 500 with HTML. I need consistent error responses."

---

## Custom Exception Classes

```python
# app/exceptions.py
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(self, status_code: int, code: str, message: str, details: dict | None = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}


class NotFoundError(AppException):
    def __init__(self, resource: str, resource_id: int | str):
        super().__init__(
            status_code=404,
            code="NOT_FOUND",
            message=f"{resource} not found",
            details={"resource": resource, "id": str(resource_id)},
        )


class ForbiddenError(AppException):
    def __init__(self, message: str = "You don't have permission to perform this action"):
        super().__init__(status_code=403, code="FORBIDDEN", message=message)


class ConflictError(AppException):
    def __init__(self, message: str):
        super().__init__(status_code=409, code="CONFLICT", message=message)
```

---

## Global Exception Handler

```python
# main.py
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Log the real error, return generic message
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {},
            }
        },
    )
```

---

## Usage in Routes

```python
@router.get("/{project_id}")
async def get_project(project_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    project = await db.get(Project, project_id)
    if not project:
        raise NotFoundError("Project", project_id)
    if project.owner_id != current_user.id:
        raise ForbiddenError("You can only view your own projects")
    return project
```

Every error response now follows the same format:

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Project not found",
    "details": { "resource": "Project", "id": "42" }
  }
}
```

Marcus can handle all errors with one pattern in the frontend.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Pattern                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
Custom exception classes        │ Typed, consistent errors
@app.exception_handler(Exc)     │ Global handler for exception type
raise NotFoundError(...)        │ Throw from anywhere in code
JSONResponse(status, content)   │ Custom response format
Catch-all Exception handler     │ Hide internal errors from users
────────────────────────────────┴──────────────────────────────────────
```

---

[← Chapter 9: Uploads](chapter-09-uploads.md) | [Chapter 11: Background Tasks →](chapter-11-background-tasks.md)

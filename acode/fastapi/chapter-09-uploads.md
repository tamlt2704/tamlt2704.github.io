# Chapter 9: File Uploads

[← Chapter 8: Pagination](chapter-08-pagination.md) | [Chapter 10: Error Handling →](chapter-10-errors.md)

---

## The Task

Marcus: "Users attach files to tasks — screenshots, documents, designs. I need an upload endpoint that validates file type and size, stores the file, and returns a URL."

---

## Basic Upload

```python
from fastapi import UploadFile, File, HTTPException
import shutil
from pathlib import Path

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_TYPES = {"image/png", "image/jpeg", "image/webp", "application/pdf"}


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    # Validate content type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"File type {file.content_type} not allowed")

    # Validate size (read in chunks)
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large (max 10MB)")

    # Save with unique name
    ext = Path(file.filename).suffix
    filename = f"{uuid4().hex}{ext}"
    filepath = UPLOAD_DIR / filename

    with open(filepath, "wb") as f:
        f.write(contents)

    return {"filename": filename, "url": f"/files/{filename}", "size": len(contents)}
```

---

## Multiple Files

```python
@router.post("/tasks/{task_id}/attachments")
async def attach_files(
    task_id: int,
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    results = []
    for file in files:
        # validate and save each...
        results.append({"filename": file.filename, "size": file.size})
    return results
```

---

## Serving Files

```python
from fastapi.staticfiles import StaticFiles

app.mount("/files", StaticFiles(directory="uploads"), name="files")
```

Now `http://localhost:8000/files/abc123.png` serves the uploaded file.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
UploadFile                      │ Represents an uploaded file
File(...)                       │ Marks parameter as file upload
file.read()                     │ Read file contents (bytes)
file.filename                   │ Original filename
file.content_type               │ MIME type
file.size                       │ File size in bytes
StaticFiles(directory)          │ Serve static files
────────────────────────────────┴──────────────────────────────────────
```

---

[← Chapter 8: Pagination](chapter-08-pagination.md) | [Chapter 10: Error Handling →](chapter-10-errors.md)

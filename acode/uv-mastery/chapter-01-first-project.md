# Chapter 1: Your First uv Project

[← Overview](chapter-00-overview.md) | [Chapter 2: Adding Dependencies →](chapter-02-adding-deps.md)

---

## The Task

Nadia: "Set up the new `dataforge-api` service. Python 3.12. FastAPI. I want a new hire to clone the repo and be running in 30 seconds."

---

## Creating a Project

```bash
# Create a new project
uv init dataforge-api
cd dataforge-api
```

This creates:

```
dataforge-api/
├── pyproject.toml      ← project metadata and dependencies
├── README.md
├── hello.py            ← sample script
└── .python-version     ← pinned Python version
```

---

## pyproject.toml: The Single Source of Truth

```toml
# pyproject.toml
[project]
name = "dataforge-api"
version = "0.1.0"
description = "DataForge API service"
readme = "README.md"
requires-python = ">=3.12"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

This is standard PEP 621 — not a uv-specific format. Any Python tool can read it.

---

## Running Code

```bash
# uv run automatically:
# 1. Creates a virtual environment (if needed)
# 2. Installs dependencies (if needed)
# 3. Runs your command in that environment

uv run python hello.py
# Hello from dataforge-api!

uv run python -c "import sys; print(sys.version)"
# 3.12.x
```

**You never manually activate a virtual environment.** `uv run` handles it. This is the key workflow difference from pip/poetry.

---

## Where's the Virtual Environment?

```bash
# uv creates .venv/ in your project root
ls .venv/
# bin/  include/  lib/  pyvenv.cfg

# You CAN activate it manually (for IDE integration)
source .venv/bin/activate  # Unix
# .venv\Scripts\activate   # Windows

# But you don't need to — uv run does it for you
```

---

## Adding Your First Dependency

```bash
uv add fastapi
```

What just happened:
1. Updated `pyproject.toml` — added `fastapi` to `dependencies`
2. Resolved all transitive dependencies
3. Created/updated `uv.lock` — pinned exact versions
4. Installed everything into `.venv/`

```toml
# pyproject.toml (after uv add)
[project]
name = "dataforge-api"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.109.0",
]
```

```bash
# Add multiple at once
uv add uvicorn[standard] pydantic-settings sqlalchemy

# Add with version constraint
uv add "httpx>=0.27,<1.0"
```

---

## The Lockfile: uv.lock

```bash
# uv.lock is auto-generated — never edit by hand
# It contains EXACT versions for ALL platforms

cat uv.lock
```

```toml
# Snippet of uv.lock
[[package]]
name = "fastapi"
version = "0.109.2"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "pydantic" },
    { name = "starlette" },
    { name = "typing-extensions" },
]

[[package]]
name = "pydantic"
version = "2.6.1"
source = { registry = "https://pypi.org/simple" }
# ...
```

**Commit `uv.lock` to git.** It ensures everyone gets identical dependencies.

---

## uv sync: Install from Lockfile

```bash
# Install exactly what's in uv.lock (fast — no resolution needed)
uv sync

# This is what new hires run after cloning:
git clone <repo>
cd dataforge-api
uv sync
uv run python -m dataforge_api
# Done. 3 seconds.
```

`uv sync` vs `uv add`:
- `uv add` → modifies pyproject.toml, re-resolves, updates lockfile, installs
- `uv sync` → reads lockfile, installs exactly those versions (no resolution)

---

## Project Structure (What We'll Build)

```
dataforge-api/
├── pyproject.toml
├── uv.lock                  ← committed to git
├── .python-version          ← "3.12"
├── .venv/                   ← NOT committed (in .gitignore)
├── src/
│   └── dataforge_api/
│       ├── __init__.py
│       ├── main.py          ← FastAPI app
│       ├── config.py
│       ├── models.py
│       └── routes/
│           └── health.py
├── tests/
│   ├── __init__.py
│   └── test_health.py
└── README.md
```

---

## Setting Up the App

```bash
# Create the source layout
uv add fastapi "uvicorn[standard]"
```

```python
# src/dataforge_api/main.py
from fastapi import FastAPI

app = FastAPI(title="DataForge API", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "healthy", "service": "dataforge-api"}
```

```bash
# Run the server
uv run uvicorn dataforge_api.main:app --reload

# Or with a script entry point (configure in pyproject.toml)
```

---

## Script Entry Points

```toml
# pyproject.toml
[project.scripts]
dataforge-api = "dataforge_api.main:start"
```

```python
# src/dataforge_api/main.py
import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "healthy"}

def start():
    uvicorn.run("dataforge_api.main:app", host="0.0.0.0", port=8000, reload=True)
```

```bash
# Now you can run:
uv run dataforge-api
# Starts the server
```

---

## Removing Dependencies

```bash
# Remove a package
uv remove httpx

# This updates pyproject.toml, re-resolves, updates lockfile, uninstalls
```

---

## Viewing What's Installed

```bash
# Show the dependency tree
uv tree

# Output:
# dataforge-api v0.1.0
# ├── fastapi v0.109.2
# │   ├── pydantic v2.6.1
# │   │   ├── annotated-types v0.6.0
# │   │   └── pydantic-core v2.16.2
# │   ├── starlette v0.36.3
# │   │   └── anyio v4.2.0
# │   └── typing-extensions v4.9.0
# └── uvicorn v0.27.1
#     ├── click v8.1.7
#     └── h11 v0.14.0

# Show outdated packages
uv lock --check  # verify lockfile is up to date with pyproject.toml
```

---

## .gitignore

```gitignore
# Virtual environment (recreated by uv sync)
.venv/

# Python cache
__pycache__/
*.pyc

# DO commit these:
# pyproject.toml  ← dependency specs
# uv.lock        ← exact versions
# .python-version ← Python version
```

---

## The 30-Second Setup (Nadia's Goal)

New hire workflow:

```bash
git clone git@github.com:dataforge/dataforge-api.git
cd dataforge-api
uv sync          # installs Python + all deps (< 5 seconds)
uv run dataforge-api   # starts the server
```

No `pyenv install`. No `python -m venv`. No `pip install -r requirements.txt`. No `source .venv/bin/activate`. One command.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Command                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
uv init <name>                  │ Create a new project
uv add <package>                │ Add dependency (updates toml + lock)
uv remove <package>             │ Remove dependency
uv sync                         │ Install from lockfile (fast, exact)
uv run <command>                │ Run in project environment
uv tree                         │ Show dependency tree
uv lock                         │ Regenerate lockfile without installing
pyproject.toml                  │ Your dependency specs (committed)
uv.lock                         │ Exact versions (committed)
.venv/                          │ Virtual env (NOT committed)
.python-version                 │ Pinned Python version
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

You have one dependency (FastAPI). But real projects have dozens — and they need to be organized. Dev tools (ruff, pytest) shouldn't ship to production. Test dependencies (pytest, factory-boy) shouldn't be in the Docker image. 

Omar: "I have 40 packages. Half are dev tools. How do I keep production lean?"

---

[← Overview](chapter-00-overview.md) | [Chapter 2: Adding Dependencies →](chapter-02-adding-deps.md)

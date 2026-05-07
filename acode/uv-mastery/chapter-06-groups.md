# Chapter 6: Dependency Groups — Dev, Test, Prod, and Beyond

[← Chapter 5: uv run](chapter-05-uv-run.md) | [Chapter 7: Platform-Specific Dependencies →](chapter-07-platform-deps.md)

---

## The Problem

Omar: "My Docker image has pytest, ruff, mypy, and mkdocs in it. That's 200MB of tools that never run in production. But if I remove them from `dependencies`, I can't use them locally."

---

## Dependency Groups (PEP 735)

Groups are named sets of dependencies that are installed by default in development but can be excluded for production:

```toml
[project]
dependencies = [
    # These ALWAYS get installed (production)
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "sqlalchemy[asyncio]>=2.0.25",
    "asyncpg>=0.29.0",
]

[dependency-groups]
dev = [
    "ruff>=0.2.0",
    "mypy>=1.8.0",
    "pre-commit>=3.6.0",
    "ipython>=8.20.0",
]
test = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "factory-boy>=3.3.0",
]
docs = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.5.0",
]
lint = [
    "ruff>=0.2.0",
    "mypy>=1.8.0",
]
```

---

## Installing Groups Selectively

```bash
# Development (everything — default behavior)
uv sync
# Installs: production + dev + test + docs + lint

# Production only (Docker, deployment)
uv sync --only-group default
# Or exclude all non-production groups:
uv sync --no-group dev --no-group test --no-group docs --no-group lint

# CI: production + test only
uv sync --no-group dev --no-group docs

# Docs build: production + docs
uv sync --group docs --no-group dev --no-group test --no-group lint
```

---

## Group Includes (Composing Groups)

Groups can include other groups to avoid repetition:

```toml
[dependency-groups]
test = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
]
lint = [
    "ruff>=0.2.0",
    "mypy>=1.8.0",
]
# 'dev' includes both test and lint, plus extras
dev = [
    { include-group = "test" },
    { include-group = "lint" },
    "ipython>=8.20.0",
    "pre-commit>=3.6.0",
]
```

Now `uv sync --group dev` gives you everything: test deps, lint deps, and dev-specific tools.

---

## Groups vs. Optional Dependencies

They serve different purposes:

```toml
# GROUPS: for development workflow (not shipped to users)
# "I need pytest to develop this project"
[dependency-groups]
test = ["pytest>=8.0.0"]

# OPTIONAL DEPS: for consumers of your package
# "Users can install my package with Redis support"
[project.optional-dependencies]
redis = ["redis>=5.0.0"]
postgres = ["asyncpg>=0.29.0"]
```

- **Groups** → developer tools, CI tools, never in the published package
- **Optional dependencies** → features consumers can opt into with `pip install pkg[redis]`

---

## Practical: Docker Multi-Stage with Groups

```dockerfile
# Dockerfile
FROM python:3.12-slim AS base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files first (layer caching)
COPY pyproject.toml uv.lock ./

# Install ONLY production dependencies
RUN uv sync --frozen --no-group dev --no-group test --no-group docs --no-dev

# Copy application code
COPY src/ ./src/

# Production image
FROM base AS production
CMD ["uv", "run", "uvicorn", "dataforge_api.main:app", "--host", "0.0.0.0"]

# Test image (for CI)
FROM base AS test
RUN uv sync --frozen --no-group dev --no-group docs
COPY tests/ ./tests/
CMD ["uv", "run", "pytest"]
```

Result:
- Production image: only FastAPI, SQLAlchemy, etc. (~150MB)
- Test image: adds pytest, factory-boy (~180MB)
- Neither has ruff, mypy, mkdocs, ipython

---

## Running Commands from Specific Groups

```bash
# Run pytest (needs test group)
uv run --group test pytest

# Run ruff (needs lint group)
uv run --group lint ruff check src/

# Run mkdocs (needs docs group)
uv run --group docs mkdocs serve
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
[dependency-groups]             │ Named sets of dev/tool dependencies
[project.optional-dependencies] │ Consumer-facing optional features
uv sync --no-group <name>       │ Exclude a group from install
uv sync --group <name>          │ Include a specific group
{ include-group = "test" }      │ Compose groups together
uv run --group test pytest      │ Run with a group's deps available
Groups = dev workflow            │ Not shipped in published package
Optional deps = consumer choice │ Installed with pkg[extra]
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Omar's ML pipeline needs PyTorch with CUDA on Linux GPU machines, but CPU-only on macOS for local development. And `uvloop` doesn't exist on Windows. Platform-specific dependencies are the next challenge.

---

[← Chapter 5: uv run](chapter-05-uv-run.md) | [Chapter 7: Platform-Specific Dependencies →](chapter-07-platform-deps.md)

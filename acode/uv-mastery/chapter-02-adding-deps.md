# Chapter 2: Adding Dependencies — Groups, Constraints, and Extras

[← Chapter 1: First Project](chapter-01-first-project.md) | [Chapter 3: Lockfile & Sync →](chapter-03-lockfile.md)

---

## The Problem

The `dataforge-api` service has 40 dependencies. Some are production (FastAPI, SQLAlchemy). Some are dev tools (ruff, mypy). Some are test-only (pytest, factory-boy). Some are docs (mkdocs).

Omar: "My Docker image is 2GB because it includes pytest, ruff, and mkdocs. None of that should be in production."

---

## Dependency Groups

uv supports **dependency groups** — named sets of dependencies that you can install selectively:

```bash
# Add production dependencies (default group)
uv add fastapi uvicorn sqlalchemy

# Add dev dependencies
uv add --group dev ruff mypy pre-commit

# Add test dependencies
uv add --group test pytest pytest-asyncio httpx factory-boy

# Add docs dependencies
uv add --group docs mkdocs mkdocs-material
```

The resulting `pyproject.toml`:

```toml
[project]
name = "dataforge-api"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "sqlalchemy>=2.0.25",
]

[dependency-groups]
dev = [
    "ruff>=0.2.0",
    "mypy>=1.8.0",
    "pre-commit>=3.6.0",
]
test = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "httpx>=0.27.0",
    "factory-boy>=3.3.0",
]
docs = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.5.0",
]
```

---

## Installing Specific Groups

```bash
# Install production deps only (for Docker)
uv sync --no-group dev --no-group test --no-group docs

# Install everything (local development)
uv sync

# Install production + test (CI)
uv sync --no-group dev --no-group docs

# Install only a specific group (plus production)
uv sync --group test
```

---

## Version Constraints

```bash
# Minimum version (most common)
uv add "fastapi>=0.109.0"

# Exact version (pin)
uv add "pydantic==2.6.1"

# Range
uv add "httpx>=0.27,<1.0"

# Compatible release (>=2.6.0, <3.0.0)
uv add "sqlalchemy~=2.0"

# Any version (not recommended)
uv add requests
```

### Constraint Syntax

```
>=1.0.0          at least 1.0.0
<=2.0.0          at most 2.0.0
>=1.0,<2.0       between 1.0 and 2.0
==1.5.3          exactly 1.5.3
~=1.5            >=1.5.0, <2.0.0 (compatible release)
!=1.5.3          anything except 1.5.3
```

---

## Extras: Optional Feature Sets

Many packages have optional features (extras) that pull in additional dependencies:

```bash
# Install uvicorn with its "standard" extras (includes uvloop, httptools)
uv add "uvicorn[standard]"

# Install SQLAlchemy with async support
uv add "sqlalchemy[asyncio]"

# Install httpx with HTTP/2 support
uv add "httpx[http2]"

# Multiple extras
uv add "fastapi[all]"
```

In `pyproject.toml`:

```toml
dependencies = [
    "uvicorn[standard]>=0.27.0",
    "sqlalchemy[asyncio]>=2.0.25",
]
```

---

## Your Project's Own Extras (Optional Dependencies)

You can define optional dependency sets for YOUR package:

```toml
[project.optional-dependencies]
postgres = ["asyncpg>=0.29.0", "psycopg2-binary>=2.9.9"]
redis = ["redis>=5.0.0"]
all = ["asyncpg>=0.29.0", "psycopg2-binary>=2.9.9", "redis>=5.0.0"]
```

Consumers install with:
```bash
uv add "dataforge-api[postgres]"
uv add "dataforge-api[redis]"
uv add "dataforge-api[all]"
```

---

## Platform-Specific Dependencies

Some packages are only needed on certain platforms:

```toml
[project]
dependencies = [
    "fastapi>=0.109.0",
    "uvloop>=0.19.0; sys_platform != 'win32'",  # not available on Windows
    "winloop>=0.1.0; sys_platform == 'win32'",   # Windows alternative
]
```

### Environment Markers

```toml
# Only on Linux
"package>=1.0; sys_platform == 'linux'"

# Only on Python 3.11+
"package>=1.0; python_version >= '3.11'"

# Only on macOS ARM
"package>=1.0; sys_platform == 'darwin' and platform_machine == 'arm64'"

# Only NOT on Windows
"package>=1.0; sys_platform != 'win32'"
```

---

## Overriding Dependency Resolution

When transitive dependencies conflict:

```toml
# pyproject.toml
[tool.uv]
# Force a specific version of a transitive dependency
override-dependencies = [
    "numpy==1.26.4",  # force this version even if packages want different
]
```

```bash
# Or use constraint files (pip-compatible)
uv add --constraint constraints.txt
```

```
# constraints.txt
numpy==1.26.4
protobuf>=4.0,<5.0
```

---

## Viewing Dependencies

```bash
# Full dependency tree
uv tree

# Show why a package is installed (reverse dependency)
uv tree --invert --package numpy
# Shows which packages depend on numpy

# Show outdated packages
uv pip list --outdated
```

---

## Upgrading Dependencies

```bash
# Upgrade a specific package (and re-resolve)
uv lock --upgrade-package fastapi

# Upgrade all packages to latest compatible versions
uv lock --upgrade

# Then install the new versions
uv sync
```

---

## Practical: DataForge API Dependencies

```toml
# pyproject.toml
[project]
name = "dataforge-api"
version = "0.1.0"
description = "DataForge data pipeline API"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "sqlalchemy[asyncio]>=2.0.25",
    "asyncpg>=0.29.0",
    "pydantic-settings>=2.1.0",
    "structlog>=24.1.0",
    "httpx>=0.27.0",
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
    "httpx>=0.27.0",
    "factory-boy>=3.3.0",
    "testcontainers[postgres]>=3.7.0",
]
docs = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.5.0",
]

[project.optional-dependencies]
redis = ["redis[hiredis]>=5.0.0"]
kafka = ["aiokafka>=0.10.0"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
# Ensure consistent numpy across all packages
override-dependencies = [
    "numpy>=1.26.0,<2.0",
]
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Command                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
uv add <pkg>                    │ Add production dependency
uv add --group dev <pkg>        │ Add to a dependency group
uv add "pkg[extra]"             │ Add with extras
uv add "pkg>=1.0,<2.0"         │ Add with version constraint
uv remove <pkg>                 │ Remove a dependency
uv sync                         │ Install all groups
uv sync --no-group dev          │ Skip a group (production install)
uv tree                         │ Show dependency tree
uv lock --upgrade               │ Upgrade all to latest compatible
uv lock --upgrade-package <pkg> │ Upgrade one package
override-dependencies           │ Force transitive dep versions
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Dependencies are organized. But how does the lockfile actually work? What makes it "deterministic"? And what happens when your teammate on macOS gets different packages than you on Linux?

---

[← Chapter 1: First Project](chapter-01-first-project.md) | [Chapter 3: Lockfile & Sync →](chapter-03-lockfile.md)

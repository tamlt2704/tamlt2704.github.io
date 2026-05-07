# Chapter 8: Workspaces — "Monorepo with Shared Packages"

[← Chapter 7: Platform-Specific Dependencies](chapter-07-platform-deps.md) | [Chapter 9: Private Registries →](chapter-09-private-registries.md)

---

## The Problem

DataForge has 14 services that all import from a shared `dataforge-core` library. Currently, each service has a copy of core. When you fix a bug in core, you update 14 copies. Someone always forgets one.

Nadia: "Monorepo. One repo. Shared library. All services import from the same source. One `uv sync` sets up everything."

---

## What Are Workspaces?

A workspace is a collection of packages in one repository that share a single lockfile. Changes to the shared library are immediately available to all services — no publishing, no version bumps, no copy-paste.

```
dataforge/                          ← workspace root
├── pyproject.toml                  ← workspace definition
├── uv.lock                         ← ONE lockfile for everything
├── packages/
│   └── dataforge-core/             ← shared library
│       ├── pyproject.toml
│       └── src/dataforge_core/
├── services/
│   ├── api/                        ← service 1
│   │   ├── pyproject.toml
│   │   └── src/dataforge_api/
│   ├── ml-pipeline/                ← service 2
│   │   ├── pyproject.toml
│   │   └── src/dataforge_ml/
│   └── worker/                     ← service 3
│       ├── pyproject.toml
│       └── src/dataforge_worker/
```

---

## Workspace Configuration

```toml
# Root pyproject.toml (workspace definition)
[project]
name = "dataforge-workspace"
version = "0.0.0"
requires-python = ">=3.12"

[tool.uv.workspace]
members = [
    "packages/*",
    "services/*",
]
```

That's it. uv discovers all `pyproject.toml` files in the member directories and treats them as one unified workspace.

---

## The Shared Library

```toml
# packages/dataforge-core/pyproject.toml
[project]
name = "dataforge-core"
version = "0.5.0"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.6.0",
    "structlog>=24.1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

```python
# packages/dataforge-core/src/dataforge_core/__init__.py
from dataforge_core.models import Transaction, Status
from dataforge_core.config import Settings

__all__ = ["Transaction", "Status", "Settings"]
```

---

## Services Depending on the Shared Library

```toml
# services/api/pyproject.toml
[project]
name = "dataforge-api"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "dataforge-core",           # ← workspace dependency (resolved locally)
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
]

[tool.uv.sources]
dataforge-core = { workspace = true }  # ← tells uv to use the local package
```

```toml
# services/ml-pipeline/pyproject.toml
[project]
name = "dataforge-ml"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "dataforge-core",           # ← same shared library
    "pandas>=2.2.0",
    "scikit-learn>=1.4.0",
]

[tool.uv.sources]
dataforge-core = { workspace = true }
```

---

## Working in a Workspace

```bash
# From the workspace root — sync everything
uv sync

# Work on a specific service
cd services/api
uv run uvicorn dataforge_api.main:app --reload
# dataforge-core is available as an editable install

# Run tests for one service
cd services/ml-pipeline
uv run pytest

# Run a command across the workspace
cd /path/to/dataforge
uv run --package dataforge-api uvicorn dataforge_api.main:app
```

---

## One Lockfile, All Packages

The workspace has a single `uv.lock` at the root. It contains resolved versions for ALL packages and services:

```bash
# Regenerate the lockfile (resolves everything together)
uv lock

# Sync a specific package
uv sync --package dataforge-api

# Sync everything
uv sync --all-packages
```

Benefits of a single lockfile:
- No version conflicts between services (they share the same numpy, pydantic, etc.)
- One `uv lock` resolves everything consistently
- Changes to `dataforge-core` are immediately reflected

---

## Editable Installs (Automatic)

Within a workspace, local packages are installed in **editable mode** by default. This means:
- You edit `packages/dataforge-core/src/dataforge_core/models.py`
- The change is immediately visible in `services/api` (no reinstall needed)
- Like `pip install -e .` but automatic

---

## Independent Versions

Each package in the workspace can have its own version:

```
dataforge-core:    0.5.0
dataforge-api:     0.1.0
dataforge-ml:      0.3.2
dataforge-worker:  0.2.1
```

They share a lockfile but are independently versioned and publishable.

---

## Workspace vs. Single Project

```
Single project:                     Workspace:
──────────────────────────────      ──────────────────────────────
One pyproject.toml                  Multiple pyproject.toml files
One package                         Multiple packages
One set of dependencies             Shared + per-package dependencies
Simple                              Monorepo-scale
uv sync installs one thing          uv sync installs everything
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
[tool.uv.workspace]             │ Define workspace in root pyproject.toml
members = ["packages/*"]        │ Glob pattern for member packages
{ workspace = true }            │ Use local package (not PyPI)
uv sync --all-packages          │ Sync entire workspace
uv sync --package <name>        │ Sync one specific package
uv run --package <name> <cmd>   │ Run in a specific package's context
Single uv.lock at root          │ One lockfile for all packages
Editable installs (automatic)   │ Changes to local deps are instant
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

DataForge has internal packages hosted on a private registry (not PyPI). The ML team publishes trained model wrappers to an internal Artifactory. You need to configure uv to authenticate and pull from private indexes.

---

[← Chapter 7: Platform-Specific Dependencies](chapter-07-platform-deps.md) | [Chapter 9: Private Registries →](chapter-09-private-registries.md)

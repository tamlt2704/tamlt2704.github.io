# Project Management

[prev: Installation](chapter-01-install.md) | [next: Virtual Environments](chapter-03-venv.md)

## Creating a Project

```bash
uv init my-project
cd my-project
```

Output:

```
Initialized project `my-project` at `/home/user/my-project`
```

This creates:

```
my-project/
├── .python-version
├── pyproject.toml
├── README.md
└── src/
    └── my_project/
        └── __init__.py
```

### Project types

```bash
# Application (default)
uv init my-app

# Library — installable, includes build system
uv init --lib my-lib

# Script — minimal, single file
uv init --script hello.py
```

## pyproject.toml Structure

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "My awesome project"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "requests>=2.31.0",
    "flask>=3.0.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.4.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## Adding Dependencies

```bash
# Add a package
uv add requests

# Add with version constraint
uv add "flask>=3.0"

# Add multiple packages
uv add requests flask sqlalchemy
```

Output:

```
Resolved 8 packages in 12ms
Installed 8 packages in 45ms
 + flask==3.0.3
 + requests==2.31.0
```

Compare with pip:

```bash
# pip (manual, no lockfile)
pip install requests
echo "requests" >> requirements.txt

# uv (automatic, updates pyproject.toml + lockfile)
uv add requests
```

## Removing Dependencies

```bash
uv remove flask
```

## Syncing (Install All Dependencies)

```bash
uv sync
```

Reads `uv.lock` and installs exactly what is specified — deterministic and fast.

```bash
# Include dev dependencies (default)
uv sync

# Production only
uv sync --no-dev

# Include specific groups
uv sync --group test --group docs
```

## The Lockfile: uv.lock

```bash
uv lock
```

`uv.lock` is a cross-platform lockfile that pins every transitive dependency with exact versions and hashes.

- **Human-readable** (TOML format)
- **Cross-platform** — contains resolution for all platforms
- **Deterministic** — same input always produces same output
- **Git-friendly** — commit to version control

Example snippet:

```toml
[[package]]
name = "requests"
version = "2.31.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "certifi" },
    { name = "charset-normalizer" },
    { name = "idna" },
    { name = "urllib3" },
]
```

### Updating locked versions

```bash
# Update all packages
uv lock --upgrade

# Update a specific package
uv lock --upgrade-package requests
```

## Dependency Groups

Organize dependencies by purpose:

```toml
[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.4.0",
    "mypy>=1.10",
]
test = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "hypothesis>=6.0",
]
docs = [
    "sphinx>=7.0",
    "sphinx-rtd-theme>=2.0",
]
```

```bash
# Add to a specific group
uv add --group dev ruff
uv add --group test pytest-cov

# Sync with specific groups
uv sync --group dev --group test

# Run with a group
uv run --group test pytest
```

Compare with poetry:

```bash
# poetry
poetry add --group dev pytest

# uv
uv add --group dev pytest
```

## Useful Commands

```bash
# Show dependency tree
uv tree

# Check lockfile is up to date
uv lock --check

# Export to requirements.txt (for legacy tools)
uv export --format requirements-txt > requirements.txt
```

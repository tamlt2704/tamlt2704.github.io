# Chapter 56: uv — Modern Python Package & Project Management

## What you'll learn

- What uv is and why it replaces pip, pip-tools, virtualenv, pyenv, and poetry
- Installing Python versions with uv
- Creating and managing projects
- Dependency management (add, remove, lock, sync)
- Virtual environments (automatic, no manual activation needed)
- Running scripts and tools
- Publishing packages
- Migrating from pip/poetry to uv

---

## PART 1: What is uv?

## 56.1 The problem uv solves

```
THE OLD PYTHON TOOLING MESS:

  Need to...                   Tool(s) required
  ─────────────────────────────────────────────────
  Install Python versions      pyenv / deadsnakes PPA / download manually
  Create virtual environments  venv / virtualenv / conda
  Install packages             pip
  Lock dependencies            pip-tools / pip freeze > requirements.txt
  Manage project metadata      setup.py / setup.cfg / pyproject.toml
  Dependency resolution        pip (slow, sometimes broken)
  Run scripts                  python / python3 (which one? where?)
  Publish to PyPI              twine / build
  All of the above coherently  poetry / pdm / hatch (each with tradeoffs)

UV REPLACES ALL OF THEM WITH ONE TOOL:
  uv python install 3.12       ← install Python
  uv init                      ← create project
  uv add requests              ← add dependency (+ resolve + lock + install)
  uv run main.py               ← run script (auto-creates venv if needed)
  uv build                     ← build package
  uv publish                   ← publish to PyPI

10-100× FASTER than pip (written in Rust).
```

## 56.2 Install uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip (if you have Python already)
pip install uv

# Or with Homebrew
brew install uv

# Verify
uv --version
```

## 56.3 uv vs other tools

| Feature | pip | poetry | uv |
|---------|-----|--------|-----|
| Install packages | ✅ (slow) | ✅ | ✅ (10-100× faster) |
| Lock file | ❌ (need pip-tools) | ✅ | ✅ |
| Dependency resolution | Basic | Good | Excellent (Rust resolver) |
| Virtual env management | Manual | Automatic | Automatic |
| Install Python versions | ❌ (need pyenv) | ❌ | ✅ |
| Run scripts | ❌ | ✅ `poetry run` | ✅ `uv run` |
| Build packages | ❌ (need build) | ✅ | ✅ |
| Publish to PyPI | ❌ (need twine) | ✅ | ✅ |
| Speed | Baseline | 2-3× pip | 10-100× pip |
| Written in | Python | Python | Rust |
| Single binary | ❌ | ❌ | ✅ (no Python needed to install uv) |

---

## PART 2: Python Version Management

## 56.4 Install and manage Python versions

```bash
# List available Python versions
uv python list

# Install a specific version
uv python install 3.12
uv python install 3.11
uv python install 3.13

# Install multiple
uv python install 3.11 3.12 3.13

# See installed versions
uv python list --only-installed

# Pin a project to a specific version
uv python pin 3.12
# Creates .python-version file (same format as pyenv)

# Use a specific version for a command
uv run --python 3.11 script.py
```

**No pyenv needed!** uv downloads and manages Python installations directly. They're stored in `~/.local/share/uv/python/`.

---

## PART 3: Project Management

## 56.5 Create a new project

```bash
# Create a new project (application)
uv init my-project
cd my-project

# Or create a library
uv init my-library --lib

# What you get:
my-project/
├── pyproject.toml    ← project metadata + dependencies
├── README.md
├── .python-version   ← pinned Python version
└── src/
    └── my_project/
        └── __init__.py
```

## 56.6 pyproject.toml (the single source of truth)

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "My awesome project"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.31.0",
    "pandas>=2.1.0",
    "fastapi>=0.109.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "ruff>=0.4.0",
    "mypy>=1.8.0",
]

[project.scripts]
my-cli = "my_project.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=8.0",
    "ruff>=0.4.0",
    "mypy>=1.8.0",
    "ipython>=8.0",
]
```

## 56.7 Dependency management

```bash
# Add a dependency
uv add requests
uv add "pandas>=2.1"
uv add fastapi uvicorn

# Add a dev dependency (not shipped with your package)
uv add --dev pytest ruff mypy

# Add an optional dependency group
uv add --group ml scikit-learn torch

# Remove a dependency
uv remove pandas

# Update a specific package
uv lock --upgrade-package requests

# Update all dependencies to latest compatible versions
uv lock --upgrade

# Install all dependencies (from lock file → deterministic)
uv sync

# Install including dev dependencies
uv sync --dev

# Install specific group
uv sync --group ml
```

## 56.8 The lock file (uv.lock)

```bash
# uv.lock is auto-generated when you run uv add / uv lock
# It pins EXACT versions of every package + transitive dependency
# Commit this to git! (like package-lock.json)

# Recreate from pyproject.toml (if lock is outdated)
uv lock

# Install exactly what's in the lock file (deterministic builds)
uv sync
```

**Why lock files matter:**
```
pyproject.toml says: requests>=2.31.0
uv.lock pins:       requests==2.32.3, urllib3==2.2.1, charset-normalizer==3.3.2, ...

Without lock: "works on my machine" (different versions on CI vs dev vs prod)
With lock:    EVERYONE gets exactly the same versions. Always.
```

---

## PART 4: Virtual Environments

## 56.9 Automatic virtual environments

```bash
# uv creates .venv automatically when needed — no manual setup!

uv run python -c "import sys; print(sys.prefix)"
# .venv is created automatically on first `uv run`

# The .venv is in your project directory:
my-project/
├── .venv/          ← created automatically by uv
├── pyproject.toml
├── uv.lock
└── src/

# You generally DON'T need to activate it. Just use `uv run`:
uv run python script.py      # runs in the venv
uv run pytest                # runs pytest from the venv
uv run ruff check .          # runs ruff from the venv

# But if you want to activate (for IDE compatibility):
source .venv/bin/activate    # Linux/Mac
.venv\Scripts\activate       # Windows
```

**Key insight:** With uv, you almost never manually create or activate virtual environments. `uv run` handles it. `uv sync` installs into it. Your IDE auto-detects `.venv/`.

## 56.10 Multiple Python versions in one project

```bash
# Test against multiple Python versions
uv run --python 3.11 pytest
uv run --python 3.12 pytest
uv run --python 3.13 pytest

# Create a venv with a specific Python
uv venv --python 3.11 .venv-311
uv venv --python 3.12 .venv-312
```

---

## PART 5: Running Things

## 56.11 Running scripts and commands

```bash
# Run a Python script
uv run python main.py

# Run a module
uv run python -m pytest
uv run python -m mypy src/

# Run a tool installed as dev dependency
uv run pytest
uv run ruff check .
uv run mypy src/
uv run ipython

# Run with extra packages (temporary — not added to project)
uv run --with rich python -c "from rich import print; print('[bold green]Hello![/]')"

# Run a one-off script with inline dependencies
uv run --script script.py
```

## 56.12 Inline script dependencies (PEP 723)

```python
# script.py
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests>=2.31",
#     "rich>=13.0",
# ]
# ///

import requests
from rich import print

response = requests.get("https://api.github.com/repos/astral-sh/uv")
data = response.json()
print(f"[bold green]uv[/] has [yellow]{data['stargazers_count']}[/] stars!")
```

```bash
# uv reads the dependencies from the script header and installs them!
uv run script.py
# No pyproject.toml needed. No requirements.txt. Just run it.
```

This is amazing for standalone scripts, automation, and one-off tasks.

## 56.13 Tools (global CLI utilities)

```bash
# Install a CLI tool globally (isolated from projects)
uv tool install ruff
uv tool install black
uv tool install httpie
uv tool install jupyter

# Run a tool without installing (like npx)
uvx ruff check .
uvx black --check .
uvx cowsay "Hello from uv!"

# List installed tools
uv tool list

# Update a tool
uv tool upgrade ruff

# Uninstall
uv tool uninstall black
```

`uvx` = "run this tool once without permanently installing it" (like `npx` for Python).

---

## PART 6: Common Workflows

## 56.14 Starting a new project from scratch

```bash
# 1. Create project
uv init my-api
cd my-api

# 2. Add dependencies
uv add fastapi uvicorn sqlalchemy asyncpg

# 3. Add dev tools
uv add --dev pytest httpx ruff mypy

# 4. Write code
mkdir -p src/my_api
cat > src/my_api/main.py << 'EOF'
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello from uv!"}
EOF

# 5. Run it
uv run uvicorn my_api.main:app --reload

# 6. Run tests
uv run pytest

# 7. Lint
uv run ruff check .
uv run mypy src/
```

## 56.15 CI/CD (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3

      - name: Install Python
        run: uv python install ${{ matrix.python-version }}

      - name: Install dependencies
        run: uv sync --dev

      - name: Lint
        run: uv run ruff check .

      - name: Type check
        run: uv run mypy src/

      - name: Test
        run: uv run pytest --cov

  publish:
    needs: test
    if: github.ref == 'refs/tags/v*'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv build
      - run: uv publish
        env:
          UV_PUBLISH_TOKEN: ${{ secrets.PYPI_TOKEN }}
```

## 56.16 Docker with uv

```dockerfile
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install dependencies (cached layer)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy source
COPY src/ ./src/

# Run
CMD ["uv", "run", "uvicorn", "my_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**`--frozen`:** Uses lock file exactly as-is (fails if lock is outdated — good for CI/Docker).

## 56.17 Migrating from pip/poetry

```bash
# From requirements.txt:
uv init
uv add $(cat requirements.txt | grep -v '^#' | grep -v '^$' | tr '\n' ' ')

# From poetry (pyproject.toml with [tool.poetry]):
# uv reads pyproject.toml directly — just run:
uv lock
uv sync
# May need to adjust [build-system] from poetry to hatchling

# From conda environment.yml:
# Extract packages, add with uv:
uv add numpy pandas scikit-learn matplotlib
```

---

## PART 7: Tips & Tricks

## 56.18 Speed comparison (real numbers)

```
Task: Install a fresh project with 50 dependencies

pip install -r requirements.txt:     ~45 seconds
poetry install:                      ~25 seconds
uv sync:                             ~2 seconds  (cold cache)
uv sync:                             ~0.3 seconds (warm cache)

That's not a typo. uv is 10-100× faster.
```

## 56.19 Useful commands cheat sheet

```bash
# Project
uv init project-name          # create new project
uv init --lib library-name    # create library
uv python pin 3.12            # set Python version

# Dependencies
uv add package                # add dependency
uv add --dev package          # add dev dependency
uv remove package             # remove
uv lock                       # resolve and lock all deps
uv lock --upgrade             # update everything
uv sync                       # install from lock file
uv sync --frozen              # strict install (CI/Docker)
uv tree                       # show dependency tree

# Running
uv run command                # run in project's venv
uv run --python 3.11 command  # specific Python version
uv run --with package command # temporary dependency
uvx tool-name                 # run tool without installing

# Tools (global)
uv tool install name          # install CLI tool globally
uv tool list                  # list installed tools
uvx name                      # run without installing

# Python
uv python install 3.12        # install Python version
uv python list                # list available versions
uv python pin 3.12            # pin for project

# Build & publish
uv build                      # build sdist + wheel
uv publish                    # upload to PyPI

# Info
uv version                    # uv version
uv self update                # update uv itself
```

## 56.20 IDE integration

```
VS Code:
  • uv creates .venv/ in project root
  • VS Code auto-detects it (Python extension)
  • If not: Cmd+Shift+P → "Python: Select Interpreter" → .venv

PyCharm:
  • Settings → Project → Python Interpreter
  • Add Interpreter → Existing → select .venv/bin/python
  • PyCharm recognises the venv automatically in most cases

Jupyter:
  uv add --dev ipykernel
  uv run python -m ipykernel install --user --name my-project
  # Now your project's venv appears as a Jupyter kernel
```

---

## Summary

✅ What uv replaces: pip, pip-tools, virtualenv, pyenv, poetry, twine — all in one tool
✅ Python management: install, list, pin versions (no pyenv needed)
✅ Project creation: `uv init` with pyproject.toml (standard PEP 621)
✅ Dependencies: add, remove, lock, sync (10-100× faster than pip)
✅ Virtual environments: automatic (created on first `uv run`, no manual activation needed)
✅ Running: `uv run` for scripts, `uvx` for one-off tools (like npx)
✅ Inline script deps: PEP 723 `# /// script` header — self-contained scripts
✅ CI/CD: GitHub Actions with `astral-sh/setup-uv`, matrix testing, publish
✅ Docker: `COPY --from=ghcr.io/astral-sh/uv:latest` + `uv sync --frozen`
✅ Migration: from pip (import requirements.txt), from poetry (just `uv lock`)

## Key takeaways

**uv is to Python what npm/cargo is to JavaScript/Rust.** One tool that handles everything: version management, dependencies, environments, running, building, publishing. Python finally has a coherent workflow.

**Speed matters more than you think.** When `uv sync` takes 0.3 seconds instead of 45 seconds, you run it after every change without thinking. When pip takes 45 seconds, you avoid it, let your environment drift, and hit "works on my machine" bugs.

**`uv run` is the new `python`.** Stop activating virtual environments. Stop wondering which Python you're using. `uv run` always uses the right Python with the right packages in the right venv. It just works.

**Commit uv.lock.** Just like package-lock.json. Everyone on the team, CI, Docker — all use exactly the same versions. No more "but it works on my machine."

---

→ [Back to Chapter 55: Mermaid Diagrams](./55-MERMAID-DIAGRAMS.md)

# Chapter 4: Python Versions — "I Need 3.12 Here and 3.9 There"

[← Chapter 3: Lockfile](chapter-03-lockfile.md) | [Chapter 5: uv run →](chapter-05-uv-run.md)

---

## The Problem

Omar: "The API needs 3.12 for the new `type` syntax. The ML pipeline needs 3.11 because torch doesn't support 3.12 yet. The legacy billing service is stuck on 3.9. I spent 2 hours yesterday compiling Python 3.9 with pyenv."

---

## uv python: Manage Python Installations

uv downloads pre-built Python binaries. No compilation. No pyenv. No system Python conflicts.

```bash
# List available Python versions
uv python list

# Install a specific version
uv python install 3.12

# Install multiple versions
uv python install 3.9 3.11 3.12

# See what's installed
uv python list --only-installed
```

Installation takes seconds (downloading a binary), not minutes (compiling from source).

---

## Pinning Python Version Per Project

```bash
# Pin this project to Python 3.12
uv python pin 3.12
```

This creates/updates `.python-version`:

```
3.12
```

Now `uv run`, `uv sync`, and `uv venv` all use Python 3.12 for this project — regardless of what's installed system-wide.

---

## requires-python in pyproject.toml

```toml
[project]
requires-python = ">=3.12"
```

This tells uv (and pip, and any PEP-compliant tool):
- This project needs Python 3.12 or higher
- Don't resolve packages that don't support 3.12+
- Fail early if someone tries to use 3.11

---

## Multiple Projects, Different Pythons

```
dataforge/
├── api/                    .python-version: 3.12
│   └── pyproject.toml      requires-python = ">=3.12"
├── ml-pipeline/            .python-version: 3.11
│   └── pyproject.toml      requires-python = ">=3.11,<3.12"
└── billing-legacy/         .python-version: 3.9
    └── pyproject.toml      requires-python = ">=3.9,<3.10"
```

Each project has its own `.python-version`. When you `cd` into a project and run `uv sync`, it uses the correct Python automatically.

```bash
cd api
uv sync          # uses Python 3.12
uv run python --version  # 3.12.x

cd ../ml-pipeline
uv sync          # uses Python 3.11
uv run python --version  # 3.11.x

cd ../billing-legacy
uv sync          # uses Python 3.9
uv run python --version  # 3.9.x
```

---

## Auto-Download

If the pinned Python version isn't installed, uv downloads it automatically:

```bash
cd ml-pipeline
uv sync
# Python 3.11 not found. Downloading...
# Downloaded cpython-3.11.8-linux-x86_64 in 2.1s
# Creating virtual environment...
# Installing dependencies...
# Done.
```

No manual `uv python install` needed. `uv sync` handles it.

---

## Where Python Gets Installed

```bash
# uv stores Python installations in a shared location
# Linux/macOS: ~/.local/share/uv/python/
# Windows: %APPDATA%\uv\python\

uv python dir
# Shows the installation directory

# Multiple projects can share the same Python installation
# (each gets its own .venv, but the interpreter is shared)
```

---

## Specifying Python for One Command

```bash
# Run with a specific Python version (ignoring .python-version)
uv run --python 3.11 python script.py

# Create a venv with a specific version
uv venv --python 3.12

# Sync with a specific version
uv sync --python 3.11
```

---

## Python Version in CI

```yaml
# .github/workflows/ci.yml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync --python ${{ matrix.python-version }}
      - run: uv run pytest
```

No `actions/setup-python` needed. uv handles Python installation.

---

## pyenv vs uv python

```
pyenv:                              uv python:
──────────────────────────────      ──────────────────────────────
Compiles from source (slow)         Downloads pre-built binary (fast)
Requires build dependencies         No build deps needed
Shims in PATH (fragile)             Direct path, no shims
Global/local version switching      Per-project .python-version
Separate tool to install/manage     Built into uv
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Command                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
uv python install 3.12          │ Download and install Python 3.12
uv python list                  │ Show available versions
uv python list --only-installed │ Show installed versions
uv python pin 3.12              │ Pin project to 3.12 (.python-version)
uv python dir                   │ Show where Pythons are stored
uv run --python 3.11 <cmd>      │ Run with specific version
uv sync --python 3.12           │ Sync with specific version
.python-version                 │ Per-project Python version file
requires-python = ">=3.12"      │ Minimum Python in pyproject.toml
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

You've been using `uv run` without thinking much about it. But it's more powerful than just "run a command in the venv." It can run scripts with inline dependencies, execute one-off commands without a project, and replace shell scripts.

---

[← Chapter 3: Lockfile](chapter-03-lockfile.md) | [Chapter 5: uv run →](chapter-05-uv-run.md)

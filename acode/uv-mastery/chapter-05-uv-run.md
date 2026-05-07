# Chapter 5: uv run — Scripts, One-Offs, and Inline Dependencies

[← Chapter 4: Python Versions](chapter-04-python-versions.md) | [Chapter 6: Dependency Groups →](chapter-06-groups.md)

---

## The Task

Nadia: "I have a one-off migration script. It needs `pandas` and `psycopg2`. I don't want to add them to the project's dependencies. I just want to run the script."

---

## Basic uv run

```bash
# Run a command in the project environment
uv run python main.py

# Run a module
uv run python -m pytest

# Run an installed script
uv run uvicorn app:main --reload

# Run with arguments
uv run python -c "import sys; print(sys.version)"
```

`uv run` automatically:
1. Finds the project (walks up to find `pyproject.toml`)
2. Creates/updates `.venv` if needed
3. Syncs dependencies if needed
4. Runs the command in that environment

---

## Inline Script Dependencies (PEP 723)

Run a script with its own dependencies — no project needed:

```python
# migrate.py
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pandas>=2.2.0",
#     "psycopg2-binary>=2.9.9",
#     "rich>=13.7.0",
# ]
# ///

import pandas as pd
import psycopg2
from rich.console import Console

console = Console()

def migrate():
    conn = psycopg2.connect("postgresql://localhost/dataforge")
    df = pd.read_sql("SELECT * FROM legacy_transactions", conn)
    console.print(f"[green]Migrating {len(df)} records...[/green]")
    # ... migration logic ...
    console.print("[bold green]Done![/bold green]")

if __name__ == "__main__":
    migrate()
```

```bash
# Run it — uv reads the inline metadata, installs deps in an isolated env, runs the script
uv run migrate.py

# No pyproject.toml needed. No venv to manage. Dependencies are in the script itself.
```

This is perfect for:
- One-off scripts
- Utility scripts shared via gist/slack
- Scripts that need different deps than the project

---

## Running Without a Project

```bash
# Run a command with ad-hoc dependencies (no project, no script metadata)
uv run --with pandas --with rich python -c "
import pandas as pd
from rich import print
print(pd.__version__)
"

# Run a package's CLI tool
uv run --with httpie http GET https://api.github.com

# Combine multiple --with flags
uv run --with requests --with beautifulsoup4 python scraper.py
```

---

## uv run vs. Activating the Venv

```bash
# Traditional workflow (don't do this):
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
deactivate

# uv workflow (do this):
uv run python main.py
# That's it. One command. No activation. No deactivation.
```

You CAN still activate the venv for IDE integration:
```bash
source .venv/bin/activate  # if your IDE needs it
```

But for running commands, `uv run` is always cleaner.

---

## Running Project Scripts

```toml
# pyproject.toml
[project.scripts]
dataforge-api = "dataforge_api.main:start"
dataforge-worker = "dataforge_api.worker:main"
dataforge-migrate = "dataforge_api.migrations:run"
```

```bash
uv run dataforge-api        # starts the API server
uv run dataforge-worker     # starts the background worker
uv run dataforge-migrate    # runs database migrations
```

---

## Running with Extra Groups

```bash
# Run pytest (which is in the 'test' group)
uv run --group test pytest

# Run with coverage
uv run --group test pytest --cov=dataforge_api

# Run ruff (which is in the 'dev' group)
uv run --group dev ruff check .

# Run mypy
uv run --group dev mypy src/
```

---

## Shebang Scripts

Make scripts directly executable:

```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["requests>=2.31.0"]
# ///

import requests

resp = requests.get("https://api.github.com/zen")
print(resp.text)
```

```bash
chmod +x zen.py
./zen.py
# Runs with uv, installs requests if needed, prints GitHub zen
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Command                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
uv run <command>                │ Run in project environment
uv run python script.py         │ Run a Python script
uv run --with <pkg> <cmd>       │ Run with ad-hoc dependency
uv run --group test pytest      │ Run with a specific dep group
uv run script.py (with PEP 723)│ Run script with inline deps
#!/usr/bin/env -S uv run        │ Shebang for executable scripts
# /// script ... # ///          │ Inline dependency metadata
[project.scripts]               │ Named entry points
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

You've been using `--group dev` and `--group test`. But how do groups interact? Can test deps see dev deps? What about groups that depend on other groups? And how does this map to Docker multi-stage builds?

---

[← Chapter 4: Python Versions](chapter-04-python-versions.md) | [Chapter 6: Dependency Groups →](chapter-06-groups.md)

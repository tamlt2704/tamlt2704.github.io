# Virtual Environments

[prev: Project Management](chapter-02-projects.md) | [next: Dependency Management](chapter-04-dependencies.md)

## Creating a Virtual Environment

```bash
# Create .venv in current directory
uv venv

# Specify Python version
uv venv --python 3.12

# Custom name
uv venv .my-env
```

Output:

```
Using CPython 3.12.7
Creating virtual environment at: .venv
Activate with: source .venv/bin/activate
```

Compare with traditional approach:

```bash
# Old way (3 tools)
pyenv install 3.12
pyenv local 3.12
python -m venv .venv

# uv (1 tool)
uv venv --python 3.12
```

## Activation

```bash
# Linux/macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (cmd)
.venv\Scripts\activate.bat
```

## uv run: Skip Activation Entirely

The recommended workflow — no activation needed:

```bash
# Run a Python script
uv run python app.py

# Run a module
uv run python -m pytest

# Run an installed CLI tool
uv run flask run

# Run with arguments
uv run python -c "import sys; print(sys.version)"
```

`uv run` automatically:

1. Creates a virtualenv if none exists
2. Syncs dependencies from `pyproject.toml`
3. Runs the command inside the virtualenv

## .python-version File

Pin the Python version for your project:

```bash
uv python pin 3.12
```

Creates `.python-version`:

```
3.12
```

Now all `uv` commands in this directory use Python 3.12 automatically.

## Per-Project Python Versions

Each project can use a different Python version:

```bash
cd project-a
uv python pin 3.11
uv sync  # uses Python 3.11

cd ../project-b
uv python pin 3.13
uv sync  # uses Python 3.13
```

No shims, no global state — just a file in each project directory.

## Inline Script Dependencies (PEP 723)

Run scripts with dependencies declared inline — no project setup needed:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests>=2.31",
#     "rich>=13.0",
# ]
# ///

import requests
from rich import print

response = requests.get("https://api.github.com/repos/astral-sh/uv")
data = response.json()
print(f"[bold]uv[/bold] has {data['stargazers_count']} stars!")
```

Run it:

```bash
uv run fetch_stars.py
```

Output:

```
Resolved 8 packages in 15ms
Installed 8 packages in 52ms
```

uv creates an ephemeral environment, installs dependencies, runs the script, done.

## Ephemeral Environments

Run one-off commands with temporary dependencies:

```bash
# Run with extra packages (not in your project)
uv run --with rich python -c "from rich import print; print('[bold]Hello![/bold]')"

# Run with a specific package version
uv run --with "requests==2.28.0" python -c "import requests; print(requests.__version__)"
```

These create temporary environments that are discarded after execution. Useful for:

- Quick experiments
- Running scripts that need different dependencies
- Testing compatibility with specific versions

# Migration Guide

[prev: Professional Workflows](chapter-06-workflows.md)

## From pip + requirements.txt

### Step 1: Initialize a project

```bash
uv init
```

### Step 2: Import existing requirements

```bash
# Add all packages from requirements.txt
uv add $(cat requirements.txt | grep -v "^#" | grep -v "^$" | tr '\n' ' ')

# Or one by one for complex files
uv add requests flask sqlalchemy
```

### Step 3: Remove old files

```bash
rm requirements.txt requirements-dev.txt
```

### Equivalents

| pip workflow                      | uv workflow                     |
| --------------------------------- | ------------------------------- |
| `python -m venv .venv`            | `uv venv`                       |
| `pip install -r requirements.txt` | `uv sync`                       |
| `pip install package`             | `uv add package`                |
| `pip freeze > requirements.txt`   | `uv lock` (automatic)           |
| `pip install -e .`                | `uv sync` (editable by default) |
| `pip list`                        | `uv tree`                       |

### Keep generating requirements.txt

If other tools still need it:

```bash
uv export --format requirements-txt > requirements.txt
```

## From Poetry

Poetry and uv both use `pyproject.toml`, making migration straightforward.

### Step 1: Remove poetry-specific sections

Replace `[tool.poetry.dependencies]` with standard `[project]` format:

Before (poetry):

```toml
[tool.poetry]
name = "my-project"
version = "0.1.0"

[tool.poetry.dependencies]
python = "^3.12"
requests = "^2.31"
flask = "^3.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0"
```

After (uv-compatible):

```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "requests>=2.31,<3.0",
    "flask>=3.0,<4.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Step 2: Generate lockfile

```bash
uv lock
```

### Step 3: Remove poetry artifacts

```bash
rm poetry.lock
# Remove [tool.poetry] sections from pyproject.toml
```

### Equivalents

| poetry command                  | uv command                  |
| ------------------------------- | --------------------------- |
| `poetry install`                | `uv sync`                   |
| `poetry add requests`           | `uv add requests`           |
| `poetry add --group dev pytest` | `uv add --group dev pytest` |
| `poetry remove flask`           | `uv remove flask`           |
| `poetry run python app.py`      | `uv run python app.py`      |
| `poetry lock`                   | `uv lock`                   |
| `poetry build`                  | `uv build`                  |
| `poetry publish`                | `uv publish`                |
| `poetry shell`                  | `uv run` (no shell needed)  |

## From Conda

### Step 1: Export conda packages

```bash
conda list --export > conda-packages.txt
```

### Step 2: Create uv project

```bash
uv init my-project
cd my-project
```

### Step 3: Add Python packages

Most conda packages have PyPI equivalents. Add them:

```bash
uv add numpy pandas scikit-learn matplotlib
```

### Packages without PyPI equivalents

Some conda packages (CUDA, system libraries) have no PyPI equivalent. For these:

- Use system package managers (apt, brew)
- Use Docker base images with required libraries
- Keep conda for system-level deps, use uv for Python packages

### Step 4: Pin Python version

```bash
uv python pin 3.12
```

### Step 5: Remove conda

```bash
conda deactivate
conda env remove -n my-env
```

## From pyenv + virtualenv

### Before (multiple tools)

```bash
# Install Python
pyenv install 3.12
pyenv local 3.12

# Create virtualenv
python -m venv .venv
source .venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### After (uv only)

```bash
# All in one tool
uv python install 3.12
uv python pin 3.12
uv init
uv add requests flask
uv run python app.py
```

Remove pyenv:

```bash
# Remove pyenv from shell config (.bashrc, .zshrc)
# Delete: export PYENV_ROOT="$HOME/.pyenv"
# Delete: eval "$(pyenv init -)"
rm -rf ~/.pyenv
```

## Common Gotchas

### 1. "Package not found" for conda-only packages

Some packages exist only on conda-forge, not PyPI. Check PyPI first:

```bash
uv add some-package  # will error if not on PyPI
```

### 2. Lockfile conflicts in teams

If multiple developers modify `uv.lock`:

```bash
# After resolving git conflicts in pyproject.toml
uv lock  # regenerate lockfile
```

### 3. System Python vs uv Python

uv manages its own Python installations. Your system Python is not affected:

```bash
# System Python (unchanged)
python --version  # whatever was there before

# uv Python
uv run python --version  # version from .python-version
```

### 4. Editable installs

uv installs your project in editable mode by default during `uv sync`. No need for `pip install -e .`.

### 5. Private registries

```toml
[[tool.uv.index]]
name = "private"
url = "https://my-registry.com/simple/"
```

```bash
# Authenticate
export UV_INDEX_PRIVATE_USERNAME=user
export UV_INDEX_PRIVATE_PASSWORD=token
```

## Performance Benchmarks

Typical results (cold cache, 50 dependencies):

| Operation         | pip | poetry | uv   |
| ----------------- | --- | ------ | ---- |
| Resolve + install | 45s | 38s    | 0.8s |
| Install from lock | 12s | 8s     | 0.3s |
| Add one package   | 8s  | 12s    | 0.2s |
| Create virtualenv | 3s  | 3s     | 0.1s |

With warm cache, uv operations are often under 100ms.

## Team Adoption Strategy

### Phase 1: Individual developer

1. Install uv
2. Use `uv run` and `uvx` alongside existing tools
3. Keep requirements.txt for compatibility

### Phase 2: Project migration

1. Run `uv init` in existing project
2. Add dependencies to `pyproject.toml`
3. Generate `uv.lock`
4. Update CI to use `uv sync --frozen`
5. Keep exporting requirements.txt if needed

### Phase 3: Full adoption

1. Remove requirements.txt, poetry.lock, Pipfile
2. Update documentation
3. Standardize on `uv run` for all commands
4. Use workspaces for monorepos

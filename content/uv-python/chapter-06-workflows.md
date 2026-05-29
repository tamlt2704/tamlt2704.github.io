# Professional Workflows

[prev: Scripts & Tools](chapter-05-scripts.md) | [next: Migration Guide](chapter-07-migration.md)

## CI/CD: GitHub Actions

```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3
        with:
          enable-cache: true

      - name: Install dependencies
        run: uv sync --frozen

      - name: Run tests
        run: uv run pytest

      - name: Lint
        run: uv run ruff check .
```

Key points:

- `--frozen` ensures the lockfile is not modified in CI (fails if out of date)
- `enable-cache: true` caches the uv cache directory between runs
- No need to install Python separately — uv handles it

### Matrix testing

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv python install ${{ matrix.python-version }}
      - run: uv sync --frozen
      - run: uv run pytest
```

## Docker: Multi-Stage Build

```dockerfile
# Build stage
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-editable

# Runtime stage
FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/

ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "-m", "my_app"]
```

Benefits:

- uv binary is only in the build stage (smaller final image)
- `--frozen` ensures reproducibility
- `--no-dev` excludes dev dependencies from production

### Minimal image with uv

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY src/ ./src/
CMD ["uv", "run", "python", "-m", "my_app"]
```

## Monorepo Setup (Workspaces)

For projects with multiple packages:

```
my-monorepo/
├── pyproject.toml          # root
├── uv.lock                 # single lockfile for all
├── packages/
│   ├── core/
│   │   ├── pyproject.toml
│   │   └── src/
│   ├── api/
│   │   ├── pyproject.toml
│   │   └── src/
│   └── cli/
│       ├── pyproject.toml
│       └── src/
```

Root `pyproject.toml`:

```toml
[project]
name = "my-monorepo"
version = "0.1.0"
requires-python = ">=3.12"

[tool.uv.workspace]
members = ["packages/*"]
```

Package `packages/api/pyproject.toml`:

```toml
[project]
name = "my-api"
version = "0.1.0"
dependencies = ["my-core"]

[tool.uv.sources]
my-core = { workspace = true }
```

```bash
# Sync all workspace members
uv sync

# Run in a specific package
uv run --package my-api python -m my_api
```

## Publishing Packages

### Build

```bash
uv build
```

Output:

```
Building source distribution...
Building wheel...
Successfully built dist/my-package-0.1.0.tar.gz
Successfully built dist/my_package-0.1.0-py3-none-any.whl
```

### Publish to PyPI

```bash
# Set token
export UV_PUBLISH_TOKEN=pypi-xxxxx

# Publish
uv publish
```

### Publish to private registry

```bash
uv publish --publish-url https://my-registry.com/simple/
```

## Reproducible Builds with Lockfile

The `uv.lock` file guarantees identical installs across machines:

```bash
# Developer machine
uv lock          # generate/update lockfile
git add uv.lock  # commit it

# CI / production
uv sync --frozen  # install exactly what's locked, fail if outdated
```

Compare with pip:

```bash
# pip (not reproducible without extra tooling)
pip freeze > requirements.txt
pip install -r requirements.txt

# uv (reproducible by default)
uv lock
uv sync --frozen
```

## Caching Strategies

uv caches downloaded packages and built wheels:

```bash
# Show cache location
uv cache dir

# Show cache size
uv cache info

# Clear cache
uv cache clean

# Clear cache for a specific package
uv cache clean requests
```

### CI caching

Cache the uv cache directory between CI runs:

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/uv
    key: uv-${{ runner.os }}-${{ hashFiles('uv.lock') }}
```

Or use the built-in caching in `setup-uv`:

```yaml
- uses: astral-sh/setup-uv@v3
  with:
    enable-cache: true
    cache-dependency-glob: "uv.lock"
```

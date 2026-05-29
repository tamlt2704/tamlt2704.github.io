# Dependency Management

[prev: Virtual Environments](chapter-03-venv.md) | [next: Scripts & Tools](chapter-05-scripts.md)

## Version Specifiers

uv uses standard PEP 440 version specifiers:

```bash
# Exact version
uv add "requests==2.31.0"

# Minimum version
uv add "requests>=2.31.0"

# Compatible release (>=2.31.0, <2.32.0)
uv add "requests~=2.31.0"

# Version range
uv add "requests>=2.28,<3.0"

# No constraint (latest)
uv add requests
```

Result in `pyproject.toml`:

```toml
[project]
dependencies = [
    "requests>=2.31.0",
    "flask~=3.0",
    "sqlalchemy>=2.0,<3.0",
]
```

## Extras

Install optional feature sets from packages:

```bash
# Single extra
uv add "httpx[http2]"

# Multiple extras
uv add "sqlalchemy[asyncio,postgresql]"

# FastAPI with all standard deps
uv add "fastapi[standard]"
```

## Optional Dependencies

Define optional features for your own package:

```toml
[project.optional-dependencies]
postgres = ["psycopg2>=2.9"]
redis = ["redis>=5.0"]
all = ["psycopg2>=2.9", "redis>=5.0"]
```

Users install with:

```bash
uv add "my-package[postgres]"
```

## Dependency Overrides

Force a specific version of a transitive dependency:

```toml
[tool.uv]
override-dependencies = [
    "urllib3>=2.0",
]
```

Useful when a transitive dependency has a security vulnerability or you need to force a newer version.

## Platform-Specific Dependencies

```toml
[project]
dependencies = [
    "pywin32>=306; sys_platform == 'win32'",
    "uvloop>=0.19; sys_platform != 'win32'",
    "numpy>=1.26; python_version >= '3.12'",
]
```

Environment markers supported:

- `sys_platform` — "win32", "linux", "darwin"
- `platform_machine` — "x86_64", "aarch64"
- `python_version` — "3.12", "3.13"
- `implementation_name` — "cpython", "pypy"

## Git Dependencies

```bash
# Default branch
uv add git+https://github.com/user/repo

# Specific branch
uv add git+https://github.com/user/repo@main

# Specific tag
uv add git+https://github.com/user/repo@v1.0.0

# Specific commit
uv add git+https://github.com/user/repo@abc1234
```

Result:

```toml
[project]
dependencies = [
    "my-lib @ git+https://github.com/user/repo@v1.0.0",
]
```

## Local Path Dependencies

```bash
# Editable (for development)
uv add --editable ../my-local-lib

# Non-editable
uv add ../my-local-lib
```

```toml
[tool.uv.sources]
my-lib = { path = "../my-local-lib", editable = true }
```

## Constraints

Constrain versions without adding them as direct dependencies:

```toml
[tool.uv]
constraint-dependencies = [
    "grpcio<1.60",
    "protobuf>=4.0,<5.0",
]
```

Constraints apply to the entire resolution — if any package pulls in `grpcio`, it will be constrained.

## Resolution Strategy

Control how uv picks versions:

```bash
# Default: highest compatible versions
uv lock --resolution highest

# Lowest compatible versions (test minimum bounds)
uv lock --resolution lowest

# Lowest direct, highest transitive
uv lock --resolution lowest-direct
```

Configure in `pyproject.toml`:

```toml
[tool.uv]
resolution = "lowest-direct"
```

### When to use lowest resolution

Testing that your minimum version bounds are correct in CI:

```bash
uv lock --resolution lowest
uv sync
uv run pytest
```

## Viewing Dependencies

```bash
# Show dependency tree
uv tree

# Show why a package is installed
uv tree --invert --package urllib3
```

Output:

```
my-project v0.1.0
├── flask v3.0.3
│   ├── click v8.1.7
│   ├── jinja2 v3.1.4
│   │   └── markupsafe v2.1.5
│   └── werkzeug v3.0.3
└── requests v2.31.0
    ├── certifi v2024.2.2
    ├── charset-normalizer v3.3.2
    ├── idna v3.7
    └── urllib3 v2.2.2
```

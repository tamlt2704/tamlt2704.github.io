# UV Mastery

Python dependency management at the speed of Rust. Migrate a 14-service monorepo (DataForge) from pip/poetry chaos to fast, reproducible builds with uv.

## Chapters

| # | Topic | Key Concepts |
|---|---|---|
| 00 | [Overview](chapter-00-overview.md) | Why uv, mental model, what it replaces |
| 01 | [First Project](chapter-01-first-project.md) | uv init, pyproject.toml, uv run, uv sync |
| 02 | [Adding Dependencies](chapter-02-adding-deps.md) | uv add, groups, constraints, extras, markers |
| 03 | [Lockfile & Sync](chapter-03-lockfile.md) | uv.lock, cross-platform resolution, hashes, --frozen |
| 04 | [Python Versions](chapter-04-python-versions.md) | uv python, .python-version, multi-version projects |
| 05 | [uv run](chapter-05-uv-run.md) | Inline scripts (PEP 723), --with, shebangs |
| 06 | [Dependency Groups](chapter-06-groups.md) | dev/test/docs groups, Docker multi-stage, include-group |
| 07 | [Platform-Specific Deps](chapter-07-platform-deps.md) | Markers, PyTorch CUDA, custom indexes, uv sources |
| 08 | [Workspaces](chapter-08-workspaces.md) | Monorepo, shared packages, single lockfile |
| 09 | Private Registries | Index config, authentication, Artifactory |
| 10 | Version Resolution | Constraints, overrides, conflict debugging |
| 11 | CLI Tools (uv tool) | uv tool install, global tools, pipx replacement |
| 12 | Docker Builds | Layer caching, multi-stage, minimal images |
| 13 | CI/CD | GitHub Actions, caching, --frozen, matrix |
| 14 | Migration | From pip/poetry/pipenv, compatibility |
| 15 | Build & Publish | uv build, uv publish, PyPI, wheels |

## Stack

- uv (Rust-based package manager)
- Python 3.9–3.12
- pyproject.toml (PEP 621)
- FastAPI, SQLAlchemy, PyTorch (example deps)
- Docker, GitHub Actions (deployment)

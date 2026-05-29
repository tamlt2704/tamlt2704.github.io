# uv: The Modern Python Package Manager

[next: Installation](chapter-01-install.md)

uv is a blazing-fast Python package manager and project tool written in Rust by Astral (the makers of Ruff). It replaces pip, pip-tools, virtualenv, pyenv, and poetry — all in a single binary.

## Why uv?

- **10-100x faster** than pip for package resolution and installation
- **Single tool** replaces an entire ecosystem of Python tooling
- **Drop-in compatible** with existing pyproject.toml and requirements.txt
- **Built-in Python version management** — no more pyenv
- **Deterministic lockfiles** for reproducible builds
- **Cross-platform** — works on Linux, macOS, and Windows

## Chapters

1. [Installation & Python Versions](chapter-01-install.md)
2. [Project Management](chapter-02-projects.md)
3. [Virtual Environments](chapter-03-venv.md)
4. [Dependency Management](chapter-04-dependencies.md)
5. [Scripts & Tools](chapter-05-scripts.md)
6. [Professional Workflows](chapter-06-workflows.md)
7. [Migration Guide](chapter-07-migration.md)

## Comparison Table

| Feature                   | uv   | pip    | poetry | conda    | pdm    |
| ------------------------- | ---- | ------ | ------ | -------- | ------ |
| Package install           | yes  | yes    | yes    | yes      | yes    |
| Dependency resolution     | yes  | yes    | yes    | yes      | yes    |
| Lockfile                  | yes  | no     | yes    | no       | yes    |
| Virtual env management    | yes  | no     | yes    | yes      | yes    |
| Python version management | yes  | no     | no     | yes      | no     |
| Script runner             | yes  | no     | yes    | no       | yes    |
| Global tool install       | yes  | no     | no     | no       | no     |
| Speed (relative)          | 100x | 1x     | 1x     | 1x       | 5x     |
| Written in                | Rust | Python | Python | Python/C | Python |
| Single binary             | yes  | no     | no     | no       | no     |
| PEP 723 inline deps       | yes  | no     | no     | no       | no     |
| Workspaces                | yes  | no     | no     | no       | no     |

## Quick Taste

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create a project
uv init my-project
cd my-project

# Add dependencies (installs in milliseconds)
uv add requests flask

# Run your code
uv run python app.py
```

No virtualenv activation, no pip install, no requirements.txt management — uv handles it all.

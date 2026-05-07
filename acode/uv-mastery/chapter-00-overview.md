# UV Mastery: Python Dependencies at the Speed of Rust

You just inherited **DataForge** — a data pipeline company with 14 Python services, 3 ML training jobs, and a monorepo that takes 8 minutes to install dependencies. The previous lead used pip, pipenv, poetry, and conda — sometimes in the same project. Virtual environments are scattered everywhere. The lockfile is 6 months stale. CI costs $400/month in compute time just waiting for `pip install`.

**Nadia**, the CTO, is done:

> "I don't care which tool you pick. I care that `install` takes seconds, not minutes. I care that what works on my laptop works in Docker. I care that new hires can set up in 5 minutes, not 2 hours. Fix the dependency mess."

**Omar**, the ML engineer, adds:

> "I need Python 3.11 for the API, Python 3.12 for the new ML pipeline, and Python 3.9 for that legacy service nobody wants to touch. And I need numpy, torch, and pandas to resolve without conflicts. Poetry takes 4 minutes to solve. I've started making coffee during installs."

You discover `uv` — a Python package manager written in Rust. It's a drop-in replacement for pip, pip-tools, pipenv, poetry, pyenv, and virtualenv. It's 10-100x faster. It resolves dependencies in milliseconds. It manages Python versions. It does everything.

Time to migrate the entire company to one tool.

---

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Platform Engineer | "One tool to rule them all." |
| **Nadia** | CTO | "If CI takes more than 2 minutes, we're wasting money." |
| **Omar** | ML Engineer | "I need torch 2.2 with CUDA 12.1. Don't break my GPU setup." |
| **The Intern** | New hire | "I ran `pip install` and now nothing works." |
| **The Lockfile** | requirements.txt | "I was generated 6 months ago. I contain vulnerabilities." |
| **The Resolver** | Dependency solver | "These 47 packages have conflicting numpy versions. Good luck." |

---

## The Stack

| Tool | What It Does |
|---|---|
| **uv** | Package manager, resolver, virtualenv, Python version manager |
| **pyproject.toml** | Project metadata and dependencies (PEP 621) |
| **uv.lock** | Deterministic lockfile (cross-platform) |
| **uv run** | Run commands in the project environment |
| **uv tool** | Install CLI tools globally (like pipx) |
| **uv python** | Manage Python installations |

---

## How to Read This

```
  🐍 Nadia or Omar needs a dependency/environment feature
   │
   ▼
  🤔 You learn the uv concept that enables it
   │
   ▼
  ⌨️  You configure it (with real commands)
   │
   ▼
  💥 Something breaks — version conflict, platform mismatch, CI failure
   │
   ▼
  🧠 You understand WHY and fix it properly
   │
   ▼
  🐍 Next feature
```

---

## The Roadmap

### Part 1: Foundations — "Replace pip"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Feature                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 01 │ Install uv, create a project           │ uv init, pyproject.toml, uv run
────┼────────────────────────────────────────┼──────────────────────────────────────
 02 │ "Add packages without breaking things" │ uv add, dependency groups, constraints
────┼────────────────────────────────────────┼──────────────────────────────────────
 03 │ "Lock it down — reproducible installs" │ uv.lock, uv sync, deterministic builds
────┼────────────────────────────────────────┼──────────────────────────────────────
 04 │ "I need Python 3.12 on this project"   │ uv python, version pinning, toolchains
────┼────────────────────────────────────────┼──────────────────────────────────────
 05 │ "Run scripts without activating envs"  │ uv run, inline scripts, shebangs
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 2: Real Projects — "Production Dependencies"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Feature                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 06 │ "Dev deps vs prod deps vs test deps"   │ Dependency groups, optional dependencies
────┼────────────────────────────────────────┼──────────────────────────────────────
 07 │ "Torch needs CUDA, but only on GPU"    │ Platform-specific deps, extras, markers
────┼────────────────────────────────────────┼──────────────────────────────────────
 08 │ "Monorepo with shared packages"        │ Workspaces, path dependencies
────┼────────────────────────────────────────┼──────────────────────────────────────
 09 │ "Private packages from our registry"   │ Index configuration, authentication
────┼────────────────────────────────────────┼──────────────────────────────────────
 10 │ "Pin everything — no surprises"        │ Version constraints, overrides, resolution
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 3: Workflows — "Developer Experience"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Feature                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 11 │ "Install CLI tools (ruff, black)"      │ uv tool install, tool management
────┼────────────────────────────────────────┼──────────────────────────────────────
 12 │ "Docker builds take forever"           │ Docker layer caching with uv, multi-stage
────┼────────────────────────────────────────┼──────────────────────────────────────
 13 │ "CI installs in 3 seconds"             │ CI caching, uv in GitHub Actions
────┼────────────────────────────────────────┼──────────────────────────────────────
 14 │ "Migrate from poetry/pip/pipenv"       │ Migration paths, compatibility
────┼────────────────────────────────────────┼──────────────────────────────────────
 15 │ "Build and publish a package"          │ uv build, uv publish, PyPI
────┴────────────────────────────────────────┴──────────────────────────────────────
```

---

## Why uv?

Nadia asks: "We already have poetry. Why switch?"

```
                    pip     poetry    conda     uv
                    ───     ──────    ─────     ──
Install speed       slow    slow      slow      ⚡ 10-100x faster
Dependency resolve  basic   good      good      ⚡ milliseconds
Lockfile            no*     yes       yes       yes (cross-platform)
Python management   no      no        yes       yes
Virtual envs        manual  auto      auto      auto
Monorepo support    no      no        no        yes (workspaces)
Reproducible        no      mostly    no        yes (deterministic)
Drop-in for pip     yes     no        no        yes
Written in          Python  Python    Python/C  Rust

* pip-tools adds lockfiles to pip
```

The speed difference is not marginal — it's transformative:

```bash
# Poetry: resolve + install a fresh environment
$ time poetry install
real    2m47s

# uv: same project, same dependencies
$ time uv sync
real    0.8s
```

---

## The Mental Model

```
┌─────────────────────────────────────────────────────────────────┐
│                          uv Workflow                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  pyproject.toml                                                   │
│  (what you WANT — loose version specs)                            │
│       │                                                           │
│       │  uv lock                                                  │
│       ▼                                                           │
│  uv.lock                                                          │
│  (what you GET — exact pinned versions, all platforms)            │
│       │                                                           │
│       │  uv sync                                                  │
│       ▼                                                           │
│  .venv/                                                           │
│  (installed packages — matches lockfile exactly)                  │
│       │                                                           │
│       │  uv run                                                   │
│       ▼                                                           │
│  Your code runs with correct dependencies                         │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────────────────┐
│                    What uv Replaces                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  pip install           →  uv add / uv pip install                 │
│  pip freeze            →  uv lock (better — cross-platform)       │
│  python -m venv        →  uv venv (automatic)                     │
│  pyenv                 →  uv python install                       │
│  pipx                  →  uv tool install                         │
│  pip-tools (compile)   →  uv lock                                 │
│  poetry                →  uv (full replacement)                   │
│  pipenv                →  uv (full replacement)                   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### Install uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip (if you must)
pip install uv

# Or with Homebrew
brew install uv
```

### Verify

```bash
uv --version
# uv 0.5.x

uv python list
# Shows available Python versions
```

That's it. No Python required to install uv (it's a standalone Rust binary). uv will download Python for you if needed.

---

## Key Concepts (Preview)

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ One-Line Explanation
────────────────────────────────┼──────────────────────────────────────
pyproject.toml                  │ Project metadata + dependency specs
uv.lock                         │ Exact versions for all platforms (committed to git)
uv add                          │ Add a dependency (updates pyproject.toml + lockfile)
uv sync                         │ Install exactly what's in the lockfile
uv run                          │ Run a command in the project environment
uv python                       │ Install/manage Python versions
uv tool                         │ Install CLI tools (ruff, black, mypy)
Dependency group                │ Named set of deps (dev, test, docs)
Workspace                       │ Monorepo with multiple packages
────────────────────────────────┴──────────────────────────────────────
```

---

[Next: Chapter 1 — Your First uv Project →](chapter-01-first-project.md)

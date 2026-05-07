# Chapter 3: The Lockfile — Reproducible Installs

[← Chapter 2: Adding Dependencies](chapter-02-adding-deps.md) | [Chapter 4: Python Versions →](chapter-04-python-versions.md)

---

## The Problem

The intern cloned the repo, ran `pip install -r requirements.txt`, and got different versions than everyone else. A test passes on your machine but fails on CI. Omar's ML pipeline produces different results after a fresh install because numpy silently upgraded.

Nadia: "I want byte-for-byte identical environments. Same versions. Same hashes. Every machine. Every time."

---

## What Is uv.lock?

`uv.lock` is a **cross-platform lockfile** that records:
- Exact version of every package (direct + transitive)
- Source URL and hash for every wheel/sdist
- Platform-specific resolution (what to install on Linux vs macOS vs Windows)
- Python version compatibility markers

```bash
# Generate/update the lockfile
uv lock

# Install exactly what's in the lockfile
uv sync
```

---

## Lockfile vs. pyproject.toml

```
pyproject.toml (what you WANT):     uv.lock (what you GET):
──────────────────────────────      ──────────────────────────────
"fastapi>=0.109.0"                  fastapi==0.109.2
"sqlalchemy>=2.0"                   sqlalchemy==2.0.25
(no mention of starlette)           starlette==0.36.3 (transitive)
(no mention of anyio)               anyio==4.2.0 (transitive)
(no hashes)                         sha256:abc123... (verified)
```

- `pyproject.toml` = intent (loose specs, human-edited)
- `uv.lock` = reality (exact versions, machine-generated)

---

## Cross-Platform Resolution

Unlike poetry.lock or pip-tools output, `uv.lock` resolves for ALL platforms simultaneously:

```toml
# uv.lock (simplified)
[[package]]
name = "uvloop"
version = "0.19.0"
source = { registry = "https://pypi.org/simple" }

# Only installed on non-Windows
[package.resolution-markers]
markers = "sys_platform != 'win32'"

[[package]]
name = "winloop"
version = "0.1.1"
source = { registry = "https://pypi.org/simple" }

[package.resolution-markers]
markers = "sys_platform == 'win32'"
```

This means:
- Developer on macOS: gets `uvloop`
- Developer on Windows: gets `winloop`
- Both from the SAME lockfile
- No "it works on my machine" problems

---

## uv sync: The Install Command

```bash
# Install everything in the lockfile
uv sync

# Install without dev/test groups (production)
uv sync --no-group dev --no-group test

# Install and remove packages not in the lockfile (clean env)
uv sync --exact

# Verify lockfile matches pyproject.toml (CI check)
uv lock --check
# Exit code 0 = lockfile is up to date
# Exit code 1 = lockfile is stale (someone edited pyproject.toml without running uv lock)
```

---

## The Workflow

### Day-to-day development:

```bash
# Add a new package
uv add httpx
# → updates pyproject.toml
# → re-resolves (updates uv.lock)
# → installs into .venv

# Commit both files
git add pyproject.toml uv.lock
git commit -m "add httpx for external API calls"
```

### Pulling changes:

```bash
git pull
uv sync   # install whatever changed in the lockfile
```

### CI:

```bash
uv sync --frozen  # install from lockfile, FAIL if lockfile is stale
# --frozen means: don't update the lockfile, just install it
# If pyproject.toml and uv.lock are out of sync, this fails (catches mistakes)
```

---

## Hash Verification

uv.lock includes content hashes for every package:

```toml
[[package]]
name = "pydantic"
version = "2.6.1"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "...", hash = "sha256:4fd5c182a2488dc63e6d32737ff19937888001e2a6d86e94b3f233104a5d1fa9" }
wheels = [
    { url = "...", hash = "sha256:0b6a909df3b3e5e3f24e..." },
]
```

If a package is tampered with (supply chain attack), the hash won't match and installation fails. This is automatic — you don't configure it.

---

## Lockfile Conflicts in Git

When two developers add different packages, `uv.lock` will conflict in git. The fix:

```bash
# After resolving the conflict in pyproject.toml:
git checkout --theirs uv.lock  # or --ours, doesn't matter
uv lock                         # regenerate from merged pyproject.toml
git add uv.lock
git commit
```

Don't try to manually merge `uv.lock`. Just regenerate it.

---

## Frozen Installs (CI Safety)

```bash
# In CI, use --frozen to catch stale lockfiles
uv sync --frozen

# This fails if:
# - pyproject.toml has deps not in uv.lock
# - uv.lock doesn't exist
# - lockfile is out of date

# Equivalent to: "install exactly this, don't think about it"
```

---

## Comparing: Lock Strategies

```
Tool          │ Lockfile          │ Cross-platform │ Hashes │ Speed
──────────────┼───────────────────┼────────────────┼────────┼──────
pip freeze    │ requirements.txt  │ ❌ (one platform)│ manual │ slow
pip-tools     │ requirements.txt  │ ❌              │ optional│ slow
poetry        │ poetry.lock       │ ⚠️ (mostly)     │ yes    │ slow
pipenv        │ Pipfile.lock      │ ⚠️ (mostly)     │ yes    │ slow
uv            │ uv.lock           │ ✅ (all at once) │ yes    │ ⚡ fast
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Command                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
uv lock                         │ Resolve and write uv.lock
uv sync                         │ Install from lockfile into .venv
uv sync --frozen                │ Install from lockfile, fail if stale
uv sync --exact                 │ Remove packages not in lockfile
uv lock --check                 │ Verify lockfile matches pyproject.toml
uv lock --upgrade               │ Upgrade all to latest compatible
uv lock --upgrade-package X     │ Upgrade one package
Commit uv.lock to git           │ Ensures reproducible installs
Don't edit uv.lock by hand      │ Always regenerate with uv lock
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The lockfile pins package versions. But what about Python itself? Omar needs 3.12 for the API, 3.11 for the ML pipeline, and 3.9 for the legacy service. With pyenv, that's 20 minutes of compilation. With uv, it's one command.

---

[← Chapter 2: Adding Dependencies](chapter-02-adding-deps.md) | [Chapter 4: Python Versions →](chapter-04-python-versions.md)

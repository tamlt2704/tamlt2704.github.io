# Chapter 7: Platform-Specific Dependencies — "Torch Needs CUDA, But Only on GPU"

[← Chapter 6: Dependency Groups](chapter-06-groups.md) | [Chapter 8: Workspaces →](chapter-08-workspaces.md)

---

## The Problem

Omar: "I need `torch` with CUDA 12.1 on our GPU training servers (Linux). On my MacBook, I need CPU-only torch. And `uvloop` doesn't exist on Windows — the intern keeps getting install errors."

---

## Environment Markers

Python's dependency specification supports markers — conditions that determine whether a dependency is installed:

```toml
[project]
dependencies = [
    "fastapi>=0.109.0",

    # Only on Linux/macOS (uvloop doesn't support Windows)
    "uvloop>=0.19.0; sys_platform != 'win32'",

    # Windows alternative
    "winloop>=0.1.0; sys_platform == 'win32'",

    # Only needed on older Python
    "typing-extensions>=4.9.0; python_version < '3.12'",
]
```

### Available Markers

```
sys_platform        │ "linux", "darwin", "win32"
platform_machine    │ "x86_64", "arm64", "aarch64"
platform_system     │ "Linux", "Darwin", "Windows"
python_version      │ "3.11", "3.12"
implementation_name │ "cpython", "pypy"
os_name             │ "posix", "nt"
```

### Combining Markers

```toml
# Linux x86_64 only
"nvidia-cuda-runtime>=12.1; sys_platform == 'linux' and platform_machine == 'x86_64'"

# macOS ARM only
"tensorflow-macos>=2.15; sys_platform == 'darwin' and platform_machine == 'arm64'"
```

---

## PyTorch: The Hard Case

PyTorch distributes different wheels for CPU vs CUDA. They use a custom index (not PyPI):

```toml
# pyproject.toml
[project]
dependencies = [
    "torch>=2.2.0",
    "torchvision>=0.17.0",
]

[tool.uv]
# Use PyTorch's index for CUDA builds
[[tool.uv.index]]
name = "pytorch-cu121"
url = "https://download.pytorch.org/whl/cu121"
explicit = true  # only use for packages explicitly assigned

[tool.uv.sources]
# Get torch from the CUDA index on Linux, default (CPU) elsewhere
torch = [
    { index = "pytorch-cu121", marker = "sys_platform == 'linux'" },
]
torchvision = [
    { index = "pytorch-cu121", marker = "sys_platform == 'linux'" },
]
```

Now:
- Linux machines get CUDA-enabled torch from PyTorch's index
- macOS/Windows get CPU torch from PyPI

---

## Platform-Specific Extras

```toml
[project.optional-dependencies]
gpu = [
    "torch[cuda]>=2.2.0; sys_platform == 'linux'",
    "nvidia-cuda-runtime>=12.1; sys_platform == 'linux'",
]
cpu = [
    "torch>=2.2.0",
]
```

```bash
# On GPU server
uv sync --extra gpu

# On laptop
uv sync --extra cpu
```

---

## How uv.lock Handles Platforms

The lockfile resolves for ALL platforms simultaneously. It records which packages go where:

```toml
# uv.lock (simplified)
[[package]]
name = "uvloop"
version = "0.19.0"
resolution-markers = ["sys_platform != 'win32'"]
# Only installed on non-Windows

[[package]]
name = "torch"
version = "2.2.0+cu121"
source = { url = "https://download.pytorch.org/whl/cu121/torch-2.2.0..." }
resolution-markers = ["sys_platform == 'linux'"]

[[package]]
name = "torch"
version = "2.2.0"
source = { registry = "https://pypi.org/simple" }
resolution-markers = ["sys_platform != 'linux'"]
```

One lockfile. All platforms. Deterministic everywhere.

---

## Conflicting Platform Dependencies

Sometimes packages have different version requirements per platform:

```toml
[tool.uv]
# Override numpy version for specific platforms
override-dependencies = [
    # ARM macOS needs newer numpy
    "numpy>=1.26.0; sys_platform == 'darwin' and platform_machine == 'arm64'",
    # Linux can use older numpy (for torch compatibility)
    "numpy>=1.24.0,<1.27; sys_platform == 'linux'",
]
```

---

## Practical: ML Pipeline Configuration

```toml
# ml-pipeline/pyproject.toml
[project]
name = "dataforge-ml"
version = "0.1.0"
requires-python = ">=3.11,<3.13"
dependencies = [
    "numpy>=1.26.0",
    "pandas>=2.2.0",
    "scikit-learn>=1.4.0",
    "structlog>=24.1.0",
]

[project.optional-dependencies]
gpu = [
    "torch>=2.2.0",
    "torchvision>=0.17.0",
]
cpu = [
    "torch>=2.2.0",
    "torchvision>=0.17.0",
]

[dependency-groups]
dev = [
    "jupyter>=1.0.0",
    "matplotlib>=3.8.0",
    "ipython>=8.20.0",
]
test = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
]

[tool.uv]
[[tool.uv.index]]
name = "pytorch-cu121"
url = "https://download.pytorch.org/whl/cu121"
explicit = true

[tool.uv.sources]
torch = [
    { index = "pytorch-cu121", marker = "sys_platform == 'linux' and platform_machine == 'x86_64'" },
]
torchvision = [
    { index = "pytorch-cu121", marker = "sys_platform == 'linux' and platform_machine == 'x86_64'" },
]
```

```bash
# Developer laptop (macOS)
uv sync --extra cpu
# Gets CPU torch from PyPI

# GPU training server (Linux)
uv sync --extra gpu
# Gets CUDA torch from PyTorch index

# CI (Linux, no GPU)
uv sync --extra cpu --no-group dev
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
; sys_platform == 'linux'       │ Only install on Linux
; python_version >= '3.12'      │ Only for Python 3.12+
; platform_machine == 'arm64'   │ Only on ARM (Apple Silicon)
[[tool.uv.index]]               │ Custom package index
explicit = true                 │ Only use index for assigned packages
[tool.uv.sources]               │ Map packages to specific indexes
marker = "..."                  │ Conditional source selection
override-dependencies           │ Force versions for transitive deps
uv.lock resolves all platforms  │ One lockfile, works everywhere
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

DataForge has 14 services in a monorepo. They share a `dataforge-core` library. Right now, each service copies the library code. uv workspaces let you define multiple packages in one repo with shared dependencies.

---

[← Chapter 6: Dependency Groups](chapter-06-groups.md) | [Chapter 8: Workspaces →](chapter-08-workspaces.md)

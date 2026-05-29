# Scripts & Tools

[prev: Dependency Management](chapter-04-dependencies.md) | [next: Professional Workflows](chapter-06-workflows.md)

## Running Scripts

```bash
# Run a script in the project environment
uv run python app.py

# Run a module
uv run python -m pytest

# Run with arguments
uv run python train.py --epochs 10 --lr 0.001
```

`uv run` ensures the environment is synced before execution — if dependencies changed, they are installed automatically.

## Inline Script Metadata (PEP 723)

Declare dependencies directly in a script file:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests>=2.31",
#     "rich>=13.0",
# ]
# ///

import requests
from rich.console import Console

console = Console()
resp = requests.get("https://api.github.com/zen")
console.print(f"[bold green]{resp.text}[/bold green]")
```

Run it:

```bash
uv run zen.py
```

Output:

```
Resolved 8 packages in 11ms
Installed 8 packages in 38ms
Speak like a human.
```

No project setup, no virtualenv, no requirements file. The script is self-contained.

### Adding inline metadata to existing scripts

```bash
uv add --script myscript.py requests rich
```

This inserts the PEP 723 metadata block at the top of the file.

## uv tool install: Global CLI Tools

Install Python CLI tools globally (like pipx):

```bash
# Install tools
uv tool install ruff
uv tool install black
uv tool install mypy
uv tool install httpie
uv tool install jupyter
```

Output:

```
Resolved 1 package in 8ms
Installed 1 package in 12ms
 + ruff==0.4.8
Installed 1 executable: ruff
```

Each tool gets its own isolated environment — no conflicts between tools.

### Managing installed tools

```bash
# List installed tools
uv tool list

# Upgrade a tool
uv tool upgrade ruff

# Upgrade all tools
uv tool upgrade --all

# Uninstall
uv tool uninstall black

# Show where tools are installed
uv tool dir
```

## uv tool run (uvx): Run Without Installing

Run a tool once without permanent installation:

```bash
# Run directly (downloads if needed, caches for reuse)
uvx ruff check .
uvx black --check .
uvx mypy src/

# Specific version
uvx ruff@0.4.0 check .
```

### When the command name differs from the package name

```bash
# Package is "httpie", command is "http"
uvx --from httpie http GET https://example.com

# Package is "jupyter", command is "jupyter-lab"
uvx --from jupyter jupyter-lab
```

## Replacing pipx Entirely

| pipx command          | uv equivalent            |
| --------------------- | ------------------------ |
| `pipx install ruff`   | `uv tool install ruff`   |
| `pipx run black .`    | `uvx black .`            |
| `pipx upgrade ruff`   | `uv tool upgrade ruff`   |
| `pipx uninstall ruff` | `uv tool uninstall ruff` |
| `pipx list`           | `uv tool list`           |
| `pipx upgrade-all`    | `uv tool upgrade --all`  |

Benefits over pipx:

- 10-100x faster installation
- Built-in Python management (no system Python dependency)
- Cached environments for `uvx` (instant re-runs)
- Part of the same tool you use for everything else

## Practical Examples

### Formatting and linting without installing

```bash
uvx black src/
uvx ruff check src/ --fix
uvx mypy src/
uvx pip-audit
```

### One-off data scripts

```python
# /// script
# dependencies = ["pandas", "matplotlib"]
# ///

import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data.csv")
df.plot(x="date", y="value")
plt.savefig("chart.png")
print("Chart saved!")
```

```bash
uv run plot.py
```

# Chapter 6: "Split Into Modules"

[← Chapter 5: Exceptions](chapter-05-exceptions.md) | [Chapter 7: Classes →](chapter-07-classes.md)

---

## The Task

Marcus: "800 lines in one file. Split it. I want to open `handlers/status.py` and see only the status command logic. Nothing else."

---

## Modules: One File = One Module

A Python file is a module. `bot.py` is the module `bot`. Import it with `import bot`.

```python
# math_utils.py
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

PI = 3.14159
```

```python
# main.py
import math_utils

result = math_utils.add(2, 3)       # 5
print(math_utils.PI)                 # 3.14159
```

### Import Styles

```python
# Import the module
import math_utils
math_utils.add(2, 3)

# Import specific names
from math_utils import add, PI
add(2, 3)

# Import with alias
import math_utils as mu
mu.add(2, 3)

# Import all (avoid — pollutes namespace)
from math_utils import *
```

**Rule**: Prefer `from module import specific_thing`. It's explicit about what you're using.

---

## Packages: Directories of Modules

A package is a directory with an `__init__.py` file:

```
pulsebot/
├── __init__.py          # makes this a package
├── config.py            # configuration loading
├── bot.py               # main loop
├── handlers/
│   ├── __init__.py
│   ├── help.py
│   ├── status.py
│   └── deploy.py
├── clients/
│   ├── __init__.py
│   └── slack.py
└── models/
    ├── __init__.py
    └── message.py
```

### __init__.py

Can be empty (just marks the directory as a package) or can define the package's public API:

```python
# pulsebot/handlers/__init__.py
from .help import cmd_help
from .status import cmd_status
from .deploy import cmd_deploy

__all__ = ["cmd_help", "cmd_status", "cmd_deploy"]
```

Now users can:

```python
from pulsebot.handlers import cmd_help, cmd_status
```

### Relative vs Absolute Imports

```python
# Inside pulsebot/handlers/status.py:

# Absolute import (from project root)
from pulsebot.clients.slack import SlackClient
from pulsebot.config import load_config

# Relative import (from current package)
from ..clients.slack import SlackClient  # go up one level
from . import help                        # same package
from .help import cmd_help               # specific name from sibling
```

**Rule**: Use absolute imports for clarity. Use relative imports within a package when it makes the code more readable.

---

## The Refactored Structure

```python
# pulsebot/config.py
import json
from pathlib import Path


def load_config(path: str = "config.json") -> dict:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    with open(config_path) as f:
        return json.load(f)
```

```python
# pulsebot/clients/slack.py
import requests


class SlackClient:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://slack.com/api"

    def fetch_messages(self, channel: str) -> list[dict]:
        resp = requests.get(
            f"{self.base_url}/conversations.history",
            headers={"Authorization": f"Bearer {self.token}"},
            params={"channel": channel},
        )
        resp.raise_for_status()
        return resp.json().get("messages", [])

    def send_message(self, channel: str, text: str) -> None:
        requests.post(
            f"{self.base_url}/chat.postMessage",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"channel": channel, "text": text},
        ).raise_for_status()
```

```python
# pulsebot/handlers/status.py
from pulsebot.clients.slack import SlackClient


def cmd_status(msg: dict, config: dict) -> str:
    """Check system status."""
    url = config.get("status_url", "https://api.example.com/status")
    try:
        import requests
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return f"✅ All systems operational: {data.get('status', 'ok')}"
    except Exception:
        return "⚠️ Status check failed. Try again later."
```

```python
# pulsebot/__main__.py — allows `python -m pulsebot`
from pulsebot.config import load_config
from pulsebot.bot import main_loop

if __name__ == "__main__":
    config = load_config()
    main_loop(config)
```

---

## if __name__ == "__main__"

```python
# utils.py
def helper():
    return "I help"

# This only runs when utils.py is executed directly,
# NOT when it's imported by another module
if __name__ == "__main__":
    print(helper())
    print("Running utils.py directly")
```

When you `import utils`, `__name__` is `"utils"`. When you `python utils.py`, `__name__` is `"__main__"`. This guard prevents code from running on import.

---

## Managing Dependencies

### Virtual Environments

```bash
# Create a virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate         # Windows

# Install packages (isolated from system Python)
pip install requests pytest

# Freeze dependencies
pip freeze > requirements.txt

# Install from requirements
pip install -r requirements.txt

# Deactivate
deactivate
```

### pyproject.toml (Modern Standard)

```toml
[project]
name = "pulsebot"
version = "1.0.0"
requires-python = ">=3.12"
dependencies = [
    "requests>=2.31.0",
    "click>=8.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "mypy>=1.0",
    "ruff>=0.1.0",
]

[project.scripts]
pulsebot = "pulsebot.__main__:main"
```

```bash
# Install the project in development mode
pip install -e ".[dev]"
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Is
────────────────────────────────┼──────────────────────────────────────
Module                          │ A single .py file
Package                         │ A directory with __init__.py
import module                   │ Access via module.name
from module import name         │ Direct access to name
from . import sibling           │ Relative import (same package)
from ..pkg import name          │ Relative import (parent package)
__init__.py                     │ Package initializer / public API
__name__ == "__main__"          │ Guard for direct execution
__all__ = [...]                 │ What `from pkg import *` exports
────────────────────────────────┼──────────────────────────────────────
python -m venv .venv            │ Create virtual environment
pip install -e ".[dev]"         │ Install project in dev mode
pyproject.toml                  │ Modern project configuration
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Leo: "The Slack client, the config, the message — these are all objects with behavior. Model them properly. Use classes."

---

[← Chapter 5: Exceptions](chapter-05-exceptions.md) | [Chapter 7: Classes →](chapter-07-classes.md)

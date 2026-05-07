# Chapter 8: "Add Type Safety"

[← Chapter 7: Classes](chapter-07-classes.md) | [Chapter 9: Testing →](chapter-09-testing.md)

---

## The Code Review

Marcus (remote, 3am his time, still reviewing PRs):

> "I'm reading `handle_message` and I have no idea what it returns. A string? A dict? None? Sometimes a list? I can't tell without reading every branch. Add type annotations everywhere. Use dataclasses. Make mypy happy. I'm not approving anything until the type checker passes."

---

## Type Hints: Documenting Contracts

```python
# ❌ What does this return? What's "msg"?
def handle_message(msg, config):
    if msg.get("type") == "command":
        return process_command(msg)
    return None

# ✅ Crystal clear
def handle_message(msg: dict[str, str], config: BotConfig) -> str | None:
    if msg.get("type") == "command":
        return process_command(msg)
    return None
```

### Basic Type Annotations

```python
# Variables
name: str = "PulseBot"
version: int = 3
debug: bool = False
threshold: float = 0.95

# Functions
def greet(user: str, channel: str = "#general") -> str:
    return f"Hello {user} in {channel}!"

# None return
def log_event(event: str) -> None:
    print(f"[EVENT] {event}")
```

---

## Collection Types

```python
# Lists
channels: list[str] = ["#support", "#engineering", "#random"]

# Dicts
config: dict[str, str] = {"token": "xoxb-...", "name": "PulseBot"}

# Tuples (fixed length, mixed types)
coordinate: tuple[float, float] = (40.7, -74.0)
record: tuple[str, int, bool] = ("ticket-42", 3, True)

# Sets
admins: set[str] = {"leo", "marcus", "rina"}

# Nested
handlers: dict[str, list[str]] = {
    "status": ["check_api", "check_db"],
    "deploy": ["run_tests", "push_image", "restart"],
}
```

---

## Optional and Union Types

```python
# A value that might be None
from typing import Optional

def find_user(user_id: str) -> Optional[str]:
    """Returns username or None if not found."""
    users = load_users()
    return users.get(user_id)

# Python 3.10+ syntax (preferred)
def find_user(user_id: str) -> str | None:
    users = load_users()
    return users.get(user_id)

# Union of multiple types
def parse_value(raw: str) -> int | float | str:
    try:
        return int(raw)
    except ValueError:
        try:
            return float(raw)
        except ValueError:
            return raw
```

---

## Dataclasses: Classes Without Boilerplate

Marcus: "Stop writing `__init__` by hand for data containers. Use dataclasses."

```python
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Ticket:
    title: str
    reporter: str
    priority: str = "medium"
    created_at: datetime = field(default_factory=datetime.now)
    tags: list[str] = field(default_factory=list)

# You get __init__, __repr__, __eq__ for free
ticket = Ticket(title="Bot crashes on Tuesday", reporter="leo")
print(ticket)
# Ticket(title='Bot crashes on Tuesday', reporter='leo', priority='medium', ...)

# Equality works
t1 = Ticket(title="Bug", reporter="rina")
t2 = Ticket(title="Bug", reporter="rina")
print(t1 == t2)  # True
```

### Frozen Dataclasses (Immutable)

```python
@dataclass(frozen=True)
class Event:
    """Immutable event — can be used as dict key or in sets."""
    type: str
    user: str
    timestamp: float

event = Event(type="message", user="leo", timestamp=1700000000.0)
event.type = "reaction"  # ❌ FrozenInstanceError!

# Can use as dict key because it's hashable
event_counts: dict[Event, int] = {event: 1}
```

### Post-Init Processing

```python
@dataclass
class Message:
    raw: dict
    text: str = field(init=False)
    user: str = field(init=False)
    command: str | None = field(init=False)

    def __post_init__(self):
        self.text = self.raw.get("text", "")
        self.user = self.raw.get("user", "unknown")
        words = self.text.strip().split()
        self.command = words[0].lower() if words else None
```

---

## TypedDict: Typing Dictionaries

When you work with JSON/API responses that have known keys:

```python
from typing import TypedDict, NotRequired


class SlackMessage(TypedDict):
    text: str
    user: str
    channel: str
    ts: str
    thread_ts: NotRequired[str]  # optional key


class BotConfig(TypedDict):
    token: str
    name: str
    channels: list[str]
    debug: NotRequired[bool]


def handle_message(msg: SlackMessage, config: BotConfig) -> str | None:
    # Now the types are clear — IDE autocompletes keys
    if msg["user"] in config.get("admins", []):
        return process_admin_command(msg["text"])
    return None
```

---

## Protocols: Structural Typing (Duck Typing with Types)

Marcus: "I don't want to force inheritance. If it has a `handle()` method, it's a handler."

```python
from typing import Protocol


class Handler(Protocol):
    """Any object with a handle() method satisfies this."""
    
    def handle(self, msg: dict) -> str | None: ...


class StatusHandler:
    def handle(self, msg: dict) -> str | None:
        return "✅ All systems go"


class DeployHandler:
    def handle(self, msg: dict) -> str | None:
        return "🚀 Deploying..."


# Both satisfy Handler without inheriting from it
def dispatch(handler: Handler, msg: dict) -> str | None:
    return handler.handle(msg)

dispatch(StatusHandler(), {"text": "status"})  # ✅ works
dispatch(DeployHandler(), {"text": "deploy"})  # ✅ works
dispatch("not a handler", {"text": "hi"})      # ❌ mypy error
```

### Protocol with Properties

```python
class Configurable(Protocol):
    @property
    def name(self) -> str: ...
    
    def reload(self) -> None: ...


class DatabaseConfig:
    name = "database"
    
    def reload(self) -> None:
        self._load_from_env()


def print_config(c: Configurable) -> None:
    print(f"Config: {c.name}")

print_config(DatabaseConfig())  # ✅ satisfies Protocol
```

---

## Callable Types

```python
from typing import Callable


# A function that takes a string and returns a string
Transformer = Callable[[str], str]

def apply_transforms(text: str, transforms: list[Transformer]) -> str:
    for fn in transforms:
        text = fn(text)
    return text

result = apply_transforms("  HELLO  ", [str.strip, str.lower])
# "hello"


# More complex callable
MessageHandler = Callable[[dict, dict], str | None]

def register_handler(command: str, handler: MessageHandler) -> None:
    registry[command] = handler
```

---

## Generics

```python
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T | None:
    """Return first item or None — works with any list type."""
    return items[0] if items else None

first(["a", "b"])   # type: str | None
first([1, 2, 3])    # type: int | None


# Bounded TypeVar
from typing import TypeVar
from dataclasses import dataclass

Numeric = TypeVar("Numeric", int, float)

def clamp(value: Numeric, low: Numeric, high: Numeric) -> Numeric:
    return max(low, min(value, high))

clamp(15, 0, 10)      # 10 (int)
clamp(3.7, 0.0, 1.0)  # 1.0 (float)
```

---

## Running mypy

```bash
# Install
pip install mypy

# Check a file
mypy bot.py

# Check the whole project
mypy src/

# Strict mode (recommended for new projects)
mypy --strict src/
```

### Common mypy Errors and Fixes

```python
# Error: Incompatible return value type (got "None", expected "str")
def get_name(user: dict) -> str:
    return user.get("name")  # ❌ .get() can return None

# Fix: handle the None case
def get_name(user: dict) -> str:
    return user.get("name", "anonymous")  # ✅


# Error: Item "None" of "Optional[str]" has no attribute "upper"
name: str | None = get_optional_name()
print(name.upper())  # ❌ might be None

# Fix: narrow the type
if name is not None:
    print(name.upper())  # ✅ mypy knows it's str here


# Error: Argument 1 has incompatible type "str"; expected "int"
def process(count: int) -> None: ...
process("5")  # ❌

# Fix: convert
process(int("5"))  # ✅
```

### pyproject.toml Configuration

```toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

# Per-module overrides (for third-party libs without stubs)
[[tool.mypy.overrides]]
module = "slack_sdk.*"
ignore_missing_imports = true
```

---

## The Annotated Bot

```python
from dataclasses import dataclass, field
from typing import Protocol
from datetime import datetime


class MessageHandler(Protocol):
    def handle(self, msg: "SlackMessage") -> str | None: ...
    def can_handle(self, command: str) -> bool: ...


@dataclass(frozen=True)
class SlackMessage:
    text: str
    user: str
    channel: str
    timestamp: float
    is_dm: bool = False

    @property
    def command(self) -> str | None:
        words = self.text.strip().split()
        return words[0].lower() if words else None


@dataclass
class Bot:
    name: str
    token: str
    handlers: dict[str, MessageHandler] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)

    def register(self, command: str, handler: MessageHandler) -> None:
        self.handlers[command] = handler

    def dispatch(self, msg: SlackMessage) -> str | None:
        command = msg.command
        if command is None:
            return None
        handler = self.handlers.get(command)
        if handler is None:
            return f"Unknown command: {command}"
        return handler.handle(msg)
```

Marcus: "Now I can read the code without running it. The types ARE the documentation."

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Annotation                      │ Meaning
────────────────────────────────┼──────────────────────────────────────
x: int                          │ Integer
x: str | None                   │ String or None
x: list[str]                    │ List of strings
x: dict[str, int]               │ Dict with str keys, int values
x: tuple[str, int]              │ Fixed-length tuple
Callable[[int], str]            │ Function (int) → str
────────────────────────────────┼──────────────────────────────────────
@dataclass                      │ Auto-generate __init__, __repr__, __eq__
@dataclass(frozen=True)         │ Immutable dataclass
field(default_factory=list)     │ Mutable default
────────────────────────────────┼──────────────────────────────────────
class X(Protocol):              │ Structural typing (duck typing)
TypeVar("T")                    │ Generic type variable
TypedDict                       │ Typed dictionary shape
────────────────────────────────┼──────────────────────────────────────
mypy --strict src/              │ Run type checker
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Leo, in standup: "The types are great. But we have zero tests. Nothing ships without tests. I want pytest, I want fixtures, I want coverage reports. If it's not tested, it doesn't work."

---

[← Chapter 7: Classes](chapter-07-classes.md) | [Chapter 9: Testing →](chapter-09-testing.md)

# Chapter 7: "Model the Domain"

[← Chapter 6: Modules](chapter-06-modules.md) | [Chapter 8: Type Hints →](chapter-08-type-hints.md)

---

## The Task

Leo: "The Slack client, the config, the message — these are all things with data AND behavior. A message has text, a sender, a timestamp, and it knows how to extract commands. Model them as classes."

---

## Classes: Data + Behavior

```python
class Message:
    """A Slack message with parsing capabilities."""
    
    def __init__(self, raw: dict):
        self.text = raw.get("text", "")
        self.user = raw.get("user", "unknown")
        self.channel = raw.get("channel", "")
        self.timestamp = raw.get("ts", "")
        self.is_dm = raw.get("channel_type") == "im"
    
    def extract_command(self) -> str | None:
        """Pull the first word as a command."""
        words = self.text.strip().split()
        return words[0].lower() if words else None
    
    def mentions_bot(self, bot_name: str) -> bool:
        """Check if this message mentions the bot."""
        return f"@{bot_name.lower()}" in self.text.lower()
    
    def __repr__(self) -> str:
        return f"Message(user={self.user!r}, text={self.text[:30]!r})"
```

### Using the Class

```python
raw = {"text": "status", "user": "leo", "channel": "#support", "ts": "123"}
msg = Message(raw)

print(msg.user)              # "leo"
print(msg.extract_command()) # "status"
print(msg.is_dm)             # False
print(msg)                   # Message(user='leo', text='status')
```

---

## __init__: The Constructor

```python
class SlackClient:
    def __init__(self, token: str, base_url: str = "https://slack.com/api"):
        self.token = token          # instance attribute
        self.base_url = base_url
        self._session = requests.Session()  # private by convention
        self._session.headers["Authorization"] = f"Bearer {token}"
    
    def fetch_messages(self, channel: str) -> list[dict]:
        resp = self._session.get(f"{self.base_url}/conversations.history",
                                  params={"channel": channel})
        resp.raise_for_status()
        return resp.json().get("messages", [])
```

- `self` is the instance being created/used
- `__init__` sets up the object's initial state
- Prefix with `_` for "private" (convention, not enforced)

---

## Properties: Controlled Access

```python
class Ticket:
    def __init__(self, title: str, priority: str = "medium"):
        self.title = title
        self._priority = priority
    
    @property
    def priority(self) -> str:
        return self._priority
    
    @priority.setter
    def priority(self, value: str) -> None:
        valid = ("low", "medium", "high", "critical")
        if value not in valid:
            raise ValueError(f"Priority must be one of {valid}")
        self._priority = value

ticket = Ticket("Bug report")
ticket.priority = "high"       # calls the setter
ticket.priority = "urgent"     # ValueError!
print(ticket.priority)         # calls the getter → "high"
```

---

## Inheritance: Shared Behavior

```python
class BaseHandler:
    """Base class for all command handlers."""
    
    def __init__(self, config: dict):
        self.config = config
    
    def can_execute(self, user: str) -> bool:
        """Override in subclasses for permission checks."""
        return True
    
    def execute(self, msg: Message) -> str:
        """Override in subclasses with actual logic."""
        raise NotImplementedError


class StatusHandler(BaseHandler):
    def execute(self, msg: Message) -> str:
        # ... check status
        return "✅ All systems operational"


class DeployHandler(BaseHandler):
    def can_execute(self, user: str) -> bool:
        return user in self.config.get("admins", [])
    
    def execute(self, msg: Message) -> str:
        return "🚀 Deployment triggered"
```

### When to Use Inheritance

| Use Inheritance | Use Composition |
|---|---|
| "Is-a" relationship (Dog is an Animal) | "Has-a" relationship (Car has an Engine) |
| Shared interface with different implementations | Combining capabilities |
| Framework requires it | Most other cases |

**Rule**: Prefer composition over inheritance. Python's duck typing means you rarely need deep hierarchies.

---

## Composition: Objects Containing Objects

```python
class Bot:
    """The main bot — composed of smaller pieces."""
    
    def __init__(self, config: dict):
        self.config = config
        self.client = SlackClient(config["token"])  # has-a client
        self.handlers = self._register_handlers()    # has-a handler registry
    
    def _register_handlers(self) -> dict[str, BaseHandler]:
        return {
            "status": StatusHandler(self.config),
            "deploy": DeployHandler(self.config),
        }
    
    def handle(self, raw_msg: dict) -> str | None:
        msg = Message(raw_msg)
        command = msg.extract_command()
        
        handler = self.handlers.get(command)
        if handler is None:
            return None
        if not handler.can_execute(msg.user):
            return "🔒 Permission denied"
        return handler.execute(msg)
```

---

## Dunder Methods: Customizing Behavior

```python
class Money:
    def __init__(self, cents: int):
        self.cents = cents
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Money(cents={self.cents})"
    
    def __str__(self) -> str:
        """User-friendly string."""
        return f"${self.cents / 100:.2f}"
    
    def __add__(self, other: "Money") -> "Money":
        return Money(self.cents + other.cents)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.cents == other.cents
    
    def __lt__(self, other: "Money") -> bool:
        return self.cents < other.cents
    
    def __bool__(self) -> bool:
        return self.cents != 0

price = Money(2999)
tax = Money(240)
total = price + tax      # Money(cents=3239)
print(total)             # $32.39
print(price == Money(2999))  # True
```

| Method | Triggered By |
|---|---|
| `__init__` | `MyClass()` |
| `__repr__` | `repr(obj)`, debugger |
| `__str__` | `str(obj)`, `print(obj)` |
| `__eq__` | `obj == other` |
| `__lt__`, `__gt__` | `obj < other`, sorting |
| `__add__` | `obj + other` |
| `__len__` | `len(obj)` |
| `__bool__` | `if obj:` |
| `__contains__` | `x in obj` |
| `__getitem__` | `obj[key]` |
| `__iter__` | `for x in obj:` |

---

## Class Methods and Static Methods

```python
class Config:
    def __init__(self, data: dict):
        self.data = data
    
    @classmethod
    def from_file(cls, path: str) -> "Config":
        """Alternative constructor — create from a file."""
        with open(path) as f:
            data = json.load(f)
        return cls(data)  # cls is the class itself
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create from environment variables."""
        return cls({
            "token": os.environ["SLACK_TOKEN"],
            "debug": os.environ.get("DEBUG", "false") == "true",
        })
    
    @staticmethod
    def validate(data: dict) -> bool:
        """Validate config structure (no instance needed)."""
        required = ["token", "channels"]
        return all(key in data for key in required)

# Usage
config = Config.from_file("config.json")
config = Config.from_env()
Config.validate({"token": "x"})  # False — missing "channels"
```

| Decorator | First Arg | Use For |
|---|---|---|
| (none) | `self` | Instance methods (most common) |
| `@classmethod` | `cls` | Alternative constructors, factory methods |
| `@staticmethod` | (none) | Utility functions that don't need instance/class |

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ Syntax
────────────────────────────────┼──────────────────────────────────────
Define a class                  │ class Name:
Constructor                     │ def __init__(self, ...):
Instance attribute              │ self.name = value
Instance method                 │ def method(self, ...):
Property                        │ @property + @name.setter
Inheritance                     │ class Child(Parent):
Class method                    │ @classmethod def from_x(cls, ...):
Static method                   │ @staticmethod def util(...):
String representation           │ __repr__, __str__
Operator overloading            │ __add__, __eq__, __lt__
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Marcus's review: "These classes have no type annotations. I can't tell what `handle()` returns without reading the implementation. Add types. Use dataclasses. Make mypy happy."

---

[← Chapter 6: Modules](chapter-06-modules.md) | [Chapter 8: Type Hints →](chapter-08-type-hints.md)

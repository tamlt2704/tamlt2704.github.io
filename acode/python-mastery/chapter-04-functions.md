# Chapter 4: "Break Up do_stuff()"

[← Chapter 3: Control Flow](chapter-03-control-flow.md) | [Chapter 5: Exceptions →](chapter-05-exceptions.md)

---

## The Task

Marcus's PR review: "The `do_stuff()` function is 400 lines. It does 12 things. Break it into small functions that each do one thing. Make them testable."

Leo adds: "And make the retry logic reusable. We retry API calls in 6 places — same pattern, copy-pasted."

---

## Defining Functions

```python
def greet(name: str) -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"

result = greet("Leo")  # "Hello, Leo!"
```

### Anatomy

```python
def function_name(param1: Type, param2: Type) -> ReturnType:
    """Docstring: what this function does."""
    # body
    return value
```

| Part | Purpose |
|---|---|
| `def` | Declares a function |
| Name | snake_case by convention |
| Parameters | Inputs (with optional type hints) |
| `-> ReturnType` | What it returns (optional but recommended) |
| Docstring | First string in body — describes the function |
| `return` | Sends a value back to the caller |

Functions without `return` (or with bare `return`) return `None`.

---

## Arguments: Positional and Keyword

```python
def send_message(channel: str, text: str, urgent: bool = False) -> dict:
    """Send a message to a Slack channel."""
    payload = {"channel": channel, "text": text}
    if urgent:
        payload["priority"] = "high"
    return payload

# Positional
send_message("#support", "Server is down")

# Keyword (explicit, readable)
send_message(channel="#support", text="Server is down", urgent=True)

# Mix (positional first, then keyword)
send_message("#support", "Server is down", urgent=True)
```

### Default Values

```python
def retry(func, max_attempts: int = 3, backoff: float = 1.0):
    """Retry a function with defaults that work for most cases."""
    ...

retry(call_api)                          # uses defaults: 3 attempts, 1s backoff
retry(call_api, max_attempts=5)          # override one default
retry(call_api, max_attempts=5, backoff=2.0)  # override both
```

⚠️ **Mutable default trap**:

```python
# ❌ BUG: the list is shared across all calls!
def add_item(item, items=[]):
    items.append(item)
    return items

add_item("a")  # ["a"]
add_item("b")  # ["a", "b"] — not ["b"]!

# ✅ Fix: use None as default, create inside
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

---

## *args and **kwargs: Flexible Arguments

### *args: Variable Positional Arguments

```python
def log(*messages):
    """Log any number of messages."""
    for msg in messages:
        print(f"[LOG] {msg}")

log("Starting")                    # one arg
log("Starting", "Processing", "Done")  # three args
```

`*args` collects extra positional arguments into a tuple.

### **kwargs: Variable Keyword Arguments

```python
def create_ticket(**fields):
    """Create a ticket with arbitrary fields."""
    ticket = {"id": generate_id(), "created_at": now()}
    ticket.update(fields)
    return ticket

create_ticket(title="Bug", priority="high", assignee="leo")
# → {"id": "...", "created_at": "...", "title": "Bug", "priority": "high", "assignee": "leo"}
```

`**kwargs` collects extra keyword arguments into a dict.

### Combining Everything

```python
def api_call(method: str, url: str, *args, timeout: int = 30, **kwargs):
    """The order matters: positional, *args, keyword-only, **kwargs."""
    ...
```

Order: `positional` → `*args` → `keyword-only` → `**kwargs`

### Unpacking: The Reverse

```python
# Unpack a list into positional args
args = ["#support", "Hello!"]
send_message(*args)  # same as send_message("#support", "Hello!")

# Unpack a dict into keyword args
config = {"channel": "#support", "text": "Hello!", "urgent": True}
send_message(**config)  # same as send_message(channel="#support", text="Hello!", urgent=True)
```

---

## Return Values

```python
# Return a single value
def count_messages(messages: list) -> int:
    return len(messages)

# Return multiple values (tuple)
def parse_command(text: str) -> tuple[str, list[str]]:
    parts = text.split()
    command = parts[0]
    args = parts[1:]
    return command, args

cmd, args = parse_command("deploy production --force")
# cmd = "deploy", args = ["production", "--force"]

# Return None explicitly (or implicitly)
def maybe_find(items: list, target: str) -> str | None:
    for item in items:
        if item == target:
            return item
    return None  # explicit is better than implicit
```

### Early Return Pattern

```python
# ❌ Deep nesting
def process_message(msg):
    if msg is not None:
        if msg.get("type") == "message":
            if msg.get("text"):
                text = msg["text"]
                # ... actual logic buried 3 levels deep

# ✅ Early returns (guard clauses)
def process_message(msg):
    if msg is None:
        return None
    if msg.get("type") != "message":
        return None
    if not msg.get("text"):
        return None
    
    text = msg["text"]
    # ... actual logic at top level
```

---

## Scope: Where Variables Live

```python
global_config = {"debug": True}  # module-level (global)

def outer():
    outer_var = "I'm in outer"  # enclosing scope
    
    def inner():
        inner_var = "I'm in inner"  # local scope
        print(outer_var)  # ✅ can read enclosing scope
        print(global_config)  # ✅ can read global scope
    
    inner()
    print(inner_var)  # ❌ NameError — inner_var doesn't exist here
```

### LEGB Rule (Lookup Order)

```
L — Local (inside current function)
E — Enclosing (inside enclosing function)
G — Global (module level)
B — Built-in (Python built-ins like len, print)
```

Python looks up variables in this order. First match wins.

```python
x = "global"

def func():
    x = "local"  # creates a NEW local variable, doesn't modify global
    print(x)     # "local"

func()
print(x)         # "global" — unchanged
```

### Modifying Outer Scope (Rarely Needed)

```python
counter = 0

def increment():
    global counter  # explicitly declare you're modifying the global
    counter += 1

# For enclosing scope:
def outer():
    count = 0
    def inner():
        nonlocal count  # modify the enclosing variable
        count += 1
    inner()
    print(count)  # 1
```

Avoid `global` and `nonlocal` when possible. Pass values as arguments and return results instead.

---

## Functions as First-Class Objects

In Python, functions are values. You can pass them around like any other variable.

```python
def shout(text: str) -> str:
    return text.upper() + "!"

def whisper(text: str) -> str:
    return text.lower() + "..."

# Assign to a variable
transform = shout
transform("hello")  # "HELLO!"

# Pass as an argument
def apply(func, text: str) -> str:
    return func(text)

apply(shout, "hello")    # "HELLO!"
apply(whisper, "hello")  # "hello..."

# Store in a collection
handlers = {
    "shout": shout,
    "whisper": whisper,
}
handlers["shout"]("hello")  # "HELLO!"
```

---

## Lambda: Anonymous Functions

Small, one-expression functions without a name:

```python
# Named function
def double(x):
    return x * 2

# Lambda equivalent
double = lambda x: x * 2

# Useful as arguments
messages = [{"text": "hello", "ts": 3}, {"text": "world", "ts": 1}]
sorted_msgs = sorted(messages, key=lambda m: m["ts"])

# Filter
urgent = list(filter(lambda t: t["priority"] == "high", tickets))

# But prefer comprehensions for readability:
urgent = [t for t in tickets if t["priority"] == "high"]
```

**Rule**: If a lambda is complex enough to need a name, make it a regular function.

---

## Practical: The Reusable Retry

Leo's request — retry logic used in 6 places, extracted into one function:

```python
import time
from typing import Callable, TypeVar

T = TypeVar("T")


def with_retry(
    func: Callable[[], T],
    max_attempts: int = 3,
    backoff: list[float] | None = None,
    exceptions: tuple = (Exception,),
) -> T:
    """Execute a function with retry logic.
    
    Args:
        func: Zero-argument callable to execute.
        max_attempts: Maximum number of attempts.
        backoff: Seconds to wait between attempts. Defaults to [1, 5, 15].
        exceptions: Tuple of exception types to catch and retry.
    
    Returns:
        The return value of func on success.
    
    Raises:
        The last exception if all attempts fail.
    """
    if backoff is None:
        backoff = [1.0, 5.0, 15.0]

    last_error: Exception | None = None

    for attempt in range(max_attempts):
        try:
            return func()
        except exceptions as e:
            last_error = e
            if attempt < max_attempts - 1:
                wait = backoff[min(attempt, len(backoff) - 1)]
                print(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait}s...")
                time.sleep(wait)

    raise last_error  # type: ignore


# Usage
def fetch_status():
    response = requests.get("https://api.example.com/status", timeout=10)
    response.raise_for_status()
    return response.json()

status = with_retry(fetch_status, max_attempts=5)

# With lambda for inline calls
data = with_retry(lambda: requests.get(url).json())

# Only retry specific errors
result = with_retry(
    fetch_status,
    exceptions=(ConnectionError, TimeoutError),
)
```

---

## Practical: Breaking Up do_stuff()

Before (Derek's code):

```python
def do_stuff(msg):
    # 400 lines of everything
    ...
```

After (your refactor):

```python
def handle_message(msg: dict, config: dict) -> str | None:
    """Top-level message handler. Routes to specific handlers."""
    if should_ignore(msg):
        return None
    
    command = extract_command(msg)
    if command is None:
        return None
    
    user = msg.get("user", "unknown")
    if not has_permission(command, user, config):
        return f"Permission denied for '{command}'."
    
    return execute_command(command, msg, config)


def should_ignore(msg: dict) -> bool:
    """Messages we never respond to."""
    return msg.get("subtype") == "bot_message" or not msg.get("text")


def extract_command(msg: dict) -> str | None:
    """Pull the command name from message text."""
    text = msg.get("text", "").strip()
    words = text.split()
    return words[0].lower() if words else None


def has_permission(command: str, user: str, config: dict) -> bool:
    """Check if user can run this command."""
    cmd_config = config.get("commands", {}).get(command, {})
    if cmd_config.get("admin_only"):
        return user in config.get("admins", [])
    return True


def execute_command(command: str, msg: dict, config: dict) -> str:
    """Dispatch to the appropriate command handler."""
    handlers = {
        "help": cmd_help,
        "status": cmd_status,
        "deploy": cmd_deploy,
    }
    handler = handlers.get(command)
    if handler is None:
        return f"Unknown command: '{command}'"
    return handler(msg, config)
```

Each function does one thing. Each is testable in isolation. Marcus approves the PR.

---

## Quick Reference

```
────────────────────────────┬──────────────────────────────────────────
Concept                     │ Syntax
────────────────────────────┼──────────────────────────────────────────
Define function             │ def name(params) -> ReturnType:
Default argument            │ def f(x, y=10):
*args                       │ Collects extra positional → tuple
**kwargs                    │ Collects extra keyword → dict
Unpack list into args       │ func(*list)
Unpack dict into kwargs     │ func(**dict)
Lambda                      │ lambda x: x * 2
Return multiple             │ return a, b (tuple)
Early return                │ if bad: return None
First-class function        │ handlers = {"cmd": func}
────────────────────────────┴──────────────────────────────────────────
```

---

## What's Next

You deploy the refactored bot. It runs for 10 minutes, then crashes:

```
KeyError: 'text'
TypeError: 'NoneType' object is not subscriptable
requests.exceptions.ConnectionError: Connection refused
```

The bot doesn't handle errors. Any unexpected input, any network hiccup, and it dies. Time to learn exceptions.

---

[← Chapter 3: Control Flow](chapter-03-control-flow.md) | [Chapter 5: Exceptions →](chapter-05-exceptions.md)

# Chapter 11: "Add Logging to Everything"

[← Chapter 10: File I/O](chapter-10-file-io.md) | [Chapter 12: Generators →](chapter-12-generators.md)

---

## The Problem

Marcus, reviewing your PR:

> "Every handler starts with the same 5 lines: log the command, start a timer, try/except, log the result, log the duration. That's 5 lines × 12 handlers = 60 lines of duplicated boilerplate. Don't repeat yourself. Use a decorator. Add timing and logging to every handler without touching the handler code."

The boilerplate:

```python
# This is in EVERY handler
def handle_status(msg: dict) -> str:
    logger.info(f"Executing 'status' for user {msg['user']}")
    start = time.time()
    try:
        result = _do_status_check()
        duration = time.time() - start
        logger.info(f"'status' completed in {duration:.3f}s")
        return result
    except Exception as e:
        duration = time.time() - start
        logger.error(f"'status' failed after {duration:.3f}s: {e}")
        raise
```

---

## Functions Are Objects

Before decorators, understand this: functions are just objects.

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"

# Functions are objects — you can assign them to variables
say_hi = greet
print(say_hi("Leo"))  # "Hello, Leo!"

# Pass them as arguments
def apply(func, value):
    return func(value)

print(apply(greet, "Rina"))  # "Hello, Rina!"

# Store them in data structures
commands = {"greet": greet, "upper": str.upper}
commands["greet"]("Marcus")  # "Hello, Marcus!"
```

---

## Closures: Functions That Remember

```python
def make_greeter(greeting: str):
    """Returns a function that 'remembers' the greeting."""
    def greeter(name: str) -> str:
        return f"{greeting}, {name}!"  # greeting is "closed over"
    return greeter

hello = make_greeter("Hello")
hey = make_greeter("Hey")

print(hello("Leo"))   # "Hello, Leo!"
print(hey("Rina"))    # "Hey, Rina!"
```

The inner function `greeter` captures `greeting` from its enclosing scope. This is a **closure**.

---

## Your First Decorator

A decorator is a function that takes a function and returns a new function:

```python
import time
import functools


def timer(func):
    """Log how long a function takes."""
    @functools.wraps(func)  # preserves name, docstring
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"{func.__name__} took {duration:.3f}s")
        return result
    return wrapper


@timer
def fetch_messages(channel: str) -> list[dict]:
    """Fetch messages from Slack."""
    # ... slow API call
    time.sleep(0.5)
    return [{"text": "hello"}]


fetch_messages("#support")
# fetch_messages took 0.502s
```

### What `@timer` Actually Does

```python
# This:
@timer
def fetch_messages(channel):
    ...

# Is exactly the same as:
def fetch_messages(channel):
    ...
fetch_messages = timer(fetch_messages)
```

---

## Decorators with Arguments

```python
import functools
import logging

logger = logging.getLogger(__name__)


def log_call(level: str = "info"):
    """Decorator that logs function calls at a specified level."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log_fn = getattr(logger, level)
            log_fn(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            result = func(*args, **kwargs)
            log_fn(f"{func.__name__} returned {result!r}")
            return result
        return wrapper
    return decorator


@log_call(level="debug")
def process_command(command: str, user: str) -> str:
    return f"Processed {command} for {user}"


@log_call(level="warning")
def delete_ticket(ticket_id: str) -> None:
    # ... dangerous operation
    pass
```

Three levels of nesting:
1. `log_call(level)` — receives the decorator arguments
2. `decorator(func)` — receives the function being decorated
3. `wrapper(*args, **kwargs)` — replaces the original function

---

## The Solution: Handler Decorators

```python
import time
import functools
import logging
from typing import Callable

logger = logging.getLogger("pulsebot")


def logged_handler(func: Callable) -> Callable:
    """Add logging and timing to any handler."""
    @functools.wraps(func)
    def wrapper(msg: dict, *args, **kwargs) -> str | None:
        command = func.__name__.replace("handle_", "")
        user = msg.get("user", "unknown")
        
        logger.info(f"[{command}] Started by {user}")
        start = time.time()
        
        try:
            result = func(msg, *args, **kwargs)
            duration = time.time() - start
            logger.info(f"[{command}] Completed in {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.time() - start
            logger.error(f"[{command}] Failed after {duration:.3f}s: {e}")
            raise
    
    return wrapper


def require_admin(func: Callable) -> Callable:
    """Reject non-admin users."""
    @functools.wraps(func)
    def wrapper(msg: dict, *args, **kwargs) -> str | None:
        user = msg.get("user", "")
        if user not in ADMINS:
            logger.warning(f"Permission denied: {user} tried {func.__name__}")
            return "🔒 Permission denied"
        return func(msg, *args, **kwargs)
    return wrapper


def rate_limit(max_calls: int, period: float):
    """Limit how often a handler can be called."""
    calls: list[float] = []
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove old calls outside the window
            calls[:] = [t for t in calls if now - t < period]
            if len(calls) >= max_calls:
                return "⏳ Rate limited. Try again later."
            calls.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### Using the Decorators

```python
@logged_handler
def handle_status(msg: dict) -> str:
    """Check system status."""
    return "✅ All systems operational"


@logged_handler
@require_admin
def handle_deploy(msg: dict) -> str:
    """Trigger deployment."""
    return "🚀 Deployment started"


@logged_handler
@rate_limit(max_calls=5, period=60.0)
def handle_joke(msg: dict) -> str:
    """Tell a joke (max 5 per minute)."""
    return "Why do programmers prefer dark mode? Less bugs."
```

Decorators stack bottom-up: `handle_deploy` is first wrapped by `require_admin`, then by `logged_handler`.

---

## functools: The Decorator Toolkit

### functools.wraps — Preserve Metadata

```python
# Without @wraps:
print(handle_status.__name__)  # "wrapper" 😱
print(handle_status.__doc__)   # None

# With @wraps:
print(handle_status.__name__)  # "handle_status" ✅
print(handle_status.__doc__)   # "Check system status." ✅
```

### functools.lru_cache — Memoization

```python
from functools import lru_cache


@lru_cache(maxsize=128)
def get_user_info(user_id: str) -> dict:
    """Cache user lookups — Slack API is slow."""
    response = slack_client.users_info(user=user_id)
    return response["user"]

# First call: hits API
info = get_user_info("U123")

# Second call: returns cached result instantly
info = get_user_info("U123")

# Check cache stats
print(get_user_info.cache_info())
# CacheInfo(hits=1, misses=1, maxsize=128, currsize=1)

# Clear cache
get_user_info.cache_clear()
```

### functools.partial — Pre-fill Arguments

```python
from functools import partial

def send_message(channel: str, text: str, bot_name: str = "PulseBot") -> None:
    print(f"[{bot_name}] → {channel}: {text}")

# Create specialized versions
send_to_support = partial(send_message, "#support")
send_to_eng = partial(send_message, "#engineering")

send_to_support("Ticket resolved")
# [PulseBot] → #support: Ticket resolved
```

---

## Class-Based Decorators

For decorators that need state:

```python
import time
from collections import defaultdict


class RateLimiter:
    """Class-based rate limiter with per-user tracking."""
    
    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self.calls: dict[str, list[float]] = defaultdict(list)
    
    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(msg: dict, *args, **kwargs):
            user = msg.get("user", "anonymous")
            now = time.time()
            
            # Clean old entries
            self.calls[user] = [
                t for t in self.calls[user] if now - t < self.period
            ]
            
            if len(self.calls[user]) >= self.max_calls:
                return f"⏳ {user}, you're rate limited. Wait {self.period}s."
            
            self.calls[user].append(now)
            return func(msg, *args, **kwargs)
        return wrapper


@RateLimiter(max_calls=3, period=60)
def handle_generate(msg: dict) -> str:
    """Generate something expensive."""
    return "Generated!"
```

---

## Real-World Pattern: Retry Decorator

```python
import time
import functools
from typing import Type


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[Type[Exception], ...] = (Exception,),
):
    """Retry a function on failure with exponential backoff."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        raise
                    logger.warning(
                        f"{func.__name__} attempt {attempt}/{max_attempts} "
                        f"failed: {e}. Retrying in {current_delay:.1f}s..."
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator


@retry(max_attempts=3, delay=1.0, exceptions=(ConnectionError, TimeoutError))
def call_slack_api(endpoint: str, payload: dict) -> dict:
    """Call Slack API with automatic retry."""
    response = requests.post(f"https://slack.com/api/{endpoint}", json=payload)
    response.raise_for_status()
    return response.json()
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ Pattern
────────────────────────────────┼──────────────────────────────────────
Basic decorator                 │ def deco(func): def wrapper(...): ...
Decorator with args             │ def deco(arg): def inner(func): ...
@functools.wraps(func)          │ Preserve __name__ and __doc__
@functools.lru_cache            │ Memoize function results
functools.partial(fn, arg)      │ Pre-fill function arguments
────────────────────────────────┼──────────────────────────────────────
Closure                         │ Inner function captures outer vars
Stacking decorators             │ Applied bottom-up
Class decorator                 │ __call__ method wraps the function
────────────────────────────────┼──────────────────────────────────────
Common uses                     │ Logging, timing, auth, retry,
                                │ caching, rate limiting, validation
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The decorators work beautifully. Every handler is clean — just business logic, no boilerplate. Then the Tuesday crash happens again, but this time it's different: "Memory usage spiked to 4GB. The bot tried to load 10,000 messages into a list." Time to learn generators and lazy evaluation.

---

[← Chapter 10: File I/O](chapter-10-file-io.md) | [Chapter 12: Generators →](chapter-12-generators.md)

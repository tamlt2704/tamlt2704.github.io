# Chapter 2: Decorators That Write Code

[← Chapter 1: Everything Is an Object](chapter-01-object-model.md) | [Chapter 3: Class Decorators →](chapter-03-class-decorators.md)

---

## The Problem

FrameForge's API framework has 40 endpoint functions. Every single one looks like this:

```python
import time
import logging

logger = logging.getLogger(__name__)

def get_user(request):
    start = time.perf_counter()
    try:
        logger.info(f"Calling get_user with {request}")
        # --- actual logic (2 lines) ---
        user = db.find_user(request.user_id)
        result = {"id": user.id, "name": user.name}
        # --- end actual logic ---
        elapsed = time.perf_counter() - start
        logger.info(f"get_user completed in {elapsed:.3f}s")
        return result
    except ValidationError as e:
        logger.warning(f"Validation failed in get_user: {e}")
        return {"error": str(e)}, 400
    except Exception as e:
        logger.error(f"get_user failed: {e}", exc_info=True)
        return {"error": "Internal server error"}, 500

def get_orders(request):
    start = time.perf_counter()
    try:
        logger.info(f"Calling get_orders with {request}")
        # --- actual logic (3 lines) ---
        orders = db.find_orders(request.user_id)
        result = [{"id": o.id, "total": o.total} for o in orders]
        # --- end actual logic ---
        elapsed = time.perf_counter() - start
        logger.info(f"get_orders completed in {elapsed:.3f}s")
        return result
    except ValidationError as e:
        logger.warning(f"Validation failed in get_orders: {e}")
        return {"error": str(e)}, 400
    except Exception as e:
        logger.error(f"get_orders failed: {e}", exc_info=True)
        return {"error": "Internal server error"}, 500
```

15 lines of boilerplate wrapping 2-3 lines of logic. Multiply by 40 endpoints. Vera is not amused.

"Every endpoint has the same try/except, the same timing, the same logging. Extract it."

## The Core Idea

A decorator is a function that takes a function and returns a function.

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        # do something before
        result = func(*args, **kwargs)
        # do something after
        return result
    return wrapper

@my_decorator
def say_hello():
    return "hello"

# The @ syntax is just sugar for:
# say_hello = my_decorator(say_hello)
```

## Solution: @timing

```python
import time
import functools

def timing(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.3f}s")
        return result
    return wrapper

@timing
def slow_function():
    time.sleep(0.1)
    return "done"

slow_function()
# slow_function took 0.103s
```

### Why @functools.wraps Matters

Without it, the wrapper replaces the original function's identity:

```python
def bad_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@bad_decorator
def my_func():
    """Important docstring."""
    pass

print(my_func.__name__)  # "wrapper" — WRONG
print(my_func.__doc__)   # None — WRONG

# With @functools.wraps(func):
print(my_func.__name__)  # "my_func" — correct
print(my_func.__doc__)   # "Important docstring." — correct
```

`@wraps` copies `__name__`, `__doc__`, `__module__`, and `__wrapped__` from the original.

## Solution: @error_handler

```python
import logging
import functools

logger = logging.getLogger(__name__)

def error_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f"Validation failed in {func.__name__}: {e}")
            return {"error": str(e)}, 400
        except Exception as e:
            logger.error(f"{func.__name__} failed: {e}", exc_info=True)
            return {"error": "Internal server error"}, 500
    return wrapper
```

## Stacking Decorators

Decorators compose. Apply them bottom-up:

```python
@timing
@error_handler
def get_user(request):
    user = db.find_user(request.user_id)
    return {"id": user.id, "name": user.name}

# Execution order:
# timing wraps (error_handler wraps get_user)
# So timing runs first (starts clock), then error_handler catches exceptions
```

Now our 40 endpoints go from 15 lines to 3:

```python
@timing
@error_handler
def get_user(request):
    user = db.find_user(request.user_id)
    return {"id": user.id, "name": user.name}

@timing
@error_handler
def get_orders(request):
    orders = db.find_orders(request.user_id)
    return [{"id": o.id, "total": o.total} for o in orders]
```

## Parameterized Decorators (Decorator Factories)

What if you want `@retry(max_attempts=3)`? You need a function that returns a decorator:

```python
import functools
import time

def retry(max_attempts=3, delay=1.0, exceptions=(Exception,)):
    """Decorator factory: returns a decorator configured with parameters."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        time.sleep(delay * attempt)  # exponential-ish backoff
            raise last_exception
        return wrapper
    return decorator

@retry(max_attempts=5, delay=0.5, exceptions=(ConnectionError, TimeoutError))
def fetch_data(url):
    return requests.get(url).json()
```

The three levels:
1. `retry(max_attempts=5)` — called first, returns `decorator`
2. `decorator(fetch_data)` — called by `@`, returns `wrapper`
3. `wrapper(*args)` — called when you invoke `fetch_data()`

## Solution: @validate_input

```python
import functools
from typing import get_type_hints

def validate_input(func):
    """Validate arguments match type hints."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        hints = get_type_hints(func)
        # Match positional args to parameter names
        params = list(func.__code__.co_varnames[:func.__code__.co_argcount])
        for name, value in zip(params, args):
            if name in hints and not isinstance(value, hints[name]):
                raise TypeError(
                    f"{func.__name__}() argument '{name}' must be "
                    f"{hints[name].__name__}, got {type(value).__name__}"
                )
        for name, value in kwargs.items():
            if name in hints and not isinstance(value, hints[name]):
                raise TypeError(
                    f"{func.__name__}() argument '{name}' must be "
                    f"{hints[name].__name__}, got {type(value).__name__}"
                )
        return func(*args, **kwargs)
    return wrapper

@validate_input
def create_user(name: str, age: int, email: str) -> dict:
    return {"name": name, "age": age, "email": email}

create_user("Alice", 30, "alice@example.com")  # Works
create_user("Alice", "thirty", "alice@example.com")  # TypeError!
```

## Solution: @cache_result

```python
import functools
import time

def cache_result(ttl_seconds=60):
    """Cache function results with a time-to-live."""
    def decorator(func):
        cache = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            now = time.time()
            if key in cache:
                result, timestamp = cache[key]
                if now - timestamp < ttl_seconds:
                    return result
            result = func(*args, **kwargs)
            cache[key] = (result, now)
            return result

        wrapper.cache_clear = lambda: cache.clear()
        wrapper.cache_info = lambda: {"size": len(cache)}
        return wrapper
    return decorator

@cache_result(ttl_seconds=300)
def expensive_query(user_id):
    """Hits the database — cache for 5 minutes."""
    return db.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

## The Complete FrameForge Endpoint

Before:

```python
# 40 functions × 15 lines of boilerplate = 600 lines of noise
def get_user(request):
    start = time.perf_counter()
    try:
        logger.info(f"Calling get_user")
        user = db.find_user(request.user_id)
        result = {"id": user.id, "name": user.name}
        elapsed = time.perf_counter() - start
        logger.info(f"get_user completed in {elapsed:.3f}s")
        return result
    except ValidationError as e:
        ...
    except Exception as e:
        ...
```

After:

```python
# 40 functions × 3 lines of logic = clarity
@timing
@error_handler
@cache_result(ttl_seconds=60)
@validate_input
def get_user(request: Request) -> dict:
    user = db.find_user(request.user_id)
    return {"id": user.id, "name": user.name}
```

Four decorators. Zero boilerplate in the function body. Each decorator is written once, tested once, used everywhere.

## Debugging Decorated Functions

The `__wrapped__` attribute (set by `@wraps`) lets you access the original:

```python
# Access the unwrapped function for testing
original = get_user.__wrapped__

# Inspect the decorator chain
print(get_user.__name__)      # "get_user" (thanks to @wraps)
print(get_user.__wrapped__)   # <function get_user at 0x...>
```

## What You Learned

- **A decorator is a function that takes a function and returns a function** — that's it
- **`@functools.wraps`** preserves the original function's identity
- **Stacking decorators** composes behavior — order matters (bottom-up application, top-down execution)
- **Parameterized decorators** are three levels deep: factory → decorator → wrapper
- **Real-world decorators**: `@retry`, `@timing`, `@cache_result`, `@validate_input`, `@error_handler`
- Decorators eliminate cross-cutting concerns — logging, timing, error handling, caching, validation

## Key Insight

> Decorators are the simplest form of metaprogramming. They modify function behavior without modifying function code. But they only work on functions. What if you need to modify an entire class — inject methods, alter `__init__`, add behavior to 20 classes at once?

That's class decorators. Next chapter.

---

[Chapter 3: Class Decorators →](chapter-03-class-decorators.md)

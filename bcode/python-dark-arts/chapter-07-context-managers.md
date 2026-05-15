# Chapter 7: Context Managers Beyond Files

[← Chapter 6: Dynamic Dispatch](chapter-06-dynamic-attrs.md) | [Chapter 8: Generators →](chapter-08-generators.md)

---

## The Problem

FrameForge's framework manages resources: database connections, transactions, temporary config overrides, timing blocks. The naive approach:

```python
# Database transaction — manual cleanup
connection = db.connect()
try:
    connection.begin()
    connection.execute("INSERT INTO users ...")
    connection.execute("UPDATE accounts ...")
    connection.commit()
except Exception:
    connection.rollback()
    raise
finally:
    connection.close()

# Timing — manual bookkeeping
import time
start = time.perf_counter()
result = expensive_operation()
elapsed = time.perf_counter() - start
print(f"Took {elapsed:.3f}s")

# Temporary config — manual restore
original = app.config["DEBUG"]
app.config["DEBUG"] = True
try:
    run_diagnostics()
finally:
    app.config["DEBUG"] = original
```

Every resource follows the same pattern: acquire → use → release. The `try/finally` is the boilerplate.

Vera: "Wrap the pattern once. Use `with` everywhere."

## The Protocol: __enter__ and __exit__

```python
class MyContext:
    def __enter__(self):
        # Acquire the resource
        # Return value is bound to 'as' variable
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Release the resource
        # exc_type/exc_val/exc_tb are set if an exception occurred
        # Return True to suppress the exception, False to propagate
        return False
```

## Solution: Timer Context Manager

```python
import time

class Timer:
    """Measure execution time of a block."""

    def __init__(self, label="Block"):
        self.label = label
        self.elapsed = None

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.perf_counter() - self.start
        print(f"{self.label} took {self.elapsed:.3f}s")
        return False  # Don't suppress exceptions

# Usage:
with Timer("Database query"):
    results = db.execute("SELECT * FROM large_table")
# "Database query took 1.234s"

# Access the timing after:
with Timer("API call") as t:
    response = requests.get("https://api.example.com")
print(f"Elapsed: {t.elapsed}")
```

## Solution: Transaction

```python
class Transaction:
    """Database transaction with automatic commit/rollback."""

    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        self.connection.begin()
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # No exception — commit
            self.connection.commit()
        else:
            # Exception occurred — rollback
            self.connection.rollback()
        return False  # Re-raise the exception

# Usage:
with Transaction(db.connect()) as conn:
    conn.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
    conn.execute("UPDATE accounts SET balance = balance - 100 WHERE user = 'Alice'")
    # If anything raises, both operations are rolled back
```

## Solution: TemporaryConfig

```python
class TemporaryConfig:
    """Override config values, restore on exit."""

    def __init__(self, config, **overrides):
        self.config = config
        self.overrides = overrides
        self.originals = {}

    def __enter__(self):
        for key, value in self.overrides.items():
            self.originals[key] = self.config.get(key)
            self.config[key] = value
        return self.config

    def __exit__(self, exc_type, exc_val, exc_tb):
        for key, original in self.originals.items():
            if original is None:
                self.config.pop(key, None)
            else:
                self.config[key] = original
        return False

# Usage:
app_config = {"DEBUG": False, "LOG_LEVEL": "INFO"}

with TemporaryConfig(app_config, DEBUG=True, LOG_LEVEL="DEBUG"):
    print(app_config["DEBUG"])      # True
    print(app_config["LOG_LEVEL"])  # "DEBUG"
    run_diagnostics()

print(app_config["DEBUG"])  # False — restored
```

## The Generator Shortcut: @contextmanager

`contextlib.contextmanager` turns a generator into a context manager in 3 lines:

```python
from contextlib import contextmanager

@contextmanager
def timer(label="Block"):
    start = time.perf_counter()
    yield  # <-- this is where the 'with' block runs
    elapsed = time.perf_counter() - start
    print(f"{label} took {elapsed:.3f}s")

with timer("Query"):
    db.execute("SELECT ...")
```

The pattern:
1. Code before `yield` = `__enter__`
2. `yield value` = the value bound to `as`
3. Code after `yield` = `__exit__`

```python
@contextmanager
def transaction(connection):
    connection.begin()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise

@contextmanager
def temporary_config(config, **overrides):
    originals = {k: config.get(k) for k in overrides}
    config.update(overrides)
    try:
        yield config
    finally:
        for key, original in originals.items():
            if original is None:
                config.pop(key, None)
            else:
                config[key] = original
```

Three context managers, each under 10 lines. No class boilerplate.

## Solution: ConnectionPool

```python
from contextlib import contextmanager
from queue import Queue

class ConnectionPool:
    """Pool of reusable connections."""

    def __init__(self, factory, max_size=10):
        self._factory = factory
        self._pool = Queue(maxsize=max_size)
        # Pre-fill the pool
        for _ in range(max_size):
            self._pool.put(factory())

    @contextmanager
    def acquire(self):
        """Borrow a connection, return it when done."""
        conn = self._pool.get()
        try:
            yield conn
        finally:
            # Always return to pool, even if exception occurred
            self._pool.put(conn)

# Usage:
pool = ConnectionPool(lambda: create_db_connection(), max_size=5)

with pool.acquire() as conn:
    conn.execute("SELECT * FROM users")
# Connection automatically returned to pool
```

## ExitStack: Managing Multiple Resources

```python
from contextlib import ExitStack

def process_files(filenames):
    """Open multiple files, close all on exit."""
    with ExitStack() as stack:
        files = [
            stack.enter_context(open(fname))
            for fname in filenames
        ]
        # All files open — process them
        for f in files:
            process(f.read())
    # All files closed, even if one raised an exception

# Dynamic resource management:
@contextmanager
def managed_resources(*factories):
    """Open multiple resources dynamically."""
    with ExitStack() as stack:
        resources = [stack.enter_context(f()) for f in factories]
        yield resources
```

## Async Context Managers

For async code, use `__aenter__` and `__aexit__`:

```python
import asyncio
from contextlib import asynccontextmanager

class AsyncTimer:
    def __init__(self, label):
        self.label = label

    async def __aenter__(self):
        self.start = asyncio.get_event_loop().time()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        elapsed = asyncio.get_event_loop().time() - self.start
        print(f"{self.label} took {elapsed:.3f}s")
        return False

# Or with the decorator:
@asynccontextmanager
async def async_transaction(connection):
    await connection.begin()
    try:
        yield connection
        await connection.commit()
    except Exception:
        await connection.rollback()
        raise

# Usage:
async def main():
    async with AsyncTimer("Fetch"):
        await fetch_data()
```

## Suppressing Exceptions

```python
from contextlib import suppress

# Instead of:
try:
    os.remove("temp.txt")
except FileNotFoundError:
    pass

# Write:
with suppress(FileNotFoundError):
    os.remove("temp.txt")
```

## Context Manager as Decorator

A context manager can double as a decorator:

```python
from contextlib import ContextDecorator

class log_calls(ContextDecorator):
    def __init__(self, label):
        self.label = label

    def __enter__(self):
        print(f"[{self.label}] Starting")
        return self

    def __exit__(self, *exc):
        print(f"[{self.label}] Finished")
        return False

# Use as context manager:
with log_calls("query"):
    db.execute("SELECT ...")

# OR as decorator:
@log_calls("handler")
def process_request(request):
    return handle(request)
```

## What You Learned

- **`__enter__`/`__exit__`** define the context manager protocol
- **`__exit__` receives exception info** — return `True` to suppress, `False` to propagate
- **`@contextmanager`** turns a generator into a context manager (code before yield = enter, after = exit)
- **`ExitStack`** manages a dynamic number of context managers
- **Async context managers** use `__aenter__`/`__aexit__` or `@asynccontextmanager`
- **Real uses**: timers, transactions, temporary state, connection pools, resource cleanup
- **`ContextDecorator`** lets a context manager double as a function decorator

## Key Insight

> Context managers handle the "setup/teardown" pattern. But what about processing data that's too large to fit in memory? You can't load a 10GB file into a list. You need lazy evaluation — producing values one at a time, on demand. That's generators.

---

[Chapter 8: Generators and Lazy Pipelines →](chapter-08-generators.md)

# Chapter 9: Closures and Factory Functions

[← Chapter 8: Generators](chapter-08-generators.md) | [Chapter 10: The Import System →](chapter-10-imports.md)

---

## The Problem

FrameForge's validation system needs 20 validator functions. They all follow the same pattern but differ in parameters:

```python
def validate_min_length_3(value):
    if len(value) < 3:
        raise ValueError(f"Must be at least 3 characters, got {len(value)}")
    return value

def validate_min_length_5(value):
    if len(value) < 5:
        raise ValueError(f"Must be at least 5 characters, got {len(value)}")
    return value

def validate_min_length_8(value):
    if len(value) < 8:
        raise ValueError(f"Must be at least 8 characters, got {len(value)}")
    return value

def validate_max_value_100(value):
    if value > 100:
        raise ValueError(f"Must be <= 100, got {value}")
    return value

def validate_max_value_255(value):
    if value > 255:
        raise ValueError(f"Must be <= 255, got {value}")
    return value

# ... 15 more nearly-identical functions
```

20 functions that differ by one number. Copy-paste programming.

Vera: "Write a function that *makes* validator functions. One factory, infinite validators."

## The Core Idea

A closure is a function that captures variables from its enclosing scope:

```python
def make_greeter(greeting):
    # 'greeting' is captured by the inner function
    def greeter(name):
        return f"{greeting}, {name}!"
    return greeter

hello = make_greeter("Hello")
hola = make_greeter("Hola")

hello("Alice")  # "Hello, Alice!"
hola("Alice")   # "Hola, Alice!"

# The inner function "remembers" the greeting value:
hello.__closure__[0].cell_contents  # "Hello"
```

`greeter` is a closure — it's a function bundled with the environment it was created in. It has "memory" of `greeting` even after `make_greeter` has returned.

## Solution: Validator Factories

```python
def make_min_length(n):
    """Factory: creates a min-length validator."""
    def validator(value):
        if len(value) < n:
            raise ValueError(f"Must be at least {n} characters, got {len(value)}")
        return value
    validator.__name__ = f"min_length_{n}"
    return validator

def make_max_value(maximum):
    """Factory: creates a max-value validator."""
    def validator(value):
        if value > maximum:
            raise ValueError(f"Must be <= {maximum}, got {value}")
        return value
    validator.__name__ = f"max_value_{maximum}"
    return validator

def make_one_of(*choices):
    """Factory: creates a choices validator."""
    def validator(value):
        if value not in choices:
            raise ValueError(f"Must be one of {choices}, got {value!r}")
        return value
    validator.__name__ = f"one_of_{'_'.join(str(c) for c in choices)}"
    return validator

def make_matches(pattern):
    """Factory: creates a regex validator."""
    import re
    compiled = re.compile(pattern)
    def validator(value):
        if not compiled.match(value):
            raise ValueError(f"Must match pattern {pattern!r}, got {value!r}")
        return value
    validator.__name__ = f"matches_{pattern}"
    return validator

# Create validators on demand:
validate_username = make_min_length(3)
validate_password = make_min_length(8)
validate_age = make_max_value(150)
validate_role = make_one_of("admin", "user", "moderator")
validate_email = make_matches(r"^[\w.]+@[\w.]+\.\w+$")

# Use them:
validate_username("Al")  # ValueError: Must be at least 3 characters
validate_role("superuser")  # ValueError: Must be one of ('admin', 'user', 'moderator')
validate_email("alice@dev.io")  # "alice@dev.io"
```

One factory per pattern. Infinite validators. Zero repetition.

## Composing Validators

```python
def compose(*validators):
    """Chain multiple validators into one."""
    def combined(value):
        for validator in validators:
            value = validator(value)
        return value
    combined.__name__ = " | ".join(v.__name__ for v in validators)
    return combined

# Build complex validators from simple ones:
validate_username = compose(
    make_min_length(3),
    make_max_length(20),
    make_matches(r"^[a-zA-Z0-9_]+$"),
)

validate_username("ab")  # ValueError: Must be at least 3 characters
validate_username("valid_user_123")  # "valid_user_123"
```

## The nonlocal Keyword

Closures can read captured variables. To *modify* them, use `nonlocal`:

```python
def make_counter(start=0):
    count = start

    def increment():
        nonlocal count  # Without this, 'count = count + 1' creates a LOCAL variable
        count += 1
        return count

    def get():
        return count

    def reset():
        nonlocal count
        count = start

    # Return multiple functions sharing the same state:
    return increment, get, reset

inc, get, reset = make_counter(0)
inc()    # 1
inc()    # 2
inc()    # 3
get()    # 3
reset()
get()    # 0
```

Three functions sharing private state — no class needed.

## Factory Functions: When Closures Beat Classes

```python
# Class approach — verbose for simple state:
class Multiplier:
    def __init__(self, factor):
        self.factor = factor

    def __call__(self, x):
        return x * self.factor

double = Multiplier(2)
triple = Multiplier(3)

# Closure approach — concise:
def make_multiplier(factor):
    def multiply(x):
        return x * factor
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)

double(5)  # 10
triple(5)  # 15
```

**Use closures when**: you need a callable with captured state and no other methods.
**Use classes when**: you need multiple methods, inheritance, or complex state management.

## functools.partial: The Quick Factory

For simple argument binding, `functools.partial` is even shorter:

```python
from functools import partial

def power(base, exponent):
    return base ** exponent

square = partial(power, exponent=2)
cube = partial(power, exponent=3)

square(5)  # 25
cube(5)    # 125

# Real-world: configure a generic function
import json

compact_json = partial(json.dumps, separators=(',', ':'))
pretty_json = partial(json.dumps, indent=2, sort_keys=True)

compact_json({"a": 1})  # '{"a":1}'
pretty_json({"a": 1})   # '{\n  "a": 1\n}'
```

`partial` is a closure under the hood — it captures the pre-filled arguments.

## Solution: Event Handler Factory

```python
def make_handler(event_type, priority=0, async_mode=False):
    """Factory that creates configured event handlers."""
    def handler(func):
        func._event_type = event_type
        func._priority = priority
        func._async = async_mode
        return func
    return handler

# This is actually a parameterized decorator (Chapter 2) — which IS a closure!
@make_handler("user.created", priority=10)
def send_welcome_email(event):
    send_email(event.user.email, "Welcome!")

@make_handler("order.completed", priority=5, async_mode=True)
def process_payment(event):
    charge(event.order)

# The decorator factory pattern is just closures all the way down
```

## Solution: Converter Factory

```python
def make_converter(from_unit, to_unit, factor, offset=0):
    """Create a unit conversion function."""
    def convert(value):
        return value * factor + offset
    convert.__name__ = f"{from_unit}_to_{to_unit}"
    convert.__doc__ = f"Convert {from_unit} to {to_unit}"
    return convert

# Generate a family of converters:
km_to_miles = make_converter("km", "miles", 0.621371)
celsius_to_fahrenheit = make_converter("celsius", "fahrenheit", 9/5, 32)
kg_to_pounds = make_converter("kg", "pounds", 2.20462)

km_to_miles(100)              # 62.1371
celsius_to_fahrenheit(0)      # 32.0
celsius_to_fahrenheit(100)    # 212.0
```

## The Late Binding Gotcha

The most common closure bug in Python:

```python
# BROKEN: all functions return 4!
functions = []
for i in range(5):
    def f():
        return i  # Captures the VARIABLE i, not its VALUE
    functions.append(f)

[f() for f in functions]  # [4, 4, 4, 4, 4] — all see i=4!

# FIX 1: Default argument (captures value at definition time)
functions = []
for i in range(5):
    def f(i=i):  # Default arg evaluated at definition time
        return i
    functions.append(f)

[f() for f in functions]  # [0, 1, 2, 3, 4]

# FIX 2: Factory function (creates a new scope each iteration)
def make_f(i):
    def f():
        return i
    return f

functions = [make_f(i) for i in range(5)]
[f() for f in functions]  # [0, 1, 2, 3, 4]
```

Closures capture **variables**, not **values**. The variable `i` changes; all closures see the final value.

## Closures as Lightweight State Machines

```python
def make_rate_limiter(max_calls, period_seconds):
    """Create a rate limiter function."""
    import time
    calls = []

    def is_allowed():
        nonlocal calls
        now = time.time()
        # Remove expired entries
        calls = [t for t in calls if now - t < period_seconds]
        if len(calls) < max_calls:
            calls.append(now)
            return True
        return False

    return is_allowed

# Allow 5 calls per second:
limiter = is_allowed = make_rate_limiter(5, 1.0)

for i in range(10):
    print(f"Call {i}: {'allowed' if limiter() else 'blocked'}")
# First 5: allowed, next 5: blocked
```

## What You Learned

- **A closure captures variables from its enclosing scope** — it's a function with memory
- **Factory functions** produce specialized functions from parameters
- **`nonlocal`** allows modifying captured variables (not just reading them)
- **`functools.partial`** is a quick way to pre-fill function arguments
- **Late binding gotcha**: closures capture variables, not values — use default args or factories
- **Closures vs classes**: use closures for simple callables, classes for complex state
- **Decorators are closures** — the parameterized decorator pattern is closures all the way down

## Key Insight

> Closures let you create families of functions from a template. But what about creating families of *modules*? What if you want Python to auto-discover plugins, lazily load heavy dependencies, or customize how `import` works? That's the import system.

---

[Chapter 10: The Import System →](chapter-10-imports.md)

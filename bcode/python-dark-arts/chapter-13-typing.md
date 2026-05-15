# Chapter 13: Type System Tricks

[← Chapter 12: Concurrency](chapter-12-concurrency.md) | [Chapter 14: Performance →](chapter-14-performance.md)

---

## The Problem

FrameForge users write type-annotated functions. They want runtime validation generated automatically from those annotations — like Pydantic, but for any function:

```python
# Users write this:
def create_user(name: str, age: int, email: str, active: bool = True) -> dict:
    return {"name": name, "age": age, "email": email, "active": active}

# They want this to happen automatically:
create_user("Alice", "thirty", "alice@dev.io")
# TypeError: 'age' must be int, got str

# Without writing validation code by hand
```

The naive approach: write validation for every function manually (Chapter 2 showed this). But what if the decorator could *read* the type hints and generate validation automatically?

Vera: "Type hints are data. They're available at runtime. Read them, generate validators, done."

## Type Hints Are Runtime Data

```python
import typing
from typing import get_type_hints

def process(name: str, count: int, items: list[str]) -> bool:
    ...

# Access annotations at runtime:
print(process.__annotations__)
# {'name': <class 'str'>, 'count': <class 'int'>,
#  'items': list[str], 'return': <class 'bool'>}

# get_type_hints() resolves forward references and handles edge cases:
hints = get_type_hints(process)
print(hints)
# Same as above, but resolves string annotations like 'MyClass'
```

## Solution: @validate Decorator from Type Hints

```python
import functools
import inspect
from typing import get_type_hints, get_origin, get_args, Union

def validate(func):
    """Auto-generate runtime validation from type hints."""
    hints = get_type_hints(func)
    sig = inspect.signature(func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Bind arguments to parameter names
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()

        for param_name, value in bound.arguments.items():
            if param_name not in hints:
                continue
            if param_name == 'return':
                continue

            expected = hints[param_name]
            _check_type(param_name, value, expected)

        result = func(*args, **kwargs)

        # Validate return type
        if 'return' in hints and hints['return'] is not type(None):
            _check_type('return', result, hints['return'])

        return result

    return wrapper


def _check_type(name, value, expected):
    """Check if value matches the expected type hint."""
    origin = get_origin(expected)

    if origin is Union:
        # Handle Optional[X] which is Union[X, None]
        args = get_args(expected)
        if not any(_is_instance(value, arg) for arg in args):
            raise TypeError(
                f"'{name}' must be {expected}, got {type(value).__name__}: {value!r}"
            )
    elif origin is list:
        if not isinstance(value, list):
            raise TypeError(f"'{name}' must be list, got {type(value).__name__}")
        item_type = get_args(expected)
        if item_type:
            for i, item in enumerate(value):
                if not isinstance(item, item_type[0]):
                    raise TypeError(
                        f"'{name}[{i}]' must be {item_type[0].__name__}, "
                        f"got {type(item).__name__}"
                    )
    elif origin is dict:
        if not isinstance(value, dict):
            raise TypeError(f"'{name}' must be dict, got {type(value).__name__}")
        key_type, val_type = get_args(expected) or (None, None)
        if key_type:
            for k, v in value.items():
                if not isinstance(k, key_type):
                    raise TypeError(f"'{name}' key must be {key_type.__name__}")
                if not isinstance(v, val_type):
                    raise TypeError(f"'{name}' value must be {val_type.__name__}")
    elif expected is not inspect.Parameter.empty:
        if not _is_instance(value, expected):
            raise TypeError(
                f"'{name}' must be {_type_name(expected)}, "
                f"got {type(value).__name__}: {value!r}"
            )


def _is_instance(value, tp):
    """Safe isinstance check that handles typing generics."""
    try:
        return isinstance(value, tp)
    except TypeError:
        return True  # Can't check complex generics at runtime


def _type_name(tp):
    """Get a readable name for a type."""
    return getattr(tp, '__name__', str(tp))


# Usage:
@validate
def create_user(name: str, age: int, email: str, active: bool = True) -> dict:
    return {"name": name, "age": age, "email": email, "active": active}

create_user("Alice", 30, "alice@dev.io")  # Works
create_user("Alice", "thirty", "alice@dev.io")
# TypeError: 'age' must be int, got str: 'thirty'

@validate
def process_items(items: list[str], count: int) -> int:
    return len(items)

process_items(["a", "b", 3], 2)
# TypeError: 'items[2]' must be str, got int
```

## get_origin() and get_args(): Deconstructing Generics

```python
from typing import get_origin, get_args, Optional, Union

# get_origin: what's the "base" generic?
get_origin(list[int])        # <class 'list'>
get_origin(dict[str, int])   # <class 'dict'>
get_origin(Optional[str])    # typing.Union
get_origin(Union[int, str])  # typing.Union
get_origin(int)              # None (not generic)

# get_args: what are the type parameters?
get_args(list[int])          # (int,)
get_args(dict[str, int])     # (str, int)
get_args(Optional[str])      # (str, NoneType)
get_args(Union[int, str])    # (int, str)
get_args(int)                # ()
```

## TypeVar and Generic Classes

```python
from typing import TypeVar, Generic

T = TypeVar('T')

class Stack(Generic[T]):
    def __init__(self):
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

# At runtime, you can inspect the type parameter:
from typing import get_type_hints

hints = get_type_hints(Stack.push)
# {'item': ~T, 'return': <class 'NoneType'>}
```

## Protocol: Structural Typing

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Serializable(Protocol):
    def to_dict(self) -> dict: ...
    def from_dict(cls, data: dict) -> 'Serializable': ...

# Any class with to_dict() and from_dict() matches — no inheritance needed:
class User:
    def to_dict(self) -> dict:
        return {"name": self.name}

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        return cls(data["name"])

# Runtime check works because of @runtime_checkable:
isinstance(User(), Serializable)  # True

# Use in validation:
@validate
def save(obj: Serializable) -> None:
    data = obj.to_dict()
    db.store(data)
```

## ParamSpec: Preserving Function Signatures

```python
from typing import ParamSpec, TypeVar, Callable
import functools

P = ParamSpec('P')
R = TypeVar('R')

def logged(func: Callable[P, R]) -> Callable[P, R]:
    """Decorator that preserves the original function's type signature."""
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@logged
def add(x: int, y: int) -> int:
    return x + y

# Type checkers know add still takes (int, int) -> int
```

## Building a Mini-Pydantic

```python
from typing import get_type_hints, get_origin, get_args
import inspect

class ValidatedModel:
    """Base class that validates fields from type annotations."""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        hints = get_type_hints(cls)
        # Filter out ClassVar and methods
        fields = {
            name: hint for name, hint in hints.items()
            if not name.startswith('_')
        }
        cls._fields = fields
        cls._defaults = {}
        for name in fields:
            if hasattr(cls, name):
                cls._defaults[name] = getattr(cls, name)

    def __init__(self, **kwargs):
        for name, expected_type in self._fields.items():
            if name in kwargs:
                value = kwargs[name]
            elif name in self._defaults:
                value = self._defaults[name]
            else:
                raise TypeError(f"Missing required field: {name}")

            # Coerce if possible, validate otherwise
            value = self._validate_field(name, value, expected_type)
            object.__setattr__(self, name, value)

    def _validate_field(self, name, value, expected_type):
        origin = get_origin(expected_type)
        if origin is None:
            # Simple type
            if not isinstance(value, expected_type):
                try:
                    return expected_type(value)  # Try coercion
                except (TypeError, ValueError):
                    raise TypeError(
                        f"{name}: expected {expected_type.__name__}, "
                        f"got {type(value).__name__}"
                    )
        return value

    def __repr__(self):
        fields = ", ".join(
            f"{name}={getattr(self, name)!r}" for name in self._fields
        )
        return f"{type(self).__name__}({fields})"

    def dict(self):
        return {name: getattr(self, name) for name in self._fields}


# Usage:
class UserModel(ValidatedModel):
    name: str
    age: int
    email: str
    active: bool = True

u = UserModel(name="Alice", age=30, email="alice@dev.io")
print(u)  # UserModel(name='Alice', age=30, email='alice@dev.io', active=True)
print(u.dict())  # {'name': 'Alice', 'age': 30, 'email': 'alice@dev.io', 'active': True}

# Type coercion:
u2 = UserModel(name="Bob", age="25", email="bob@dev.io")
print(u2.age)  # 25 (int, coerced from str)

# Validation:
UserModel(name="Charlie", age="not a number", email="x")
# TypeError: age: expected int, got str
```

## Introspecting Annotations for Documentation

```python
from typing import get_type_hints
import inspect

def generate_schema(cls):
    """Generate a JSON-schema-like dict from type annotations."""
    hints = get_type_hints(cls)
    schema = {"type": "object", "properties": {}, "required": []}

    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }

    for name, hint in hints.items():
        if name.startswith('_'):
            continue
        origin = get_origin(hint)
        if origin is list:
            item_type = get_args(hint)[0] if get_args(hint) else None
            schema["properties"][name] = {
                "type": "array",
                "items": {"type": type_map.get(item_type, "any")}
            }
        else:
            schema["properties"][name] = {"type": type_map.get(hint, "any")}

        if not hasattr(cls, name):  # No default = required
            schema["required"].append(name)

    return schema

print(generate_schema(UserModel))
# {'type': 'object',
#  'properties': {'name': {'type': 'string'}, 'age': {'type': 'integer'}, ...},
#  'required': ['name', 'age', 'email']}
```

## What You Learned

- **`__annotations__`** and **`get_type_hints()`** expose type hints at runtime
- **`get_origin()`** and **`get_args()`** deconstruct generic types (`list[int]` → `list`, `(int,)`)
- **`@validate` decorator** reads hints and generates runtime type checking
- **`Protocol`** enables structural typing — match by shape, not inheritance
- **`ParamSpec`** preserves function signatures through decorators
- **Type hints drive code generation** — validation, serialization, documentation, all from annotations
- **Coercion vs validation** — try to convert, fail if impossible

## Key Insight

> Type hints are metadata that drives runtime behavior. But all this metaprogramming has a cost: abstraction layers, dynamic dispatch, and introspection are slower than direct code. When your elegant framework is 10x slower than hand-written code, you need performance techniques.

---

[Chapter 14: Performance: Write Less, Run Faster →](chapter-14-performance.md)

# Chapter 3: Class Decorators

[← Chapter 2: Decorators That Write Code](chapter-02-decorators.md) | [Chapter 4: Descriptors →](chapter-04-descriptors.md)

---

## The Problem

FrameForge has 20 model classes. Every single one needs:

```python
class User:
    def __init__(self, name, email, age):
        self.name = name
        self.email = email
        self.age = age

    def __repr__(self):
        return f"User(name={self.name!r}, email={self.email!r}, age={self.age!r})"

    def __eq__(self, other):
        if not isinstance(other, User):
            return NotImplemented
        return (self.name, self.email, self.age) == (other.name, other.email, other.age)

    def to_dict(self):
        return {"name": self.name, "email": self.email, "age": self.age}

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["email"], data["age"])
```

That's 20 lines of boilerplate per class. With 20 classes, that's 400 lines of repetitive code. Every time you add a field, you update `__init__`, `__repr__`, `__eq__`, `to_dict`, and `from_dict`. Five places. Every time.

Vera: "A class decorator can inject all of that. The user declares fields, the decorator writes the methods."

## The Core Idea

A class decorator takes a class and returns a (modified) class:

```python
def my_class_decorator(cls):
    # modify cls or return a new class
    cls.decorated = True
    return cls

@my_class_decorator
class MyClass:
    pass

MyClass.decorated  # True
```

## Solution: @auto_repr

Start simple. Inject `__repr__` based on `__init__` parameters:

```python
import inspect

def auto_repr(cls):
    """Generate __repr__ from __init__ parameters."""
    params = list(inspect.signature(cls.__init__).parameters.keys())
    params = [p for p in params if p != 'self']

    def __repr__(self):
        args = ", ".join(f"{p}={getattr(self, p)!r}" for p in params)
        return f"{cls.__name__}({args})"

    cls.__repr__ = __repr__
    return cls

@auto_repr
class User:
    def __init__(self, name, email, age):
        self.name = name
        self.email = email
        self.age = age

print(User("Alice", "alice@dev.io", 30))
# User(name='Alice', email='alice@dev.io', age=30)
```

One decorator. Never write `__repr__` by hand again.

## Solution: @serializable

Inject `to_dict()` and `from_dict()`:

```python
import inspect

def serializable(cls):
    """Add to_dict() and from_dict() based on __init__ parameters."""
    params = list(inspect.signature(cls.__init__).parameters.keys())
    params = [p for p in params if p != 'self']

    def to_dict(self):
        return {p: getattr(self, p) for p in params}

    @classmethod
    def from_dict(klass, data):
        return klass(**{p: data[p] for p in params})

    cls.to_dict = to_dict
    cls.from_dict = from_dict
    return cls

@serializable
@auto_repr
class Order:
    def __init__(self, order_id, total, status):
        self.order_id = order_id
        self.total = total
        self.status = status

order = Order("ORD-001", 99.99, "pending")
data = order.to_dict()
# {'order_id': 'ORD-001', 'total': 99.99, 'status': 'pending'}

restored = Order.from_dict(data)
# Order(order_id='ORD-001', total=99.99, status='pending')
```

## Solution: @singleton

Ensure only one instance ever exists:

```python
def singleton(cls):
    """Only one instance of this class can exist."""
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    get_instance.__name__ = cls.__name__
    get_instance.__doc__ = cls.__doc__
    return get_instance

@singleton
class DatabaseConnection:
    def __init__(self, url):
        self.url = url
        print(f"Connecting to {url}...")

db1 = DatabaseConnection("postgres://localhost/app")
# Connecting to postgres://localhost/app...
db2 = DatabaseConnection("postgres://localhost/app")
# (no output — reuses existing instance)
assert db1 is db2  # True
```

## Solution: @register

Auto-register classes in a global registry:

```python
REGISTRY = {}

def register(cls):
    """Register class by its name in the global registry."""
    REGISTRY[cls.__name__] = cls
    return cls

@register
class JsonHandler:
    def parse(self, data):
        import json
        return json.loads(data)

@register
class XmlHandler:
    def parse(self, data):
        from xml.etree import ElementTree
        return ElementTree.fromstring(data)

@register
class CsvHandler:
    def parse(self, data):
        import csv, io
        return list(csv.reader(io.StringIO(data)))

# Discover handlers at runtime:
print(REGISTRY)
# {'JsonHandler': <class 'JsonHandler'>, 'XmlHandler': ...}

# Instantiate by name (from config, user input, etc.):
handler = REGISTRY["JsonHandler"]()
handler.parse('{"key": "value"}')
```

## The Full Solution: @model

Combine everything into one decorator:

```python
import inspect

def model(cls):
    """Full model decorator: __repr__, __eq__, to_dict, from_dict."""
    params = list(inspect.signature(cls.__init__).parameters.keys())
    params = [p for p in params if p != 'self']

    # __repr__
    def __repr__(self):
        args = ", ".join(f"{p}={getattr(self, p)!r}" for p in params)
        return f"{cls.__name__}({args})"

    # __eq__
    def __eq__(self, other):
        if not isinstance(other, cls):
            return NotImplemented
        return all(getattr(self, p) == getattr(other, p) for p in params)

    # __hash__ (needed if __eq__ is defined)
    def __hash__(self):
        return hash(tuple(getattr(self, p) for p in params))

    # to_dict
    def to_dict(self):
        return {p: getattr(self, p) for p in params}

    # from_dict
    @classmethod
    def from_dict(klass, data):
        return klass(**{p: data[p] for p in params})

    cls.__repr__ = __repr__
    cls.__eq__ = __eq__
    cls.__hash__ = __hash__
    cls.to_dict = to_dict
    cls.from_dict = from_dict
    return cls

@model
class User:
    def __init__(self, name, email, age):
        self.name = name
        self.email = email
        self.age = age

u1 = User("Alice", "alice@dev.io", 30)
u2 = User("Alice", "alice@dev.io", 30)
print(u1)          # User(name='Alice', email='alice@dev.io', age=30)
print(u1 == u2)    # True
print(u1.to_dict())  # {'name': 'Alice', 'email': 'alice@dev.io', 'age': 30}
```

20 classes × 0 lines of boilerplate = done.

## Class Decorator vs dataclass vs Metaclass

When to use which:

```python
# dataclass — when you just need a data container
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

# Class decorator — when you need custom logic beyond what dataclass provides
@model
class User:
    def __init__(self, name, email, age):
        self.name = name
        self.email = email
        self.age = age

# Metaclass — when you need to intercept class CREATION
# (validate fields, register subclasses, modify the class namespace)
# We'll cover this in Chapter 5
```

**Rule of thumb:**
- Need `__repr__`, `__eq__`, `__init__` generated? → `@dataclass`
- Need custom method injection, registration, or transformation? → class decorator
- Need to control what happens when `class Foo:` is executed? → metaclass

## Parameterized Class Decorators

Just like function decorators, class decorators can take parameters:

```python
def add_methods(*method_names):
    """Decorator factory: add stub methods to a class."""
    def decorator(cls):
        for name in method_names:
            if not hasattr(cls, name):
                def make_method(method_name):
                    def method(self):
                        raise NotImplementedError(
                            f"{cls.__name__}.{method_name}() not implemented"
                        )
                    method.__name__ = method_name
                    return method
                setattr(cls, name, make_method(name))
        return cls
    return decorator

@add_methods("save", "delete", "refresh")
class BaseModel:
    pass

m = BaseModel()
m.save()  # NotImplementedError: BaseModel.save() not implemented
```

## Modifying __init__

A class decorator can wrap `__init__` to add validation:

```python
def validate_types(cls):
    """Validate __init__ arguments match type annotations."""
    original_init = cls.__init__
    hints = cls.__init__.__annotations__

    def new_init(self, *args, **kwargs):
        # Bind arguments to parameter names
        import inspect
        sig = inspect.signature(original_init)
        bound = sig.bind(self, *args, **kwargs)
        bound.apply_defaults()

        for param, value in bound.arguments.items():
            if param == 'self':
                continue
            if param in hints and not isinstance(value, hints[param]):
                raise TypeError(
                    f"{cls.__name__}.__init__(): '{param}' must be "
                    f"{hints[param].__name__}, got {type(value).__name__}"
                )
        original_init(self, *args, **kwargs)

    cls.__init__ = new_init
    return cls

@validate_types
class Config:
    def __init__(self, host: str, port: int, debug: bool):
        self.host = host
        self.port = port
        self.debug = debug

Config("localhost", 8080, True)   # Works
Config("localhost", "8080", True)  # TypeError: 'port' must be int, got str
```

## What You Learned

- **Class decorators take a class and return a (modified) class**
- **`@auto_repr`** — generate `__repr__` from `__init__` parameters
- **`@serializable`** — inject `to_dict()` and `from_dict()`
- **`@singleton`** — ensure only one instance exists
- **`@register`** — auto-register classes in a global registry
- **Parameterized class decorators** work like function decorator factories
- **Class decorators can modify `__init__`** — add validation, logging, etc.
- **Use `@dataclass` for simple cases**, class decorators for custom transformations

## Key Insight

> Class decorators modify classes after they're created. But what if you need to control attribute access — validate on assignment, compute on read, share behavior across unrelated classes? That's descriptors.

---

[Chapter 4: Descriptors: Reusable Properties →](chapter-04-descriptors.md)

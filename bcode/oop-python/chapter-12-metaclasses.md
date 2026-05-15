# Chapter 12: Metaclasses — Class Creation Hooks

[← Chapter 11: Descriptors](chapter-11-descriptors.md) | [Chapter 13: Dataclasses →](chapter-13-dataclasses.md)

---

## The Problem

ShipFast has a plugin system for shipping providers. Each provider is a class:

```python
class StandardShipping(ShippingStrategy):
    name = "standard"
    def calculate(self, weight): ...

class ExpressShipping(ShippingStrategy):
    name = "express"
    def calculate(self, weight): ...

class DroneShipping(ShippingStrategy):
    name = "drone"
    def calculate(self, weight): ...
```

The routing engine needs to discover all available providers. Marcus's solution:

```python
# providers.py
SHIPPING_REGISTRY = {
    "standard": StandardShipping,
    "express": ExpressShipping,
    "drone": DroneShipping,
}
```

Problem: every time someone adds a new provider, they forget to add it to the registry. The class exists but the system doesn't know about it. Dana finds out when a customer selects "freight" shipping and gets a `KeyError`.

Dana: "The registry should build itself. When you create a subclass, it should automatically register."

## `__init_subclass__`: The Simple Solution

Python 3.6+ provides `__init_subclass__` — a hook that runs every time a class is subclassed:

```python
class ShippingStrategy:
    """Base class that auto-registers all subclasses."""

    _registry = {}

    def __init_subclass__(cls, **kwargs):
        """Called automatically when a subclass is defined."""
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "name"):
            ShippingStrategy._registry[cls.name] = cls

    @classmethod
    def get_provider(cls, name):
        """Look up a provider by name."""
        if name not in cls._registry:
            available = ", ".join(sorted(cls._registry.keys()))
            raise ValueError(f"Unknown provider '{name}'. Available: {available}")
        return cls._registry[name]

    @classmethod
    def list_providers(cls):
        """List all registered providers."""
        return dict(cls._registry)
```

Now subclasses register themselves just by existing:

```python
class StandardShipping(ShippingStrategy):
    name = "standard"

    def calculate(self, weight):
        return 5.00 + (weight * 2.50)

class ExpressShipping(ShippingStrategy):
    name = "express"

    def calculate(self, weight):
        return 15.00 + (weight * 5.00)

class DroneShipping(ShippingStrategy):
    name = "drone"

    def calculate(self, weight):
        return 8.00 + (weight * 3.00)
```

```python
# Auto-discovered — no manual registry!
print(ShippingStrategy.list_providers())
# {'standard': <class 'StandardShipping'>, 'express': <class 'ExpressShipping'>, 'drone': <class 'DroneShipping'>}

# Look up and instantiate
provider_cls = ShippingStrategy.get_provider("express")
provider = provider_cls()
print(provider.calculate(3.0))  # 30.00
```

Add a new provider? Just create the class. It registers itself:

```python
class FreightShipping(ShippingStrategy):
    name = "freight"

    def calculate(self, weight):
        return 25.00 + (weight * 1.50)

# Already registered!
print(ShippingStrategy.get_provider("freight"))
# <class 'FreightShipping'>
```

## `__init_subclass__` with Parameters

You can pass keyword arguments to the subclass definition:

```python
class EventHandler:
    """Base class for event handlers with auto-registration."""

    _handlers = {}

    def __init_subclass__(cls, event=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if event:
            EventHandler._handlers.setdefault(event, []).append(cls)

    @classmethod
    def dispatch(cls, event, *args, **kwargs):
        """Call all handlers registered for an event."""
        handlers = cls._handlers.get(event, [])
        for handler_cls in handlers:
            handler = handler_cls()
            handler.handle(*args, **kwargs)


class PackageShippedNotifier(EventHandler, event="package_shipped"):
    def handle(self, package):
        print(f"📧 Notification: {package.id} has shipped")

class PackageShippedLogger(EventHandler, event="package_shipped"):
    def handle(self, package):
        print(f"📝 Log: {package.id} shipped at {time.time()}")

class PackageDeliveredNotifier(EventHandler, event="package_delivered"):
    def handle(self, package):
        print(f"📧 Notification: {package.id} delivered")
```

```python
# Dispatch triggers all registered handlers
EventHandler.dispatch("package_shipped", some_package)
# 📧 Notification: PKG-001 has shipped
# 📝 Log: PKG-001 shipped at 1705234567.89
```

## When You Actually Need Metaclasses

`__init_subclass__` handles 90% of class-creation hooks. Metaclasses are for the remaining 10% — when you need to modify the class **itself** during creation.

A metaclass is a class whose instances are classes. `type` is the default metaclass:

```python
# These are equivalent:
class Package:
    weight = 0

# Same as:
Package = type("Package", (), {"weight": 0})
```

### A Custom Metaclass

```python
class ValidatedMeta(type):
    """Metaclass that ensures all subclasses define required class attributes."""

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)

        # Skip the base class itself
        if bases:
            required = getattr(cls, "_required_attrs", [])
            for attr in required:
                if attr not in namespace:
                    raise TypeError(
                        f"Class '{name}' must define '{attr}' "
                        f"(required by {bases[0].__name__})"
                    )
        return cls


class ShippingProvider(metaclass=ValidatedMeta):
    _required_attrs = ["name", "calculate"]

class ValidProvider(ShippingProvider):
    name = "valid"

    def calculate(self, weight):
        return weight * 2.0

class InvalidProvider(ShippingProvider):
    # Missing 'name' and 'calculate'!
    pass
# TypeError: Class 'InvalidProvider' must define 'name' (required by ShippingProvider)
```

The error happens at **class definition time** — not even at instantiation. The class itself can't exist without the required attributes.

## Metaclass vs `__init_subclass__` vs ABC

| Feature | `__init_subclass__` | ABC | Metaclass |
|---|---|---|---|
| Complexity | Low | Medium | High |
| Error timing | Class definition | Instantiation | Class definition |
| Use case | Registration, validation | Interface enforcement | Deep class modification |
| Inheritance | Automatic | Requires explicit ABC base | Requires `metaclass=` |
| Python version | 3.6+ | 2.6+ | Always |

Decision tree:
1. Need to auto-register subclasses? → `__init_subclass__`
2. Need to enforce method implementation? → ABC
3. Need to modify class structure at creation? → Metaclass
4. Not sure? → `__init_subclass__` (simplest)

## Real-World Example: Serializable Models

```python
class Serializable:
    """Auto-generates to_dict/from_dict based on __init__ parameters."""

    _model_registry = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._model_registry[cls.__name__] = cls

    def to_dict(self):
        """Serialize to dictionary using instance attributes."""
        data = {"_type": type(self).__name__}
        data.update(self.__dict__)
        return data

    @classmethod
    def from_dict(cls, data):
        """Deserialize from dictionary."""
        type_name = data.pop("_type", cls.__name__)
        target_cls = cls._model_registry.get(type_name, cls)
        obj = object.__new__(target_cls)
        obj.__dict__.update(data)
        return obj


class Package(Serializable):
    def __init__(self, id, weight, destination):
        self.id = id
        self.weight = weight
        self.destination = destination
        self.status = "pending"

class Driver(Serializable):
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity
```

```python
pkg = Package("PKG-001", 3.5, "123 Main St")
data = pkg.to_dict()
# {'_type': 'Package', 'id': 'PKG-001', 'weight': 3.5, 'destination': '123 Main St', 'status': 'pending'}

restored = Serializable.from_dict(data)
print(type(restored).__name__)  # Package
print(restored.weight)          # 3.5
```

## Dana's Advice on Metaclasses

"In 8 years of Python, I've needed a custom metaclass exactly twice. Both times I later replaced it with `__init_subclass__`. Use metaclasses when you're building a framework — Django models, SQLAlchemy, pytest fixtures. For application code, `__init_subclass__` does the job."

## What You Learned

- **`__init_subclass__`** — hook that runs when a class is subclassed (Python 3.6+)
- **Auto-registration** — subclasses register themselves in a registry automatically
- **Keyword arguments in class definition** — `class X(Base, event="foo")`
- **Metaclasses** — classes that create classes (`type` is the default metaclass)
- **`type(name, bases, namespace)`** — programmatic class creation
- **When to use what** — `__init_subclass__` for 90% of cases, metaclass for framework-level magic

The plugin system is self-maintaining. New providers register automatically. But you're still writing `__init__`, `__repr__`, and `__eq__` boilerplate for every simple data class. There's a decorator that eliminates all of it.

---

[← Chapter 11: Descriptors](chapter-11-descriptors.md) | [Chapter 13: Dataclasses →](chapter-13-dataclasses.md)

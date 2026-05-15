# Chapter 11: Descriptors & Properties — Reusable Validation

[← Chapter 10: Class Machinery](chapter-10-classmethod.md) | [Chapter 12: Metaclasses →](chapter-12-metaclasses.md)

---

## The Problem

You've written the same validation pattern in twelve classes:

```python
class Package:
    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("Must be a number")
        if value <= 0:
            raise ValueError("Must be positive")
        self._weight = float(value)

class Driver:
    @property
    def capacity(self):
        return self._capacity

    @capacity.setter
    def capacity(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("Must be a number")
        if value <= 0:
            raise ValueError("Must be positive")
        self._capacity = float(value)

class Route:
    @property
    def max_weight(self):
        return self._max_weight

    @max_weight.setter
    def max_weight(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("Must be a number")
        if value <= 0:
            raise ValueError("Must be positive")
        self._max_weight = float(value)
```

Three classes, same validation, copy-pasted. And there are nine more with "must be a non-empty string" and "must be one of these values." Every time you fix a bug in the validation, you fix it in one place and forget the other eleven.

Dana: "You need reusable validators. Not properties — descriptors."

## What Is a Descriptor?

A descriptor is any object that implements `__get__`, `__set__`, or `__delete__`. When you assign a descriptor instance as a **class variable**, Python intercepts attribute access and calls the descriptor's methods instead.

```python
class PositiveNumber:
    """Descriptor that validates a value is a positive number."""

    def __set_name__(self, owner, name):
        """Called when the descriptor is assigned to a class variable."""
        self.public_name = name
        self.private_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        """Called when the attribute is accessed."""
        if obj is None:
            return self  # Accessed on the class, not an instance
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        """Called when the attribute is assigned."""
        if not isinstance(value, (int, float)):
            raise TypeError(f"{self.public_name} must be a number, got {type(value).__name__}")
        if value <= 0:
            raise ValueError(f"{self.public_name} must be positive, got {value}")
        setattr(obj, self.private_name, float(value))
```

Now use it in any class:

```python
class Package:
    weight = PositiveNumber()

    def __init__(self, weight, destination):
        self.weight = weight  # Goes through PositiveNumber.__set__
        self.destination = destination

class Driver:
    capacity = PositiveNumber()

    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity  # Same validator, zero duplication

class Route:
    max_weight = PositiveNumber()
    max_distance = PositiveNumber()

    def __init__(self, max_weight, max_distance):
        self.max_weight = max_weight
        self.max_distance = max_distance
```

```python
pkg = Package(3.5, "123 Main St")
print(pkg.weight)  # 3.5

pkg.weight = -1
# ValueError: weight must be positive, got -1

driver = Driver("Alice", 50.0)
driver.capacity = "lots"
# TypeError: capacity must be a number, got str
```

One validator class. Used everywhere. Fix a bug once, fixed everywhere.

## How `__set_name__` Works

When Python creates a class, it calls `__set_name__` on every descriptor it finds:

```python
class Package:
    weight = PositiveNumber()  # Python calls: PositiveNumber.__set_name__(self, Package, "weight")
```

This tells the descriptor its own name (`"weight"`), so it can store data under `_weight` on the instance and produce useful error messages.

## Building a Descriptor Library

### NonEmptyString

```python
class NonEmptyString:
    """Descriptor that validates a value is a non-empty string."""

    def __init__(self, max_length=None):
        self.max_length = max_length

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        if not isinstance(value, str):
            raise TypeError(f"{self.public_name} must be a string, got {type(value).__name__}")
        value = value.strip()
        if not value:
            raise ValueError(f"{self.public_name} cannot be empty")
        if self.max_length and len(value) > self.max_length:
            raise ValueError(f"{self.public_name} cannot exceed {self.max_length} characters")
        setattr(obj, self.private_name, value)
```

### OneOf

```python
class OneOf:
    """Descriptor that validates a value is from an allowed set."""

    def __init__(self, *options):
        self.options = set(options)

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.private_name, None)

    def __set__(self, obj, value):
        if value not in self.options:
            raise ValueError(
                f"{self.public_name} must be one of {sorted(self.options)}, got {value!r}"
            )
        setattr(obj, self.private_name, value)
```

### BoundedNumber

```python
class BoundedNumber:
    """Descriptor for a number within a range."""

    def __init__(self, min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        if not isinstance(value, (int, float)):
            raise TypeError(f"{self.public_name} must be a number")
        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"{self.public_name} must be >= {self.min_value}, got {value}")
        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"{self.public_name} must be <= {self.max_value}, got {value}")
        setattr(obj, self.private_name, float(value))
```

## Using the Descriptor Library

```python
class Package:
    weight = BoundedNumber(min_value=0.01, max_value=500.0)
    destination = NonEmptyString(max_length=200)
    sender = NonEmptyString(max_length=100)
    status = OneOf("pending", "in_transit", "delivered", "returned", "lost")

    def __init__(self, weight, destination, sender):
        self.weight = weight
        self.destination = destination
        self.sender = sender
        self.status = "pending"


class Driver:
    name = NonEmptyString(max_length=100)
    capacity = BoundedNumber(min_value=0.1, max_value=10000.0)
    status = OneOf("available", "on_route", "off_duty")

    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity
        self.status = "available"


class Route:
    name = NonEmptyString(max_length=50)
    max_weight = BoundedNumber(min_value=1.0, max_value=50000.0)
    priority = OneOf("low", "normal", "high", "critical")

    def __init__(self, name, max_weight, priority="normal"):
        self.name = name
        self.max_weight = max_weight
        self.priority = priority
```

```python
pkg = Package(3.5, "123 Main St", "Alice")
pkg.status = "banana"
# ValueError: status must be one of ['delivered', 'in_transit', 'lost', 'pending', 'returned'], got 'banana'

driver = Driver("", 50.0)
# ValueError: name cannot be empty

route = Route("Downtown Loop", 0.5, "normal")
# ValueError: max_weight must be >= 1.0, got 0.5
```

## How Properties Are Actually Descriptors

The `@property` decorator creates a descriptor under the hood:

```python
# This:
class Package:
    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, value):
        self._weight = value

# Is equivalent to:
class Package:
    def _get_weight(self):
        return self._weight

    def _set_weight(self, value):
        self._weight = value

    weight = property(_get_weight, _set_weight)
```

`property` is just a built-in descriptor class. When you write custom descriptors, you're using the same mechanism — just with reusable logic.

## Descriptor Protocol Summary

```python
class MyDescriptor:
    def __set_name__(self, owner, name):
        """Called once when the class is created."""
        # owner = the class this descriptor is on
        # name = the attribute name it's assigned to

    def __get__(self, obj, objtype=None):
        """Called when the attribute is read."""
        # obj = the instance (None if accessed on class)
        # objtype = the class

    def __set__(self, obj, value):
        """Called when the attribute is assigned."""
        # obj = the instance
        # value = the value being assigned

    def __delete__(self, obj):
        """Called when the attribute is deleted (del obj.attr)."""
```

## What You Learned

- **Descriptor protocol** — `__get__`, `__set__`, `__set_name__` for intercepting attribute access
- **Reusable validators** — write once, use in any class
- **`__set_name__`** — automatically learns the attribute name it's assigned to
- **Data descriptor** — implements `__set__` (takes priority over instance `__dict__`)
- **Properties are descriptors** — `@property` is syntactic sugar for the descriptor protocol
- **Descriptor library** — `PositiveNumber`, `NonEmptyString`, `OneOf`, `BoundedNumber`

Validation is now DRY. One fix propagates everywhere. But there's another pattern emerging: you need to automatically discover all `ShippingStrategy` subclasses for a plugin system. Every time someone adds a new strategy, they forget to register it.

You need class creation hooks.

---

[← Chapter 10: Class Machinery](chapter-10-classmethod.md) | [Chapter 12: Metaclasses →](chapter-12-metaclasses.md)

# Chapter 4: Descriptors: Reusable Properties

[← Chapter 3: Class Decorators](chapter-03-class-decorators.md) | [Chapter 5: Metaclasses →](chapter-05-metaclasses.md)

---

## The Problem

FrameForge's model classes need field validation. Every class validates the same patterns:

```python
class Product:
    def __init__(self, name, price, category, rating):
        # Validate non-empty string
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string")
        self.name = name

        # Validate positive number
        if not isinstance(price, (int, float)) or price <= 0:
            raise ValueError("price must be a positive number")
        self.price = price

        # Validate one of choices
        if category not in ("electronics", "clothing", "food"):
            raise ValueError(f"category must be one of: electronics, clothing, food")
        self.category = category

        # Validate bounded number
        if not isinstance(rating, (int, float)) or not (0 <= rating <= 5):
            raise ValueError("rating must be between 0 and 5")
        self.rating = rating

class Employee:
    def __init__(self, name, salary, department, performance):
        # Same validation patterns, different values...
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string")
        self.name = name

        if not isinstance(salary, (int, float)) or salary <= 0:
            raise ValueError("salary must be a positive number")
        self.salary = salary
        # ... 12 more lines of the same patterns
```

Same validation logic, copy-pasted across 12 classes. Change the error message format? Update 12 files.

Vera: "Write the validation once. Use it everywhere. That's what descriptors are for."

## The Core Idea

A descriptor is an object that defines how attribute access works. It implements `__get__`, `__set__`, or `__delete__`:

```python
class Descriptor:
    def __get__(self, obj, objtype=None):
        # Called when attribute is read: instance.attr
        ...

    def __set__(self, obj, value):
        # Called when attribute is assigned: instance.attr = value
        ...

    def __delete__(self, obj):
        # Called when attribute is deleted: del instance.attr
        ...

    def __set_name__(self, owner, name):
        # Called at class creation time — tells descriptor its own name
        ...
```

## @property Is Just a Descriptor

You already use descriptors without knowing it:

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("radius must be non-negative")
        self._radius = value
```

`property` is a built-in descriptor class. But `@property` isn't reusable — you write a getter and setter for every attribute. Descriptors let you write the validation once.

## Solution: PositiveNumber Descriptor

```python
class PositiveNumber:
    """Descriptor that ensures a value is a positive number."""

    def __set_name__(self, owner, name):
        # Called automatically when the class is created
        # owner = the class, name = the attribute name
        self.name = name
        self.storage_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self  # Accessed from the class, not an instance
        return getattr(obj, self.storage_name, None)

    def __set__(self, obj, value):
        if not isinstance(value, (int, float)):
            raise TypeError(f"{self.name} must be a number, got {type(value).__name__}")
        if value <= 0:
            raise ValueError(f"{self.name} must be positive, got {value}")
        setattr(obj, self.storage_name, value)

# Usage — write once, use everywhere:
class Product:
    price = PositiveNumber()
    weight = PositiveNumber()

    def __init__(self, name, price, weight):
        self.name = name
        self.price = price    # Triggers PositiveNumber.__set__
        self.weight = weight  # Triggers PositiveNumber.__set__

p = Product("Widget", 9.99, 0.5)
p.price = -1  # ValueError: price must be positive, got -1
p.price = "free"  # TypeError: price must be a number, got str
```

The magic: `__set_name__` is called automatically by Python when the class is created. The descriptor knows its own name without you telling it.

## Solution: NonEmptyString

```python
class NonEmptyString:
    """Descriptor that ensures a non-empty string value."""

    def __set_name__(self, owner, name):
        self.name = name
        self.storage_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.storage_name, None)

    def __set__(self, obj, value):
        if not isinstance(value, str):
            raise TypeError(f"{self.name} must be a string, got {type(value).__name__}")
        if not value.strip():
            raise ValueError(f"{self.name} must not be empty")
        setattr(obj, self.storage_name, value.strip())
```

## Solution: OneOf (Choices)

```python
class OneOf:
    """Descriptor that restricts values to a set of choices."""

    def __init__(self, *choices):
        self.choices = choices

    def __set_name__(self, owner, name):
        self.name = name
        self.storage_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.storage_name, None)

    def __set__(self, obj, value):
        if value not in self.choices:
            raise ValueError(
                f"{self.name} must be one of {self.choices}, got {value!r}"
            )
        setattr(obj, self.storage_name, value)
```

## Solution: Bounded (Range Validation)

```python
class Bounded:
    """Descriptor that ensures a number is within a range."""

    def __init__(self, min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value

    def __set_name__(self, owner, name):
        self.name = name
        self.storage_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.storage_name, None)

    def __set__(self, obj, value):
        if not isinstance(value, (int, float)):
            raise TypeError(f"{self.name} must be a number")
        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"{self.name} must be >= {self.min_value}, got {value}")
        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"{self.name} must be <= {self.max_value}, got {value}")
        setattr(obj, self.storage_name, value)
```

## The Elegant Version

Now our 12 classes go from walls of validation code to clean declarations:

```python
class Product:
    name = NonEmptyString()
    price = PositiveNumber()
    category = OneOf("electronics", "clothing", "food", "home")
    rating = Bounded(min_value=0, max_value=5)

    def __init__(self, name, price, category, rating):
        self.name = name        # Validated by NonEmptyString
        self.price = price      # Validated by PositiveNumber
        self.category = category  # Validated by OneOf
        self.rating = rating    # Validated by Bounded

class Employee:
    name = NonEmptyString()
    salary = PositiveNumber()
    department = OneOf("engineering", "sales", "marketing", "hr")
    performance = Bounded(min_value=1, max_value=10)

    def __init__(self, name, salary, department, performance):
        self.name = name
        self.salary = salary
        self.department = department
        self.performance = performance
```

Validation logic written once. Used in 12 classes. Change the error format in one place.

## Data Descriptors vs Non-Data Descriptors

Python distinguishes between two types:

```python
# Data descriptor: defines __set__ (or __delete__)
# Takes priority over instance __dict__
class DataDescriptor:
    def __get__(self, obj, objtype=None):
        return "from descriptor"
    def __set__(self, obj, value):
        pass

# Non-data descriptor: only defines __get__
# Instance __dict__ takes priority
class NonDataDescriptor:
    def __get__(self, obj, objtype=None):
        return "from descriptor"

class MyClass:
    data = DataDescriptor()
    non_data = NonDataDescriptor()

obj = MyClass()
obj.__dict__['data'] = "from dict"
obj.__dict__['non_data'] = "from dict"

print(obj.data)      # "from descriptor" — data descriptor wins
print(obj.non_data)  # "from dict" — instance dict wins
```

**Attribute lookup order:**
1. Data descriptors (have `__set__`)
2. Instance `__dict__`
3. Non-data descriptors (only `__get__`)
4. `__getattr__` (fallback)

## A Generic Typed Descriptor

```python
class Typed:
    """Generic descriptor that enforces a type."""

    def __init__(self, expected_type, default=None):
        self.expected_type = expected_type
        self.default = default

    def __set_name__(self, owner, name):
        self.name = name
        self.storage_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.storage_name, self.default)

    def __set__(self, obj, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name} must be {self.expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
        setattr(obj, self.storage_name, value)

class Config:
    host = Typed(str, default="localhost")
    port = Typed(int, default=8080)
    debug = Typed(bool, default=False)

    def __init__(self, host="localhost", port=8080, debug=False):
        self.host = host
        self.port = port
        self.debug = debug

c = Config()
c.port = "not a number"  # TypeError: port must be int, got str
```

## Composing Descriptors with Validation Chains

```python
class Validated:
    """Base descriptor with composable validators."""

    def __init__(self, *validators):
        self.validators = validators

    def __set_name__(self, owner, name):
        self.name = name
        self.storage_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.storage_name, None)

    def __set__(self, obj, value):
        for validator in self.validators:
            value = validator(self.name, value)  # validators can transform
        setattr(obj, self.storage_name, value)

# Validator functions:
def is_string(name, value):
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    return value

def not_empty(name, value):
    if not value.strip():
        raise ValueError(f"{name} must not be empty")
    return value.strip()

def max_length(n):
    def check(name, value):
        if len(value) > n:
            raise ValueError(f"{name} must be <= {n} chars, got {len(value)}")
        return value
    return check

# Compose validators:
class User:
    name = Validated(is_string, not_empty, max_length(100))
    email = Validated(is_string, not_empty, max_length(255))
```

## What You Learned

- **Descriptors control attribute access** via `__get__`, `__set__`, `__delete__`
- **`__set_name__`** tells the descriptor its own attribute name automatically
- **Data descriptors** (with `__set__`) override instance `__dict__`
- **Non-data descriptors** (only `__get__`) are overridden by instance `__dict__`
- **`@property` is a descriptor** — but not reusable across classes
- **Custom descriptors** (`PositiveNumber`, `OneOf`, `Bounded`, `Typed`) are reusable validation
- **Attribute lookup order**: data descriptor → instance dict → non-data descriptor → `__getattr__`

## Key Insight

> Descriptors let you write validation once and use it in any class. But notice: you still write `__init__` by hand. What if the framework could look at your descriptor declarations and generate `__init__` automatically? That's what metaclasses do — they intercept class creation and transform the class before it exists.

---

[Chapter 5: Metaclasses: Classes That Build Classes →](chapter-05-metaclasses.md)

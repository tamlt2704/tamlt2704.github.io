# Chapter 5: Metaclasses: Classes That Build Classes

[← Chapter 4: Descriptors](chapter-04-descriptors.md) | [Chapter 6: Dynamic Dispatch →](chapter-06-dynamic-attrs.md)

---

## The Problem

FrameForge's model system is growing. You have descriptors for validation (Chapter 4), but users still write too much:

```python
class User:
    name = NonEmptyString()
    email = NonEmptyString()
    age = PositiveNumber()

    # Still writing __init__ by hand!
    def __init__(self, name, email, age):
        self.name = name
        self.email = email
        self.age = age
```

And Vera wants more:
- Auto-generate `__init__` from field declarations
- Auto-register every model subclass in a global registry
- Validate that field names don't conflict with reserved words
- All of this should happen at class creation time — not at instantiation

"I want users to write `class User(Model): name = StringField()` and get everything else for free. The class itself should be transformed the moment it's defined."

## The Simpler Path: __init_subclass__

Before reaching for metaclasses, try `__init_subclass__`. It handles 90% of cases:

```python
REGISTRY = {}

class Model:
    """Base class that auto-registers subclasses and generates __init__."""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register the subclass
        REGISTRY[cls.__name__] = cls
        # Collect field descriptors
        fields = []
        for name, value in cls.__dict__.items():
            if isinstance(value, Field):
                fields.append(name)
        cls._fields = fields
        # Generate __init__ if not explicitly defined
        if '__init__' not in cls.__dict__:
            def make_init(field_names):
                def __init__(self, **kwargs):
                    for fname in field_names:
                        if fname not in kwargs:
                            raise TypeError(f"Missing required field: {fname}")
                        setattr(self, fname, kwargs[fname])
                return __init__
            cls.__init__ = make_init(fields)

class Field:
    def __set_name__(self, owner, name):
        self.name = name
        self.storage_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.storage_name, None)

    def __set__(self, obj, value):
        setattr(obj, self.storage_name, value)

class StringField(Field):
    def __set__(self, obj, value):
        if not isinstance(value, str):
            raise TypeError(f"{self.name} must be a string")
        setattr(obj, self.storage_name, value)

class IntField(Field):
    def __init__(self, min_value=None):
        self.min_value = min_value

    def __set__(self, obj, value):
        if not isinstance(value, int):
            raise TypeError(f"{self.name} must be an int")
        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"{self.name} must be >= {self.min_value}")
        setattr(obj, self.storage_name, value)

# Now users write:
class User(Model):
    name = StringField()
    email = StringField()
    age = IntField(min_value=0)

# And get:
u = User(name="Alice", email="alice@dev.io", age=30)
print(REGISTRY)  # {'User': <class 'User'>}
print(User._fields)  # ['name', 'email', 'age']
```

`__init_subclass__` is called every time a class inherits from `Model`. No metaclass needed.

## When You Actually Need a Metaclass

`__init_subclass__` can't:
- Control the class namespace before the class body executes
- Modify `__new__` behavior of the class creation itself
- Use `__prepare__` to provide a custom namespace (e.g., ordered dict, recording dict)

For FrameForge, we need `__prepare__` to track field declaration order (pre-Python 3.7 dicts weren't ordered):

```python
class ModelMeta(type):
    """Metaclass that transforms model classes at creation time."""

    @classmethod
    def __prepare__(mcs, name, bases):
        # Return a custom namespace that tracks insertion order
        # (In 3.7+ dicts are ordered, but this shows the pattern)
        return {}

    def __new__(mcs, name, bases, namespace):
        # Called BEFORE __init__ — creates the class object
        cls = super().__new__(mcs, name, bases, namespace)

        # Skip the base Model class itself
        if name == 'Model':
            return cls

        # Collect fields
        fields = {}
        for key, value in namespace.items():
            if isinstance(value, Field):
                fields[key] = value
        cls._fields = fields

        # Generate __init__
        if '__init__' not in namespace:
            field_names = list(fields.keys())
            def __init__(self, **kwargs):
                for fname in field_names:
                    if fname in kwargs:
                        setattr(self, fname, kwargs[fname])
                    elif hasattr(fields[fname], 'default'):
                        setattr(self, fname, fields[fname].default)
                    else:
                        raise TypeError(f"Missing required field: {fname}")
            cls.__init__ = __init__

        # Generate __repr__
        def __repr__(self):
            parts = ", ".join(
                f"{k}={getattr(self, k)!r}" for k in fields
            )
            return f"{name}({parts})"
        cls.__repr__ = __repr__

        # Register
        if not hasattr(cls, '_registry'):
            cls._registry = {}
        cls._registry[name] = cls

        return cls

    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)
        # Post-creation hook — class already exists here


class Model(metaclass=ModelMeta):
    """Base model class. Subclasses get auto-generated methods."""
    pass
```

## Using the Metaclass

```python
class Field:
    def __init__(self, field_type=None, default=None, required=True):
        self.field_type = field_type
        self.default = default
        self.required = required

    def __set_name__(self, owner, name):
        self.name = name
        self.storage_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.storage_name, self.default)

    def __set__(self, obj, value):
        if self.field_type and not isinstance(value, self.field_type):
            raise TypeError(
                f"{self.name} must be {self.field_type.__name__}, "
                f"got {type(value).__name__}"
            )
        setattr(obj, self.storage_name, value)


class User(Model):
    name = Field(str)
    email = Field(str)
    age = Field(int)

class Product(Model):
    title = Field(str)
    price = Field(float)
    in_stock = Field(bool, default=True)

# Auto-generated __init__:
u = User(name="Alice", email="alice@dev.io", age=30)

# Auto-generated __repr__:
print(u)  # User(name='Alice', email='alice@dev.io', age=30)

# Auto-registration:
print(Model._registry)
# {'User': <class 'User'>, 'Product': <class 'Product'>}

# Type validation from Field descriptors:
u.age = "thirty"  # TypeError: age must be int, got str
```

## __new__ vs __init__ in Metaclasses

```python
class Meta(type):
    def __new__(mcs, name, bases, namespace):
        # Called to CREATE the class object
        # Can modify name, bases, namespace before class exists
        # Must return the class object
        print(f"__new__: Creating {name}")
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace):
        # Called to INITIALIZE the class object (already created)
        # cls is the newly created class
        # Can add attributes but can't change bases
        print(f"__init__: Initializing {name}")
        super().__init__(name, bases, namespace)

class MyClass(metaclass=Meta):
    pass
# Output:
# __new__: Creating MyClass
# __init__: Initializing MyClass
```

**Use `__new__`** when you need to modify the class before it's created (change bases, modify namespace).
**Use `__init__`** for post-creation setup (registration, validation).

## Validation at Class Creation Time

```python
RESERVED_NAMES = {'save', 'delete', 'update', 'query', 'meta'}

class StrictModelMeta(type):
    def __new__(mcs, name, bases, namespace):
        # Validate field names at class definition time
        for key, value in namespace.items():
            if isinstance(value, Field):
                if key.startswith('_'):
                    raise ValueError(
                        f"Field names cannot start with underscore: {key!r} in {name}"
                    )
                if key in RESERVED_NAMES:
                    raise ValueError(
                        f"Field name {key!r} is reserved in {name}"
                    )

        return super().__new__(mcs, name, bases, namespace)

class StrictModel(metaclass=StrictModelMeta):
    pass

# This raises at CLASS DEFINITION TIME — not at runtime:
class BadModel(StrictModel):
    save = Field(str)  # ValueError: Field name 'save' is reserved in BadModel
```

The error happens when Python executes the `class` statement. The class never exists.

## __init_subclass__ vs Metaclass — Decision Guide

```python
# Use __init_subclass__ when you need to:
# ✓ Register subclasses
# ✓ Validate class attributes after creation
# ✓ Add methods based on class attributes
# ✓ Set class-level defaults

# Use a metaclass when you need to:
# ✓ Control the namespace (__prepare__)
# ✓ Modify bases before class creation
# ✓ Prevent class creation (raise in __new__)
# ✓ Implement abstract base class patterns
# ✓ Deep framework internals (Django ORM, SQLAlchemy)
```

## The Abstract Base Class Pattern

```python
class InterfaceMeta(type):
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)

        # Skip the base interface class
        if not bases:
            return cls

        # Check that all abstract methods are implemented
        for base in bases:
            for attr_name in getattr(base, '_abstract_methods', []):
                if attr_name not in namespace:
                    raise TypeError(
                        f"Can't create {name}: missing implementation "
                        f"of abstract method '{attr_name}'"
                    )
        return cls

class Interface(metaclass=InterfaceMeta):
    _abstract_methods = []

class Serializable(Interface):
    _abstract_methods = ['to_bytes', 'from_bytes']

class MyData(Serializable):
    pass
# TypeError: Can't create MyData: missing implementation of abstract method 'to_bytes'

class MyData(Serializable):
    def to_bytes(self):
        return b"data"
    def from_bytes(self, data):
        return data
# Works!
```

## What You Learned

- **`type` is the default metaclass** — every `class` statement calls `type()`
- **`__init_subclass__`** handles 90% of metaclass use cases (registration, validation, method injection)
- **Metaclass `__new__`** creates the class — can modify name, bases, namespace
- **Metaclass `__init__`** initializes the class — post-creation setup
- **`__prepare__`** provides a custom namespace for the class body
- **Validation at class creation time** catches errors before any instance exists
- **Rule**: try `__init_subclass__` first. Use metaclass only when you need `__new__` or `__prepare__`

## Key Insight

> Metaclasses control class creation. But sometimes you don't need to create classes — you need to intercept attribute access on existing objects. What if accessing `client.users` should dynamically build a URL? What if reading `config.database.host` should traverse a nested dict? That's `__getattr__` and dynamic dispatch.

---

[Chapter 6: __getattr__ and Dynamic Dispatch →](chapter-06-dynamic-attrs.md)

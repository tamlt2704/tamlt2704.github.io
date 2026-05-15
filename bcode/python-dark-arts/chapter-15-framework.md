# Chapter 15: Building a Mini-Framework

[← Chapter 14: Performance](chapter-14-performance.md)

---

## The Problem

It's time. Vera wants the full FrameForge ORM prototype. Users should write:

```python
class User(Model):
    name = Field(str, max_length=100)
    email = Field(str, unique=True)
    age = Field(int, min_value=0)

class Post(Model):
    title = Field(str, max_length=200)
    author = Field(str)
    published = Field(bool, default=False)
```

And get:
- Validated `__init__` (type checking + constraints)
- `__repr__` and `__eq__`
- `to_dict()` and `from_dict()`
- Auto-registration in a model registry
- A query interface: `User.objects.filter(age__gt=18)`
- Hooks: `@before_save`, `@after_create`

Everything from chapters 1-14 comes together.

## The Field Descriptor (Chapter 4)

```python
class Field:
    """Descriptor that validates on assignment."""

    def __init__(self, field_type, default=None, required=True,
                 min_value=None, max_value=None, max_length=None,
                 unique=False):
        self.field_type = field_type
        self.default = default
        self.required = required
        self.min_value = min_value
        self.max_value = max_value
        self.max_length = max_length
        self.unique = unique

    def __set_name__(self, owner, name):
        self.name = name
        self.storage_name = f"_field_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.storage_name, self.default)

    def __set__(self, obj, value):
        if value is None and self.default is not None:
            value = self.default
        if value is not None:
            self._validate(value)
        setattr(obj, self.storage_name, value)

    def _validate(self, value):
        # Type check
        if not isinstance(value, self.field_type):
            raise TypeError(
                f"{self.name}: expected {self.field_type.__name__}, "
                f"got {type(value).__name__}"
            )
        # Constraints
        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"{self.name}: must be >= {self.min_value}, got {value}")
        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"{self.name}: must be <= {self.max_value}, got {value}")
        if self.max_length is not None and len(value) > self.max_length:
            raise ValueError(
                f"{self.name}: max length {self.max_length}, got {len(value)}"
            )
```

## The Model Registry (Chapter 5: Metaclass)

```python
class ModelRegistry:
    """Global registry of all model classes."""

    def __init__(self):
        self._models = {}

    def register(self, cls):
        self._models[cls.__name__] = cls

    def get(self, name):
        return self._models[name]

    def all(self):
        return dict(self._models)

registry = ModelRegistry()
```

## The QuerySet (Chapter 6: Dynamic Dispatch + Chapter 8: Generators)

```python
class QuerySet:
    """Lazy, chainable query builder."""

    def __init__(self, model_class, storage):
        self._model = model_class
        self._storage = storage
        self._filters = []
        self._order_by = None
        self._limit_val = None

    def filter(self, **kwargs):
        """Chain filters: User.objects.filter(age__gt=18, active=True)"""
        qs = QuerySet(self._model, self._storage)
        qs._filters = self._filters + list(kwargs.items())
        qs._order_by = self._order_by
        qs._limit_val = self._limit_val
        return qs

    def order_by(self, field):
        qs = QuerySet(self._model, self._storage)
        qs._filters = self._filters
        qs._order_by = field
        qs._limit_val = self._limit_val
        return qs

    def limit(self, n):
        qs = QuerySet(self._model, self._storage)
        qs._filters = self._filters
        qs._order_by = self._order_by
        qs._limit_val = n
        return qs

    def _matches(self, instance, key, value):
        """Check if instance matches a filter condition."""
        if "__" in key:
            field, op = key.rsplit("__", 1)
            attr_val = getattr(instance, field)
            if op == "gt":
                return attr_val > value
            elif op == "lt":
                return attr_val < value
            elif op == "gte":
                return attr_val >= value
            elif op == "lte":
                return attr_val <= value
            elif op == "contains":
                return value in attr_val
            elif op == "startswith":
                return attr_val.startswith(value)
        else:
            return getattr(instance, key) == value

    def __iter__(self):
        """Lazy evaluation — filter on iteration (Chapter 8: generators)."""
        results = self._storage.get(self._model.__name__, [])

        # Apply filters
        for item in results:
            if all(self._matches(item, k, v) for k, v in self._filters):
                yield item

    def all(self):
        """Return all instances as a list."""
        results = list(self)
        if self._order_by:
            reverse = self._order_by.startswith('-')
            field = self._order_by.lstrip('-')
            results.sort(key=lambda x: getattr(x, field), reverse=reverse)
        if self._limit_val:
            results = results[:self._limit_val]
        return results

    def first(self):
        """Return first matching instance or None."""
        for item in self:
            return item
        return None

    def count(self):
        return sum(1 for _ in self)

    def __repr__(self):
        return f"<QuerySet({self._model.__name__}) filters={self._filters}>"
```

## The Hook System (Chapter 2: Decorators + Chapter 9: Closures)

```python
# Hook decorators — closures that register callbacks
_hooks = {}

def before_save(func):
    """Register a function to run before save()."""
    model_name = func.__qualname__.split('.')[0]
    _hooks.setdefault(model_name, {}).setdefault('before_save', []).append(func)
    return func

def after_create(func):
    """Register a function to run after creation."""
    model_name = func.__qualname__.split('.')[0]
    _hooks.setdefault(model_name, {}).setdefault('after_create', []).append(func)
    return func

def after_save(func):
    model_name = func.__qualname__.split('.')[0]
    _hooks.setdefault(model_name, {}).setdefault('after_save', []).append(func)
    return func

def _run_hooks(instance, hook_name):
    """Execute all registered hooks for a model."""
    model_name = type(instance).__name__
    hooks = _hooks.get(model_name, {}).get(hook_name, [])
    for hook in hooks:
        hook(instance)
```

## The Model Base Class (Chapter 5: __init_subclass__)

```python
# In-memory storage (would be a database in production)
_storage = {}

class Model:
    """Base model class. Combines all techniques."""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Collect fields (Chapter 4: descriptors)
        fields = {}
        for name in dir(cls):
            value = getattr(cls, name, None)
            if isinstance(value, Field):
                fields[name] = value
        cls._fields = fields

        # Generate __slots__ for performance (Chapter 14)
        cls.__slots__ = tuple(f"_field_{name}" for name in fields) + ('_pk',)

        # Register in global registry (Chapter 5)
        registry.register(cls)

        # Attach query manager (Chapter 6)
        cls.objects = QuerySet(cls, _storage)

        # Initialize storage
        _storage[cls.__name__] = []

    def __init__(self, **kwargs):
        # Set fields with validation (triggers Field.__set__)
        for name, field in self._fields.items():
            if name in kwargs:
                setattr(self, name, kwargs[name])
            elif field.default is not None:
                setattr(self, name, field.default)
            elif field.required:
                raise TypeError(f"Missing required field: {name}")

        # Generate a primary key
        import uuid
        object.__setattr__(self, '_pk', str(uuid.uuid4())[:8])

        # Run after_create hooks (Chapter 2)
        _run_hooks(self, 'after_create')

    def save(self):
        """Persist the instance to storage."""
        _run_hooks(self, 'before_save')

        store = _storage[type(self).__name__]
        # Update if exists, insert if new
        existing = [i for i, obj in enumerate(store) if obj._pk == self._pk]
        if existing:
            store[existing[0]] = self
        else:
            store.append(self)

        _run_hooks(self, 'after_save')
        return self

    def delete(self):
        """Remove from storage."""
        store = _storage[type(self).__name__]
        _storage[type(self).__name__] = [
            obj for obj in store if obj._pk != self._pk
        ]

    def to_dict(self):
        """Serialize to dictionary."""
        return {name: getattr(self, name) for name in self._fields}

    @classmethod
    def from_dict(cls, data):
        """Deserialize from dictionary."""
        return cls(**data)

    def __repr__(self):
        fields = ", ".join(
            f"{name}={getattr(self, name)!r}" for name in self._fields
        )
        return f"{type(self).__name__}({fields})"

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return all(
            getattr(self, name) == getattr(other, name)
            for name in self._fields
        )

    def __hash__(self):
        return hash(self._pk)
```

## The Complete Framework in Action

```python
# --- User defines models (4 lines each) ---

class User(Model):
    name = Field(str, max_length=100)
    email = Field(str, max_length=255)
    age = Field(int, min_value=0, max_value=150)
    active = Field(bool, default=True)

    @after_create
    def log_creation(self):
        print(f"  [hook] User created: {self.name}")

    @before_save
    def validate_email(self):
        if "@" not in self.email:
            raise ValueError(f"Invalid email: {self.email}")

class Post(Model):
    title = Field(str, max_length=200)
    author = Field(str)
    published = Field(bool, default=False)


# --- Framework provides everything else ---

# Create instances (validated automatically):
alice = User(name="Alice", email="alice@dev.io", age=30)
#   [hook] User created: Alice

bob = User(name="Bob", email="bob@dev.io", age=25)
#   [hook] User created: Bob

charlie = User(name="Charlie", email="charlie@dev.io", age=35, active=False)
#   [hook] User created: Charlie

# Save to storage (hooks run automatically):
alice.save()
bob.save()
charlie.save()

# Query with chainable API:
young_users = User.objects.filter(age__lt=30).all()
print(young_users)  # [User(name='Bob', ...)]

active_users = User.objects.filter(active=True).all()
print(len(active_users))  # 2

# Serialization:
print(alice.to_dict())
# {'name': 'Alice', 'email': 'alice@dev.io', 'age': 30, 'active': True}

restored = User.from_dict(alice.to_dict())
print(restored)  # User(name='Alice', email='alice@dev.io', age=30, active=True)

# Validation catches errors at assignment:
try:
    User(name="X" * 200, email="x@y.z", age=30)
except ValueError as e:
    print(e)  # name: max length 100, got 200

try:
    User(name="Dave", email="invalid", age=30).save()
except ValueError as e:
    print(e)  # Invalid email: invalid

# Registry knows all models:
print(registry.all())
# {'User': <class 'User'>, 'Post': <class 'Post'>}

# Posts work the same way:
post = Post(title="Python Dark Arts", author="Alice")
post.save()
print(Post.objects.filter(published=False).count())  # 1
```

## The Techniques Map

Every chapter contributed:

| Chapter | Technique | Used For |
|---|---|---|
| 1 | Object model | Understanding that classes are objects created by `type` |
| 2 | Decorators | `@before_save`, `@after_create` hook registration |
| 3 | Class decorators | Could replace `__init_subclass__` for simpler cases |
| 4 | Descriptors | `Field` — validates on every assignment |
| 5 | Metaclass / `__init_subclass__` | Auto-registration, `__init__` generation, attaching QuerySet |
| 6 | `__getattr__` | QuerySet chaining, dynamic filter operators |
| 7 | Context managers | Transaction wrapping (not shown but natural extension) |
| 8 | Generators | Lazy `QuerySet.__iter__` — filter without loading all |
| 9 | Closures | Hook decorators capture model name in closure |
| 10 | Import system | Plugin discovery (extend with custom model loaders) |
| 11 | AST | Could generate optimized `__init__` at class creation |
| 12 | Concurrency | Async query execution (extend QuerySet with `async for`) |
| 13 | Typing | Could read type hints instead of explicit `Field(str)` |
| 14 | Performance | `__slots__`, cached field introspection |

## Extending the Framework

The framework is designed to be extended:

```python
# Add a type-hint-based model (Chapter 13):
class TypedModel(Model):
    """Model that reads fields from type annotations."""

    def __init_subclass__(cls, **kwargs):
        # Convert type annotations to Field descriptors
        from typing import get_type_hints
        hints = get_type_hints(cls)
        for name, hint in hints.items():
            if name.startswith('_'):
                continue
            if not isinstance(getattr(cls, name, None), Field):
                setattr(cls, name, Field(hint))
        super().__init_subclass__(**kwargs)

# Now users can write:
class Product(TypedModel):
    name: str
    price: float
    in_stock: bool
```

## What You Learned

- **Descriptors** (Field) handle per-attribute validation
- **`__init_subclass__`** transforms classes at definition time — registration, method generation, slot creation
- **Generators** make QuerySet lazy — iterate without loading everything
- **Decorators** register hooks with zero boilerplate
- **Closures** capture context in hook decorators
- **`__slots__`** and caching optimize the hot paths
- **The framework pattern**: users write declarations, the framework generates implementations

## The Final Insight

> Every technique in this course serves one goal: **users write WHAT they want, the framework figures out HOW**. Descriptors validate. Metaclasses transform. Decorators inject. Generators stream. Closures configure. Together, they turn 50 lines of boilerplate into 4 lines of declaration.
>
> That's the dark art of Python metaprogramming: making complex machinery invisible behind a simple API.

---

*You've completed Python Dark Arts. Go build something that makes other developers say "how does that work?"*

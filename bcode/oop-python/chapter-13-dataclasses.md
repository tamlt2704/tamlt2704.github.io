# Chapter 13: Dataclasses & Slots

[← Chapter 12: Metaclasses](chapter-12-metaclasses.md) | [Chapter 14: Design Patterns →](chapter-14-patterns.md)

---

## The Problem

You're writing the 50th class that's mostly data with a bit of behavior:

```python
class Address:
    def __init__(self, street, city, state, zip_code, country="US"):
        self.street = street
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.country = country

    def __repr__(self):
        return (
            f"Address(street={self.street!r}, city={self.city!r}, "
            f"state={self.state!r}, zip_code={self.zip_code!r}, country={self.country!r})"
        )

    def __eq__(self, other):
        if not isinstance(other, Address):
            return NotImplemented
        return (
            self.street == other.street
            and self.city == other.city
            and self.state == other.state
            and self.zip_code == other.zip_code
            and self.country == other.country
        )

    def __hash__(self):
        return hash((self.street, self.city, self.state, self.zip_code, self.country))
```

Thirty lines of boilerplate for five fields. And you need the same for `Dimensions`, `TrackingEvent`, `ContactInfo`, `GeoCoordinate`...

Marcus: "I just skip `__repr__` and `__eq__`. Who needs them?"

You (remembering Chapter 6): "Everyone debugging at 2 AM needs them."

Dana: "Use `@dataclass`. It generates all of that for you."

## @dataclass: Boilerplate Eliminated

```python
from dataclasses import dataclass

@dataclass
class Address:
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "US"
```

That's it. Five lines. Python generates `__init__`, `__repr__`, and `__eq__` automatically:

```python
addr = Address("123 Main St", "Springfield", "IL", "62701")
print(addr)
# Address(street='123 Main St', city='Springfield', state='IL', zip_code='62701', country='US')

addr2 = Address("123 Main St", "Springfield", "IL", "62701")
print(addr == addr2)  # True — field-by-field comparison
```

## What @dataclass Generates

For the `Address` class above, Python generates:

```python
# __init__ with all fields as parameters
def __init__(self, street: str, city: str, state: str, zip_code: str, country: str = "US"):
    self.street = street
    self.city = city
    self.state = state
    self.zip_code = zip_code
    self.country = country

# __repr__ showing all fields
def __repr__(self):
    return f"Address(street={self.street!r}, city={self.city!r}, ...)"

# __eq__ comparing all fields
def __eq__(self, other):
    if other.__class__ is self.__class__:
        return (self.street, self.city, ...) == (other.street, other.city, ...)
    return NotImplemented
```

## field(): Fine-Grained Control

```python
from dataclasses import dataclass, field
from typing import List
import time

@dataclass
class TrackingEvent:
    location: str
    status: str
    timestamp: float = field(default_factory=time.time)
    notes: str = ""

@dataclass
class Package:
    id: str
    weight: float
    destination: str
    sender: str
    status: str = "pending"
    history: list = field(default_factory=list)  # Mutable default — must use field()
    _internal: str = field(default="", repr=False, compare=False)  # Hidden from repr/eq
```

`field()` options:
- `default_factory` — callable for mutable defaults (avoids the shared-list bug)
- `repr=False` — exclude from `__repr__`
- `compare=False` — exclude from `__eq__`
- `hash=False` — exclude from `__hash__`
- `init=False` — don't include in `__init__` (set in `__post_init__`)

## __post_init__: Validation and Computed Fields

```python
@dataclass
class Package:
    id: str
    weight: float
    destination: str
    sender: str
    status: str = "pending"
    shipping_cost: float = field(init=False)  # Computed, not passed in

    def __post_init__(self):
        """Runs after __init__ — validate and compute."""
        if self.weight <= 0:
            raise ValueError(f"Weight must be positive, got {self.weight}")
        if not self.destination.strip():
            raise ValueError("Destination cannot be empty")
        # Compute shipping cost
        self.shipping_cost = 5.00 + (self.weight * 2.50)
```

```python
pkg = Package("PKG-001", 3.5, "123 Main St", "Alice")
print(pkg.shipping_cost)  # 13.75 — computed automatically

Package("PKG-002", -1.0, "addr", "Bob")
# ValueError: Weight must be positive, got -1.0
```

## frozen=True: Immutable Data

Some objects should never change after creation:

```python
@dataclass(frozen=True)
class Dimensions:
    length: float
    width: float
    height: float

    @property
    def volume(self):
        return self.length * self.width * self.height

@dataclass(frozen=True)
class GeoCoordinate:
    latitude: float
    longitude: float
```

```python
dims = Dimensions(30.0, 20.0, 15.0)
print(dims.volume)  # 9000.0

dims.length = 50.0
# FrozenInstanceError: cannot assign to field 'length'

# Frozen dataclasses are automatically hashable
locations = {GeoCoordinate(40.7128, -74.0060): "New York"}
```

Frozen dataclasses get `__hash__` for free (since they can't change, they're safe as dict keys).

## Ordering: Sortable Dataclasses

```python
@dataclass(order=True)
class Priority:
    level: int
    name: str = field(compare=False)  # Don't compare by name

p1 = Priority(1, "low")
p2 = Priority(3, "high")
p3 = Priority(2, "medium")

print(sorted([p2, p3, p1]))
# [Priority(level=1, name='low'), Priority(level=2, name='medium'), Priority(level=3, name='high')]
```

`order=True` generates `__lt__`, `__le__`, `__gt__`, `__ge__` based on fields (in declaration order, respecting `compare=False`).

## __slots__: Memory and Speed

Every Python object stores attributes in a `__dict__` dictionary. For millions of objects, that's a lot of overhead. `__slots__` eliminates the dict:

```python
@dataclass(slots=True)  # Python 3.10+
class TrackingEvent:
    package_id: str
    location: str
    timestamp: float
    status: str
```

Or manually:

```python
class TrackingEvent:
    __slots__ = ("package_id", "location", "timestamp", "status")

    def __init__(self, package_id, location, timestamp, status):
        self.package_id = package_id
        self.location = location
        self.timestamp = timestamp
        self.status = status
```

Benefits of `__slots__`:
- **~40% less memory** per instance (no `__dict__`)
- **~10-20% faster** attribute access
- **Prevents typos** — can't add attributes that aren't in `__slots__`

```python
event = TrackingEvent("PKG-001", "Warehouse", 1705234567.0, "arrived")
event.locaton = "Depot"  # AttributeError: 'TrackingEvent' has no attribute 'locaton'
# Caught the typo!
```

Trade-off: no dynamic attributes, no `__dict__`, can complicate inheritance.

## ShipFast's Data Models

```python
from dataclasses import dataclass, field
from typing import Optional
import time

@dataclass(frozen=True)
class Address:
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "US"

    @property
    def one_line(self):
        return f"{self.street}, {self.city}, {self.state} {self.zip_code}"

@dataclass(frozen=True, slots=True)
class Dimensions:
    length_cm: float
    width_cm: float
    height_cm: float

    @property
    def volume_cm3(self):
        return self.length_cm * self.width_cm * self.height_cm

@dataclass
class TrackingEvent:
    location: str
    status: str
    timestamp: float = field(default_factory=time.time)
    notes: Optional[str] = None

@dataclass(slots=True)
class PackageRecord:
    """Lightweight record for bulk processing — millions of these in memory."""
    id: str
    weight: float
    destination: str
    status: str = "pending"
    created_at: float = field(default_factory=time.time)
```

## When to Use @dataclass vs Regular Class

| Use @dataclass when... | Use a regular class when... |
|---|---|
| Mostly data with some methods | Mostly behavior with some data |
| Equality means "same field values" | Equality means "same identity" (same ID) |
| You want auto-generated boilerplate | You need custom `__init__` logic |
| Fields are the primary interface | Methods are the primary interface |
| Immutability is desirable (`frozen`) | State changes are the point |

Dana's rule: "If the class is a noun (Address, Dimensions, Event), it's probably a dataclass. If it's an actor (Router, Tracker, Engine), it's probably a regular class."

## What You Learned

- **`@dataclass`** — auto-generates `__init__`, `__repr__`, `__eq__`
- **`field()`** — fine-grained control over defaults, repr, comparison
- **`default_factory`** — safe mutable defaults (lists, dicts)
- **`__post_init__`** — validation and computed fields after construction
- **`frozen=True`** — immutable instances, auto-hashable
- **`order=True`** — auto-generated comparison operators
- **`__slots__`** — memory-efficient, faster attribute access, typo prevention
- **`slots=True`** — combine dataclass with slots (Python 3.10+)

The boilerplate is gone. Data classes are concise, correct, and fast. But as the codebase grows, you notice the same structural problems recurring: objects that need to be created without knowing their exact class, events that multiple systems need to react to, data access that's scattered everywhere.

These are design patterns — and they have names.

---

[← Chapter 12: Metaclasses](chapter-12-metaclasses.md) | [Chapter 14: Design Patterns →](chapter-14-patterns.md)

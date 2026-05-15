# Chapter 15: Refactoring — The Full Arc

[← Chapter 14: Design Patterns](chapter-14-patterns.md)

---

## The Problem

Remember where we started? A 4,000-line script called `tracking.py`:

```python
# tracking.py — the original horror
packages = []
next_package_id = 1
drivers = []
routes = []
warehouse_inventory = {}
# ... 200 more global variables ...

def create_package(weight, destination, sender_name, sender_address):
    global next_package_id
    pkg = {"id": f"PKG-{next_package_id:05d}", "weight": weight, ...}
    next_package_id += 1
    packages.append(pkg)
    # Also update billing, also notify, also log...
    return pkg

# ... 4000 lines of functions modifying global state ...
```

Over 14 chapters, you've learned the tools. Now let's see the final architecture — and reflect on when each tool was the right choice.

## The Final Package Structure

```
shipfast/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── package.py          # Package class with encapsulation (Ch 2)
│   ├── driver.py           # Driver class
│   ├── route.py            # Route with __add__, __iter__ (Ch 7)
│   ├── warehouse.py        # Warehouse with __contains__ (Ch 7)
│   └── data.py             # Dataclasses: Address, Dimensions, TrackingEvent (Ch 13)
├── shipping/
│   ├── __init__.py
│   ├── base.py             # ShippingStrategy ABC (Ch 9)
│   ├── standard.py         # StandardShipping
│   ├── express.py          # ExpressShipping
│   ├── freight.py          # FreightShipping
│   └── factory.py          # PackageFactory (Ch 14)
├── tracking/
│   ├── __init__.py
│   ├── tracker.py          # GPSTracker component (Ch 8)
│   └── events.py           # TrackingEvent dataclass
├── notifications/
│   ├── __init__.py
│   ├── base.py             # NotificationChannel ABC (Ch 9)
│   ├── email.py            # EmailChannel
│   ├── sms.py              # SMSChannel
│   └── webhook.py          # WebhookChannel
├── events/
│   ├── __init__.py
│   └── bus.py              # EventBus (Ch 14)
├── repositories/
│   ├── __init__.py
│   ├── packages.py         # PackageRepository (Ch 14)
│   └── drivers.py          # DriverRepository
├── validators/
│   ├── __init__.py
│   └── descriptors.py      # PositiveNumber, NonEmptyString, OneOf (Ch 11)
└── config.py               # ConnectionPool, settings
```

## Before and After: The Core Package

### Before (from the script):

```python
def create_package(weight, destination, sender_name, sender_address):
    global next_package_id
    pkg = {
        "id": f"PKG-{next_package_id:05d}",
        "weight": weight,
        "destination": destination,
        "sender_name": sender_name,
        "status": "pending",
    }
    next_package_id += 1
    packages.append(pkg)
    send_email(sender_name, "Package created!")
    log_event("package_created", pkg["id"])
    return pkg
```

### After (the final class):

```python
from dataclasses import dataclass, field
from shipfast.validators.descriptors import PositiveNumber, NonEmptyString, OneOf
from shipfast.shipping.base import ShippingStrategy
from shipfast.tracking.tracker import GPSTracker
from shipfast.events.bus import EventBus

class Package:
    """A package in the ShipFast system."""

    # Reusable validators (Ch 11)
    weight = PositiveNumber()
    destination = NonEmptyString(max_length=200)
    sender = NonEmptyString(max_length=100)
    status = OneOf("pending", "in_transit", "delivered", "returned", "lost")

    _next_id = 1

    def __init__(self, weight, destination, sender, shipping_strategy=None, event_bus=None):
        self.id = f"PKG-{Package._next_id:05d}"
        Package._next_id += 1

        # Validated by descriptors
        self.weight = weight
        self.destination = destination
        self.sender = sender
        self.status = "pending"

        # Composition (Ch 8)
        self.shipping_strategy = shipping_strategy or StandardShipping()
        self.tracker = GPSTracker()
        self._event_bus = event_bus

    # Alternative constructors (Ch 10)
    @classmethod
    def from_json(cls, json_str, **kwargs):
        data = json.loads(json_str)
        return cls(data["weight"], data["destination"], data["sender"], **kwargs)

    # Polymorphic behavior (Ch 5)
    def shipping_cost(self):
        return self.shipping_strategy.calculate(self.weight)

    # State transitions with validation (Ch 2)
    def ship(self):
        if self.status != "pending":
            raise RuntimeError(f"Can only ship pending packages, got {self.status}")
        self.status = "in_transit"
        if self._event_bus:
            self._event_bus.publish("package_shipped", package_id=self.id)

    def deliver(self):
        if self.status != "in_transit":
            raise RuntimeError(f"Can only deliver in-transit packages, got {self.status}")
        self.status = "delivered"
        if self._event_bus:
            self._event_bus.publish("package_delivered", package_id=self.id)

    # Self-describing (Ch 6)
    def __repr__(self):
        return f"Package(id={self.id!r}, weight={self.weight}, status={self.status!r})"

    def __str__(self):
        return f"📦 {self.id} ({self.weight}kg) → {self.destination}"

    # Identity and hashing (Ch 6)
    def __eq__(self, other):
        if not isinstance(other, Package):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    # Sortable (Ch 7)
    def __lt__(self, other):
        if not isinstance(other, Package):
            return NotImplemented
        return self.weight < other.weight
```

## SOLID Principles — How They Showed Up

### S — Single Responsibility

Each class does one thing:
- `Package` — manages package state
- `GPSTracker` — records locations
- `EventBus` — routes events
- `PackageRepository` — stores/queries packages

### O — Open/Closed

Open for extension, closed for modification:
- New shipping strategy? Create a class, it auto-registers (Ch 12)
- New notification channel? Implement the ABC (Ch 9)
- New package type? Subclass or compose (Ch 3, 8)

### L — Liskov Substitution

Subclasses work wherever the parent is expected:
- `ExpressPackage` works in any function that accepts `Package`
- Any `ShippingStrategy` subclass works in `Package.shipping_cost()`

### I — Interface Segregation

Small, focused interfaces:
- `ShippingStrategy` has 2 methods, not 20
- `NotificationChannel` has `send()` and `validate_recipient()`
- Protocols define minimal contracts (Ch 5)

### D — Dependency Inversion

High-level modules don't depend on low-level details:
- `Package` depends on `ShippingStrategy` (abstract), not `ExpressShipping` (concrete)
- `Package` receives an `EventBus`, doesn't create one
- Repository hides storage implementation

## The Decision Framework

After 15 chapters, here's when to use what:

| Problem | Solution | Chapter |
|---|---|---|
| Tangled global state | Classes and instances | 1 |
| External code corrupts state | Properties, validation | 2 |
| Duplicated code across types | Inheritance | 3 |
| Multiple inheritance conflicts | Mixins, MRO awareness | 4 |
| if/elif checking types | Polymorphism | 5 |
| Can't debug objects | `__repr__`, `__eq__`, `__hash__` | 6 |
| Can't sort/combine objects | Operator overloading | 7 |
| Deep inheritance hierarchy | Composition, strategy | 8 |
| Missing method crashes at runtime | ABC, abstractmethod | 9 |
| Need multiple constructors | @classmethod | 10 |
| Validation duplicated everywhere | Descriptors | 11 |
| Need auto-registration | `__init_subclass__` | 12 |
| Boilerplate `__init__`/`__repr__` | @dataclass | 13 |
| Recurring structural problems | Design patterns | 14 |

## When OOP Is Overkill

Not everything in the final codebase is a class. Some things stayed as functions:

```python
# shipfast/utils.py — pure functions, no state
def format_tracking_id(raw_id: str) -> str:
    """Normalize a tracking ID to standard format."""
    return raw_id.upper().strip().replace(" ", "-")

def calculate_distance(origin: GeoCoordinate, dest: GeoCoordinate) -> float:
    """Haversine distance between two points."""
    # Pure math — no state, no side effects
    ...

def validate_zip_code(zip_code: str) -> bool:
    """Check if a ZIP code is valid."""
    return bool(re.match(r"^\d{5}(-\d{4})?$", zip_code))
```

Dana's final rule: "Use a class when you have state that changes over time and behavior that operates on that state. Use a function when you're transforming data without side effects. Use a module when you're grouping related functions. The right tool depends on the problem."

## The Journey

```
Chapter 1:  "Everything is global"        → Classes bundle state + behavior
Chapter 2:  "Anyone can corrupt state"    → Properties enforce invariants
Chapter 3:  "Same code in 5 places"       → Inheritance shares logic
Chapter 4:  "Diamond inheritance breaks"  → MRO and mixins
Chapter 5:  "Giant if/elif chains"        → Polymorphism
Chapter 6:  "Can't see what objects are"  → Dunder methods
Chapter 7:  "Can't sort or combine"       → Operator overloading
Chapter 8:  "Hierarchy too deep"          → Composition
Chapter 9:  "Missing methods crash"       → Abstract contracts
Chapter 10: "Need multiple constructors"  → Class machinery
Chapter 11: "Validation everywhere"       → Descriptors
Chapter 12: "Forget to register"          → Class creation hooks
Chapter 13: "Boilerplate everywhere"      → Dataclasses
Chapter 14: "Same problems recurring"     → Design patterns
Chapter 15: "The full picture"            → Architecture
```

The 4,000-line script is now a clean package with:
- **Encapsulated state** — objects protect their own invariants
- **Polymorphic behavior** — new types don't require modifying existing code
- **Composed capabilities** — features are components, not inheritance levels
- **Enforced contracts** — ABCs catch missing methods before production
- **Self-describing objects** — debugging is possible
- **Event-driven architecture** — systems are decoupled
- **Reusable validation** — descriptors eliminate duplication

## What You Learned

- OOP is about **organizing complexity**, not about using classes for everything
- Every pattern exists because **a specific problem demanded it**
- **Inheritance** is for identity ("is-a"), **composition** is for capability ("has-a")
- **Abstractions** should be discovered from concrete code, not designed upfront
- The best code uses **the simplest tool that solves the problem**
- A function is fine. A module is fine. A class is fine. Match the tool to the problem.

The ShipFast codebase is maintainable. New features don't break existing code. Bugs are caught at definition time, not in production. Objects describe themselves. The architecture is clear.

You did it. Dana's buying lunch.

---

[← Chapter 14: Design Patterns](chapter-14-patterns.md)

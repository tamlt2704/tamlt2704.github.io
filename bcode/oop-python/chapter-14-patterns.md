# Chapter 14: Design Patterns

[← Chapter 13: Dataclasses](chapter-13-dataclasses.md) | [Chapter 15: Refactoring →](chapter-15-refactoring.md)

---

## The Problem

Four recurring problems in the ShipFast codebase:

1. **Creation**: The routing engine needs to create packages without knowing the exact class (standard? express? fragile?)
2. **Events**: When a package status changes, billing, notifications, analytics, and tracking all need to react — but they shouldn't know about each other
3. **Data access**: Package queries are scattered across 15 files with raw dict lookups
4. **Shared resources**: Multiple modules create their own database connections instead of sharing one

These aren't ShipFast-specific problems. They're structural problems that show up in every growing codebase. They have names: Factory, Observer, Repository, Singleton.

## Factory: Create Without Knowing the Class

The routing engine receives package data and needs to create the right type:

```python
# ❌ The routing engine shouldn't know about every package type
def create_package(data):
    if data["type"] == "standard":
        return StandardPackage(data["weight"], data["dest"])
    elif data["type"] == "express":
        return ExpressPackage(data["weight"], data["dest"])
    elif data["type"] == "fragile":
        return FragilePackage(data["weight"], data["dest"])
    elif data["type"] == "hazmat":
        return HazmatPackage(data["weight"], data["dest"])
    # ... grows forever
```

### The Factory Pattern

```python
class PackageFactory:
    """Creates packages without the caller knowing concrete classes."""

    _creators = {}

    @classmethod
    def register(cls, package_type, creator):
        """Register a creator function for a package type."""
        cls._creators[package_type] = creator

    @classmethod
    def create(cls, package_type, **kwargs):
        """Create a package by type name."""
        if package_type not in cls._creators:
            available = ", ".join(sorted(cls._creators.keys()))
            raise ValueError(f"Unknown type '{package_type}'. Available: {available}")
        return cls._creators[package_type](**kwargs)


# Register creators (can use __init_subclass__ to auto-register)
PackageFactory.register("standard", lambda **kw: StandardPackage(**kw))
PackageFactory.register("express", lambda **kw: ExpressPackage(**kw))
PackageFactory.register("fragile", lambda **kw: FragilePackage(**kw))
PackageFactory.register("hazmat", lambda **kw: HazmatPackage(**kw))
```

```python
# The routing engine doesn't import any concrete class
pkg = PackageFactory.create("express", weight=3.0, destination="123 Main St")
print(type(pkg).__name__)  # ExpressPackage
```

Combined with `__init_subclass__` from Chapter 12:

```python
class Package:
    _factory = {}

    def __init_subclass__(cls, type_name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if type_name:
            Package._factory[type_name] = cls

    @classmethod
    def create(cls, type_name, **kwargs):
        return cls._factory[type_name](**kwargs)


class StandardPackage(Package, type_name="standard"):
    def __init__(self, weight, destination):
        self.weight = weight
        self.destination = destination

class ExpressPackage(Package, type_name="express"):
    def __init__(self, weight, destination):
        self.weight = weight
        self.destination = destination
        self.priority = "next_day"
```

```python
pkg = Package.create("express", weight=5.0, destination="addr")
```

## Observer: Event System

When a package ships, multiple systems need to know — but they shouldn't be coupled:

```python
# ❌ Package knows about every system that cares about it
class Package:
    def ship(self):
        self.status = "in_transit"
        send_email(self.sender, "Your package shipped!")      # Coupling
        update_analytics("package_shipped", self.id)          # Coupling
        notify_warehouse(self.origin, "package_left")         # Coupling
        update_billing(self.id, "in_transit")                 # Coupling
```

### The Observer Pattern (Event Bus)

```python
from collections import defaultdict
from typing import Callable, Any

class EventBus:
    """Publish-subscribe event system."""

    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event: str, handler: Callable):
        """Register a handler for an event."""
        self._subscribers[event].append(handler)

    def unsubscribe(self, event: str, handler: Callable):
        """Remove a handler."""
        self._subscribers[event].remove(handler)

    def publish(self, event: str, **data):
        """Notify all subscribers of an event."""
        for handler in self._subscribers[event]:
            handler(**data)


# Global event bus (or inject it)
events = EventBus()
```

Systems subscribe independently:

```python
# Notifications module
def on_package_shipped(package_id, destination, **kwargs):
    print(f"📧 Sending shipping notification for {package_id}")

events.subscribe("package_shipped", on_package_shipped)

# Analytics module
def on_package_shipped_analytics(package_id, **kwargs):
    print(f"📊 Recording shipment metric for {package_id}")

events.subscribe("package_shipped", on_package_shipped_analytics)

# Billing module
def on_package_shipped_billing(package_id, **kwargs):
    print(f"💰 Activating billing for {package_id}")

events.subscribe("package_shipped", on_package_shipped_billing)
```

The package just publishes:

```python
class Package:
    def __init__(self, id, weight, destination, event_bus):
        self.id = id
        self.weight = weight
        self.destination = destination
        self.status = "pending"
        self._events = event_bus

    def ship(self):
        self.status = "in_transit"
        self._events.publish(
            "package_shipped",
            package_id=self.id,
            destination=self.destination,
            weight=self.weight,
        )
```

```python
pkg = Package("PKG-001", 3.0, "123 Main St", events)
pkg.ship()
# 📧 Sending shipping notification for PKG-001
# 📊 Recording shipment metric for PKG-001
# 💰 Activating billing for PKG-001
```

Add a new system? Subscribe. Remove one? Unsubscribe. The package doesn't change.

## Repository: Clean Data Access

Package queries are scattered everywhere:

```python
# ❌ Raw data access in business logic
def get_pending_packages():
    return [p for p in all_packages if p["status"] == "pending"]

def get_heavy_packages():
    return [p for p in all_packages if p["weight"] > 20]

def find_package(id):
    for p in all_packages:
        if p["id"] == id:
            return p
    return None
```

### The Repository Pattern

```python
class PackageRepository:
    """Single point of access for package data."""

    def __init__(self):
        self._packages: dict[str, Package] = {}

    def add(self, package: Package):
        """Store a package."""
        self._packages[package.id] = package

    def get(self, package_id: str) -> Package | None:
        """Find by ID."""
        return self._packages.get(package_id)

    def get_or_raise(self, package_id: str) -> Package:
        """Find by ID or raise."""
        pkg = self.get(package_id)
        if pkg is None:
            raise KeyError(f"Package {package_id} not found")
        return pkg

    def find_by_status(self, status: str) -> list[Package]:
        """Find all packages with a given status."""
        return [p for p in self._packages.values() if p.status == status]

    def find_by_destination(self, destination: str) -> list[Package]:
        """Find all packages going to a destination."""
        return [p for p in self._packages.values() if p.destination == destination]

    def find_heavy(self, min_weight: float = 20.0) -> list[Package]:
        """Find packages above a weight threshold."""
        return [p for p in self._packages.values() if p.weight >= min_weight]

    def count(self) -> int:
        return len(self._packages)

    def remove(self, package_id: str) -> Package | None:
        return self._packages.pop(package_id, None)

    def all(self) -> list[Package]:
        return list(self._packages.values())
```

```python
repo = PackageRepository()
repo.add(Package("PKG-001", 3.0, "Main St"))
repo.add(Package("PKG-002", 25.0, "Oak Ave"))
repo.add(Package("PKG-003", 1.0, "Main St"))

pending = repo.find_by_status("pending")
heavy = repo.find_heavy(20.0)
main_st = repo.find_by_destination("Main St")
```

Benefits: one place to add caching, logging, or swap to a database later.

## Singleton: Shared Resources

Multiple modules create their own database connections:

```python
# ❌ Each module creates its own connection
# billing.py
db = DatabaseConnection("postgres://...")

# tracking.py
db = DatabaseConnection("postgres://...")  # Another connection!

# analytics.py
db = DatabaseConnection("postgres://...")  # And another!
```

### Connection Pool (Singleton-ish)

In Python, the cleanest "singleton" is just a module-level instance:

```python
# connection.py
class ConnectionPool:
    """Manages a pool of database connections."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, connection_string="", pool_size=5):
        if self._initialized:
            return
        self._connection_string = connection_string
        self._pool_size = pool_size
        self._connections = []
        self._initialized = True

    def get_connection(self):
        """Get a connection from the pool."""
        if self._connections:
            return self._connections.pop()
        return self._create_connection()

    def release(self, conn):
        """Return a connection to the pool."""
        if len(self._connections) < self._pool_size:
            self._connections.append(conn)

    def _create_connection(self):
        return f"Connection({self._connection_string})"
```

```python
# Same instance everywhere
pool1 = ConnectionPool("postgres://localhost/shipfast")
pool2 = ConnectionPool()  # Returns the same instance
print(pool1 is pool2)  # True
```

Dana's preferred approach — simpler:

```python
# connection.py
_pool = None

def get_pool(connection_string="postgres://localhost/shipfast", pool_size=5):
    """Module-level singleton — simpler than __new__ tricks."""
    global _pool
    if _pool is None:
        _pool = ConnectionPool(connection_string, pool_size)
    return _pool
```

## When to Use Each Pattern

| Pattern | Use When | ShipFast Example |
|---|---|---|
| Factory | Object creation depends on runtime data | Creating packages from API data |
| Observer | Multiple systems react to the same event | Status change notifications |
| Repository | Centralize data access and queries | Package lookup and filtering |
| Singleton | Exactly one shared resource | Database connection pool |

## Patterns Are Tools, Not Rules

Dana: "Don't use a pattern because it has a name. Use it because it solves a specific problem you're having. If your code is simple and clear without a pattern, leave it alone."

```python
# ❌ Over-engineered: Factory for one type
class WidgetFactory:
    def create(self):
        return Widget()

# ✅ Just create the thing
widget = Widget()
```

## What You Learned

- **Factory** — decouple object creation from the code that uses objects
- **Observer (Event Bus)** — decouple event producers from event consumers
- **Repository** — centralize data access behind a clean interface
- **Singleton** — ensure one shared instance of a resource
- **Pattern discipline** — use patterns to solve problems, not to look clever

The codebase has clean patterns for creation, events, data access, and shared resources. It's time to step back and see the full picture — from the original 4,000-line script to the final architecture.

---

[← Chapter 13: Dataclasses](chapter-13-dataclasses.md) | [Chapter 15: Refactoring →](chapter-15-refactoring.md)

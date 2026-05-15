# Chapter 1: The God Script — Classes and Instances

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Encapsulation →](chapter-02-encapsulation.md)

---

## The Problem

Here's a fragment of ShipFast's `tracking.py` — the 4,000-line script:

```python
# --- Package tracking section (lines 1-400) ---
packages = []
next_package_id = 1

def create_package(weight, destination, sender_name, sender_address):
    global next_package_id
    pkg = {
        "id": f"PKG-{next_package_id:05d}",
        "weight": weight,
        "destination": destination,
        "sender_name": sender_name,
        "sender_address": sender_address,
        "status": "pending",
        "created_at": time.time(),
        "history": [],
    }
    next_package_id += 1
    packages.append(pkg)
    return pkg

def update_package_status(package_id, new_status):
    for pkg in packages:
        if pkg["id"] == package_id:
            pkg["history"].append({"status": pkg["status"], "timestamp": time.time()})
            pkg["status"] = new_status
            return True
    return False

def get_package_weight(package_id):
    for pkg in packages:
        if pkg["id"] == package_id:
            return pkg["weight"]
    return None

# ... 50 more functions that search through `packages` ...
```

Problems:
1. **Global state**: `packages` and `next_package_id` are globals. Any function anywhere can modify them.
2. **No structure**: A package is a dict. Nothing prevents `pkg["stauts"] = "shipped"` (typo).
3. **Linear search**: Every operation scans the entire list.
4. **No validation**: You can set weight to -5 or status to "banana".
5. **Tangled**: The billing section (line 2000) directly modifies package dicts.

Dana: "Start with packages. Turn them into proper objects."

## Your First Class

A class defines what a package **is** (data) and what it can **do** (behavior):

```python
import time

class Package:
    """A package in the ShipFast system."""

    def __init__(self, weight, destination, sender_name, sender_address):
        """Initialize a new package."""
        self.weight = weight
        self.destination = destination
        self.sender_name = sender_name
        self.sender_address = sender_address
        self.status = "pending"
        self.created_at = time.time()
        self.history = []

    def update_status(self, new_status):
        """Change the package status and record history."""
        self.history.append({
            "from_status": self.status,
            "to_status": new_status,
            "timestamp": time.time(),
        })
        self.status = new_status

    def is_deliverable(self):
        """Check if the package can be delivered."""
        return self.status == "in_transit"
```

### What Just Happened

- `class Package:` — defines a new type called `Package`
- `__init__` — the **constructor**. Called automatically when you create an instance.
- `self` — refers to the specific instance being created/used
- `self.weight = weight` — stores data on the instance (an **attribute**)
- `def update_status(self, ...)` — a **method** (function that belongs to the class)

### Creating Instances

```python
# Each call to Package() creates a NEW, independent object
pkg1 = Package(2.5, "123 Main St", "Alice", "456 Oak Ave")
pkg2 = Package(10.0, "789 Pine Rd", "Bob", "321 Elm St")

# Each instance has its own state
print(pkg1.weight)       # 2.5
print(pkg2.weight)       # 10.0
print(pkg1.status)       # "pending"

# Methods operate on the specific instance
pkg1.update_status("in_transit")
print(pkg1.status)       # "in_transit"
print(pkg2.status)       # "pending" — unaffected
```

`pkg1` and `pkg2` are **instances** of the `Package` class. They share the same structure (weight, destination, status) but have independent values. Changing one doesn't affect the other.

## The ID Problem

The old script used a global counter for IDs. Where does that go in OOP?

```python
class Package:
    _next_id = 1  # Class variable — shared across all instances

    def __init__(self, weight, destination, sender_name, sender_address):
        self.id = f"PKG-{Package._next_id:05d}"
        Package._next_id += 1

        self.weight = weight
        self.destination = destination
        self.sender_name = sender_name
        self.sender_address = sender_address
        self.status = "pending"
        self.created_at = time.time()
        self.history = []
```

`_next_id` is a **class variable** — it belongs to the class itself, not to any instance. All packages share the same counter. We'll explore this more in Chapter 10.

## The Registry Problem

The old script kept all packages in a global list. Now what?

```python
class PackageRegistry:
    """Manages all packages in the system."""

    def __init__(self):
        self._packages = {}  # id → Package

    def register(self, package):
        """Add a package to the registry."""
        self._packages[package.id] = package

    def find(self, package_id):
        """Look up a package by ID. O(1) instead of O(n)."""
        return self._packages.get(package_id)

    def find_by_status(self, status):
        """Find all packages with a given status."""
        return [pkg for pkg in self._packages.values() if pkg.status == status]

    def count(self):
        """Total packages in the system."""
        return len(self._packages)


# Usage
registry = PackageRegistry()

pkg = Package(2.5, "123 Main St", "Alice", "456 Oak Ave")
registry.register(pkg)

found = registry.find("PKG-00001")
print(found.destination)  # "123 Main St"
```

Now lookup is O(1) (dict) instead of O(n) (list scan). And the registry is a proper object with a clear interface — not a naked global list.

## Before and After

### Before (procedural):

```python
# Global state
packages = []
next_package_id = 1

# Functions that operate on global state
def create_package(weight, destination, sender, sender_addr):
    global next_package_id
    pkg = {"id": f"PKG-{next_package_id:05d}", "weight": weight, ...}
    next_package_id += 1
    packages.append(pkg)
    return pkg

def ship_package(package_id):
    for pkg in packages:
        if pkg["id"] == package_id:
            pkg["status"] = "in_transit"
```

### After (object-oriented):

```python
# No global state
class Package:
    def __init__(self, weight, destination, sender, sender_addr):
        self.weight = weight
        self.destination = destination
        self.status = "pending"

    def ship(self):
        self.status = "in_transit"

class PackageRegistry:
    def __init__(self):
        self._packages = {}

    def register(self, package):
        self._packages[package.id] = package
```

The data and the operations on that data live together. You can't accidentally modify a package's status from the billing section because you'd need a reference to the specific package object.

## Instance vs Class

A common confusion:

```python
class Package:
    warehouse = "Main Hub"  # Class variable — shared by ALL packages

    def __init__(self, weight):
        self.weight = weight  # Instance variable — unique per package

pkg1 = Package(2.5)
pkg2 = Package(10.0)

# Instance variables are independent
print(pkg1.weight)  # 2.5
print(pkg2.weight)  # 10.0

# Class variable is shared
print(pkg1.warehouse)  # "Main Hub"
print(pkg2.warehouse)  # "Main Hub"

Package.warehouse = "East Hub"
print(pkg1.warehouse)  # "East Hub" — changed for all!
```

Rule of thumb: if every instance should have its own copy, put it in `__init__`. If all instances share the same value, make it a class variable.

## Methods Are Just Functions (With Self)

```python
class Package:
    def __init__(self, weight):
        self.weight = weight

    def is_heavy(self):
        return self.weight > 20.0

pkg = Package(25.0)

# These are equivalent:
print(pkg.is_heavy())          # True — method call
print(Package.is_heavy(pkg))   # True — explicit self
```

When you call `pkg.is_heavy()`, Python translates it to `Package.is_heavy(pkg)`. The instance is passed as the first argument (`self`). That's all `self` is — the instance the method is operating on.

## Common Mistakes

### Forgetting self

```python
class Package:
    def __init__(self, weight):
        weight = weight  # BUG: assigns to local variable, not instance
        # Fix: self.weight = weight
```

### Mutable Default Arguments

```python
class Package:
    def __init__(self, tags=[]):  # BUG: all instances share the same list!
        self.tags = tags

# Fix:
class Package:
    def __init__(self, tags=None):
        self.tags = tags if tags is not None else []
```

### Confusing Class and Instance Variables

```python
class Package:
    history = []  # BUG: shared across ALL instances!

    def add_event(self, event):
        self.history.append(event)  # Modifies the shared list

# Fix: initialize in __init__
class Package:
    def __init__(self):
        self.history = []  # Each instance gets its own list
```

## What You Learned

- **Class** — a template defining attributes and methods
- **Instance** — a specific object created from a class
- **`__init__`** — constructor, initializes instance state
- **`self`** — reference to the current instance
- **Instance variables** — unique per object (`self.x`)
- **Class variables** — shared across all instances
- **Methods** — functions that operate on instance state
- **Registry pattern** — a class that manages a collection of objects

The 4,000-line script now has `Package` and `PackageRegistry` classes. State is organized. Lookup is fast. Methods live next to the data they operate on.

But there's a problem. Marcus (the junior dev) just wrote:

```python
pkg = registry.find("PKG-00001")
pkg.weight = -50  # Negative weight?!
pkg.status = "banana"  # Invalid status!
```

Nothing stops external code from setting attributes to nonsense values. The object's state can be corrupted by anyone with a reference to it.

You need encapsulation.

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Encapsulation →](chapter-02-encapsulation.md)

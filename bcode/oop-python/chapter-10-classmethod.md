# Chapter 10: Class Machinery — classmethod, staticmethod, Class Variables

[← Chapter 9: Abstract Contracts](chapter-09-abc.md) | [Chapter 11: Descriptors →](chapter-11-descriptors.md)

---

## The Problem

Packages arrive from three different sources:

```python
# 1. JSON from the web API
json_data = '{"id": "PKG-001", "weight": 3.5, "dest": "123 Main St", "sender": "Alice"}'

# 2. CSV rows from bulk upload
csv_row = "PKG-002,5.0,456 Oak Ave,Bob"

# 3. Dict from the partner API
api_response = {"package_id": "PKG-003", "mass_kg": 2.0, "address": "789 Pine Rd", "from": "Carol"}
```

Each has different field names, different formats, different validation needs. Marcus's solution:

```python
def package_from_json(json_str):
    data = json.loads(json_str)
    return Package(data["id"], data["weight"], data["dest"], data["sender"])

def package_from_csv(row):
    parts = row.split(",")
    return Package(parts[0], float(parts[1]), parts[2], parts[3])

def package_from_api(response):
    return Package(response["package_id"], response["mass_kg"], response["address"], response["from"])
```

These functions work, but they're disconnected from the `Package` class. They live in a `utils.py` file that nobody can find. When `Package.__init__` changes, these functions break silently.

Dana: "Alternative constructors belong on the class itself. That's what `@classmethod` is for."

## @classmethod: Alternative Constructors

A classmethod receives the **class** as its first argument (conventionally `cls`), not an instance:

```python
import json

class Package:
    _next_id = 1

    def __init__(self, id, weight, destination, sender):
        self.id = id
        self.weight = weight
        self.destination = destination
        self.sender = sender
        self.status = "pending"

    @classmethod
    def from_json(cls, json_str):
        """Create a Package from a JSON string."""
        data = json.loads(json_str)
        return cls(
            id=data["id"],
            weight=data["weight"],
            dest=data["dest"],
            sender=data["sender"],
        )

    @classmethod
    def from_csv_row(cls, row):
        """Create a Package from a CSV row: id,weight,destination,sender."""
        parts = [p.strip() for p in row.split(",")]
        return cls(
            id=parts[0],
            weight=float(parts[1]),
            destination=parts[2],
            sender=parts[3],
        )

    @classmethod
    def from_api_response(cls, response):
        """Create a Package from the partner API response format."""
        return cls(
            id=response["package_id"],
            weight=response["mass_kg"],
            destination=response["address"],
            sender=response["from"],
        )

    @classmethod
    def create_new(cls, weight, destination, sender):
        """Create a Package with an auto-generated ID."""
        pkg_id = f"PKG-{cls._next_id:05d}"
        cls._next_id += 1
        return cls(pkg_id, weight, destination, sender)
```

Usage is clean and discoverable:

```python
# From JSON
pkg1 = Package.from_json('{"id": "PKG-001", "weight": 3.5, "dest": "Main St", "sender": "Alice"}')

# From CSV
pkg2 = Package.from_csv_row("PKG-002, 5.0, Oak Ave, Bob")

# From API
pkg3 = Package.from_api_response({"package_id": "PKG-003", "mass_kg": 2.0, "address": "Pine Rd", "from": "Carol"})

# Auto-generated ID
pkg4 = Package.create_new(1.5, "Elm St", "Dave")
print(pkg4.id)  # "PKG-00001"
```

## Why `cls` Instead of `Package`?

The `cls` parameter matters for inheritance:

```python
class ExpressPackage(Package):
    def __init__(self, id, weight, destination, sender):
        super().__init__(id, weight, destination, sender)
        self.priority = "next_day"

# This works because from_json uses cls(), not Package()
express = ExpressPackage.from_json('{"id": "EXP-001", "weight": 2.0, "dest": "addr", "sender": "X"}')
print(type(express))  # <class 'ExpressPackage'> — not Package!
print(express.priority)  # "next_day"
```

If we'd written `return Package(...)` instead of `return cls(...)`, subclasses would always get a base `Package` back. Using `cls` makes classmethods inheritance-friendly.

## @staticmethod: Utility Functions

A staticmethod doesn't receive `self` or `cls`. It's just a function namespaced to the class:

```python
class Package:
    @staticmethod
    def validate_id(package_id):
        """Check if a package ID has the correct format."""
        if not isinstance(package_id, str):
            return False
        if not package_id.startswith("PKG-"):
            return False
        if len(package_id) != 9:  # PKG-XXXXX
            return False
        return package_id[4:].isdigit()

    @staticmethod
    def weight_category(weight):
        """Classify a weight into a shipping category."""
        if weight <= 1.0:
            return "letter"
        elif weight <= 5.0:
            return "small"
        elif weight <= 20.0:
            return "medium"
        elif weight <= 50.0:
            return "large"
        else:
            return "freight"
```

```python
# Called on the class — no instance needed
Package.validate_id("PKG-00042")  # True
Package.validate_id("FAKE")       # False
Package.weight_category(3.5)      # "small"
```

### When to Use @staticmethod vs a Module Function

```python
# ✅ staticmethod: logically belongs to the class
class Package:
    @staticmethod
    def validate_id(id): ...

# ✅ Module function: general utility, not specific to Package
def format_currency(amount):
    return f"${amount:.2f}"
```

Dana's rule: "If you'd look for it on the class, make it a staticmethod. If it's general-purpose, make it a module function."

## Class Variables: Shared State

Class variables belong to the class, not to instances. Useful for configuration and counters:

```python
class Package:
    # Class variables — shared across all instances
    _next_id = 1
    MAX_WEIGHT = 500.0
    VALID_STATUSES = {"pending", "in_transit", "delivered", "returned"}

    # Track all created packages
    _instance_count = 0

    def __init__(self, weight, destination, sender):
        Package._instance_count += 1
        self.id = f"PKG-{Package._next_id:05d}"
        Package._next_id += 1

        self.weight = weight
        self.destination = destination
        self.sender = sender

    @classmethod
    def get_instance_count(cls):
        """How many packages have been created."""
        return cls._instance_count

    @classmethod
    def reset_counter(cls):
        """Reset for testing."""
        cls._next_id = 1
        cls._instance_count = 0
```

```python
Package.reset_counter()
p1 = Package(2.0, "addr1", "Alice")
p2 = Package(3.0, "addr2", "Bob")
p3 = Package(1.0, "addr3", "Carol")

print(Package.get_instance_count())  # 3
print(Package.MAX_WEIGHT)            # 500.0
```

## Class Variable Gotcha: Mutable Defaults

```python
class Package:
    tags = []  # ⚠️ Shared mutable — all instances modify the same list!

    def add_tag(self, tag):
        self.tags.append(tag)

p1 = Package()
p2 = Package()
p1.add_tag("fragile")
print(p2.tags)  # ["fragile"] — oops! Shared state.
```

Fix: mutable state goes in `__init__`:

```python
class Package:
    def __init__(self):
        self.tags = []  # Each instance gets its own list
```

Immutable class variables (`str`, `int`, `tuple`, `frozenset`) are safe to share. Mutable ones (`list`, `dict`, `set`) should be instance variables.

## Putting It Together: A Complete Factory

```python
import json
import csv
from io import StringIO

class Package:
    _next_id = 1
    MAX_WEIGHT = 500.0

    def __init__(self, id, weight, destination, sender):
        if weight > self.MAX_WEIGHT:
            raise ValueError(f"Weight {weight} exceeds max {self.MAX_WEIGHT}")
        self.id = id
        self.weight = weight
        self.destination = destination
        self.sender = sender
        self.status = "pending"

    @classmethod
    def create(cls, weight, destination, sender):
        """Create with auto-generated ID."""
        pkg_id = f"PKG-{cls._next_id:05d}"
        cls._next_id += 1
        return cls(pkg_id, weight, destination, sender)

    @classmethod
    def from_json(cls, json_str):
        """Parse from JSON string."""
        data = json.loads(json_str)
        return cls.create(data["weight"], data["destination"], data["sender"])

    @classmethod
    def from_csv_row(cls, row):
        """Parse from CSV row."""
        parts = next(csv.reader(StringIO(row)))
        return cls.create(float(parts[0]), parts[1], parts[2])

    @classmethod
    def bulk_from_csv(cls, csv_text):
        """Create multiple packages from CSV text."""
        packages = []
        reader = csv.reader(StringIO(csv_text))
        next(reader)  # Skip header
        for row in reader:
            pkg = cls.create(float(row[0]), row[1], row[2])
            packages.append(pkg)
        return packages

    @staticmethod
    def validate_destination(address):
        """Check if an address is valid for shipping."""
        return bool(address) and len(address) >= 5

    def __repr__(self):
        return f"Package({self.id!r}, {self.weight}kg, {self.destination!r})"
```

```python
# Single package from different sources
p1 = Package.create(3.5, "123 Main St", "Alice")
p2 = Package.from_json('{"weight": 2.0, "destination": "456 Oak Ave", "sender": "Bob"}')

# Bulk import
csv_data = """weight,destination,sender
1.5,789 Pine Rd,Carol
4.0,321 Elm St,Dave
2.5,654 Maple Dr,Eve"""

packages = Package.bulk_from_csv(csv_data)
print(len(packages))  # 3
```

## What You Learned

- **`@classmethod`** — receives `cls`, used for alternative constructors
- **`cls()` vs `ClassName()`** — `cls()` respects inheritance in subclasses
- **`@staticmethod`** — no `self` or `cls`, just a namespaced utility function
- **Class variables** — shared state across all instances (counters, config, constants)
- **Mutable class variable trap** — lists/dicts as class variables are shared; use `__init__` instead
- **Factory pattern** — `from_json()`, `from_csv()`, `create()` as classmethods

The package can now be created from any source with a clean, discoverable API. But there's a new problem: the validation logic in `weight.setter` (must be positive), `destination.setter` (must be non-empty string), and `status.setter` (must be from allowed set) is being copy-pasted into `Driver`, `Route`, and `Warehouse` classes.

You need reusable validators. That's what descriptors are for.

---

[← Chapter 9: Abstract Contracts](chapter-09-abc.md) | [Chapter 11: Descriptors →](chapter-11-descriptors.md)

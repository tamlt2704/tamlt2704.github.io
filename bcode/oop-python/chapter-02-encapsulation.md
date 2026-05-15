# Chapter 2: State That Lies — Encapsulation

[← Chapter 1: Classes](chapter-01-classes.md) | [Chapter 3: Inheritance →](chapter-03-inheritance.md)

---

## The Problem

Marcus found the `Package` class you wrote last week. He's using it in the billing module:

```python
pkg = registry.find("PKG-00042")
pkg.weight = -50        # "Negative weight means refund, right?"
pkg.status = "banana"   # Copy-paste from his lunch order app
pkg.destination = ""    # Forgot to fill it in
```

Nothing stops him. Python doesn't care. The object happily accepts garbage values, and the system breaks three hours later when the routing engine tries to calculate shipping cost for a package that weighs negative fifty kilograms and is headed to nowhere.

Dana pulls up the crash log: "The package had status 'banana'. How is that possible?"

You: "Anyone can set any attribute to anything."

Dana: "Then make it so they can't."

## The Naive Fix: Naming Conventions

Python doesn't have `private` or `protected` keywords like Java. Instead, it uses conventions:

```python
class Package:
    def __init__(self, weight, destination):
        self._weight = weight          # Single underscore: "please don't touch"
        self.__internal_id = id(self)   # Double underscore: name mangling
        self.destination = destination  # Public: go ahead and use it
```

- `_weight` — a **convention** meaning "internal, don't access directly." Nothing enforces it.
- `__internal_id` — **name mangling**. Python renames it to `_Package__internal_id`. Harder to access accidentally, but still not truly private.

```python
pkg = Package(2.5, "123 Main St")
print(pkg._weight)                # Works. Convention only.
print(pkg._Package__internal_id)  # Works. Name mangling isn't security.
```

Conventions help. But Marcus doesn't read conventions. You need enforcement.

## Properties: Controlled Access

The `@property` decorator lets you define methods that look like attributes:

```python
class Package:
    VALID_STATUSES = {"pending", "in_transit", "delivered", "returned", "lost"}

    def __init__(self, weight, destination):
        # Use the setters — they validate
        self.weight = weight
        self.destination = destination
        self._status = "pending"
        self._history = []

    @property
    def weight(self):
        """Get the package weight in kg."""
        return self._weight

    @weight.setter
    def weight(self, value):
        """Set weight — must be a positive number."""
        if not isinstance(value, (int, float)):
            raise TypeError(f"Weight must be a number, got {type(value).__name__}")
        if value <= 0:
            raise ValueError(f"Weight must be positive, got {value}")
        if value > 500:
            raise ValueError(f"Weight exceeds maximum (500kg), got {value}")
        self._weight = float(value)

    @property
    def status(self):
        """Get the current package status."""
        return self._status

    @status.setter
    def status(self, value):
        """Set status — must be from the allowed set."""
        if value not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{value}'. Must be one of: {self.VALID_STATUSES}"
            )
        self._status = value

    @property
    def destination(self):
        """Get the destination address."""
        return self._destination

    @destination.setter
    def destination(self, value):
        """Set destination — must be a non-empty string."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Destination must be a non-empty string")
        self._destination = value.strip()
```

Now Marcus's code explodes immediately — at the point of the mistake, not three hours later:

```python
pkg = Package(2.5, "123 Main St")

pkg.weight = -50
# ValueError: Weight must be positive, got -50

pkg.status = "banana"
# ValueError: Invalid status 'banana'. Must be one of: {'pending', 'in_transit', ...}

pkg.destination = ""
# ValueError: Destination must be a non-empty string
```

The interface looks identical to before — `pkg.weight = 5` — but now there's validation behind it.

## Read-Only Properties

Some attributes should never be changed after creation:

```python
class Package:
    _next_id = 1

    def __init__(self, weight, destination):
        self._id = f"PKG-{Package._next_id:05d}"
        Package._next_id += 1
        self.weight = weight
        self.destination = destination
        self._created_at = time.time()

    @property
    def id(self):
        """Package ID — read-only after creation."""
        return self._id

    # No setter defined → assignment raises AttributeError

    @property
    def created_at(self):
        """Creation timestamp — read-only."""
        return self._created_at
```

```python
pkg = Package(2.5, "123 Main St")
print(pkg.id)          # "PKG-00001"
pkg.id = "FAKE-ID"     # AttributeError: property 'id' has no setter
```

## Computed Properties

Properties can also compute values on the fly:

```python
class Package:
    def __init__(self, weight, destination):
        self.weight = weight
        self.destination = destination
        self._status = "pending"

    @property
    def is_deliverable(self):
        """Whether this package can be delivered right now."""
        return self._status == "in_transit"

    @property
    def shipping_cost(self):
        """Calculate cost based on current weight."""
        base_rate = 5.00
        per_kg = 2.50
        return base_rate + (self._weight * per_kg)
```

```python
pkg = Package(3.0, "123 Main St")
print(pkg.shipping_cost)   # 12.50 — looks like an attribute, computed on access
print(pkg.is_deliverable)  # False
```

No parentheses needed. The caller doesn't know (or care) whether it's stored or computed.

## The Full Encapsulated Package

```python
import time

class Package:
    """A package with validated, encapsulated state."""

    VALID_STATUSES = {"pending", "in_transit", "delivered", "returned", "lost"}
    _next_id = 1

    def __init__(self, weight, destination, sender):
        self._id = f"PKG-{Package._next_id:05d}"
        Package._next_id += 1
        self._created_at = time.time()
        self._history = []

        # These go through the setters
        self.weight = weight
        self.destination = destination
        self.sender = sender
        self._status = "pending"

    # --- Read-only properties ---

    @property
    def id(self):
        return self._id

    @property
    def created_at(self):
        return self._created_at

    @property
    def history(self):
        """Return a copy so external code can't mutate our history."""
        return list(self._history)

    # --- Validated properties ---

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError(f"Weight must be a number, got {type(value).__name__}")
        if value <= 0:
            raise ValueError(f"Weight must be positive, got {value}")
        self._weight = float(value)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new_status):
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status '{new_status}'")
        self._history.append({
            "from": self._status,
            "to": new_status,
            "timestamp": time.time(),
        })
        self._status = new_status

    @property
    def destination(self):
        return self._destination

    @destination.setter
    def destination(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Destination must be a non-empty string")
        self._destination = value.strip()

    # --- Public methods ---

    def ship(self):
        """Mark the package as in transit."""
        if self._status != "pending":
            raise RuntimeError(f"Can only ship pending packages, current: {self._status}")
        self.status = "in_transit"

    def deliver(self):
        """Mark the package as delivered."""
        if self._status != "in_transit":
            raise RuntimeError(f"Can only deliver in-transit packages, current: {self._status}")
        self.status = "delivered"
```

State transitions are enforced. You can't deliver a package that hasn't been shipped. You can't set weight to -50. The object protects its own invariants.

## When to Use Properties vs Methods

| Use a property when... | Use a method when... |
|---|---|
| It feels like accessing data | It feels like performing an action |
| It's cheap to compute | It's expensive or has side effects |
| No arguments needed | Arguments are required |
| `pkg.weight` reads naturally | `pkg.calculate_route()` reads naturally |

Dana's rule: "If you'd be surprised it triggers a database query, it shouldn't be a property."

## What You Learned

- **Single underscore** (`_name`) — convention for "internal, don't touch"
- **Double underscore** (`__name`) — name mangling, prevents accidental access in subclasses
- **`@property`** — defines a getter that looks like attribute access
- **`@x.setter`** — defines a setter with validation logic
- **Read-only properties** — define getter without setter
- **Computed properties** — calculate values on access
- **Invariant enforcement** — the object validates its own state transitions

The package now protects itself. Marcus can't corrupt it. But you notice something: you're about to write `ExpressPackage`, `FragilePackage`, and `OversizedPackage` — and they all share 80% of the same code.

Time for inheritance.

---

[← Chapter 1: Classes](chapter-01-classes.md) | [Chapter 3: Inheritance →](chapter-03-inheritance.md)

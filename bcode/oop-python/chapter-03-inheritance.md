# Chapter 3: Copy-Paste Inheritance

[← Chapter 2: Encapsulation](chapter-02-encapsulation.md) | [Chapter 4: The Diamond Problem →](chapter-04-mro.md)

---

## The Problem

ShipFast now handles three package types: standard, express (guaranteed next-day), and fragile (requires special handling). Marcus wrote them:

```python
class StandardPackage:
    def __init__(self, weight, destination, sender):
        self.weight = weight
        self.destination = destination
        self.sender = sender
        self.status = "pending"

    def shipping_cost(self):
        return 5.00 + (self.weight * 2.50)

    def ship(self):
        self.status = "in_transit"

    def deliver(self):
        self.status = "delivered"


class ExpressPackage:
    def __init__(self, weight, destination, sender):
        self.weight = weight
        self.destination = destination
        self.sender = sender
        self.status = "pending"
        self.priority = "next_day"

    def shipping_cost(self):
        return 15.00 + (self.weight * 5.00)  # Express premium

    def ship(self):
        self.status = "in_transit"

    def deliver(self):
        self.status = "delivered"


class FragilePackage:
    def __init__(self, weight, destination, sender):
        self.weight = weight
        self.destination = destination
        self.sender = sender
        self.status = "pending"
        self.requires_signature = True

    def shipping_cost(self):
        return 5.00 + (self.weight * 2.50) + 10.00  # Handling surcharge

    def ship(self):
        self.status = "in_transit"

    def deliver(self):
        self.status = "delivered"
```

Three classes. 80% identical code. When Dana asks you to add tracking history to all packages, you have to change three places. When the status validation from Chapter 2 needs to apply everywhere, you copy-paste it three times.

Marcus: "It works though!"

Dana: "Until you forget to update one of the copies. Inheritance exists for exactly this."

## Inheritance: Share the Common Parts

Pull the shared logic into a **base class**. Specialized classes **inherit** from it:

```python
class Package:
    """Base class for all package types."""

    VALID_STATUSES = {"pending", "in_transit", "delivered", "returned"}

    def __init__(self, weight, destination, sender):
        self.weight = weight
        self.destination = destination
        self.sender = sender
        self._status = "pending"
        self._history = []

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if value not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {value}")
        self._history.append(self._status)
        self._status = value

    def ship(self):
        """Mark as in transit."""
        if self._status != "pending":
            raise RuntimeError("Can only ship pending packages")
        self.status = "in_transit"

    def deliver(self):
        """Mark as delivered."""
        if self._status != "in_transit":
            raise RuntimeError("Can only deliver in-transit packages")
        self.status = "delivered"

    def shipping_cost(self):
        """Base shipping cost. Override in subclasses."""
        return 5.00 + (self.weight * 2.50)
```

Now the specialized classes only define what's **different**:

```python
class ExpressPackage(Package):
    """Next-day delivery with premium pricing."""

    def __init__(self, weight, destination, sender):
        super().__init__(weight, destination, sender)
        self.priority = "next_day"

    def shipping_cost(self):
        """Express costs more."""
        return 15.00 + (self.weight * 5.00)


class FragilePackage(Package):
    """Requires careful handling and signature on delivery."""

    def __init__(self, weight, destination, sender):
        super().__init__(weight, destination, sender)
        self.requires_signature = True

    def shipping_cost(self):
        """Base cost plus handling surcharge."""
        return super().shipping_cost() + 10.00
```

## How `super()` Works

`super()` gives you access to the parent class's methods:

```python
class FragilePackage(Package):
    def __init__(self, weight, destination, sender):
        super().__init__(weight, destination, sender)  # Call Package.__init__
        self.requires_signature = True                 # Add fragile-specific state

    def shipping_cost(self):
        return super().shipping_cost() + 10.00  # Parent's cost + surcharge
```

- `super().__init__(...)` — runs the parent's constructor. Without this, the package wouldn't have `weight`, `destination`, or `status`.
- `super().shipping_cost()` — calls the parent's version of the method. Useful when you want to extend behavior rather than replace it.

### What Happens Without `super().__init__`

```python
class BrokenPackage(Package):
    def __init__(self, weight, destination, sender):
        # Forgot super().__init__()!
        self.fragile = True

pkg = BrokenPackage(2.5, "123 Main St", "Alice")
pkg.ship()  # AttributeError: 'BrokenPackage' has no attribute '_status'
```

The parent's `__init__` never ran, so none of the base attributes exist.

## Method Overriding

When a subclass defines a method with the same name as the parent, it **overrides** it:

```python
class ExpressPackage(Package):
    def shipping_cost(self):
        # This completely replaces Package.shipping_cost()
        return 15.00 + (self.weight * 5.00)

    def ship(self):
        # Override to add express-specific behavior
        super().ship()  # Still do the normal shipping logic
        self._schedule_priority_pickup()

    def _schedule_priority_pickup(self):
        print(f"Priority pickup scheduled for {self.sender}")
```

The subclass controls what happens. It can:
1. **Replace** the parent method entirely (like `shipping_cost`)
2. **Extend** the parent method by calling `super()` first (like `ship`)

## isinstance() and Type Checking

```python
pkg1 = Package(2.5, "123 Main St", "Alice")
pkg2 = ExpressPackage(1.0, "456 Oak Ave", "Bob")
pkg3 = FragilePackage(5.0, "789 Pine Rd", "Carol")

# isinstance checks the inheritance chain
isinstance(pkg2, ExpressPackage)  # True
isinstance(pkg2, Package)         # True — Express IS a Package
isinstance(pkg1, ExpressPackage)  # False — base Package is not Express

# Process any package type uniformly
def process_shipment(package):
    """Works with ANY Package subclass."""
    cost = package.shipping_cost()
    package.ship()
    return cost

# All three work — they're all Packages
process_shipment(pkg1)  # 11.25
process_shipment(pkg2)  # 20.00
process_shipment(pkg3)  # 22.50
```

This is the power of inheritance: code that accepts a `Package` automatically works with all subclasses.

## Adding Behavior Without Changing the Base

New requirement: oversized packages (over 30kg) need a surcharge. You don't touch `Package` at all:

```python
class OversizedPackage(Package):
    """Packages over 30kg requiring special logistics."""

    OVERSIZE_THRESHOLD = 30.0

    def __init__(self, weight, destination, sender):
        if weight <= self.OVERSIZE_THRESHOLD:
            raise ValueError(f"OversizedPackage requires weight > {self.OVERSIZE_THRESHOLD}kg")
        super().__init__(weight, destination, sender)

    def shipping_cost(self):
        base = super().shipping_cost()
        oversize_surcharge = (self.weight - self.OVERSIZE_THRESHOLD) * 4.00
        return base + oversize_surcharge

    def ship(self):
        super().ship()
        print(f"⚠️  Oversized package ({self.weight}kg) — requires freight vehicle")
```

The base class is unchanged. Existing code that handles `Package` objects still works. The new subclass adds its own rules.

## The Inheritance Hierarchy So Far

```
Package (base)
├── ExpressPackage      — premium pricing, priority pickup
├── FragilePackage      — handling surcharge, signature required
└── OversizedPackage    — weight surcharge, freight vehicle
```

## When Inheritance Goes Wrong

Marcus is excited. He creates:

```python
class FragileExpressPackage(FragilePackage, ExpressPackage):
    """Both fragile AND express!"""
    pass
```

This... sort of works? But which `shipping_cost()` gets called? Which `__init__` runs? What if both parents modify the same attribute differently?

You've just hit the diamond problem.

## What You Learned

- **`class Child(Parent)`** — Child inherits all methods and attributes from Parent
- **`super().__init__()`** — call the parent's constructor to initialize inherited state
- **Method overriding** — redefine a parent method in the subclass
- **`super().method()`** — call the parent's version when extending (not replacing)
- **`isinstance(obj, Class)`** — check if an object is an instance of a class or its subclasses
- **Open/Closed Principle** — open for extension (new subclasses), closed for modification (don't change the base)

The duplication is gone. Three classes share one implementation of `ship()`, `deliver()`, and status validation. Changes propagate automatically.

But Marcus's `FragileExpressPackage(FragilePackage, ExpressPackage)` just opened a can of worms. When two parents inherit from the same grandparent, Python has to decide which path to follow.

That's the Method Resolution Order.

---

[← Chapter 2: Encapsulation](chapter-02-encapsulation.md) | [Chapter 4: The Diamond Problem →](chapter-04-mro.md)

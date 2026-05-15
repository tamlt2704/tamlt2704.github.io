# Chapter 8: Composition Over Inheritance

[← Chapter 7: Operators](chapter-07-operators.md) | [Chapter 9: Abstract Contracts →](chapter-09-abc.md)

---

## The Problem

Marcus built this inheritance hierarchy over the past month:

```
Package
├── TrackablePackage
│   ├── InsurableTrackablePackage
│   │   ├── PriorityInsurableTrackablePackage
│   │   │   └── FragilePriorityInsurableTrackablePackage
│   │   └── FragileInsurableTrackablePackage
│   └── PriorityTrackablePackage
├── InsurablePackage
│   └── PriorityInsurablePackage
├── PriorityPackage
└── FragilePackage
```

Seven levels deep. Twelve classes. And now the product team wants "refrigerated" packages. Marcus: "Do I need `RefrigeratedFragilePriorityInsurableTrackablePackage`?"

The problems:
1. **Combinatorial explosion** — N features means 2^N possible subclasses
2. **Rigid hierarchy** — can't add tracking to a `FragilePackage` without creating a new class
3. **Fragile base class** — changing `TrackablePackage` breaks everything below it
4. **God classes** — deep subclasses inherit methods they don't need

Dana: "You're modeling features as *types*. They should be *components*. A package isn't a TrackableInsurablePackage — it's a package that *has* tracking and *has* insurance."

## Has-A vs Is-A

The question to ask: "Is this an identity or a capability?"

- **Is-a**: An `ExpressPackage` IS a `Package` (identity — it's a kind of package)
- **Has-a**: A package HAS tracking, HAS insurance, HAS a shipping strategy (capabilities)

When you use inheritance for capabilities, you get the explosion above. Use composition instead:

```python
class Package:
    """Core package — identity and essential state."""

    def __init__(self, id, weight, destination):
        self.id = id
        self.weight = weight
        self.destination = destination
        self.status = "pending"

        # Composed capabilities — injected, not inherited
        self.tracker = None
        self.insurance = None
        self.shipping_strategy = StandardShipping()

    def shipping_cost(self):
        """Delegate to the shipping strategy."""
        return self.shipping_strategy.calculate(self.weight)

    def track(self, location):
        """Delegate to the tracker (if one exists)."""
        if self.tracker:
            self.tracker.record(location)

    @property
    def is_insured(self):
        return self.insurance is not None
```

## The Strategy Pattern

Instead of subclasses overriding `shipping_cost()`, inject a strategy object:

```python
class StandardShipping:
    """Standard ground shipping."""
    name = "standard"

    def calculate(self, weight):
        return 5.00 + (weight * 2.50)

    def estimated_days(self):
        return 5


class ExpressShipping:
    """Next-day air shipping."""
    name = "express"

    def calculate(self, weight):
        return 15.00 + (weight * 5.00)

    def estimated_days(self):
        return 1


class FreightShipping:
    """Heavy cargo shipping."""
    name = "freight"

    def calculate(self, weight):
        return 25.00 + (weight * 1.50)

    def estimated_days(self):
        return 10


class RefrigeratedShipping:
    """Temperature-controlled shipping."""
    name = "refrigerated"

    def calculate(self, weight):
        return 30.00 + (weight * 4.00)

    def estimated_days(self):
        return 3
```

Now any package can use any shipping method — no new subclass needed:

```python
pkg = Package("PKG-001", 5.0, "123 Main St")
print(pkg.shipping_cost())  # 17.50 (standard)

pkg.shipping_strategy = ExpressShipping()
print(pkg.shipping_cost())  # 40.00 (express)

pkg.shipping_strategy = RefrigeratedShipping()
print(pkg.shipping_cost())  # 50.00 (refrigerated)
```

You can even change the strategy at runtime. Try doing that with inheritance.

## Delegation: Tracker as a Component

```python
class GPSTracker:
    """Records GPS coordinates over time."""

    def __init__(self):
        self._events = []

    def record(self, location, timestamp=None):
        import time
        self._events.append({
            "location": location,
            "timestamp": timestamp or time.time(),
        })

    @property
    def last_location(self):
        return self._events[-1]["location"] if self._events else None

    @property
    def history(self):
        return list(self._events)


class InsurancePolicy:
    """Tracks insured value and claims."""

    def __init__(self, value, provider="ShipSafe"):
        self.insured_value = value
        self.provider = provider
        self._claimed = False

    @property
    def premium(self):
        return self.insured_value * 0.02

    def file_claim(self, reason):
        if self._claimed:
            raise RuntimeError("Claim already filed")
        self._claimed = True
        return {"value": self.insured_value, "reason": reason}
```

Compose them into a package:

```python
# A tracked, insured package with express shipping
pkg = Package("PKG-042", 3.0, "123 Main St")
pkg.tracker = GPSTracker()
pkg.insurance = InsurancePolicy(value=500.00)
pkg.shipping_strategy = ExpressShipping()

# Use the composed capabilities
pkg.track("Warehouse A")
pkg.track("Distribution Center")
print(pkg.tracker.last_location)  # "Distribution Center"
print(pkg.insurance.premium)       # 10.00
print(pkg.shipping_cost())         # 30.00
```

No `InsuredTrackedExpressPackage` class needed. Just a `Package` with components attached.

## Dependency Injection: Building Packages

A factory function makes composition clean:

```python
def create_premium_package(id, weight, destination, insured_value):
    """Create a fully-featured premium package."""
    pkg = Package(id, weight, destination)
    pkg.tracker = GPSTracker()
    pkg.insurance = InsurancePolicy(insured_value)
    pkg.shipping_strategy = ExpressShipping()
    return pkg

def create_fragile_package(id, weight, destination):
    """Create a package with careful handling."""
    pkg = Package(id, weight, destination)
    pkg.tracker = GPSTracker()
    pkg.shipping_strategy = StandardShipping()
    # Fragile handling is just a flag — not a whole class hierarchy
    pkg.requires_careful_handling = True
    return pkg
```

## Before and After

### Before: Inheritance Explosion

```python
# 12 classes, 7 levels deep
class TrackablePackage(Package): ...
class InsurableTrackablePackage(TrackablePackage): ...
class PriorityInsurableTrackablePackage(InsurableTrackablePackage): ...
# Adding "refrigerated" means 4+ new classes

# Rigid — can't change shipping method at runtime
pkg = PriorityInsurableTrackablePackage(...)
# This is ALWAYS priority. Can't downgrade to standard.
```

### After: Composition

```python
# 1 Package class + small focused components
class Package: ...           # Core identity
class GPSTracker: ...        # Tracking capability
class InsurancePolicy: ...   # Insurance capability
class ExpressShipping: ...   # Shipping strategy
class StandardShipping: ...  # Shipping strategy

# Flexible — combine any way you want
pkg = Package("PKG-001", 5.0, "addr")
pkg.tracker = GPSTracker()
pkg.shipping_strategy = ExpressShipping()

# Change at runtime
pkg.shipping_strategy = StandardShipping()  # Downgrade? No problem.
```

## When to Use Inheritance vs Composition

| Use Inheritance When... | Use Composition When... |
|---|---|
| True "is-a" relationship | "Has-a" or "uses-a" relationship |
| Subclass is a specialization | Feature is a capability that can be mixed |
| Behavior is fixed for the type | Behavior might change at runtime |
| Hierarchy is shallow (2-3 levels) | Combinations would explode |
| You want polymorphism with a base type | You want flexibility and swappability |

Dana's rule: "Inherit for identity. Compose for capability. If you're past 3 levels of inheritance, you're modeling capabilities as types."

## The Refactored Hierarchy

```
Package (core identity + composed components)
├── .tracker: GPSTracker | None
├── .insurance: InsurancePolicy | None
├── .shipping_strategy: ShippingStrategy
└── .handling: HandlingRequirements

ExpressPackage(Package)    — only if "express" is truly a different KIND of package
FragilePackage(Package)    — only if fragile changes core identity
```

Keep inheritance for true type distinctions. Use composition for everything else.

## What You Learned

- **Composition** — objects contain other objects as components
- **Has-a vs Is-a** — capabilities are "has-a," identity is "is-a"
- **Strategy pattern** — swap behavior by injecting different strategy objects
- **Delegation** — forward method calls to composed objects
- **Dependency injection** — pass components in rather than hardcoding them
- **Combinatorial explosion** — N features × inheritance = 2^N classes; composition = N components

The 12-class hierarchy is now 1 class with 4 composable components. Adding "refrigerated" is one new strategy class, not a cascade of subclasses.

But there's a new risk. With composition, nothing forces a shipping strategy to implement `calculate()`. If someone writes a strategy that's missing the method, it crashes at runtime. You need a way to enforce contracts.

---

[← Chapter 7: Operators](chapter-07-operators.md) | [Chapter 9: Abstract Contracts →](chapter-09-abc.md)

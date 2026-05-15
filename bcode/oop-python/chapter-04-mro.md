# Chapter 4: The Diamond Problem

[← Chapter 3: Inheritance](chapter-03-inheritance.md) | [Chapter 5: Polymorphism →](chapter-05-polymorphism.md)

---

## The Problem

Marcus created `FragileExpressPackage` by inheriting from both `FragilePackage` and `ExpressPackage`:

```python
class Package:
    def shipping_cost(self):
        return 5.00 + (self.weight * 2.50)

class ExpressPackage(Package):
    def shipping_cost(self):
        return 15.00 + (self.weight * 5.00)

class FragilePackage(Package):
    def shipping_cost(self):
        return super().shipping_cost() + 10.00

class FragileExpressPackage(FragilePackage, ExpressPackage):
    pass
```

The inheritance diamond:

```
        Package
       /       \
FragilePackage  ExpressPackage
       \       /
  FragileExpressPackage
```

Question: when you call `FragileExpressPackage(3.0, "addr", "sender").shipping_cost()`, which version runs?

```python
pkg = FragileExpressPackage(3.0, "123 Main St", "Alice")
print(pkg.shipping_cost())  # What do you expect?
```

Is it:
- `FragilePackage.shipping_cost()` → `super().shipping_cost() + 10` → uses `Package` base? = 22.50
- `FragilePackage.shipping_cost()` → `super().shipping_cost() + 10` → uses `ExpressPackage`? = 40.00

The answer is 40.00. And understanding why requires knowing the MRO.

## Method Resolution Order (MRO)

Python uses **C3 linearization** to determine the order in which classes are searched for a method:

```python
print(FragileExpressPackage.__mro__)
# (
#   <class 'FragileExpressPackage'>,
#   <class 'FragilePackage'>,
#   <class 'ExpressPackage'>,
#   <class 'Package'>,
#   <class 'object'>
# )
```

When you call `pkg.shipping_cost()`:
1. Python checks `FragileExpressPackage` — no `shipping_cost` defined
2. Checks `FragilePackage` — found! Calls it.
3. `FragilePackage.shipping_cost()` calls `super().shipping_cost()`
4. `super()` in `FragilePackage` doesn't mean "parent" — it means **next in MRO**
5. Next in MRO is `ExpressPackage`, so `ExpressPackage.shipping_cost()` runs
6. Result: `15.00 + (3.0 * 5.00) + 10.00 = 40.00`

The key insight: **`super()` follows the MRO, not the direct parent**. In a diamond, `super()` in `FragilePackage` calls `ExpressPackage`, not `Package`.

## C3 Linearization Rules

The MRO follows three rules:
1. A class always comes before its parents
2. If a class inherits from multiple parents, they maintain their order
3. A parent class appears only once (no duplicates)

```python
class A: pass
class B(A): pass
class C(A): pass
class D(B, C): pass

print(D.__mro__)  # D → B → C → A → object
```

Python guarantees: children before parents, left before right, each class appears once.

## The Real Problem: Cooperative `super()`

For multiple inheritance to work correctly, **every class in the chain** must call `super()`:

```python
class Package:
    def __init__(self, weight, destination, sender, **kwargs):
        super().__init__(**kwargs)  # Pass remaining kwargs up
        self.weight = weight
        self.destination = destination
        self.sender = sender
        self._status = "pending"

class ExpressPackage(Package):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.priority = "next_day"

class FragilePackage(Package):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.requires_signature = True

class FragileExpressPackage(FragilePackage, ExpressPackage):
    pass
```

This is called **cooperative multiple inheritance**. Each class takes what it needs from `**kwargs` and passes the rest along. It works, but it's fragile and hard to reason about.

Dana: "If you need a diagram to understand your class hierarchy, the hierarchy is too complex."

## The Better Way: Mixins

Instead of deep diamond hierarchies, use **mixins** — small, focused classes that add one capability:

```python
class Package:
    """Core package — weight, destination, status."""

    def __init__(self, weight, destination, sender):
        self.weight = weight
        self.destination = destination
        self.sender = sender
        self._status = "pending"

    def shipping_cost(self):
        return 5.00 + (self.weight * 2.50)

    def ship(self):
        self._status = "in_transit"


class TrackableMixin:
    """Adds GPS tracking capability."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tracking_events = []

    def add_tracking_event(self, location, timestamp):
        self._tracking_events.append({"location": location, "time": timestamp})

    @property
    def last_known_location(self):
        if self._tracking_events:
            return self._tracking_events[-1]["location"]
        return None


class InsurableMixin:
    """Adds insurance capability."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._insured_value = 0.0

    def insure(self, value):
        self._insured_value = value

    @property
    def insurance_premium(self):
        return self._insured_value * 0.02  # 2% of insured value


class SignatureRequiredMixin:
    """Requires signature on delivery."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._signature = None

    def sign(self, name):
        self._signature = name

    @property
    def is_signed(self):
        return self._signature is not None
```

Now compose exactly what you need:

```python
class TrackedPackage(TrackableMixin, Package):
    """A package with GPS tracking."""
    pass

class PremiumPackage(TrackableMixin, InsurableMixin, SignatureRequiredMixin, Package):
    """Full-featured premium package."""
    pass
```

```python
pkg = PremiumPackage(5.0, "123 Main St", "Alice")
pkg.add_tracking_event("Warehouse A", "2024-01-15 09:00")
pkg.insure(500.00)
print(pkg.last_known_location)  # "Warehouse A"
print(pkg.insurance_premium)    # 10.00
print(pkg.shipping_cost())      # 17.50
```

## Mixin Design Rules

Mixins work well when they follow these rules:

```python
# ✅ Good mixin: small, focused, no __init__ dependencies on specific parent
class TimestampMixin:
    """Adds created_at and updated_at tracking."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._created_at = time.time()
        self._updated_at = time.time()

    def touch(self):
        self._updated_at = time.time()

# ❌ Bad mixin: too much responsibility, assumes parent structure
class EverythingMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.weight = kwargs["weight"] * 1.1  # Overrides parent's weight!
        self._status = "special"               # Corrupts parent's status!
```

Rules:
1. **Single responsibility** — one mixin, one capability
2. **No state conflicts** — don't override attributes the base class owns
3. **Use `*args, **kwargs`** — pass through what you don't consume
4. **Name with `Mixin` suffix** — makes the intent clear
5. **Mixins go left** — `class X(MixinA, MixinB, BaseClass)` — base class last

## Inspecting the MRO

When debugging multiple inheritance, check the MRO:

```python
print(PremiumPackage.__mro__)
# PremiumPackage → TrackableMixin → InsurableMixin →
# SignatureRequiredMixin → Package → object

# Or more readable:
for cls in PremiumPackage.__mro__:
    print(f"  {cls.__name__}")
```

If the MRO surprises you, your hierarchy is too complex. Simplify.

## When Multiple Inheritance Is Appropriate

| Use Case | Approach |
|---|---|
| "Is-a" relationship (Express IS a Package) | Single inheritance |
| Adding capabilities (tracking, insurance) | Mixins |
| Combining unrelated behaviors | Mixins |
| Deep diamond hierarchies | **Refactor to composition** (Chapter 8) |

Dana's rule: "If your MRO has more than 6 entries, you've gone too far. Use composition instead."

## What You Learned

- **Diamond problem** — when two parents share a grandparent, method resolution is ambiguous
- **MRO (Method Resolution Order)** — Python's deterministic order for searching methods
- **C3 linearization** — the algorithm: children before parents, left before right, no duplicates
- **`super()` follows MRO** — not just "call parent," but "call next in the chain"
- **Cooperative inheritance** — every class calls `super()` and passes `**kwargs`
- **Mixins** — small classes that add one focused capability
- **Mixin conventions** — suffix with `Mixin`, put left of base class, use `*args/**kwargs`

The mixin pattern keeps multiple inheritance manageable. But there's still a problem in the codebase: the `calculate_shipping()` function has a giant if/elif chain checking package types by string. Every time you add a new package type, you have to modify that function.

There's a better way — let the objects decide their own behavior.

---

[← Chapter 3: Inheritance](chapter-03-inheritance.md) | [Chapter 5: Polymorphism →](chapter-05-polymorphism.md)

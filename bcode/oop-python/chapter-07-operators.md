# Chapter 7: Objects That Behave Like Built-ins — Operator Overloading

[← Chapter 6: Dunder Methods](chapter-06-dunder.md) | [Chapter 8: Composition →](chapter-08-composition.md)

---

## The Problem

Three things that should work but don't:

```python
# 1. Sort packages by weight
packages = [pkg_heavy, pkg_light, pkg_medium]
sorted(packages)
# TypeError: '<' not supported between instances of 'Package' and 'Package'

# 2. Combine two routes
morning_route = Route(["Warehouse", "Stop A", "Stop B"])
afternoon_route = Route(["Stop C", "Stop D", "Depot"])
full_route = morning_route + afternoon_route
# TypeError: unsupported operand type(s) for +: 'Route' and 'Route'

# 3. Check if a package is in a warehouse
if pkg in warehouse:
    print("Found it")
# TypeError: argument of type 'Warehouse' is not iterable
```

Python's built-in types (`list`, `int`, `str`) support operators because they implement special dunder methods. Your custom classes can do the same.

## Comparison Operators: Sortable Packages

To make packages sortable by weight, implement `__lt__` (less than):

```python
from functools import total_ordering

@total_ordering
class Package:
    def __init__(self, id, weight, destination):
        self.id = id
        self.weight = weight
        self.destination = destination

    def __eq__(self, other):
        if not isinstance(other, Package):
            return NotImplemented
        return self.id == other.id

    def __lt__(self, other):
        """Packages are ordered by weight."""
        if not isinstance(other, Package):
            return NotImplemented
        return self.weight < other.weight

    def __repr__(self):
        return f"Package({self.id!r}, {self.weight}kg)"
```

`@total_ordering` fills in `__le__`, `__gt__`, `__ge__` from your `__eq__` and `__lt__`:

```python
light = Package("PKG-001", 1.5, "addr")
medium = Package("PKG-002", 5.0, "addr")
heavy = Package("PKG-003", 20.0, "addr")

print(light < heavy)    # True
print(heavy >= medium)  # True (from @total_ordering)

# Sorting works now
packages = [heavy, light, medium]
print(sorted(packages))
# [Package('PKG-001', 1.5kg), Package('PKG-002', 5.0kg), Package('PKG-003', 20.0kg)]

# min/max work too
print(min(packages))  # Package('PKG-001', 1.5kg)
print(max(packages))  # Package('PKG-003', 20.0kg)
```

## Arithmetic Operators: Combinable Routes

```python
class Route:
    def __init__(self, stops):
        self.stops = list(stops)

    def __add__(self, other):
        """Combine two routes: route1 + route2."""
        if not isinstance(other, Route):
            return NotImplemented
        # Connect: last stop of first route is first stop of second
        combined = self.stops + other.stops[1:] if self.stops[-1] == other.stops[0] else self.stops + other.stops
        return Route(combined)

    def __iadd__(self, other):
        """In-place addition: route1 += route2."""
        if not isinstance(other, Route):
            return NotImplemented
        if self.stops[-1] == other.stops[0]:
            self.stops.extend(other.stops[1:])
        else:
            self.stops.extend(other.stops)
        return self

    def __len__(self):
        return len(self.stops)

    def __repr__(self):
        return f"Route({self.stops})"
```

```python
morning = Route(["Warehouse", "Stop A", "Stop B"])
afternoon = Route(["Stop B", "Stop C", "Depot"])

full = morning + afternoon  # Connects at "Stop B"
print(full)
# Route(['Warehouse', 'Stop A', 'Stop B', 'Stop C', 'Depot'])

# In-place works too
morning += afternoon
print(morning)
# Route(['Warehouse', 'Stop A', 'Stop B', 'Stop C', 'Depot'])
```

## Container Operators: `in` and Iteration

```python
class Warehouse:
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity
        self._packages = {}  # id → Package

    def store(self, package):
        if len(self._packages) >= self.capacity:
            raise RuntimeError(f"Warehouse {self.name} is full")
        self._packages[package.id] = package

    def remove(self, package_id):
        return self._packages.pop(package_id, None)

    def __contains__(self, item):
        """Support 'package in warehouse' syntax."""
        if isinstance(item, Package):
            return item.id in self._packages
        if isinstance(item, str):
            return item in self._packages  # Check by ID string
        return False

    def __iter__(self):
        """Support 'for package in warehouse' syntax."""
        return iter(self._packages.values())

    def __len__(self):
        return len(self._packages)

    def __getitem__(self, package_id):
        """Support warehouse['PKG-001'] syntax."""
        return self._packages[package_id]

    def __repr__(self):
        return f"Warehouse({self.name!r}, {len(self)}/{self.capacity} packages)"
```

```python
warehouse = Warehouse("East Hub", capacity=100)
pkg1 = Package("PKG-001", 2.0, "addr")
pkg2 = Package("PKG-002", 5.0, "addr")

warehouse.store(pkg1)
warehouse.store(pkg2)

# __contains__
print(pkg1 in warehouse)       # True
print("PKG-001" in warehouse)  # True
print("PKG-999" in warehouse)  # False

# __iter__
for pkg in warehouse:
    print(f"  {pkg}")
# Package('PKG-001', 2.0kg)
# Package('PKG-002', 5.0kg)

# __getitem__
print(warehouse["PKG-001"])  # Package('PKG-001', 2.0kg)

# __len__
print(f"Warehouse has {len(warehouse)} packages")  # 2
```

## Multiplication: Scaling Shipments

```python
class Shipment:
    """A batch of identical packages."""

    def __init__(self, package, quantity):
        self.package = package
        self.quantity = quantity

    def __mul__(self, factor):
        """Scale a shipment: shipment * 3."""
        if not isinstance(factor, int):
            return NotImplemented
        return Shipment(self.package, self.quantity * factor)

    def __rmul__(self, factor):
        """Support 3 * shipment (reversed operand)."""
        return self.__mul__(factor)

    @property
    def total_weight(self):
        return self.package.weight * self.quantity

    def __repr__(self):
        return f"Shipment({self.package!r} × {self.quantity})"
```

```python
pkg = Package("PKG-001", 2.0, "addr")
batch = Shipment(pkg, 10)

doubled = batch * 2
print(doubled)              # Shipment(Package('PKG-001', 2.0kg) × 20)
print(doubled.total_weight) # 40.0

# Reversed works too
tripled = 3 * batch
print(tripled)  # Shipment(Package('PKG-001', 2.0kg) × 30)
```

`__rmul__` handles the case where the left operand doesn't know how to multiply with your type (`int.__mul__(3, shipment)` returns `NotImplemented`, so Python tries `shipment.__rmul__(3)`).

## The Complete Operator Reference

| Operator | Method | Reverse | In-place |
|---|---|---|---|
| `+` | `__add__` | `__radd__` | `__iadd__` |
| `-` | `__sub__` | `__rsub__` | `__isub__` |
| `*` | `__mul__` | `__rmul__` | `__imul__` |
| `<` | `__lt__` | — | — |
| `<=` | `__le__` | — | — |
| `==` | `__eq__` | — | — |
| `in` | `__contains__` | — | — |
| `[]` | `__getitem__` | — | `__setitem__` |
| `len()` | `__len__` | — | — |
| `iter()` | `__iter__` | — | — |

## When Operator Overloading Goes Wrong

Marcus gets creative:

```python
class Package:
    def __add__(self, other):
        """Merge two packages into one?!"""
        return Package(
            self.id + "+" + other.id,
            self.weight + other.weight,
            self.destination  # Whose destination??
        )
```

Dana: "Operators should be intuitive. If `pkg1 + pkg2` doesn't have an obvious meaning, use a named method instead."

```python
# ❌ Confusing — what does "adding" packages mean?
merged = pkg1 + pkg2

# ✅ Clear — explicit method name
merged = Package.merge(pkg1, pkg2)
```

Rule: only overload operators when the meaning is **obvious** to someone reading the code. `Route + Route` = combined route (clear). `Package + Package` = ??? (confusing).

## What You Learned

- **`@total_ordering`** — implement `__eq__` + `__lt__`, get all comparison operators free
- **`__add__`, `__iadd__`** — define `+` and `+=` for your objects
- **`__rmul__`** — handle reversed operands (`3 * obj`)
- **`__contains__`** — define what `in` means for your container
- **`__iter__`** — make your object work in `for` loops
- **`__getitem__`** — support `obj[key]` subscript access
- **Operator discipline** — only overload when the meaning is obvious

Packages sort by weight. Routes combine with `+`. Warehouses support `in` and `for`. The objects behave like Python built-ins.

But there's a growing problem. Marcus built a 7-level inheritance hierarchy: `Package → TrackablePackage → InsurableTrackablePackage → PriorityInsurableTrackablePackage → ...`. Every change to the base class cascades unpredictably. Every new feature requires a new subclass.

It's time to learn when inheritance is the wrong tool.

---

[← Chapter 6: Dunder Methods](chapter-06-dunder.md) | [Chapter 8: Composition →](chapter-08-composition.md)

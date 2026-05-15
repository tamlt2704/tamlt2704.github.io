# Chapter 6: Objects That Describe Themselves — Dunder Methods

[← Chapter 5: Polymorphism](chapter-05-polymorphism.md) | [Chapter 7: Operators →](chapter-07-operators.md)

---

## The Problem

It's 2 AM. The routing engine crashed. You're staring at logs:

```
ERROR: Failed to process package <shipfast.Package object at 0x7f3a2b1c4d50>
ERROR: Duplicate detected: <shipfast.Package object at 0x7f3a2b1c4d50> == <shipfast.Package object at 0x7f3a9c2e1a80>?
ERROR: Package set contains 847 items (expected 200)
```

Which package failed? Are those two objects actually the same package? Why does the set have duplicates?

You can't debug what you can't see. Python's default `__repr__` is useless, its default `__eq__` compares memory addresses (not package IDs), and its default `__hash__` means two Package objects with the same ID are treated as different in sets and dicts.

Dana: "Make the objects tell you what they are."

## `__repr__`: The Developer's View

`__repr__` should return a string that helps you **recreate** the object (or at least identify it):

```python
class Package:
    def __init__(self, id, weight, destination):
        self.id = id
        self.weight = weight
        self.destination = destination
        self.status = "pending"

    def __repr__(self):
        return (
            f"Package(id={self.id!r}, weight={self.weight}, "
            f"destination={self.destination!r}, status={self.status!r})"
        )
```

```python
pkg = Package("PKG-00042", 3.5, "123 Main St")
print(repr(pkg))
# Package(id='PKG-00042', weight=3.5, destination='123 Main St', status='pending')
```

Now the error log is useful:

```
ERROR: Failed to process Package(id='PKG-00042', weight=3.5, destination='123 Main St', status='in_transit')
```

The `!r` format spec applies `repr()` to the value — it adds quotes around strings so you can distinguish `status='pending'` from `status=pending` (which would be a variable name).

## `__str__`: The User's View

`__str__` is for human-readable display — what end users or non-technical logs should see:

```python
class Package:
    def __init__(self, id, weight, destination):
        self.id = id
        self.weight = weight
        self.destination = destination
        self.status = "pending"

    def __repr__(self):
        return f"Package(id={self.id!r}, weight={self.weight}, status={self.status!r})"

    def __str__(self):
        return f"📦 {self.id} → {self.destination} ({self.weight}kg, {self.status})"
```

```python
pkg = Package("PKG-00042", 3.5, "123 Main St")

print(repr(pkg))  # Package(id='PKG-00042', weight=3.5, status='pending')
print(str(pkg))   # 📦 PKG-00042 → 123 Main St (3.5kg, pending)
print(pkg)        # Uses __str__ → 📦 PKG-00042 → 123 Main St (3.5kg, pending)

# In f-strings:
print(f"Processing: {pkg}")    # Uses __str__
print(f"Debug: {pkg!r}")       # Uses __repr__
```

Rule: `__repr__` is for developers (debugging). `__str__` is for users (display). If you only implement one, implement `__repr__` — Python falls back to it when `__str__` isn't defined.

## `__eq__`: When Are Two Objects "Equal"?

By default, Python compares objects by identity (memory address):

```python
pkg1 = Package("PKG-00042", 3.5, "123 Main St")
pkg2 = Package("PKG-00042", 3.5, "123 Main St")

print(pkg1 == pkg2)  # False! Different objects in memory.
print(pkg1 is pkg2)  # False — different memory addresses
```

But logically, two Package objects with the same ID represent the same package. Define `__eq__`:

```python
class Package:
    def __init__(self, id, weight, destination):
        self.id = id
        self.weight = weight
        self.destination = destination

    def __eq__(self, other):
        if not isinstance(other, Package):
            return NotImplemented  # Let Python try the other object's __eq__
        return self.id == other.id

    def __repr__(self):
        return f"Package(id={self.id!r}, weight={self.weight})"
```

```python
pkg1 = Package("PKG-00042", 3.5, "123 Main St")
pkg2 = Package("PKG-00042", 3.5, "123 Main St")
pkg3 = Package("PKG-00099", 1.0, "456 Oak Ave")

print(pkg1 == pkg2)  # True — same ID
print(pkg1 == pkg3)  # False — different ID
print(pkg1 == "PKG-00042")  # NotImplemented → False
```

`NotImplemented` (not `NotImplementedError`) tells Python: "I don't know how to compare myself to this type — ask the other object."

## `__hash__`: Making Objects Work in Sets and Dicts

If you define `__eq__`, Python makes your class **unhashable** by default:

```python
pkg = Package("PKG-00042", 3.5, "123 Main St")
{pkg}  # TypeError: unhashable type: 'Package'
```

To use objects in sets or as dict keys, define `__hash__` consistent with `__eq__`:

```python
class Package:
    def __init__(self, id, weight, destination):
        self.id = id
        self.weight = weight
        self.destination = destination

    def __eq__(self, other):
        if not isinstance(other, Package):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"Package(id={self.id!r})"
```

```python
pkg1 = Package("PKG-00042", 3.5, "123 Main St")
pkg2 = Package("PKG-00042", 3.5, "123 Main St")

# Now works in sets — duplicates detected by ID
packages = {pkg1, pkg2}
print(len(packages))  # 1 — they're the same package

# Works as dict keys
tracking = {pkg1: "Warehouse A"}
print(tracking[pkg2])  # "Warehouse A" — same hash, same equality
```

The rule: **objects that are equal must have the same hash**. Hash by the same fields you compare in `__eq__`.

## `__bool__`: Truthiness

By default, all objects are truthy. You can customize this:

```python
class Route:
    def __init__(self):
        self.stops = []

    def add_stop(self, location):
        self.stops.append(location)

    def __bool__(self):
        """A route is truthy if it has at least one stop."""
        return len(self.stops) > 0

    def __repr__(self):
        return f"Route(stops={self.stops})"
```

```python
route = Route()
if not route:
    print("Empty route — nothing to dispatch")  # This prints

route.add_stop("Warehouse A")
if route:
    print("Route has stops — ready to dispatch")  # This prints
```

## `__len__`: How Big Is It?

```python
class Warehouse:
    def __init__(self, name):
        self.name = name
        self._packages = []

    def store(self, package):
        self._packages.append(package)

    def __len__(self):
        """Number of packages in the warehouse."""
        return len(self._packages)

    def __bool__(self):
        """Warehouse is truthy if it has packages."""
        return len(self._packages) > 0
```

```python
warehouse = Warehouse("East Hub")
print(len(warehouse))  # 0

warehouse.store(Package("PKG-001", 2.0, "addr"))
warehouse.store(Package("PKG-002", 5.0, "addr"))
print(len(warehouse))  # 2
```

## Putting It All Together

```python
class Package:
    """A fully self-describing package."""

    def __init__(self, id, weight, destination):
        self.id = id
        self.weight = weight
        self.destination = destination
        self.status = "pending"

    def __repr__(self):
        return (
            f"Package(id={self.id!r}, weight={self.weight}, "
            f"status={self.status!r})"
        )

    def __str__(self):
        return f"📦 {self.id} ({self.weight}kg) → {self.destination}"

    def __eq__(self, other):
        if not isinstance(other, Package):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __bool__(self):
        """A package is truthy if it hasn't been delivered yet (still active)."""
        return self.status != "delivered"
```

```python
pkg = Package("PKG-00042", 3.5, "123 Main St")

# Debugging
print(f"Processing {pkg!r}")
# Processing Package(id='PKG-00042', weight=3.5, status='pending')

# User-facing
print(f"Your shipment: {pkg}")
# Your shipment: 📦 PKG-00042 (3.5kg) → 123 Main St

# Deduplication
all_packages = {pkg, Package("PKG-00042", 3.5, "123 Main St")}
print(len(all_packages))  # 1

# Conditional logic
if pkg:
    print("Still in transit")
```

## What You Learned

- **`__repr__`** — developer-facing string, used in debuggers and logs
- **`__str__`** — user-facing string, used by `print()` and f-strings
- **`__eq__`** — defines equality (what `==` means for your objects)
- **`__hash__`** — enables use in sets and dict keys (must be consistent with `__eq__`)
- **`__bool__`** — defines truthiness for `if obj:` checks
- **`__len__`** — defines what `len(obj)` returns
- **`NotImplemented`** — return this from `__eq__` for unsupported comparisons

Objects now describe themselves. Debugging is possible. Sets work correctly. But you still can't sort a list of packages by weight, combine two routes, or check if a package is in a warehouse using `in`.

For that, you need operator overloading.

---

[← Chapter 5: Polymorphism](chapter-05-polymorphism.md) | [Chapter 7: Operators →](chapter-07-operators.md)

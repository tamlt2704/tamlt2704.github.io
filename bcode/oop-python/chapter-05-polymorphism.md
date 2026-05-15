# Chapter 5: One Interface, Many Forms — Polymorphism

[← Chapter 4: The Diamond Problem](chapter-04-mro.md) | [Chapter 6: Dunder Methods →](chapter-06-dunder.md)

---

## The Problem

The billing module has this function:

```python
def calculate_shipping(package_type, weight, destination):
    """Calculate shipping cost based on package type."""
    if package_type == "standard":
        cost = 5.00 + (weight * 2.50)
    elif package_type == "express":
        cost = 15.00 + (weight * 5.00)
    elif package_type == "fragile":
        cost = 5.00 + (weight * 2.50) + 10.00
    elif package_type == "oversized":
        cost = 5.00 + (weight * 2.50) + (weight - 30) * 4.00
    elif package_type == "international":
        cost = 25.00 + (weight * 8.00)
    elif package_type == "hazmat":
        cost = 50.00 + (weight * 12.00)
    else:
        raise ValueError(f"Unknown package type: {package_type}")

    # Apply destination surcharges
    if package_type == "international":
        cost += _international_surcharge(destination)
    if package_type in ("fragile", "hazmat"):
        cost += _handling_fee(weight)

    return cost
```

Every new package type means modifying this function. And there are six more functions just like it: `estimate_delivery_time()`, `get_required_vehicle()`, `calculate_insurance()`, `validate_contents()`, `generate_label()`, `assign_handler()`.

Marcus adds "refrigerated" packages. He updates `calculate_shipping` but forgets `get_required_vehicle`. The refrigerated package gets assigned to a regular van. Frozen goods arrive thawed.

Dana: "The package should know its own shipping cost. Stop asking what type it is."

## Polymorphism: Let Objects Decide

Instead of external code checking types, each object implements its own version of the method:

```python
class Package:
    def __init__(self, weight, destination):
        self.weight = weight
        self.destination = destination

    def shipping_cost(self):
        return 5.00 + (self.weight * 2.50)

    def required_vehicle(self):
        return "standard_van"

    def delivery_estimate_days(self):
        return 5


class ExpressPackage(Package):
    def shipping_cost(self):
        return 15.00 + (self.weight * 5.00)

    def required_vehicle(self):
        return "priority_van"

    def delivery_estimate_days(self):
        return 1


class HazmatPackage(Package):
    def shipping_cost(self):
        return 50.00 + (self.weight * 12.00)

    def required_vehicle(self):
        return "hazmat_certified_truck"

    def delivery_estimate_days(self):
        return 7
```

Now the billing function is trivial:

```python
def calculate_shipping(package):
    """Works with ANY package type. No if/elif needed."""
    return package.shipping_cost()

def assign_vehicle(package):
    """Works with ANY package type."""
    return package.required_vehicle()
```

Add a new package type? Create a new class. No existing code changes:

```python
class RefrigeratedPackage(Package):
    def shipping_cost(self):
        return 20.00 + (self.weight * 6.00)

    def required_vehicle(self):
        return "refrigerated_truck"  # Can't forget this anymore

    def delivery_estimate_days(self):
        return 2
```

## Duck Typing: "If It Quacks..."

Python doesn't require inheritance for polymorphism. If an object has the right methods, it works:

```python
class ThirdPartyPackage:
    """From an external API — doesn't inherit from our Package class."""

    def __init__(self, data):
        self.weight = data["weight_kg"]
        self.destination = data["dest"]

    def shipping_cost(self):
        return data["quoted_price"]

    def required_vehicle(self):
        return "standard_van"


def process_shipment(package):
    """Doesn't care about the class — only that the methods exist."""
    cost = package.shipping_cost()
    vehicle = package.required_vehicle()
    print(f"Shipping for ${cost:.2f} via {vehicle}")

# All of these work:
process_shipment(Package(3.0, "addr"))
process_shipment(ExpressPackage(3.0, "addr"))
process_shipment(ThirdPartyPackage({"weight_kg": 3.0, "dest": "addr", "quoted_price": 12.0}))
```

This is **duck typing**: "If it walks like a duck and quacks like a duck, it's a duck." Python doesn't check the class — it checks whether the method exists when you call it.

## Protocol: Structural Typing for Duck Types

Duck typing is powerful but invisible. How does a developer know what methods `process_shipment` expects? Use `Protocol` from `typing`:

```python
from typing import Protocol

class Shippable(Protocol):
    """Any object that can be shipped."""

    weight: float
    destination: str

    def shipping_cost(self) -> float: ...
    def required_vehicle(self) -> str: ...
    def delivery_estimate_days(self) -> int: ...


def process_shipment(package: Shippable) -> float:
    """Process any shippable object."""
    cost = package.shipping_cost()
    vehicle = package.required_vehicle()
    days = package.delivery_estimate_days()
    print(f"${cost:.2f} via {vehicle}, ETA {days} days")
    return cost
```

`Protocol` is a **structural type** — it says "any object with these methods" without requiring inheritance. It's documentation that type checkers (mypy, pyright) can verify:

```python
class BrokenPackage:
    def shipping_cost(self):
        return 10.0
    # Missing required_vehicle and delivery_estimate_days!

process_shipment(BrokenPackage())
# mypy error: "BrokenPackage" is not compatible with "Shippable"
# Missing methods: required_vehicle, delivery_estimate_days
```

The code still runs (Python is dynamic), but the type checker catches the mistake before production.

## Dispatch Without Conditionals

The old pattern:

```python
# ❌ Adding a type means modifying every function
def generate_label(package_type, package_data):
    if package_type == "standard":
        return _standard_label(package_data)
    elif package_type == "express":
        return _express_label(package_data)
    elif package_type == "hazmat":
        return _hazmat_label(package_data)
    # ... grows forever
```

The polymorphic pattern:

```python
# ✅ Adding a type means creating a new class — nothing else changes
class Package:
    def generate_label(self):
        return f"STANDARD | {self.weight}kg | {self.destination}"

class ExpressPackage(Package):
    def generate_label(self):
        return f"⚡ EXPRESS | {self.weight}kg | {self.destination} | PRIORITY"

class HazmatPackage(Package):
    def generate_label(self):
        return f"☠️ HAZMAT | {self.weight}kg | {self.destination} | HANDLE WITH CARE"


# Caller doesn't know or care about the type
def print_all_labels(packages):
    for pkg in packages:
        print(pkg.generate_label())
```

## Real Example: The Notification System

ShipFast sends notifications when packages change status. The old code:

```python
def notify_status_change(package, channel):
    if channel == "email":
        send_email(package.sender_email, f"Package {package.id} is now {package.status}")
    elif channel == "sms":
        send_sms(package.sender_phone, f"PKG {package.id}: {package.status}")
    elif channel == "webhook":
        post_webhook(package.sender_webhook_url, {"id": package.id, "status": package.status})
    elif channel == "slack":
        post_slack(package.sender_slack_channel, f"📦 {package.id} → {package.status}")
```

Polymorphic version:

```python
class NotificationChannel(Protocol):
    def send(self, package_id: str, status: str, recipient: str) -> None: ...

class EmailNotifier:
    def send(self, package_id, status, recipient):
        send_email(recipient, f"Package {package_id} is now {status}")

class SMSNotifier:
    def send(self, package_id, status, recipient):
        send_sms(recipient, f"PKG {package_id}: {status}")

class WebhookNotifier:
    def send(self, package_id, status, recipient):
        post_webhook(recipient, {"id": package_id, "status": status})

class SlackNotifier:
    def send(self, package_id, status, recipient):
        post_slack(recipient, f"📦 {package_id} → {status}")


def notify_status_change(package, notifier: NotificationChannel):
    """Works with any notifier — current or future."""
    notifier.send(package.id, package.status, package.sender_contact)
```

Adding push notifications? Create `PushNotifier` with a `send` method. Zero changes to existing code.

## When to Use Each Approach

| Situation | Approach |
|---|---|
| Related types with shared base | Inheritance + method overriding |
| Unrelated types with same interface | Duck typing + Protocol |
| Need type checker enforcement | Protocol |
| Simple one-off function | Just check with `hasattr()` |

## What You Learned

- **Polymorphism** — same method name, different behavior per class
- **Dispatch without conditionals** — let objects decide their own behavior
- **Duck typing** — Python checks methods at call time, not class hierarchy
- **Protocol** — structural typing that documents expected interfaces
- **Open/Closed Principle** — open for extension (new classes), closed for modification (no if/elif changes)

The if/elif chains are gone. Each package type owns its behavior. Adding new types doesn't touch existing code.

But there's a debugging problem. When you `print(package)` to inspect it, you get `<Package object at 0x7f3a2b1c4d50>`. Useless. You need objects that can describe themselves.

---

[← Chapter 4: The Diamond Problem](chapter-04-mro.md) | [Chapter 6: Dunder Methods →](chapter-06-dunder.md)

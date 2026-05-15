# Chapter 9: Abstract Contracts — ABC

[← Chapter 8: Composition](chapter-08-composition.md) | [Chapter 10: Class Machinery →](chapter-10-classmethod.md)

---

## The Problem

After the composition refactoring, Marcus writes a new shipping provider:

```python
class DroneShipping:
    """Experimental drone delivery."""
    name = "drone"

    def cost(self, weight):  # Wrong method name! Should be 'calculate'
        return 8.00 + (weight * 3.00)

    def eta(self):  # Wrong method name! Should be 'estimated_days'
        return 0  # Same-day
```

He plugs it in:

```python
pkg = Package("PKG-001", 2.0, "addr")
pkg.shipping_strategy = DroneShipping()
print(pkg.shipping_cost())
# AttributeError: 'DroneShipping' object has no attribute 'calculate'
```

This crashes at **runtime** — in production, when a customer tries to ship a package. The bug could have been caught at class definition time if there was a contract saying "every shipping strategy MUST implement `calculate()` and `estimated_days()`."

Dana: "We need interfaces. Not Java-style ceremony — just enough to catch missing methods early."

## Abstract Base Classes

Python's `abc` module lets you define abstract classes that **cannot be instantiated** unless all abstract methods are implemented:

```python
from abc import ABC, abstractmethod

class ShippingStrategy(ABC):
    """Contract: all shipping strategies must implement these methods."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this shipping method."""
        ...

    @abstractmethod
    def calculate(self, weight: float) -> float:
        """Calculate shipping cost for the given weight in kg."""
        ...

    @abstractmethod
    def estimated_days(self) -> int:
        """Estimated delivery time in business days."""
        ...
```

Now if Marcus forgets a method, he finds out immediately:

```python
class DroneShipping(ShippingStrategy):
    name = "drone"

    def calculate(self, weight):
        return 8.00 + (weight * 3.00)

    # Forgot estimated_days!

drone = DroneShipping()
# TypeError: Can't instantiate abstract class DroneShipping
#   with abstract method estimated_days
```

The error happens at **instantiation**, not when the method is called. No more production crashes from missing methods.

## Implementing the Contract

```python
class StandardShipping(ShippingStrategy):
    name = "standard"

    def calculate(self, weight):
        return 5.00 + (weight * 2.50)

    def estimated_days(self):
        return 5


class ExpressShipping(ShippingStrategy):
    name = "express"

    def calculate(self, weight):
        return 15.00 + (weight * 5.00)

    def estimated_days(self):
        return 1


class DroneShipping(ShippingStrategy):
    name = "drone"

    def calculate(self, weight):
        return 8.00 + (weight * 3.00)

    def estimated_days(self):
        return 0  # Same-day
```

All three satisfy the contract. They can be used interchangeably anywhere a `ShippingStrategy` is expected.

## Abstract Properties

You can make properties abstract too:

```python
from abc import ABC, abstractmethod

class Vehicle(ABC):
    """Contract for delivery vehicles."""

    @property
    @abstractmethod
    def capacity_kg(self) -> float:
        """Maximum cargo weight in kg."""
        ...

    @property
    @abstractmethod
    def fuel_type(self) -> str:
        """Type of fuel this vehicle uses."""
        ...

    @abstractmethod
    def can_carry(self, package) -> bool:
        """Whether this vehicle can carry the given package."""
        ...


class Van(Vehicle):
    @property
    def capacity_kg(self):
        return 1000.0

    @property
    def fuel_type(self):
        return "diesel"

    def can_carry(self, package):
        return package.weight <= self.capacity_kg


class Bicycle(Vehicle):
    @property
    def capacity_kg(self):
        return 10.0

    @property
    def fuel_type(self):
        return "human"

    def can_carry(self, package):
        return package.weight <= self.capacity_kg and not package.requires_careful_handling
```

## Providing Default Implementations

Abstract classes can have concrete methods too — shared logic that subclasses inherit:

```python
class ShippingStrategy(ABC):
    @abstractmethod
    def calculate(self, weight: float) -> float:
        ...

    @abstractmethod
    def estimated_days(self) -> int:
        ...

    def calculate_with_insurance(self, weight: float, insured_value: float) -> float:
        """Concrete method — all strategies get this for free."""
        base_cost = self.calculate(weight)
        insurance_fee = insured_value * 0.02
        return base_cost + insurance_fee

    def summary(self, weight: float) -> str:
        """Concrete method using abstract methods."""
        cost = self.calculate(weight)
        days = self.estimated_days()
        return f"${cost:.2f}, {days} business days"
```

Subclasses must implement `calculate` and `estimated_days`, but they get `calculate_with_insurance` and `summary` for free.

## A Real Example: The Notification System

```python
class NotificationChannel(ABC):
    """Contract for all notification channels."""

    @property
    @abstractmethod
    def channel_name(self) -> str:
        ...

    @abstractmethod
    def send(self, recipient: str, message: str) -> bool:
        """Send a notification. Returns True if successful."""
        ...

    @abstractmethod
    def validate_recipient(self, recipient: str) -> bool:
        """Check if the recipient address is valid for this channel."""
        ...

    def send_if_valid(self, recipient: str, message: str) -> bool:
        """Concrete: validate then send."""
        if not self.validate_recipient(recipient):
            return False
        return self.send(recipient, message)


class EmailChannel(NotificationChannel):
    channel_name = "email"

    def send(self, recipient, message):
        # Send email logic
        print(f"📧 → {recipient}: {message}")
        return True

    def validate_recipient(self, recipient):
        return "@" in recipient and "." in recipient


class SMSChannel(NotificationChannel):
    channel_name = "sms"

    def send(self, recipient, message):
        print(f"📱 → {recipient}: {message[:160]}")
        return True

    def validate_recipient(self, recipient):
        return recipient.startswith("+") and len(recipient) >= 10
```

## ABC vs Protocol: When to Use Which

| Feature | ABC | Protocol |
|---|---|---|
| Enforcement | At instantiation time | At type-check time (mypy) |
| Requires inheritance | Yes (`class X(MyABC)`) | No (structural) |
| Runtime check | `isinstance(obj, MyABC)` works | Doesn't work without `@runtime_checkable` |
| Default methods | Yes | No |
| Best for | Internal hierarchies you control | External/third-party code |

```python
# ABC: "You MUST inherit from me"
class ShippingStrategy(ABC):
    @abstractmethod
    def calculate(self, weight): ...

class Express(ShippingStrategy):  # Must inherit
    def calculate(self, weight):
        return 15.0 + weight * 5.0

# Protocol: "Just have the right methods"
from typing import Protocol

class Shippable(Protocol):
    def calculate(self, weight: float) -> float: ...

class ThirdPartyShipper:  # No inheritance needed
    def calculate(self, weight):
        return weight * 3.0
```

Use ABC when you control the hierarchy and want runtime enforcement. Use Protocol when you want structural typing without forcing inheritance.

## When ABCs Are Overkill

Not everything needs an abstract class:

```python
# ❌ Overkill — only one implementation exists
class AbstractDatabaseConnection(ABC):
    @abstractmethod
    def connect(self): ...
    @abstractmethod
    def query(self, sql): ...

class PostgresConnection(AbstractDatabaseConnection):
    # The only implementation...

# ✅ Just use the class directly
class PostgresConnection:
    def connect(self): ...
    def query(self, sql): ...
```

Dana's rule: "Don't create an ABC until you have at least two implementations. Premature abstraction is worse than no abstraction."

## What You Learned

- **ABC (Abstract Base Class)** — defines a contract that subclasses must fulfill
- **`@abstractmethod`** — marks methods that MUST be implemented by subclasses
- **`@property` + `@abstractmethod`** — abstract properties
- **Instantiation enforcement** — can't create an instance of a class with missing abstract methods
- **Concrete methods in ABCs** — shared logic that uses abstract methods
- **ABC vs Protocol** — ABC for internal hierarchies, Protocol for structural typing
- **When to avoid ABCs** — don't abstract until you have multiple implementations

The contracts are enforced. No more missing methods in production. But there's another pattern emerging: you need to create packages from different sources — JSON payloads, CSV rows, API responses. Each needs a different constructor.

Python only allows one `__init__`. How do you provide alternative ways to create objects?

---

[← Chapter 8: Composition](chapter-08-composition.md) | [Chapter 10: Class Machinery →](chapter-10-classmethod.md)

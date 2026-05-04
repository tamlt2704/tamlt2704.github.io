# Chapter 2: The instanceof Staircase

[← Chapter 1: The DTO Graveyard](chapter-01-records.md) | [Chapter 3: The Switch From Hell →](chapter-03-switch-expressions.md)

---

## The Incident

Priya opens `PaymentProcessor.java` during code review. 217 lines. One method. An `instanceof` chain that handles every payment event type:

```java
public String process(PaymentEvent event) {
    if (event instanceof PaymentReceived) {
        PaymentReceived e = (PaymentReceived) event;
        return "Received " + e.getAmount() + " " + e.getCurrency();
    } else if (event instanceof PaymentRefunded) {
        PaymentRefunded e = (PaymentRefunded) event;
        return "Refunded " + e.getAmount() + " reason: " + e.getReason();
    } else if (event instanceof PaymentDisputed) {
        PaymentDisputed e = (PaymentDisputed) event;
        return "Disputed by " + e.getCustomerId();
    } else if (event instanceof PaymentChargedBack) {
        PaymentChargedBack e = (PaymentChargedBack) event;
        return "Chargeback " + e.getAmount();
    } else {
        throw new IllegalArgumentException("Unknown event: " + event.getClass());
    }
}
```

Two problems:

1. Every branch casts manually — `(PaymentReceived) event` — even though you just checked the type
2. If someone adds `PaymentCancelled` next week, the compiler says nothing. The `else` branch throws at runtime. In production. On a Friday.

Marcus: "The visitor pattern?"

Priya: "No. Sealed classes."

---

## Problem 1: The Redundant Cast

Java 16 introduced **pattern matching for instanceof**. The cast is gone:

```java
// Before (Java 11):
if (event instanceof PaymentReceived) {
    PaymentReceived e = (PaymentReceived) event;
    return "Received " + e.getAmount();
}

// After (Java 16+):
if (event instanceof PaymentReceived e) {
    return "Received " + e.amount();
}
```

The variable `e` is declared, typed, and scoped — all in one line. No cast. No separate declaration.

### The Test

```java
@Test
void patternMatching_shouldBindVariableInScope() {
    PaymentEvent event = new PaymentReceived("tx-1", new BigDecimal("50.00"), "USD");

    String result = "";
    if (event instanceof PaymentReceived e) {
        result = e.transactionId() + ": " + e.amount();
    }

    assertEquals("tx-1: 50.00", result);
}
```

The pattern variable `e` is only in scope inside the `if` block. Try to use it outside — compiler error.

---

## Problem 2: The Missing Branch

The real danger isn't the cast. It's the `else throw`. When someone adds a new event type, the compiler doesn't force them to handle it. You find out at runtime.

### Sealed Classes

A **sealed class** declares exactly which classes can extend it:

```java
public sealed interface PaymentEvent
    permits PaymentReceived, PaymentRefunded, PaymentDisputed, PaymentChargedBack {
}
```

`sealed` + `permits` = a closed set of subtypes. The compiler knows every possible case. If you miss one in a switch, it tells you.

Each subtype must be `final`, `sealed`, or `non-sealed`:

```java
public record PaymentReceived(
    String transactionId, BigDecimal amount, String currency
) implements PaymentEvent {}

public record PaymentRefunded(
    String transactionId, BigDecimal amount, String reason
) implements PaymentEvent {}

public record PaymentDisputed(
    String transactionId, String customerId
) implements PaymentEvent {}

public record PaymentChargedBack(
    String transactionId, BigDecimal amount
) implements PaymentEvent {}
```

Records are implicitly `final` — perfect for sealed hierarchies.

```
                    PaymentEvent (sealed)
                    ┌───────┼───────────────┐
                    │       │               │
              ┌─────┴──┐ ┌──┴────────┐ ┌───┴──────────┐
              │Received │ │Refunded   │ │Disputed      │
              │(record) │ │(record)   │ │(record)      │
              └────────┘ └───────────┘ └──────────────┘
                                              │
                                        ┌─────┴──────────┐
                                        │ChargedBack     │
                                        │(record)        │
                                        └────────────────┘

              All subtypes known at compile time.
              Miss one in a switch → compiler error.
```

---

## The Refactored Processor

Combine sealed classes + pattern matching + switch expressions:

```java
public String process(PaymentEvent event) {
    return switch (event) {
        case PaymentReceived e    -> "Received " + e.amount() + " " + e.currency();
        case PaymentRefunded e    -> "Refunded " + e.amount() + " reason: " + e.reason();
        case PaymentDisputed e    -> "Disputed by " + e.customerId();
        case PaymentChargedBack e -> "Chargeback " + e.amount();
    };
}
```

No `default`. No `else throw`. The compiler guarantees exhaustiveness — every subtype is handled. If someone adds `PaymentCancelled` to the `permits` list, every switch that doesn't handle it fails to compile.

### The Test

```java
@Test
void sealedSwitch_shouldHandleAllEventTypes() {
    assertAll(
        () -> assertEquals("Received 50.00 USD",
            process(new PaymentReceived("tx-1", new BigDecimal("50.00"), "USD"))),
        () -> assertEquals("Refunded 10.00 reason: duplicate",
            process(new PaymentRefunded("tx-2", new BigDecimal("10.00"), "duplicate"))),
        () -> assertEquals("Disputed by cust-42",
            process(new PaymentDisputed("tx-3", "cust-42"))),
        () -> assertEquals("Chargeback 25.00",
            process(new PaymentChargedBack("tx-4", new BigDecimal("25.00"))))
    );
}
```

### The Compile-Time Safety Test

Add a new event type:

```java
public record PaymentCancelled(String transactionId, String reason)
    implements PaymentEvent {}
```

Update the `permits` clause:

```java
public sealed interface PaymentEvent
    permits PaymentReceived, PaymentRefunded, PaymentDisputed,
            PaymentChargedBack, PaymentCancelled {}
```

Now every `switch (event)` without a `PaymentCancelled` case **fails to compile**:

```
error: the switch expression does not cover all possible input values
    return switch (event) {
           ^
```

This is the killer feature. The compiler is your safety net.

---

## Guarded Patterns

Sometimes you need to match a type AND a condition:

```java
public String classify(PaymentEvent event) {
    return switch (event) {
        case PaymentReceived e when e.amount().compareTo(new BigDecimal("10000")) > 0
            -> "HIGH_VALUE_RECEIPT";
        case PaymentReceived e
            -> "STANDARD_RECEIPT";
        case PaymentRefunded e when e.reason().equals("fraud")
            -> "FRAUD_REFUND";
        case PaymentRefunded e
            -> "STANDARD_REFUND";
        case PaymentDisputed e    -> "DISPUTE";
        case PaymentChargedBack e -> "CHARGEBACK";
    };
}
```

`when` is the guard. The more specific pattern goes first — Java evaluates top to bottom.

### The Test

```java
@Test
void guardedPattern_shouldMatchHighValueReceipt() {
    var highValue = new PaymentReceived("tx-1", new BigDecimal("50000"), "USD");
    var normal = new PaymentReceived("tx-2", new BigDecimal("25"), "USD");

    assertEquals("HIGH_VALUE_RECEIPT", classify(highValue));
    assertEquals("STANDARD_RECEIPT", classify(normal));
}

@Test
void guardedPattern_shouldMatchFraudRefund() {
    var fraud = new PaymentRefunded("tx-3", new BigDecimal("100"), "fraud");
    var normal = new PaymentRefunded("tx-4", new BigDecimal("100"), "customer_request");

    assertEquals("FRAUD_REFUND", classify(fraud));
    assertEquals("STANDARD_REFUND", classify(normal));
}
```

---

## Sealed Classes vs Enums

The Architect: "Why not just use an enum?"

| Feature | Enum | Sealed Class |
|---|---|---|
| Fixed set of values | ✓ | ✓ |
| Each value carries different data | ✗ | ✓ |
| Pattern matching in switch | ✓ (constants only) | ✓ (with destructuring) |
| Compile-time exhaustiveness | ✓ | ✓ |
| Subtypes can be records, classes | ✗ | ✓ |

Use enums when every variant has the same shape. Use sealed classes when each variant carries different data.

```java
// Enum: every status is just a name
enum PaymentStatus { PENDING, COMPLETED, FAILED }

// Sealed: each event has different fields
sealed interface PaymentEvent permits PaymentReceived, PaymentRefunded, ... {}
```

---

## Sealed Classes with Interfaces

Sealed works on interfaces too. A common pattern — define behavior per subtype:

```java
public sealed interface Notification permits EmailNotification, SmsNotification, PushNotification {
    String recipient();
    String body();
}

public record EmailNotification(String recipient, String subject, String body)
    implements Notification {}

public record SmsNotification(String recipient, String body)
    implements Notification {}

public record PushNotification(String recipient, String body, String deepLink)
    implements Notification {}
```

```java
public double estimateCost(Notification n) {
    return switch (n) {
        case EmailNotification e -> 0.001;
        case SmsNotification s   -> 0.05;
        case PushNotification p  -> 0.0;
    };
}
```

---

## non-sealed: The Escape Hatch

Sometimes one branch of the hierarchy needs to be open for extension:

```java
public sealed interface Shape permits Circle, Rectangle, Polygon {}

public record Circle(double radius) implements Shape {}
public record Rectangle(double width, double height) implements Shape {}

// Open for extension — anyone can subclass Polygon
public non-sealed abstract class Polygon implements Shape {
    abstract int sides();
}

public class Triangle extends Polygon {
    @Override public int sides() { return 3; }
}
```

`non-sealed` breaks the seal for that branch. Use it sparingly — you lose exhaustiveness guarantees for that subtree.

---

## The Visitor Pattern Is Dead

Before sealed classes, the visitor pattern was the only way to get compile-time exhaustiveness on a type hierarchy. Compare:

```java
// Old: Visitor pattern (Java 11)
interface PaymentEventVisitor<T> {
    T visit(PaymentReceived e);
    T visit(PaymentRefunded e);
    T visit(PaymentChargedBack e);
    // add new method for every new type
}

interface PaymentEvent {
    <T> T accept(PaymentEventVisitor<T> visitor);
}

class PaymentReceived implements PaymentEvent {
    public <T> T accept(PaymentEventVisitor<T> v) { return v.visit(this); }
}
// ... repeat for every subtype

// Usage:
event.accept(new PaymentEventVisitor<String>() {
    public String visit(PaymentReceived e) { return "received"; }
    public String visit(PaymentRefunded e) { return "refunded"; }
    public String visit(PaymentChargedBack e) { return "chargeback"; }
});
```

```java
// New: Sealed + switch (Java 21)
return switch (event) {
    case PaymentReceived e    -> "received";
    case PaymentRefunded e    -> "refunded";
    case PaymentChargedBack e -> "chargeback";
};
```

Same compile-time safety. A fraction of the code. The visitor pattern served us well. It can rest now.

---

## What You Learned

| Concept | One-liner |
|---|---|
| `instanceof` pattern matching | Check type + bind variable in one expression |
| `sealed` | Declares a closed set of subtypes |
| `permits` | Lists the allowed subtypes explicitly |
| `final` / `sealed` / `non-sealed` | Every subtype must pick one |
| Exhaustive switch | Compiler forces you to handle every subtype |
| Guarded patterns (`when`) | Match type + condition |
| Records + sealed | Algebraic data types in Java |
| Visitor pattern | Replaced by sealed + switch |

---

## The Foreshadow

The `instanceof` staircase is gone. But Marcus opens `FeeCalculator.java`:

```java
switch (transactionType) {
    case "DOMESTIC":
        fee = amount * 0.01;
        break;
    case "INTERNATIONAL":
        fee = amount * 0.03;
        // BUG: missing break — falls through to CRYPTO
    case "CRYPTO":
        fee = amount * 0.05;
        break;
    default:
        fee = 0;
        // silently returns 0 for unknown types
}
```

A fall-through bug that's been in production for 8 months. International transactions have been charged crypto fees. Nobody noticed because the tests only check domestic.

That's **switch expressions**.

---

[← Chapter 1: The DTO Graveyard](chapter-01-records.md) | [Chapter 3: The Switch From Hell →](chapter-03-switch-expressions.md)

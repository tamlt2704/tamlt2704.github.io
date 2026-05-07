# Chapter 3: The Switch From Hell

[← Chapter 2: The instanceof Staircase](chapter-02-sealed-classes.md) | [Chapter 4: The String Butcher →](chapter-04-text-blocks.md)

---

## The Incident

Marcus finds the bug during a routine audit. International transactions have been charged 5% (crypto fee) instead of 3% for **eight months**. The culprit:

```java
double fee;
switch (transactionType) {
    case "DOMESTIC":
        fee = amount * 0.01;
        break;
    case "INTERNATIONAL":
        fee = amount * 0.03;
        // missing break
    case "CRYPTO":
        fee = amount * 0.05;
        break;
    default:
        fee = 0;
}
```

Fall-through. The oldest trap in C-family languages. `INTERNATIONAL` computes 0.03, then falls into `CRYPTO` and overwrites it with 0.05. No warning. No error. Just wrong money.

Compliance Carl: "How much did we overcharge?"

Marcus: "$47,000."

Compliance Carl: "..."

---

## Switch Expressions: No More Fall-Through

Java 14 introduced **switch expressions** with arrow syntax. No `break`. No fall-through. The switch returns a value:

```java
double fee = switch (transactionType) {
    case "DOMESTIC"      -> amount * 0.01;
    case "INTERNATIONAL" -> amount * 0.03;
    case "CRYPTO"        -> amount * 0.05;
    default              -> throw new IllegalArgumentException("Unknown: " + transactionType);
};
```

Arrow `->` means: execute the right side, return the value, done. No fall-through possible.

### The Test

```java
@Test
void switchExpression_shouldNotFallThrough() {
    double amount = 1000.0;

    double domestic      = calculateFee("DOMESTIC", amount);
    double international = calculateFee("INTERNATIONAL", amount);
    double crypto        = calculateFee("CRYPTO", amount);

    assertEquals(10.0, domestic);
    assertEquals(30.0, international);  // was 50.0 with the old bug
    assertEquals(50.0, crypto);
}

@Test
void switchExpression_shouldRejectUnknownType() {
    assertThatThrownBy(() -> calculateFee("BARTER", 100.0))
        .isInstanceOf(IllegalArgumentException.class);
}
```

---

## Switch Expressions Return Values

The old switch was a statement — it didn't return anything. You had to declare a variable before it and assign inside each branch. The new switch is an expression — it evaluates to a value:

```java
// Statement (old) — variable declared outside, assigned inside
String label;
switch (status) {
    case "P": label = "Pending"; break;
    case "C": label = "Completed"; break;
    default:  label = "Unknown"; break;
}

// Expression (new) — the switch IS the value
String label = switch (status) {
    case "P" -> "Pending";
    case "C" -> "Completed";
    default  -> "Unknown";
};  // ← semicolon: it's an assignment statement
```

---

## Multiple Labels Per Case

Group cases that share the same result:

```java
String category = switch (transactionType) {
    case "DOMESTIC", "INTERNATIONAL" -> "FIAT";
    case "CRYPTO", "STABLECOIN"      -> "DIGITAL";
    default -> "OTHER";
};
```

### The Test

```java
@Test
void multipleLabels_shouldGroupCases() {
    assertEquals("FIAT", categorize("DOMESTIC"));
    assertEquals("FIAT", categorize("INTERNATIONAL"));
    assertEquals("DIGITAL", categorize("CRYPTO"));
    assertEquals("DIGITAL", categorize("STABLECOIN"));
}
```

---

## yield: Multi-Line Cases

When a case needs more than one line, use a block and `yield`:

```java
String summary = switch (event) {
    case PaymentReceived e -> "Received " + e.amount();
    case PaymentRefunded e -> {
        log.info("Processing refund for {}", e.transactionId());
        var formatted = NumberFormat.getCurrencyInstance().format(e.amount());
        yield "Refunded " + formatted + " — reason: " + e.reason();
    }
    case PaymentDisputed e    -> "Disputed by " + e.customerId();
    case PaymentChargedBack e -> "Chargeback " + e.amount();
};
```

`yield` is the `return` of a switch block. It exits the block and provides the value.

### The Test

```java
@Test
void yield_shouldReturnFromMultiLineBlock() {
    var refund = new PaymentRefunded("tx-1", new BigDecimal("99.99"), "duplicate");

    String result = summarize(refund);

    assertThat(result).contains("Refunded").contains("$99.99").contains("duplicate");
}
```

---

## Pattern Matching in Switch

Combine sealed classes (Chapter 2) with switch expressions for the full power:

```java
public BigDecimal calculateProcessingFee(PaymentEvent event) {
    return switch (event) {
        case PaymentReceived e when e.amount().compareTo(new BigDecimal("10000")) > 0
            -> e.amount().multiply(new BigDecimal("0.005"));  // 0.5% for high value
        case PaymentReceived e
            -> e.amount().multiply(new BigDecimal("0.01"));   // 1% standard
        case PaymentRefunded e
            -> e.amount().multiply(new BigDecimal("0.02"));   // 2% refund fee
        case PaymentDisputed _
            -> new BigDecimal("25.00");                       // flat $25
        case PaymentChargedBack _
            -> new BigDecimal("50.00");                       // flat $50
    };
}
```

Notice `_` — the unnamed variable (Java 22+). When you don't need the bound variable, use `_` to signal intent.

### The Test

```java
@Test
void patternMatchingSwitch_shouldApplyCorrectFees() {
    assertEquals(new BigDecimal("50.00"),
        calculateProcessingFee(new PaymentReceived("tx-1", new BigDecimal("5000"), "USD")));

    assertEquals(new BigDecimal("50.00"),
        calculateProcessingFee(new PaymentReceived("tx-2", new BigDecimal("50000"), "USD"))
            .stripTrailingZeros());  // 50000 * 0.005 = 250? No — 0.5% of 50000 = 250

    assertEquals(new BigDecimal("25.00"),
        calculateProcessingFee(new PaymentDisputed("tx-3", "cust-1")));
}
```

---

## null in Switch

Before Java 21, passing `null` to a switch threw `NullPointerException` before any case was evaluated. Now you can handle it:

```java
String describe(String status) {
    return switch (status) {
        case "ACTIVE"   -> "Active";
        case "INACTIVE" -> "Inactive";
        case null        -> "No status provided";
        default          -> "Unknown: " + status;
    };
}
```

### The Test

```java
@Test
void nullInSwitch_shouldBeHandledExplicitly() {
    assertEquals("No status provided", describe(null));
    assertEquals("Active", describe("ACTIVE"));
    assertEquals("Unknown: BANANA", describe("BANANA"));
}
```

No more wrapping every switch in `if (x != null)`.

---

## Enum Switch Exhaustiveness

When switching on an enum, the compiler enforces exhaustiveness — no `default` needed:

```java
enum PaymentStatus { PENDING, COMPLETED, FAILED, CANCELLED }

String icon(PaymentStatus status) {
    return switch (status) {
        case PENDING   -> "⏳";
        case COMPLETED -> "✅";
        case FAILED    -> "❌";
        case CANCELLED -> "🚫";
    };
}
```

Add `REFUNDED` to the enum → every switch without it fails to compile. Same safety as sealed classes.

---

## Old Switch vs New Switch

```
Old switch (statement):              New switch (expression):

┌─────────────────────────┐          ┌─────────────────────────┐
│ Fall-through by default │          │ No fall-through          │
│ Must use break          │          │ Arrow → returns value    │
│ Doesn't return a value  │          │ IS the value             │
│ default is optional     │          │ Exhaustiveness enforced  │
│ null → NPE              │          │ null is a valid case     │
│ Constants only           │          │ Patterns + guards        │
└─────────────────────────┘          └─────────────────────────┘
```

---

## What You Learned

| Concept | One-liner |
|---|---|
| Switch expression | Switch that returns a value — no fall-through |
| Arrow syntax `->` | Execute right side, return, done |
| `yield` | Return from a multi-line switch block |
| Multiple labels | `case "A", "B" ->` groups cases |
| Pattern matching | `case PaymentReceived e ->` binds type + variable |
| Guarded patterns | `case X when condition ->` adds a filter |
| `null` case | Handle null explicitly instead of NPE |
| Exhaustiveness | Compiler forces all cases for sealed/enum types |
| Unnamed variable `_` | Signal that you don't need the bound variable |

---

## The Foreshadow

The fee calculator is fixed. But Marcus opens `EmailTemplateBuilder.java`:

```java
String body = "Dear " + customer.getName() + ",\n\n"
    + "Your payment of " + amount + " " + currency + " has been processed.\n"
    + "Transaction ID: " + txId + "\n"
    + "Date: " + date.format(DateTimeFormatter.ISO_LOCAL_DATE) + "\n\n"
    + "If you have questions, contact support@finpulse.com.\n\n"
    + "Best regards,\n"
    + "The FinPulse Team";
```

Seven string concatenations. Escaped newlines. Unreadable. And the SQL query builder is worse — 40 lines of `StringBuilder.append()`.

That's **text blocks**.

---

[← Chapter 2: The instanceof Staircase](chapter-02-sealed-classes.md) | [Chapter 4: The String Butcher →](chapter-04-text-blocks.md)

# Chapter 1: The DTO Graveyard

[README](README.md) | [Chapter 2: The instanceof Staircase →](chapter-02-sealed-classes.md)

---

## The Incident

Your first refactoring ticket. Priya assigns it with one line:

> "The `dto/` package has 47 classes. Each one is 80 lines of getters, setters, equals, hashCode, and toString. Kill them."

You open `PaymentResponse.java`. 94 lines:

```java
public class PaymentResponse {
    private final String transactionId;
    private final BigDecimal amount;
    private final String currency;
    private final String status;
    private final Instant processedAt;

    public PaymentResponse(String transactionId, BigDecimal amount,
                           String currency, String status, Instant processedAt) {
        this.transactionId = transactionId;
        this.amount = amount;
        this.currency = currency;
        this.status = status;
        this.processedAt = processedAt;
    }

    public String getTransactionId() { return transactionId; }
    public BigDecimal getAmount() { return amount; }
    public String getCurrency() { return currency; }
    public String getStatus() { return status; }
    public Instant getProcessedAt() { return processedAt; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        PaymentResponse that = (PaymentResponse) o;
        return Objects.equals(transactionId, that.transactionId)
            && Objects.equals(amount, that.amount)
            && Objects.equals(currency, that.currency)
            && Objects.equals(status, that.status)
            && Objects.equals(processedAt, that.processedAt);
    }

    @Override
    public int hashCode() {
        return Objects.hash(transactionId, amount, currency, status, processedAt);
    }

    @Override
    public String toString() {
        return "PaymentResponse{" +
            "transactionId='" + transactionId + '\'' +
            ", amount=" + amount +
            ", currency='" + currency + '\'' +
            ", status='" + status + '\'' +
            ", processedAt=" + processedAt +
            '}';
    }
}
```

94 lines. Zero logic. Pure ceremony. And there are 46 more like it.

Marcus: "Lombok?"

Priya: "No. Java has records now. Use them."

---

## Records: The One-Liner

```java
public record PaymentResponse(
    String transactionId,
    BigDecimal amount,
    String currency,
    String status,
    Instant processedAt
) {}
```

That's it. 6 lines. The compiler generates:
- A constructor with all fields
- `transactionId()`, `amount()`, `currency()`, `status()`, `processedAt()` — accessor methods (no `get` prefix)
- `equals()` based on all fields
- `hashCode()` based on all fields
- `toString()` with all fields

```
94 lines → 6 lines. Same behavior. Zero Lombok.
```

### The Test

```java
@Test
void record_shouldGenerateEqualsHashCodeToString() {
    var a = new PaymentResponse("tx-1", new BigDecimal("99.99"), "USD", "SUCCESS", Instant.now());
    var b = new PaymentResponse("tx-1", new BigDecimal("99.99"), "USD", "SUCCESS", a.processedAt());

    assertEquals(a, b);
    assertEquals(a.hashCode(), b.hashCode());
    assertThat(a.toString()).contains("tx-1", "99.99", "USD");
}

@Test
void record_accessors_haveNoGetPrefix() {
    var r = new PaymentResponse("tx-1", BigDecimal.TEN, "EUR", "PENDING", Instant.now());

    assertEquals("tx-1", r.transactionId());  // not getTransactionId()
    assertEquals("EUR", r.currency());         // not getCurrency()
}
```

---

## Compact Constructors: Validation

Compliance Carl walks by. "Can you prove that `amount` is never negative?"

You can. Records support **compact constructors** — validation logic without repeating the parameter list:

```java
public record PaymentResponse(
    String transactionId,
    BigDecimal amount,
    String currency,
    String status,
    Instant processedAt
) {
    public PaymentResponse {
        Objects.requireNonNull(transactionId, "transactionId must not be null");
        Objects.requireNonNull(currency, "currency must not be null");
        if (amount.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("amount must not be negative");
        }
    }
}
```

No `this.x = x;` — the compiler adds the assignments after your validation code runs.

### The Test

```java
@Test
void compactConstructor_shouldRejectNegativeAmount() {
    assertThatThrownBy(() ->
        new PaymentResponse("tx-1", new BigDecimal("-5.00"), "USD", "FAIL", Instant.now()))
        .isInstanceOf(IllegalArgumentException.class)
        .hasMessageContaining("negative");
}

@Test
void compactConstructor_shouldRejectNullTransactionId() {
    assertThatThrownBy(() ->
        new PaymentResponse(null, BigDecimal.ONE, "USD", "OK", Instant.now()))
        .isInstanceOf(NullPointerException.class);
}
```

Compliance Carl nods. "Immutable and validated at construction. I like it."

---

## Records Are Immutable

Records are `final`. Fields are `final`. No setters. No subclassing.

```java
// This does NOT compile:
public record PaymentResponse(...) {
    public void setAmount(BigDecimal a) { this.amount = a; } // ❌ cannot assign final field
}

// This does NOT compile:
public class SpecialPayment extends PaymentResponse { } // ❌ cannot extend record
```

```
Record guarantees:
┌──────────────────────────────────────┐
│ ✓ Immutable — fields are final       │
│ ✓ Final — cannot be subclassed       │
│ ✓ Transparent — all fields in header │
│ ✓ Value-based equality               │
└──────────────────────────────────────┘
```

---

## Records with Custom Methods

Records aren't just dumb data carriers. You can add methods:

```java
public record Money(BigDecimal amount, String currency) {

    public Money {
        Objects.requireNonNull(amount);
        Objects.requireNonNull(currency);
    }

    public Money add(Money other) {
        if (!this.currency.equals(other.currency)) {
            throw new IllegalArgumentException("Currency mismatch: " + currency + " vs " + other.currency);
        }
        return new Money(this.amount.add(other.amount), this.currency);
    }

    public boolean isPositive() {
        return amount.compareTo(BigDecimal.ZERO) > 0;
    }
}
```

### The Test

```java
@Test
void record_canHaveCustomMethods() {
    var a = new Money(new BigDecimal("10.00"), "USD");
    var b = new Money(new BigDecimal("5.50"), "USD");

    var sum = a.add(b);

    assertEquals(new BigDecimal("15.50"), sum.amount());
    assertEquals("USD", sum.currency());
}

@Test
void record_shouldRejectCurrencyMismatch() {
    var usd = new Money(BigDecimal.TEN, "USD");
    var eur = new Money(BigDecimal.ONE, "EUR");

    assertThatThrownBy(() -> usd.add(eur))
        .isInstanceOf(IllegalArgumentException.class)
        .hasMessageContaining("mismatch");
}
```

---

## Records as Map Keys

Because records generate proper `equals()` and `hashCode()`, they work perfectly as map keys — something that old DTOs with hand-written (or forgotten) equals/hashCode often got wrong.

```java
public record CacheKey(String userId, String region) {}
```

```java
@Test
void record_asMapKey_shouldWorkCorrectly() {
    Map<CacheKey, String> cache = new HashMap<>();
    cache.put(new CacheKey("user-1", "us-east"), "cached-data");

    // Different object, same values → same key
    String result = cache.get(new CacheKey("user-1", "us-east"));
    assertEquals("cached-data", result);
}
```

With the old DTO, if you forgot to override `equals()`, this returns `null`. With records, it just works.

---

## Records with Jackson (Spring Boot)

Marcus: "Do records work with `@RestController`?"

Yes. Jackson supports records out of the box since Spring Boot 3:

```java
@RestController
@RequestMapping("/payments")
public class PaymentController {

    @PostMapping
    public PaymentResponse process(@RequestBody PaymentRequest request) {
        return new PaymentResponse(
            UUID.randomUUID().toString(),
            request.amount(),
            request.currency(),
            "SUCCESS",
            Instant.now()
        );
    }
}

public record PaymentRequest(BigDecimal amount, String currency) {}
```

```bash
curl -X POST http://localhost:8080/payments \
  -H "Content-Type: application/json" \
  -d '{"amount": 42.50, "currency": "USD"}'
# → {"transactionId":"a1b2c3","amount":42.50,"currency":"USD","status":"SUCCESS",...}
```

No `@JsonProperty`. No `@JsonCreator`. It just works.

---

## When NOT to Use Records

The Architect raises a finger. "Records aren't for everything."

| Use Records For | Don't Use Records For |
|---|---|
| DTOs / API responses | JPA entities (need mutable state, no-arg constructor) |
| Value objects (Money, Address) | Classes with complex mutable state |
| Map keys / cache keys | Classes that need inheritance |
| Configuration snapshots | Anything that needs setters |
| Event payloads | Spring beans (`@Service`, `@Component`) |

```java
// ❌ JPA entity — needs no-arg constructor, mutable fields
@Entity
public record User(String id, String name) {} // won't work

// ✓ DTO returned from the entity
public record UserResponse(String id, String name) {} // perfect
```

---

## Local Records

You can declare records inside methods. Useful for intermediate transformations:

```java
public List<String> summarizePayments(List<Payment> payments) {
    record Summary(String currency, BigDecimal total, long count) {}

    return payments.stream()
        .collect(Collectors.groupingBy(Payment::getCurrency))
        .entrySet().stream()
        .map(e -> new Summary(
            e.getKey(),
            e.getValue().stream().map(Payment::getAmount).reduce(BigDecimal.ZERO, BigDecimal::add),
            e.getValue().size()))
        .map(s -> s.currency() + ": " + s.total() + " (" + s.count() + " txns)")
        .toList();
}
```

No need to pollute the package with a one-off class.

---

## The Refactoring Scorecard

```
Before                          After
────────────────────────────    ────────────────────────────
47 DTO classes                  47 records
~4,000 lines of boilerplate     ~300 lines total
Hand-written equals/hashCode    Compiler-generated
Lombok dependency               Zero dependencies
Mutable (setters everywhere)    Immutable by default
No validation                   Compact constructors
```

Priya reviews the PR. One comment: "Nice."

That's the highest praise she gives.

---

## What You Learned

| Concept | One-liner |
|---|---|
| `record` | Immutable data class — constructor, accessors, equals, hashCode, toString for free |
| Compact constructor | Validation without repeating the parameter list |
| No `get` prefix | `r.amount()` not `r.getAmount()` |
| Immutable + final | No setters, no subclassing |
| Custom methods | Records can have behavior, just no mutable state |
| Local records | Declare inside a method for one-off transformations |
| Jackson support | Works out of the box with Spring Boot 3 |

---

## The Foreshadow

47 DTOs down. But Priya opens `PaymentProcessor.java` and sighs:

```java
if (event instanceof PaymentReceived) {
    PaymentReceived pr = (PaymentReceived) event;
    // ...
} else if (event instanceof PaymentRefunded) {
    PaymentRefunded pr = (PaymentRefunded) event;
    // ...
} else if (event instanceof PaymentDisputed) {
    // ...
} else if (event instanceof PaymentChargedBack) {
    // ...
}
// 14 more branches
```

> "This `instanceof` staircase is 200 lines. And every time we add a new event type, someone forgets to add a branch. The compiler doesn't warn us."

That's **sealed classes** and **pattern matching**.

---

[README](README.md) | [Chapter 2: The instanceof Staircase →](chapter-02-sealed-classes.md)

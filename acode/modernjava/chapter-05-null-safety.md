# Chapter 5: The Null Minefield

[← Chapter 4: The String Butcher](chapter-04-text-blocks.md) | [Chapter 6: The Thread Avalanche →](chapter-06-virtual-threads.md)

---

## The Incident

Friday. 4:58 PM. Jenkins goes red:

```
java.lang.NullPointerException
    at com.finpulse.service.PaymentService.process(PaymentService.java:47)
```

Line 47:

```java
String city = payment.getCustomer().getAddress().getCity().toUpperCase();
```

Which one is null? `payment`? `getCustomer()`? `getAddress()`? `getCity()`? The stack trace doesn't say. You add breakpoints. You add print statements. 20 minutes later: `getAddress()` returned null.

Marcus: "Why doesn't Java just tell us which one?"

Priya: "It does now. Since Java 14."

---

## Helpful NullPointerExceptions

Java 14+ tells you exactly which call returned null:

```
java.lang.NullPointerException:
    Cannot invoke "Address.getCity()" because the return value of
    "Customer.getAddress()" is null
```

No configuration needed. Just run on Java 14+. The JVM analyzes the bytecode and tells you the exact null reference.

### The Test

```java
@Test
void helpfulNpe_shouldIdentifyNullReference() {
    var customer = new Customer("Alice", null); // no address
    var payment = new Payment("tx-1", customer, BigDecimal.TEN);

    var ex = assertThrows(NullPointerException.class, () ->
        payment.getCustomer().getAddress().getCity());

    assertThat(ex.getMessage()).contains("getAddress()");
}
```

This is free. But it's a band-aid. The real fix is not having nulls in the first place.

---

## The Null Chain Problem

The legacy code is full of this:

```java
// Defensive null checks — the pyramid of doom
String city = "Unknown";
if (payment != null) {
    if (payment.getCustomer() != null) {
        if (payment.getCustomer().getAddress() != null) {
            if (payment.getCustomer().getAddress().getCity() != null) {
                city = payment.getCustomer().getAddress().getCity().toUpperCase();
            }
        }
    }
}
```

12 lines to safely get a city name. And someone will forget a level.

---

## Optional: The Right Way

`Optional` isn't a replacement for null checks. It's a signal: **this value might not exist, and you must handle that explicitly**.

```java
public Optional<String> getCity(Payment payment) {
    return Optional.ofNullable(payment)
        .map(Payment::getCustomer)
        .map(Customer::getAddress)
        .map(Address::getCity)
        .map(String::toUpperCase);
}
```

### The Test

```java
@Test
void optional_shouldChainSafely() {
    var payment = new Payment("tx-1",
        new Customer("Alice", new Address("123 Main", "Springfield")),
        BigDecimal.TEN);

    Optional<String> city = getCity(payment);

    assertEquals("SPRINGFIELD", city.orElse("Unknown"));
}

@Test
void optional_shouldReturnEmptyForNullAddress() {
    var payment = new Payment("tx-1", new Customer("Alice", null), BigDecimal.TEN);

    Optional<String> city = getCity(payment);

    assertTrue(city.isEmpty());
    assertEquals("Unknown", city.orElse("Unknown"));
}
```

---

## Optional Anti-Patterns

The Architect reviews Marcus's PR and sighs:

```java
// ❌ Anti-pattern 1: Optional as a field
public class Customer {
    private Optional<Address> address; // NO — use nullable field + Optional return
}

// ❌ Anti-pattern 2: Optional as a parameter
public void process(Optional<String> name) { } // NO — just use @Nullable or overload

// ❌ Anti-pattern 3: isPresent + get
if (result.isPresent()) {
    doSomething(result.get()); // NO — use ifPresent, map, or orElse
}

// ❌ Anti-pattern 4: Optional.of(null)
Optional.of(null); // throws NPE — use Optional.ofNullable()
```

The rules:

| Do | Don't |
|---|---|
| Return `Optional` from methods | Use `Optional` as a field type |
| Use `map`, `flatMap`, `orElse` | Use `isPresent()` + `get()` |
| Use `Optional.ofNullable()` | Use `Optional.of()` with possibly-null values |
| Use `Optional` for "might not exist" | Use `Optional` as a method parameter |

---

## Optional Methods You Should Know

```java
Optional<String> name = findCustomerName(id);

// orElse — default value (always evaluated)
String result = name.orElse("Anonymous");

// orElseGet — lazy default (only evaluated if empty)
String result = name.orElseGet(() -> lookupDefault(id));

// orElseThrow — fail fast
String result = name.orElseThrow(() -> new CustomerNotFoundException(id));

// ifPresent — side effect
name.ifPresent(n -> log.info("Found customer: {}", n));

// ifPresentOrElse — handle both cases
name.ifPresentOrElse(
    n -> log.info("Found: {}", n),
    () -> log.warn("Customer {} not found", id)
);

// map — transform if present
Optional<String> upper = name.map(String::toUpperCase);

// flatMap — when the transform also returns Optional
Optional<Address> addr = findCustomer(id).flatMap(Customer::getAddress);

// or — alternative Optional (Java 9+)
Optional<String> result = findInCache(id).or(() -> findInDb(id));

// stream — bridge to Stream API (Java 9+)
List<String> names = ids.stream()
    .map(this::findCustomerName)
    .flatMap(Optional::stream)  // filters out empties
    .toList();
```

---

## Records as Non-Null Value Objects

The best null defense: make nulls impossible at construction time.

```java
public record Address(String street, String city) {
    public Address {
        Objects.requireNonNull(street, "street must not be null");
        Objects.requireNonNull(city, "city must not be null");
    }
}

public record Customer(String name, Address address) {
    public Customer {
        Objects.requireNonNull(name, "name must not be null");
        // address CAN be null — it's optional
    }

    public Optional<Address> address() {
        return Optional.ofNullable(address);
    }
}
```

Now `Address` can never have null fields. `Customer` explicitly models that address is optional via the return type.

### The Test

```java
@Test
void record_shouldRejectNullFields() {
    assertThatThrownBy(() -> new Address(null, "Springfield"))
        .isInstanceOf(NullPointerException.class)
        .hasMessageContaining("street");
}

@Test
void record_shouldReturnOptionalForNullableField() {
    var customer = new Customer("Alice", null);

    assertTrue(customer.address().isEmpty());
    assertEquals("Unknown", customer.address().map(Address::city).orElse("Unknown"));
}
```

---

## Objects.requireNonNull: Fail Fast

Don't let nulls travel deep into your code. Catch them at the boundary:

```java
public class PaymentService {

    public PaymentResponse process(PaymentRequest request) {
        Objects.requireNonNull(request, "request must not be null");
        Objects.requireNonNull(request.currency(), "currency must not be null");

        // by this point, nothing is null — no defensive checks needed
        return doProcess(request);
    }
}
```

Fail at the front door, not in the basement.

---

## The Refactoring Pattern

```
Legacy code:                          Modern code:

null everywhere                       Records with requireNonNull
→ defensive if-null pyramids          → Optional return types
→ NPE in production                   → Helpful NPE messages
→ 20 min debugging                    → map/flatMap chains
                                      → Fail fast at boundaries
```

---

## What You Learned

| Concept | One-liner |
|---|---|
| Helpful NPEs | Java 14+ tells you exactly which reference was null |
| `Optional.map/flatMap` | Chain safely through nullable values |
| `orElse` / `orElseGet` / `orElseThrow` | Three ways to unwrap an Optional |
| `Optional::stream` | Bridge Optional to Stream — filters empties |
| `Optional.or()` | Fallback to another Optional |
| `Objects.requireNonNull` | Fail fast at method boundaries |
| Records + compact constructors | Make nulls impossible at construction |
| Optional as return type | Signal "might not exist" in the API |

---

## The Foreshadow

The null minefield is cleared. But the performance team sends an alert:

```
ALERT: OOM — heap exhausted
Active threads: 12,847
Thread stack memory: ~12 GB
```

The payment notification service spawns a platform thread per request. Black Friday traffic hit 10,000 concurrent requests. Each thread costs ~1MB of stack. The JVM ran out of memory.

Marcus: "Can we just... make threads cheaper?"

Priya: "Java 21. Virtual threads."

---

[← Chapter 4: The String Butcher](chapter-04-text-blocks.md) | [Chapter 6: The Thread Avalanche →](chapter-06-virtual-threads.md)

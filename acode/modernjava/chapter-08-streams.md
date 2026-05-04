# Chapter 8: The Stream Spaghetti

[← Chapter 7: The Collection Ceremony](chapter-07-collections.md) | [README](README.md)

---

## The Incident

Marcus wrote a stream pipeline. Nobody can read it. Including Marcus, two days later.

```java
var result = transactions.stream()
    .filter(t -> t.status() == Status.COMPLETED)
    .filter(t -> t.amount().compareTo(BigDecimal.ZERO) > 0)
    .collect(Collectors.groupingBy(
        Transaction::currency,
        Collectors.collectingAndThen(
            Collectors.toList(),
            list -> list.stream()
                .map(Transaction::amount)
                .reduce(BigDecimal.ZERO, BigDecimal::add))));
```

Priya: "What does this do?"

Marcus: "It... groups completed transactions by currency and sums the amounts."

Priya: "Then write that."

---

## Collectors.teeing: Two Results, One Pass

`teeing` runs two collectors in parallel on the same stream and merges the results:

```java
record TransactionSummary(BigDecimal total, long count) {}

TransactionSummary summary = transactions.stream()
    .filter(t -> t.status() == Status.COMPLETED)
    .collect(Collectors.teeing(
        Collectors.reducing(BigDecimal.ZERO, Transaction::amount, BigDecimal::add),
        Collectors.counting(),
        TransactionSummary::new
    ));
```

One pass through the data. Two results. Merged into a record.

### The Test

```java
@Test
void teeing_shouldComputeTotalAndCount() {
    var txns = List.of(
        new Transaction("tx-1", new BigDecimal("100"), "USD", Status.COMPLETED),
        new Transaction("tx-2", new BigDecimal("200"), "USD", Status.COMPLETED),
        new Transaction("tx-3", new BigDecimal("50"), "USD", Status.FAILED)
    );

    var summary = txns.stream()
        .filter(t -> t.status() == Status.COMPLETED)
        .collect(Collectors.teeing(
            Collectors.reducing(BigDecimal.ZERO, Transaction::amount, BigDecimal::add),
            Collectors.counting(),
            TransactionSummary::new
        ));

    assertEquals(new BigDecimal("300"), summary.total());
    assertEquals(2, summary.count());
}
```

---

## mapMulti: One-to-Many Without flatMap

`flatMap` creates an intermediate stream for every element. `mapMulti` avoids that overhead — you push results directly into the downstream:

```java
// flatMap: creates a stream per element
transactions.stream()
    .flatMap(t -> t.lineItems().stream())
    .toList();

// mapMulti: pushes directly, no intermediate stream
transactions.stream()
    .<LineItem>mapMulti((t, consumer) -> {
        for (LineItem item : t.lineItems()) {
            consumer.accept(item);
        }
    })
    .toList();
```

When to prefer `mapMulti`:
- The mapping produces 0 or 1 elements (conditional expansion)
- You want to avoid creating intermediate streams
- The logic is imperative (loops, conditions)

### The Test

```java
@Test
void mapMulti_shouldExpandConditionally() {
    var numbers = List.of(1, 2, 3, 4, 5);

    // Only emit even numbers, doubled
    List<Integer> result = numbers.stream()
        .<Integer>mapMulti((n, consumer) -> {
            if (n % 2 == 0) {
                consumer.accept(n * 2);
            }
        })
        .toList();

    assertEquals(List.of(4, 8), result);
}
```

---

## takeWhile and dropWhile

Process elements until a condition changes:

```java
// takeWhile: take elements while the predicate is true, stop at first false
var sorted = List.of(1, 2, 3, 10, 20, 30);
var small = sorted.stream().takeWhile(n -> n < 10).toList();
// → [1, 2, 3]

// dropWhile: skip elements while the predicate is true, take the rest
var large = sorted.stream().dropWhile(n -> n < 10).toList();
// → [10, 20, 30]
```

These work best on **ordered** streams. On unordered streams, the behavior is non-deterministic.

### The Test

```java
@Test
void takeWhile_shouldStopAtFirstFalse() {
    var transactions = List.of(
        new Transaction("tx-1", new BigDecimal("10"), "USD", Status.COMPLETED),
        new Transaction("tx-2", new BigDecimal("20"), "USD", Status.COMPLETED),
        new Transaction("tx-3", new BigDecimal("500"), "USD", Status.COMPLETED),
        new Transaction("tx-4", new BigDecimal("5"), "USD", Status.COMPLETED)
    );

    // Take transactions while amount < 100 (sorted by amount)
    var small = transactions.stream()
        .takeWhile(t -> t.amount().compareTo(new BigDecimal("100")) < 0)
        .toList();

    assertEquals(2, small.size()); // tx-1 and tx-2 only
}
```

---

## Gatherers (Preview — Java 22+)

Gatherers are the stream equivalent of custom collectors, but for **intermediate operations**. They let you write custom stateful transformations that plug into the stream pipeline.

```java
// Built-in gatherer: windowFixed — groups elements into fixed-size windows
List<List<Integer>> windows = Stream.of(1, 2, 3, 4, 5, 6, 7)
    .gather(Gatherers.windowFixed(3))
    .toList();
// → [[1, 2, 3], [4, 5, 6], [7]]
```

```java
// windowSliding — sliding window
List<List<Integer>> sliding = Stream.of(1, 2, 3, 4, 5)
    .gather(Gatherers.windowSliding(3))
    .toList();
// → [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
```

### The Test

```java
@Test
void gatherer_windowFixed_shouldGroupIntoChunks() {
    var windows = Stream.of(1, 2, 3, 4, 5, 6, 7)
        .gather(Gatherers.windowFixed(3))
        .toList();

    assertEquals(3, windows.size());
    assertEquals(List.of(1, 2, 3), windows.get(0));
    assertEquals(List.of(4, 5, 6), windows.get(1));
    assertEquals(List.of(7), windows.get(2));
}

@Test
void gatherer_windowSliding_shouldCreateOverlappingWindows() {
    var windows = Stream.of("A", "B", "C", "D")
        .gather(Gatherers.windowSliding(2))
        .toList();

    assertEquals(List.of(List.of("A", "B"), List.of("B", "C"), List.of("C", "D")), windows);
}
```

### Built-in Gatherers

| Gatherer | What It Does |
|---|---|
| `windowFixed(n)` | Non-overlapping chunks of size n |
| `windowSliding(n)` | Sliding window of size n |
| `fold(init, fn)` | Running accumulation (like reduce but intermediate) |
| `scan(init, fn)` | Emit every intermediate accumulation result |
| `mapConcurrent(n, fn)` | Map with bounded concurrency (virtual threads) |

`mapConcurrent` is particularly powerful — it runs the mapping function on virtual threads with a concurrency limit:

```java
// Fetch prices concurrently, max 5 at a time
List<Price> prices = products.stream()
    .gather(Gatherers.mapConcurrent(5, product -> fetchPrice(product)))
    .toList();
```

---

## The Refactored Analyzer

Marcus's unreadable pipeline, cleaned up:

```java
// Before: nested collectingAndThen, stream-inside-stream
var result = transactions.stream()
    .filter(t -> t.status() == Status.COMPLETED)
    .filter(t -> t.amount().compareTo(BigDecimal.ZERO) > 0)
    .collect(Collectors.groupingBy(
        Transaction::currency,
        Collectors.collectingAndThen(
            Collectors.toList(),
            list -> list.stream()
                .map(Transaction::amount)
                .reduce(BigDecimal.ZERO, BigDecimal::add))));

// After: groupingBy + reducing
Map<String, BigDecimal> totals = transactions.stream()
    .filter(t -> t.status() == Status.COMPLETED)
    .filter(t -> t.amount().compareTo(BigDecimal.ZERO) > 0)
    .collect(Collectors.groupingBy(
        Transaction::currency,
        Collectors.reducing(BigDecimal.ZERO, Transaction::amount, BigDecimal::add)
    ));
```

The `collectingAndThen` + inner stream was doing what `reducing` does in one step.

### The Test

```java
@Test
void groupingByWithReducing_shouldSumByCurrency() {
    var txns = List.of(
        new Transaction("tx-1", new BigDecimal("100"), "USD", Status.COMPLETED),
        new Transaction("tx-2", new BigDecimal("200"), "USD", Status.COMPLETED),
        new Transaction("tx-3", new BigDecimal("150"), "EUR", Status.COMPLETED),
        new Transaction("tx-4", new BigDecimal("50"), "EUR", Status.FAILED)
    );

    Map<String, BigDecimal> totals = txns.stream()
        .filter(t -> t.status() == Status.COMPLETED)
        .collect(Collectors.groupingBy(
            Transaction::currency,
            Collectors.reducing(BigDecimal.ZERO, Transaction::amount, BigDecimal::add)
        ));

    assertEquals(new BigDecimal("300"), totals.get("USD"));
    assertEquals(new BigDecimal("150"), totals.get("EUR"));
    assertNull(totals.get("GBP"));
}
```

---

## Stream Collector Cheat Sheet

```
┌──────────────────────────────┬──────────────────────────────────────┐
│ Collector                    │ What It Does                         │
├──────────────────────────────┼──────────────────────────────────────┤
│ toList()                     │ Collect to mutable ArrayList         │
│ toUnmodifiableList()         │ Collect to unmodifiable list         │
│ toSet()                      │ Collect to mutable HashSet           │
│ toMap(keyFn, valFn)          │ Collect to mutable HashMap           │
│ groupingBy(classifier)       │ Group into Map<K, List<V>>           │
│ groupingBy(classifier, down) │ Group + downstream collector         │
│ partitioningBy(predicate)    │ Split into Map<Boolean, List<V>>     │
│ counting()                   │ Count elements                       │
│ reducing(identity, fn)       │ Reduce to single value               │
│ summarizingInt/Long/Double   │ Count, sum, min, max, avg            │
│ teeing(c1, c2, merger)       │ Two collectors, one pass, merge      │
│ joining(delimiter)           │ Concatenate strings                  │
│ filtering(pred, downstream)  │ Filter inside groupingBy             │
│ flatMapping(fn, downstream)  │ FlatMap inside groupingBy            │
└──────────────────────────────┴──────────────────────────────────────┘
```

---

## What You Learned

| Concept | One-liner |
|---|---|
| `Collectors.teeing` | Two collectors in parallel, merge results |
| `mapMulti` | One-to-many mapping without intermediate streams |
| `takeWhile` / `dropWhile` | Process elements until a condition changes |
| `Gatherers.windowFixed` | Non-overlapping chunks (preview) |
| `Gatherers.windowSliding` | Sliding window (preview) |
| `Gatherers.mapConcurrent` | Bounded concurrent mapping with virtual threads (preview) |
| `groupingBy` + `reducing` | Group and aggregate in one pass |
| `stream().toList()` | Unmodifiable list — prefer over `collect(toList())` |

---

## The Series Wrap-Up

You started with a Java 11 codebase: 400,000 lines of boilerplate, null checks, `instanceof` chains, and `StringBuilder` gymnastics. You ended with:

```
Chapter 1: Records              → 47 DTOs, 4,000 lines of boilerplate → 300 lines
Chapter 2: Sealed Classes       → 200-line instanceof staircase → exhaustive switch
Chapter 3: Switch Expressions   → Fall-through bug costing $47K → arrow syntax, no fall-through
Chapter 4: Text Blocks          → StringBuilder SQL/JSON/HTML → readable multi-line strings
Chapter 5: Null Safety          → NPE at 4:58 PM Friday → helpful NPEs, Optional, fail-fast
Chapter 6: Virtual Threads      → OOM at 12K threads → millions of virtual threads, ~1KB each
Chapter 7: Collections          → 18 lines to create a list → List.of(), getFirst(), reversed()
Chapter 8: Streams              → Unreadable 15-line pipelines → teeing, mapMulti, Gatherers
```

Every chapter was a real problem. The theory followed the bug. The fix followed the test.

Priya reviews the final PR. One comment:

> "Ship it."

---

[← Chapter 7: The Collection Ceremony](chapter-07-collections.md) | [README](README.md)

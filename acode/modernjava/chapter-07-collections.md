# Chapter 7: The Collection Ceremony

[← Chapter 6: The Thread Avalanche](chapter-06-virtual-threads.md) | [Chapter 8: The Stream Spaghetti →](chapter-08-streams.md)

---

## The Incident

Marcus opens `ReportGenerator.java`. The first 30 lines are just creating collections:

```java
List<String> currencies = new ArrayList<>();
currencies.add("USD");
currencies.add("EUR");
currencies.add("GBP");
currencies = Collections.unmodifiableList(currencies);

Map<String, BigDecimal> rates = new HashMap<>();
rates.put("USD", BigDecimal.ONE);
rates.put("EUR", new BigDecimal("0.92"));
rates.put("GBP", new BigDecimal("0.79"));
rates = Collections.unmodifiableMap(rates);

Set<String> supportedRegions = new HashSet<>();
supportedRegions.add("us-east");
supportedRegions.add("eu-west");
supportedRegions.add("ap-south");
supportedRegions = Collections.unmodifiableSet(supportedRegions);
```

18 lines. Zero logic. Pure ceremony.

And later:

```java
String last = currencies.get(currencies.size() - 1);
String first = currencies.get(0);
```

Priya: "This is Java 11 code running on Java 21. Fix it."

---

## Collection Factories (Java 9+)

`List.of()`, `Set.of()`, `Map.of()` — immutable collections in one line:

```java
List<String> currencies = List.of("USD", "EUR", "GBP");
Set<String> regions = Set.of("us-east", "eu-west", "ap-south");
Map<String, BigDecimal> rates = Map.of(
    "USD", BigDecimal.ONE,
    "EUR", new BigDecimal("0.92"),
    "GBP", new BigDecimal("0.79")
);
```

18 lines → 7 lines. Already immutable. No `Collections.unmodifiableX()` wrapper.

### The Test

```java
@Test
void factoryMethods_shouldCreateImmutableCollections() {
    var list = List.of("a", "b", "c");
    var set = Set.of(1, 2, 3);
    var map = Map.of("key", "value");

    assertThrows(UnsupportedOperationException.class, () -> list.add("d"));
    assertThrows(UnsupportedOperationException.class, () -> set.add(4));
    assertThrows(UnsupportedOperationException.class, () -> map.put("k2", "v2"));
}

@Test
void factoryMethods_shouldRejectNulls() {
    assertThrows(NullPointerException.class, () -> List.of("a", null));
    assertThrows(NullPointerException.class, () -> Set.of(1, null));
    assertThrows(NullPointerException.class, () -> Map.of("key", null));
}
```

Key rules:
- Immutable — `add`, `put`, `remove` throw `UnsupportedOperationException`
- No nulls — `NullPointerException` on creation
- `Set.of()` rejects duplicates — `IllegalArgumentException`
- `Map.of()` supports up to 10 key-value pairs; use `Map.ofEntries()` for more

---

## Map.ofEntries and Map.entry

For maps with more than 10 entries:

```java
Map<String, BigDecimal> rates = Map.ofEntries(
    Map.entry("USD", BigDecimal.ONE),
    Map.entry("EUR", new BigDecimal("0.92")),
    Map.entry("GBP", new BigDecimal("0.79")),
    Map.entry("JPY", new BigDecimal("149.50")),
    Map.entry("CAD", new BigDecimal("1.36")),
    // ... as many as you need
);
```

---

## List.copyOf, Set.copyOf, Map.copyOf

Create an immutable copy of an existing mutable collection:

```java
List<String> mutable = new ArrayList<>(List.of("a", "b", "c"));
List<String> immutable = List.copyOf(mutable);

mutable.add("d"); // mutable changes
assertEquals(3, immutable.size()); // immutable doesn't
```

### The Test

```java
@Test
void copyOf_shouldCreateIndependentImmutableCopy() {
    var original = new ArrayList<>(List.of("x", "y"));
    var copy = List.copyOf(original);

    original.add("z");

    assertEquals(3, original.size());
    assertEquals(2, copy.size()); // unaffected
    assertThrows(UnsupportedOperationException.class, () -> copy.add("w"));
}
```

---

## Sequenced Collections (Java 21)

Before Java 21, there was no common interface for "a collection with a defined encounter order." `List` has order. `LinkedHashSet` has order. `LinkedHashMap` has order. But they shared no common type that expressed it.

Java 21 adds three interfaces:

```
┌──────────────────────────┐
│  SequencedCollection     │  getFirst(), getLast(), reversed()
├──────────────────────────┤
│  SequencedSet            │  + no duplicates
├──────────────────────────┤
│  SequencedMap            │  firstEntry(), lastEntry(), reversed()
└──────────────────────────┘
```

### getFirst() and getLast()

No more `list.get(list.size() - 1)`:

```java
// Before (Java 11):
String first = currencies.get(0);
String last = currencies.get(currencies.size() - 1);

// After (Java 21):
String first = currencies.getFirst();
String last = currencies.getLast();
```

### The Test

```java
@Test
void sequencedCollection_getFirstAndLast() {
    var list = List.of("USD", "EUR", "GBP");

    assertEquals("USD", list.getFirst());
    assertEquals("GBP", list.getLast());
}

@Test
void sequencedCollection_emptyList_shouldThrow() {
    var empty = List.of();

    assertThrows(NoSuchElementException.class, empty::getFirst);
    assertThrows(NoSuchElementException.class, empty::getLast);
}
```

---

## reversed()

Get a reversed view of any sequenced collection:

```java
var list = List.of("A", "B", "C");
var reversed = list.reversed();

assertEquals(List.of("C", "B", "A"), reversed);
```

It's a **view** — no copying. Changes to the original (if mutable) are reflected in the reversed view.

### The Test

```java
@Test
void reversed_shouldReturnReversedView() {
    var original = new ArrayList<>(List.of(1, 2, 3));
    var reversed = original.reversed();

    assertEquals(List.of(3, 2, 1), reversed);

    original.add(4);
    assertEquals(List.of(4, 3, 2, 1), reversed); // view reflects changes
}
```

---

## SequencedMap

```java
var map = new LinkedHashMap<String, Integer>();
map.put("alpha", 1);
map.put("beta", 2);
map.put("gamma", 3);

Map.Entry<String, Integer> first = map.firstEntry(); // alpha=1
Map.Entry<String, Integer> last = map.lastEntry();   // gamma=3

map.putFirst("zero", 0);  // insert at the beginning
map.putLast("delta", 4);  // insert at the end

var reversed = map.reversed(); // gamma, beta, alpha order
```

### The Test

```java
@Test
void sequencedMap_firstAndLastEntry() {
    var map = new LinkedHashMap<String, Integer>();
    map.put("a", 1);
    map.put("b", 2);
    map.put("c", 3);

    assertEquals("a", map.firstEntry().getKey());
    assertEquals("c", map.lastEntry().getKey());
}
```

---

## stream().toList() vs collect(toList())

Java 16 added `toList()` directly on streams:

```java
// Before (Java 11):
List<String> result = items.stream()
    .filter(i -> i.startsWith("A"))
    .collect(Collectors.toList());

// After (Java 16+):
List<String> result = items.stream()
    .filter(i -> i.startsWith("A"))
    .toList();
```

Key difference: `toList()` returns an **unmodifiable** list. `collect(toList())` returns a mutable `ArrayList`.

### The Test

```java
@Test
void streamToList_shouldReturnUnmodifiableList() {
    var result = List.of("Alice", "Bob", "Charlie").stream()
        .filter(s -> s.length() > 3)
        .toList();

    assertEquals(List.of("Alice", "Charlie"), result);
    assertThrows(UnsupportedOperationException.class, () -> result.add("Dave"));
}

@Test
void collectToList_shouldReturnMutableList() {
    var result = List.of("Alice", "Bob").stream()
        .collect(Collectors.toList());

    result.add("Charlie"); // works — it's mutable
    assertEquals(3, result.size());
}
```

---

## The Cheat Sheet

```
Creating collections:
┌────────────────────────────────────────────────────────────┐
│ List.of("a", "b")           → immutable, no nulls          │
│ Set.of(1, 2, 3)             → immutable, no nulls, no dups │
│ Map.of("k", "v")            → immutable, ≤10 entries       │
│ Map.ofEntries(entry(...))   → immutable, any size           │
│ List.copyOf(mutable)        → immutable copy                │
│ stream().toList()            → unmodifiable list             │
│ stream().collect(toList())   → mutable ArrayList             │
└────────────────────────────────────────────────────────────┘

Sequenced collections (Java 21):
┌────────────────────────────────────────────────────────────┐
│ list.getFirst()              → first element                │
│ list.getLast()               → last element                 │
│ list.reversed()              → reversed view                │
│ map.firstEntry()             → first key-value pair         │
│ map.lastEntry()              → last key-value pair          │
│ map.putFirst(k, v)           → insert at beginning          │
│ map.sequencedKeySet()        → keys in order                │
└────────────────────────────────────────────────────────────┘
```

---

## What You Learned

| Concept | One-liner |
|---|---|
| `List.of()` / `Set.of()` / `Map.of()` | Immutable collections in one line |
| `Map.ofEntries()` | Immutable map with >10 entries |
| `List.copyOf()` | Immutable copy of a mutable collection |
| `SequencedCollection` | Interface for ordered collections — `getFirst()`, `getLast()`, `reversed()` |
| `SequencedMap` | `firstEntry()`, `lastEntry()`, `putFirst()`, `putLast()` |
| `stream().toList()` | Unmodifiable list from a stream (Java 16+) |
| No nulls in factory methods | `List.of(null)` throws NPE |

---

## The Foreshadow

The collection ceremony is gone. But Marcus opens `TransactionAnalyzer.java` — a 15-line stream pipeline that nobody can read:

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

Priya: "There are better collectors now. And Gatherers are coming."

---

[← Chapter 6: The Thread Avalanche](chapter-06-virtual-threads.md) | [Chapter 8: The Stream Spaghetti →](chapter-08-streams.md)

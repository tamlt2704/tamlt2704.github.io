# Chapter 11: Bulk Operations — Streams + Collections

[← Chapter 10: Unmodifiable](chapter-10-unmodifiable.md) | [Chapter 12: Choosing the Right Tool →](chapter-12-tradeoffs.md)

---

## The Problem

ShipStream needs complex aggregations: "Group orders by city, filter to those over $100, sum revenue per city, sort by total descending." The imperative version is 30 lines of loops and temporary maps.

## Streams: Declarative Collection Processing

```java
Map<String, Double> revenueByCity = orders.stream()
    .filter(o -> o.amount() > 100)
    .collect(Collectors.groupingBy(
        Order::city,
        Collectors.summingDouble(Order::amount)
    ));

// Sort by revenue descending
List<Map.Entry<String, Double>> ranked = revenueByCity.entrySet().stream()
    .sorted(Map.Entry.<String, Double>comparingByValue().reversed())
    .toList();
```

## Key Collectors

```java
// Group by
Map<String, List<Order>> byStatus = orders.stream()
    .collect(Collectors.groupingBy(Order::status));

// Count per group
Map<String, Long> countByStatus = orders.stream()
    .collect(Collectors.groupingBy(Order::status, Collectors.counting()));

// Partition (boolean split)
Map<Boolean, List<Order>> split = orders.stream()
    .collect(Collectors.partitioningBy(o -> o.amount() > 1000));

// To specific collection type
TreeSet<Order> sorted = orders.stream()
    .collect(Collectors.toCollection(() -> new TreeSet<>(Comparator.comparing(Order::amount))));

// Joining strings
String ids = orders.stream()
    .map(Order::id)
    .collect(Collectors.joining(", "));
```

## Parallel Streams (Use Carefully)

```java
// Parallel processing for CPU-heavy operations on large collections
double total = orders.parallelStream()
    .filter(o -> o.status() == Status.COMPLETED)
    .mapToDouble(Order::amount)
    .sum();
```

Rules for parallel streams:
- Collection must be large (>10,000 elements)
- Operation must be CPU-bound (not I/O)
- No shared mutable state
- Source must support efficient splitting (ArrayList yes, LinkedList no)

## What You Learned

- **Streams** — declarative pipeline for collection processing
- **Collectors** — groupingBy, counting, summingDouble, joining
- **toList()** — Java 16+ shorthand for collecting to list
- **Parallel streams** — use only for large, CPU-bound, stateless operations
- **Streams don't modify** the source collection — they produce new results

---

[← Chapter 10: Unmodifiable](chapter-10-unmodifiable.md) | [Chapter 12: Choosing the Right Tool →](chapter-12-tradeoffs.md)

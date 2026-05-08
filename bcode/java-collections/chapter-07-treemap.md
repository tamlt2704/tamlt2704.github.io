# Chapter 7: Price Ranges — TreeMap

[← Chapter 6: LinkedHashMap](chapter-06-linkedhashmap.md) | [Chapter 8: PriorityQueue →](chapter-08-priorityqueue.md)

---

## The Problem

ShipStream's pricing engine needs range queries: "Find all shipping rates between $5 and $15" or "What's the cheapest rate above $10?"

HashMap can't do range queries — it has no concept of order. You'd scan all entries.

## TreeMap: Sorted Map with Range Queries

```java
TreeMap<Double, ShippingRate> rates = new TreeMap<>();
rates.put(5.99, new ShippingRate("economy", 5.99, 7));
rates.put(9.99, new ShippingRate("standard", 9.99, 3));
rates.put(14.99, new ShippingRate("express", 14.99, 1));
rates.put(24.99, new ShippingRate("overnight", 24.99, 0));

// Range query: rates between $8 and $20
SortedMap<Double, ShippingRate> midRange = rates.subMap(8.0, 20.0);
// {9.99=standard, 14.99=express}

// Floor/ceiling
rates.floorKey(12.0);    // 9.99 (largest key ≤ 12)
rates.ceilingKey(12.0);  // 14.99 (smallest key ≥ 12)

// First/last
rates.firstKey();         // 5.99
rates.lastKey();          // 24.99
```

## NavigableMap Operations

```java
rates.headMap(10.0);              // All rates < $10
rates.tailMap(10.0);              // All rates ≥ $10
rates.subMap(5.0, true, 15.0, true);  // $5 ≤ rate ≤ $15 (inclusive)

rates.descendingMap();            // Reverse order view
rates.navigableKeySet();          // Keys as NavigableSet
```

## Performance

| Operation | TreeMap | HashMap |
|---|---|---|
| put/get/remove | O(log n) | O(1) |
| Range query | O(log n + k) | O(n) |
| First/last | O(log n) | O(n) |
| Ordered iteration | O(n) | O(n) but unordered |

Use TreeMap when you need sorted keys or range queries. Use HashMap when you just need fast lookup.

## ShipStream's Rate Finder

```java
public class RateFinder {
    private final TreeMap<Double, List<ShippingRate>> byWeight = new TreeMap<>();

    public List<ShippingRate> findRatesForWeight(double weight) {
        // Find the rate tier that covers this weight
        Map.Entry<Double, List<ShippingRate>> entry = byWeight.floorEntry(weight);
        return entry != null ? entry.getValue() : List.of();
    }

    public List<ShippingRate> findRatesInPriceRange(double min, double max) {
        return byWeight.subMap(min, true, max, true)
            .values().stream()
            .flatMap(List::stream)
            .toList();
    }
}
```

## What You Learned

- **TreeMap** — sorted map using red-black tree, O(log n) operations
- **Range queries** — subMap, headMap, tailMap
- **Floor/ceiling** — nearest key above/below a value
- **Use case** — price ranges, time-series data, interval lookups

---

[← Chapter 6: LinkedHashMap](chapter-06-linkedhashmap.md) | [Chapter 8: PriorityQueue →](chapter-08-priorityqueue.md)

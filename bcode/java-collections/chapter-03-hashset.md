# Chapter 3: No Duplicates Allowed — HashSet

[← Chapter 2: LinkedList](chapter-02-linkedlist.md) | [Chapter 4: TreeSet →](chapter-04-treeset.md)

---

## The Problem

ShipStream processes 4 million orders per day. Sometimes the same order arrives twice — network retries, webhook duplicates, user double-clicks. The deduplication check:

```java
public class OrderIngestion {
    private final List<String> processedIds = new ArrayList<>();

    public boolean isDuplicate(String orderId) {
        return processedIds.contains(orderId);  // O(n) — scans entire list
    }

    public void markProcessed(String orderId) {
        processedIds.add(orderId);
    }
}
```

After processing 1 million orders, `contains()` scans up to 1 million entries for every new order. The dedup check alone takes 3 hours nightly.

Raj: "You're doing a linear scan on a million-element list for every single order. That's O(n) per check, O(n²) total. Use a HashSet."

## HashSet: O(1) Contains

```java
import java.util.HashSet;
import java.util.Set;

public class OrderIngestion {
    private final Set<String> processedIds = new HashSet<>();

    public boolean isDuplicate(String orderId) {
        return processedIds.contains(orderId);  // O(1) average
    }

    public void markProcessed(String orderId) {
        processedIds.add(orderId);  // O(1) average, rejects duplicates
    }
}
```

Same logic. O(1) instead of O(n). The nightly job drops from 3 hours to 4 seconds.

## How Hashing Works

A hash function converts any object into an integer (the hash code). That integer determines where the element is stored in an internal array:

```
"ORD-001" → hashCode() → 738291 → index = 738291 % 16 → bucket 3
"ORD-002" → hashCode() → 194823 → index = 194823 % 16 → bucket 7
"ORD-003" → hashCode() → 738291 → index = 738291 % 16 → bucket 3 (collision!)
```

```
Buckets:  [0] [1] [2] [3]        [4] [5] [6] [7]     ...
                       │                       │
                    ORD-001                  ORD-002
                       │
                    ORD-003 (chained)
```

To check if an element exists:
1. Compute hash code → find bucket (O(1))
2. Check elements in that bucket (usually 1-2 elements)

Average case: O(1). Worst case (all elements in one bucket): O(n).

## The equals/hashCode Contract

For HashSet to work correctly, your objects must implement `hashCode()` and `equals()` consistently:

```java
public record Order(String id, String customer, double amount) {
    // Records auto-generate equals() and hashCode() based on all fields
}

// Or manually:
public class Order {
    private String id;
    private String customer;
    private double amount;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Order other)) return false;
        return Objects.equals(id, other.id);  // Two orders are "same" if same ID
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);  // Must be consistent with equals
    }
}
```

**The contract:**
1. If `a.equals(b)` is true, then `a.hashCode() == b.hashCode()` must be true
2. If hash codes differ, the objects are definitely not equal (fast rejection)
3. If hash codes are the same, objects *might* be equal (check with `equals()`)

**Break this contract and HashSet silently fails:**

```java
// BROKEN: equals uses id, hashCode uses default (memory address)
Set<Order> orders = new HashSet<>();
orders.add(new Order("ORD-1", "Alice", 100));
orders.contains(new Order("ORD-1", "Alice", 100));  // false! Different hash codes!
```

## Load Factor and Rehashing

HashSet starts with 16 buckets. As you add elements, buckets fill up. When the **load factor** (elements / buckets) exceeds 0.75, the set doubles its bucket count and rehashes everything:

```java
// Default: 16 buckets, load factor 0.75
// Rehash at: 16 × 0.75 = 12 elements
Set<String> set = new HashSet<>();

// Custom: 1M initial capacity (avoids rehashing for known sizes)
Set<String> set = new HashSet<>(1_000_000);

// Custom load factor (higher = more collisions, less memory)
Set<String> set = new HashSet<>(16, 0.9f);
```

For ShipStream's 4M daily orders, pre-sizing avoids expensive rehashes:

```java
Set<String> processedIds = new HashSet<>(6_000_000);  // ~4M / 0.75 load factor
```

## Set Operations

HashSet supports mathematical set operations:

```java
Set<String> todayOrders = new HashSet<>(List.of("A", "B", "C", "D"));
Set<String> yesterdayOrders = new HashSet<>(List.of("C", "D", "E", "F"));

// Union: all orders from both days
Set<String> union = new HashSet<>(todayOrders);
union.addAll(yesterdayOrders);  // [A, B, C, D, E, F]

// Intersection: orders that appeared both days (duplicates!)
Set<String> intersection = new HashSet<>(todayOrders);
intersection.retainAll(yesterdayOrders);  // [C, D]

// Difference: orders only today (new orders)
Set<String> difference = new HashSet<>(todayOrders);
difference.removeAll(yesterdayOrders);  // [A, B]
```

## Common Pitfalls

### 1. Mutable Objects as Set Elements

```java
// DANGEROUS: modifying an element after adding it
Set<List<String>> set = new HashSet<>();
List<String> list = new ArrayList<>(List.of("a", "b"));
set.add(list);

list.add("c");  // Mutates the element — hash code changes!
set.contains(list);  // false! It's in the wrong bucket now
```

Rule: **never mutate an object after adding it to a HashSet.** Use immutable objects (records, `List.of()`, etc.).

### 2. No Ordering Guarantee

```java
Set<String> set = new HashSet<>();
set.add("banana");
set.add("apple");
set.add("cherry");

for (String s : set) System.out.println(s);
// Could print in ANY order: cherry, banana, apple
// Order depends on hash codes, not insertion order
```

If you need insertion order, use `LinkedHashSet`. If you need sorted order, use `TreeSet` (Chapter 4).

## Performance Characteristics

| Operation | Average | Worst Case |
|---|---|---|
| `add(element)` | O(1) | O(n) (all in one bucket) |
| `contains(element)` | O(1) | O(n) |
| `remove(element)` | O(1) | O(n) |
| `size()` | O(1) | O(1) |
| Iteration | O(n + buckets) | O(n + buckets) |

The worst case (O(n)) happens when all elements hash to the same bucket. In practice, with a good hash function, this essentially never happens. Java 8+ converts long chains to balanced trees (O(log n) worst case per bucket).

## ShipStream's Deduplication — Final Version

```java
public class DeduplicationService {
    // Rolling window: keep last 24 hours of order IDs
    private final Set<String> recentIds = new HashSet<>(6_000_000);
    private final Queue<String> insertionOrder = new ArrayDeque<>();
    private static final int MAX_SIZE = 5_000_000;

    public synchronized boolean processIfNew(String orderId) {
        if (recentIds.contains(orderId)) {
            return false;  // Duplicate — skip
        }

        recentIds.add(orderId);
        insertionOrder.add(orderId);

        // Evict oldest if over capacity
        while (recentIds.size() > MAX_SIZE) {
            String oldest = insertionOrder.poll();
            recentIds.remove(oldest);
        }

        return true;  // New order — process it
    }
}
```

## What You Learned

- **HashSet** — O(1) add/contains/remove using hash codes
- **hashCode/equals contract** — must be consistent or HashSet breaks silently
- **Load factor** — 0.75 default, triggers rehash when exceeded
- **Pre-size for known volumes** — avoids expensive rehashing
- **No ordering** — iteration order is unpredictable
- **Immutable elements** — never mutate objects in a HashSet
- **Set operations** — union, intersection, difference

Deduplication is instant now. But Marcus wants a leaderboard: "Show me the top 100 sellers, sorted by revenue, updated in real-time." A HashSet can't sort. We need a TreeSet.

---

[← Chapter 2: LinkedList](chapter-02-linkedlist.md) | [Chapter 4: TreeSet →](chapter-04-treeset.md)

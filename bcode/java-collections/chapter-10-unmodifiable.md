# Chapter 10: Immutable Snapshots — Unmodifiable Collections

[← Chapter 9: Deque](chapter-09-deque.md) | [Chapter 11: Streams + Collections →](chapter-11-streams-collections.md)

---

## The Problem

ShipStream's API returns internal lists directly. A bug: a controller modifies the returned list, corrupting shared state:

```java
public List<Order> getActiveOrders() {
    return activeOrders;  // Returns the actual internal list!
}

// Somewhere else:
List<Order> orders = service.getActiveOrders();
orders.clear();  // Oops — cleared the service's internal state!
```

## Unmodifiable Collections

```java
// Java 9+ factory methods (truly immutable)
List<String> immutable = List.of("a", "b", "c");
Set<String> immutableSet = Set.of("x", "y", "z");
Map<String, Integer> immutableMap = Map.of("key", 1, "other", 2);

// Wrapping existing collections (unmodifiable view)
List<Order> safe = Collections.unmodifiableList(activeOrders);

// Copying to immutable (Java 10+)
List<Order> snapshot = List.copyOf(activeOrders);
```

## Defensive Copies

```java
public class OrderService {
    private final List<Order> activeOrders = new ArrayList<>();

    public List<Order> getActiveOrders() {
        return List.copyOf(activeOrders);  // Snapshot — caller can't corrupt us
    }

    public void addOrder(Order order) {
        activeOrders.add(Objects.requireNonNull(order));
    }
}
```

## List.of() vs Collections.unmodifiableList()

| | `List.of()` | `Collections.unmodifiableList()` |
|---|---|---|
| Truly immutable | Yes | No — view of mutable list |
| Null elements | Not allowed | Allowed |
| Underlying changes | N/A | Reflected in view |
| Serializable | Yes | Yes |

## What You Learned

- **List.of/Set.of/Map.of** — create truly immutable collections
- **List.copyOf** — immutable snapshot of existing collection
- **Collections.unmodifiableX** — unmodifiable view (underlying can still change)
- **Defensive copies** — return copies from getters to protect internal state
- **Never return internal mutable collections** — always copy or wrap

---

[← Chapter 9: Deque](chapter-09-deque.md) | [Chapter 11: Streams + Collections →](chapter-11-streams-collections.md)

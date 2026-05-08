# Chapter 1: The Order Queue — ArrayList

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: LinkedList →](chapter-02-linkedlist.md)

---

## The Problem

ShipStream's order ingestion service receives orders and stores them for processing. The original code uses a raw array:

```java
public class OrderQueue {
    private Order[] orders = new Order[100];
    private int size = 0;

    public void addOrder(Order order) {
        if (size >= orders.length) {
            // Uh oh — array is full
            throw new RuntimeException("Order queue full!");
        }
        orders[size++] = order;
    }
}
```

At 3 AM on Black Friday, the queue hits 100 orders and crashes. The on-call engineer bumps it to 10,000. It crashes again at 4 AM. They bump it to 1,000,000. Now it wastes memory on quiet days and still might crash on the next spike.

Raj: "Why are we managing array sizes manually? It's 2024."

## ArrayList: The Dynamic Array

`ArrayList` is a resizable array. It handles growth automatically:

```java
import java.util.ArrayList;
import java.util.List;

public class OrderQueue {
    private final List<Order> orders = new ArrayList<>();

    public void addOrder(Order order) {
        orders.add(order);  // Never throws "full" — grows as needed
    }

    public Order getOrder(int index) {
        return orders.get(index);  // O(1) random access
    }

    public int size() {
        return orders.size();
    }
}
```

No capacity limit. No manual resizing. It just works.

## How ArrayList Works Internally

Under the hood, ArrayList is still an array — but it manages resizing for you:

```java
// Simplified internal structure
public class MyArrayList<E> {
    private Object[] elementData;
    private int size;

    public MyArrayList() {
        this.elementData = new Object[10];  // Default capacity: 10
        this.size = 0;
    }

    public void add(E element) {
        if (size == elementData.length) {
            grow();  // Array full — make it bigger
        }
        elementData[size++] = element;
    }

    private void grow() {
        int newCapacity = elementData.length + (elementData.length >> 1); // 1.5x
        elementData = Arrays.copyOf(elementData, newCapacity);
    }

    public E get(int index) {
        if (index >= size) throw new IndexOutOfBoundsException();
        return (E) elementData[index];
    }
}
```

Key insight: when the array fills up, ArrayList creates a new array **1.5x larger** and copies everything over. This is expensive (O(n)) but happens rarely.

## Amortized O(1) — Why Growth Is Cheap

"Wait — copying the entire array is O(n). How is `add()` O(1)?"

Because it doesn't happen every time. It happens less and less frequently as the list grows:

```
Capacity: 10  → adds 1-10 are free, add 11 triggers copy (10 elements)
Capacity: 15  → adds 12-15 are free, add 16 triggers copy (15 elements)
Capacity: 22  → adds 17-22 are free, add 23 triggers copy (22 elements)
Capacity: 33  → ...
```

If you add n elements, the total copies are roughly: 10 + 15 + 22 + 33 + ... ≈ 3n

Total work for n adds: n (the adds themselves) + 3n (copies) = 4n = **O(n) total**, which is **O(1) per add** on average.

This is **amortized O(1)** — any single add might be expensive, but averaged over many adds, each one is constant time.

## Performance Characteristics

| Operation | Time | Why |
|---|---|---|
| `get(index)` | O(1) | Direct array access |
| `add(element)` | O(1) amortized | Append to end, occasional resize |
| `add(index, element)` | O(n) | Must shift elements right |
| `remove(index)` | O(n) | Must shift elements left |
| `contains(element)` | O(n) | Linear scan |
| `size()` | O(1) | Stored as field |

## ShipStream's Order Processing

```java
public class OrderProcessor {
    private final List<Order> pending = new ArrayList<>();
    private final List<Order> completed = new ArrayList<>();

    public void ingest(Order order) {
        pending.add(order);  // O(1) amortized — handles any volume
    }

    public void processBatch(int batchSize) {
        // Process from the end (avoids shifting)
        int start = Math.max(0, pending.size() - batchSize);
        List<Order> batch = new ArrayList<>(pending.subList(start, pending.size()));

        for (Order order : batch) {
            process(order);
            completed.add(order);
        }

        // Remove processed orders
        pending.subList(start, pending.size()).clear();
    }

    public Order findById(String orderId) {
        // O(n) — this is the problem we'll fix in Chapter 5 (HashMap)
        for (Order order : pending) {
            if (order.id().equals(orderId)) {
                return order;
            }
        }
        return null;
    }

    private void process(Order order) {
        // ... business logic
    }
}
```

## Common Pitfalls

### 1. Removing While Iterating

```java
// WRONG — ConcurrentModificationException
for (Order order : orders) {
    if (order.isExpired()) {
        orders.remove(order);  // 💥
    }
}

// RIGHT — use Iterator
Iterator<Order> it = orders.iterator();
while (it.hasNext()) {
    if (it.next().isExpired()) {
        it.remove();  // Safe
    }
}

// ALSO RIGHT — removeIf (Java 8+)
orders.removeIf(Order::isExpired);
```

### 2. Frequent Inserts at the Beginning

```java
// O(n) every time — shifts all elements
orders.add(0, newOrder);  // Don't do this in a loop
```

If you need frequent inserts at the front, ArrayList is the wrong choice (see Chapter 2: LinkedList, or Chapter 9: ArrayDeque).

### 3. Not Pre-sizing When You Know the Count

```java
// BAD: starts at 10, resizes 20+ times for 1M elements
List<Order> orders = new ArrayList<>();

// GOOD: one allocation, no resizing
List<Order> orders = new ArrayList<>(1_000_000);
```

If you know (or can estimate) the final size, pass it to the constructor.

## Benchmark: Raw Array vs ArrayList

```java
public static void main(String[] args) {
    int n = 10_000_000;

    // ArrayList
    long start = System.nanoTime();
    List<Integer> list = new ArrayList<>(n);
    for (int i = 0; i < n; i++) list.add(i);
    long listTime = System.nanoTime() - start;

    // Raw array
    start = System.nanoTime();
    int[] arr = new int[n];
    for (int i = 0; i < n; i++) arr[i] = i;
    long arrTime = System.nanoTime() - start;

    System.out.printf("ArrayList: %d ms%n", listTime / 1_000_000);
    System.out.printf("int[]:     %d ms%n", arrTime / 1_000_000);
}
```

Typical output:
```
ArrayList: 180 ms  (autoboxing Integer objects)
int[]:      25 ms  (primitive, no objects)
```

ArrayList is ~7x slower here due to autoboxing (`int` → `Integer`). For primitive-heavy workloads, consider `int[]` or specialized libraries (Eclipse Collections, HPPC).

## When to Use ArrayList

✅ **Use ArrayList when:**
- You need indexed access (`get(i)`)
- Most operations are add-to-end and random reads
- You don't know the size upfront (but it grows)
- You iterate frequently (cache-friendly, contiguous memory)

❌ **Don't use ArrayList when:**
- You insert/remove from the middle frequently (O(n) shifts)
- You need O(1) contains/lookup (use HashSet/HashMap)
- You need sorted order maintained automatically (use TreeSet)
- You need thread safety (use CopyOnWriteArrayList or synchronize)

## What You Learned

- **ArrayList** = dynamic array that grows by 1.5x when full
- **Amortized O(1)** add — occasional O(n) resize, but rare
- **O(1) random access** — direct index into backing array
- **O(n) insert/remove in middle** — elements must shift
- **Pre-size when possible** — avoids unnecessary resizing
- **Don't remove while iterating** — use Iterator or removeIf

ShipStream's order queue no longer crashes on Black Friday. But the undo system (which needs frequent inserts and removals in the middle) is still painfully slow. That's a different data structure.

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: LinkedList →](chapter-02-linkedlist.md)

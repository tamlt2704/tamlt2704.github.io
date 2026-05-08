# Chapter 5: The Lookup Table — HashMap

[← Chapter 4: TreeSet](chapter-04-treeset.md) | [Chapter 6: LinkedHashMap →](chapter-06-linkedhashmap.md)

---

## The Problem

ShipStream's customer lookup scans an ArrayList:

```java
public Customer findById(String customerId) {
    for (Customer c : customers) {
        if (c.id().equals(customerId)) return c;
    }
    return null;  // O(n) — 4 million customers
}
```

At 4 million customers, each lookup takes ~2ms. The API endpoint calls this 500 times per second. That's 1 second of CPU time per second — 100% utilization on one core just for lookups.

## HashMap: O(1) Key-Value Lookup

```java
Map<String, Customer> customerMap = new HashMap<>();

// Populate
for (Customer c : allCustomers) {
    customerMap.put(c.id(), c);
}

// Lookup: O(1)
Customer customer = customerMap.get("CUST-12345");
```

4 million customers. Lookup time: ~50 nanoseconds. That's 40,000x faster than the ArrayList scan.

## How HashMap Works

HashMap is an array of buckets. Each key's `hashCode()` determines which bucket it goes in:

```java
// Simplified internal logic
int hash = key.hashCode();
int bucket = hash & (capacity - 1);  // Fast modulo for power-of-2 sizes
```

When two keys hash to the same bucket (collision), they're stored in a linked list (or tree for long chains):

```
Bucket 0: → null
Bucket 1: → [K1:V1] → [K5:V5]  (collision chain)
Bucket 2: → [K2:V2]
Bucket 3: → null
Bucket 4: → [K3:V3]
...
```

## Essential Operations

```java
Map<String, Integer> inventory = new HashMap<>();

// Put (add/update)
inventory.put("widget", 100);
inventory.put("gadget", 50);
inventory.put("widget", 95);  // Overwrites previous value

// Get
int count = inventory.get("widget");           // 95
Integer maybe = inventory.get("nonexistent");  // null

// getOrDefault
int safe = inventory.getOrDefault("missing", 0);  // 0

// containsKey / containsValue
inventory.containsKey("widget");    // true — O(1)
inventory.containsValue(95);        // true — O(n)! Scans all values

// Remove
inventory.remove("gadget");         // Removes and returns 50

// Size
inventory.size();                   // 1

// Iterate
for (Map.Entry<String, Integer> entry : inventory.entrySet()) {
    System.out.println(entry.getKey() + ": " + entry.getValue());
}
```

## Modern Map Methods (Java 8+)

```java
Map<String, List<Order>> ordersByCustomer = new HashMap<>();

// computeIfAbsent: create value if key missing
ordersByCustomer.computeIfAbsent("alice", k -> new ArrayList<>()).add(order);

// merge: combine with existing value
Map<String, Integer> wordCount = new HashMap<>();
for (String word : words) {
    wordCount.merge(word, 1, Integer::sum);  // Increment or set to 1
}

// putIfAbsent: only put if not already present
cache.putIfAbsent(key, expensiveComputation());

// replaceAll: transform all values
prices.replaceAll((item, price) -> price * 1.1);  // 10% increase
```

## Performance

| Operation | Average | Worst Case |
|---|---|---|
| `put(key, value)` | O(1) | O(n) |
| `get(key)` | O(1) | O(n) |
| `remove(key)` | O(1) | O(n) |
| `containsKey(key)` | O(1) | O(n) |
| `containsValue(value)` | O(n) | O(n) |

Worst case happens with pathological hash collisions. Java 8+ mitigates this by converting long chains to balanced trees (O(log n) per bucket).

## ShipStream's Customer Service

```java
public class CustomerService {
    private final Map<String, Customer> byId = new HashMap<>(6_000_000);
    private final Map<String, List<Customer>> byCity = new HashMap<>();

    public void index(List<Customer> customers) {
        for (Customer c : customers) {
            byId.put(c.id(), c);
            byCity.computeIfAbsent(c.city(), k -> new ArrayList<>()).add(c);
        }
    }

    public Customer findById(String id) {
        return byId.get(id);  // O(1)
    }

    public List<Customer> findByCity(String city) {
        return byCity.getOrDefault(city, List.of());  // O(1) lookup
    }
}
```

## null Keys and Values

HashMap allows one null key and any number of null values:

```java
map.put(null, "value for null key");  // Legal
map.put("key", null);                  // Legal

// But be careful:
Integer val = map.get("missing");  // null — missing or value is null?
// Use containsKey to distinguish:
if (map.containsKey("key")) { /* key exists, value might be null */ }
```

## What You Learned

- **HashMap** — O(1) key-value lookup using hash codes
- **put/get/remove** — constant time operations
- **computeIfAbsent/merge** — modern idioms for common patterns
- **Pre-size** — `new HashMap<>(expectedSize)` avoids rehashing
- **null handling** — allows null keys/values (be careful)
- **containsValue is O(n)** — only containsKey is O(1)

Customer lookup is instant. But the config replay system needs insertion-order iteration — HashMap doesn't guarantee order. That's LinkedHashMap.

---

[← Chapter 4: TreeSet](chapter-04-treeset.md) | [Chapter 6: LinkedHashMap →](chapter-06-linkedhashmap.md)

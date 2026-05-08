# Chapter 4: Sorted Leaderboard — TreeSet

[← Chapter 3: HashSet](chapter-03-hashset.md) | [Chapter 5: HashMap →](chapter-05-hashmap.md)

---

## The Problem

Marcus wants a real-time leaderboard: "Show me the top 100 sellers by revenue, updated live." The current approach:

```java
List<Seller> sellers = new ArrayList<>(allSellers);
Collections.sort(sellers, Comparator.comparingDouble(Seller::revenue).reversed());
return sellers.subList(0, 100);
```

This re-sorts 50,000 sellers on every request. Sorting is O(n log n) — fine once, but the leaderboard refreshes every second. That's 50,000 × log(50,000) ≈ 780,000 comparisons per second.

Raj: "You're sorting the entire list every second. Use a data structure that stays sorted."

## TreeSet: Always Sorted

`TreeSet` maintains elements in sorted order at all times. Insertions, removals, and lookups are O(log n):

```java
TreeSet<Seller> leaderboard = new TreeSet<>(
    Comparator.comparingDouble(Seller::revenue).reversed()
        .thenComparing(Seller::id)  // Tiebreaker — TreeSet needs unique ordering
);

leaderboard.add(new Seller("alice", 48000));
leaderboard.add(new Seller("bob", 72000));
leaderboard.add(new Seller("carol", 55000));

// Always sorted — no explicit sort needed
leaderboard.forEach(System.out::println);
// bob: 72000, carol: 55000, alice: 48000
```

## How TreeSet Works: Red-Black Tree

Internally, TreeSet uses a **red-black tree** — a self-balancing binary search tree:

```
            [carol: 55000]
           /              \
    [alice: 48000]    [bob: 72000]
```

Every insertion and removal rebalances the tree to maintain O(log n) height. You never need to sort — the structure IS sorted.

| Operation | TreeSet | ArrayList + sort |
|---|---|---|
| Add | O(log n) | O(1) + O(n log n) to re-sort |
| Remove | O(log n) | O(n) |
| Contains | O(log n) | O(n) |
| First/Last | O(log n) | O(1) after sort |
| Get top K | O(K + log n) | O(n log n) |

## Comparable vs Comparator

TreeSet needs to know how to order elements. Two options:

### Option 1: Implement Comparable

```java
public record Seller(String id, double revenue) implements Comparable<Seller> {
    @Override
    public int compareTo(Seller other) {
        int cmp = Double.compare(other.revenue, this.revenue);  // Descending
        if (cmp != 0) return cmp;
        return this.id.compareTo(other.id);  // Tiebreaker
    }
}

TreeSet<Seller> set = new TreeSet<>();  // Uses natural ordering
```

### Option 2: Provide a Comparator

```java
TreeSet<Seller> set = new TreeSet<>(
    Comparator.comparingDouble(Seller::revenue).reversed()
        .thenComparing(Seller::id)
);
```

**Critical**: TreeSet uses comparison for equality. If `compareTo` returns 0, TreeSet considers the elements equal and won't add the second one. Always include a tiebreaker field.

## NavigableSet: Range Operations

TreeSet implements `NavigableSet`, giving you powerful range queries:

```java
TreeSet<Integer> prices = new TreeSet<>(List.of(10, 25, 50, 75, 100, 150, 200));

prices.headSet(75);           // [10, 25, 50] — less than 75
prices.tailSet(75);           // [75, 100, 150, 200] — >= 75
prices.subSet(25, 150);       // [25, 50, 75, 100] — >= 25 and < 150

prices.floor(80);             // 75 — largest element <= 80
prices.ceiling(80);           // 100 — smallest element >= 80
prices.lower(75);             // 50 — largest element < 75
prices.higher(75);            // 100 — smallest element > 75

prices.first();               // 10 — minimum
prices.last();                // 200 — maximum
prices.pollFirst();           // removes and returns 10
```

## ShipStream's Leaderboard

```java
public class Leaderboard {
    private final TreeSet<Seller> rankings;
    private final Map<String, Seller> sellerMap;  // For O(1) lookup by ID

    public Leaderboard() {
        this.rankings = new TreeSet<>(
            Comparator.comparingDouble(Seller::revenue).reversed()
                .thenComparing(Seller::id));
        this.sellerMap = new HashMap<>();
    }

    public void updateRevenue(String sellerId, double newRevenue) {
        Seller old = sellerMap.get(sellerId);
        if (old != null) {
            rankings.remove(old);  // O(log n)
        }
        Seller updated = new Seller(sellerId, newRevenue);
        rankings.add(updated);     // O(log n)
        sellerMap.put(sellerId, updated);
    }

    public List<Seller> getTop(int k) {
        return rankings.stream().limit(k).toList();  // O(k)
    }

    public int getRank(String sellerId) {
        Seller seller = sellerMap.get(sellerId);
        if (seller == null) return -1;
        return rankings.headSet(seller).size() + 1;  // O(n) — not ideal
    }
}
```

## When to Use TreeSet vs HashSet

| Need | Use |
|---|---|
| Fast contains/add/remove, no order | HashSet (O(1)) |
| Sorted iteration | TreeSet (O(log n)) |
| Range queries (between X and Y) | TreeSet |
| First/last/floor/ceiling | TreeSet |
| Maximum performance for add/contains | HashSet |

## What You Learned

- **TreeSet** — always-sorted set using a red-black tree
- **O(log n)** for add, remove, contains (vs O(1) for HashSet)
- **NavigableSet** — range queries, floor/ceiling, first/last
- **Comparator or Comparable** — required for ordering
- **Tiebreaker** — always include one, or TreeSet drops "equal" elements
- **Use case** — leaderboards, range queries, sorted iteration

The leaderboard updates in O(log n) per change instead of O(n log n). But the customer lookup endpoint still scans an ArrayList. We need O(1) key-value lookup — that's HashMap.

---

[← Chapter 3: HashSet](chapter-03-hashset.md) | [Chapter 5: HashMap →](chapter-05-hashmap.md)

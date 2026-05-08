# Chapter 6: Ordered Config — LinkedHashMap

[← Chapter 5: HashMap](chapter-05-hashmap.md) | [Chapter 7: TreeMap →](chapter-07-treemap.md)

---

## The Problem

ShipStream's config replay system applies settings in order. When a warehouse reconnects after downtime, it replays config changes sequentially. But HashMap doesn't preserve insertion order:

```java
Map<String, String> config = new HashMap<>();
config.put("region", "us-east-1");
config.put("max_workers", "16");
config.put("timeout", "30s");

// Iteration order is UNPREDICTABLE
config.forEach((k, v) -> applyConfig(k, v));
// Might apply timeout before region — breaks dependencies!
```

## LinkedHashMap: HashMap + Insertion Order

```java
Map<String, String> config = new LinkedHashMap<>();
config.put("region", "us-east-1");
config.put("max_workers", "16");
config.put("timeout", "30s");

// Iteration order = insertion order (guaranteed)
config.forEach((k, v) -> System.out.println(k + "=" + v));
// region=us-east-1
// max_workers=16
// timeout=30s
```

Same O(1) performance as HashMap, plus a doubly-linked list maintaining order.

## Access-Order Mode: LRU Cache

LinkedHashMap has a secret power — access-order mode:

```java
Map<String, Object> cache = new LinkedHashMap<>(16, 0.75f, true) {
    @Override
    protected boolean removeEldestEntry(Map.Entry<String, Object> eldest) {
        return size() > 1000;  // Evict when over 1000 entries
    }
};
```

With `accessOrder=true`, every `get()` moves the entry to the end. The least-recently-used entry is always first — perfect for an LRU cache.

```java
cache.put("a", 1);  // Order: a
cache.put("b", 2);  // Order: a, b
cache.put("c", 3);  // Order: a, b, c
cache.get("a");      // Order: b, c, a (a moved to end)
cache.put("d", 4);   // Order: b, c, a, d
// If size > max, "b" gets evicted (least recently used)
```

## ShipStream's Config Replay

```java
public class ConfigReplayService {
    private final LinkedHashMap<String, ConfigChange> changelog = new LinkedHashMap<>();

    public void recordChange(String key, String value, Instant timestamp) {
        changelog.put(key, new ConfigChange(key, value, timestamp));
    }

    public void replayFrom(Instant since) {
        changelog.values().stream()
            .filter(c -> c.timestamp().isAfter(since))
            .forEach(c -> applyConfig(c.key(), c.value()));
    }
}
```

## What You Learned

- **LinkedHashMap** — HashMap with guaranteed insertion order
- **Access-order mode** — moves accessed entries to end (LRU behavior)
- **removeEldestEntry** — automatic eviction for bounded caches
- **Same O(1) performance** as HashMap, slight memory overhead for links

---

[← Chapter 5: HashMap](chapter-05-hashmap.md) | [Chapter 7: TreeMap →](chapter-07-treemap.md)

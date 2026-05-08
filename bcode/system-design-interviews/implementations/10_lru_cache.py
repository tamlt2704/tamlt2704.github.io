"""
Distributed Cache — Core Implementation
=========================================
Demonstrates: LRU cache with O(1) get/put, consistent hashing ring
with virtual nodes, cache-aside pattern, thundering herd protection.

In a real system:
- LRU cache: Redis with maxmemory-policy allkeys-lru
- Consistent hashing: client-side (Jedis) or proxy (Twemproxy, Envoy)
- Cache-aside: application code checks cache → DB → backfill cache
- Thundering herd: Redis distributed lock (Redlock) or singleflight pattern
- Replication: Redis Sentinel or Redis Cluster for HA
"""

import hashlib
import time
import threading
from bisect import bisect_right
from dataclasses import dataclass


# ─── LRU Cache (O(1) get/put with doubly-linked list + hashmap) ──────────────

class DLLNode:
    """Doubly-linked list node for LRU ordering."""
    __slots__ = ['key', 'value', 'prev', 'next', 'expire_at']

    def __init__(self, key: str = "", value: str = "", expire_at: float = 0):
        self.key = key
        self.value = value
        self.prev: "DLLNode | None" = None
        self.next: "DLLNode | None" = None
        self.expire_at = expire_at  # 0 = no expiry


class LRUCache:
    """
    LRU Cache: O(1) get and put using hashmap + doubly-linked list.
    - Hashmap: key → DLLNode (O(1) lookup)
    - DLL: maintains access order (head = most recent, tail = least recent)
    - Eviction: remove from tail when capacity exceeded
    """

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: dict[str, DLLNode] = {}
        # Sentinel nodes simplify edge cases
        self.head = DLLNode()  # Most recently used
        self.tail = DLLNode()  # Least recently used
        self.head.next = self.tail
        self.tail.prev = self.head
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> str | None:
        """O(1) get — move to head on access."""
        if key not in self.cache:
            self.misses += 1
            return None
        node = self.cache[key]
        # Check TTL
        if node.expire_at and time.time() > node.expire_at:
            self._remove(node)
            del self.cache[key]
            self.misses += 1
            return None
        self._move_to_head(node)
        self.hits += 1
        return node.value

    def put(self, key: str, value: str, ttl: float = 0):
        """O(1) put — add/update and evict LRU if over capacity."""
        expire_at = time.time() + ttl if ttl > 0 else 0

        if key in self.cache:
            node = self.cache[key]
            node.value = value
            node.expire_at = expire_at
            self._move_to_head(node)
        else:
            node = DLLNode(key, value, expire_at)
            self.cache[key] = node
            self._add_to_head(node)
            if len(self.cache) > self.capacity:
                evicted = self._remove_tail()
                del self.cache[evicted.key]

    def _add_to_head(self, node: DLLNode):
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def _remove(self, node: DLLNode):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _move_to_head(self, node: DLLNode):
        self._remove(node)
        self._add_to_head(node)

    def _remove_tail(self) -> DLLNode:
        node = self.tail.prev
        self._remove(node)
        return node

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


# ─── Consistent Hashing Ring ─────────────────────────────────────────────────

class ConsistentHashRing:
    """
    Consistent hashing: adding/removing a node only remaps K/N keys (not all).
    Virtual nodes ensure even distribution across physical nodes.

    Production: used in DynamoDB, Cassandra, Memcached client libraries.
    """

    def __init__(self, num_virtual_nodes: int = 150):
        self.num_virtual_nodes = num_virtual_nodes
        self.ring: list[int] = []           # Sorted hash positions
        self.ring_map: dict[int, str] = {}  # hash position → node name
        self.nodes: set[str] = set()

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add_node(self, node: str):
        """Add a node with virtual nodes for better distribution."""
        self.nodes.add(node)
        for i in range(self.num_virtual_nodes):
            virtual_key = f"{node}:vn{i}"
            h = self._hash(virtual_key)
            self.ring.append(h)
            self.ring_map[h] = node
        self.ring.sort()

    def remove_node(self, node: str):
        """Remove a node — only its keys get remapped."""
        self.nodes.discard(node)
        self.ring = [h for h in self.ring if self.ring_map.get(h) != node]
        self.ring_map = {h: n for h, n in self.ring_map.items() if n != node}

    def get_node(self, key: str) -> str | None:
        """Find which node owns this key (clockwise walk)."""
        if not self.ring:
            return None
        h = self._hash(key)
        idx = bisect_right(self.ring, h)
        if idx == len(self.ring):
            idx = 0  # Wrap around
        return self.ring_map[self.ring[idx]]

    def get_distribution(self, keys: list[str]) -> dict[str, int]:
        """Show how keys are distributed across nodes."""
        dist: dict[str, int] = {node: 0 for node in self.nodes}
        for key in keys:
            node = self.get_node(key)
            if node:
                dist[node] += 1
        return dist


# ─── Cache-Aside Pattern ─────────────────────────────────────────────────────

class CacheAsideDB:
    """Simulates a slow database."""

    def __init__(self, latency_ms: float = 50):
        self.data: dict[str, str] = {}
        self.latency = latency_ms
        self.queries = 0

    def get(self, key: str) -> str | None:
        self.queries += 1
        time.sleep(self.latency / 1000)  # Simulate DB latency
        return self.data.get(key)

    def put(self, key: str, value: str):
        self.data[key] = value


def cache_aside_get(cache: LRUCache, db: CacheAsideDB, key: str) -> str | None:
    """Cache-aside: check cache → miss → query DB → backfill cache."""
    value = cache.get(key)
    if value is not None:
        return value  # Cache hit
    # Cache miss — query DB
    value = db.get(key)
    if value is not None:
        cache.put(key, value, ttl=300)  # Backfill with 5min TTL
    return value


# ─── Thundering Herd Protection (Singleflight) ──────────────────────────────

class Singleflight:
    """
    Prevents thundering herd: when cache expires, only ONE request
    fetches from DB. Others wait for that result.

    Production: Redis distributed lock or Go's singleflight package.
    """

    def __init__(self):
        self.in_flight: dict[str, threading.Event] = {}
        self.results: dict[str, str | None] = {}
        self.lock = threading.Lock()
        self.deduped = 0

    def do(self, key: str, fetch_fn) -> str | None:
        """Execute fetch_fn only once per key, even with concurrent callers."""
        with self.lock:
            if key in self.in_flight:
                # Another thread is already fetching — wait for it
                event = self.in_flight[key]
                self.deduped += 1
            else:
                # We're the first — create event and fetch
                event = threading.Event()
                self.in_flight[key] = event
                event = None  # Signal that WE should fetch

        if event:
            # Wait for the fetcher to finish
            event.wait(timeout=5.0)
            return self.results.get(key)
        else:
            # We're the fetcher
            try:
                result = fetch_fn(key)
                self.results[key] = result
                return result
            finally:
                with self.lock:
                    evt = self.in_flight.pop(key, None)
                    if evt:
                        evt.set()  # Wake up waiters


# ─── Demo ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Distributed Cache Demo ===\n")

    # --- LRU Cache ---
    print("--- LRU Cache (capacity=3) ---")
    cache = LRUCache(capacity=3)
    cache.put("a", "1")
    cache.put("b", "2")
    cache.put("c", "3")
    print(f"  get('a') = {cache.get('a')}")  # Hit, moves 'a' to front
    cache.put("d", "4")  # Evicts 'b' (least recently used)
    print(f"  After put('d'): get('b') = {cache.get('b')} (evicted!)")
    print(f"  get('c') = {cache.get('c')}")
    print(f"  get('d') = {cache.get('d')}")
    print(f"  Hit rate: {cache.hit_rate:.1%}")

    # --- Consistent Hashing ---
    print("\n--- Consistent Hashing Ring ---")
    ring = ConsistentHashRing(num_virtual_nodes=150)
    ring.add_node("cache-1")
    ring.add_node("cache-2")
    ring.add_node("cache-3")

    keys = [f"user:{i}" for i in range(1000)]
    dist = ring.get_distribution(keys)
    print(f"  3 nodes, 1000 keys:")
    for node, count in sorted(dist.items()):
        bar = "█" * (count // 20)
        print(f"    {node}: {count} keys {bar}")

    # Remove a node — see how few keys move
    original_mapping = {k: ring.get_node(k) for k in keys}
    ring.remove_node("cache-2")
    new_mapping = {k: ring.get_node(k) for k in keys}
    moved = sum(1 for k in keys if original_mapping[k] != new_mapping[k])
    print(f"\n  After removing cache-2:")
    print(f"    Keys remapped: {moved}/1000 ({moved/10:.1f}%)")
    print(f"    → Only ~1/N keys move (vs 100% with naive hash % N)")

    # --- Cache-Aside Pattern ---
    print("\n--- Cache-Aside Pattern ---")
    db = CacheAsideDB(latency_ms=10)
    app_cache = LRUCache(capacity=100)
    db.put("user:1", "Alice")
    db.put("user:2", "Bob")

    t0 = time.time()
    v1 = cache_aside_get(app_cache, db, "user:1")  # Miss → DB
    miss_time = time.time() - t0

    t0 = time.time()
    v2 = cache_aside_get(app_cache, db, "user:1")  # Hit → cache
    hit_time = time.time() - t0

    print(f"  First read (miss):  '{v1}' in {miss_time*1000:.1f}ms")
    print(f"  Second read (hit):  '{v2}' in {hit_time*1000:.1f}ms")
    print(f"  DB queries: {db.queries}")

    # --- Singleflight ---
    print("\n--- Thundering Herd Protection ---")
    sf = Singleflight()
    fetch_count = 0

    def slow_fetch(key):
        global fetch_count
        fetch_count += 1
        time.sleep(0.05)
        return f"value_for_{key}"

    # Simulate 10 concurrent requests for same key
    threads = []
    results = []
    for _ in range(10):
        t = threading.Thread(target=lambda: results.append(sf.do("hot_key", slow_fetch)))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    print(f"  10 concurrent requests for 'hot_key':")
    print(f"  Actual DB fetches: {fetch_count} (should be 1)")
    print(f"  Deduplicated: {sf.deduped} requests")
    print(f"  → Prevents thundering herd on cache miss!")

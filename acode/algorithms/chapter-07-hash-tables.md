# Chapter 7: Instant Lookup — Hash Tables

[← Chapter 6: Heaps](chapter-06-heaps.md) | [Chapter 8: Autocomplete →](chapter-08-tries.md)

---

## The Problem

The support tool needs to find packages by tracking number, recipient name, or address. Binary search gives O(log n) for one sorted key. But you can't sort by tracking number AND recipient AND address simultaneously.

You need O(1) lookup by any field. A hash table maps any key to a value in constant time — on average.

## The Idea

A hash table is an array where the index is computed from the key using a **hash function**.

```
hash("RM-058291") → 7231
array[7231] = Package(...)
```

Instead of searching, you calculate where the item lives. Direct access. O(1).

## Building a Hash Table

```python
class HashTable:
    def __init__(self, capacity=16):
        self.capacity = capacity
        self.size = 0
        self.buckets = [None] * capacity

    def _hash(self, key):
        """Convert key to array index."""
        h = 0
        for char in str(key):
            h = (h * 31 + ord(char)) % self.capacity
        return h

    def put(self, key, value):
        """Insert or update. O(1) average."""
        index = self._hash(key)

        # Linear probing for collision resolution
        start = index
        while self.buckets[index] is not None:
            stored_key, _ = self.buckets[index]
            if stored_key == key:
                self.buckets[index] = (key, value)  # Update
                return
            index = (index + 1) % self.capacity
            if index == start:
                raise Exception("Hash table full")

        self.buckets[index] = (key, value)
        self.size += 1

        # Resize if load factor > 0.7
        if self.size / self.capacity > 0.7:
            self._resize()

    def get(self, key):
        """Retrieve by key. O(1) average."""
        index = self._hash(key)
        start = index

        while self.buckets[index] is not None:
            stored_key, value = self.buckets[index]
            if stored_key == key:
                return value
            index = (index + 1) % self.capacity
            if index == start:
                break

        return None  # Not found

    def delete(self, key):
        """Remove by key. O(1) average."""
        index = self._hash(key)
        start = index

        while self.buckets[index] is not None:
            stored_key, _ = self.buckets[index]
            if stored_key == key:
                self.buckets[index] = None
                self.size -= 1
                self._rehash_cluster(index)
                return True
            index = (index + 1) % self.capacity
            if index == start:
                break
        return False

    def _resize(self):
        """Double capacity and rehash everything."""
        old_buckets = self.buckets
        self.capacity *= 2
        self.buckets = [None] * self.capacity
        self.size = 0
        for item in old_buckets:
            if item is not None:
                self.put(item[0], item[1])

    def _rehash_cluster(self, start):
        """Re-insert items that might have been displaced."""
        index = (start + 1) % self.capacity
        while self.buckets[index] is not None:
            item = self.buckets[index]
            self.buckets[index] = None
            self.size -= 1
            self.put(item[0], item[1])
            index = (index + 1) % self.capacity
```

## Collisions: When Two Keys Hash to the Same Index

With 100,000 packages and 131,072 slots (next power of 2), collisions are inevitable. Two strategies:

### Chaining (Separate Chaining)

Each bucket holds a linked list of all items that hash to that index:

```python
class ChainingHashTable:
    def __init__(self, capacity=16):
        self.capacity = capacity
        self.buckets = [[] for _ in range(capacity)]
        self.size = 0

    def put(self, key, value):
        index = self._hash(key)
        bucket = self.buckets[index]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self.size += 1

    def get(self, key):
        index = self._hash(key)
        for k, v in self.buckets[index]:
            if k == key:
                return v
        return None
```

### Open Addressing (Linear Probing)

If the slot is taken, check the next one. And the next. Until you find an empty slot.

Both are O(1) average, O(n) worst case (all keys hash to the same slot).

## Load Factor and Resizing

**Load factor** = size / capacity. As it approaches 1.0, collisions increase and performance degrades.

| Load Factor | Average probes (linear probing) |
|---|---|
| 0.5 | 1.5 |
| 0.7 | 2.2 |
| 0.9 | 5.5 |
| 0.95 | 10.5 |

Rule of thumb: resize when load factor exceeds 0.7. Double the capacity and rehash everything.

## RouteMaster's Multi-Index Lookup

```python
class PackageIndex:
    """O(1) lookup by any field using multiple hash tables."""

    def __init__(self):
        self.by_tracking = {}   # tracking_number → package
        self.by_recipient = {}  # recipient → [packages]
        self.by_address = {}    # address → [packages]
        self.by_status = {}     # status → [packages]

    def add(self, package):
        self.by_tracking[package.tracking] = package

        self.by_recipient.setdefault(package.recipient, []).append(package)
        self.by_address.setdefault(package.address, []).append(package)
        self.by_status.setdefault(package.status, []).append(package)

    def find_by_tracking(self, tracking):
        """O(1)"""
        return self.by_tracking.get(tracking)

    def find_by_recipient(self, name):
        """O(1) to find the list, O(k) to return k results"""
        return self.by_recipient.get(name, [])

    def update_status(self, tracking, new_status):
        """Update status and re-index."""
        package = self.by_tracking.get(tracking)
        if not package:
            return False

        # Remove from old status index
        old_list = self.by_status.get(package.status, [])
        old_list.remove(package)

        # Update and re-index
        package.status = new_status
        self.by_status.setdefault(new_status, []).append(package)
        return True
```

100,000 packages. Lookup by any field: O(1). The support tool responds instantly.

## The Holiday Rush: Hash Table Degeneration

December. Package volume triples. The intern's custom hash function:

```python
def bad_hash(key):
    return len(key) % capacity  # All 10-char tracking numbers → same bucket!
```

Every tracking number is 10 characters. They all hash to the same index. The hash table degenerates to a linked list. O(n) lookups. The support tool crashes.

A good hash function distributes keys uniformly. Python's built-in `hash()` uses SipHash — cryptographically inspired, excellent distribution.

## Complexity

| Operation | Average | Worst (all collisions) |
|---|---|---|
| Insert | O(1) | O(n) |
| Lookup | O(1) | O(n) |
| Delete | O(1) | O(n) |
| Resize | O(n) | O(n) |

Amortized insert (including occasional resizes): O(1).

## What You Learned

- **Hash function** — maps keys to array indices
- **Collisions** — chaining vs open addressing
- **Load factor** — resize at 0.7 to maintain O(1)
- **Multi-index** — multiple hash tables for different lookup keys
- **Good vs bad hash functions** — uniform distribution matters
- **Amortized O(1)** — occasional O(n) resize, but O(1) on average

The support tool is instant. But Derek from the mobile team wants address autocomplete — type "123 Ma" and see "123 Main St", "123 Maple Ave", "123 Market Rd". Hash tables can't do prefix matching. You need a different structure.

That's Chapter 8.

---

[← Chapter 6: Heaps](chapter-06-heaps.md) | [Chapter 8: Autocomplete →](chapter-08-tries.md)

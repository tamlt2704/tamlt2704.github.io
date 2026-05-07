# Chapter 8: Autocomplete — Tries

[← Chapter 7: Hash Tables](chapter-07-hash-tables.md) | [Chapter 9: Binary Search Trees →](chapter-09-bst.md)

---

## The Problem

The driver app needs address autocomplete. Marcus types "123 Ma" and should instantly see:
- 123 Main Street
- 123 Maple Avenue
- 123 Market Road

A hash table can't help — it needs the exact key. Binary search on sorted addresses could work (find the range starting with "123 Ma"), but inserting new addresses into a sorted array is O(n).

You need a data structure that's built for prefix matching: the **trie** (pronounced "try", from re**trie**val).

## The Trie: A Prefix Tree

A trie stores strings character by character. Each node represents a prefix. Shared prefixes share nodes.

```
Storing: "cat", "car", "card", "care", "dog"

         (root)
        /      \
       c        d
       |        |
       a        o
      / \       |
     t   r      g*
     *   |
        / \
       d   e
       *   *

* = marks end of a complete word
```

"cat" and "car" share the prefix "ca". "card" and "care" share "car". No duplication.

## Implementation

```python
class TrieNode:
    def __init__(self):
        self.children = {}  # char → TrieNode
        self.is_end = False
        self.value = None   # Store associated data at word endpoints

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, key, value=None):
        """Insert a string into the trie. O(m) where m = len(key)."""
        node = self.root
        for char in key:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.value = value

    def search(self, key):
        """Exact match lookup. O(m)."""
        node = self._find_node(key)
        if node and node.is_end:
            return node.value
        return None

    def starts_with(self, prefix):
        """Find all strings with this prefix. O(m + k) where k = results."""
        node = self._find_node(prefix)
        if not node:
            return []
        results = []
        self._collect(node, prefix, results)
        return results

    def _find_node(self, prefix):
        """Navigate to the node representing this prefix."""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def _collect(self, node, prefix, results):
        """Collect all complete words below this node."""
        if node.is_end:
            results.append((prefix, node.value))
        for char, child in node.children.items():
            self._collect(child, prefix + char, results)
```

## RouteMaster's Address Autocomplete

```python
class AddressAutocomplete:
    def __init__(self):
        self.trie = Trie()

    def index_address(self, address, package_count=0):
        """Add an address to the autocomplete index."""
        # Index the full address
        self.trie.insert(address.lower(), {"address": address, "deliveries": package_count})

        # Also index by street name (skip house number)
        parts = address.split(" ", 1)
        if len(parts) > 1:
            self.trie.insert(parts[1].lower(), {"address": address, "deliveries": package_count})

    def suggest(self, query, limit=10):
        """Get autocomplete suggestions. O(prefix_len + results)."""
        results = self.trie.starts_with(query.lower())
        # Sort by delivery frequency (most common addresses first)
        results.sort(key=lambda r: -r[1]["deliveries"])
        return [r[1]["address"] for r in results[:limit]]
```

```python
# Build index from delivery history
autocomplete = AddressAutocomplete()
autocomplete.index_address("123 Main Street", package_count=47)
autocomplete.index_address("123 Maple Avenue", package_count=12)
autocomplete.index_address("123 Market Road", package_count=89)
autocomplete.index_address("456 Main Street", package_count=23)
autocomplete.index_address("789 Oak Drive", package_count=5)

# Driver types "123 ma"
autocomplete.suggest("123 ma")
# → ["123 Market Road", "123 Main Street", "123 Maple Avenue"]
# (sorted by delivery frequency)

# Driver types "main"
autocomplete.suggest("main")
# → ["123 Main Street", "456 Main Street"]
```

## Complexity

| Operation | Time | Space |
|---|---|---|
| Insert | O(m) — m = key length | O(m) new nodes |
| Search (exact) | O(m) | — |
| Prefix search | O(m + k) — k = results | — |
| Delete | O(m) | — |
| Total space | O(N × m) worst case | N = number of keys |

Compare to alternatives:

| Approach | Prefix search | Insert | Space |
|---|---|---|---|
| Sorted array + binary search | O(log n + k) | O(n) — shift elements | O(n) |
| Hash table | Not possible | O(1) | O(n) |
| Trie | O(m + k) | O(m) | O(N × m) |

Tries win when prefix operations are frequent and keys share common prefixes (addresses, URLs, words).

## Compressed Trie (Radix Tree)

If a chain of nodes has no branching, compress it into a single node:

```
Before (standard trie for "romane", "romanus", "romulus"):
r → o → m → a → n → e*
                    → u → s*
            → u → l → u → s*

After (radix tree):
"rom" → "an" → "e"*
              → "us"*
       → "ulus"*
```

Fewer nodes, less memory. Same O(m) operations. Used in IP routing tables and HTTP routers.

## What You Learned

- **Trie** — tree where each edge is a character, paths form strings
- **Prefix search** — navigate to prefix node, collect all descendants
- **Shared prefixes** — common prefixes share nodes (memory efficient for similar strings)
- **Autocomplete** — prefix search + ranking by frequency
- **Radix tree** — compressed trie for space efficiency
- **When to use** — prefix matching, autocomplete, spell checking, IP routing

Marcus gets instant address suggestions. Typos decrease. Delivery accuracy improves.

But the address data needs more structure. Addresses have hierarchies: city → district → street → building. Packages have tracking hierarchies: batch → sub-batch → individual. You need a tree that supports ordered operations — finding ranges, predecessors, successors.

That's binary search trees. Chapter 9.

---

[← Chapter 7: Hash Tables](chapter-07-hash-tables.md) | [Chapter 9: Binary Search Trees →](chapter-09-bst.md)

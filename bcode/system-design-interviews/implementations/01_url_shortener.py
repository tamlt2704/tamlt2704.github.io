"""
URL Shortener — Core Implementation
=====================================
Demonstrates: Base62 encoding, collision handling, LRU cache layer.

In a real system:
- The counter would be a distributed ID generator (Snowflake, Redis INCR)
- The cache would be Redis
- The DB would be DynamoDB or Cassandra (key-value, read-heavy)
"""

import hashlib
import time
from collections import OrderedDict

# ─── Base62 Encoding ──────────────────────────────────────────────────────────

CHARSET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def base62_encode(num: int) -> str:
    """Convert an integer to a base62 string (used for short URLs)."""
    if num == 0:
        return CHARSET[0]
    result = []
    while num > 0:
        result.append(CHARSET[num % 62])
        num //= 62
    return ''.join(reversed(result))

def base62_decode(s: str) -> int:
    """Convert a base62 string back to an integer."""
    num = 0
    for char in s:
        num = num * 62 + CHARSET.index(char)
    return num


# ─── LRU Cache (simulates Redis) ─────────────────────────────────────────────

class LRUCache:
    """Simple LRU cache — in production this would be Redis."""

    def __init__(self, capacity: int = 10000):
        self.capacity = capacity
        self.cache: OrderedDict[str, str] = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> str | None:
        if key in self.cache:
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None

    def put(self, key: str, value: str) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


# ─── URL Shortener Service ────────────────────────────────────────────────────

class URLShortener:
    """
    URL shortening service with two strategies:
    1. Counter-based (guaranteed unique, sequential)
    2. Hash-based (deterministic, may collide)
    """

    def __init__(self, domain: str = "short.ly"):
        self.domain = domain
        self.counter = 100000  # Start at 100K for 3+ char codes
        self.url_to_code: dict[str, str] = {}  # Dedup: same URL → same code
        self.code_to_url: dict[str, str] = {}  # Lookup: code → original URL
        self.cache = LRUCache(capacity=1000)
        self.analytics: dict[str, int] = {}  # code → click count

    # ─── Strategy 1: Counter-Based (preferred) ────────────────────────────

    def shorten_counter(self, long_url: str) -> str:
        """Generate short URL using auto-incrementing counter + base62."""
        # Dedup: if we've seen this URL before, return existing code
        if long_url in self.url_to_code:
            return f"https://{self.domain}/{self.url_to_code[long_url]}"

        # Generate new code from counter
        self.counter += 1
        code = base62_encode(self.counter)

        # Store mappings
        self.url_to_code[long_url] = code
        self.code_to_url[code] = long_url
        self.cache.put(code, long_url)

        return f"https://{self.domain}/{code}"

    # ─── Strategy 2: Hash-Based ───────────────────────────────────────────

    def shorten_hash(self, long_url: str, length: int = 7) -> str:
        """Generate short URL using MD5 hash (first N chars of base62)."""
        if long_url in self.url_to_code:
            return f"https://{self.domain}/{self.url_to_code[long_url]}"

        # Hash the URL
        hash_bytes = hashlib.md5(long_url.encode()).digest()
        hash_int = int.from_bytes(hash_bytes[:8], 'big')
        code = base62_encode(hash_int)[:length]

        # Handle collision (rare but possible)
        original_code = code
        attempt = 0
        while code in self.code_to_url and self.code_to_url[code] != long_url:
            attempt += 1
            code = base62_encode(hash_int + attempt)[:length]
            if attempt > 10:
                # Fall back to counter-based
                return self.shorten_counter(long_url)

        self.url_to_code[long_url] = code
        self.code_to_url[code] = long_url
        self.cache.put(code, long_url)

        return f"https://{self.domain}/{code}"

    # ─── Redirect (Read Path) ─────────────────────────────────────────────

    def resolve(self, code: str) -> str | None:
        """Resolve a short code to the original URL (with caching)."""
        # Check cache first (hot path)
        cached = self.cache.get(code)
        if cached:
            self.analytics[code] = self.analytics.get(code, 0) + 1
            return cached

        # Cache miss — check DB
        url = self.code_to_url.get(code)
        if url:
            self.cache.put(code, url)
            self.analytics[code] = self.analytics.get(code, 0) + 1
            return url

        return None  # 404

    # ─── Analytics ────────────────────────────────────────────────────────

    def get_stats(self, code: str) -> dict:
        return {
            "code": code,
            "original_url": self.code_to_url.get(code),
            "clicks": self.analytics.get(code, 0),
        }


# ─── Demo ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    shortener = URLShortener()

    print("=== URL Shortener Demo ===\n")

    # Shorten some URLs
    urls = [
        "https://www.example.com/very/long/path/to/some/resource?param=value",
        "https://docs.python.org/3/library/collections.html#ordereddict-objects",
        "https://github.com/user/repo/blob/main/src/components/Button.tsx",
        "https://www.example.com/very/long/path/to/some/resource?param=value",  # Duplicate
    ]

    print("--- Counter-Based Strategy ---")
    for url in urls:
        short = shortener.shorten_counter(url)
        print(f"  {url[:50]}... → {short}")

    print(f"\n--- Resolving ---")
    code = "q0U"  # Will be one of our codes
    # Resolve the first URL's code
    first_code = shortener.url_to_code[urls[0]]
    for _ in range(5):
        resolved = shortener.resolve(first_code)
    stats = shortener.get_stats(first_code)
    print(f"  Code '{first_code}': {stats['clicks']} clicks → {stats['original_url'][:50]}...")

    print(f"\n--- Cache Performance ---")
    print(f"  Hit rate: {shortener.cache.hit_rate:.1%}")
    print(f"  Hits: {shortener.cache.hits}, Misses: {shortener.cache.misses}")

    print(f"\n--- Base62 Examples ---")
    for num in [1, 62, 3844, 100000, 999999999]:
        encoded = base62_encode(num)
        decoded = base62_decode(encoded)
        print(f"  {num:>12} → '{encoded}' → {decoded}")

    print(f"\n--- Hash-Based Strategy ---")
    shortener2 = URLShortener(domain="hash.ly")
    for url in urls[:3]:
        short = shortener2.shorten_hash(url)
        print(f"  {url[:50]}... → {short}")

# Chapter 14: Performance: Write Less, Run Faster

[← Chapter 13: Type System Tricks](chapter-13-typing.md) | [Chapter 15: Building a Mini-Framework →](chapter-15-framework.md)

---

## The Problem

FrameForge's model system is elegant. Users love the API. But benchmarks show it's 10x slower than hand-written classes:

```python
import time

# Hand-written class:
class UserManual:
    def __init__(self, name, age, email):
        self.name = name
        self.age = age
        self.email = email

# FrameForge model (with descriptors, validation, metaclass):
class UserModel(Model):
    name = StringField()
    age = IntField(min_value=0)
    email = StringField()

# Benchmark: create 1 million instances
start = time.perf_counter()
for i in range(1_000_000):
    UserManual(f"user_{i}", i % 100, f"user_{i}@dev.io")
manual_time = time.perf_counter() - start

start = time.perf_counter()
for i in range(1_000_000):
    UserModel(name=f"user_{i}", age=i % 100, email=f"user_{i}@dev.io")
model_time = time.perf_counter() - start

print(f"Manual: {manual_time:.2f}s")   # ~0.8s
print(f"Model:  {model_time:.2f}s")    # ~8.0s — 10x slower!
```

Vera: "Elegance doesn't excuse slowness. Find the bottlenecks. Fix them without sacrificing the API."

## __slots__: Faster Attribute Access, Less Memory

By default, Python objects store attributes in a `__dict__` (a hash table). `__slots__` replaces it with a fixed-size array:

```python
import sys

class WithDict:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class WithSlots:
    __slots__ = ('x', 'y', 'z')
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

# Memory comparison:
d = WithDict(1, 2, 3)
s = WithSlots(1, 2, 3)
print(sys.getsizeof(d) + sys.getsizeof(d.__dict__))  # ~152 bytes
print(sys.getsizeof(s))  # ~64 bytes — 58% less memory

# Speed comparison (attribute access):
import timeit
print(timeit.timeit('obj.x', globals={'obj': d}, number=10_000_000))  # ~0.45s
print(timeit.timeit('obj.x', globals={'obj': s}, number=10_000_000))  # ~0.35s — 22% faster
```

### Slots with Dataclasses

```python
from dataclasses import dataclass

@dataclass(slots=True)  # Python 3.10+
class Point:
    x: float
    y: float
    z: float

# Equivalent to manually defining __slots__ = ('x', 'y', 'z')
p = Point(1.0, 2.0, 3.0)
# p.w = 4.0  # AttributeError — can't add new attributes
```

## @lru_cache: Memoization

Cache expensive computations:

```python
from functools import lru_cache

# Without cache: O(2^n) — exponential
def fib_slow(n):
    if n < 2:
        return n
    return fib_slow(n - 1) + fib_slow(n - 2)

# With cache: O(n) — linear
@lru_cache(maxsize=128)
def fib_fast(n):
    if n < 2:
        return n
    return fib_fast(n - 1) + fib_fast(n - 2)

import timeit
# fib_slow(35): ~3.5 seconds
# fib_fast(35): ~0.00001 seconds
```

### cached_property: Compute Once Per Instance

```python
from functools import cached_property

class DataAnalysis:
    def __init__(self, data):
        self.data = data

    @cached_property
    def mean(self):
        """Computed once, then stored as instance attribute."""
        print("Computing mean...")
        return sum(self.data) / len(self.data)

    @cached_property
    def std_dev(self):
        """Also computed once."""
        print("Computing std_dev...")
        avg = self.mean
        variance = sum((x - avg) ** 2 for x in self.data) / len(self.data)
        return variance ** 0.5

analysis = DataAnalysis(range(1_000_000))
analysis.mean     # "Computing mean..." → 499999.5
analysis.mean     # No computation — returns cached value
```

## Avoiding Repeated Attribute Lookups

```python
import timeit

# Slow: repeated dot lookups in a loop
def slow_append():
    result = []
    for i in range(1_000_000):
        result.append(i)  # 'result.append' looked up 1M times
    return result

# Fast: local reference to the method
def fast_append():
    result = []
    append = result.append  # Look up once
    for i in range(1_000_000):
        append(i)  # Direct call — no attribute lookup
    return result

print(timeit.timeit(slow_append, number=10))  # ~0.65s
print(timeit.timeit(fast_append, number=10))  # ~0.45s — 30% faster
```

## struct and memoryview: Binary Data

For processing binary data, avoid creating Python objects:

```python
import struct
import array

# Parsing binary data — naive (creates many Python objects):
def parse_points_naive(data: bytes) -> list:
    points = []
    for i in range(0, len(data), 12):  # 3 floats × 4 bytes
        x, y, z = struct.unpack_from('fff', data, i)
        points.append((x, y, z))
    return points

# Faster: use memoryview to avoid copies
def parse_points_fast(data: bytes) -> array.array:
    # Interpret bytes directly as floats — zero copy
    view = memoryview(data).cast('f')
    return view  # Access elements without creating Python floats

# Even faster: use array module for homogeneous data
def create_float_array(n):
    # array.array stores raw C floats — 8x less memory than list of float
    return array.array('f', (i * 0.1 for i in range(n)))

import sys
float_list = [float(i) for i in range(10000)]
float_array = array.array('f', range(10000))
print(sys.getsizeof(float_list))   # ~85,176 bytes
print(sys.getsizeof(float_array))  # ~40,064 bytes — 53% less
```

## __length_hint__: Optimization for Iterators

```python
class ChunkedReader:
    """Iterator with a size hint for pre-allocation."""

    def __init__(self, data, chunk_size=1000):
        self.data = data
        self.chunk_size = chunk_size
        self.pos = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.pos >= len(self.data):
            raise StopIteration
        chunk = self.data[self.pos:self.pos + self.chunk_size]
        self.pos += self.chunk_size
        return chunk

    def __length_hint__(self):
        """Hint for list() and other consumers to pre-allocate."""
        remaining = len(self.data) - self.pos
        return (remaining + self.chunk_size - 1) // self.chunk_size

# list() uses __length_hint__ to pre-allocate the right size
reader = ChunkedReader(range(10000), chunk_size=100)
chunks = list(reader)  # Pre-allocates ~100 slots instead of growing dynamically
```

## Benchmarking: Before and After

```python
import timeit
from dataclasses import dataclass

# Version 1: Regular class with dict
class UserDict:
    def __init__(self, name, age, email):
        self.name = name
        self.age = age
        self.email = email

# Version 2: Dataclass with slots
@dataclass(slots=True)
class UserSlots:
    name: str
    age: int
    email: str

# Version 3: Named tuple (immutable)
from typing import NamedTuple
class UserTuple(NamedTuple):
    name: str
    age: int
    email: str

# Benchmark: creation
n = 1_000_000
print("Creation (1M instances):")
print(f"  dict class:  {timeit.timeit(lambda: UserDict('Alice', 30, 'a@b.c'), number=n):.3f}s")
print(f"  slots class: {timeit.timeit(lambda: UserSlots('Alice', 30, 'a@b.c'), number=n):.3f}s")
print(f"  namedtuple:  {timeit.timeit(lambda: UserTuple('Alice', 30, 'a@b.c'), number=n):.3f}s")

# Typical results:
#   dict class:  0.45s
#   slots class: 0.35s  (22% faster)
#   namedtuple:  0.30s  (33% faster)

# Benchmark: attribute access
obj_d = UserDict('Alice', 30, 'a@b.c')
obj_s = UserSlots('Alice', 30, 'a@b.c')
obj_t = UserTuple('Alice', 30, 'a@b.c')

print("\nAttribute access (10M reads):")
print(f"  dict class:  {timeit.timeit('obj.name', globals={'obj': obj_d}, number=10_000_000):.3f}s")
print(f"  slots class: {timeit.timeit('obj.name', globals={'obj': obj_s}, number=10_000_000):.3f}s")
print(f"  namedtuple:  {timeit.timeit('obj.name', globals={'obj': obj_t}, number=10_000_000):.3f}s")
```

## Making FrameForge Fast

Apply these techniques to the framework:

```python
from dataclasses import dataclass, field
from functools import lru_cache, cached_property

class OptimizedModel:
    """Base model with performance optimizations."""
    __slots__ = ()  # Subclasses define their own slots

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Auto-generate __slots__ from field annotations
        if '__annotations__' in cls.__dict__:
            cls.__slots__ = tuple(cls.__annotations__.keys())

    @classmethod
    @lru_cache(maxsize=None)
    def _get_fields(cls):
        """Cache field introspection — computed once per class."""
        return tuple(cls.__annotations__.keys())

    def __init__(self, **kwargs):
        for name in self._get_fields():
            object.__setattr__(self, name, kwargs.get(name))

    def __repr__(self):
        fields = ", ".join(
            f"{name}={getattr(self, name)!r}"
            for name in self._get_fields()
        )
        return f"{type(self).__name__}({fields})"

class User(OptimizedModel):
    name: str
    age: int
    email: str

# Now creation is fast (slots) and field lookup is cached
u = User(name="Alice", age=30, email="alice@dev.io")
```

## The Performance Hierarchy

From fastest to slowest for data containers:

```
1. C struct (via ctypes/cffi)     — fastest, no Python overhead
2. array.array / numpy array      — C-level storage, Python interface
3. NamedTuple                     — immutable, tuple-based
4. @dataclass(slots=True)         — mutable, slot-based
5. Regular class with __slots__   — mutable, slot-based
6. Regular class (dict-based)     — mutable, flexible
7. Class with descriptors         — validation overhead per access
8. Class with __getattribute__    — hook overhead on every access
```

Choose based on your needs: flexibility vs speed.

## What You Learned

- **`__slots__`** replaces `__dict__` with fixed-size storage — less memory, faster access
- **`@lru_cache`** memoizes function results — turns O(n) into O(1) for repeated calls
- **`@cached_property`** computes once per instance, stores as attribute
- **Local variable references** avoid repeated attribute lookups in hot loops
- **`struct` and `memoryview`** process binary data without creating Python objects
- **`__length_hint__`** helps consumers pre-allocate for iterators
- **Benchmark before optimizing** — measure, don't guess
- **The right data structure matters more than micro-optimizations**

## Key Insight

> Performance is about choosing the right tool: slots for memory, caching for computation, arrays for homogeneous data. Now you have all the pieces — decorators, descriptors, metaclasses, generators, closures, imports, AST, concurrency, typing, and performance. Time to combine them into a complete framework.

---

[Chapter 15: Building a Mini-Framework →](chapter-15-framework.md)

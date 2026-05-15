# Chapter 8: Generators and Lazy Pipelines

[← Chapter 7: Context Managers](chapter-07-context-managers.md) | [Chapter 9: Closures →](chapter-09-closures.md)

---

## The Problem

FrameForge's log analysis tool processes server logs. The naive approach:

```python
def analyze_errors(log_path):
    """Find all error entries, parse them, compute stats."""
    # Step 1: Read ALL lines into memory
    with open(log_path) as f:
        lines = f.readlines()  # 10GB file → 10GB in RAM → MemoryError

    # Step 2: Filter errors
    error_lines = []
    for line in lines:
        if "ERROR" in line:
            error_lines.append(line)

    # Step 3: Parse JSON
    import json
    parsed = []
    for line in error_lines:
        parsed.append(json.loads(line))

    # Step 4: Aggregate
    from collections import Counter
    errors_by_type = Counter(entry["error_type"] for entry in parsed)
    return errors_by_type
```

This loads the entire file into memory, then creates three more lists. A 10GB log file needs 40GB+ of RAM.

Vera: "Process one line at a time. Never hold more than one line in memory. Generators."

## The Core Idea

A generator is a function that uses `yield` instead of `return`. It produces values one at a time, on demand:

```python
def count_up(n):
    """Generate numbers 0 to n-1, one at a time."""
    i = 0
    while i < n:
        yield i  # Pause here, produce a value
        i += 1   # Resume here on next() call

gen = count_up(3)
next(gen)  # 0
next(gen)  # 1
next(gen)  # 2
next(gen)  # StopIteration
```

Key: the function's state is **suspended** at each `yield`. It doesn't run to completion — it produces values lazily.

## Solution: Lazy Pipeline

```python
import json
from collections import Counter

def read_lines(path):
    """Generator: yield one line at a time. Never loads full file."""
    with open(path) as f:
        for line in f:
            yield line.rstrip('\n')

def filter_errors(lines):
    """Generator: yield only lines containing ERROR."""
    for line in lines:
        if "ERROR" in line:
            yield line

def parse_json(lines):
    """Generator: parse each line as JSON."""
    for line in lines:
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue  # Skip malformed lines

def extract_field(entries, field):
    """Generator: extract a single field from each entry."""
    for entry in entries:
        if field in entry:
            yield entry[field]

# Compose the pipeline:
def analyze_errors(log_path):
    lines = read_lines(log_path)           # Generator — no data loaded
    errors = filter_errors(lines)           # Generator — no data loaded
    parsed = parse_json(errors)             # Generator — no data loaded
    types = extract_field(parsed, "error_type")  # Generator — no data loaded

    # Only NOW does data flow — one item at a time:
    return Counter(types)

# Processes 10GB file with ~1KB of memory
result = analyze_errors("/var/log/app.log")
```

Each generator holds one item in memory. The pipeline processes 10GB with constant memory usage.

## Generator Expressions

For simple transformations, use generator expressions (like list comprehensions, but lazy):

```python
# List comprehension — creates entire list in memory:
squares = [x**2 for x in range(1_000_000)]  # 8MB of memory

# Generator expression — produces values on demand:
squares = (x**2 for x in range(1_000_000))  # ~100 bytes of memory

# Use in functions that consume iterables:
total = sum(x**2 for x in range(1_000_000))  # No intermediate list
```

## Chaining Generators with itertools

```python
import itertools

def read_multiple_logs(paths):
    """Chain multiple log files into one stream."""
    return itertools.chain.from_iterable(
        read_lines(path) for path in paths
    )

def take(n, iterable):
    """Take first n items from any iterable."""
    return itertools.islice(iterable, n)

def batch(iterable, size):
    """Group items into batches of 'size'."""
    iterator = iter(iterable)
    while True:
        chunk = list(itertools.islice(iterator, size))
        if not chunk:
            break
        yield chunk

# Process logs in batches of 1000:
lines = read_lines("huge.log")
for chunk in batch(filter_errors(lines), 1000):
    send_to_elasticsearch(chunk)
```

## The yield from Statement

Delegate to another generator:

```python
def flatten(nested):
    """Flatten arbitrarily nested iterables."""
    for item in nested:
        if isinstance(item, (list, tuple, set)):
            yield from flatten(item)  # Delegate to recursive call
        else:
            yield item

list(flatten([1, [2, [3, 4]], [5, 6]]))
# [1, 2, 3, 4, 5, 6]

# Without yield from, you'd need:
def flatten_verbose(nested):
    for item in nested:
        if isinstance(item, (list, tuple, set)):
            for sub_item in flatten_verbose(item):
                yield sub_item
        else:
            yield item
```

## send(): Two-Way Communication

Generators can receive values via `send()`:

```python
def running_average():
    """Generator that computes a running average."""
    total = 0
    count = 0
    average = None
    while True:
        value = yield average  # Receive a value, yield the current average
        if value is not None:
            total += value
            count += 1
            average = total / count

avg = running_average()
next(avg)          # Prime the generator (returns None)
avg.send(10)       # 10.0
avg.send(20)       # 15.0
avg.send(30)       # 20.0
avg.send(15)       # 18.75
```

## A Complete Pipeline: Log Processor

```python
import json
import re
from datetime import datetime
from collections import Counter, defaultdict

def read_lines(path):
    with open(path) as f:
        for line in f:
            yield line.rstrip('\n')

def parse_log_entry(lines):
    """Parse structured log lines into dicts."""
    pattern = re.compile(
        r'\[(?P<timestamp>[\d\-T:]+)\] (?P<level>\w+) (?P<message>.*)'
    )
    for line in lines:
        match = pattern.match(line)
        if match:
            yield match.groupdict()

def filter_by_level(entries, level):
    for entry in entries:
        if entry['level'] == level:
            yield entry

def window(iterable, size):
    """Sliding window over an iterable."""
    from collections import deque
    it = iter(iterable)
    win = deque(itertools.islice(it, size), maxlen=size)
    if len(win) == size:
        yield tuple(win)
    for item in it:
        win.append(item)
        yield tuple(win)

def rate_detector(entries, threshold=10, window_seconds=60):
    """Detect error rate spikes."""
    recent = []
    for entry in entries:
        ts = datetime.fromisoformat(entry['timestamp'])
        recent.append(ts)
        # Remove entries outside the window
        cutoff = ts.timestamp() - window_seconds
        recent = [t for t in recent if t.timestamp() > cutoff]
        if len(recent) > threshold:
            yield {
                "alert": "high_error_rate",
                "count": len(recent),
                "timestamp": str(ts),
            }

# Compose:
pipeline = rate_detector(
    filter_by_level(
        parse_log_entry(
            read_lines("/var/log/app.log")
        ),
        level="ERROR"
    ),
    threshold=50,
    window_seconds=300
)

for alert in pipeline:
    send_alert(alert)
```

## Memory Comparison

```python
import sys

# List approach:
data_list = [x**2 for x in range(1_000_000)]
print(sys.getsizeof(data_list))  # ~8,448,728 bytes (8MB)

# Generator approach:
data_gen = (x**2 for x in range(1_000_000))
print(sys.getsizeof(data_gen))   # 200 bytes

# Same result, 40,000x less memory:
sum(data_list) == sum(data_gen)  # True
```

## Generator Gotchas

```python
# Gotcha 1: Generators are single-use
gen = (x for x in range(5))
list(gen)  # [0, 1, 2, 3, 4]
list(gen)  # [] — exhausted!

# Gotcha 2: Generators are lazy — side effects don't happen until consumed
def log_and_yield(items):
    for item in items:
        print(f"Processing {item}")  # Only prints when consumed
        yield item

gen = log_and_yield([1, 2, 3])  # Nothing printed yet!
list(gen)  # NOW it prints

# Gotcha 3: Can't get length without consuming
gen = (x for x in range(1000))
# len(gen)  # TypeError: object of type 'generator' has no len()
```

## What You Learned

- **Generators use `yield`** to produce values lazily, one at a time
- **Generator expressions** `(x for x in ...)` are lazy list comprehensions
- **Pipelines** chain generators — data flows through with constant memory
- **`yield from`** delegates to another generator
- **`send()`** enables two-way communication with a generator
- **`itertools`** provides building blocks: `chain`, `islice`, `groupby`, `tee`
- **Memory**: generators use bytes where lists use megabytes
- **Gotcha**: generators are single-use and have no length

## Key Insight

> Generators produce values lazily. But what about producing *functions* lazily? What if you need 20 similar functions that differ only in their parameters? You could write 20 functions, or you could write one factory that produces them. That's closures.

---

[Chapter 9: Closures and Factory Functions →](chapter-09-closures.md)

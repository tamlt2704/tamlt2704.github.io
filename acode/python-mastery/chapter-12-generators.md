# Chapter 12: "Process 10,000 Messages"

[← Chapter 11: Decorators](chapter-11-decorators.md) | [Chapter 13: Async →](chapter-13-async.md)

---

## The Crash

Tuesday. The bot dies. But this time it's not bad input — it's memory:

```
MemoryError: Unable to allocate 3.8 GiB for array
```

Leo checks the logs:

> "Someone ran the `backlog` command. It tried to load 10,000 messages into a list, process them all, then return results. The server has 2GB of RAM. Do the math."

Marcus (in the PR review): "Use generators. Process one message at a time. Never load everything into memory."

---

## The Problem: Eager Loading

```python
# ❌ Loads ALL messages into memory at once
def get_all_messages(channels: list[str]) -> list[dict]:
    messages = []
    for channel in channels:
        page = fetch_page(channel)
        while page:
            messages.extend(page["messages"])  # growing list!
            page = fetch_page(channel, cursor=page.get("next_cursor"))
    return messages  # 10,000 messages × ~2KB each = 20MB minimum

# Then we process them all
all_msgs = get_all_messages(channels)  # 💥 MemoryError
results = [process(msg) for msg in all_msgs]  # doubles the memory
```

---

## Generators: Lazy Sequences

A generator produces values one at a time, on demand:

```python
# ✅ Yields one message at a time — constant memory
def get_all_messages(channels: list[str]):
    """Generate messages lazily — one at a time."""
    for channel in channels:
        page = fetch_page(channel)
        while page:
            for msg in page["messages"]:
                yield msg  # produce one, pause, wait for next request
            page = fetch_page(channel, cursor=page.get("next_cursor"))


# Process one at a time — never more than one message in memory
for msg in get_all_messages(channels):
    process(msg)
```

### How yield Works

```python
def countdown(n: int):
    print("Starting countdown")
    while n > 0:
        yield n       # pause here, return n
        n -= 1        # resume here on next() call
    print("Done!")

gen = countdown(3)
print(next(gen))  # "Starting countdown" → 3
print(next(gen))  # 2
print(next(gen))  # 1
print(next(gen))  # "Done!" → StopIteration
```

The function **pauses** at each `yield` and **resumes** when the next value is requested.

---

## Generator Expressions

Like list comprehensions, but lazy:

```python
# List comprehension — builds entire list in memory
squares = [x**2 for x in range(1_000_000)]  # 8MB of memory

# Generator expression — computes on demand
squares = (x**2 for x in range(1_000_000))  # ~100 bytes

# Use in functions that accept iterables
total = sum(x**2 for x in range(1_000_000))  # no list created
largest = max(len(msg["text"]) for msg in messages)
```

### When to Use Which

| Syntax | Memory | Use When |
|---|---|---|
| `[x for x in ...]` | All at once | Need random access, len(), multiple passes |
| `(x for x in ...)` | One at a time | Single pass, large data, piping to another function |

---

## Building a Processing Pipeline

```python
def read_messages(path: str):
    """Read messages from a log file, one at a time."""
    with open(path) as f:
        for line in f:
            yield json.loads(line)


def filter_commands(messages):
    """Keep only messages that are commands."""
    for msg in messages:
        if msg.get("text", "").startswith("/"):
            yield msg


def extract_metrics(messages):
    """Extract timing data from command messages."""
    for msg in messages:
        yield {
            "command": msg["text"].split()[0],
            "user": msg["user"],
            "timestamp": msg["ts"],
        }


def batch(iterable, size: int):
    """Group items into batches of `size`."""
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch


# Pipeline — nothing executes until we iterate
messages = read_messages("messages.jsonl")      # lazy
commands = filter_commands(messages)             # lazy
metrics = extract_metrics(commands)             # lazy
batches = batch(metrics, size=100)              # lazy

# NOW it executes — one batch at a time
for metric_batch in batches:
    save_to_database(metric_batch)
```

Memory usage: constant. Could process 10 million messages without breaking a sweat.

---

## yield from: Delegating to Sub-generators

```python
def get_channel_messages(channel: str):
    """Get all messages from one channel (paginated)."""
    cursor = None
    while True:
        page = fetch_page(channel, cursor=cursor)
        yield from page["messages"]  # yield each message from the page
        cursor = page.get("next_cursor")
        if not cursor:
            break


def get_all_messages(channels: list[str]):
    """Get messages from all channels."""
    for channel in channels:
        yield from get_channel_messages(channel)
```

`yield from` flattens nested generators — cleaner than a for loop with yield.

---

## itertools: The Generator Toolkit

```python
import itertools

# Chain multiple iterables
all_messages = itertools.chain(
    get_messages("#support"),
    get_messages("#engineering"),
    get_messages("#random"),
)

# Take first N items
sample = itertools.islice(get_all_messages(), 10)

# Group by key
messages = sorted(messages, key=lambda m: m["user"])
for user, user_msgs in itertools.groupby(messages, key=lambda m: m["user"]):
    print(f"{user}: {sum(1 for _ in user_msgs)} messages")

# Filter
errors = filter(lambda m: "error" in m.get("text", "").lower(), messages)

# Accumulate (running total)
daily_counts = [5, 12, 3, 8, 15]
running_total = itertools.accumulate(daily_counts)
# 5, 17, 20, 28, 43

# Product (all combinations)
priorities = ["low", "medium", "high"]
statuses = ["open", "closed"]
for p, s in itertools.product(priorities, statuses):
    print(f"{p}-{s}")  # low-open, low-closed, medium-open, ...

# Repeat and cycle
retry_delays = itertools.islice(
    itertools.accumulate(itertools.repeat(2), lambda a, b: a * b),
    5
)
# 2, 4, 8, 16, 32 (exponential backoff)
```

---

## The Iterator Protocol

Under the hood, generators implement the iterator protocol:

```python
class MessageIterator:
    """Manual iterator — same behavior as a generator."""
    
    def __init__(self, channel: str, page_size: int = 100):
        self.channel = channel
        self.page_size = page_size
        self.cursor = None
        self.buffer: list[dict] = []
        self.exhausted = False
    
    def __iter__(self):
        return self
    
    def __next__(self) -> dict:
        if not self.buffer:
            if self.exhausted:
                raise StopIteration
            self._fetch_next_page()
        if not self.buffer:
            raise StopIteration
        return self.buffer.pop(0)
    
    def _fetch_next_page(self):
        page = fetch_page(self.channel, cursor=self.cursor, limit=self.page_size)
        self.buffer = page.get("messages", [])
        self.cursor = page.get("next_cursor")
        if not self.cursor:
            self.exhausted = True


# Usage — same as a generator
for msg in MessageIterator("#support"):
    process(msg)
```

The generator version is much simpler — use classes only when you need extra state or methods.

---

## The Fixed Backlog Command

```python
import itertools
from typing import Generator


def process_backlog(
    channels: list[str],
    limit: int | None = None,
    batch_size: int = 50,
) -> Generator[dict, None, None]:
    """Process message backlog lazily."""
    
    # Build the pipeline
    messages = get_all_messages(channels)
    
    # Apply limit if specified
    if limit:
        messages = itertools.islice(messages, limit)
    
    # Process in batches
    batch: list[dict] = []
    for msg in messages:
        result = process_message(msg)
        batch.append(result)
        
        if len(batch) >= batch_size:
            save_batch(batch)
            yield {"processed": len(batch), "status": "in_progress"}
            batch = []
    
    # Final batch
    if batch:
        save_batch(batch)
        yield {"processed": len(batch), "status": "complete"}


# The handler streams progress updates
@logged_handler
def handle_backlog(msg: dict) -> str:
    channels = msg.get("channels", ["#support"])
    total = 0
    
    for progress in process_backlog(channels, limit=10_000):
        total += progress["processed"]
    
    return f"✅ Processed {total} messages from backlog"
```

Memory usage: ~50 messages at a time, regardless of total backlog size.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ Syntax
────────────────────────────────┼──────────────────────────────────────
Generator function              │ def gen(): yield value
Generator expression            │ (x for x in iterable)
Delegate to sub-generator       │ yield from other_gen()
Next value                      │ next(gen)
────────────────────────────────┼──────────────────────────────────────
itertools.chain(a, b)           │ Concatenate iterables
itertools.islice(gen, n)        │ Take first n items
itertools.groupby(it, key)      │ Group consecutive items
itertools.product(a, b)         │ Cartesian product
itertools.accumulate(it)        │ Running totals
────────────────────────────────┼──────────────────────────────────────
Iterator protocol               │ __iter__() + __next__()
StopIteration                   │ Signals end of iteration
────────────────────────────────┼──────────────────────────────────────
Memory: list                    │ O(n) — all items at once
Memory: generator               │ O(1) — one item at a time
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The backlog processes smoothly now — constant memory, streaming results. But there's a new problem: the bot handles Slack events one at a time. When 50 users send commands simultaneously, they queue up. Response time goes from 200ms to 10 seconds. Leo: "We need concurrency. Learn async."

---

[← Chapter 11: Decorators](chapter-11-decorators.md) | [Chapter 13: Async →](chapter-13-async.md)

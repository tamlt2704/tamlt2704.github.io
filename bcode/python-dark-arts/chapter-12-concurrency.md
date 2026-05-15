# Chapter 12: Concurrency Patterns

[← Chapter 11: AST Manipulation](chapter-11-ast.md) | [Chapter 13: Type System Tricks →](chapter-13-typing.md)

---

## The Problem

FrameForge's data sync service fetches data from 100 external APIs. Each call takes ~200ms. Sequential execution:

```python
import requests
import time

ENDPOINTS = [f"https://api.example.com/data/{i}" for i in range(100)]

def fetch_all_sequential():
    """Fetch 100 endpoints one at a time."""
    results = []
    for url in ENDPOINTS:
        response = requests.get(url)  # 200ms each
        results.append(response.json())
    return results

start = time.perf_counter()
data = fetch_all_sequential()
elapsed = time.perf_counter() - start
# 100 × 200ms = 20 seconds. Unacceptable.
```

20 seconds for I/O-bound work where the CPU is idle 99% of the time.

Vera: "These are independent requests. Run them concurrently. 20 seconds becomes 0.5 seconds."

## asyncio: Cooperative Multitasking

```python
import asyncio
import aiohttp
import time

async def fetch_one(session, url):
    """Fetch a single URL asynchronously."""
    async with session.get(url) as response:
        return await response.json()

async def fetch_all_async():
    """Fetch 100 endpoints concurrently."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_one(session, url) for url in ENDPOINTS]
        results = await asyncio.gather(*tasks)
        return results

start = time.perf_counter()
data = asyncio.run(fetch_all_async())
elapsed = time.perf_counter() - start
# ~0.3 seconds — all requests run concurrently
```

100 requests in the time of 1-2 requests. The event loop switches between tasks at each `await`.

## How async/await Works

```python
async def example():
    print("Start")
    await asyncio.sleep(1)  # Yield control to event loop
    print("After 1 second")
    await asyncio.sleep(1)  # Yield control again
    print("After 2 seconds")

# 'await' is where the magic happens:
# - The function suspends
# - The event loop runs other tasks
# - When the awaited operation completes, the function resumes
```

Key insight: `await` is a **suspension point**. The event loop can run other coroutines while this one waits for I/O.

## TaskGroup: Structured Concurrency (Python 3.11+)

```python
async def fetch_with_taskgroup():
    """Structured concurrency — all tasks complete or all fail."""
    results = []

    async with aiohttp.ClientSession() as session:
        async with asyncio.TaskGroup() as tg:
            for url in ENDPOINTS:
                task = tg.create_task(fetch_one(session, url))
                results.append(task)

    # All tasks guaranteed complete here
    return [task.result() for task in results]
```

`TaskGroup` is better than `gather()` because:
- If one task fails, all others are cancelled
- Exceptions are collected into an `ExceptionGroup`
- No orphaned tasks

## Rate-Limited Concurrent Requests

100 concurrent requests might overwhelm the target API. Use a semaphore:

```python
async def fetch_rate_limited(urls, max_concurrent=10):
    """Fetch URLs with a concurrency limit."""
    semaphore = asyncio.Semaphore(max_concurrent)
    results = []

    async def fetch_with_limit(session, url):
        async with semaphore:  # Only N tasks run simultaneously
            async with session.get(url) as response:
                return await response.json()

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_with_limit(session, url) for url in urls]
        results = await asyncio.gather(*tasks)

    return results

# At most 10 requests in flight at any time:
data = asyncio.run(fetch_rate_limited(ENDPOINTS, max_concurrent=10))
```

## Async Generators: Streaming Results

Don't wait for all 100 to finish — process results as they arrive:

```python
async def fetch_stream(urls, max_concurrent=10):
    """Yield results as they complete, not all at once."""
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_one(session, url):
        async with semaphore:
            async with session.get(url) as response:
                return url, await response.json()

    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(fetch_one(session, url)) for url in urls]
        for coro in asyncio.as_completed(tasks):
            url, data = await coro
            yield url, data  # Process immediately, don't wait for all

# Usage:
async def process_stream():
    async for url, data in fetch_stream(ENDPOINTS):
        print(f"Got result from {url}: {len(data)} items")
        # Process each result as it arrives
```

## concurrent.futures: Thread/Process Pools

For code that can't use async (blocking libraries, CPU-bound work):

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import requests

def fetch_sync(url):
    """Regular synchronous fetch."""
    return requests.get(url).json()

# Thread pool for I/O-bound work:
def fetch_all_threaded(urls, max_workers=20):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_sync, url): url for url in urls}
        for future in as_completed(futures):
            url = futures[future]
            try:
                data = future.result()
                results.append((url, data))
            except Exception as e:
                print(f"Failed {url}: {e}")
    return results

# Process pool for CPU-bound work:
def compute_heavy(data):
    """CPU-intensive computation."""
    return sum(x**2 for x in range(1_000_000))

def parallel_compute(items):
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(compute_heavy, items))
    return results
```

## Mixing async and sync: run_in_executor

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Run blocking code inside an async function:
async def fetch_with_blocking_library():
    loop = asyncio.get_event_loop()

    # Run requests.get in a thread pool (it's blocking)
    result = await loop.run_in_executor(
        None,  # Default executor
        requests.get,
        "https://api.example.com/data"
    )
    return result.json()
```

## Async Pipeline: Producer-Consumer

```python
async def producer(queue, urls):
    """Fetch URLs and put results in queue."""
    async with aiohttp.ClientSession() as session:
        for url in urls:
            async with session.get(url) as response:
                data = await response.json()
                await queue.put(data)
    await queue.put(None)  # Sentinel: done producing

async def consumer(queue, name):
    """Process items from queue."""
    while True:
        item = await queue.get()
        if item is None:
            await queue.put(None)  # Pass sentinel to other consumers
            break
        # Process the item
        print(f"[{name}] Processing: {item.get('id', '?')}")
        await asyncio.sleep(0.01)  # Simulate processing

async def pipeline():
    queue = asyncio.Queue(maxsize=50)

    # 1 producer, 3 consumers
    await asyncio.gather(
        producer(queue, ENDPOINTS),
        consumer(queue, "worker-1"),
        consumer(queue, "worker-2"),
        consumer(queue, "worker-3"),
    )

asyncio.run(pipeline())
```

## Timeouts and Cancellation

```python
async def fetch_with_timeout(url, timeout=5.0):
    """Fetch with a timeout — don't wait forever."""
    async with aiohttp.ClientSession() as session:
        try:
            async with asyncio.timeout(timeout):
                async with session.get(url) as response:
                    return await response.json()
        except asyncio.TimeoutError:
            return {"error": f"Timeout after {timeout}s", "url": url}

# Cancel a long-running task:
async def cancellable_work():
    task = asyncio.create_task(long_running_operation())
    await asyncio.sleep(5)
    if not task.done():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            print("Task was cancelled")
```

## When to Use What

```python
# I/O-bound (network, disk) + can use async libraries:
#   → asyncio + aiohttp/asyncpg/etc.

# I/O-bound + must use blocking libraries (requests, psycopg2):
#   → ThreadPoolExecutor or loop.run_in_executor()

# CPU-bound (number crunching, image processing):
#   → ProcessPoolExecutor (bypasses GIL)

# Simple parallelism without async complexity:
#   → concurrent.futures.ThreadPoolExecutor
```

## What You Learned

- **`asyncio`** is cooperative multitasking — `await` is the suspension point
- **`asyncio.gather()`** runs multiple coroutines concurrently
- **`TaskGroup`** (3.11+) provides structured concurrency with proper cancellation
- **Semaphores** limit concurrency to avoid overwhelming resources
- **`asyncio.as_completed()`** processes results as they arrive
- **Async generators** (`async for`) stream results without buffering all in memory
- **`ThreadPoolExecutor`** for I/O-bound blocking code
- **`ProcessPoolExecutor`** for CPU-bound work (bypasses GIL)
- **`run_in_executor()`** bridges blocking code into async context

## Key Insight

> Concurrency handles the "too slow" problem for I/O. But what about making your metaprogramming code itself smarter? What if type annotations could drive runtime behavior — generating validation, serialization, and documentation from `def foo(x: int, y: str) -> bool`? That's type system tricks.

---

[Chapter 13: Type System Tricks →](chapter-13-typing.md)

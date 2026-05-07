# Chapter 13: "Handle 50 Requests at Once"

[← Chapter 12: Generators](chapter-12-generators.md) | [Chapter 14: CLI →](chapter-14-cli.md)

---

## The Bottleneck

Friday afternoon. The #support channel explodes — a feature launch brought 50 users asking questions simultaneously. The bot responds to them one by one:

```
User 1 asks → bot calls Slack API (200ms) → responds
User 2 asks → bot calls Slack API (200ms) → responds
...
User 50 asks → bot calls Slack API (200ms) → responds
```

Total time: 10 seconds. User 50 waits 10 seconds for a response.

Leo: "The bot spends 95% of its time waiting for network responses. It should handle all 50 at once. Use async."

---

## Sync vs Async: The Restaurant Analogy

**Synchronous** (one waiter, one table at a time):
- Take order from table 1 → wait in kitchen → deliver food → move to table 2

**Asynchronous** (one waiter, many tables):
- Take order from table 1 → while kitchen cooks, take order from table 2 → deliver food to table 1 when ready → ...

The waiter (your code) doesn't sit idle while waiting for the kitchen (network I/O).

---

## async/await: The Basics

```python
import asyncio


# Regular function — blocks while sleeping
def fetch_sync(url: str) -> str:
    time.sleep(1)  # blocks the entire program
    return f"Response from {url}"


# Async function (coroutine) — yields control while waiting
async def fetch_async(url: str) -> str:
    await asyncio.sleep(1)  # yields control, other tasks can run
    return f"Response from {url}"


# Running async code
async def main():
    result = await fetch_async("https://slack.com/api/status")
    print(result)

asyncio.run(main())
```

### Key Rules

```python
# 1. async def creates a coroutine
async def my_function():
    ...

# 2. await pauses the coroutine (only inside async def)
result = await some_async_operation()

# 3. You can't call await in regular functions
def regular():
    await something()  # ❌ SyntaxError

# 4. Calling an async function returns a coroutine object (doesn't run it)
coro = fetch_async("url")  # doesn't execute!
result = await coro         # NOW it executes
```

---

## Concurrency with gather

```python
import asyncio
import aiohttp


async def fetch_user(session: aiohttp.ClientSession, user_id: str) -> dict:
    """Fetch a single user from Slack API."""
    async with session.get(
        f"https://slack.com/api/users.info",
        params={"user": user_id}
    ) as response:
        data = await response.json()
        return data["user"]


async def fetch_all_users(user_ids: list[str]) -> list[dict]:
    """Fetch all users concurrently."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_user(session, uid) for uid in user_ids]
        results = await asyncio.gather(*tasks)
        return list(results)


# 50 users fetched concurrently — ~200ms total instead of 10s
async def main():
    user_ids = ["U001", "U002", ..., "U050"]
    users = await fetch_all_users(user_ids)
    print(f"Fetched {len(users)} users")

asyncio.run(main())
```

### gather vs sequential

```python
# Sequential: 50 × 200ms = 10 seconds
async def sequential():
    results = []
    for uid in user_ids:
        result = await fetch_user(session, uid)
        results.append(result)
    return results

# Concurrent: max(200ms each) ≈ 200ms total
async def concurrent():
    tasks = [fetch_user(session, uid) for uid in user_ids]
    return await asyncio.gather(*tasks)
```

---

## aiohttp: Async HTTP Client

```bash
pip install aiohttp
```

```python
import aiohttp


async def call_slack_api(method: str, payload: dict) -> dict:
    """Make an async Slack API call."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"https://slack.com/api/{method}",
            json=payload,
            headers={"Authorization": f"Bearer {TOKEN}"},
            timeout=aiohttp.ClientTimeout(total=10),
        ) as response:
            response.raise_for_status()
            return await response.json()


async def send_message(channel: str, text: str) -> dict:
    return await call_slack_api("chat.postMessage", {
        "channel": channel,
        "text": text,
    })
```

### Reusing Sessions (Important for Performance)

```python
class AsyncSlackClient:
    """Reuse a single session for all requests."""
    
    def __init__(self, token: str):
        self.token = token
        self._session: aiohttp.ClientSession | None = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                base_url="https://slack.com/api",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=aiohttp.ClientTimeout(total=30),
            )
        return self._session
    
    async def post(self, method: str, payload: dict) -> dict:
        session = await self._get_session()
        async with session.post(f"/{method}", json=payload) as resp:
            resp.raise_for_status()
            return await resp.json()
    
    async def close(self):
        if self._session:
            await self._session.close()
```

---

## Error Handling in Async Code

```python
async def fetch_with_retry(
    session: aiohttp.ClientSession,
    url: str,
    max_retries: int = 3,
) -> dict:
    """Fetch with exponential backoff."""
    for attempt in range(1, max_retries + 1):
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if attempt == max_retries:
                raise
            delay = 2 ** attempt
            print(f"Attempt {attempt} failed: {e}. Retrying in {delay}s...")
            await asyncio.sleep(delay)


# Handle partial failures with gather
async def fetch_many(urls: list[str]) -> list[dict | None]:
    """Fetch many URLs, returning None for failures."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_with_retry(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        processed = []
        for result in results:
            if isinstance(result, Exception):
                print(f"Failed: {result}")
                processed.append(None)
            else:
                processed.append(result)
        return processed
```

---

## asyncio.TaskGroup (Python 3.11+)

```python
async def process_events(events: list[dict]) -> list[str]:
    """Process events with structured concurrency."""
    results = []
    
    async with asyncio.TaskGroup() as tg:
        tasks = [
            tg.create_task(handle_event(event))
            for event in events
        ]
    
    # All tasks complete (or one raises → all cancelled)
    return [task.result() for task in tasks]
```

TaskGroup is safer than gather — if one task fails, all others are cancelled.

---

## Async Generators

Combine generators with async:

```python
async def stream_messages(channel: str):
    """Async generator — yield messages as they arrive."""
    cursor = None
    while True:
        page = await fetch_page_async(channel, cursor=cursor)
        for msg in page["messages"]:
            yield msg
        cursor = page.get("next_cursor")
        if not cursor:
            break


# Consume with async for
async def process_stream():
    async for msg in stream_messages("#support"):
        await handle_message(msg)
```

---

## Semaphores: Limiting Concurrency

Don't overwhelm the Slack API with 1000 concurrent requests:

```python
async def fetch_all_controlled(
    user_ids: list[str],
    max_concurrent: int = 10,
) -> list[dict]:
    """Fetch users with concurrency limit."""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def fetch_one(uid: str) -> dict:
        async with semaphore:  # at most 10 concurrent
            return await fetch_user(session, uid)
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_one(uid) for uid in user_ids]
        return await asyncio.gather(*tasks)
```

---

## The Async Bot

```python
import asyncio
import aiohttp
from dataclasses import dataclass


@dataclass
class AsyncBot:
    token: str
    max_concurrent: int = 20
    
    async def run(self):
        """Main event loop — handle messages concurrently."""
        async with aiohttp.ClientSession() as session:
            self.session = session
            self.semaphore = asyncio.Semaphore(self.max_concurrent)
            
            while True:
                events = await self._poll_events()
                if events:
                    await self._handle_events(events)
                await asyncio.sleep(1)
    
    async def _poll_events(self) -> list[dict]:
        """Poll Slack for new events."""
        try:
            async with self.session.get(
                "https://slack.com/api/rtm.connect",
                headers={"Authorization": f"Bearer {self.token}"},
            ) as resp:
                data = await resp.json()
                return data.get("events", [])
        except aiohttp.ClientError:
            return []
    
    async def _handle_events(self, events: list[dict]):
        """Handle all events concurrently."""
        async with asyncio.TaskGroup() as tg:
            for event in events:
                tg.create_task(self._handle_one(event))
    
    async def _handle_one(self, event: dict):
        """Handle a single event with rate limiting."""
        async with self.semaphore:
            command = event.get("text", "").split()[0] if event.get("text") else None
            if command in self.handlers:
                response = await self.handlers[command](event)
                await self._send_response(event["channel"], response)


# Run the bot
async def main():
    bot = AsyncBot(token="xoxb-...")
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ Syntax
────────────────────────────────┼──────────────────────────────────────
Define coroutine                │ async def func():
Await a coroutine               │ result = await coro()
Run async code                  │ asyncio.run(main())
────────────────────────────────┼──────────────────────────────────────
Concurrent execution            │ await asyncio.gather(*tasks)
Structured concurrency          │ async with asyncio.TaskGroup() as tg
Limit concurrency               │ asyncio.Semaphore(n)
Sleep without blocking          │ await asyncio.sleep(n)
────────────────────────────────┼──────────────────────────────────────
HTTP client                     │ aiohttp.ClientSession()
Async context manager           │ async with session.get(url) as r:
Async generator                 │ async def gen(): yield value
Async iteration                 │ async for item in gen():
────────────────────────────────┼──────────────────────────────────────
Error handling                  │ return_exceptions=True in gather
Timeout                         │ asyncio.timeout(seconds)
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The bot handles 50 concurrent requests in 200ms. Leo is impressed. Then Dani (the designer) pings you: "I'm tired of managing the bot through Slack commands. Can you build a CLI tool? Something pretty, with colors and progress bars?" Time to build a command-line interface.

---

[← Chapter 12: Generators](chapter-12-generators.md) | [Chapter 14: CLI →](chapter-14-cli.md)

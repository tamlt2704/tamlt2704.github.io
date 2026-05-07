# Chapter 4: The Matchmaking Queue — Lists and Reliable Queues

[← Chapter 3: Hashes and Caching](chapter-03-hashes-caching.md) | [Chapter 5: Chat Messages →](chapter-05-pubsub-streams.md)

---

## The Problem

Players click "Find Match" and wait. The current system:
1. Writes a row to `matchmaking_queue` in Postgres
2. A background worker polls the table every 5 seconds
3. When two players are found, it creates a match and deletes the rows

Average wait time: 15 seconds. Peak: 45 seconds. Players rage-quit before the game even starts.

The bottleneck is polling. Every 5 seconds, the worker runs `SELECT * FROM matchmaking_queue ORDER BY created_at LIMIT 2`. Between polls, players sit idle. And when 500 players queue simultaneously, the worker pairs them two at a time — 250 iterations, 5 seconds apart.

Marta: "Redis lists. BRPOP. It blocks until something arrives. No polling. No delay."

## Lists: The Simplest Queue

A Redis list is a doubly-linked list of strings. Push to one end, pop from the other. FIFO queue in two commands.

```redis
# Producer: player joins queue
LPUSH matchmaking:queue "player:alice"
LPUSH matchmaking:queue "player:bob"
LPUSH matchmaking:queue "player:charlie"

# Consumer: matchmaker takes players
RPOP matchmaking:queue
# "player:alice" (first in, first out)

RPOP matchmaking:queue
# "player:bob"
```

`LPUSH` adds to the left (head). `RPOP` removes from the right (tail). Together: FIFO.

### BRPOP: Blocking Pop

`RPOP` returns nil if the list is empty. You'd have to poll. `BRPOP` blocks until an item arrives:

```redis
BRPOP matchmaking:queue 30
# Blocks for up to 30 seconds
# Returns immediately when an item is pushed
# 1) "matchmaking:queue"
# 2) "player:alice"
```

The matchmaker doesn't poll. It sleeps until a player arrives. Zero CPU usage while waiting. Instant response when someone queues.

## The Matchmaker

```python
import redis
import json
import uuid

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

QUEUE_KEY = "matchmaking:queue"

def join_queue(player_id: str, skill_rating: int):
    """Player wants to find a match."""
    entry = json.dumps({"player_id": player_id, "skill": skill_rating, "queued_at": time.time()})
    r.lpush(QUEUE_KEY, entry)

def matchmaker_loop():
    """Continuously pair players. Runs as a dedicated worker."""
    while True:
        # Block until a player arrives (or 5s timeout)
        result = r.brpop(QUEUE_KEY, timeout=5)
        if not result:
            continue  # Timeout — check health, loop again

        _, first_raw = result
        first = json.loads(first_raw)

        # Wait for a second player (up to 10s)
        result = r.brpop(QUEUE_KEY, timeout=10)
        if not result:
            # No opponent found — re-queue the first player
            r.lpush(QUEUE_KEY, first_raw)
            continue

        _, second_raw = result
        second = json.loads(second_raw)

        # Create match
        match_id = str(uuid.uuid4())
        create_match(match_id, first["player_id"], second["player_id"])
```

Average wait time drops from 15 seconds to under 1 second. Players get matched the instant a second player joins.

## The Lost Message Problem

The matchmaker pops a player from the queue, then crashes before creating the match. That player is gone — popped from Redis, never matched, never re-queued. They wait forever.

```
1. BRPOP → "alice"     ← alice removed from queue
2. BRPOP → "bob"       ← bob removed from queue
3. create_match(...)   ← CRASH HERE
4. alice and bob are lost forever
```

This is the fundamental problem with simple RPOP queues: the message is deleted before it's processed.

### Fix: RPOPLPUSH (Reliable Queue Pattern)

Pop from the main queue and simultaneously push to a "processing" list. If the worker crashes, items in the processing list can be recovered.

```redis
# Atomic: pop from queue, push to processing
LMOVE matchmaking:queue matchmaking:processing RIGHT LEFT
# Returns the item AND moves it to the processing list

# After successful match creation:
LREM matchmaking:processing 1 "player:alice"
# Remove from processing (acknowledged)
```

In Python:

```python
def reliable_matchmaker_loop():
    while True:
        # Atomically move from queue to processing
        first_raw = r.lmove(QUEUE_KEY, PROCESSING_KEY, "RIGHT", "LEFT")
        if not first_raw:
            time.sleep(0.1)
            continue

        first = json.loads(first_raw)

        second_raw = r.lmove(QUEUE_KEY, PROCESSING_KEY, "RIGHT", "LEFT")
        if not second_raw:
            # No second player — move first back to queue
            r.lmove(PROCESSING_KEY, QUEUE_KEY, "RIGHT", "LEFT")
            time.sleep(1)
            continue

        second = json.loads(second_raw)

        try:
            match_id = create_match(first["player_id"], second["player_id"])
            # Success — remove from processing
            r.lrem(PROCESSING_KEY, 1, first_raw)
            r.lrem(PROCESSING_KEY, 1, second_raw)
        except Exception:
            # Failed — move back to queue for retry
            r.lmove(PROCESSING_KEY, QUEUE_KEY, "RIGHT", "LEFT")
            r.lmove(PROCESSING_KEY, QUEUE_KEY, "RIGHT", "LEFT")
```

### Recovery Worker

A separate process checks the processing list for items that have been there too long (worker crashed):

```python
def recovery_worker():
    """Runs every 30 seconds. Recovers stuck items."""
    while True:
        items = r.lrange(PROCESSING_KEY, 0, -1)
        for item_raw in items:
            item = json.loads(item_raw)
            if time.time() - item["queued_at"] > 60:  # Stuck for >60s
                r.lmove(PROCESSING_KEY, QUEUE_KEY, "RIGHT", "LEFT")
                log.warning(f"Recovered stuck player: {item['player_id']}")
        time.sleep(30)
```

No more lost players.

## Skill-Based Matchmaking

The simple FIFO queue pairs a 2100-rated player with a 950-rated player. That's not fun for either of them.

Solution: multiple queues by skill bracket.

```python
SKILL_BRACKETS = [
    (0, 1000, "matchmaking:bronze"),
    (1000, 1500, "matchmaking:silver"),
    (1500, 2000, "matchmaking:gold"),
    (2000, 3000, "matchmaking:diamond"),
]

def join_queue(player_id: str, skill: int):
    for low, high, queue_key in SKILL_BRACKETS:
        if low <= skill < high:
            entry = json.dumps({"player_id": player_id, "skill": skill, "queued_at": time.time()})
            r.lpush(queue_key, entry)
            return queue_key
    raise ValueError(f"No bracket for skill {skill}")

def matchmaker_for_bracket(queue_key: str):
    """One matchmaker per bracket."""
    while True:
        result = r.brpop(queue_key, timeout=5)
        if not result:
            continue
        # ... pair players within the same bracket
```

Four matchmaker workers, one per bracket. Players only face opponents within ±500 rating points.

### Queue Widening

If no opponent is found within 10 seconds, expand the search to adjacent brackets:

```python
def join_queue_with_widening(player_id: str, skill: int):
    entry = json.dumps({"player_id": player_id, "skill": skill, "queued_at": time.time()})
    primary_queue = get_bracket_queue(skill)
    r.lpush(primary_queue, entry)

    # After 10s, also add to adjacent brackets
    # (handled by a background widening worker)

def widening_worker():
    """Checks for players waiting too long, expands their search."""
    for queue_key in all_bracket_queues():
        items = r.lrange(queue_key, 0, -1)
        for item_raw in items:
            item = json.loads(item_raw)
            wait_time = time.time() - item["queued_at"]
            if wait_time > 10:
                adjacent = get_adjacent_brackets(item["skill"])
                for adj_queue in adjacent:
                    r.lpush(adj_queue, item_raw)
```

## List Commands Reference

| Command | Description | Complexity |
|---|---|---|
| `LPUSH key value [value ...]` | Push to head (left) | O(N) |
| `RPUSH key value [value ...]` | Push to tail (right) | O(N) |
| `LPOP key` | Pop from head | O(1) |
| `RPOP key` | Pop from tail | O(1) |
| `BRPOP key [key ...] timeout` | Blocking pop from tail | O(1) |
| `BLPOP key [key ...] timeout` | Blocking pop from head | O(1) |
| `LMOVE src dst LEFT\|RIGHT LEFT\|RIGHT` | Atomic move between lists | O(1) |
| `LRANGE key start stop` | Get range of elements | O(S+N) |
| `LLEN key` | List length | O(1) |
| `LREM key count value` | Remove occurrences | O(N) |
| `LINDEX key index` | Get element by index | O(N) |
| `LTRIM key start stop` | Trim to range | O(N) |

## Priority Queues

CEO Chad: "Tournament matches should be prioritized over casual games."

Redis doesn't have a native priority queue, but you can simulate one with multiple lists and `BRPOP`'s multi-key feature:

```redis
# BRPOP checks keys left-to-right, pops from the first non-empty one
BRPOP matchmaking:priority:tournament matchmaking:priority:ranked matchmaking:priority:casual 5
```

If `tournament` has items, it's served first. If empty, check `ranked`. If empty, check `casual`. Built-in priority without sorted sets.

```python
PRIORITY_QUEUES = [
    "matchmaking:priority:tournament",
    "matchmaking:priority:ranked",
    "matchmaking:priority:casual",
]

def join_queue(player_id: str, skill: int, mode: str = "casual"):
    queue_key = f"matchmaking:priority:{mode}"
    entry = json.dumps({"player_id": player_id, "skill": skill, "mode": mode})
    r.lpush(queue_key, entry)

def matchmaker_loop():
    while True:
        result = r.brpop(PRIORITY_QUEUES, timeout=5)
        if not result:
            continue
        queue_name, item_raw = result
        # Tournament players get matched first, always
```

## Queue Metrics

Ops Olga wants dashboards. How long is the queue? How long are players waiting?

```python
def queue_stats():
    stats = {}
    for queue_key in all_queues():
        length = r.llen(queue_key)
        # Peek at the oldest item (tail) without removing it
        oldest_raw = r.lindex(queue_key, -1)
        wait_time = 0
        if oldest_raw:
            oldest = json.loads(oldest_raw)
            wait_time = time.time() - oldest["queued_at"]
        stats[queue_key] = {"length": length, "max_wait_seconds": wait_time}
    return stats
```

```bash
curl http://localhost:5000/matchmaking/stats
# {
#   "matchmaking:bronze": {"length": 12, "max_wait_seconds": 3.2},
#   "matchmaking:gold": {"length": 2, "max_wait_seconds": 0.8},
#   "matchmaking:diamond": {"length": 45, "max_wait_seconds": 18.5}
# }
```

Diamond bracket has 45 players waiting 18 seconds. Time to widen the search.

## Dead Letter Queue

Some entries are malformed or cause repeated failures. After 3 retries, move them to a dead letter queue for manual inspection:

```python
def process_with_retries(item_raw: str, max_retries: int = 3):
    retry_key = f"retry_count:{hash(item_raw)}"
    retries = int(r.get(retry_key) or 0)

    if retries >= max_retries:
        r.lpush("matchmaking:dead_letter", item_raw)
        r.delete(retry_key)
        log.error(f"Moved to dead letter after {max_retries} failures: {item_raw}")
        return

    try:
        process(item_raw)
        r.delete(retry_key)
    except Exception as e:
        r.incr(retry_key)
        r.expire(retry_key, 300)
        r.lpush(QUEUE_KEY, item_raw)  # Re-queue for retry
        log.warning(f"Retry {retries + 1}/{max_retries}: {e}")
```

## What You Learned

- **LPUSH/RPOP** — basic FIFO queue
- **BRPOP** — blocking pop (no polling, instant response)
- **LMOVE** — atomic move for reliable queues
- **Reliable queue pattern** — processing list + recovery worker
- **Multi-key BRPOP** — priority queues
- **Skill brackets** — multiple queues for fair matchmaking
- **Queue widening** — expand search after timeout
- **Dead letter queue** — isolate poison messages

Matchmaking wait time: 15 seconds → under 2 seconds. No more lost players. Priority works. Ops Olga has her dashboards.

But now the game has in-match chat. Players send messages. Other players need to receive them instantly. You could poll Redis lists... but that's the same polling problem you just solved. You need real-time message delivery — push, not pull.

That's Chapter 5.

---

[← Chapter 3: Hashes and Caching](chapter-03-hashes-caching.md) | [Chapter 5: Chat Messages →](chapter-05-pubsub-streams.md)

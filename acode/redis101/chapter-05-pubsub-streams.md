# Chapter 5: Chat Messages Vanish — Pub/Sub and Streams

[← Chapter 4: Lists and Queues](chapter-04-lists-queues.md) | [Chapter 6: Spam Bots →](chapter-06-rate-limiting.md)

---

## The Problem

PingPong has in-match chat. Player A sends "gg" — Player B should see it instantly. The first implementation uses Redis Pub/Sub:

```python
# Publisher (when player sends a message)
r.publish(f"chat:match:{match_id}", json.dumps({"from": "alice", "text": "gg"}))

# Subscriber (player B's WebSocket handler)
pubsub = r.pubsub()
pubsub.subscribe(f"chat:match:{match_id}")
for message in pubsub.listen():
    if message["type"] == "message":
        send_to_websocket(message["data"])
```

It works. Messages arrive in real-time. Everyone is happy.

Then a player disconnects for 3 seconds (bad WiFi) and reconnects. Every message sent during those 3 seconds is gone. Pub/Sub is fire-and-forget — if nobody is listening when the message is published, it vanishes.

Marta: "Pub/Sub is for ephemeral notifications. Chat needs history. Look at Redis Streams."

## Pub/Sub: How It Works

Redis Pub/Sub is a broadcast system. Publishers send messages to channels. Subscribers listen on channels. Messages are delivered to all current subscribers and then discarded.

```redis
# Terminal 1: Subscribe
SUBSCRIBE chat:match:abc
# Waiting for messages...

# Terminal 2: Publish
PUBLISH chat:match:abc "hello from alice"
# (integer) 1 — delivered to 1 subscriber

# Terminal 1 receives:
# 1) "message"
# 2) "chat:match:abc"
# 3) "hello from alice"
```

### Pattern Subscriptions

```redis
PSUBSCRIBE chat:match:*
# Subscribes to ALL match chat channels
# Useful for admin monitoring
```

### Pub/Sub Characteristics

| Property | Value |
|---|---|
| Delivery | At-most-once (fire and forget) |
| Persistence | None — messages are never stored |
| History | None — can't replay past messages |
| Ordering | Guaranteed within a single publisher |
| Fan-out | All subscribers get every message |
| Backpressure | None — slow subscribers get disconnected |

### When Pub/Sub Is Perfect

- Real-time notifications that don't need history
- Cache invalidation signals ("key X changed, evict it")
- Live game state broadcasts (player positions, scores)
- System events ("server shutting down in 60s")

### When Pub/Sub Fails

- Chat (needs history for reconnecting clients)
- Task queues (messages must not be lost)
- Event sourcing (need to replay events)
- Anything where "I missed it" is unacceptable

## The Disconnect Problem in Detail

```
Timeline:
  t=0: Alice subscribes to chat:match:abc
  t=1: Bob sends "nice shot" → Alice receives it ✓
  t=2: Alice's WiFi drops → unsubscribed
  t=3: Bob sends "gg" → nobody listening → message GONE
  t=4: Bob sends "rematch?" → nobody listening → message GONE
  t=5: Alice reconnects, resubscribes → sees nothing
```

Alice missed two messages. With Pub/Sub, there's no way to ask "what did I miss?" The messages don't exist anymore.

## Redis Streams: Pub/Sub with Memory

A Redis Stream is an append-only log. Messages are stored with auto-generated IDs (timestamps). Consumers can read from any point in the stream — including "everything since I last read."

```redis
# Add messages to a stream
XADD chat:match:abc * from alice text "nice shot"
# "1705312800000-0" ← auto-generated ID (timestamp-sequence)

XADD chat:match:abc * from bob text "gg"
# "1705312801000-0"

XADD chat:match:abc * from bob text "rematch?"
# "1705312802000-0"

# Read all messages from the beginning
XRANGE chat:match:abc - +
# 1) 1) "1705312800000-0"
#    2) 1) "from" 2) "alice" 3) "text" 4) "nice shot"
# 2) 1) "1705312801000-0"
#    2) 1) "from" 2) "bob" 3) "text" 4) "gg"
# 3) 1) "1705312802000-0"
#    2) 1) "from" 2) "bob" 3) "text" 4) "rematch?"

# Read messages after a specific ID (what did I miss?)
XRANGE chat:match:abc 1705312801000-0 +
# Returns "gg" and "rematch?" — everything after "nice shot"
```

### XREAD: Blocking Read (Like BRPOP for Streams)

```redis
# Block until new messages arrive (or 5s timeout)
XREAD BLOCK 5000 STREAMS chat:match:abc $
# $ means "only new messages from now"
# Returns immediately when a message is added

# Read from a specific position (for reconnection)
XREAD BLOCK 5000 STREAMS chat:match:abc 1705312800000-0
# Returns everything after that ID
```

## Chat with Streams: The Fix

```python
import redis
import json
import time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def send_message(match_id: str, player_id: str, text: str):
    """Send a chat message — stored permanently in the stream."""
    stream_key = f"chat:match:{match_id}"
    message_id = r.xadd(stream_key, {
        "from": player_id,
        "text": text,
        "timestamp": str(time.time())
    })
    # Auto-trim: keep only last 1000 messages per match
    r.xtrim(stream_key, maxlen=1000, approximate=True)
    return message_id

def get_history(match_id: str, since_id: str = "0-0", limit: int = 50):
    """Get chat history — for reconnecting clients."""
    stream_key = f"chat:match:{match_id}"
    messages = r.xrange(stream_key, min=since_id, max="+", count=limit)
    return [{"id": msg_id, **fields} for msg_id, fields in messages]

def listen_for_messages(match_id: str, last_id: str = "$"):
    """Block until new messages arrive. Used by WebSocket handler."""
    stream_key = f"chat:match:{match_id}"
    while True:
        results = r.xread({stream_key: last_id}, block=5000, count=10)
        if results:
            for stream_name, messages in results:
                for msg_id, fields in messages:
                    yield {"id": msg_id, **fields}
                    last_id = msg_id
```

### The Reconnection Flow

```python
async def websocket_handler(ws, match_id: str):
    # Client sends their last seen message ID
    last_id = await ws.recv()  # e.g., "1705312800000-0" or "0-0" for full history

    # 1. Send missed messages (catch-up)
    missed = get_history(match_id, since_id=last_id)
    for msg in missed:
        await ws.send(json.dumps(msg))

    # 2. Stream new messages in real-time
    for msg in listen_for_messages(match_id, last_id=missed[-1]["id"] if missed else last_id):
        await ws.send(json.dumps(msg))
```

Alice disconnects at t=2, reconnects at t=5. She sends her last seen ID. The server replays "gg" and "rematch?" from the stream, then continues with live messages. No gaps.

## Consumer Groups: Distributed Processing

For the matchmaking notification system, multiple worker processes need to consume from the same stream — but each message should be processed by exactly one worker (not all of them).

Consumer groups solve this:

```redis
# Create a consumer group
XGROUP CREATE notifications:matchmaking workers 0
# "workers" is the group name, 0 means start from the beginning

# Worker 1 reads (gets messages no other worker in the group has seen)
XREADGROUP GROUP workers worker-1 COUNT 5 BLOCK 2000 STREAMS notifications:matchmaking >
# > means "give me new messages that haven't been delivered to anyone in this group"

# Worker 2 reads (gets DIFFERENT messages)
XREADGROUP GROUP workers worker-2 COUNT 5 BLOCK 2000 STREAMS notifications:matchmaking >
```

Each message goes to exactly one consumer in the group. If worker-1 gets message A, worker-2 won't see it.

### Acknowledgment

After processing, acknowledge the message:

```redis
XACK notifications:matchmaking workers 1705312800000-0
# Message is marked as processed
```

Unacknowledged messages can be claimed by other workers if the original consumer dies:

```redis
# Check for pending (unacknowledged) messages older than 60 seconds
XPENDING notifications:matchmaking workers - + 10

# Claim them for worker-2
XCLAIM notifications:matchmaking workers worker-2 60000 1705312800000-0
# worker-2 now owns this message and can process it
```

### In Python

```python
def notification_worker(worker_name: str):
    """Process match notifications. Multiple workers share the load."""
    stream_key = "notifications:matchmaking"
    group_name = "workers"

    # Create group if it doesn't exist
    try:
        r.xgroup_create(stream_key, group_name, id="0", mkstream=True)
    except redis.ResponseError:
        pass  # Group already exists

    while True:
        results = r.xreadgroup(group_name, worker_name,
                               {stream_key: ">"}, count=10, block=5000)
        if not results:
            # No new messages — check for stuck messages from dead workers
            claim_stuck_messages(stream_key, group_name, worker_name)
            continue

        for stream_name, messages in results:
            for msg_id, fields in messages:
                try:
                    process_notification(fields)
                    r.xack(stream_key, group_name, msg_id)
                except Exception as e:
                    log.error(f"Failed to process {msg_id}: {e}")
                    # Don't ACK — message stays pending for retry/claim

def claim_stuck_messages(stream_key: str, group_name: str, worker_name: str):
    """Claim messages from dead workers (pending > 60s)."""
    pending = r.xpending_range(stream_key, group_name, "-", "+", count=10)
    for entry in pending:
        if entry["time_since_delivered"] > 60000:  # 60 seconds
            r.xclaim(stream_key, group_name, worker_name,
                     min_idle_time=60000, message_ids=[entry["message_id"]])
```

## Stream Commands Reference

| Command | Description |
|---|---|
| `XADD key * field value [...]` | Append message to stream |
| `XRANGE key start end [COUNT n]` | Read range of messages |
| `XREVRANGE key end start [COUNT n]` | Read range in reverse |
| `XREAD [BLOCK ms] STREAMS key id` | Read new messages (optionally blocking) |
| `XLEN key` | Number of messages in stream |
| `XTRIM key MAXLEN [~] n` | Trim stream to N messages |
| `XGROUP CREATE key group id` | Create consumer group |
| `XREADGROUP GROUP g consumer STREAMS key >` | Read as consumer in group |
| `XACK key group id [id ...]` | Acknowledge processed messages |
| `XPENDING key group [start end count]` | List unacknowledged messages |
| `XCLAIM key group consumer min-idle id` | Claim stuck messages |

## Pub/Sub vs Streams: When to Use Which

| Feature | Pub/Sub | Streams |
|---|---|---|
| Persistence | No | Yes |
| History/Replay | No | Yes |
| Consumer groups | No | Yes |
| Acknowledgment | No | Yes |
| Speed | Slightly faster | Fast |
| Memory | Zero (fire-forget) | Grows until trimmed |
| Use case | Ephemeral broadcasts | Durable message processing |

**Use Pub/Sub for:** cache invalidation, live game state, typing indicators, "user is online" signals.

**Use Streams for:** chat, notifications, task queues, event logs, anything where losing a message is unacceptable.

## Trimming Streams

Streams grow forever unless trimmed. Two strategies:

```redis
# Hard cap: keep exactly 1000 messages
XTRIM chat:match:abc MAXLEN 1000

# Approximate cap (faster, allows slight overshoot)
XTRIM chat:match:abc MAXLEN ~ 1000

# Time-based: remove messages older than 24 hours
# (No native command — use XRANGE + XDEL in a cleanup worker)
```

For match chat, trim to 1000 messages. Matches last 10-30 minutes — 1000 messages is more than enough.

For the notification stream, trim after all consumers have acknowledged:

```python
def trim_acknowledged(stream_key: str, group_name: str):
    """Remove messages that all consumers have processed."""
    info = r.xinfo_groups(stream_key)
    for group in info:
        if group["name"] == group_name:
            last_delivered = group["last-delivered-id"]
            # Trim everything before the last delivered ID
            r.xtrim(stream_key, minid=last_delivered)
```

## What You Learned

- **Pub/Sub** — fire-and-forget broadcast (PUBLISH, SUBSCRIBE, PSUBSCRIBE)
- **Pub/Sub limitations** — no persistence, no history, no replay
- **Streams** — append-only log with IDs, ranges, and blocking reads
- **XADD/XRANGE/XREAD** — write, read history, block for new messages
- **Consumer groups** — distribute stream processing across workers
- **XACK/XCLAIM** — acknowledgment and dead consumer recovery
- **XTRIM** — prevent unbounded stream growth
- **Reconnection pattern** — replay missed messages from last seen ID

Chat messages no longer vanish. Disconnected players catch up seamlessly. The notification system processes messages exactly once across multiple workers.

But Ops Olga is seeing something alarming in the logs. Thousands of requests per second from the same IP addresses. Spam bots are flooding the matchmaking API, creating fake accounts, and sending garbage chat messages. You need rate limiting — and it needs to be fast enough to not slow down legitimate players.

That's Chapter 6.

---

[← Chapter 4: Lists and Queues](chapter-04-lists-queues.md) | [Chapter 6: Spam Bots →](chapter-06-rate-limiting.md)

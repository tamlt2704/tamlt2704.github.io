# Chapter 19: Real-Time at Scale

[← Ch 18](chapter-18-url-shortener.md) | [Ch 20 →](chapter-20-launch-day.md)

---

## The Crisis

Week five. 12M users. Product is pushing hard on engagement features.

**Kai** (Product meeting):
> Users want to know instantly when someone downloads their file. Right now they have to refresh the page. Also, upload progress — we show a spinner but no percentage. And when two people are viewing the same shared folder, they should see each other's cursors... okay maybe not cursors, but at least see new files appear in real-time.

**Sana**:
> All of these require the server to push data to the client. HTTP is request-response — the client has to ask. We need the server to initiate communication.

**Omar**:
> We have 12M users. If even 10% are online simultaneously, that's 1.2 million concurrent connections. Each WebSocket connection holds a TCP socket open. How do we manage that?

---

## Architecture (Before — Polling)

```
┌──────────┐                    ┌──────────┐
│  Client  │──GET /updates──→  │  Server  │
│          │←── "nothing" ────│          │
│          │                    │          │
│  (wait 5s)                    │          │
│          │──GET /updates──→  │          │
│          │←── "nothing" ────│          │
│          │                    │          │
│  (wait 5s)                    │          │
│          │──GET /updates──→  │          │
│          │←── "1 new file" ──│          │
└──────────┘                    └──────────┘

Problem: 1.2M users × 1 request/5s = 240K requests/sec (mostly wasted)
```

## Architecture (After — WebSockets)

```
┌──────────┐                    ┌──────────┐
│  Client  │══ WebSocket ══════│  Server  │
│          │                    │          │
│          │←── push: "file    │          │
│          │    downloaded" ───│          │
│          │                    │          │
│          │←── push: "upload  │          │
│          │    progress 47%" ─│          │
│          │                    │          │
│          │←── push: "new     │          │
│          │    file in folder"│          │
└──────────┘                    └──────────┘

Persistent connection. Server pushes when events happen. Zero wasted requests.
```

---

## Concept: WebSocket Connections

### HTTP vs WebSocket

| Feature | HTTP | WebSocket |
|---------|------|-----------|
| Direction | Client → Server (request-response) | Bidirectional |
| Connection | New connection per request | Persistent (long-lived) |
| Overhead | Headers on every request (~800 bytes) | 2-6 bytes per frame |
| Server push | Not possible (without hacks) | Native |
| Scaling | Stateless (easy) | Stateful (harder) |

### WebSocket Lifecycle

```
1. Client sends HTTP Upgrade request
2. Server responds with 101 Switching Protocols
3. Connection upgraded to WebSocket
4. Both sides can send messages at any time
5. Either side can close the connection
```

```python
# Server-side WebSocket handler
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    async def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)
    
    async def send_to_user(self, user_id: str, message: dict):
        ws = self.active_connections.get(user_id)
        if ws:
            await ws.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    try:
        while True:
            # Keep connection alive, handle client messages
            data = await websocket.receive_json()
            await handle_client_message(user_id, data)
    except WebSocketDisconnect:
        await manager.disconnect(user_id)
```

---

## Concept: The Multi-Server Problem

With one server, `ConnectionManager` works. With 8 servers behind a load balancer:

```
User A connected to Server 3
User B connected to Server 7

User B downloads User A's file.
Server 7 knows about the download.
But User A's WebSocket is on Server 3.
Server 7 can't push to User A!
```

### Solution: Pub/Sub for Cross-Server Communication

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Server 1 │     │ Server 2 │     │ Server 3 │
│ (Users   │     │ (Users   │     │ (Users   │
│  A, D, G) │     │  B, E, H) │     │  C, F)   │
└─────┬────┘     └─────┬────┘     └─────┬────┘
      │                 │                 │
      └────────────┬────┴────────────────┘
                   │
          ┌────────┴────────┐
          │   Redis Pub/Sub  │
          │  (or Kafka)      │
          └─────────────────┘

Flow:
1. Server 7 receives "file downloaded by User B"
2. Server 7 publishes to Redis channel: "notify:user_A"
3. Server 3 (subscribed to "notify:user_A") receives message
4. Server 3 pushes to User A's WebSocket
```

```python
# Cross-server notification via Redis Pub/Sub
import aioredis

class DistributedConnectionManager:
    def __init__(self):
        self.local_connections: dict[str, WebSocket] = {}
        self.redis = aioredis.from_url("redis://elasticache:6379")
        self.pubsub = self.redis.pubsub()
    
    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.local_connections[user_id] = websocket
        # Subscribe to this user's channel
        await self.pubsub.subscribe(f"notify:{user_id}")
    
    async def notify_user(self, user_id: str, message: dict):
        """Send to user regardless of which server they're on."""
        # Publish to Redis — the server with the connection will deliver
        await self.redis.publish(
            f"notify:{user_id}",
            json.dumps(message)
        )
    
    async def listen_for_messages(self):
        """Background task: deliver messages from Redis to local WebSockets."""
        async for message in self.pubsub.listen():
            if message["type"] == "message":
                channel = message["channel"].decode()
                user_id = channel.split(":")[1]
                
                ws = self.local_connections.get(user_id)
                if ws:
                    data = json.loads(message["data"])
                    await ws.send_json(data)
```

---

## Concept: Connection Management at Scale

1.2M concurrent connections. Each WebSocket holds:
- A TCP socket (file descriptor)
- Memory for buffers (~10KB per connection)
- A subscription in Redis pub/sub

### Resource Planning

```
Per connection:
  - File descriptor: 1
  - Memory: ~10KB
  - Redis subscription: 1 channel

Per server (c5.2xlarge, 8 vCPU, 16GB RAM):
  - Max file descriptors: 100,000 (after tuning)
  - Memory for connections: 100K × 10KB = 1GB
  - Available for app logic: 15GB
  
Servers needed: 1,200,000 / 100,000 = 12 WebSocket servers
```

### Connection Lifecycle

```python
# Heartbeat to detect dead connections
async def heartbeat_loop(websocket: WebSocket, user_id: str):
    while True:
        try:
            await asyncio.sleep(30)
            await websocket.send_json({"type": "ping"})
            # Wait for pong with timeout
            response = await asyncio.wait_for(
                websocket.receive_json(), timeout=10
            )
            if response.get("type") != "pong":
                break
        except (asyncio.TimeoutError, WebSocketDisconnect):
            await manager.disconnect(user_id)
            break
```

---

## Concept: Presence (Who's Online?)

```python
# Track online users with Redis sorted set (score = last seen timestamp)
class PresenceService:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def mark_online(self, user_id: str):
        """Mark user as online (refresh every 30s via heartbeat)."""
        await self.redis.zadd(
            "presence:online",
            {user_id: time.time()}
        )
    
    async def mark_offline(self, user_id: str):
        await self.redis.zrem("presence:online", user_id)
    
    async def get_online_users(self, user_ids: list[str]) -> list[str]:
        """Which of these users are currently online?"""
        cutoff = time.time() - 60  # Online = seen in last 60s
        online = []
        for uid in user_ids:
            score = await self.redis.zscore("presence:online", uid)
            if score and score > cutoff:
                online.append(uid)
        return online
    
    async def cleanup_stale(self):
        """Remove users who haven't heartbeated in 60s."""
        cutoff = time.time() - 60
        await self.redis.zremrangebyscore("presence:online", 0, cutoff)
```

---

## Concept: Fan-Out

When a file is downloaded, notify the owner. Simple. But what about shared folders with 50 collaborators?

```
File uploaded to shared folder (50 collaborators)
  → Need to notify all 50 users
  → Each might be on a different server
  → That's 50 Redis publishes
```

### Fan-Out Strategies

| Strategy | How | Best For |
|----------|-----|----------|
| **Fan-out on write** | Publish to each user's channel immediately | Small groups (< 100 users) |
| **Fan-out on read** | Users poll/subscribe to folder channel | Large groups (1000+ users) |
| **Hybrid** | Small groups: on write. Large groups: on read | Mixed sizes |

```python
# GhostDrop: Fan-out on write (folders are typically < 20 collaborators)
async def notify_folder_update(folder_id: str, event: dict):
    collaborators = await db.get_folder_collaborators(folder_id)
    
    for user_id in collaborators:
        await manager.notify_user(user_id, {
            "type": "folder.updated",
            "folder_id": folder_id,
            "event": event,
        })
```

---

## Concept: Long Polling Fallback

WebSockets don't work everywhere (corporate proxies, old browsers). Long polling is the fallback.

```python
# Long polling endpoint
@app.get("/api/poll/{user_id}")
async def long_poll(user_id: str, last_event_id: str = None):
    """Block until there's a new event or timeout (30s)."""
    timeout = 30
    start = time.time()
    
    while time.time() - start < timeout:
        events = await get_pending_events(user_id, after=last_event_id)
        if events:
            return {"events": events, "last_event_id": events[-1]["id"]}
        await asyncio.sleep(1)
    
    return {"events": [], "last_event_id": last_event_id}
```

### Client-Side Connection Strategy

```javascript
// Client: Try WebSocket, fall back to long polling
class RealtimeClient {
  connect() {
    if ('WebSocket' in window) {
      this.ws = new WebSocket(`wss://ws.ghostdrop.io/ws/${userId}`);
      this.ws.onmessage = (e) => this.handleMessage(JSON.parse(e.data));
      this.ws.onerror = () => this.fallbackToPolling();
    } else {
      this.fallbackToPolling();
    }
  }
  
  fallbackToPolling() {
    const poll = async () => {
      const res = await fetch(`/api/poll/${userId}?last=${this.lastEventId}`);
      const data = await res.json();
      data.events.forEach(e => this.handleMessage(e));
      this.lastEventId = data.last_event_id;
      poll(); // Immediately poll again
    };
    poll();
  }
}
```

---

## GhostDrop Real-Time Features

| Feature | Mechanism | Fan-Out |
|---------|-----------|---------|
| Upload progress | WebSocket to uploader only | 1:1 |
| Download notification | Pub/Sub to file owner | 1:1 |
| Folder updates | Pub/Sub to collaborators | 1:N (N < 50) |
| Online presence | Redis sorted set + heartbeat | Passive (query on demand) |

### Architecture

```
┌──────────┐     ┌──────────┐     ┌──────────────────┐
│  Client  │═══WS═══│   LB    │════│  WS Server 1-12  │
└──────────┘     │ (sticky  │     └────────┬─────────┘
                 │ sessions)│              │
                 └──────────┘              │
                                           ▼
                                  ┌────────────────┐
                                  │  Redis Pub/Sub  │
                                  └────────┬───────┘
                                           │
                              ┌────────────┼────────────┐
                              ▼            ▼            ▼
                        ┌──────────┐ ┌──────────┐ ┌──────────┐
                        │  Kafka   │ │  Upload  │ │  Share   │
                        │Consumer  │ │ Service  │ │ Service  │
                        └──────────┘ └──────────┘ └──────────┘
```

---

## Tradeoffs

| Decision | Gain | Cost |
|----------|------|------|
| WebSocket over polling | Real-time, low overhead | Stateful connections, harder to scale |
| Redis Pub/Sub for cross-server | Simple, fast | Redis becomes critical path |
| Sticky sessions for WS | Connection stability | Uneven load distribution |
| Long polling fallback | Universal compatibility | Higher server load than WS |
| Fan-out on write | Instant delivery | O(N) publishes per event |

---

## Why Not Just...

**"Why not use Server-Sent Events (SSE) instead of WebSockets?"**
SSE is server-to-client only. GhostDrop needs bidirectional (client sends typing indicators, read receipts). Also, SSE has a 6-connection limit per domain in HTTP/1.1.

**"Why not use a managed service (Pusher, Ably)?"**
At 1.2M connections, managed services cost $5,000-15,000/month. Self-hosted Redis Pub/Sub + WebSocket servers cost ~$2,000/month. At GhostDrop's scale, self-hosting is cheaper.

**"Why not use Kafka for pub/sub instead of Redis?"**
Kafka is designed for durable event streaming, not ephemeral real-time notifications. Redis Pub/Sub is fire-and-forget (if no subscriber is listening, the message is lost). That's fine for real-time notifications — if the user isn't connected, they'll see it when they reconnect via a REST API call.

**"Why not just poll every 1 second?"**
1.2M users × 1 req/sec = 1.2M requests/sec. That's 10x more load than WebSockets, and you still have 1-second latency. WebSockets deliver in milliseconds with near-zero idle overhead.

---

## Exercise

GhostDrop adds a "live viewers" feature: when viewing a shared file, you can see who else is viewing it right now (like Google Docs).

1. How do you track who's viewing a specific file?
2. How do you handle users who close the tab without disconnecting cleanly?
3. What's the maximum number of viewers you'd show (and why)?

<details>
<summary>Hint</summary>

Track viewers with a Redis sorted set per file: `viewers:{file_id}` with score = last heartbeat timestamp. When a user opens a file, add them. Heartbeat every 10 seconds. Clean up entries older than 30 seconds (handles unclean disconnects). Show max 10 viewers with "+N more" — rendering 1000 avatars is a UX problem, and querying 1000 user profiles for every viewer list is expensive. Publish viewer count changes to the file's channel so all viewers see updates in real-time.
</details>

---

## Quick Reference

| Term | Definition |
|------|-----------|
| **WebSocket** | Persistent bidirectional connection over TCP |
| **Pub/Sub** | Publish-subscribe messaging pattern |
| **Fan-Out** | Distributing one message to many recipients |
| **Presence** | Tracking which users are currently online |
| **Long Polling** | HTTP request that blocks until data is available |
| **SSE** | Server-Sent Events — server-to-client streaming over HTTP |
| **Heartbeat** | Periodic ping to verify connection is alive |
| **Sticky Session** | Route same client to same server (for WS) |
| **Connection Pool** | Managed set of reusable connections |

---

## What Breaks Next

Real-time features are live. Users see instant notifications. Upload progress is smooth. Folder collaboration feels alive.

The system is ready. But the real test is coming: launch day. The podcast airs in 24 hours. You need to make sure everything holds under 10x traffic.

Time for capacity planning and the final checklist.

[← Ch 18](chapter-18-url-shortener.md) | [Ch 20 →](chapter-20-launch-day.md)

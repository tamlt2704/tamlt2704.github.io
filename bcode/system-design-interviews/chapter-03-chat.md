# Chapter 3: Design a Chat System (WhatsApp/Slack)

[← Rate Limiter](./chapter-02-rate-limiter.md) | [Next: News Feed →](./chapter-04-newsfeed.md)

---

## The Question

> "Design a real-time messaging system like WhatsApp or Slack. Users can send 1:1 messages and group messages. Messages should be delivered in real-time with delivery receipts (sent, delivered, read). Support online/offline presence indicators."

---

## Step 1: Requirements & Scope

**Functional:**
- 1:1 messaging and group chat (up to 500 members)
- Real-time delivery via persistent connections
- Delivery status: sent → delivered → read
- Online/offline presence indicators
- Push notifications for offline users
- Message history and search

**Non-functional:**
- 500M DAU, average 40 messages/user/day
- Message delivery latency <200ms (same region)
- Messages must never be lost (durability)
- Eventual consistency for presence, strong consistency for messages
- End-to-end encryption (mention, don't deep-dive)

---

## Step 2: Estimation

| Metric | Calculation | Result |
|--------|-------------|--------|
| Messages/day | 500M × 40 | 20B messages/day |
| Messages/sec | 20B / 86400 | ~230K msg/sec |
| Storage/day | 20B × 200 bytes | ~4 TB/day |
| Storage (5 years) | 4 TB × 365 × 5 | ~7.3 PB |
| Concurrent connections | 500M × 10% online | 50M WebSockets |

---

## Step 3: API Design

```
WebSocket: wss://chat.example.com/ws?token=<jwt>

-- Send message
{ "action": "send", "to": "user_456", "content": "Hello!", "msg_id": "uuid" }

-- Receive message
{ "action": "message", "from": "user_123", "content": "Hello!", "timestamp": ... }

-- Delivery receipt
{ "action": "ack", "msg_id": "uuid", "status": "delivered" }

-- Presence
{ "action": "presence", "user_id": "user_123", "status": "online" }

REST (for history):
GET /api/v1/messages?chat_id=xxx&before=timestamp&limit=50
```

---

## Step 4: Data Model

**Messages (Cassandra — write-heavy, time-series, partitioned by chat):**

| Field | Type |
|-------|------|
| chat_id (partition key) | UUID |
| message_id (clustering key) | TIMEUUID |
| sender_id | UUID |
| content | TEXT |
| type | ENUM (text, image, video) |
| status | ENUM (sent, delivered, read) |
| created_at | TIMESTAMP |

**User Sessions (Redis):**

```
Key:   session:{user_id}
Value: { "server_id": "ws-server-7", "last_seen": timestamp }
TTL:   300 seconds (heartbeat refreshes)
```

---

## Step 5: High-Level Architecture

```
┌──────────┐     ┌──────────────┐     ┌─────────────────┐
│  Client  │◀═══▶│ Load Balancer│◀═══▶│  WebSocket      │
│  (App)   │ WS  │ (L4/sticky)  │     │  Servers        │
└──────────┘     └──────────────┘     └────────┬────────┘
                                               │
                              ┌─────────────────┼─────────────────┐
                              ▼                 ▼                  ▼
                     ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
                     │ Session Store│  │ Message Queue │  │   Push       │
                     │ (Redis)      │  │ (Kafka)       │  │ Notification │
                     └──────────────┘  └──────┬───────┘  └──────────────┘
                                              │
                                              ▼
                                     ┌──────────────┐
                                     │  Message DB  │
                                     │ (Cassandra)  │
                                     └──────────────┘
```

---

## Step 6: Deep Dive

### Message Delivery Flow (1:1)

1. User A sends message via WebSocket to WS-Server-1
2. Server looks up User B's session in Redis → finds WS-Server-3
3. Server publishes message to Kafka topic for WS-Server-3
4. WS-Server-3 pushes message to User B's WebSocket
5. User B's client sends "delivered" ack → forwarded back to User A
6. Message persisted to Cassandra asynchronously

**If User B is offline:**
- Message stored in DB with status "sent"
- Push notification triggered via APNs/FCM
- When B comes online, pull undelivered messages from DB

### Group Chat Fan-Out

**Small groups (<500):** Write message once, fan-out on delivery.
- Look up all group members' sessions
- Push to each connected member's WS server via Kafka

**Why not fan-out on write?** For a 500-member group, writing 500 copies per message is wasteful. Fan-out on read (pull) for very large groups.

### Presence (Online/Offline)

- Client sends heartbeat every 30 seconds
- Redis key with TTL=60s; heartbeat refreshes TTL
- When TTL expires → user is offline
- Presence updates published to friends/group members via pub/sub
- **Optimization:** Only send presence to users who have the chat open (not all contacts)

### Delivery Guarantees

| Status | Meaning | Trigger |
|--------|---------|---------|
| Sent ✓ | Server received message | Server ACKs to sender |
| Delivered ✓✓ | Recipient's device received | Client ACKs to server |
| Read ✓✓✓ | Recipient opened chat | Client sends read receipt |

---

## Step 7: Bottlenecks & Scaling

| Bottleneck | Solution |
|-----------|----------|
| 50M concurrent WebSockets | Shard across 1000+ WS servers |
| Cross-server message routing | Kafka as message bus between servers |
| Hot group chats | Dedicated servers for large groups |
| Message ordering | TIMEUUID ensures order per chat |
| Presence thundering herd | Batch presence updates, debounce |

**Sticky sessions:** WebSocket connections are stateful — use consistent hashing or session affinity at the load balancer (L4, not L7).

---

## Key Talking Points

- WebSockets for real-time, with fallback to long-polling
- Redis for session/presence, Cassandra for message storage
- Fan-out on delivery for groups (not fan-out on write)
- Three-tier delivery receipts map to real UX (✓ ✓✓ ✓✓✓)
- Heartbeat-based presence with TTL is simple and scalable

---

## Common Mistakes

- Using HTTP polling instead of WebSockets for real-time chat
- Storing messages in a relational DB without considering write volume
- Fan-out on write for group messages (doesn't scale for large groups)
- Ignoring the offline case — what happens when the user isn't connected?
- Not addressing message ordering in distributed systems
- Overcomplicating presence with a separate consensus system

---

[← Rate Limiter](./chapter-02-rate-limiter.md) | [Next: News Feed →](./chapter-04-newsfeed.md)

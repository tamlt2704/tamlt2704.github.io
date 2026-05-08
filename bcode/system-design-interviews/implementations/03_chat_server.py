"""
Chat Server — Core Implementation
====================================
Demonstrates: Message routing, session registry, delivery receipts,
presence tracking with heartbeat TTL, group message fan-out.

In a real system:
- WebSocket connections managed by gateway servers (Nginx, Envoy)
- Session registry in Redis (user_id → server_id mapping)
- Messages routed via pub/sub (Redis Pub/Sub, Kafka)
- Presence tracked with Redis EXPIRE (heartbeat refreshes TTL)
- Group fan-out via Kafka consumer groups or dedicated fan-out service
- Messages persisted in Cassandra (write-heavy, time-series)
"""

import asyncio
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ─── Message Status ───────────────────────────────────────────────────────────

class MessageStatus(Enum):
    SENT = "sent"           # Server received it
    DELIVERED = "delivered"  # Recipient's device got it
    READ = "read"           # Recipient opened the chat


@dataclass
class Message:
    id: str
    sender: str
    recipient: str
    content: str
    timestamp: float = field(default_factory=time.time)
    status: MessageStatus = MessageStatus.SENT
    group_id: Optional[str] = None


# ─── Session Registry (which server each user is on) ─────────────────────────

class SessionRegistry:
    """
    Maps user_id → server_id. In production, this is Redis:
      HSET sessions user123 server-west-2a
      EXPIRE sessions:user123 300
    """

    def __init__(self):
        self.sessions: dict[str, str] = {}  # user_id → server_id

    def register(self, user_id: str, server_id: str):
        self.sessions[user_id] = server_id

    def unregister(self, user_id: str):
        self.sessions.pop(user_id, None)

    def get_server(self, user_id: str) -> Optional[str]:
        return self.sessions.get(user_id)

    def is_online(self, user_id: str) -> bool:
        return user_id in self.sessions


# ─── Presence Tracker (heartbeat with TTL) ───────────────────────────────────

class PresenceTracker:
    """
    Tracks user online/offline status via heartbeats.
    If no heartbeat within TTL, user is considered offline.

    Production: Redis with EXPIRE — each heartbeat does SET + EXPIRE.
    """

    def __init__(self, ttl_seconds: float = 30.0):
        self.ttl = ttl_seconds
        self.last_heartbeat: dict[str, float] = {}

    def heartbeat(self, user_id: str):
        self.last_heartbeat[user_id] = time.time()

    def is_online(self, user_id: str) -> bool:
        last = self.last_heartbeat.get(user_id)
        if last is None:
            return False
        return (time.time() - last) < self.ttl

    def get_online_users(self) -> list[str]:
        now = time.time()
        return [uid for uid, ts in self.last_heartbeat.items()
                if (now - ts) < self.ttl]


# ─── Chat Server ─────────────────────────────────────────────────────────────

class ChatServer:
    """
    Simulates a chat server node. In production, multiple server instances
    communicate via pub/sub for cross-server message routing.
    """

    def __init__(self, server_id: str, registry: SessionRegistry, presence: PresenceTracker):
        self.server_id = server_id
        self.registry = registry
        self.presence = presence
        self.msg_counter = 0
        # Local connections on this server
        self.local_users: set[str] = set()
        # Inbox: messages waiting for offline users
        self.offline_queue: dict[str, list[Message]] = defaultdict(list)
        # Delivery receipts log
        self.receipts: list[tuple[str, str, MessageStatus]] = []
        # Group membership
        self.groups: dict[str, set[str]] = defaultdict(set)

    def connect_user(self, user_id: str):
        """User connects to this server (WebSocket open)."""
        self.local_users.add(user_id)
        self.registry.register(user_id, self.server_id)
        self.presence.heartbeat(user_id)
        # Deliver queued messages
        if user_id in self.offline_queue:
            queued = self.offline_queue.pop(user_id)
            for msg in queued:
                self._deliver(msg)

    def disconnect_user(self, user_id: str):
        """User disconnects (WebSocket close)."""
        self.local_users.discard(user_id)
        self.registry.unregister(user_id)

    def send_message(self, sender: str, recipient: str, content: str) -> Message:
        """Route a 1:1 message."""
        self.msg_counter += 1
        msg = Message(
            id=f"msg_{self.msg_counter:04d}",
            sender=sender,
            recipient=recipient,
            content=content,
        )
        # Route to recipient
        if self.registry.is_online(recipient):
            target_server = self.registry.get_server(recipient)
            if target_server == self.server_id:
                self._deliver(msg)
            else:
                # In production: publish to Redis/Kafka for target server
                self._deliver(msg)  # Simulated cross-server delivery
        else:
            # User offline — queue for later
            self.offline_queue[recipient].append(msg)
        return msg

    def send_group_message(self, sender: str, group_id: str, content: str) -> list[Message]:
        """Fan-out a message to all group members."""
        members = self.groups.get(group_id, set())
        messages = []
        for member in members:
            if member == sender:
                continue
            msg = self.send_message(sender, member, content)
            msg.group_id = group_id
            messages.append(msg)
        return messages

    def join_group(self, user_id: str, group_id: str):
        self.groups[group_id].add(user_id)

    def _deliver(self, msg: Message):
        """Deliver message to recipient and update status."""
        msg.status = MessageStatus.DELIVERED
        self.receipts.append((msg.id, msg.recipient, MessageStatus.DELIVERED))

    def mark_read(self, msg: Message):
        """Recipient marks message as read."""
        msg.status = MessageStatus.READ
        self.receipts.append((msg.id, msg.sender, MessageStatus.READ))


# ─── Async Simulation ────────────────────────────────────────────────────────

async def simulate_chat():
    """Simulate a chat session with multiple users."""
    registry = SessionRegistry()
    presence = PresenceTracker(ttl_seconds=5.0)

    server1 = ChatServer("server-east-1", registry, presence)
    server2 = ChatServer("server-west-1", registry, presence)

    print("=== Chat Server Simulation ===\n")

    # Users connect
    print("--- Users Connecting ---")
    server1.connect_user("alice")
    server1.connect_user("bob")
    server2.connect_user("charlie")
    print(f"  server-east-1: alice, bob")
    print(f"  server-west-1: charlie")
    print(f"  Online: {presence.get_online_users()}")

    # 1:1 messaging
    print("\n--- 1:1 Messages ---")
    msg1 = server1.send_message("alice", "bob", "Hey Bob!")
    print(f"  {msg1.sender} → {msg1.recipient}: '{msg1.content}' [{msg1.status.value}]")

    msg2 = server1.send_message("bob", "alice", "Hi Alice!")
    print(f"  {msg2.sender} → {msg2.recipient}: '{msg2.content}' [{msg2.status.value}]")

    # Mark as read
    server1.mark_read(msg1)
    print(f"  {msg1.id} marked as READ by {msg1.recipient}")

    # Offline messaging
    print("\n--- Offline Message Queue ---")
    server1.disconnect_user("bob")
    msg3 = server1.send_message("alice", "bob", "Are you there?")
    print(f"  bob is offline — message queued: '{msg3.content}' [{msg3.status.value}]")
    print(f"  Queue size for bob: {len(server1.offline_queue['bob'])}")

    # Bob reconnects — gets queued messages
    server1.connect_user("bob")
    print(f"  bob reconnects — delivered queued messages")
    print(f"  Queue size for bob: {len(server1.offline_queue.get('bob', []))}")
    print(f"  msg3 status: {msg3.status.value}")

    # Group messaging
    print("\n--- Group Fan-Out ---")
    server1.join_group("alice", "team-chat")
    server1.join_group("bob", "team-chat")
    server1.join_group("charlie", "team-chat")

    group_msgs = server1.send_group_message("alice", "team-chat", "Hello team!")
    print(f"  alice → team-chat: 'Hello team!'")
    print(f"  Fan-out to {len(group_msgs)} members: {[m.recipient for m in group_msgs]}")

    # Presence with heartbeat expiry
    print("\n--- Presence & Heartbeat ---")
    presence.heartbeat("alice")
    await asyncio.sleep(0.1)
    print(f"  alice online: {presence.is_online('alice')}")
    # Simulate expired heartbeat
    presence.last_heartbeat["dave"] = time.time() - 60  # Expired
    print(f"  dave online: {presence.is_online('dave')} (heartbeat expired)")

    # Delivery receipts summary
    print("\n--- Delivery Receipts ---")
    for msg_id, user, status in server1.receipts[:5]:
        print(f"  {msg_id} → {user}: {status.value}")


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    asyncio.run(simulate_chat())

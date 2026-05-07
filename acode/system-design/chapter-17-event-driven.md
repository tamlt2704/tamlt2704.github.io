# Chapter 17: Event-Driven Architecture

[← Ch 16](chapter-16-sharding.md) | [Ch 18 →](chapter-18-url-shortener.md)

---

## The Crisis

Post-podcast. 10M users. The system is scaling, but the architecture is getting tangled.

**Sana** (Monday standup):
> We need to add analytics tracking. Every file upload should update the analytics dashboard. But the upload service already publishes to 4 different SQS queues: virus scan, thumbnails, notifications, and quota updates. Adding a 5th means changing the upload service code. Again.

**Omar**:
> The notification service went down for 10 minutes yesterday. The upload service kept trying to send to its queue and timing out. Uploads slowed down because of a notification dependency.

**Amir**:
> Every time we add a new consumer, we modify the producer. That's tight coupling with extra steps.

**You**:
> We need to flip the model. The upload service publishes ONE event: "file uploaded." Anyone who cares subscribes. The upload service doesn't know or care who's listening.

---

## Architecture (Before — Point-to-Point)

```
┌──────────────┐
│   Upload     │──→ SQS Queue 1 ──→ Virus Scanner
│   Service    │──→ SQS Queue 2 ──→ Thumbnail Generator
│              │──→ SQS Queue 3 ──→ Notification Service
│              │──→ SQS Queue 4 ──→ Quota Service
│              │──→ SQS Queue 5 ──→ Analytics (NEW — requires code change!)
└──────────────┘

Upload service knows about every consumer. Adding one = code change.
```

## Architecture (After — Event-Driven)

```
┌──────────────┐         ┌─────────────────────────────┐
│   Upload     │──event─→│         Kafka                │
│   Service    │         │   Topic: "file.events"       │
└──────────────┘         └──────────┬──────────────────┘
                                    │
                    ┌───────────────┼───────────────────┐
                    │               │                   │
                    ▼               ▼                   ▼
            ┌────────────┐  ┌────────────┐  ┌────────────────┐
            │Virus Scanner│  │ Thumbnails │  │ Notifications  │
            │(consumer)   │  │(consumer)  │  │ (consumer)     │
            └────────────┘  └────────────┘  └────────────────┘
                    │               │                   │
                    ▼               ▼                   ▼
            ┌────────────┐  ┌────────────┐
            │  Quota     │  │ Analytics  │  ← Added without touching
            │(consumer)  │  │(consumer)  │    upload service!
            └────────────┘  └────────────┘
```

---

## Concept: Kafka Fundamentals

### Topics and Partitions

```
Topic: "file.events"
  ├── Partition 0: [event1, event4, event7, ...]
  ├── Partition 1: [event2, event5, event8, ...]
  └── Partition 2: [event3, event6, event9, ...]

Events are distributed across partitions by key (user_id).
Each partition is an ordered, append-only log.
```

### Producers and Consumers

```python
# Producer: Upload service publishes events
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['kafka-1:9092', 'kafka-2:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8'),
)

def publish_file_event(event_type: str, file_data: dict):
    event = {
        "type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "data": file_data,
        "version": "1.0",
    }
    producer.send(
        topic="file.events",
        key=file_data["user_id"],  # Partition by user
        value=event,
    )

# Usage in upload handler
publish_file_event("file.uploaded", {
    "file_id": "file_abc123",
    "user_id": "usr_4821",
    "filename": "report.pdf",
    "size_bytes": 5242880,
    "s3_key": "uploads/usr_4821/abc123/report.pdf",
})
```

```python
# Consumer: Analytics service subscribes
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'file.events',
    bootstrap_servers=['kafka-1:9092', 'kafka-2:9092'],
    group_id='analytics-service',
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
)

for message in consumer:
    event = message.value
    match event["type"]:
        case "file.uploaded":
            track_upload(event["data"])
        case "file.downloaded":
            track_download(event["data"])
        case "file.deleted":
            track_deletion(event["data"])
```

---

## Concept: Consumer Groups

Multiple instances of a service share the work:

```
Topic: "file.events" (3 partitions)

Consumer Group: "virus-scanner" (3 instances)
  Instance A → reads Partition 0
  Instance B → reads Partition 1
  Instance C → reads Partition 2

Consumer Group: "analytics" (2 instances)
  Instance A → reads Partition 0, 1
  Instance B → reads Partition 2

Each group gets ALL events. Within a group, events are distributed.
```

### Key Properties

| Property | Behavior |
|----------|----------|
| **Within a group** | Each event processed by exactly one instance |
| **Across groups** | Each event processed by every group |
| **Ordering** | Guaranteed within a partition |
| **Replay** | Consumers can rewind and reprocess events |

---

## Concept: Event Sourcing

Instead of storing current state, store the sequence of events that led to it.

```
Traditional (state-based):
  files table: {id: "abc", name: "report.pdf", size: 5MB, downloads: 47}

Event-sourced:
  events log:
    1. FileUploaded {id: "abc", name: "report.pdf", size: 5MB}
    2. FileRenamed {id: "abc", new_name: "Q4 Report.pdf"}
    3. FileDownloaded {id: "abc", user: "usr_999"}
    4. FileDownloaded {id: "abc", user: "usr_888"}
    ... (47 download events)
    
  Current state = replay all events
```

### When Event Sourcing Makes Sense

| Good Fit | Bad Fit |
|----------|---------|
| Audit trail required (finance, compliance) | Simple CRUD with no history needs |
| Need to replay/rebuild state | High-frequency updates (counters) |
| Multiple views of same data | Team unfamiliar with the pattern |
| Temporal queries ("state at time T") | Simple domain model |

### GhostDrop's Approach

**Not full event sourcing** — too complex for the team size. But event-driven communication between services using Kafka as the event bus. Events are retained for 7 days (replay window for new consumers).

---

## Concept: CQRS (Command Query Responsibility Segregation)

Separate the write model from the read model.

```
┌──────────────┐                    ┌──────────────┐
│   Commands   │                    │   Queries    │
│  (writes)    │                    │  (reads)     │
└──────┬───────┘                    └──────┬───────┘
       │                                   │
       ▼                                   ▼
┌──────────────┐     events         ┌──────────────┐
│  Write Model │────────────────────│  Read Model  │
│  (Postgres)  │                    │  (Redis/ES)  │
│  Normalized  │                    │ Denormalized │
└──────────────┘                    └──────────────┘
```

### GhostDrop Example: File Activity Feed

```python
# Write side: Upload service writes to Postgres and publishes event
def upload_file(user_id, file_data):
    file = db.insert_file(file_data)
    publish_event("file.uploaded", {"file_id": file.id, "user_id": user_id})
    return file

# Read side: Activity feed consumer builds a denormalized view
class ActivityFeedConsumer:
    def handle_event(self, event):
        match event["type"]:
            case "file.uploaded":
                redis.lpush(f"feed:{event['data']['user_id']}", json.dumps({
                    "action": "uploaded",
                    "file_name": event["data"]["filename"],
                    "timestamp": event["timestamp"],
                }))
                redis.ltrim(f"feed:{event['data']['user_id']}", 0, 99)
            
            case "file.shared":
                redis.lpush(f"feed:{event['data']['recipient_id']}", json.dumps({
                    "action": "received_share",
                    "from": event["data"]["sharer_name"],
                    "file_name": event["data"]["filename"],
                    "timestamp": event["timestamp"],
                }))

# Query side: Fast read from denormalized store
def get_activity_feed(user_id: str):
    return redis.lrange(f"feed:{user_id}", 0, 19)  # Last 20 activities
```

---

## Concept: Eventual Consistency in Practice

With event-driven architecture, consumers process events asynchronously. The system is eventually consistent.

```
t=0ms:    User uploads file → write to DB (committed)
t=5ms:    Event published to Kafka
t=50ms:   Virus scanner picks up event
t=100ms:  Thumbnail generator picks up event
t=200ms:  Analytics consumer picks up event
t=3000ms: Virus scan complete → status updated

Window: 0-3000ms where different views disagree
  - DB says: file exists (status: processing)
  - Analytics says: upload counted
  - Thumbnail says: not yet generated
  - Virus scan says: not yet scanned
```

### Handling Eventual Consistency in the UI

```python
# Show processing status to user
@app.get("/api/files/{file_id}")
def get_file(file_id: str):
    file = db.get_file(file_id)
    return {
        "id": file.id,
        "name": file.name,
        "status": file.status,  # "processing", "ready", "quarantined"
        "thumbnail_url": file.thumbnail_url or None,  # null until generated
        "scan_status": file.scan_status,  # "pending", "clean", "infected"
    }
```

---

## GhostDrop Event Schema

```json
{
  "event_id": "evt_abc123",
  "type": "file.uploaded",
  "version": "1.0",
  "timestamp": "2024-01-20T14:23:45.123Z",
  "source": "upload-service",
  "data": {
    "file_id": "file_xyz789",
    "user_id": "usr_4821",
    "filename": "presentation.pptx",
    "size_bytes": 15728640,
    "content_type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "s3_key": "uploads/usr_4821/xyz789/presentation.pptx"
  },
  "metadata": {
    "trace_id": "trace_def456",
    "correlation_id": "corr_ghi789"
  }
}
```

### Event Types

| Topic | Events |
|-------|--------|
| `file.events` | file.uploaded, file.downloaded, file.deleted, file.renamed |
| `share.events` | share.created, share.revoked, share.accessed |
| `user.events` | user.registered, user.upgraded, user.quota_exceeded |

---

## Tradeoffs

| Decision | Gain | Cost |
|----------|------|------|
| Kafka over SQS | Replay, multiple consumers, ordering | Operational complexity |
| Event-driven over point-to-point | Decoupled, add consumers freely | Eventual consistency, harder debugging |
| CQRS for activity feed | Fast reads, optimized per use case | Two models to maintain |
| 7-day retention | New consumers can catch up | Storage cost |

---

## Why Not Just...

**"Why not just use SQS with SNS fan-out?"**
SNS+SQS works for simple fan-out. But you lose: replay (can't reprocess old events), ordering guarantees, and consumer offset management. Kafka gives you a durable, replayable event log.

**"Why not use event sourcing for everything?"**
Event sourcing adds complexity: rebuilding state from events, handling schema evolution, managing snapshots. For GhostDrop, traditional state + event-driven communication is the right balance.

**"Why not just have services call each other's APIs?"**
Tight coupling. If the analytics service is down, should uploads fail? No. Events decouple: the upload service doesn't know or care if analytics is running.

---

## Exercise

GhostDrop wants to add a "storage analytics" feature showing users their storage usage over time (daily breakdown by file type). 

1. What events would you consume?
2. Where would you store the aggregated data?
3. How would you handle the initial backfill for existing users?

<details>
<summary>Hint</summary>

Consume: file.uploaded (add to daily total), file.deleted (subtract from daily total). Store in a time-series table or Redis sorted set keyed by date. For backfill: either replay Kafka events from retention window (7 days), or run a one-time batch job against the database to compute historical aggregates. Going forward, the consumer keeps the view updated in real-time.
</details>

---

## Quick Reference

| Term | Definition |
|------|-----------|
| **Event-Driven** | Services communicate via events, not direct calls |
| **Kafka** | Distributed event streaming platform |
| **Topic** | Named stream of events (like a category) |
| **Partition** | Ordered subset of a topic (parallelism unit) |
| **Consumer Group** | Set of consumers sharing work on a topic |
| **Event Sourcing** | Storing events instead of current state |
| **CQRS** | Separate read and write models |
| **Offset** | Consumer's position in a partition |
| **Replay** | Reprocessing old events from a topic |

---

## What Breaks Next

Event-driven architecture decouples services. Adding new consumers is trivial. The system is more resilient.

But product wants a new feature: shareable short links. Instead of `ghostdrop.io/share/a3f8c2e1-b7d1-4f2a-9c3e-1234567890ab`, they want `gdrop.io/x7Kp2`. At 10M users generating millions of links, you need to design a URL shortener that's fast, unique, and scalable.

You need to think about ID generation and read-heavy optimization.

[← Ch 16](chapter-16-sharding.md) | [Ch 18 →](chapter-18-url-shortener.md)

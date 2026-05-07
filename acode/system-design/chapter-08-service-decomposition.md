# Chapter 8: Service Decomposition

[← Ch 7](chapter-07-read-replicas.md) | [Ch 9 →](chapter-09-cdn-edge.md)

---

## The Crisis

It's Wednesday of week two. The podcast is in 8 days.

**Sana** (Slack, 10:15 AM):
> I need to deploy a fix for the share link expiration bug. But the deploy pipeline runs all tests — upload tests, notification tests, billing tests. 40 minutes. For a one-line fix.

**Kai**:
> I pushed a frontend change that accidentally broke the upload API validation. Didn't know my code touched that path.

**Omar**:
> Last night the notification worker had a memory leak. It took down the entire app because it's the same process.

**Amir** (in the meeting room):
> Everyone wants to split the monolith. But I've seen teams do this wrong and create a distributed monolith that's worse. What do we split, and what stays together?

---

## Architecture (Before — Monolith)

```
┌─────────────────────────────────────────────────────┐
│                  Django Monolith                      │
│                                                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │  Upload   │ │  Share    │ │  Notify  │ │ Billing│ │
│  │  Module   │ │  Module   │ │  Module  │ │ Module │ │
│  └──────────┘ └──────────┘ └──────────┘ └────────┘ │
│                                                       │
│  One codebase. One deploy. One process.              │
└─────────────────────────────────────────────────────┘
```

## Architecture (After — Services)

```
┌──────────┐
│   API    │
│ Gateway  │
└────┬─────┘
     │
     ├──────────────────────────────────────┐
     │              │              │         │
     ▼              ▼              ▼         ▼
┌──────────┐  ┌──────────┐  ┌────────┐  ┌────────┐
│  Upload   │  │  Share    │  │ Notify │  │Billing │
│  Service  │  │  Service  │  │Service │  │Service │
└──────────┘  └──────────┘  └────────┘  └────────┘
     │              │              │         │
     ▼              ▼              ▼         ▼
┌──────────┐  ┌──────────┐  ┌────────┐  ┌────────┐
│ Files DB  │  │ Share DB  │  │  SQS   │  │Bill DB │
└──────────┘  └──────────┘  └────────┘  └────────┘
```

---

## Concept: Finding Service Boundaries

### The Wrong Way: Split by Technical Layer

```
❌ "API Service" + "Database Service" + "Queue Service"
   (This is just the monolith with network calls between layers)
```

### The Right Way: Split by Business Domain

```
✓ "Upload Service" — owns file storage and processing
✓ "Share Service" — owns links, permissions, expiration
✓ "Notification Service" — owns emails, push, webhooks
✓ "User Service" — owns profiles, auth, quotas
```

### How to Identify Boundaries

| Signal | Meaning |
|--------|---------|
| Different teams own different modules | Natural team boundary |
| Module changes independently | Low coupling |
| Module has its own data | Can own its database |
| Module has different scaling needs | Benefits from independent scaling |
| Module has different uptime requirements | Isolate failure domains |

### GhostDrop's Boundaries

```
┌─────────────────────────────────────────────────┐
│ Core (stays together for now):                   │
│   - File upload/download                         │
│   - File metadata                                │
│   - User authentication                          │
│   - Share link creation                          │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Extract first:                                   │
│   - Notification service (email, push)           │
│   - File processing (virus scan, thumbnails)     │
│   - Analytics (view counts, download stats)      │
└─────────────────────────────────────────────────┘
```

**Why extract notifications first?** It's already async (queue-based), has no shared state with the core app, and its failure shouldn't affect uploads/downloads.

---

## Concept: API Gateway

With multiple services, clients need a single entry point.

```
Without Gateway:
  Client → Upload Service (port 8001)
  Client → Share Service (port 8002)
  Client → User Service (port 8003)
  (Client must know about every service)

With Gateway:
  Client → API Gateway → routes to correct service
  (Client knows one URL)
```

### Gateway Responsibilities

| Function | Example |
|----------|---------|
| **Routing** | `/api/files/*` → Upload Service |
| **Auth** | Validate JWT before forwarding |
| **Rate limiting** | 100 req/min per API key |
| **SSL termination** | HTTPS at the edge |
| **Request transformation** | Add internal headers |
| **Response aggregation** | Combine data from multiple services |

### GhostDrop's Gateway (Kong/AWS API Gateway)

```yaml
# kong.yml (simplified)
services:
  - name: upload-service
    url: http://upload-svc:8000
    routes:
      - paths: ["/api/files", "/api/upload"]
        methods: ["GET", "POST", "DELETE"]

  - name: share-service
    url: http://share-svc:8000
    routes:
      - paths: ["/api/shares", "/api/links"]
        methods: ["GET", "POST", "PUT", "DELETE"]

  - name: notification-service
    url: http://notify-svc:8000
    routes:
      - paths: ["/api/notifications"]
        methods: ["GET", "POST"]

plugins:
  - name: jwt
    config:
      secret_is_base64: false
  - name: rate-limiting
    config:
      minute: 100
```

---

## Concept: Inter-Service Communication

### Synchronous (HTTP/gRPC)

```
Upload Service ──HTTP──→ User Service: "Is this user's quota exceeded?"
                ←────── Response: {"exceeded": false, "remaining": "4.2GB"}
```

**When to use**: Need an immediate answer. Request-response pattern.

### Asynchronous (Events/Messages)

```
Upload Service ──publishes──→ [Queue] ──→ Notification Service
               "file.uploaded"              (sends email whenever it gets to it)
```

**When to use**: Don't need immediate response. Fire-and-forget. Decoupled.

### Comparison

| | Sync (HTTP) | Async (Queue) |
|---|---|---|
| Latency | Immediate response | Eventually processed |
| Coupling | Caller depends on callee being up | Caller independent |
| Failure | Callee down = caller fails | Callee down = messages queue up |
| Debugging | Request/response trace | Harder to trace across queues |
| Consistency | Strong (if needed) | Eventual |

### GhostDrop's Communication Map

```
Upload Service:
  → User Service (sync): check quota before upload
  → Queue (async): "file.uploaded" event
  
Notification Service:
  ← Queue (async): listens for "file.uploaded", "file.shared"
  → SendGrid (sync): send email

Share Service:
  → Upload Service (sync): verify file exists
  → Queue (async): "link.created" event
```

---

## Concept: When NOT to Split

**Amir**: "Should we split the share service from the upload service?"

Not yet. Here's why:

| Don't Split When... | GhostDrop Example |
|--------------------|--------------------|
| Services would call each other constantly | Share needs file metadata on every request |
| Data is tightly coupled | Share permissions reference file IDs |
| Team is small (< 8 engineers) | 4 engineers can't maintain 6 services |
| You'd need distributed transactions | Creating a share + updating file in one operation |
| You're not sure about boundaries | Wait until the domain is clearer |

**Rule of thumb**: If two services would need a synchronous call on >50% of requests, they should probably be one service.

---

## GhostDrop Implementation

### Phase 1: Extract Notification Service

```python
# notification_service/main.py
from fastapi import FastAPI
import boto3

app = FastAPI()
sqs = boto3.client('sqs')

@app.on_event("startup")
async def start_consumer():
    """Poll SQS for notification events"""
    asyncio.create_task(consume_messages())

async def consume_messages():
    while True:
        messages = sqs.receive_message(
            QueueUrl=NOTIFICATION_QUEUE,
            WaitTimeSeconds=20,
        )
        for msg in messages.get('Messages', []):
            event = json.loads(msg['Body'])
            await handle_event(event)
            sqs.delete_message(...)

async def handle_event(event: dict):
    match event['type']:
        case 'file.uploaded':
            await send_upload_confirmation(event['user_id'], event['file_name'])
        case 'file.shared':
            await send_share_notification(event['recipient_email'], event['link'])
        case 'quota.warning':
            await send_quota_alert(event['user_id'], event['usage_percent'])
```

### Phase 2: Extract File Processing

```python
# processing_service/main.py
# Already mostly separate (runs as SQS worker)
# Just needs its own deployment pipeline and scaling config
```

### What Stays in the Monolith (For Now)

- File upload/download API
- Share link CRUD
- User authentication
- File metadata

These are tightly coupled and the team is small. Split later when team grows.

---

## Tradeoffs

| Decision | Gain | Cost |
|----------|------|------|
| Extract notifications | Independent deploy, isolated failures | Network calls, eventual consistency |
| Keep core monolith | Simple debugging, ACID transactions | Slower deploys, coupled scaling |
| API Gateway | Single entry point, centralized auth | Another component, slight latency |
| Async communication | Decoupled, resilient | Harder to debug, eventual consistency |

---

## Why Not Just...

**"Why not go full microservices from day one?"**
With 4 engineers and 8 days until the podcast, you'd spend all your time on service mesh, distributed tracing, and deployment pipelines instead of scaling. Extract what hurts. Keep what works.

**"Why not use a service mesh (Istio)?"**
Istio adds 10-20ms latency per hop, requires Kubernetes expertise, and takes weeks to configure properly. At 3 services, direct HTTP calls with a simple retry library are fine.

**"Why not share one database across services?"**
Shared databases create hidden coupling. If the notification service runs a heavy query, it slows down the upload service. Each service should own its data. But for GhostDrop's current size, the core monolith sharing one DB is fine.

---

## Exercise

GhostDrop wants to add a "file preview" feature (PDF rendering, video thumbnails, document conversion). This is CPU-intensive and takes 5-30 seconds per file.

1. Should this be part of the monolith or a separate service?
2. How would it communicate with the upload service?
3. What happens if the preview service is overloaded?

<details>
<summary>Hint</summary>

Separate service. It has different scaling needs (CPU-intensive, bursty), different failure modes (preview failing shouldn't block uploads), and different deployment cadence (ML model updates). Communication: async via SQS. Upload service publishes "file.uploaded" event, preview service consumes it. If overloaded: auto-scale workers, queue buffers the backlog, users see "preview generating..." status.
</details>

---

## Quick Reference

| Term | Definition |
|------|-----------|
| **Monolith** | Single deployable unit containing all functionality |
| **Service** | Independent deployable unit with its own data |
| **API Gateway** | Single entry point that routes to backend services |
| **Service Boundary** | The line between what one service owns vs another |
| **Sync Communication** | Request-response (HTTP, gRPC) |
| **Async Communication** | Fire-and-forget (queues, events) |
| **Distributed Monolith** | Services that must deploy together (worst of both worlds) |
| **Domain-Driven Design** | Splitting by business capability, not technical layer |

---

## What Breaks Next

Notification service is extracted. File processing is independent. Deploys are faster. The core app is leaner.

But users in Asia-Pacific are complaining. Page loads take 800ms. API responses are fast (50ms) but static assets and file previews are slow. Everything is served from us-east-1.

"We need to get closer to our users," Omar says.

You need a CDN strategy.

[← Ch 7](chapter-07-read-replicas.md) | [Ch 9 →](chapter-09-cdn-edge.md)

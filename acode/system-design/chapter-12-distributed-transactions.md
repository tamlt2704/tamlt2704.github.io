# Chapter 12: Distributed Transactions

[← Ch 11](chapter-11-circuit-breakers.md) | [Ch 13 →](chapter-13-consistency.md)

---

## The Crisis

Monday morning, week three. Podcast in 4 days.

**Sana** (Slack, 9:30 AM):
> Found a bug. User uploaded a file. S3 upload succeeded. Database insert succeeded. But the virus scan worker crashed mid-scan. The file is marked "ready" in the database but was never scanned. It's a malware risk.

**Omar**:
> Worse: I found 47 files in this state from last week's worker crash.

**Kai**:
> Also, a user created a share link. The link was saved to the database, but the notification email failed. The recipient never got the link. User thinks it was sent.

**Amir**:
> In the monolith, this was one database transaction. Now that we have separate services, how do we keep things consistent?

---

## The Problem

In a monolith with one database:

```python
# Monolith: one transaction, all-or-nothing
with db.transaction():
    file = db.insert_file(metadata)
    db.update_quota(user_id, file.size)
    db.create_share_link(file.id, recipient)
    # If anything fails, everything rolls back
```

With separate services:

```python
# Distributed: multiple systems, no shared transaction
s3.upload(file)                    # Step 1: S3 (can't roll back easily)
db.insert_file(metadata)           # Step 2: Postgres
queue.send("scan_file", file.id)   # Step 3: SQS
notify.send(recipient, link)       # Step 4: Email service

# What if Step 3 succeeds but Step 4 fails?
# What if Step 1 succeeds but Step 2 fails?
# There's no "rollback" across S3 + Postgres + SQS + Email
```

---

## Concept: Two-Phase Commit (2PC) — And Why Not

### How 2PC Works

```
Coordinator → All participants: "PREPARE to commit"
Participant A: "READY"
Participant B: "READY"
Coordinator → All participants: "COMMIT"
All commit.

If any participant says "NOT READY":
Coordinator → All: "ABORT"
All roll back.
```

### Why 2PC Doesn't Work Here

| Problem | Impact |
|---------|--------|
| Coordinator is a SPOF | If coordinator dies mid-commit, participants are stuck |
| Blocking | All participants lock resources until commit/abort |
| Latency | Two network round-trips minimum |
| Heterogeneous systems | S3, SQS, and email don't support 2PC |
| Availability | Any participant down = entire transaction blocked |

**Bottom line**: 2PC works for databases talking to databases. It doesn't work when your "transaction" spans S3, SQS, PostgreSQL, and SendGrid.

---

## Concept: Saga Pattern

A saga is a sequence of local transactions. If one step fails, execute **compensating transactions** to undo previous steps.

### GhostDrop Upload Saga

```
Step 1: Upload to S3
Step 2: Insert file record (status: "processing")
Step 3: Queue virus scan
Step 4: Virus scan completes → update status to "ready"

If Step 3 fails:
  Compensate Step 2: Mark file as "failed"
  Compensate Step 1: Delete from S3

If Step 4 fails (virus found):
  Compensate Step 2: Mark file as "quarantined"
  Compensate Step 1: Move to quarantine bucket
```

### Choreography vs Orchestration

#### Choreography (Event-Driven)

Each service listens for events and reacts. No central coordinator.

```
Upload Service publishes: "file.uploaded"
    │
    ├──→ Scan Service hears it → scans → publishes "file.scanned"
    │
    ├──→ Thumbnail Service hears it → generates → publishes "thumb.created"
    │
    └──→ Quota Service hears it → updates quota

Scan Service publishes: "file.infected"
    │
    └──→ Upload Service hears it → quarantines file
```

**Pros**: Decoupled, no SPOF, services are independent
**Cons**: Hard to track overall progress, complex failure flows, no single view of the saga

#### Orchestration (Central Coordinator)

One service coordinates the entire flow.

```
┌─────────────────────────────────────────┐
│           Upload Orchestrator            │
│                                          │
│  1. Upload to S3         ✓              │
│  2. Save metadata        ✓              │
│  3. Request virus scan   ✓              │
│  4. Wait for scan result  ⏳             │
│  5. Update status        (pending)      │
│                                          │
│  On failure at step N:                   │
│    Run compensations for steps N-1...1   │
└─────────────────────────────────────────┘
```

**Pros**: Clear flow, easy to monitor, centralized error handling
**Cons**: Orchestrator is a coupling point, can become a bottleneck

### GhostDrop's Choice

**Orchestration** for the upload flow (critical path, needs clear status tracking).
**Choreography** for notifications (fire-and-forget, eventual delivery is fine).

---

## Concept: Idempotency Keys

With at-least-once delivery, operations might execute twice. Idempotency keys prevent duplicate effects.

```python
# Client sends an idempotency key with the request
POST /api/upload
Headers:
  Idempotency-Key: "upload-abc123-attempt-1"

# Server checks if this key was already processed
def upload_file(request):
    idem_key = request.headers.get("Idempotency-Key")
    
    # Check if already processed
    existing = db.get_idempotency_record(idem_key)
    if existing:
        return existing.response  # Return same response as before
    
    # Process the request
    result = do_upload(request)
    
    # Store the result keyed by idempotency key
    db.save_idempotency_record(idem_key, result, ttl=24*3600)
    
    return result
```

### Idempotency in Practice

| Operation | Naturally Idempotent? | How to Make Idempotent |
|-----------|----------------------|------------------------|
| `PUT /files/123` (update) | Yes (same result) | N/A |
| `POST /files` (create) | No (creates duplicates) | Idempotency key |
| `DELETE /files/123` | Yes (already gone) | N/A |
| `POST /shares` (create link) | No | Idempotency key |
| Increment counter | No | Use "set to value" instead |
| Send email | No | Track sent message IDs |

---

## Concept: Compensation

When a saga step fails, you can't "rollback" — you **compensate**.

```python
class UploadSaga:
    def __init__(self, file_data, user_id):
        self.file_data = file_data
        self.user_id = user_id
        self.completed_steps = []
    
    def execute(self):
        try:
            # Step 1: Upload to S3
            s3_key = self._upload_to_s3()
            self.completed_steps.append(("s3_upload", s3_key))
            
            # Step 2: Create DB record
            file_id = self._create_db_record(s3_key)
            self.completed_steps.append(("db_record", file_id))
            
            # Step 3: Update quota
            self._update_quota()
            self.completed_steps.append(("quota_update", self.user_id))
            
            # Step 4: Queue processing
            self._queue_processing(file_id, s3_key)
            self.completed_steps.append(("queue_processing", file_id))
            
            return {"file_id": file_id, "status": "processing"}
            
        except Exception as e:
            self._compensate()
            raise UploadFailed(f"Upload saga failed: {e}")
    
    def _compensate(self):
        """Undo completed steps in reverse order."""
        for step_name, step_data in reversed(self.completed_steps):
            try:
                match step_name:
                    case "queue_processing":
                        pass  # Can't un-queue, but worker checks file status
                    case "quota_update":
                        db.execute("UPDATE users SET quota_used = quota_used - %s", 
                                   self.file_data.size)
                    case "db_record":
                        db.execute("UPDATE files SET status = 'failed' WHERE id = %s",
                                   step_data)
                    case "s3_upload":
                        s3.delete_object(Bucket="ghostdrop-files", Key=step_data)
            except Exception as comp_error:
                # Log compensation failure — needs manual intervention
                log.error(f"Compensation failed for {step_name}: {comp_error}")
                alert_ops(f"Manual cleanup needed: {step_name} = {step_data}")
```

---

## GhostDrop: The Share Link Saga

```python
class ShareLinkSaga:
    """Create a share link: verify file → create link → notify recipient."""
    
    def execute(self, file_id: str, recipient_email: str, user_id: str):
        # Step 1: Verify file exists and user owns it
        file = self._verify_ownership(file_id, user_id)
        
        # Step 2: Create share link in database
        link = self._create_link(file_id, recipient_email)
        self.completed_steps.append(("link_created", link.id))
        
        # Step 3: Send notification (async, best-effort)
        try:
            self._notify_recipient(recipient_email, link.url)
        except NotificationFailed:
            # Don't compensate — link is valid, notification can retry
            self._queue_retry_notification(recipient_email, link.url)
        
        return {"link_id": link.id, "url": link.url, "notified": True}
```

**Key insight**: Not every step needs compensation. If the share link is created but the email fails, the link is still valid. Queue the email for retry rather than rolling back the link.

---

## Tradeoffs

| Decision | Gain | Cost |
|----------|------|------|
| Saga over 2PC | Works across heterogeneous systems, non-blocking | Complex compensation logic |
| Orchestration for uploads | Clear status tracking, centralized error handling | Orchestrator coupling |
| Choreography for notifications | Decoupled, resilient | Harder to debug |
| Idempotency keys | Safe retries, no duplicates | Storage for key records |
| Compensation over rollback | Works with external systems (S3, email) | Compensation can fail too |

---

## Why Not Just...

**"Why not use a distributed transaction manager?"**
They exist (e.g., Seata, Atomikos) but add significant complexity, latency, and operational burden. For GhostDrop's scale and team size, explicit sagas are simpler to understand and debug.

**"Why not just retry until it works?"**
Some failures are permanent (file too large, user doesn't exist, virus detected). Retrying forever wastes resources. Sagas distinguish between transient failures (retry) and permanent failures (compensate).

**"Why not make everything eventually consistent and not worry about it?"**
Some operations have business requirements for consistency. A file marked "ready" that was never virus-scanned is a security risk. A user charged for storage they don't have is a billing error. Sagas give you controlled eventual consistency.

---

## Exercise

GhostDrop adds a "paid storage upgrade" flow:
1. Charge the user's credit card (Stripe)
2. Update their storage quota in the database
3. Send a confirmation email

Design the saga:
1. What's the compensation for each step?
2. What if the charge succeeds but the quota update fails?
3. What if the email fails — should you refund?

<details>
<summary>Hint</summary>

Compensations: (1) Charge → Refund via Stripe. (2) Quota update → Decrement quota. (3) Email → Queue for retry (don't refund just because email failed). If charge succeeds but quota fails: refund the charge. The user shouldn't pay for something they didn't receive. If email fails: don't compensate — the upgrade is valid, just retry the email. Key principle: compensate when the user would be harmed by the inconsistency.
</details>

---

## Quick Reference

| Term | Definition |
|------|-----------|
| **Saga** | Sequence of local transactions with compensating actions |
| **Compensation** | Action that undoes the effect of a previous step |
| **Choreography** | Services react to events independently (no coordinator) |
| **Orchestration** | Central coordinator manages the saga flow |
| **Idempotency Key** | Client-provided key ensuring an operation executes only once |
| **2PC** | Two-Phase Commit — distributed transaction protocol (blocking) |
| **At-Least-Once** | Message may be delivered multiple times |
| **Exactly-Once** | Message delivered exactly once (very hard to achieve) |

---

## What Breaks Next

Sagas handle multi-step operations. Idempotency keys prevent duplicates. Compensation handles failures.

But a new problem emerges: the cache says a file exists, but S3 says it doesn't. The database says a share link is active, but the cache says it's expired. Different parts of the system disagree about the current state.

"We have a consistency problem," Sana says. "And it's not just about transactions — it's about what 'consistent' even means in a distributed system."

You need to understand consistency models.

[← Ch 11](chapter-11-circuit-breakers.md) | [Ch 13 →](chapter-13-consistency.md)

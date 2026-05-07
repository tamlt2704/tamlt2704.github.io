# Chapter 6: Message Queues

[← Ch 5](chapter-05-caching.md) | [Ch 7 →](chapter-07-read-replicas.md)

---

## The Crisis

Uploads are slow. Not network-slow — processing-slow.

**Kai** (Slack, 3:22 PM):
> Users are complaining. Upload a 50MB file, wait 12 seconds for the spinner. They think it failed and retry. Now we have duplicate files.

**Sana**:
> The upload endpoint does everything synchronously: save to S3, scan for viruses, generate thumbnail, extract metadata, update database, send notification email. All in one request.

```python
# Current upload handler (blocking everything)
@app.post("/upload")
def upload_file(file: UploadFile):
    s3_key = save_to_s3(file)           # 2-3 seconds
    scan_result = virus_scan(file)       # 3-4 seconds
    thumbnail = generate_thumbnail(file) # 2-3 seconds
    metadata = extract_metadata(file)    # 1-2 seconds
    db.save_file_record(...)             # 50ms
    send_email_notification(...)         # 500ms
    return {"status": "complete"}        # Total: 8-12 seconds
```

**Amir**:
> The user only cares that the file is saved. Everything else can happen after we respond.

---

## Architecture (Before)

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │────→│    LB    │────→│  Worker  │
└──────────┘     └──────────┘     └──────────┘
                                       │
                              (blocks for 12 seconds)
                                       │
                                       ▼
                              ┌─────────────────┐
                              │ S3 + Virus Scan  │
                              │ + Thumbnail      │
                              │ + Metadata       │
                              │ + Email          │
                              └─────────────────┘
```

## Architecture (After)

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │────→│    LB    │────→│  Web App │──→ Save to S3 + DB
└──────────┘     └──────────┘     └──────────┘   (responds in 2s)
                                       │
                                       │ publish message
                                       ▼
                              ┌─────────────────┐
                              │  Message Queue   │
                              │   (SQS/Rabbit)   │
                              └────────┬────────┘
                                       │
                         ┌─────────────┼─────────────┐
                         ▼             ▼             ▼
                  ┌────────────┐ ┌──────────┐ ┌──────────┐
                  │Virus Worker│ │Thumb Wrkr│ │Email Wrkr│
                  └────────────┘ └──────────┘ └──────────┘
```

---

## Concept: Message Queues

A message queue decouples producers (who create work) from consumers (who do work).

```
Producer → [Queue] → Consumer

- Producer doesn't wait for consumer
- Consumer processes at its own pace
- Queue buffers the difference in speed
```

### Queue vs Direct Call

| | Synchronous (Direct) | Asynchronous (Queue) |
|---|---|---|
| Latency | Caller waits | Caller returns immediately |
| Coupling | Caller knows about callee | Caller only knows about queue |
| Failure | Callee down = caller fails | Callee down = messages wait |
| Scaling | Must scale together | Scale independently |
| Ordering | Guaranteed | Best-effort (usually FIFO) |

---

## Concept: Queue Technologies

| Technology | Type | Best For |
|-----------|------|----------|
| **AWS SQS** | Managed, pull-based | Simple job queues, no ops |
| **RabbitMQ** | Self-hosted, push-based | Complex routing, priorities |
| **Redis (lists)** | In-memory | Simple queues, already have Redis |
| **Kafka** | Distributed log | High throughput, event streaming |

### GhostDrop's Choice: SQS

- Managed (no ops)
- Scales automatically
- Built-in dead letter queue
- $0.40 per million messages
- We don't need complex routing or ordering guarantees

---

## Concept: Workers and Processing

```python
# worker.py — processes messages from the queue
import boto3
import json

sqs = boto3.client('sqs')
QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/123/ghostdrop-uploads"

def process_messages():
    while True:
        response = sqs.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20,  # Long polling
        )
        
        for message in response.get('Messages', []):
            body = json.loads(message['Body'])
            
            try:
                process_upload(body)
                # Success — delete from queue
                sqs.delete_message(
                    QueueUrl=QUEUE_URL,
                    ReceiptHandle=message['ReceiptHandle']
                )
            except Exception as e:
                # Failed — message becomes visible again after timeout
                log.error(f"Failed to process {body['file_id']}: {e}")

def process_upload(event: dict):
    file_id = event['file_id']
    s3_key = event['s3_key']
    
    # These run sequentially but DON'T block the web request
    virus_scan(s3_key)
    generate_thumbnail(s3_key, file_id)
    extract_metadata(s3_key, file_id)
    send_notification(event['user_id'], file_id)
    
    db.update_file_status(file_id, status="ready")
```

### The New Upload Handler

```python
@app.post("/upload")
def upload_file(file: UploadFile, user: User):
    # Only do the minimum synchronously
    s3_key = save_to_s3(file)  # 2-3 seconds
    file_record = db.create_file(
        user_id=user.id,
        s3_key=s3_key,
        status="processing",  # Not "ready" yet
    )
    
    # Queue everything else
    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps({
            "file_id": file_record.id,
            "s3_key": s3_key,
            "user_id": user.id,
            "filename": file.filename,
        })
    )
    
    return {"file_id": file_record.id, "status": "processing"}
    # Response time: 2-3 seconds instead of 12
```

---

## Concept: Dead Letter Queues (DLQ)

What happens when a message fails repeatedly?

```
Main Queue → Worker fails → Message returns to queue
          → Worker fails again → Message returns
          → Worker fails 3rd time → Message moves to DLQ
```

```python
# SQS DLQ configuration
{
    "RedrivePolicy": {
        "deadLetterTargetArn": "arn:aws:sqs:us-east-1:123:ghostdrop-dlq",
        "maxReceiveCount": 3  # After 3 failures, move to DLQ
    }
}
```

**Why not just retry forever?**
- Poison messages (malformed data) will never succeed
- Infinite retries waste compute
- DLQ lets you inspect failures and fix them manually

**Omar**: "I set up a CloudWatch alarm on DLQ depth. If messages pile up, we get paged."

---

## Concept: At-Least-Once Delivery

SQS guarantees **at-least-once** delivery. A message might be delivered twice if:
- Worker processes it but crashes before deleting it
- Network timeout on the delete call
- SQS internal retry

**This means your workers must be idempotent.**

```python
def generate_thumbnail(s3_key: str, file_id: str):
    # Idempotent: if thumbnail already exists, skip
    if s3.head_object(Bucket="ghostdrop-thumbs", Key=f"{file_id}.jpg"):
        return  # Already done
    
    # Generate and upload
    thumb = create_thumbnail(s3_key)
    s3.put_object(Bucket="ghostdrop-thumbs", Key=f"{file_id}.jpg", Body=thumb)
```

---

## Concept: Backpressure

What if messages arrive faster than workers can process them?

```
Incoming: 500 messages/sec
Processing: 200 messages/sec
Queue depth grows: 300/sec accumulation

After 1 hour: 1,080,000 messages backlogged
```

### Solutions

| Strategy | How | Tradeoff |
|----------|-----|----------|
| **Auto-scale workers** | More workers when queue depth grows | Cost, startup time |
| **Rate limit producers** | Reject uploads when queue is deep | Users see errors |
| **Batch processing** | Process 10 messages at once | Complexity |
| **Priority queues** | VIP users processed first | Fairness concerns |

### GhostDrop's Approach

Auto-scale workers based on queue depth:

```yaml
# Auto-scaling policy
scaling_policy:
  metric: ApproximateNumberOfMessagesVisible
  target: 100  # Keep queue under 100 messages
  min_workers: 2
  max_workers: 20
  scale_up_cooldown: 60s
  scale_down_cooldown: 300s
```

---

## GhostDrop Implementation Results

| Metric | Before (Sync) | After (Async) |
|--------|--------------|---------------|
| Upload response time | 8-12 seconds | 2-3 seconds |
| Web worker utilization | 95% (blocked) | 40% (free for other requests) |
| Throughput | 50 uploads/min | 200 uploads/min |
| User retries | 23% retry rate | 2% retry rate |
| Processing cost | Web server CPU | Cheap worker instances |

---

## Tradeoffs

| Decision | Gain | Cost |
|----------|------|------|
| Async processing | Fast response, decoupled scaling | Eventual consistency (file "processing" state) |
| SQS over RabbitMQ | Zero ops, auto-scaling | No complex routing, ~100ms delivery latency |
| DLQ | Failed messages don't block queue | Must monitor and handle DLQ manually |
| At-least-once | No message loss | Must design idempotent workers |

---

## Why Not Just...

**"Why not use a background thread in the web process?"**
If the web process crashes, the background work is lost. No retry, no visibility, no scaling. The queue persists messages independently.

**"Why not use Celery with Redis as broker?"**
You could. But Redis isn't durable — if it restarts, queued messages are lost. SQS persists messages for 14 days. For a file-sharing app, losing upload processing jobs is unacceptable.

**"Why not process everything in a cron job every minute?"**
Latency. Users would wait up to 60 seconds for their file to be "ready." With a queue, processing starts within seconds of upload.

**"Why not use Lambda for workers?"**
Actually, that's a great option. Lambda + SQS is a natural fit. GhostDrop will likely move to this. For now, ECS workers give more control over the virus scanning binary.

---

## Exercise

GhostDrop adds a "share via email" feature. When a user shares a file, the system sends an email to the recipient. The email service (SendGrid) has a rate limit of 100 emails/second.

1. What happens if 500 users share files simultaneously?
2. How would you design the email sending to respect the rate limit?
3. What if SendGrid is down for 5 minutes?

<details>
<summary>Hint</summary>

Put email sends on a queue with a rate-limited consumer (process max 100/sec). If SendGrid is down, messages stay in the queue and retry with exponential backoff. After 3 failures, move to DLQ. When SendGrid recovers, the backlog drains automatically. The queue acts as a buffer between your burst traffic and SendGrid's rate limit.
</details>

---

## Quick Reference

| Term | Definition |
|------|-----------|
| **Message Queue** | Buffer between producers and consumers |
| **Producer** | Service that creates messages (publishes work) |
| **Consumer/Worker** | Service that processes messages |
| **Dead Letter Queue** | Queue for messages that failed processing repeatedly |
| **At-Least-Once** | Message delivered one or more times (may duplicate) |
| **Idempotent** | Operation that produces same result if executed multiple times |
| **Backpressure** | When consumers can't keep up with producers |
| **Long Polling** | Consumer waits for messages (vs busy-polling) |
| **Visibility Timeout** | Time a message is hidden after being received |

---

## What Breaks Next

Uploads are fast. Background workers handle processing. The queue buffers traffic spikes.

But the database is still getting hammered. Not by the upload processing — by reads. Every page load queries user profiles, file lists, permissions. Caching helps, but cache misses still hit the single primary database.

"Our read-to-write ratio is 8:1," Sana says. "We need to split the read load off the primary."

You need read replicas.

[← Ch 5](chapter-05-caching.md) | [Ch 7 →](chapter-07-read-replicas.md)

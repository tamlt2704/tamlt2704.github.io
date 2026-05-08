# Chapter 8: Design a Notification System

[← Video Platform](./chapter-07-video.md) | [Next: Payment System →](./chapter-09-payments.md)

---

## The Question

> "Design a notification system that can send push notifications, emails, and SMS to millions of users. It should support templates, user preferences, rate limiting per user, priority levels, and delivery tracking."

---

## Step 1: Requirements & Scope

**Functional:**
- Multi-channel: push (iOS/Android), email, SMS
- Template-based notifications with variable substitution
- User preferences (opt-in/out per channel, per category)
- Priority levels (critical, high, normal, low)
- Delivery tracking (sent, delivered, opened, failed)
- Rate limiting per user (no spam)

**Non-functional:**
- 500M users, 1B notifications/day
- Critical notifications delivered within 30 seconds
- At-least-once delivery (never silently drop)
- Graceful degradation under load (delay low-priority, never drop critical)

---

## Step 2: Estimation

| Metric | Calculation | Result |
|--------|-------------|--------|
| Notifications/sec | 1B / 86400 | ~12,000/sec |
| Peak (3x) | 12,000 × 3 | ~36,000/sec |
| Email volume | 1B × 40% email | 400M emails/day |
| Push volume | 1B × 50% push | 500M pushes/day |
| SMS volume | 1B × 10% SMS | 100M SMS/day |

---

## Step 3: API Design

```
POST /api/v1/notifications/send
  Body: {
    "user_ids": ["u_123", "u_456"],
    "template_id": "order_shipped",
    "variables": { "order_id": "ORD-789", "eta": "2 days" },
    "channels": ["push", "email"],
    "priority": "high"
  }
  Response: { "notification_id": "n_001", "status": "queued" }

GET /api/v1/notifications/{notification_id}/status
  Response: { "push": "delivered", "email": "opened", "sms": "not_sent" }

PUT /api/v1/users/{user_id}/preferences
  Body: { "email": { "marketing": false, "transactional": true }, ... }
```

---

## Step 4: Data Model

**Notification Record (NoSQL — high write volume):**

| Field | Type |
|-------|------|
| notification_id (PK) | UUID |
| user_id | UUID |
| template_id | VARCHAR |
| channel | ENUM (push, email, sms) |
| priority | ENUM (critical, high, normal, low) |
| status | ENUM (queued, sent, delivered, opened, failed) |
| created_at | TIMESTAMP |
| sent_at | TIMESTAMP |

**User Preferences (SQL):**

| Field | Type |
|-------|------|
| user_id (PK) | UUID |
| channel | VARCHAR |
| category | VARCHAR |
| enabled | BOOLEAN |
| quiet_hours_start | TIME |
| quiet_hours_end | TIME |

---

## Step 5: High-Level Architecture

```
┌──────────────┐     ┌─────────────────┐     ┌──────────────────┐
│  Services    │────▶│  Notification   │────▶│  Priority Queue  │
│  (triggers)  │     │  API            │     │  (Kafka/SQS)     │
└──────────────┘     └─────────────────┘     └────────┬─────────┘
                                                      │
                            ┌──────────────────────────┼────────────────┐
                            ▼                          ▼                ▼
                   ┌──────────────┐          ┌──────────────┐  ┌──────────────┐
                   │ Push Worker  │          │ Email Worker │  │  SMS Worker  │
                   │ (APNs/FCM)  │          │ (SES/SMTP)   │  │ (Twilio)     │
                   └──────────────┘          └──────────────┘  └──────────────┘
                            │                          │                │
                            └──────────────────────────┼────────────────┘
                                                       ▼
                                              ┌──────────────┐
                                              │  Delivery    │
                                              │  Tracker     │
                                              └──────────────┘
```

---

## Step 6: Deep Dive

### Notification Processing Pipeline

1. **Service triggers notification** via API (e.g., order service says "order shipped")
2. **Validation:** Check template exists, user exists
3. **Preference check:** Does user want this notification on this channel?
4. **Rate limit check:** Has user received too many notifications recently?
5. **Template rendering:** Substitute variables into template
6. **Queue:** Place in priority queue (separate queues per priority)
7. **Worker picks up:** Send via appropriate channel provider
8. **Track delivery:** Record status from provider callback

### Priority Queues

```
┌─────────────────────────────────────────┐
│  Critical  │  High  │  Normal  │  Low   │
│  (OTP,     │ (order │ (social  │ (mktg, │
│   alerts)  │  ship) │  likes)  │  digest)│
└─────────────────────────────────────────┘
     ▲ processed first                last ▲
```

Workers always drain critical queue first. Under load, low-priority notifications are delayed (never dropped).

### Rate Limiting Per User

Rules to prevent notification fatigue:
- Max 5 push notifications per hour per user
- Max 1 email per category per day
- Respect quiet hours (no notifications 10pm-8am local time)
- Critical notifications bypass all limits

Implementation: Redis counter per user with sliding window (same pattern as Chapter 2).

### Delivery Tracking

| Channel | "Sent" | "Delivered" | "Opened" |
|---------|--------|-------------|----------|
| Push | APNs/FCM accepted | Device received (callback) | User tapped |
| Email | SMTP accepted | Not bounced | Tracking pixel loaded |
| SMS | Provider accepted | Carrier delivered (DLR) | N/A |

### Template System

```
Template: "Hi {{name}}, your order {{order_id}} shipped! ETA: {{eta}}"
Variables: { "name": "Alice", "order_id": "ORD-789", "eta": "2 days" }
Result: "Hi Alice, your order ORD-789 shipped! ETA: 2 days"
```

Templates stored in DB, cached in memory. Versioned for A/B testing.

### Retry and Dead Letter Queue

- Failed notifications retried with exponential backoff
- After 3 retries → dead letter queue for manual inspection
- Provider-specific handling (APNs invalid token → remove device)

---

## Step 7: Bottlenecks & Scaling

| Bottleneck | Solution |
|-----------|----------|
| Burst traffic (flash sales) | Priority queues + auto-scaling workers |
| Provider rate limits (APNs) | Connection pooling, multiple provider accounts |
| User preference lookups | Cache preferences in Redis |
| Duplicate notifications | Idempotency key per notification |
| Analytics at scale | Async event stream to data warehouse |

**Graceful degradation:** Under extreme load:
1. Critical: always delivered immediately
2. High: slight delay acceptable
3. Normal: queue and deliver within minutes
4. Low: batch and deliver within hours

---

## Key Talking Points

- Separate queues per priority ensures critical notifications are never delayed
- Rate limiting per user prevents notification fatigue
- Template system decouples content from delivery logic
- At-least-once with idempotency keys prevents both loss and duplicates
- Each channel has different delivery semantics — design accordingly

---

## Common Mistakes

- Single queue for all priorities (critical delayed by marketing blasts)
- Not respecting user preferences (legal issues with GDPR/CAN-SPAM)
- Synchronous sending (blocks the calling service)
- No retry logic (notifications silently lost on provider failure)
- Ignoring rate limits from providers (APNs will throttle you)
- Not tracking delivery status (can't debug "I never got the notification")

---

[← Video Platform](./chapter-07-video.md) | [Next: Payment System →](./chapter-09-payments.md)

# Chapter 9: Design a Payment System (Stripe)

[← Notification System](./chapter-08-notifications.md) | [Next: Distributed Cache →](./chapter-10-cache.md)

---

## The Question

> "Design a payment processing system like Stripe. Merchants integrate via API to charge customers. The system must handle idempotency, prevent double-charges, maintain a ledger, deliver webhooks reliably, and handle the complexities of payment state transitions."

---

## Step 1: Requirements & Scope

**Functional:**
- Accept payments (credit card, bank transfer)
- Idempotent payment creation (retry-safe)
- Payment state machine (pending → authorized → captured → settled)
- Refunds (full and partial)
- Webhook delivery to merchants on state changes
- Double-entry ledger for accounting

**Non-functional:**
- 10M transactions/day
- Exactly-once payment processing (no double charges)
- Strong consistency (money can't be lost or created)
- 99.999% availability for payment API
- PCI DSS compliance for card data

---

## Step 2: Estimation

| Metric | Calculation | Result |
|--------|-------------|--------|
| Transaction QPS | 10M / 86400 | ~115 TPS |
| Peak TPS | 115 × 5 (Black Friday) | ~575 TPS |
| Ledger entries/day | 10M × 2 (double-entry) | 20M rows/day |
| Webhook deliveries/day | 10M × 3 events avg | 30M webhooks/day |
| Storage (1 year) | 10M × 365 × 2KB | ~7 TB |

---

## Step 3: API Design

```
POST /api/v1/payments
  Headers: Idempotency-Key: "idk_abc123"
  Body: {
    "amount": 5000,
    "currency": "usd",
    "payment_method": "pm_card_visa",
    "merchant_id": "merch_456",
    "metadata": { "order_id": "ord_789" }
  }
  Response: { "payment_id": "pay_001", "status": "pending" }

POST /api/v1/payments/{payment_id}/capture
POST /api/v1/payments/{payment_id}/refund
  Body: { "amount": 2000 }

GET /api/v1/payments/{payment_id}
  Response: { "status": "captured", "amount": 5000, ... }
```

---

## Step 4: Data Model

**Payments (SQL — ACID required):**

| Field | Type |
|-------|------|
| payment_id (PK) | UUID |
| idempotency_key | VARCHAR (unique) |
| merchant_id | UUID |
| amount | BIGINT (cents) |
| currency | VARCHAR(3) |
| status | ENUM |
| payment_method_id | UUID |
| created_at | TIMESTAMP |
| updated_at | TIMESTAMP |

**Ledger Entries (SQL — append-only):**

| Field | Type |
|-------|------|
| entry_id (PK) | UUID |
| payment_id | UUID |
| account_id | UUID |
| type | ENUM (debit, credit) |
| amount | BIGINT |
| balance_after | BIGINT |
| created_at | TIMESTAMP |

---

## Step 5: High-Level Architecture

```
┌──────────┐     ┌──────────────┐     ┌─────────────────┐
│ Merchant │────▶│  API Gateway │────▶│ Payment Service │
└──────────┘     └──────────────┘     └────────┬────────┘
                                               │
                    ┌──────────────────────────┼──────────────────┐
                    ▼                          ▼                   ▼
           ┌──────────────┐          ┌──────────────┐    ┌──────────────┐
           │  Payment DB  │          │   Ledger     │    │  Payment     │
           │  (Postgres)  │          │   Service    │    │  Processor   │
           └──────────────┘          └──────────────┘    │  (PSP/Bank)  │
                                                         └──────┬───────┘
                    ┌────────────────────────────────────────────┘
                    ▼
           ┌──────────────┐          ┌──────────────┐
           │  Webhook     │────────▶│   Merchant   │
           │  Service     │          │   Server     │
           └──────────────┘          └──────────────┘
```

---

## Step 6: Deep Dive

### Idempotency Keys

**Problem:** Network timeout → merchant retries → double charge?

**Solution:** Merchant sends `Idempotency-Key` header with each request.

```
1. Receive request with idempotency_key
2. Check DB: does this key already exist?
   - Yes → return cached response (no re-processing)
   - No → process payment, store result keyed by idempotency_key
3. Return response
```

Implementation: Unique constraint on idempotency_key column. First write wins.

### Payment State Machine

```
         authorize         capture          settle
PENDING ──────────▶ AUTHORIZED ──────────▶ CAPTURED ──────────▶ SETTLED
   │                    │                      │
   │ fail               │ void                 │ refund
   ▼                    ▼                      ▼
 FAILED              VOIDED               REFUNDED
```

Each transition is a DB transaction. Invalid transitions rejected (can't refund a pending payment).

### Double-Entry Ledger

Every money movement creates TWO entries that sum to zero:

```
Payment captured ($50):
  DEBIT   customer_account    $50
  CREDIT  merchant_account    $50

Refund ($20):
  DEBIT   merchant_account    $20
  CREDIT  customer_account    $20
```

**Why?** Auditable, self-balancing. Sum of all entries must always equal zero. Any discrepancy = bug.

### Webhook Delivery

Merchants need to know when payment status changes:

1. Payment state changes → event created
2. Webhook service picks up event from queue
3. POST to merchant's configured URL with event payload
4. If merchant returns 2xx → mark delivered
5. If failure → retry with exponential backoff (1s, 5s, 30s, 5m, 1h)
6. After 72 hours of failures → mark as failed, alert merchant

**Ordering:** Webhooks may arrive out of order. Include event timestamp. Merchants should handle idempotently.

### Reconciliation

Daily batch job compares:
- Internal ledger totals vs bank settlement reports
- Flags discrepancies for manual review
- Catches: missed settlements, duplicate charges, fraud

### PCI Compliance (Overview)

- Card numbers never touch your servers (use tokenization)
- Payment method → token stored, actual card at PCI-compliant vault
- All data encrypted at rest and in transit
- Access logging, network segmentation, regular audits

---

## Step 7: Bottlenecks & Scaling

| Bottleneck | Solution |
|-----------|----------|
| DB write contention | Shard by merchant_id |
| Idempotency check latency | Index on idempotency_key, cache recent keys |
| Webhook delivery at scale | Separate queue per merchant, parallel delivery |
| Bank API latency (2-5s) | Async processing, return "pending" immediately |
| Reconciliation at scale | Partition by date, parallel batch jobs |

**Exactly-once semantics:**
- Use DB transactions for state changes
- Idempotency keys prevent duplicate processing
- Outbox pattern: write event to DB in same transaction as state change, then publish

---

## Key Talking Points

- Idempotency keys are THE critical concept — prevents double charges on retry
- Double-entry ledger ensures money is never lost or created
- Payment state machine enforces valid transitions
- Webhooks need retry + idempotent receivers (at-least-once delivery)
- Tokenization keeps you out of PCI scope for card storage

---

## Common Mistakes

- Not discussing idempotency (the #1 concern in payments)
- Storing credit card numbers directly (PCI violation)
- Using floating point for money (use integers in cents)
- Single-entry accounting (can't detect discrepancies)
- Synchronous bank calls blocking the API (use async + polling)
- Webhooks without retry logic (merchants miss events)

---

[← Notification System](./chapter-08-notifications.md) | [Next: Distributed Cache →](./chapter-10-cache.md)

# Chapter 6: Webhooks — Receiving External Events

[← Chapter 5: Error Handling](chapter-05-errors.md) | [Chapter 7: Database Operations →](chapter-07-databases.md)

---

## The Problem

Stripe needs to notify LaunchPad when a payment succeeds, fails, or is disputed. Currently, the finance team checks the Stripe dashboard manually every morning. Chargebacks sit unnoticed for days. Failed payments don't trigger follow-up emails.

Diana: "When a payment fails, I want the customer success team notified within 5 minutes. Not the next morning when someone remembers to check Stripe."

Stripe supports webhooks — it'll POST event data to a URL you provide. But you can't just expose an open endpoint to the internet. Anyone could send fake payment events to your webhook URL. You need authentication.

## Webhook Node: The Basics

You used a basic webhook in Chapter 1. Let's go deeper.

### Webhook Configuration

| Setting | Options | Use When |
|---|---|---|
| HTTP Method | GET, POST, PUT, DELETE | POST for most webhooks |
| Path | Custom string | Unique per workflow |
| Response Mode | "When last node finishes" / "Immediately" | Immediately for slow workflows |
| Response Code | 200, 201, etc. | Match what the sender expects |
| Response Data | None / First entry / JSON | Return data to the caller |
| Authentication | None, Basic, Header, JWT | Always in production |

### Response Mode Matters

Stripe expects a 200 response within 5 seconds. If your workflow takes 30 seconds to process, Stripe will timeout and retry — creating duplicates.

Set **Response Mode** to "Respond Immediately":
- n8n returns 200 right away
- The workflow continues processing in the background
- Stripe is happy, your workflow has time to work

## HMAC Signature Verification

Stripe signs every webhook payload with a secret. You verify the signature to prove the request actually came from Stripe.

### How It Works

1. Stripe computes `HMAC-SHA256(payload, webhook_secret)` and sends it in the `Stripe-Signature` header
2. You compute the same HMAC with your copy of the secret
3. If they match, the request is authentic

### Implementation in n8n

Add a Code node immediately after the Webhook to verify:

```javascript
const crypto = require('crypto');

const payload = JSON.stringify($input.item.json.body);
const signature = $input.item.json.headers['stripe-signature'];
const secret = 'whsec_your_webhook_secret'; // Use credentials in production

// Stripe signature format: t=timestamp,v1=signature
const elements = signature.split(',');
const timestamp = elements.find(e => e.startsWith('t=')).split('=')[1];
const expectedSig = elements.find(e => e.startsWith('v1=')).split('=')[1];

// Compute expected signature
const signedPayload = `${timestamp}.${payload}`;
const computedSig = crypto
  .createHmac('sha256', secret)
  .update(signedPayload)
  .digest('hex');

if (computedSig !== expectedSig) {
  throw new Error('Invalid webhook signature — request rejected');
}

// Signature valid — pass through the event
return { json: $input.item.json.body };
```

If the signature doesn't match, the workflow throws an error and stops. Fake requests never reach your business logic.

### Using n8n's Built-in Header Auth

For simpler cases (not Stripe's complex signature), use the Webhook node's built-in authentication:

1. Set **Authentication** to "Header Auth"
2. **Header Name**: `X-Webhook-Secret`
3. **Header Value**: your shared secret

The webhook rejects any request without the correct header.

## The Stripe Payment Workflow

```json
{
  "name": "Stripe Payment Events",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "stripe-webhook",
        "responseMode": "onReceived",
        "options": { "responseCode": 200 }
      },
      "name": "Stripe Webhook",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300]
    },
    {
      "parameters": {
        "mode": "runOnceForEachItem",
        "jsCode": "const crypto = require('crypto');\nconst body = JSON.stringify($input.item.json.body);\nconst sig = $input.item.json.headers['stripe-signature'];\nconst secret = $env.STRIPE_WEBHOOK_SECRET;\nconst timestamp = sig.split(',').find(e => e.startsWith('t=')).split('=')[1];\nconst expected = sig.split(',').find(e => e.startsWith('v1=')).split('=')[1];\nconst computed = crypto.createHmac('sha256', secret).update(`${timestamp}.${body}`).digest('hex');\nif (computed !== expected) throw new Error('Invalid signature');\nreturn { json: $input.item.json.body };"
      },
      "name": "Verify Signature",
      "type": "n8n-nodes-base.code",
      "position": [450, 300]
    },
    {
      "parameters": {
        "rules": {
          "rules": [
            { "conditions": { "conditions": [{ "leftValue": "={{ $json.type }}", "rightValue": "payment_intent.succeeded" }] }, "output": 0 },
            { "conditions": { "conditions": [{ "leftValue": "={{ $json.type }}", "rightValue": "payment_intent.payment_failed" }] }, "output": 1 },
            { "conditions": { "conditions": [{ "leftValue": "={{ $json.type }}", "rightValue": "charge.dispute.created" }] }, "output": 2 }
          ]
        }
      },
      "name": "Route by Event Type",
      "type": "n8n-nodes-base.switch",
      "position": [650, 300]
    }
  ],
  "connections": {
    "Stripe Webhook": { "main": [[{ "node": "Verify Signature", "type": "main", "index": 0 }]] },
    "Verify Signature": { "main": [[{ "node": "Route by Event Type", "type": "main", "index": 0 }]] }
  }
}
```

## Testing Webhooks Locally

Your local n8n isn't accessible from the internet. Stripe can't reach `localhost:5678`. Options:

### Option 1: Stripe CLI (Recommended)

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Forward events to your local webhook
stripe listen --forward-to localhost:5678/webhook/stripe-webhook

# In another terminal, trigger a test event
stripe trigger payment_intent.succeeded
```

### Option 2: ngrok

```bash
ngrok http 5678
# Gives you a public URL like https://abc123.ngrok.io
# Use https://abc123.ngrok.io/webhook/stripe-webhook in Stripe's dashboard
```

### Option 3: n8n's Test Webhook

Click "Listen for test event" in the Webhook node, then use curl:

```bash
curl -X POST http://localhost:5678/webhook-test/stripe-webhook \
  -H "Content-Type: application/json" \
  -H "Stripe-Signature: t=1234,v1=test" \
  -d '{"type": "payment_intent.succeeded", "data": {"object": {"amount": 5000, "customer": "cus_123"}}}'
```

## Responding to Webhooks

Some services expect data back in the webhook response — not just a 200 OK.

### Returning Custom Responses

Set **Response Mode** to "When Last Node Finishes" and use a **Respond to Webhook** node:

```json
{
  "parameters": {
    "respondWith": "json",
    "responseBody": "={{ JSON.stringify({ received: true, processed: $json.eventId }) }}"
  },
  "name": "Respond to Webhook",
  "type": "n8n-nodes-base.respondToWebhook",
  "position": [850, 300]
}
```

### Idempotency: Handling Duplicate Deliveries

Stripe retries failed webhook deliveries. If your workflow is slow and Stripe retries, you'll process the same event twice. Use the event ID to deduplicate:

```javascript
// Code node — check if we've already processed this event
const eventId = $input.item.json.id; // Stripe event ID like "evt_1234"

// Query your database for this event ID
const existing = await this.helpers.httpRequest({
  method: 'GET',
  url: `http://localhost:5678/webhook/check-processed/${eventId}`
});

if (existing.processed) {
  // Already handled — skip
  return [];
}

return $input.all();
```

## What You Learned

- **Response Mode** — respond immediately for slow workflows, avoid sender timeouts
- **HMAC verification** — validate webhook signatures to reject forged requests
- **Header Auth** — simpler alternative for services with shared secrets
- **Local testing** — Stripe CLI, ngrok, or curl with test payloads
- **Respond to Webhook node** — return custom data to the caller
- **Idempotency** — deduplicate retried deliveries using event IDs
- **Route by event type** — one webhook URL, multiple event handlers via Switch

Stripe payments now trigger instant notifications. Failed payments alert customer success. Chargebacks create urgent tickets. The finance team stops checking dashboards manually.

But all this event data is flowing through workflows and disappearing. Jake asks: "Can we store this somewhere? I want to query which customers had failed payments last month." You're currently using Google Sheets. It's not going to scale.

---

[← Chapter 5: Error Handling](chapter-05-errors.md) | [Chapter 7: Database Operations →](chapter-07-databases.md)

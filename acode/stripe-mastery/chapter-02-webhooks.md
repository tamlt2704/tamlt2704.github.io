# Chapter 2: Webhooks — "Payment Succeeded, But My App Doesn't Know"

[← Chapter 1: First Payment](chapter-01-first-payment.md) | [Chapter 3: Customers →](chapter-03-customers.md)

---

## The Problem

Jake: "Three people bought my program today. But when they log in, it says 'No purchases.' What's going on?"

You check the Stripe Dashboard. Three successful payments. $147 in your balance. But your database has zero purchase records.

The redirect to `success.html` is cosmetic. Your server never processed the payment. You need Stripe to **tell** your server when something happens.

---

## What Are Webhooks?

A webhook is Stripe calling YOUR server with event data. Instead of you asking Stripe "did the payment work?", Stripe tells you:

```
Traditional (polling):          Webhooks (event-driven):
──────────────────────────      ──────────────────────────
Your server: "Did it work?"     Stripe: "Hey, payment succeeded. Here's the data."
Stripe: "No."                   Your server: "Got it. Updating database."
Your server: "How about now?"
Stripe: "No."
Your server: "Now?"
Stripe: "Yes!"
```

Webhooks are HTTP POST requests from Stripe to an endpoint you define.

---

## Setting Up the Webhook Endpoint

```javascript
// server.js
const express = require("express");
const stripe = require("stripe")(process.env.STRIPE_SECRET_KEY);

const app = express();

// IMPORTANT: Webhook endpoint needs raw body for signature verification
// This MUST come before express.json() middleware
app.post(
  "/webhooks",
  express.raw({ type: "application/json" }),
  (req, res) => {
    const sig = req.headers["stripe-signature"];
    let event;

    try {
      event = stripe.webhooks.constructEvent(
        req.body,
        sig,
        process.env.STRIPE_WEBHOOK_SECRET
      );
    } catch (err) {
      console.error(`Webhook signature verification failed: ${err.message}`);
      return res.status(400).send(`Webhook Error: ${err.message}`);
    }

    // Handle the event
    switch (event.type) {
      case "checkout.session.completed":
        handleCheckoutComplete(event.data.object);
        break;
      case "payment_intent.succeeded":
        handlePaymentSucceeded(event.data.object);
        break;
      case "payment_intent.payment_failed":
        handlePaymentFailed(event.data.object);
        break;
      default:
        console.log(`Unhandled event type: ${event.type}`);
    }

    // Always return 200 to acknowledge receipt
    res.json({ received: true });
  }
);

// Other routes use JSON parsing
app.use(express.json());

// ... rest of your routes

app.listen(3000);
```

---

## Handling the Checkout Complete Event

```javascript
async function handleCheckoutComplete(session) {
  // session.metadata contains what you set when creating the session
  const userId = session.metadata.user_id;
  const productId = session.metadata.product_id;
  const amountPaid = session.amount_total; // in cents

  console.log(`✅ Payment complete: User ${userId} bought ${productId} for $${amountPaid / 100}`);

  // Update your database
  await db.purchases.create({
    userId,
    productId,
    amountPaid,
    stripeSessionId: session.id,
    stripePaymentIntentId: session.payment_intent,
    status: "completed",
    createdAt: new Date(),
  });

  // Grant access
  await db.users.update(userId, {
    purchasedProducts: db.arrayUnion(productId),
  });

  // Send confirmation email
  await sendEmail(session.customer_details.email, {
    subject: "Your purchase is confirmed!",
    template: "purchase-confirmation",
    data: { productId, amount: amountPaid / 100 },
  });
}
```

---

## Signature Verification: Why It Matters

Without signature verification, anyone could POST fake events to your webhook endpoint:

```bash
# An attacker could do this:
curl -X POST http://yoursite.com/webhooks \
  -H "Content-Type: application/json" \
  -d '{"type":"checkout.session.completed","data":{"object":{"metadata":{"user_id":"attacker"}}}}'
```

The signature proves the event came from Stripe:

```javascript
// This line verifies the signature
event = stripe.webhooks.constructEvent(
  req.body,          // raw request body (NOT parsed JSON)
  sig,               // stripe-signature header
  webhookSecret      // your webhook signing secret (whsec_...)
);
```

If the signature doesn't match, `constructEvent` throws an error. The event is fake. Reject it.

**Critical:** The body must be the raw buffer, not parsed JSON. That's why the webhook route uses `express.raw()` instead of `express.json()`.

---

## Testing Webhooks Locally

Stripe can't reach `localhost`. The Stripe CLI solves this:

```bash
# Terminal 1: Run your server
npm run dev

# Terminal 2: Forward Stripe events to your local server
stripe listen --forward-to localhost:3000/webhooks
```

The CLI prints a webhook signing secret:

```
> Ready! Your webhook signing secret is whsec_1234567890abcdef...
```

Use this as your `STRIPE_WEBHOOK_SECRET` in `.env` during development.

Now trigger a test event:

```bash
# Terminal 3: Trigger a test payment
stripe trigger checkout.session.completed
```

Your server receives the event. Your handler runs. Check your database.

---

## The Event Object

Every webhook delivers an Event object:

```json
{
  "id": "evt_1234567890",
  "type": "checkout.session.completed",
  "created": 1680000000,
  "data": {
    "object": {
      "id": "cs_test_abc123",
      "payment_intent": "pi_xyz789",
      "amount_total": 4900,
      "currency": "usd",
      "customer": "cus_def456",
      "metadata": {
        "user_id": "user_abc123",
        "product_id": "program_shred_12wk"
      },
      "payment_status": "paid",
      "status": "complete"
    }
  }
}
```

- `event.type` → what happened
- `event.data.object` → the Stripe object that changed
- `event.data.object.metadata` → YOUR data that you attached

---

## Critical Events to Handle

| Event | When It Fires | What to Do |
|---|---|---|
| `checkout.session.completed` | User finished checkout | Grant access, create purchase record |
| `payment_intent.succeeded` | Payment confirmed | Update payment status |
| `payment_intent.payment_failed` | Card declined / error | Notify user, log failure |
| `invoice.payment_succeeded` | Subscription renewed | Extend access period |
| `invoice.payment_failed` | Subscription payment failed | Warn user, start grace period |
| `customer.subscription.deleted` | Subscription cancelled | Revoke access |
| `charge.dispute.created` | Customer filed a dispute | Alert team, gather evidence |

---

## Idempotency: Handle Duplicates

Stripe may send the same event multiple times (network retries, outages). Your handler must be idempotent — processing the same event twice should have the same result as processing it once.

```javascript
async function handleCheckoutComplete(session) {
  // Check if we already processed this session
  const existing = await db.purchases.findOne({
    stripeSessionId: session.id,
  });

  if (existing) {
    console.log(`Already processed session ${session.id}, skipping`);
    return;
  }

  // Process the purchase...
  await db.purchases.create({
    stripeSessionId: session.id,
    // ...
  });
}
```

---

## Return 200 Quickly

Stripe expects a 2xx response within 20 seconds. If your handler takes too long, Stripe thinks it failed and retries.

```javascript
// BAD — slow processing blocks the response
app.post("/webhooks", async (req, res) => {
  const event = verifyEvent(req);
  await processPayment(event);      // takes 10 seconds
  await sendEmail(event);           // takes 5 seconds
  await updateAnalytics(event);     // takes 3 seconds
  res.json({ received: true });     // 18 seconds later 😬
});

// GOOD — acknowledge immediately, process async
app.post("/webhooks", async (req, res) => {
  const event = verifyEvent(req);
  res.json({ received: true });     // respond immediately

  // Process in background (or use a job queue)
  try {
    await processPayment(event);
    await sendEmail(event);
    await updateAnalytics(event);
  } catch (err) {
    console.error("Background processing failed:", err);
    // Log for manual review — Stripe already got the 200
  }
});
```

For production, use a job queue (Bull, BullMQ, or a managed queue) instead of fire-and-forget.

---

## Webhook Retry Behavior

If your endpoint returns a non-2xx status or times out:

- Stripe retries up to **3 days**
- Retry schedule: 1 hour, 2 hours, 4 hours, 8 hours... (exponential backoff)
- After all retries fail, the event is marked as failed in your Dashboard

This means your webhook handler should:
1. Return 200 even if background processing might fail
2. Be idempotent (handle retries gracefully)
3. Log failures for manual investigation

---

## Common Mistakes

### 1. Parsing body before webhook route

```javascript
// WRONG — express.json() parses the body before the webhook route sees it
app.use(express.json());
app.post("/webhooks", (req, res) => {
  // req.body is already parsed — signature verification FAILS
});

// RIGHT — use express.raw() specifically for the webhook route
app.post("/webhooks", express.raw({ type: "application/json" }), (req, res) => {
  // req.body is a Buffer — signature verification works
});
app.use(express.json()); // other routes get parsed JSON
```

### 2. Not verifying signatures

```javascript
// WRONG — trusting any POST to your webhook endpoint
app.post("/webhooks", (req, res) => {
  const event = JSON.parse(req.body); // anyone could send this!
  handleEvent(event);
});

// RIGHT — verify it came from Stripe
const event = stripe.webhooks.constructEvent(req.body, sig, secret);
```

### 3. Trusting the success redirect

```javascript
// WRONG — granting access on the success page
app.get("/success", (req, res) => {
  grantAccess(req.query.session_id); // user could fake this URL!
});

// RIGHT — grant access only in the webhook handler
// The success page just shows a "thank you" message
```

---

## Production Webhook Setup

In development, the Stripe CLI forwards events. In production, you register your endpoint in the Stripe Dashboard:

1. Dashboard → Developers → Webhooks
2. Click "Add endpoint"
3. URL: `https://api.fitforge.app/webhooks`
4. Select events: `checkout.session.completed`, `payment_intent.succeeded`, etc.
5. Stripe gives you a `whsec_` signing secret for this endpoint

Use the production `whsec_` secret in your production environment variables.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
Webhook                         │ Stripe POSTs events to your server
stripe-signature header         │ Proves the event is from Stripe
constructEvent()                │ Verifies signature, parses event
express.raw()                   │ Keeps body as Buffer (required)
event.type                      │ What happened (e.g., "checkout.session.completed")
event.data.object               │ The Stripe object that changed
Return 200 quickly              │ Acknowledge receipt, process async
Idempotency                     │ Handle duplicate events gracefully
stripe listen --forward-to      │ Forward events to localhost (dev)
stripe trigger <event>          │ Send a test event (dev)
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Payments work. Webhooks confirm them. But every payment creates a new "guest" — no saved cards, no history, no relationship.

Jake: "My repeat clients have to enter their card every time. Can't we just remember them?"

That's Customers.

---

[← Chapter 1: First Payment](chapter-01-first-payment.md) | [Chapter 3: Customers →](chapter-03-customers.md)

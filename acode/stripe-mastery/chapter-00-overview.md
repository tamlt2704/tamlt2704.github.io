# Stripe Mastery: From First Charge to Subscription Empire

You just launched **FitForge** — a fitness coaching platform where trainers sell workout plans, one-on-one coaching sessions, and monthly subscriptions. You built the app. Users love it. Trainers are signing up.

One problem: nobody can pay you.

**Priya**, your co-founder (the business brain), is losing patience:

> "We have 200 trainers waiting to sell plans. We have 3,000 users who clicked 'Buy' and got a 'Coming Soon' page. Every day we don't have payments is money we're burning. Use Stripe. I don't care how — just make money move."

**Jake**, your first paying trainer (hopefully), adds:

> "I need subscriptions for my monthly coaching. I need one-time payments for my 12-week programs. I need to see my earnings. And I need refunds to work because clients ghost me after week 2."

You open the Stripe dashboard. It's beautiful. It's also overwhelming — Payment Intents, Checkout Sessions, Customer objects, Webhooks, Connect, Billing, Tax, Radar, Terminal...

Time to figure out what you actually need, build it correctly, and not accidentally charge someone $10,000.

---

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Fullstack Dev | "I'll just call the charge API... wait, that's deprecated?" |
| **Priya** | Co-founder / Business | "Revenue. Yesterday." |
| **Jake** | First trainer (seller) | "Where's my money? When do I get paid?" |
| **The Angry Customer** | Disputed a charge | "I didn't authorize this!" (they did) |
| **The Webhook** | Stripe's messenger | "Something happened. You should know about it." |
| **The $10K Mistake** | That one test-mode key in production | Someone used `sk_test_` in prod. Charges went nowhere. |

---

## The Stack

| Tool | What It Does |
|---|---|
| **Stripe Checkout** | Pre-built payment page (fastest path to revenue) |
| **Payment Intents** | Low-level payment control (custom flows) |
| **Customers** | Store payment methods, track history |
| **Subscriptions / Billing** | Recurring payments, plan management |
| **Stripe Connect** | Pay out to trainers (marketplace payments) |
| **Webhooks** | Real-time event notifications from Stripe |
| **Stripe CLI** | Local testing, webhook forwarding |
| **Radar** | Fraud detection (automatic) |
| **Node.js + Express** | Backend (any language works — we use Node) |
| **React** | Frontend |

---

## How to Read This

Every chapter follows the same loop:

```
  💰 Priya or Jake needs a payment feature
   │
   ▼
  🤔 You learn the Stripe concept that enables it
   │
   ▼
  ⌨️  You build it (with real API calls)
   │
   ▼
  💥 Something breaks — webhook missed, double charge, payout fails
   │
   ▼
  🧠 You understand WHY and fix it properly
   │
   ▼
  💰 Next feature
```

No concept shows up before you need it. You won't learn webhooks until a payment succeeds but your database doesn't update. You won't touch Connect until trainers ask "where's my money?" You won't learn disputes until a customer files one.

---

## The Roadmap

### Part 1: First Revenue — "Make Money Move"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Feature                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 01 │ Accept a payment (one-time)            │ Stripe Checkout, test mode, API keys
────┼────────────────────────────────────────┼──────────────────────────────────────
 02 │ "Payment succeeded but DB didn't update"│ Webhooks — the backbone of Stripe
────┼────────────────────────────────────────┼──────────────────────────────────────
 03 │ "Remember the customer's card"         │ Customers, saved payment methods
────┼────────────────────────────────────────┼──────────────────────────────────────
 04 │ Custom payment form (no redirect)      │ Payment Intents + Stripe Elements
────┼────────────────────────────────────────┼──────────────────────────────────────
 05 │ "Show a receipt and payment history"   │ Charges, balance transactions, metadata
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 2: Subscriptions — "Recurring Revenue"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Feature                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 06 │ Monthly coaching subscription          │ Products, Prices, Subscriptions
────┼────────────────────────────────────────┼──────────────────────────────────────
 07 │ "User wants to cancel / downgrade"     │ Subscription lifecycle, proration
────┼────────────────────────────────────────┼──────────────────────────────────────
 08 │ "Card expired, payment failed"         │ Dunning, retry logic, grace periods
────┼────────────────────────────────────────┼──────────────────────────────────────
 09 │ Free trials and coupons                │ Trial periods, promotion codes, discounts
────┼────────────────────────────────────────┼──────────────────────────────────────
 10 │ Usage-based pricing (per session)      │ Metered billing, usage records
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 3: Marketplace — "Pay the Trainers"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Feature                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 11 │ "Trainers need to get paid"            │ Stripe Connect — platform basics
────┼────────────────────────────────────────┼──────────────────────────────────────
 12 │ Onboard trainers (KYC)                 │ Connect onboarding, account types
────┼────────────────────────────────────────┼──────────────────────────────────────
 13 │ Split payments (platform fee)          │ Destination charges, transfer amounts
────┼────────────────────────────────────────┼──────────────────────────────────────
 14 │ "When does Jake get his money?"        │ Payouts, payout schedules, balance
────┼────────────────────────────────────────┼──────────────────────────────────────
 15 │ Refunds and disputes                   │ Refund flows, dispute evidence, Radar
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 4: Production — "Don't Lose Money"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Problem                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 16 │ "Is this card stolen?"                 │ Radar rules, fraud prevention, 3D Secure
────┼────────────────────────────────────────┼──────────────────────────────────────
 17 │ Tax collection (VAT, sales tax)        │ Stripe Tax, tax IDs, invoices
────┼────────────────────────────────────────┼──────────────────────────────────────
 18 │ Idempotency and error handling         │ Idempotency keys, retry safety, error types
────┼────────────────────────────────────────┼──────────────────────────────────────
 19 │ Testing everything                     │ Test clocks, test cards, CI integration
────┼────────────────────────────────────────┼──────────────────────────────────────
 20 │ Go live checklist                      │ Live mode, PCI compliance, monitoring
────┴────────────────────────────────────────┴──────────────────────────────────────
```

---

## The Architecture We're Building

By Chapter 20:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        FitForge Payment Architecture                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  React Frontend                                                   │   │
│  │  ├── Checkout Button → redirects to Stripe Checkout               │   │
│  │  ├── Embedded Payment Form (Stripe Elements)                      │   │
│  │  ├── Subscription Management (Customer Portal)                    │   │
│  │  └── Trainer Dashboard (earnings, payouts)                        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              │                                           │
│                              ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Node.js Backend (Express)                                        │   │
│  │  ├── POST /create-checkout-session                                │   │
│  │  ├── POST /create-subscription                                    │   │
│  │  ├── POST /webhooks (Stripe events)                               │   │
│  │  ├── POST /connect/onboard (trainer signup)                       │   │
│  │  └── GET  /billing/portal (customer portal link)                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              │                                           │
│                              ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Stripe                                                           │   │
│  │                                                                    │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────────┐  │   │
│  │  │  Checkout  │  │  Billing   │  │  Connect   │  │   Radar   │  │   │
│  │  │ (payments) │  │  (subs)    │  │ (payouts)  │  │  (fraud)  │  │   │
│  │  └────────────┘  └────────────┘  └────────────┘  └───────────┘  │   │
│  │                                                                    │   │
│  │  ┌──────────────────────────────────────────────────────────┐    │   │
│  │  │  Webhooks → Your Server                                   │    │   │
│  │  │  ├── checkout.session.completed                           │    │   │
│  │  │  ├── invoice.payment_succeeded                            │    │   │
│  │  │  ├── customer.subscription.deleted                        │    │   │
│  │  │  └── charge.dispute.created                               │    │   │
│  │  └──────────────────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Database (Postgres)                                              │   │
│  │  ├── users (stripe_customer_id)                                   │   │
│  │  ├── trainers (stripe_connect_account_id)                         │   │
│  │  ├── subscriptions (stripe_subscription_id, status)               │   │
│  │  └── payments (stripe_payment_intent_id, amount, status)          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Stripe vs. Building Payments Yourself

Priya asks: "Why not just use a bank API directly?"

```
Build it yourself:                    Stripe:
──────────────────────────────────    ─────────
PCI DSS Level 1 compliance ($$$)     Stripe handles PCI (you never touch card numbers)
Build fraud detection                 Radar (automatic, ML-based)
Handle 135+ currencies               Built in
Manage failed payments / retries      Automatic dunning
Build subscription logic              Billing API
Handle tax in 40+ countries           Stripe Tax
Build marketplace payouts             Connect
Time to first payment: 3-6 months    Time to first payment: 1 afternoon
```

The tradeoff: Stripe takes 2.9% + 30¢ per transaction. For a startup, that's nothing compared to the engineering cost of building it yourself.

---

## The Trap: "Just Call the Charge API"

Stripe is easy to start. That's the trap. The easy path leads to:

1. **No webhooks** — payment succeeds but your app never knows
2. **No idempotency** — user double-clicks, gets charged twice
3. **Test keys in production** — charges silently succeed in test mode, no real money moves
4. **No error handling** — card declined = unhandled exception = white screen
5. **No subscription lifecycle** — user cancels but still has access forever

This series teaches you to avoid every one of these.

---

## Prerequisites

### Node.js 18+

```bash
node --version  # 18+
```

### Stripe Account (Free)

1. Go to [dashboard.stripe.com](https://dashboard.stripe.com)
2. Sign up (no credit card needed)
3. Stay in **Test Mode** (toggle in top-right)

### Stripe CLI

```bash
# macOS
brew install stripe/stripe-cli/stripe

# Windows (scoop)
scoop install stripe

# Or download from https://stripe.com/docs/stripe-cli
```

```bash
stripe login
stripe listen --forward-to localhost:3000/webhooks
```

### API Keys

From the Stripe Dashboard → Developers → API Keys:

```bash
# .env (NEVER commit this file)
STRIPE_SECRET_KEY=sk_test_51...
STRIPE_PUBLISHABLE_KEY=pk_test_51...
STRIPE_WEBHOOK_SECRET=whsec_...
```

- `pk_test_` → safe for frontend (public)
- `sk_test_` → backend only (secret — treat like a password)
- `whsec_` → webhook signature verification

### Project Setup

```bash
mkdir fitforge-payments && cd fitforge-payments
npm init -y
npm install express stripe dotenv
npm install -D nodemon
```

```json
// package.json
{
  "scripts": {
    "dev": "nodemon server.js"
  }
}
```

```javascript
// server.js
require("dotenv").config();
const express = require("express");
const stripe = require("stripe")(process.env.STRIPE_SECRET_KEY);

const app = express();

app.get("/health", (req, res) => {
  res.json({ status: "healthy", mode: "test" });
});

app.listen(3000, () => {
  console.log("FitForge payments running on http://localhost:3000");
});
```

### Verify

```bash
npm run dev
curl http://localhost:3000/health
# → {"status":"healthy","mode":"test"}

stripe trigger payment_intent.succeeded
# → You should see the event in your Stripe Dashboard → Developers → Events
```

If both work — you're ready to accept your first payment.

---

## Key Concepts (Preview)

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ One-Line Explanation
────────────────────────────────┼──────────────────────────────────────
Payment Intent                  │ "I intend to charge $X" — the core payment object
Checkout Session                │ Pre-built payment page (Stripe hosts it)
Customer                        │ A person who pays (stores cards, history)
Subscription                    │ Recurring Payment Intent on a schedule
Product / Price                 │ What you sell and how much it costs
Webhook                         │ "Hey, something happened" — Stripe → your server
Connect Account                 │ A seller on your platform (trainer)
Idempotency Key                 │ "Don't do this twice" — prevents double charges
────────────────────────────────┴──────────────────────────────────────
```

---

[Next: Chapter 1 — Your First Payment (Stripe Checkout) →](chapter-01-first-payment.md)

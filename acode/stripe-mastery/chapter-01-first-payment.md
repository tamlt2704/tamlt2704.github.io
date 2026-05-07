# Chapter 1: Your First Payment — Stripe Checkout

[← Overview](chapter-00-overview.md) | [Chapter 2: Webhooks →](chapter-02-webhooks.md)

---

## The Task

Priya: "Jake's 12-week shred program costs $49. A user clicks 'Buy'. Money appears in our Stripe account. That's it. Ship it today."

---

## The Fastest Path: Stripe Checkout

Stripe Checkout is a pre-built, hosted payment page. You don't build a form. You don't handle card numbers. You don't worry about PCI compliance. You redirect the user to Stripe, they pay, Stripe redirects them back.

```
User clicks "Buy"
       │
       ▼
Your server creates a Checkout Session
       │
       ▼
User is redirected to Stripe's hosted page
       │
       ▼
User enters card details (on Stripe's domain)
       │
       ▼
Payment succeeds → redirect to your success page
```

---

## The Code

### Backend: Create a Checkout Session

```javascript
// server.js
const express = require("express");
const stripe = require("stripe")(process.env.STRIPE_SECRET_KEY);

const app = express();
app.use(express.static("public")); // serve frontend
app.use(express.json());

app.post("/create-checkout-session", async (req, res) => {
  const session = await stripe.checkout.sessions.create({
    payment_method_types: ["card"],
    line_items: [
      {
        price_data: {
          currency: "usd",
          product_data: {
            name: "12-Week Shred Program",
            description: "Jake's complete transformation plan",
            images: ["https://fitforge.app/images/shred-program.jpg"],
          },
          unit_amount: 4900, // $49.00 in cents
        },
        quantity: 1,
      },
    ],
    mode: "payment", // one-time payment (not subscription)
    success_url: "http://localhost:3000/success.html?session_id={CHECKOUT_SESSION_ID}",
    cancel_url: "http://localhost:3000/cancel.html",
  });

  res.json({ url: session.url });
});

app.listen(3000, () => console.log("Running on http://localhost:3000"));
```

### Frontend: The Buy Button

```html
<!-- public/index.html -->
<!DOCTYPE html>
<html>
<head><title>FitForge</title></head>
<body>
  <h1>12-Week Shred Program</h1>
  <p>$49.00 — Jake's complete transformation plan</p>
  <button id="buy-btn">Buy Now</button>

  <script>
    document.getElementById("buy-btn").addEventListener("click", async () => {
      const response = await fetch("/create-checkout-session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      const { url } = await response.json();
      window.location.href = url; // redirect to Stripe
    });
  </script>
</body>
</html>
```

```html
<!-- public/success.html -->
<!DOCTYPE html>
<html>
<body>
  <h1>🎉 Payment Successful!</h1>
  <p>You now have access to the 12-Week Shred Program.</p>
  <a href="/">Back to FitForge</a>
</body>
</html>
```

```html
<!-- public/cancel.html -->
<!DOCTYPE html>
<html>
<body>
  <h1>Payment Cancelled</h1>
  <p>No charge was made. <a href="/">Try again</a></p>
</body>
</html>
```

---

## Test It

1. Run `npm run dev`
2. Open `http://localhost:3000`
3. Click "Buy Now"
4. You're redirected to Stripe's checkout page
5. Use test card: `4242 4242 4242 4242`, any future expiry, any CVC
6. Click "Pay"
7. Redirected to success page

Check your Stripe Dashboard → Payments. You'll see a $49.00 payment (in test mode).

**That's it. You just accepted your first payment.**

---

## Test Cards

| Card Number | Behavior |
|---|---|
| `4242 4242 4242 4242` | Succeeds |
| `4000 0000 0000 3220` | Requires 3D Secure authentication |
| `4000 0000 0000 9995` | Declined (insufficient funds) |
| `4000 0000 0000 0002` | Declined (generic) |
| `4000 0025 0000 3155` | Requires authentication (SCA) |

Use any future expiry date and any 3-digit CVC.

---

## What Just Happened (Under the Hood)

When you called `stripe.checkout.sessions.create()`, Stripe:

1. Created a **Payment Intent** (the actual charge object)
2. Created a **Checkout Session** (the hosted page tied to that intent)
3. Generated a URL for the hosted payment page

When the user paid:

1. Stripe collected the card details (on their PCI-compliant servers)
2. Stripe charged the card
3. Stripe created a **Charge** object
4. Stripe redirected the user to your `success_url`

```
Checkout Session
    └── Payment Intent
            └── Charge
                    └── Balance Transaction (money in your Stripe balance)
```

---

## The Problem: "Payment Succeeded But Nothing Happened"

Priya: "A user paid $49 but they don't have access to the program. What happened?"

Here's what went wrong:

```
User pays → Stripe redirects to success.html → User sees "Payment Successful!"
                                                         │
                                                         ▼
                                              But your DATABASE was never updated.
                                              The user has no record of the purchase.
```

Why? Because the redirect to `success.html` is just a URL change. Your server never confirmed the payment. What if:
- The user closes the browser before the redirect?
- The redirect fails (network issue)?
- The user navigates directly to `success.html`?

**You cannot trust the redirect.** You need Stripe to TELL your server that payment succeeded. That's what webhooks are for.

---

## Amounts Are in Cents

This trips up everyone:

```javascript
// WRONG — charges $490,000
unit_amount: 49.00  // Stripe interprets this as 4900 cents? No — as 49 cents!

// Actually wrong — this charges $0.49
unit_amount: 49

// CORRECT — charges $49.00
unit_amount: 4900  // 4900 cents = $49.00
```

Always multiply by 100. Always use integers. Stripe never uses floats for money.

```javascript
// Helper
const toCents = (dollars) => Math.round(dollars * 100);

unit_amount: toCents(49.00)  // 4900
```

---

## Metadata: Tag Everything

Metadata is free-form key-value data you attach to Stripe objects. It's how you connect Stripe to your database:

```javascript
const session = await stripe.checkout.sessions.create({
  // ... line_items, mode, urls ...
  metadata: {
    user_id: "user_abc123",
    product_id: "program_shred_12wk",
    trainer_id: "trainer_jake",
  },
  payment_intent_data: {
    metadata: {
      user_id: "user_abc123",
      product_id: "program_shred_12wk",
    },
  },
});
```

When the webhook fires, you'll read this metadata to know WHO bought WHAT. Without metadata, you're guessing.

---

## Checkout Session Options

```javascript
const session = await stripe.checkout.sessions.create({
  // Required
  line_items: [/* ... */],
  mode: "payment",           // "payment" | "subscription" | "setup"
  success_url: "https://...",
  cancel_url: "https://...",

  // Optional but useful
  customer_email: "user@example.com",  // pre-fill email
  metadata: { user_id: "..." },        // your reference data
  expires_after: 1800,                 // session expires in 30 min
  allow_promotion_codes: true,         // enable coupon codes
  
  // Collect extra info
  billing_address_collection: "required",
  shipping_address_collection: {
    allowed_countries: ["US", "CA", "GB"],
  },
});
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
Checkout Session                │ Creates a hosted payment page
mode: "payment"                 │ One-time charge
mode: "subscription"            │ Recurring charge
mode: "setup"                   │ Save card without charging
line_items                      │ What the user is buying
unit_amount                     │ Price in CENTS (4900 = $49.00)
success_url                     │ Where to redirect after payment
cancel_url                      │ Where to redirect if user cancels
metadata                        │ Your custom data (user_id, etc.)
{CHECKOUT_SESSION_ID}           │ Template variable Stripe replaces
Test card: 4242...              │ Always succeeds in test mode
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The payment works. But your app doesn't know about it. The success page is a lie — it shows "Payment Successful" whether or not the payment actually went through.

You need webhooks: Stripe calling YOUR server to confirm what happened.

---

[← Overview](chapter-00-overview.md) | [Chapter 2: Webhooks →](chapter-02-webhooks.md)

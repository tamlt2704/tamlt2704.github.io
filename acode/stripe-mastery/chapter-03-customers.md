# Chapter 3: Customers — "Remember My Card"

[← Chapter 2: Webhooks](chapter-02-webhooks.md) | [Chapter 4: Payment Intents →](chapter-04-payment-intents.md)

---

## The Problem

Jake's client Maria bought the 12-Week Shred. Now she wants the Nutrition Add-on ($19). She clicks "Buy" and has to enter her card again.

Maria: "I literally just paid you 5 minutes ago. Why don't you remember my card?"

Because right now, every payment is anonymous. Stripe doesn't know that the person who paid $49 and the person paying $19 are the same human.

---

## What Is a Customer?

A Stripe Customer is a persistent identity that ties together:
- Payment methods (saved cards)
- Payment history
- Subscriptions
- Invoices
- Metadata (your user ID)

```javascript
const customer = await stripe.customers.create({
  email: "maria@example.com",
  name: "Maria Santos",
  metadata: {
    user_id: "user_maria_123", // YOUR database ID
  },
});

// customer.id = "cus_abc123" — save this in your database
```

---

## Linking Customers to Your Users

When a user signs up on FitForge, create a Stripe Customer and store the ID:

```javascript
// When user registers
app.post("/register", async (req, res) => {
  const { email, name, password } = req.body;

  // Create user in your database
  const user = await db.users.create({ email, name, password: hash(password) });

  // Create Stripe customer
  const customer = await stripe.customers.create({
    email,
    name,
    metadata: { user_id: user.id },
  });

  // Save Stripe customer ID in your database
  await db.users.update(user.id, { stripeCustomerId: customer.id });

  res.json({ user: { id: user.id, email } });
});
```

Now every payment references this customer:

```javascript
app.post("/create-checkout-session", async (req, res) => {
  const user = await db.users.findById(req.userId);

  const session = await stripe.checkout.sessions.create({
    customer: user.stripeCustomerId, // ← link to existing customer
    line_items: [/* ... */],
    mode: "payment",
    success_url: "http://localhost:3000/success",
    cancel_url: "http://localhost:3000/cancel",
  });

  res.json({ url: session.url });
});
```

---

## Saving Payment Methods

To let users pay with a saved card, use Checkout in `setup` mode or enable saved payment methods:

```javascript
const session = await stripe.checkout.sessions.create({
  customer: user.stripeCustomerId,
  payment_method_types: ["card"],
  line_items: [/* ... */],
  mode: "payment",

  // Save the card for future use
  payment_intent_data: {
    setup_future_usage: "off_session", // save card for later charges
  },

  success_url: "...",
  cancel_url: "...",
});
```

After payment, the card is saved to the Customer. Next time, you can charge it without the user re-entering details.

---

## Listing Saved Payment Methods

```javascript
app.get("/payment-methods", async (req, res) => {
  const user = await db.users.findById(req.userId);

  const paymentMethods = await stripe.paymentMethods.list({
    customer: user.stripeCustomerId,
    type: "card",
  });

  // Return safe info (never expose full card numbers)
  const cards = paymentMethods.data.map((pm) => ({
    id: pm.id,
    brand: pm.card.brand,       // "visa", "mastercard"
    last4: pm.card.last4,       // "4242"
    expMonth: pm.card.exp_month,
    expYear: pm.card.exp_year,
  }));

  res.json({ cards });
});
```

---

## Charging a Saved Card

```javascript
app.post("/charge-saved-card", async (req, res) => {
  const { paymentMethodId, amount, productId } = req.body;
  const user = await db.users.findById(req.userId);

  const paymentIntent = await stripe.paymentIntents.create({
    amount: amount, // in cents
    currency: "usd",
    customer: user.stripeCustomerId,
    payment_method: paymentMethodId,
    off_session: true,   // user is not present (e.g., renewal)
    confirm: true,       // charge immediately
    metadata: {
      user_id: user.id,
      product_id: productId,
    },
  });

  res.json({ status: paymentIntent.status });
});
```

`off_session: true` means the user isn't actively on your site. This is how you charge saved cards for things like:
- Subscription renewals
- Usage-based billing
- One-click reorders

---

## The Customer Portal

Stripe provides a pre-built portal where customers can:
- View payment history
- Update their card
- Cancel subscriptions
- Download invoices

```javascript
app.post("/billing-portal", async (req, res) => {
  const user = await db.users.findById(req.userId);

  const portalSession = await stripe.billingPortal.sessions.create({
    customer: user.stripeCustomerId,
    return_url: "http://localhost:3000/account",
  });

  res.json({ url: portalSession.url });
});
```

The user clicks "Manage Billing" → redirected to Stripe's portal → manages their payment methods → redirected back. You build nothing.

---

## Customer vs. No Customer

```
Without Customer:                 With Customer:
──────────────────────────────    ──────────────────────────────
Every payment is anonymous        Payments linked to a person
Card entered every time           Card saved, one-click pay
No payment history                Full history in Dashboard
Can't do subscriptions            Subscriptions work
Can't charge off-session          Can charge saved cards later
No billing portal                 Self-service billing portal
```

---

## Handling the "Customer Already Exists" Problem

What if a user registers, you create a Customer, then they register again with the same email?

```javascript
async function getOrCreateCustomer(user) {
  // If we already have a Stripe customer ID, use it
  if (user.stripeCustomerId) {
    return user.stripeCustomerId;
  }

  // Check if a customer with this email already exists in Stripe
  const existing = await stripe.customers.list({
    email: user.email,
    limit: 1,
  });

  if (existing.data.length > 0) {
    const customerId = existing.data[0].id;
    await db.users.update(user.id, { stripeCustomerId: customerId });
    return customerId;
  }

  // Create new customer
  const customer = await stripe.customers.create({
    email: user.email,
    name: user.name,
    metadata: { user_id: user.id },
  });

  await db.users.update(user.id, { stripeCustomerId: customer.id });
  return customer.id;
}
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
stripe.customers.create()       │ Create a persistent customer identity
customer: "cus_..."             │ Link a checkout/payment to a customer
setup_future_usage              │ Save card for later charges
stripe.paymentMethods.list()    │ Get customer's saved cards
off_session: true               │ Charge without user present
stripe.billingPortal.sessions   │ Self-service billing management
metadata.user_id                │ Link Stripe customer to your DB user
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Checkout is great for simple flows — redirect to Stripe, come back. But Jake wants a custom payment form embedded in his trainer page. No redirects. Card input right on the page.

That's Payment Intents + Stripe Elements.

---

[← Chapter 2: Webhooks](chapter-02-webhooks.md) | [Chapter 4: Payment Intents →](chapter-04-payment-intents.md)

# Chapter 4: "Add a New Product Line"

[← Chapter 3: JOINs](chapter-03-joins.md) | [Chapter 5: Data Integrity →](chapter-05-constraints.md)

---

## The Request

Priya walks to your desk with a printed spreadsheet. "We're launching three new products next Monday. I need them in the database. Also, the 'Legacy Viewer' needs to be deactivated, and the 'Basic Dashboard' price is going up to $39."

She pauses. "And Derek left test data in production. Customer named 'Test McTestface'. Delete it."

Three operations. Three ways to change data.

---

## INSERT: Adding Rows

### Single Row

```sql
INSERT INTO products (name, category, price_cents, active)
VALUES ('Real-time Alerts', 'alerts', 7900, true);
```

Column list on the left, values on the right. They must match in order and count. Columns with defaults (`id`, `created_at`) can be omitted.

### Multiple Rows

```sql
INSERT INTO products (name, category, price_cents, active)
VALUES
    ('Real-time Alerts', 'alerts', 7900, true),
    ('Team Dashboard', 'analytics', 19900, true),
    ('Compliance Report', 'reporting', 24900, true);
```

One statement, three rows. Faster than three separate INSERTs — Postgres processes them in a single transaction.

### RETURNING: Get Back What You Inserted

```sql
INSERT INTO products (name, category, price_cents, active)
VALUES ('Real-time Alerts', 'alerts', 7900, true)
RETURNING id, name, created_at;
```

```
 id |      name       |         created_at
----+-----------------+----------------------------
  9 | Real-time Alerts| 2024-09-16 14:30:00.000000
```

`RETURNING` is a PostgreSQL superpower. Instead of inserting and then querying to find the generated ID, you get it back immediately. Works with `UPDATE` and `DELETE` too.

### INSERT from a SELECT

Maya: "Copy all enterprise customers into a VIP table for the sales team."

```sql
INSERT INTO vip_customers (name, email, plan)
SELECT name, email, plan
FROM customers
WHERE plan = 'enterprise';
```

No `VALUES` keyword. The `SELECT` provides the rows. Useful for data migrations, archiving, and bulk operations.

---

## UPDATE: Changing Existing Rows

### Basic Update

"Basic Dashboard price goes up to $39."

```sql
UPDATE products
SET price_cents = 3900
WHERE name = 'Basic Dashboard';
```

⚠️ **The cardinal rule of UPDATE**: Always include a `WHERE` clause. Without it:

```sql
-- ❌ DANGER: updates EVERY product
UPDATE products
SET price_cents = 3900;
```

Every product is now $39. Priya's enterprise suite costs $39. You're fired.

### Update Multiple Columns

```sql
UPDATE products
SET
    price_cents = 3900,
    active = true
WHERE name = 'Basic Dashboard';
```

### Update with a Calculation

"Raise all reporting products by 10%."

```sql
UPDATE products
SET price_cents = round(price_cents * 1.10)
WHERE category = 'reporting';
```

The old value is used in the calculation. `price_cents * 1.10` reads the current price and multiplies it.

### UPDATE with RETURNING

```sql
UPDATE products
SET price_cents = 3900
WHERE name = 'Basic Dashboard'
RETURNING id, name, price_cents;
```

```
 id |      name       | price_cents
----+-----------------+-------------
  1 | Basic Dashboard |        3900
```

Confirms exactly what changed. No need for a follow-up SELECT.

### UPDATE with a JOIN (FROM clause)

"Set all orders from churned customers to 'cancelled'."

```sql
UPDATE orders
SET status = 'cancelled'
FROM mrr_events m
WHERE orders.customer_id = m.customer_id
  AND m.event_type = 'churn'
  AND orders.status = 'pending'
RETURNING orders.id, orders.customer_id;
```

PostgreSQL uses `FROM` instead of `JOIN` in UPDATE statements. The `WHERE` clause connects the tables.

---

## DELETE: Removing Rows

### Basic Delete

"Delete Test McTestface."

```sql
DELETE FROM customers
WHERE name = 'Test McTestface';
```

⚠️ Same rule as UPDATE: **always use WHERE**.

```sql
-- ❌ CATASTROPHE: deletes ALL customers
DELETE FROM customers;
```

### DELETE with RETURNING

```sql
DELETE FROM customers
WHERE name = 'Test McTestface'
RETURNING id, name, email;
```

```
 id |      name       |       email
----+-----------------+-------------------
 99 | Test McTestface | test@example.com
```

Proof of what was deleted. Useful for audit logs.

### Safe Delete Pattern

Before deleting, always check what you're about to remove:

```sql
-- Step 1: Preview
SELECT * FROM customers WHERE name = 'Test McTestface';

-- Step 2: Confirm it's what you expect, then delete
DELETE FROM customers WHERE name = 'Test McTestface';
```

Or wrap it in a transaction (Chapter 12):

```sql
BEGIN;
DELETE FROM customers WHERE name = 'Test McTestface';
-- Check the result... if wrong:
ROLLBACK;
-- If correct:
COMMIT;
```

---

## UPSERT: Insert or Update (ON CONFLICT)

Hank: "I'm importing a customer list from a CSV. Some already exist. Don't create duplicates — just update their plan."

```sql
INSERT INTO customers (name, email, plan, country)
VALUES ('Acme Corp', 'billing@acme.com', 'enterprise', 'US')
ON CONFLICT (email)
DO UPDATE SET
    plan = EXCLUDED.plan,
    name = EXCLUDED.name;
```

| Part | What It Does |
|---|---|
| `ON CONFLICT (email)` | If a row with this email already exists... |
| `DO UPDATE SET` | ...update these columns instead of failing |
| `EXCLUDED.plan` | The value that was attempted to be inserted |

If `billing@acme.com` exists → update their plan. If not → insert a new row.

### DO NOTHING: Skip Duplicates

```sql
INSERT INTO customers (name, email, plan, country)
VALUES ('Acme Corp', 'billing@acme.com', 'enterprise', 'US')
ON CONFLICT (email)
DO NOTHING;
```

Silently skips the row if it already exists. No error, no update.

---

## TRUNCATE: The Nuclear Option

```sql
-- Delete ALL rows, instantly. No WHERE clause. No undo.
TRUNCATE TABLE order_items;
```

`TRUNCATE` is faster than `DELETE FROM table` (no row-by-row processing), but it can't be rolled back in some contexts and resets sequences. Use it for test data cleanup, never in production on real data.

---

## Soft Delete vs Hard Delete

Maya: "Don't actually delete the Legacy Viewer. Just mark it inactive. We might need it for historical reports."

```sql
-- Soft delete: mark as inactive
UPDATE products
SET active = false
WHERE name = 'Legacy Viewer';

-- Queries should filter:
SELECT * FROM products WHERE active = true;
```

| Approach | Pros | Cons |
|---|---|---|
| Hard delete (`DELETE`) | Clean, saves space | Data is gone forever |
| Soft delete (`active = false`) | Reversible, audit trail | Queries must always filter |

Most production systems use soft deletes for important data. You can always hard-delete later after a retention period.

---

## Bulk Operations: Real-World Patterns

### Batch Insert with Conflict Handling

```sql
INSERT INTO customers (name, email, plan, country)
VALUES
    ('NewCo', 'hello@newco.com', 'starter', 'US'),
    ('Acme Corp', 'billing@acme.com', 'enterprise', 'US'),  -- exists
    ('FreshFace', 'hi@freshface.io', 'free', 'CA')
ON CONFLICT (email)
DO UPDATE SET plan = EXCLUDED.plan
RETURNING id, name, email,
    (xmax = 0) AS was_inserted;  -- true if new, false if updated
```

The `xmax = 0` trick tells you whether each row was inserted (new) or updated (existing). Handy for import reports.

### Conditional Update

"Only raise prices for products that haven't been updated in 6 months."

```sql
UPDATE products
SET price_cents = round(price_cents * 1.05)
WHERE category = 'analytics'
  AND created_at < now() - interval '6 months'
  AND active = true
RETURNING name, price_cents;
```

---

## What You Did Today

```sql
-- Priya's checklist:
-- ✅ Added 3 new products
INSERT INTO products (name, category, price_cents, active) VALUES ...;

-- ✅ Deactivated Legacy Viewer
UPDATE products SET active = false WHERE name = 'Legacy Viewer';

-- ✅ Raised Basic Dashboard price
UPDATE products SET price_cents = 3900 WHERE name = 'Basic Dashboard';

-- ✅ Removed test data
DELETE FROM customers WHERE name = 'Test McTestface';
```

---

## Quick Reference

```
────────────────────┬──────────────────────────────────────────────────────
Statement           │ What It Does
────────────────────┼──────────────────────────────────────────────────────
INSERT INTO ... VALUES  │ Add new rows
INSERT INTO ... SELECT  │ Add rows from a query
UPDATE ... SET ... WHERE│ Change existing rows
DELETE FROM ... WHERE   │ Remove rows
TRUNCATE TABLE          │ Remove ALL rows (fast, no filter)
ON CONFLICT DO UPDATE   │ Upsert (insert or update)
ON CONFLICT DO NOTHING  │ Skip duplicates silently
RETURNING               │ Get back affected rows
────────────────────┴──────────────────────────────────────────────────────
```

---

## What's Next

You insert a customer with `plan = 'superduper'`. No error. You insert an order with `customer_id = 99999`. No error. You insert a negative price. No error.

The database accepts anything. Derek never set up constraints.

Maya: "The data is garbage because nothing enforces the rules. Fix it."

---

[← Chapter 3: JOINs](chapter-03-joins.md) | [Chapter 5: Data Integrity →](chapter-05-constraints.md)

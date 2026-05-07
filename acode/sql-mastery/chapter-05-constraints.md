# Chapter 5: "The Data Is Garbage"

[← Chapter 4: Modifying Data](chapter-04-insert-update-delete.md) | [Chapter 6: Window Functions →](chapter-06-window-functions.md)

---

## The Incident

Tuesday morning. Maya runs a customer report and gets this:

```
     name      |    plan     | country
---------------+-------------+---------
 Acme Corp     | enterprise  | US
 TechStart     | pro         | US
               | superduper  | NULL
 NULL          | enterprise  |
```

A customer with no name. A plan called "superduper." A country that's NULL when it shouldn't be. An order references `customer_id = 99999` — a customer that doesn't exist.

Derek never set up constraints. The database accepted anything. Now the data is garbage and every report is wrong.

Maya: "Make the database enforce the rules. If the data is invalid, reject it at the door."

---

## Data Types: The First Line of Defense

Every column has a type. Choose the right one:

```sql
-- ❌ Derek's approach: everything is TEXT
CREATE TABLE bad_example (
    price TEXT,        -- "29.99" or "twenty bucks" or ""
    quantity TEXT,     -- "5" or "five" or "-1"
    order_date TEXT    -- "2024-01-15" or "next Tuesday" or "asdf"
);

-- ✅ Proper types
CREATE TABLE good_example (
    price_cents INTEGER,       -- only whole numbers
    quantity INTEGER,          -- only whole numbers
    order_date DATE            -- only valid dates
);
```

| Type | Use For | Example |
|---|---|---|
| `INTEGER` | Whole numbers | IDs, quantities, cents |
| `BIGINT` | Large numbers | Timestamps as epoch, large counts |
| `NUMERIC(p,s)` | Exact decimals | Money (if not using cents) |
| `TEXT` | Variable-length strings | Names, emails, descriptions |
| `VARCHAR(n)` | Bounded strings | Country codes (2 chars) |
| `BOOLEAN` | True/false | Flags, toggles |
| `DATE` | Calendar date | `2024-01-15` |
| `TIMESTAMP` | Date + time | `2024-01-15 09:30:00` |
| `TIMESTAMPTZ` | Date + time + timezone | Always use this over TIMESTAMP |
| `UUID` | Unique identifiers | `gen_random_uuid()` |
| `JSONB` | Structured flexible data | Metadata, settings |

**Rule**: Store money as integers (cents). `$29.99` → `2999`. Floating point math is broken for money: `0.1 + 0.2 = 0.30000000000000004`.

---

## NOT NULL: Required Fields

```sql
ALTER TABLE customers
ALTER COLUMN name SET NOT NULL;
```

Now this fails:

```sql
INSERT INTO customers (email, plan) VALUES ('x@y.com', 'free');
-- ERROR: null value in column "name" violates not-null constraint
```

Good. A customer without a name is meaningless.

```sql
-- Fix existing NULLs first, then add the constraint
UPDATE customers SET name = 'Unknown' WHERE name IS NULL;
ALTER TABLE customers ALTER COLUMN name SET NOT NULL;
ALTER TABLE customers ALTER COLUMN country SET NOT NULL;
```

---

## DEFAULT: Sensible Fallbacks

```sql
ALTER TABLE customers
ALTER COLUMN plan SET DEFAULT 'free';

ALTER TABLE orders
ALTER COLUMN status SET DEFAULT 'pending';
```

Now if someone inserts without specifying a plan:

```sql
INSERT INTO customers (name, email, country)
VALUES ('NewUser', 'new@user.com', 'US');
-- plan automatically = 'free'
```

---

## CHECK: Business Rules

"Plans can only be: free, starter, pro, enterprise."

```sql
ALTER TABLE customers
ADD CONSTRAINT valid_plan
CHECK (plan IN ('free', 'starter', 'pro', 'enterprise'));
```

Now:

```sql
INSERT INTO customers (name, email, plan, country)
VALUES ('Bad', 'bad@bad.com', 'superduper', 'US');
-- ERROR: new row violates check constraint "valid_plan"
```

More CHECK constraints:

```sql
-- Prices must be positive
ALTER TABLE products
ADD CONSTRAINT positive_price
CHECK (price_cents > 0);

-- Quantity must be at least 1
ALTER TABLE order_items
ADD CONSTRAINT positive_quantity
CHECK (quantity >= 1);

-- Priority must be valid
ALTER TABLE tickets
ADD CONSTRAINT valid_priority
CHECK (priority IN ('low', 'medium', 'high', 'critical'));
```

---

## UNIQUE: No Duplicates

```sql
-- Email must be unique (already exists on customers, but let's understand it)
ALTER TABLE products
ADD CONSTRAINT unique_product_name
UNIQUE (name);
```

```sql
INSERT INTO products (name, category, price_cents)
VALUES ('Pro Dashboard', 'analytics', 9900);
-- ERROR: duplicate key value violates unique constraint "unique_product_name"
```

### Composite Unique

"A customer can only have one order per day per product" (business rule):

```sql
ALTER TABLE order_items
ADD CONSTRAINT one_product_per_order
UNIQUE (order_id, product_id);
```

---

## PRIMARY KEY: Identity

Every table needs a primary key — a column (or columns) that uniquely identifies each row. It's automatically `UNIQUE` and `NOT NULL`.

```sql
-- Already defined in our schema:
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,  -- auto-incrementing integer
    ...
);
```

| Strategy | Syntax | Pros | Cons |
|---|---|---|---|
| `SERIAL` | Auto-increment integer | Simple, compact | Predictable, gaps on delete |
| `BIGSERIAL` | Auto-increment bigint | Handles billions of rows | Same as SERIAL |
| `UUID` | `gen_random_uuid()` | Globally unique, no collisions | Larger, slower indexes |

For most tables, `SERIAL` or `BIGSERIAL` is fine. Use `UUID` when you need IDs generated outside the database (distributed systems, APIs).

---

## FOREIGN KEY: Referential Integrity

"An order must belong to a real customer."

```sql
-- Already in our schema:
CREATE TABLE orders (
    customer_id INTEGER REFERENCES customers(id),
    ...
);
```

This means:

```sql
INSERT INTO orders (customer_id, order_date, status, total_cents)
VALUES (99999, '2024-01-01', 'pending', 1000);
-- ERROR: insert or update on table "orders" violates foreign key constraint
-- Key (customer_id)=(99999) is not present in table "customers"
```

And:

```sql
DELETE FROM customers WHERE id = 1;
-- ERROR: update or delete on table "customers" violates foreign key constraint
-- Key (id)=(1) is still referenced from table "orders"
```

You can't delete a customer who has orders. The database protects data integrity.

### ON DELETE Options

| Option | Behavior |
|---|---|
| `RESTRICT` (default) | Block the delete |
| `CASCADE` | Delete the customer AND all their orders |
| `SET NULL` | Set `customer_id` to NULL on orphaned orders |
| `SET DEFAULT` | Set to default value |

```sql
-- If we want deleting a customer to also delete their orders:
ALTER TABLE orders
DROP CONSTRAINT orders_customer_id_fkey,
ADD CONSTRAINT orders_customer_id_fkey
    FOREIGN KEY (customer_id) REFERENCES customers(id)
    ON DELETE CASCADE;
```

⚠️ `CASCADE` is dangerous. Deleting one customer could cascade through orders → order_items → mrr_events. Use it carefully.

---

## NULLs: The Billion-Dollar Mistake

NULL means "unknown" or "not applicable." It's not zero. It's not empty string. It's the absence of a value.

### NULL Arithmetic

```sql
SELECT 5 + NULL;        -- NULL (not 5)
SELECT NULL = NULL;     -- NULL (not true!)
SELECT NULL != NULL;    -- NULL (not true!)
```

Nothing equals NULL. Not even NULL itself. Use `IS NULL` and `IS NOT NULL`:

```sql
-- ❌ Wrong
SELECT * FROM tickets WHERE resolved_at = NULL;  -- returns nothing!

-- ✅ Correct
SELECT * FROM tickets WHERE resolved_at IS NULL;
```

### COALESCE: NULL Replacement

```sql
SELECT
    name,
    COALESCE(country, 'Unknown') AS country
FROM customers;
```

`COALESCE` returns the first non-NULL argument. Chain multiple fallbacks:

```sql
SELECT COALESCE(nickname, name, email) AS display_name
FROM customers;
```

### NULLIF: Create NULLs

```sql
-- Avoid division by zero
SELECT total_cents / NULLIF(quantity, 0) AS unit_price
FROM order_items;
```

`NULLIF(quantity, 0)` returns NULL if quantity is 0. Division by NULL returns NULL instead of crashing.

---

## Putting It All Together: The Cleaned Schema

```sql
-- The constraints Derek should have added:
ALTER TABLE customers
    ALTER COLUMN name SET NOT NULL,
    ALTER COLUMN email SET NOT NULL,
    ALTER COLUMN country SET NOT NULL,
    ADD CONSTRAINT valid_plan CHECK (plan IN ('free', 'starter', 'pro', 'enterprise'));

ALTER TABLE products
    ADD CONSTRAINT positive_price CHECK (price_cents > 0),
    ADD CONSTRAINT unique_product_name UNIQUE (name);

ALTER TABLE orders
    ADD CONSTRAINT valid_status CHECK (status IN ('pending', 'completed', 'refunded', 'cancelled')),
    ADD CONSTRAINT positive_total CHECK (total_cents >= 0);

ALTER TABLE order_items
    ADD CONSTRAINT positive_quantity CHECK (quantity >= 1),
    ADD CONSTRAINT positive_unit_price CHECK (unit_price > 0);

ALTER TABLE tickets
    ADD CONSTRAINT valid_priority CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    ADD CONSTRAINT valid_ticket_status CHECK (status IN ('open', 'in_progress', 'resolved', 'closed'));
```

Now the database rejects bad data at the door. No more "superduper" plans. No more negative prices. No more orphaned orders.

---

## Quick Reference

```
────────────────────┬──────────────────────────────────────────────────────
Constraint          │ What It Enforces
────────────────────┼──────────────────────────────────────────────────────
NOT NULL            │ Column must have a value
DEFAULT             │ Value used when none provided
CHECK               │ Custom boolean condition must be true
UNIQUE              │ No duplicate values (NULLs are allowed)
PRIMARY KEY         │ Unique + Not Null (one per table)
FOREIGN KEY         │ Value must exist in referenced table
────────────────────┼──────────────────────────────────────────────────────
COALESCE(a, b, c)   │ First non-NULL value
NULLIF(a, b)        │ NULL if a = b, else a
IS NULL / IS NOT NULL│ Test for NULL (never use = NULL)
────────────────────┴──────────────────────────────────────────────────────
```

---

## What's Next

Hank: "I need a report showing each customer's revenue with a running total. And rank them — who's #1, #2, #3?"

You can't do running totals with GROUP BY. You need something more powerful.

Window functions.

---

[← Chapter 4: Modifying Data](chapter-04-insert-update-delete.md) | [Chapter 6: Window Functions →](chapter-06-window-functions.md)

# Chapter 1: "Show Me All the Customers"

[← Overview](chapter-00-overview.md) | [Chapter 2: Aggregates →](chapter-02-aggregates.md)

---

## The Request

First morning. Maya walks you to a monitor showing a Grafana dashboard with a big red number: **-$40,000 revenue**. Priya, the CEO, is in a glass office staring at the same number.

Maya: "Ignore that for now. First, I need you to understand what's in this database. Derek left no docs. Start with customers — who are they, how many, what plans are they on."

She hands you a sticky note:

> 1. How many customers do we have?
> 2. Who signed up this month?
> 3. Show me enterprise customers, sorted by signup date.

You open `psql` and stare at the blinking cursor.

---

## Seed the Database

Before you can query anything, you need data. Run this once:

```sql
-- Customers
INSERT INTO customers (name, email, plan, signed_up, country) VALUES
('Acme Corp', 'billing@acme.com', 'enterprise', '2024-01-15', 'US'),
('TechStart', 'admin@techstart.io', 'pro', '2024-02-20', 'US'),
('Berlin Analytics', 'hello@berlinanalytics.de', 'pro', '2024-03-01', 'DE'),
('Quick Books Ltd', 'info@quickbooks.co.uk', 'starter', '2024-03-15', 'GB'),
('Solo Dev', 'solo@gmail.com', 'free', '2024-04-01', 'US'),
('MegaRetail', 'ops@megaretail.com', 'enterprise', '2024-04-10', 'US'),
('Nordic SaaS', 'team@nordicsaas.fi', 'pro', '2024-05-01', 'FI'),
('DataHouse', 'contact@datahouse.jp', 'enterprise', '2024-05-15', 'JP'),
('FreshStart', 'hey@freshstart.com', 'starter', '2024-06-01', 'US'),
('CloudNine', 'support@cloudnine.io', 'pro', '2024-06-15', 'CA'),
('Pixel Perfect', 'design@pixelperfect.se', 'starter', '2024-07-01', 'SE'),
('OceanView', 'admin@oceanview.au', 'free', '2024-07-10', 'AU'),
('RocketShip', 'launch@rocketship.com', 'enterprise', '2024-08-01', 'US'),
('TinyTeam', 'hello@tinyteam.dev', 'free', '2024-08-15', 'NL'),
('GigaCorp', 'enterprise@gigacorp.com', 'enterprise', '2024-09-01', 'US');

-- Products
INSERT INTO products (name, category, price_cents, active) VALUES
('Basic Dashboard', 'analytics', 2900, true),
('Pro Dashboard', 'analytics', 9900, true),
('Enterprise Suite', 'analytics', 29900, true),
('Email Alerts', 'alerts', 1900, true),
('SMS Alerts', 'alerts', 4900, true),
('Weekly Report', 'reporting', 3900, true),
('Custom Report Builder', 'reporting', 14900, true),
('Legacy Viewer', 'analytics', 1900, false);

-- Orders
INSERT INTO orders (customer_id, order_date, status, total_cents) VALUES
(1, '2024-01-20', 'completed', 29900),
(1, '2024-03-15', 'completed', 4900),
(2, '2024-02-25', 'completed', 9900),
(3, '2024-03-05', 'completed', 9900),
(3, '2024-03-05', 'completed', 3900),
(4, '2024-03-20', 'completed', 2900),
(5, '2024-04-05', 'completed', 2900),
(6, '2024-04-15', 'completed', 29900),
(6, '2024-04-15', 'completed', 14900),
(6, '2024-05-01', 'refunded', 4900),
(7, '2024-05-05', 'completed', 9900),
(8, '2024-05-20', 'completed', 29900),
(8, '2024-06-01', 'completed', 4900),
(9, '2024-06-05', 'completed', 2900),
(10, '2024-06-20', 'completed', 9900),
(10, '2024-07-01', 'cancelled', 3900),
(11, '2024-07-05', 'completed', 2900),
(12, '2024-07-15', 'pending', 2900),
(13, '2024-08-05', 'completed', 29900),
(13, '2024-08-05', 'completed', 14900),
(14, '2024-08-20', 'completed', 2900),
(15, '2024-09-05', 'completed', 29900);

-- Order items
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(1, 3, 1, 29900), (2, 5, 1, 4900), (3, 2, 1, 9900),
(4, 2, 1, 9900), (5, 6, 1, 3900), (6, 1, 1, 2900),
(7, 1, 1, 2900), (8, 3, 1, 29900), (9, 7, 1, 14900),
(10, 5, 1, 4900), (11, 2, 1, 9900), (12, 3, 1, 29900),
(13, 5, 1, 4900), (14, 1, 1, 2900), (15, 2, 1, 9900),
(16, 6, 1, 3900), (17, 1, 1, 2900), (18, 1, 1, 2900),
(19, 3, 1, 29900), (20, 7, 1, 14900), (21, 1, 1, 2900),
(22, 3, 1, 29900);

-- MRR events
INSERT INTO mrr_events (customer_id, event_type, amount_cents, event_date) VALUES
(1, 'new', 29900, '2024-01-15'), (2, 'new', 9900, '2024-02-20'),
(3, 'new', 9900, '2024-03-01'), (4, 'new', 2900, '2024-03-15'),
(5, 'new', 0, '2024-04-01'), (6, 'new', 29900, '2024-04-10'),
(6, 'expansion', 14900, '2024-04-15'), (7, 'new', 9900, '2024-05-01'),
(8, 'new', 29900, '2024-05-15'), (9, 'new', 2900, '2024-06-01'),
(10, 'new', 9900, '2024-06-15'), (10, 'contraction', -3900, '2024-07-01'),
(11, 'new', 2900, '2024-07-01'), (12, 'new', 0, '2024-07-10'),
(5, 'churn', 0, '2024-07-15'), (13, 'new', 29900, '2024-08-01'),
(13, 'expansion', 14900, '2024-08-05'), (14, 'new', 0, '2024-08-15'),
(15, 'new', 29900, '2024-09-01');

-- Support tickets
INSERT INTO tickets (customer_id, subject, priority, status, created_at, resolved_at) VALUES
(1, 'Dashboard not loading', 'high', 'resolved', '2024-02-01 09:00:00', '2024-02-01 11:30:00'),
(1, 'Export button broken', 'medium', 'resolved', '2024-04-10 14:00:00', '2024-04-11 09:00:00'),
(3, 'Cannot add team members', 'high', 'resolved', '2024-03-20 10:00:00', '2024-03-20 16:00:00'),
(6, 'Billing discrepancy', 'critical', 'resolved', '2024-05-02 08:00:00', '2024-05-02 09:15:00'),
(6, 'Data not syncing', 'high', 'in_progress', '2024-09-10 11:00:00', NULL),
(8, 'Custom report error', 'medium', 'open', '2024-09-12 15:00:00', NULL),
(10, 'Slow dashboard load', 'low', 'open', '2024-09-15 09:00:00', NULL),
(13, 'Need API access', 'medium', 'resolved', '2024-08-10 10:00:00', '2024-08-12 14:00:00'),
(15, 'Onboarding help', 'low', 'open', '2024-09-08 16:00:00', NULL);
```

Data loaded. Time to answer Maya's questions.

---

## SELECT: Your First Query

The most basic SQL statement. "Give me data from this table."

```sql
SELECT * FROM customers;
```

```
 id |       name        |           email            |    plan    |      signed_up      | country
----+-------------------+----------------------------+------------+---------------------+---------
  1 | Acme Corp         | billing@acme.com           | enterprise | 2024-01-15 00:00:00 | US
  2 | TechStart         | admin@techstart.io         | pro        | 2024-02-20 00:00:00 | US
  3 | Berlin Analytics  | hello@berlinanalytics.de   | pro        | 2024-03-01 00:00:00 | DE
 ...
```

`SELECT *` means "all columns." It works, but Maya immediately says:

> "Never use `SELECT *` in production code. It pulls columns you don't need, breaks when someone adds a column, and makes queries harder to read. Always name your columns."

```sql
SELECT name, email, plan FROM customers;
```

Better. You know exactly what you're getting.

---

## WHERE: Filtering Rows

Maya's sticky note #3: "Show me enterprise customers."

```sql
SELECT name, email, signed_up
FROM customers
WHERE plan = 'enterprise';
```

```
     name     |         email          |      signed_up
--------------+------------------------+---------------------
 Acme Corp    | billing@acme.com       | 2024-01-15 00:00:00
 MegaRetail   | ops@megaretail.com     | 2024-04-10 00:00:00
 DataHouse    | contact@datahouse.jp   | 2024-05-15 00:00:00
 RocketShip   | launch@rocketship.com  | 2024-08-01 00:00:00
 GigaCorp     | enterprise@gigacorp.com| 2024-09-01 00:00:00
```

Five enterprise customers. `WHERE` filters rows — only rows where the condition is true come back.

### Comparison Operators

| Operator | Meaning | Example |
|---|---|---|
| `=` | Equals | `plan = 'pro'` |
| `!=` or `<>` | Not equals | `status <> 'cancelled'` |
| `>`, `<` | Greater/less than | `price_cents > 5000` |
| `>=`, `<=` | Greater/less or equal | `signed_up >= '2024-06-01'` |
| `BETWEEN` | Range (inclusive) | `price_cents BETWEEN 1000 AND 5000` |
| `IN` | One of a list | `plan IN ('pro', 'enterprise')` |
| `LIKE` | Pattern match | `email LIKE '%@gmail.com'` |
| `IS NULL` | Is null | `resolved_at IS NULL` |

### Combining Conditions

```sql
-- Enterprise customers in the US
SELECT name, country
FROM customers
WHERE plan = 'enterprise'
  AND country = 'US';

-- Pro OR enterprise customers
SELECT name, plan
FROM customers
WHERE plan IN ('pro', 'enterprise');

-- Signed up in Q1 2024
SELECT name, signed_up
FROM customers
WHERE signed_up >= '2024-01-01'
  AND signed_up < '2024-04-01';
```

Note: for dates, use `>=` start and `<` end-exclusive. Don't use `BETWEEN` for timestamps — it includes the end boundary, which can miss or double-count records at midnight.

---

## ORDER BY: Sorting Results

Sticky note #3 continued: "...sorted by signup date."

```sql
SELECT name, plan, signed_up
FROM customers
WHERE plan = 'enterprise'
ORDER BY signed_up ASC;
```

`ASC` = oldest first (ascending). `DESC` = newest first (descending). Default is `ASC`.

```sql
-- Most recent signups first
SELECT name, signed_up
FROM customers
ORDER BY signed_up DESC;

-- Sort by plan, then by name within each plan
SELECT name, plan
FROM customers
ORDER BY plan, name;
```

You can sort by multiple columns. Postgres evaluates them left to right — first by `plan`, then by `name` within each plan group.

---

## LIMIT and OFFSET: Pagination

Maya: "Just show me the 5 most recent signups."

```sql
SELECT name, plan, signed_up
FROM customers
ORDER BY signed_up DESC
LIMIT 5;
```

`LIMIT` caps the result set. `OFFSET` skips rows:

```sql
-- Page 2 (rows 6-10)
SELECT name, plan, signed_up
FROM customers
ORDER BY signed_up DESC
LIMIT 5 OFFSET 5;
```

⚠️ **Warning**: `OFFSET` gets slower as the number grows. For large tables, use keyset pagination instead (we'll cover that in Chapter 11 when The Slow Query appears).

---

## DISTINCT: Removing Duplicates

"What countries are our customers in?"

```sql
SELECT DISTINCT country
FROM customers
ORDER BY country;
```

```
 country
---------
 AU
 CA
 DE
 FI
 GB
 JP
 NL
 SE
 US
```

`DISTINCT` removes duplicate rows from the result. Without it, you'd see "US" five times.

---

## Aliases: Renaming Columns

The output column names are whatever you selected. You can rename them:

```sql
SELECT
    name AS customer_name,
    plan AS subscription_tier,
    signed_up AS join_date
FROM customers
WHERE plan = 'enterprise';
```

`AS` is optional — `name customer_name` works too — but always use it for clarity.

---

## The Anatomy of a SELECT

Every SELECT follows this order:

```sql
SELECT columns        -- what to show
FROM table            -- where to look
WHERE condition       -- which rows to include
ORDER BY column       -- how to sort
LIMIT n               -- how many to return
OFFSET n              -- how many to skip
```

Postgres executes them in a different order internally:

```
1. FROM    → find the table
2. WHERE   → filter rows
3. SELECT  → pick columns
4. ORDER BY → sort
5. LIMIT/OFFSET → cap results
```

This matters. You can't use a column alias in `WHERE` because `SELECT` hasn't run yet:

```sql
-- ❌ This fails
SELECT name, price_cents / 100.0 AS price_dollars
FROM products
WHERE price_dollars > 50;

-- ✅ This works
SELECT name, price_cents / 100.0 AS price_dollars
FROM products
WHERE price_cents > 5000;
```

---

## Answering Maya's Questions

### 1. How many customers do we have?

```sql
SELECT count(*) FROM customers;
```

```
 count
-------
    15
```

(We'll cover `COUNT` properly in Chapter 2. For now, it counts rows.)

### 2. Who signed up this month?

```sql
SELECT name, email, signed_up
FROM customers
WHERE signed_up >= date_trunc('month', CURRENT_DATE)
ORDER BY signed_up DESC;
```

`date_trunc('month', CURRENT_DATE)` gives you the first day of the current month. This query adapts automatically — no hardcoded dates.

### 3. Enterprise customers, sorted by signup date

```sql
SELECT name, email, country, signed_up
FROM customers
WHERE plan = 'enterprise'
ORDER BY signed_up ASC;
```

Done. Maya nods. "Good. Now Hank from Sales just walked in. He wants to know how much revenue we made last month."

That's aggregates. That's Chapter 2.

---

## Quick Reference

```
────────────────────┬──────────────────────────────────────────────
Clause              │ What It Does
────────────────────┼──────────────────────────────────────────────
SELECT              │ Choose which columns to return
FROM                │ Specify the table
WHERE               │ Filter rows (before grouping)
ORDER BY            │ Sort results (ASC or DESC)
LIMIT               │ Cap number of rows returned
OFFSET              │ Skip N rows (for pagination)
DISTINCT            │ Remove duplicate rows
AS                  │ Rename a column in output
────────────────────┴──────────────────────────────────────────────
```

---

[← Overview](chapter-00-overview.md) | [Chapter 2: Aggregates →](chapter-02-aggregates.md)

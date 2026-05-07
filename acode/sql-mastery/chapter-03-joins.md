# Chapter 3: "Connect Orders to Customers"

[← Chapter 2: Aggregates](chapter-02-aggregates.md) | [Chapter 4: Modifying Data →](chapter-04-insert-update-delete.md)

---

## The Request

Maya pulls up a spreadsheet. "Hank wants a customer revenue report. Name, email, total spent. Sorted by biggest spender first."

The problem: customer names are in `customers`. Revenue is in `orders`. They're in different tables.

You need to connect them.

---

## The Concept: Why JOINs Exist

Relational databases split data across tables to avoid repetition. You don't store the customer's name on every order — you store a `customer_id` that points back to the `customers` table.

```
customers                          orders
┌────┬───────────┐                ┌────┬─────────────┬─────────────┐
│ id │ name      │                │ id │ customer_id │ total_cents │
├────┼───────────┤                ├────┼─────────────┼─────────────┤
│  1 │ Acme Corp │◄───────────────│  1 │      1      │    29900    │
│  2 │ TechStart │◄──────┐        │  2 │      1      │     4900    │
│  3 │ Berlin... │       └────────│  3 │      2      │     9900    │
└────┴───────────┘                └────┴─────────────┴─────────────┘
```

A JOIN reconnects them. "For each order, find the matching customer."

---

## INNER JOIN: Only Matches

```sql
SELECT
    c.name,
    c.email,
    o.order_date,
    o.total_cents / 100.0 AS total_dollars
FROM customers c
INNER JOIN orders o ON o.customer_id = c.id
WHERE o.status = 'completed'
ORDER BY o.order_date DESC;
```

```
      name       |         email          | order_date | total_dollars
-----------------+------------------------+------------+---------------
 GigaCorp        | enterprise@gigacorp.com| 2024-09-05 |        299.00
 RocketShip      | launch@rocketship.com  | 2024-08-05 |        299.00
 RocketShip      | launch@rocketship.com  | 2024-08-05 |        149.00
 TinyTeam        | hello@tinyteam.dev     | 2024-08-20 |         29.00
 ...
```

### Breaking It Down

| Part | What It Does |
|---|---|
| `FROM customers c` | Start with customers table, alias it `c` |
| `INNER JOIN orders o` | Bring in orders table, alias it `o` |
| `ON o.customer_id = c.id` | The connection rule — match on this column |
| `c.name`, `o.total_cents` | Use aliases to reference columns from each table |

`INNER JOIN` only returns rows where a match exists in BOTH tables. Customers with no orders? Gone. Orders with no customer? Gone.

### Hank's Report: Revenue Per Customer

```sql
SELECT
    c.name,
    c.email,
    c.plan,
    count(o.id) AS order_count,
    sum(o.total_cents) / 100.0 AS total_spent
FROM customers c
INNER JOIN orders o ON o.customer_id = c.id
WHERE o.status = 'completed'
GROUP BY c.id, c.name, c.email, c.plan
ORDER BY total_spent DESC;
```

```
      name       |          email           |    plan    | order_count | total_spent
-----------------+--------------------------+------------+-------------+-------------
 MegaRetail      | ops@megaretail.com       | enterprise |           2 |      448.00
 RocketShip      | launch@rocketship.com    | enterprise |           2 |      448.00
 DataHouse       | contact@datahouse.jp     | enterprise |           2 |      348.00
 Acme Corp       | billing@acme.com         | enterprise |           2 |      348.00
 GigaCorp        | enterprise@gigacorp.com  | enterprise |           1 |      299.00
 ...
```

Enterprise customers dominate. Hank will love this.

---

## LEFT JOIN: Keep Everything on the Left

Maya: "Which customers have NEVER placed an order?"

`INNER JOIN` drops customers without orders. You need `LEFT JOIN`:

```sql
SELECT
    c.name,
    c.plan,
    o.id AS order_id
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
WHERE o.id IS NULL;
```

```
    name     |  plan  | order_id
-------------+--------+----------
 Nordic SaaS | pro    |     NULL
```

Wait — Nordic SaaS is on the pro plan but never ordered? That's weird. (Turns out they signed up but their payment failed. We'll handle that in Chapter 5.)

### How LEFT JOIN Works

```
INNER JOIN:                    LEFT JOIN:
Only matching rows             All left rows + matches

customers  orders              customers  orders
┌───┐      ┌───┐              ┌───┐      ┌───┐
│ A │──────│ A │              │ A │──────│ A │
│ B │──────│ B │              │ B │──────│ B │
│ C │      │   │              │ C │      │NULL│  ← kept, with NULLs
└───┘      └───┘              └───┘      └───┘
```

`LEFT JOIN` keeps ALL rows from the left table (`customers`). If there's no match in the right table (`orders`), the right columns are NULL.

---

## RIGHT JOIN and FULL JOIN

| Join Type | Keeps |
|---|---|
| `INNER JOIN` | Only rows with matches in both tables |
| `LEFT JOIN` | All rows from left + matches from right |
| `RIGHT JOIN` | All rows from right + matches from left |
| `FULL OUTER JOIN` | All rows from both, NULLs where no match |

In practice, you'll use `INNER JOIN` and `LEFT JOIN` 95% of the time. `RIGHT JOIN` is just a `LEFT JOIN` with the tables swapped. `FULL OUTER JOIN` is rare — useful for reconciliation queries.

```sql
-- Find orders that reference a deleted customer (data integrity check)
SELECT o.id, o.customer_id, o.total_cents
FROM orders o
LEFT JOIN customers c ON c.id = o.customer_id
WHERE c.id IS NULL;
```

If this returns rows, you have orphaned orders. Derek might have deleted customers without cleaning up their orders. (We'll add constraints to prevent this in Chapter 5.)

---

## Joining Multiple Tables

Maya: "I need order details — customer name, product name, quantity, price."

That's three tables: `customers` → `orders` → `order_items` → `products`.

```sql
SELECT
    c.name AS customer,
    p.name AS product,
    p.category,
    oi.quantity,
    oi.unit_price / 100.0 AS price
FROM customers c
JOIN orders o ON o.customer_id = c.id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id
WHERE o.status = 'completed'
ORDER BY c.name, o.order_date;
```

```
    customer    |       product        | category  | quantity | price
----------------+----------------------+-----------+----------+-------
 Acme Corp      | Enterprise Suite     | analytics |        1 | 299.00
 Acme Corp      | SMS Alerts           | alerts    |        1 |  49.00
 Berlin Analyt. | Pro Dashboard        | analytics |        1 |  99.00
 Berlin Analyt. | Weekly Report        | reporting |        1 |  39.00
 ...
```

Each `JOIN` adds one more table to the chain. The `ON` clause specifies how they connect. Think of it as following the foreign keys.

---

## Self JOIN: A Table Joined to Itself

Maya: "Find customers in the same country as Acme Corp."

```sql
SELECT c2.name, c2.plan, c2.country
FROM customers c1
JOIN customers c2 ON c2.country = c1.country
WHERE c1.name = 'Acme Corp'
  AND c2.name != 'Acme Corp';
```

```
     name     |    plan    | country
--------------+------------+---------
 TechStart    | pro        | US
 Solo Dev     | free       | US
 MegaRetail   | enterprise | US
 FreshStart   | starter    | US
 RocketShip   | enterprise | US
 GigaCorp     | enterprise | US
```

Same table, two aliases (`c1` and `c2`). `c1` finds Acme Corp. `c2` finds everyone else in the same country.

---

## CROSS JOIN: Every Combination

Rarely useful, but important to understand. A `CROSS JOIN` produces every possible combination of rows from both tables:

```sql
-- Every customer × every product (cartesian product)
SELECT c.name, p.name
FROM customers c
CROSS JOIN products p;
-- 15 customers × 8 products = 120 rows
```

You almost never want this. But if you accidentally forget the `ON` clause in a regular JOIN, you get a cross join — and suddenly your query returns millions of rows. That's how The Slow Query was born.

---

## The Duplicate Trap

You write a revenue report and get weird numbers. Total revenue is higher than expected.

```sql
-- ❌ BUG: counts revenue multiple times if customer has multiple order items
SELECT
    c.name,
    sum(o.total_cents) / 100.0 AS revenue
FROM customers c
JOIN orders o ON o.customer_id = c.id
JOIN order_items oi ON oi.order_id = o.id
WHERE o.status = 'completed'
GROUP BY c.name
ORDER BY revenue DESC;
```

The problem: if an order has 2 line items, the `total_cents` from the `orders` table gets summed TWICE — once for each line item row. The JOIN multiplies rows.

```sql
-- ✅ FIX: aggregate at the right level
SELECT
    c.name,
    sum(o.total_cents) / 100.0 AS revenue
FROM customers c
JOIN orders o ON o.customer_id = c.id
WHERE o.status = 'completed'
GROUP BY c.name
ORDER BY revenue DESC;
```

Don't join `order_items` if you only need order-level totals. Or use a subquery (Chapter 7).

**Rule**: Every JOIN can multiply rows. If you're aggregating, make sure you're aggregating at the right level.

---

## The Revenue Mystery: Solved

Maya: "Now figure out why the dashboard shows -$40,000."

You trace Derek's view:

```sql
-- Derek's broken view (reconstructed)
SELECT sum(amount_cents) / 100.0 AS mrr
FROM mrr_events;
```

```
   mrr
---------
 1868.00
```

That's positive. So where's the negative number? You dig into the dashboard code and find:

```sql
-- The actual dashboard query (found in Derek's notes)
SELECT sum(amount_cents) / 100.0 AS daily_revenue
FROM mrr_events
WHERE event_date = CURRENT_DATE;
```

On days with no events, this returns NULL. The dashboard JavaScript treats NULL as the string "null", parses it as NaN, and displays -$40,000 (a rendering bug in the charting library).

The database isn't wrong. The dashboard is. But you needed JOINs and aggregates to prove it.

Maya: "Write a proper view. We'll fix the dashboard later."

```sql
-- A correct daily revenue view
SELECT
    COALESCE(sum(amount_cents), 0) / 100.0 AS daily_revenue
FROM mrr_events
WHERE event_date = CURRENT_DATE;
```

`COALESCE(value, 0)` — if the value is NULL, use 0 instead. No more phantom negative revenue.

---

## Quick Reference

```
────────────────────┬──────────────────────────────────────────────────────
Join Type           │ What It Returns
────────────────────┼──────────────────────────────────────────────────────
INNER JOIN          │ Only rows with matches in both tables
LEFT JOIN           │ All left rows + matching right (NULL if no match)
RIGHT JOIN          │ All right rows + matching left (NULL if no match)
FULL OUTER JOIN     │ All rows from both (NULLs where no match)
CROSS JOIN          │ Every combination (cartesian product)
Self JOIN           │ Table joined to itself (use different aliases)
────────────────────┼──────────────────────────────────────────────────────
ON                  │ The condition that connects two tables
Table aliases       │ Short names (FROM customers c)
────────────────────┴──────────────────────────────────────────────────────
```

### Common Patterns

```sql
-- "Find rows with no match" (anti-join)
SELECT c.* FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
WHERE o.id IS NULL;

-- "Aggregate after joining"
SELECT c.name, sum(o.total_cents)
FROM customers c
JOIN orders o ON o.customer_id = c.id
GROUP BY c.name;

-- "Join through a bridge table"
SELECT c.name, p.name
FROM customers c
JOIN orders o ON o.customer_id = c.id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id;
```

---

## What's Next

Priya: "We're launching a new product line next week. I need you to add products, update prices, and clean up the old data Derek left behind."

Time to write to the database, not just read from it.

---

[← Chapter 2: Aggregates](chapter-02-aggregates.md) | [Chapter 4: Modifying Data →](chapter-04-insert-update-delete.md)

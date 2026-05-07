# Chapter 2: "How Much Did We Sell Last Month?"

[← Chapter 1: SELECT](chapter-01-select.md) | [Chapter 3: JOINs →](chapter-03-joins.md)

---

## The Request

Hank from Sales barges in at 2:47 PM. He has a board slide due at 3:00 PM.

"I need three numbers. Total revenue last month. Average order value. Number of paying customers. Go."

You have 13 minutes.

---

## COUNT: How Many?

```sql
-- Total number of orders
SELECT count(*) FROM orders;
```

```
 count
-------
    22
```

`count(*)` counts all rows. `count(column)` counts non-NULL values in that column:

```sql
-- How many tickets have been resolved?
SELECT
    count(*) AS total_tickets,
    count(resolved_at) AS resolved_tickets
FROM tickets;
```

```
 total_tickets | resolved_tickets
---------------+------------------
             9 |                5
```

Four tickets have `resolved_at = NULL` — they're still open. `count(resolved_at)` skips them.

---

## SUM: How Much?

```sql
-- Total revenue from completed orders
SELECT sum(total_cents) / 100.0 AS total_revenue_dollars
FROM orders
WHERE status = 'completed';
```

```
 total_revenue_dollars
-----------------------
              2519.00
```

⚠️ **The trap**: if you forget `WHERE status = 'completed'`, you include refunded and cancelled orders. That's how Priya's dashboard showed negative revenue — Derek's view summed everything, including refunds stored as negative amounts in `mrr_events`.

---

## AVG: What's Typical?

```sql
-- Average order value (completed only)
SELECT
    round(avg(total_cents) / 100.0, 2) AS avg_order_dollars
FROM orders
WHERE status = 'completed';
```

```
 avg_order_dollars
-------------------
            131.00
```

`round(value, 2)` rounds to 2 decimal places. Without it, you get `130.9999999...` and Hank's slide looks unprofessional.

---

## MIN and MAX: The Extremes

```sql
SELECT
    min(total_cents) / 100.0 AS smallest_order,
    max(total_cents) / 100.0 AS largest_order
FROM orders
WHERE status = 'completed';
```

```
 smallest_order | largest_order
----------------+---------------
          29.00 |        299.00
```

---

## GROUP BY: Aggregates Per Category

Hank's back. "Break it down by month."

```sql
SELECT
    date_trunc('month', order_date) AS month,
    count(*) AS order_count,
    sum(total_cents) / 100.0 AS revenue
FROM orders
WHERE status = 'completed'
GROUP BY date_trunc('month', order_date)
ORDER BY month;
```

```
        month        | order_count | revenue
---------------------+-------------+---------
 2024-01-01 00:00:00 |           1 |  299.00
 2024-02-01 00:00:00 |           1 |   99.00
 2024-03-01 00:00:00 |           3 |  167.00
 2024-04-01 00:00:00 |           3 |  477.00
 2024-05-01 00:00:00 |           2 |  398.00
 2024-06-01 00:00:00 |           3 |  157.00
 2024-07-01 00:00:00 |           1 |   29.00
 2024-08-01 00:00:00 |           4 |  477.00
 2024-09-01 00:00:00 |           1 |  299.00
```

`GROUP BY` splits rows into buckets. Each bucket gets its own aggregate. Think of it as: "For each month, count the orders and sum the revenue."

### The Rule

> Every column in `SELECT` must either be in `GROUP BY` or inside an aggregate function.

```sql
-- ❌ This fails: "name" is not aggregated or grouped
SELECT name, count(*)
FROM customers
GROUP BY plan;

-- ✅ This works
SELECT plan, count(*) AS customer_count
FROM customers
GROUP BY plan;
```

```
    plan    | customer_count
------------+----------------
 enterprise |              5
 free       |              3
 pro        |              4
 starter    |              3
```

---

## HAVING: Filtering Groups

Maya: "Which plans have more than 3 customers?"

You can't use `WHERE` to filter aggregated results — `WHERE` runs before `GROUP BY`. Use `HAVING`:

```sql
SELECT plan, count(*) AS customer_count
FROM customers
GROUP BY plan
HAVING count(*) > 3;
```

```
    plan    | customer_count
------------+----------------
 enterprise |              5
 pro        |              4
```

### WHERE vs HAVING

| Clause | Filters | Runs |
|---|---|---|
| `WHERE` | Individual rows | Before grouping |
| `HAVING` | Groups (aggregated results) | After grouping |

```sql
-- Months where completed orders totaled more than $300
SELECT
    date_trunc('month', order_date) AS month,
    sum(total_cents) / 100.0 AS revenue
FROM orders
WHERE status = 'completed'          -- filter rows first
GROUP BY date_trunc('month', order_date)
HAVING sum(total_cents) > 30000     -- then filter groups
ORDER BY month;
```

`WHERE` removes non-completed orders. `HAVING` removes months with less than $300 revenue. Different jobs, different stages.

---

## Multiple Aggregates in One Query

Hank's slide needs everything at once:

```sql
SELECT
    count(DISTINCT customer_id) AS paying_customers,
    count(*) AS total_orders,
    sum(total_cents) / 100.0 AS total_revenue,
    round(avg(total_cents) / 100.0, 2) AS avg_order_value,
    min(order_date) AS first_order,
    max(order_date) AS last_order
FROM orders
WHERE status = 'completed';
```

```
 paying_customers | total_orders | total_revenue | avg_order_value | first_order | last_order
------------------+--------------+---------------+-----------------+-------------+------------
               13 |           19 |       2519.00 |          132.58 | 2024-01-20  | 2024-09-05
```

`count(DISTINCT customer_id)` — counts unique customers, not total orders. Without `DISTINCT`, a customer with 3 orders counts as 3.

---

## GROUP BY with Multiple Columns

"Break revenue down by month AND status."

```sql
SELECT
    date_trunc('month', order_date) AS month,
    status,
    count(*) AS orders,
    sum(total_cents) / 100.0 AS total
FROM orders
GROUP BY date_trunc('month', order_date), status
ORDER BY month, status;
```

Each unique combination of (month, status) becomes its own group. You'll see rows like:

```
        month        |   status   | orders | total
---------------------+------------+--------+-------
 2024-04-01 00:00:00 | completed  |      3 | 477.00
 2024-05-01 00:00:00 | completed  |      2 | 398.00
 2024-05-01 00:00:00 | refunded   |      1 |  49.00
 2024-07-01 00:00:00 | cancelled  |      1 |  39.00
 2024-07-01 00:00:00 | completed  |      1 |  29.00
 2024-07-01 00:00:00 | pending    |      1 |  29.00
```

Now you can see that May had a refund and July had a cancellation. That's where Priya's negative number might be coming from.

---

## The Revenue Mystery: A First Look

Maya leans over. "Check the MRR events table. Derek used that for the dashboard."

```sql
SELECT
    event_type,
    count(*) AS events,
    sum(amount_cents) / 100.0 AS total
FROM mrr_events
GROUP BY event_type
ORDER BY total DESC;
```

```
  event_type  | events |  total
--------------+--------+---------
 new          |     15 | 1609.00
 expansion    |      2 |  298.00
 contraction  |      1 |  -39.00
 churn        |      1 |    0.00
```

Interesting. Contraction is negative. Churn is zero (free plan customer). The dashboard probably sums `amount_cents` without filtering — and if there's a bug in how refunds are recorded...

We'll dig deeper in Chapter 3 when we JOIN these tables together. For now, you have Hank's numbers.

---

## Hank's Slide (Done at 2:59 PM)

```sql
-- The final query for Hank
SELECT
    count(DISTINCT customer_id) AS paying_customers,
    sum(total_cents) / 100.0 AS revenue_dollars,
    round(avg(total_cents) / 100.0, 2) AS avg_order_value
FROM orders
WHERE status = 'completed'
  AND order_date >= date_trunc('month', CURRENT_DATE - interval '1 month')
  AND order_date < date_trunc('month', CURRENT_DATE);
```

Hank grabs the numbers and runs. You hear him presenting 30 seconds later.

---

## Execution Order (Updated)

```
1. FROM       → find the table
2. WHERE      → filter individual rows
3. GROUP BY   → bucket rows into groups
4. HAVING     → filter groups
5. SELECT     → compute columns and aggregates
6. ORDER BY   → sort
7. LIMIT      → cap results
```

This is why you can't use a column alias from `SELECT` in `WHERE` or `HAVING` — they haven't been computed yet. But you CAN use an alias in `ORDER BY` because it runs after `SELECT`.

---

## Quick Reference

```
────────────────────┬──────────────────────────────────────────────
Function            │ What It Does
────────────────────┼──────────────────────────────────────────────
count(*)            │ Count all rows in the group
count(col)          │ Count non-NULL values
count(DISTINCT col) │ Count unique non-NULL values
sum(col)            │ Total of all values
avg(col)            │ Average (ignores NULLs)
min(col)            │ Smallest value
max(col)            │ Largest value
round(val, n)       │ Round to n decimal places
────────────────────┼──────────────────────────────────────────────
GROUP BY            │ Split rows into groups for aggregation
HAVING              │ Filter groups (after aggregation)
────────────────────┴──────────────────────────────────────────────
```

---

## What's Next

Maya: "Good. Now I need you to figure out which customers are generating the most revenue. That means connecting orders to customers. You'll need JOINs."

You've been dreading this.

---

[← Chapter 1: SELECT](chapter-01-select.md) | [Chapter 3: JOINs →](chapter-03-joins.md)

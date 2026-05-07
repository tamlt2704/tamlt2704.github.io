# Chapter 9: "Handle This Complex Logic"

[← Chapter 8: Views](chapter-08-views.md) | [Chapter 10: Dates & Times →](chapter-10-dates.md)

---

## The Request

Hank's back. "I need customer segments. 'High Value' if they spent over $300, 'Medium' if over $100, 'Low' otherwise. And a pivot table — how many customers per plan per segment."

This isn't a filter. It's a classification. You need conditional logic inside SQL.

---

## CASE: SQL's If/Else

```sql
SELECT
    c.name,
    c.plan,
    COALESCE(sum(o.total_cents), 0) / 100.0 AS total_spent,
    CASE
        WHEN COALESCE(sum(o.total_cents), 0) > 30000 THEN 'High Value'
        WHEN COALESCE(sum(o.total_cents), 0) > 10000 THEN 'Medium'
        ELSE 'Low'
    END AS segment
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id AND o.status = 'completed'
GROUP BY c.id, c.name, c.plan
ORDER BY total_spent DESC;
```

```
      name       |    plan    | total_spent |  segment
-----------------+------------+-------------+------------
 MegaRetail      | enterprise |      448.00 | High Value
 RocketShip      | enterprise |      448.00 | High Value
 DataHouse       | enterprise |      348.00 | High Value
 Acme Corp       | enterprise |      348.00 | High Value
 GigaCorp        | enterprise |      299.00 | High Value
 Berlin Analytics| pro        |      138.00 | Medium
 CloudNine       | pro        |       99.00 | Low
 ...
```

### CASE Syntax

```sql
-- Searched CASE (most common)
CASE
    WHEN condition1 THEN result1
    WHEN condition2 THEN result2
    ELSE default_result
END

-- Simple CASE (equality check)
CASE column
    WHEN 'value1' THEN result1
    WHEN 'value2' THEN result2
    ELSE default_result
END
```

Conditions are evaluated top to bottom. First match wins. If nothing matches and there's no `ELSE`, the result is NULL.

---

## CASE in ORDER BY

"Sort tickets by priority — critical first, then high, medium, low."

```sql
SELECT subject, priority, created_at
FROM tickets
WHERE status IN ('open', 'in_progress')
ORDER BY
    CASE priority
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
    END,
    created_at ASC;
```

You can use CASE anywhere an expression is valid: SELECT, WHERE, ORDER BY, GROUP BY, HAVING.

---

## Conditional Aggregation: The Pivot Table

Hank's pivot: "How many customers per plan per segment?"

```sql
WITH customer_segments AS (
    SELECT
        c.plan,
        CASE
            WHEN COALESCE(sum(o.total_cents), 0) > 30000 THEN 'High Value'
            WHEN COALESCE(sum(o.total_cents), 0) > 10000 THEN 'Medium'
            ELSE 'Low'
        END AS segment
    FROM customers c
    LEFT JOIN orders o ON o.customer_id = c.id AND o.status = 'completed'
    GROUP BY c.id, c.plan
)
SELECT
    plan,
    count(*) FILTER (WHERE segment = 'High Value') AS high_value,
    count(*) FILTER (WHERE segment = 'Medium') AS medium,
    count(*) FILTER (WHERE segment = 'Low') AS low,
    count(*) AS total
FROM customer_segments
GROUP BY plan
ORDER BY total DESC;
```

```
    plan    | high_value | medium | low | total
------------+------------+--------+-----+-------
 enterprise |          5 |      0 |   0 |     5
 pro        |          0 |      1 |   3 |     4
 starter    |          0 |      0 |   3 |     3
 free       |          0 |      0 |   3 |     3
```

### FILTER: PostgreSQL's Clean Conditional Aggregate

```sql
-- PostgreSQL-specific (cleaner)
count(*) FILTER (WHERE segment = 'High Value')

-- Standard SQL equivalent (works everywhere)
sum(CASE WHEN segment = 'High Value' THEN 1 ELSE 0 END)
```

Both produce the same result. `FILTER` is more readable.

---

## Conditional Aggregation Patterns

### Revenue by Status (Pivot)

```sql
SELECT
    date_trunc('month', order_date) AS month,
    sum(total_cents) FILTER (WHERE status = 'completed') / 100.0 AS completed,
    sum(total_cents) FILTER (WHERE status = 'refunded') / 100.0 AS refunded,
    sum(total_cents) FILTER (WHERE status = 'cancelled') / 100.0 AS cancelled
FROM orders
GROUP BY date_trunc('month', order_date)
ORDER BY month;
```

```
        month        | completed | refunded | cancelled
---------------------+-----------+----------+-----------
 2024-01-01 00:00:00 |    299.00 |          |
 2024-04-01 00:00:00 |    477.00 |          |
 2024-05-01 00:00:00 |    398.00 |    49.00 |
 2024-07-01 00:00:00 |     29.00 |          |     39.00
```

One row per month, columns for each status. This is how you build pivot tables in SQL.

### Boolean Aggregation

"What percentage of orders are completed?"

```sql
SELECT
    count(*) AS total,
    count(*) FILTER (WHERE status = 'completed') AS completed,
    round(
        100.0 * count(*) FILTER (WHERE status = 'completed') / count(*), 1
    ) AS completion_rate
FROM orders;
```

---

## COALESCE and NULLIF in Practice

### COALESCE: Replace NULLs

```sql
-- Show "No orders" instead of NULL for customers without orders
SELECT
    c.name,
    COALESCE(
        (SELECT max(order_date)::text FROM orders WHERE customer_id = c.id),
        'No orders'
    ) AS last_order
FROM customers c;
```

### NULLIF: Avoid Division by Zero

```sql
-- Average resolution time (avoid dividing by zero if no resolved tickets)
SELECT
    c.name,
    count(*) FILTER (WHERE t.status = 'resolved') AS resolved,
    round(
        avg(extract(epoch FROM (t.resolved_at - t.created_at)) / 3600)
        FILTER (WHERE t.resolved_at IS NOT NULL), 1
    ) AS avg_hours_to_resolve
FROM customers c
LEFT JOIN tickets t ON t.customer_id = c.id
GROUP BY c.id, c.name
HAVING count(t.id) > 0;
```

---

## GREATEST and LEAST

```sql
-- Ensure a minimum price of $10 (1000 cents)
SELECT
    name,
    price_cents / 100.0 AS original_price,
    GREATEST(price_cents, 1000) / 100.0 AS effective_price
FROM products;

-- Cap discount at 50%
SELECT
    name,
    LEAST(discount_pct, 50) AS capped_discount
FROM promotions;
```

---

## Real-World: Customer Health Score

Priya wants a "customer health" indicator combining multiple signals:

```sql
CREATE VIEW customer_health AS
WITH metrics AS (
    SELECT
        c.id,
        c.name,
        c.plan,
        -- Revenue signal
        COALESCE(sum(o.total_cents), 0) / 100.0 AS total_spent,
        -- Recency signal
        max(o.order_date) AS last_order,
        -- Support signal
        (SELECT count(*) FROM tickets t
         WHERE t.customer_id = c.id
           AND t.priority IN ('high', 'critical')
           AND t.status IN ('open', 'in_progress')) AS open_critical_tickets
    FROM customers c
    LEFT JOIN orders o ON o.customer_id = c.id AND o.status = 'completed'
    GROUP BY c.id, c.name, c.plan
)
SELECT
    name,
    plan,
    total_spent,
    last_order,
    open_critical_tickets,
    CASE
        WHEN open_critical_tickets > 0 THEN 'At Risk'
        WHEN last_order < CURRENT_DATE - interval '90 days' THEN 'Inactive'
        WHEN total_spent > 30000 THEN 'Healthy'
        WHEN total_spent > 10000 THEN 'Okay'
        ELSE 'New'
    END AS health_status
FROM metrics;
```

```sql
SELECT * FROM customer_health ORDER BY health_status, total_spent DESC;
```

One view. Multiple business rules. Hank can filter by health status without understanding the logic.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Expression                      │ What It Does
────────────────────────────────┼──────────────────────────────────────
CASE WHEN ... THEN ... END      │ Conditional value (if/else)
CASE col WHEN val THEN ... END  │ Equality-based conditional
FILTER (WHERE ...)              │ Conditional aggregate (PG-specific)
COALESCE(a, b, c)               │ First non-NULL value
NULLIF(a, b)                    │ NULL if a = b
GREATEST(a, b, c)               │ Largest value
LEAST(a, b, c)                  │ Smallest value
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Priya: "The board wants to see monthly cohort retention. How many customers from each signup month are still active 30, 60, 90 days later?"

That's date math. Intervals. Generating series of dates. Time to learn how PostgreSQL handles time.

---

[← Chapter 8: Views](chapter-08-views.md) | [Chapter 10: Dates & Times →](chapter-10-dates.md)

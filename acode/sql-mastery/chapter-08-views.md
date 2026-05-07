# Chapter 8: "Build Me a Reusable Report"

[← Chapter 7: Subqueries & CTEs](chapter-07-subqueries-ctes.md) | [Chapter 9: Conditional Logic →](chapter-09-case-expressions.md)

---

## The Request

Maya counts on her fingers. "Hank runs the revenue report every morning. Priya checks it hourly. The sales team runs it before every call. That's 50 executions a day. And every time someone copies the query, they tweak it slightly and get different numbers."

"One source of truth. One query. Everyone uses the same thing."

---

## Views: Saved Queries

A view is a named query. It doesn't store data — it stores the SQL. When you query the view, Postgres runs the underlying query.

```sql
CREATE VIEW monthly_revenue AS
SELECT
    date_trunc('month', order_date) AS month,
    count(*) AS order_count,
    sum(total_cents) / 100.0 AS revenue
FROM orders
WHERE status = 'completed'
GROUP BY date_trunc('month', order_date);
```

Now anyone can:

```sql
SELECT * FROM monthly_revenue ORDER BY month;
```

Same result every time. No copy-paste. No drift.

### Views Are Transparent

You can filter, join, and aggregate views like tables:

```sql
-- Only months with revenue > $200
SELECT * FROM monthly_revenue WHERE revenue > 200 ORDER BY month;

-- Join a view with another table
SELECT
    mr.month,
    mr.revenue,
    count(t.id) AS tickets_that_month
FROM monthly_revenue mr
LEFT JOIN tickets t ON date_trunc('month', t.created_at) = mr.month
GROUP BY mr.month, mr.revenue
ORDER BY mr.month;
```

### Updating and Dropping Views

```sql
-- Replace the definition (must return same columns or superset)
CREATE OR REPLACE VIEW monthly_revenue AS
SELECT
    date_trunc('month', order_date) AS month,
    count(*) AS order_count,
    sum(total_cents) / 100.0 AS revenue,
    count(DISTINCT customer_id) AS unique_customers  -- added column
FROM orders
WHERE status = 'completed'
GROUP BY date_trunc('month', order_date);

-- Remove a view
DROP VIEW monthly_revenue;

-- Remove only if it exists (no error if missing)
DROP VIEW IF EXISTS monthly_revenue;
```

---

## Building a View Library

Maya wants a set of standard views everyone uses:

```sql
-- Customer lifetime value
CREATE VIEW customer_ltv AS
SELECT
    c.id AS customer_id,
    c.name,
    c.plan,
    c.signed_up,
    count(o.id) AS total_orders,
    COALESCE(sum(o.total_cents), 0) / 100.0 AS lifetime_value,
    max(o.order_date) AS last_order_date
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id AND o.status = 'completed'
GROUP BY c.id, c.name, c.plan, c.signed_up;

-- Active MRR by customer
CREATE VIEW customer_mrr AS
SELECT
    c.id AS customer_id,
    c.name,
    c.plan,
    COALESCE(sum(m.amount_cents), 0) / 100.0 AS current_mrr
FROM customers c
LEFT JOIN mrr_events m ON m.customer_id = c.id
GROUP BY c.id, c.name, c.plan;

-- Open tickets summary
CREATE VIEW open_tickets_summary AS
SELECT
    c.name AS customer_name,
    c.plan,
    t.subject,
    t.priority,
    t.created_at,
    now() - t.created_at AS age
FROM tickets t
JOIN customers c ON c.id = t.customer_id
WHERE t.status IN ('open', 'in_progress')
ORDER BY
    CASE t.priority
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
    END,
    t.created_at;
```

Now Hank types `SELECT * FROM customer_ltv ORDER BY lifetime_value DESC` and gets his report. No SQL knowledge needed beyond SELECT.

---

## Materialized Views: Precomputed Results

The `customer_ltv` view joins three tables and aggregates thousands of rows. It takes 2 seconds. Hank runs it 10 times a day. That's 20 seconds of database time for the same result.

A materialized view stores the result physically. Like a cached snapshot.

```sql
CREATE MATERIALIZED VIEW mv_customer_ltv AS
SELECT
    c.id AS customer_id,
    c.name,
    c.plan,
    c.signed_up,
    count(o.id) AS total_orders,
    COALESCE(sum(o.total_cents), 0) / 100.0 AS lifetime_value,
    max(o.order_date) AS last_order_date
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id AND o.status = 'completed'
GROUP BY c.id, c.name, c.plan, c.signed_up;
```

Query it like a table — instant results:

```sql
SELECT * FROM mv_customer_ltv ORDER BY lifetime_value DESC;
-- Returns in <10ms instead of 2 seconds
```

### The Catch: Stale Data

Materialized views don't auto-update. The data is frozen at creation time. You must refresh manually:

```sql
-- Blocks reads during refresh
REFRESH MATERIALIZED VIEW mv_customer_ltv;

-- Non-blocking refresh (requires a UNIQUE index)
CREATE UNIQUE INDEX ON mv_customer_ltv (customer_id);
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_customer_ltv;
```

`CONCURRENTLY` lets people query the old data while the refresh runs. Without it, queries block until the refresh completes.

### When to Refresh

| Strategy | How | Use When |
|---|---|---|
| Manual | `REFRESH MATERIALIZED VIEW ...` | After known data loads |
| Scheduled | Cron job / pg_cron | Every hour, every night |
| On-demand | Application triggers refresh | After bulk imports |

```sql
-- Using pg_cron (if installed):
SELECT cron.schedule('refresh-ltv', '0 * * * *',
    'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_customer_ltv');
```

---

## Views vs Materialized Views

| Feature | View | Materialized View |
|---|---|---|
| Stores data? | No (just the query) | Yes (physical copy) |
| Always fresh? | Yes | No (must refresh) |
| Speed | Same as running the query | Fast (precomputed) |
| Indexes? | No | Yes |
| Use when | Query is fast, data must be current | Query is slow, slight staleness OK |

---

## Derek's Mystery View

Remember `v_dont_touch_ask_derek`? Time to look at it:

```sql
-- See the definition of any view
SELECT pg_get_viewdef('v_dont_touch_ask_derek', true);
```

Or in psql:

```
\d+ v_dont_touch_ask_derek
```

It turns out Derek's view calculates a complex revenue attribution model that three dashboards depend on. Now you understand it, you can rewrite it properly with CTEs and document it.

```sql
-- Derek's view, rewritten and documented
CREATE OR REPLACE VIEW revenue_attribution AS
-- Attributes revenue to the month it was earned, not invoiced.
-- Used by: CEO dashboard, sales forecast, board report.
WITH completed_orders AS (
    SELECT
        customer_id,
        order_date,
        total_cents
    FROM orders
    WHERE status = 'completed'
),
monthly_attribution AS (
    SELECT
        date_trunc('month', order_date) AS month,
        customer_id,
        sum(total_cents) / 100.0 AS revenue
    FROM completed_orders
    GROUP BY date_trunc('month', order_date), customer_id
)
SELECT
    month,
    customer_id,
    revenue,
    sum(revenue) OVER (PARTITION BY customer_id ORDER BY month) AS cumulative_revenue
FROM monthly_attribution;
```

You can now safely drop Derek's view:

```sql
DROP VIEW v_dont_touch_ask_derek;
```

---

## Dependent Views

Views can reference other views. But be careful — dropping a base view breaks dependent views:

```sql
-- This fails if other views depend on monthly_revenue
DROP VIEW monthly_revenue;
-- ERROR: cannot drop view monthly_revenue because other objects depend on it

-- Force drop with all dependents
DROP VIEW monthly_revenue CASCADE;
-- WARNING: drop cascades to view quarterly_summary
```

Check dependencies before dropping:

```sql
SELECT
    dependent.relname AS dependent_view
FROM pg_depend d
JOIN pg_rewrite r ON r.oid = d.objid
JOIN pg_class dependent ON dependent.oid = r.ev_class
JOIN pg_class source ON source.oid = d.refobjid
WHERE source.relname = 'monthly_revenue'
  AND dependent.relname != 'monthly_revenue';
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Command                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
CREATE VIEW name AS SELECT ...  │ Save a query as a virtual table
CREATE OR REPLACE VIEW ...      │ Update view definition
DROP VIEW name                  │ Remove a view
DROP VIEW name CASCADE          │ Remove view + all dependents
\d+ view_name                   │ Show view definition (psql)
────────────────────────────────┼──────────────────────────────────────
CREATE MATERIALIZED VIEW ...    │ Save query results physically
REFRESH MATERIALIZED VIEW name  │ Recompute the cached results
REFRESH ... CONCURRENTLY        │ Non-blocking refresh (needs index)
CREATE UNIQUE INDEX ON mv(col)  │ Required for CONCURRENTLY
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Hank: "The report needs a column that says 'High Value' if they spent over $300, 'Medium' if over $100, and 'Low' otherwise. Also, count how many customers are in each bucket."

Conditional logic. CASE expressions.

---

[← Chapter 7: Subqueries & CTEs](chapter-07-subqueries-ctes.md) | [Chapter 9: Conditional Logic →](chapter-09-case-expressions.md)

# Chapter 7: "This Query Is Unreadable"

[← Chapter 6: Window Functions](chapter-06-window-functions.md) | [Chapter 8: Views →](chapter-08-views.md)

---

## The Incident

Maya reviews your board report query. It's 47 lines of nested subqueries, repeated expressions, and inline calculations. She stares at it for 30 seconds.

"I can't tell what this does. If I can't read it, I can't debug it. Break it into pieces."

She's right. SQL doesn't have to be one giant blob. You can name intermediate steps, build queries from smaller queries, and make the logic readable.

---

## Subqueries: A Query Inside a Query

### Subquery in WHERE

"Find customers who spent more than the average order value."

```sql
SELECT name, email
FROM customers
WHERE id IN (
    SELECT customer_id
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
    HAVING sum(total_cents) > (SELECT avg(total_cents) FROM orders WHERE status = 'completed')
);
```

The inner query runs first, produces a list of customer IDs, and the outer query filters by that list.

### Subquery in FROM (Derived Table)

```sql
SELECT
    plan,
    round(avg(total_spent), 2) AS avg_spend_per_customer
FROM (
    SELECT
        c.plan,
        sum(o.total_cents) / 100.0 AS total_spent
    FROM customers c
    JOIN orders o ON o.customer_id = c.id
    WHERE o.status = 'completed'
    GROUP BY c.id, c.plan
) customer_totals
GROUP BY plan
ORDER BY avg_spend_per_customer DESC;
```

```
    plan    | avg_spend_per_customer
------------+------------------------
 enterprise |                 378.40
 pro        |                 112.00
 starter    |                  29.00
 free       |                  29.00
```

The inner query calculates per-customer totals. The outer query averages those totals per plan. You can't do this in one level because you'd be aggregating an aggregate.

### Subquery in SELECT (Scalar Subquery)

```sql
SELECT
    name,
    plan,
    (SELECT count(*) FROM orders WHERE customer_id = c.id) AS order_count
FROM customers c
ORDER BY order_count DESC;
```

A scalar subquery returns exactly one value. It runs once per row in the outer query — which can be slow on large tables. Prefer JOINs for performance.

---

## Correlated Subqueries

A correlated subquery references the outer query. It runs once per outer row.

"Find each customer's most recent order:"

```sql
SELECT c.name, o.order_date, o.total_cents / 100.0 AS total
FROM customers c
JOIN orders o ON o.customer_id = c.id
WHERE o.order_date = (
    SELECT max(order_date)
    FROM orders
    WHERE customer_id = c.id
);
```

The inner query uses `c.id` from the outer query — that's the correlation. For each customer, it finds their latest order date.

### EXISTS: Does a Match Exist?

"Find customers who have at least one critical ticket."

```sql
SELECT name, email
FROM customers c
WHERE EXISTS (
    SELECT 1
    FROM tickets t
    WHERE t.customer_id = c.id
      AND t.priority = 'critical'
);
```

`EXISTS` returns true/false — it doesn't care what the subquery returns, just whether it returns anything. Often faster than `IN` for large datasets because it stops at the first match.

### NOT EXISTS: Anti-Pattern

"Customers who have never placed an order."

```sql
SELECT name, email, plan
FROM customers c
WHERE NOT EXISTS (
    SELECT 1 FROM orders WHERE customer_id = c.id
);
```

Equivalent to the `LEFT JOIN ... WHERE id IS NULL` pattern from Chapter 3. Use whichever reads better.

---

## CTEs: Named Building Blocks

A Common Table Expression (CTE) is a named temporary result set. Think of it as a variable for queries.

```sql
WITH customer_revenue AS (
    SELECT
        c.id,
        c.name,
        c.plan,
        sum(o.total_cents) / 100.0 AS total_spent
    FROM customers c
    JOIN orders o ON o.customer_id = c.id
    WHERE o.status = 'completed'
    GROUP BY c.id, c.name, c.plan
)
SELECT
    name,
    plan,
    total_spent,
    rank() OVER (ORDER BY total_spent DESC) AS revenue_rank
FROM customer_revenue
ORDER BY revenue_rank;
```

### Multiple CTEs

Chain them. Each CTE can reference the ones before it:

```sql
WITH monthly_revenue AS (
    SELECT
        date_trunc('month', order_date) AS month,
        sum(total_cents) / 100.0 AS revenue
    FROM orders
    WHERE status = 'completed'
    GROUP BY date_trunc('month', order_date)
),
with_growth AS (
    SELECT
        month,
        revenue,
        lag(revenue) OVER (ORDER BY month) AS prev_revenue
    FROM monthly_revenue
),
final AS (
    SELECT
        to_char(month, 'Mon YYYY') AS period,
        revenue,
        prev_revenue,
        CASE
            WHEN prev_revenue IS NULL THEN NULL
            ELSE round((revenue - prev_revenue) / prev_revenue * 100, 1)
        END AS growth_pct
    FROM with_growth
)
SELECT * FROM final ORDER BY month;
```

Each CTE is a named step. Read top to bottom. Debug one step at a time by changing the final `SELECT * FROM final` to `SELECT * FROM monthly_revenue` or `SELECT * FROM with_growth`.

### Maya's Rewrite of Your Board Report

Before (unreadable):

```sql
SELECT to_char(m, 'Mon YYYY'), r, sum(r) OVER (ORDER BY m),
CASE WHEN lag(r) OVER (ORDER BY m) IS NULL THEN NULL
ELSE round((r - lag(r) OVER (ORDER BY m)) / lag(r) OVER (ORDER BY m) * 100, 1) END
FROM (SELECT date_trunc('month', order_date) m, sum(total_cents)/100.0 r
FROM orders WHERE status='completed' GROUP BY 1) x ORDER BY m;
```

After (readable):

```sql
WITH monthly AS (
    SELECT
        date_trunc('month', order_date) AS month,
        sum(total_cents) / 100.0 AS revenue
    FROM orders
    WHERE status = 'completed'
    GROUP BY date_trunc('month', order_date)
),
enriched AS (
    SELECT
        month,
        revenue,
        sum(revenue) OVER (ORDER BY month) AS cumulative,
        lag(revenue) OVER (ORDER BY month) AS prev_month
    FROM monthly
)
SELECT
    to_char(month, 'Mon YYYY') AS period,
    revenue,
    cumulative,
    CASE
        WHEN prev_month IS NULL THEN NULL
        ELSE round((revenue - prev_month) / prev_month * 100, 1)
    END AS growth_pct
FROM enriched
ORDER BY month;
```

Same result. Readable. Debuggable. Maintainable.

---

## WITH RECURSIVE: Hierarchical Data

Silent Sasha sends you a Slack message (rare). It's a screenshot of a table:

```
employees
┌────┬──────────┬────────────┐
│ id │ name     │ manager_id │
├────┼──────────┼────────────┤
│  1 │ Priya    │ NULL       │
│  2 │ Maya     │ 1          │
│  3 │ Hank     │ 1          │
│  4 │ You      │ 2          │
│  5 │ Sasha    │ 2          │
│  6 │ Intern   │ 4          │
└────┴──────────┴────────────┘
```

"Build the org chart. Show each person's level and full reporting chain."

This is a tree structure. You need recursion.

```sql
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    manager_id INTEGER REFERENCES employees(id)
);

INSERT INTO employees (name, manager_id) VALUES
('Priya', NULL), ('Maya', 1), ('Hank', 1),
('You', 2), ('Sasha', 2), ('Intern', 4);
```

```sql
WITH RECURSIVE org_chart AS (
    -- Base case: the CEO (no manager)
    SELECT id, name, manager_id, 0 AS level, name AS chain
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive case: find direct reports
    SELECT e.id, e.name, e.manager_id, oc.level + 1,
           oc.chain || ' → ' || e.name
    FROM employees e
    JOIN org_chart oc ON e.manager_id = oc.id
)
SELECT level, name, chain
FROM org_chart
ORDER BY chain;
```

```
 level |  name  |          chain
-------+--------+---------------------------
     0 | Priya  | Priya
     1 | Hank   | Priya → Hank
     1 | Maya   | Priya → Maya
     2 | Sasha  | Priya → Maya → Sasha
     2 | You    | Priya → Maya → You
     3 | Intern | Priya → Maya → You → Intern
```

### How Recursive CTEs Work

```
1. Run the base case (anchor) → produces initial rows
2. Run the recursive part, joining against previous results
3. Repeat step 2 until no new rows are produced
4. Combine all results with UNION ALL
```

⚠️ Always have a termination condition. If your data has cycles (A reports to B, B reports to A), the recursion runs forever. Add `WHERE level < 10` as a safety limit.

### Practical: Category Trees

```sql
-- Product categories with parent-child relationships
WITH RECURSIVE category_tree AS (
    SELECT id, name, parent_id, 0 AS depth,
           ARRAY[name] AS path
    FROM categories
    WHERE parent_id IS NULL

    UNION ALL

    SELECT c.id, c.name, c.parent_id, ct.depth + 1,
           ct.path || c.name
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT
    repeat('  ', depth) || name AS category,
    array_to_string(path, ' > ') AS full_path
FROM category_tree
ORDER BY path;
```

---

## When to Use What

| Tool | Use When |
|---|---|
| Subquery in WHERE | Filtering by a computed list |
| Subquery in FROM | Need to aggregate an aggregate |
| Scalar subquery | Need one value per row (prefer JOIN) |
| EXISTS / NOT EXISTS | Checking existence (faster than IN for large sets) |
| CTE | Breaking complex queries into readable steps |
| WITH RECURSIVE | Hierarchical/tree data, graph traversal |

### Performance Note

In PostgreSQL 12+, CTEs are inlined by default (optimized like subqueries). If you need to force materialization (compute once, reuse many times):

```sql
WITH expensive_calc AS MATERIALIZED (
    SELECT ... -- computed once, even if referenced multiple times
)
SELECT ... FROM expensive_calc;
```

---

## Quick Reference

```
────────────────────────┬──────────────────────────────────────────────
Pattern                 │ Syntax
────────────────────────┼──────────────────────────────────────────────
Subquery in WHERE       │ WHERE col IN (SELECT ...)
Subquery in FROM        │ FROM (SELECT ...) alias
Scalar subquery         │ SELECT (SELECT ... ) AS col
EXISTS                  │ WHERE EXISTS (SELECT 1 FROM ... WHERE ...)
CTE                     │ WITH name AS (SELECT ...) SELECT ... FROM name
Multiple CTEs           │ WITH a AS (...), b AS (...) SELECT ...
Recursive CTE           │ WITH RECURSIVE name AS (base UNION ALL recursive)
────────────────────────┴──────────────────────────────────────────────
```

---

## What's Next

Maya: "This monthly revenue query — Hank runs it every morning. Priya runs it every hour. The sales team runs it before every call. That's 50 executions a day of the same query. Can we just... save it?"

Views.

---

[← Chapter 6: Window Functions](chapter-06-window-functions.md) | [Chapter 8: Views →](chapter-08-views.md)

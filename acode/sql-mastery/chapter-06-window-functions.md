# Chapter 6: "I Need a Running Total"

[← Chapter 5: Data Integrity](chapter-05-constraints.md) | [Chapter 7: Subqueries & CTEs →](chapter-07-subqueries-ctes.md)

---

## The Request

Hank slides into your DMs at 4:47 PM on a Thursday.

"I need a report for the board. For each month, show: revenue that month, running total, and rank each customer by total spend. Also month-over-month growth percentage. By tomorrow morning."

You try GROUP BY. It collapses rows — you lose the individual detail. You need to aggregate WITHOUT collapsing. You need to compute values across rows while keeping every row visible.

You need window functions.

---

## The Concept: Aggregate Without Collapsing

`GROUP BY` squishes rows into groups. You get one row per group. Window functions compute across rows but keep every row intact.

```
GROUP BY:                          Window Function:
┌─────────┬─────────┐             ┌─────────┬─────────┬─────────────┐
│  month  │ revenue │             │  month  │ revenue │ running_total│
├─────────┼─────────┤             ├─────────┼─────────┼─────────────┤
│ Jan     │  299    │             │ Jan     │  299    │     299     │
│ Feb     │   99    │             │ Feb     │   99    │     398     │
│ Mar     │  167    │             │ Mar     │  167    │     565     │
└─────────┴─────────┘             │ Apr     │  477    │    1042     │
  3 rows (collapsed)              └─────────┴─────────┴─────────────┘
                                    4 rows (all preserved)
```

---

## SUM() OVER: Running Total

```sql
SELECT
    date_trunc('month', order_date) AS month,
    sum(total_cents) / 100.0 AS monthly_revenue,
    sum(sum(total_cents)) OVER (ORDER BY date_trunc('month', order_date))
        / 100.0 AS running_total
FROM orders
WHERE status = 'completed'
GROUP BY date_trunc('month', order_date)
ORDER BY month;
```

```
        month        | monthly_revenue | running_total
---------------------+-----------------+---------------
 2024-01-01 00:00:00 |          299.00 |        299.00
 2024-02-01 00:00:00 |           99.00 |        398.00
 2024-03-01 00:00:00 |          167.00 |        565.00
 2024-04-01 00:00:00 |          477.00 |       1042.00
 2024-05-01 00:00:00 |          398.00 |       1440.00
 ...
```

### Breaking It Down

```sql
sum(sum(total_cents)) OVER (ORDER BY date_trunc('month', order_date))
│    │                  │         │
│    │                  │         └─ "in this order" (chronological)
│    │                  └─ "across the window of rows"
│    └─ inner sum: the GROUP BY aggregate (monthly total)
└─ outer sum: the window function (running sum of monthly totals)
```

`OVER(...)` is what makes it a window function. Without `OVER`, it's just a regular aggregate.

---

## ROW_NUMBER: Ranking

"Rank customers by total spend."

```sql
SELECT
    row_number() OVER (ORDER BY total_spent DESC) AS rank,
    name,
    total_spent
FROM (
    SELECT
        c.name,
        sum(o.total_cents) / 100.0 AS total_spent
    FROM customers c
    JOIN orders o ON o.customer_id = c.id
    WHERE o.status = 'completed'
    GROUP BY c.id, c.name
) customer_revenue;
```

```
 rank |      name       | total_spent
------+-----------------+-------------
    1 | MegaRetail      |      448.00
    2 | RocketShip      |      448.00
    3 | DataHouse       |      348.00
    4 | Acme Corp       |      348.00
    5 | GigaCorp        |      299.00
    ...
```

### ROW_NUMBER vs RANK vs DENSE_RANK

MegaRetail and RocketShip are tied at $448. How should ties be handled?

```sql
SELECT
    name,
    total_spent,
    row_number() OVER (ORDER BY total_spent DESC) AS row_num,
    rank()       OVER (ORDER BY total_spent DESC) AS rank,
    dense_rank() OVER (ORDER BY total_spent DESC) AS dense_rank
FROM customer_revenue;
```

```
     name     | total_spent | row_num | rank | dense_rank
--------------+-------------+---------+------+------------
 MegaRetail   |      448.00 |       1 |    1 |          1
 RocketShip   |      448.00 |       2 |    1 |          1
 DataHouse    |      348.00 |       3 |    3 |          2
 Acme Corp    |      348.00 |       4 |    3 |          2
 GigaCorp     |      299.00 |       5 |    5 |          3
```

| Function | Ties | Gaps |
|---|---|---|
| `ROW_NUMBER` | Arbitrary (1, 2, 3...) | Never |
| `RANK` | Same rank for ties | Gaps after ties (1, 1, 3) |
| `DENSE_RANK` | Same rank for ties | No gaps (1, 1, 2) |

---

## PARTITION BY: Windows Within Groups

"Rank customers within each plan tier."

```sql
SELECT
    plan,
    name,
    total_spent,
    rank() OVER (PARTITION BY plan ORDER BY total_spent DESC) AS rank_in_plan
FROM (
    SELECT c.plan, c.name, sum(o.total_cents) / 100.0 AS total_spent
    FROM customers c
    JOIN orders o ON o.customer_id = c.id
    WHERE o.status = 'completed'
    GROUP BY c.id, c.plan, c.name
) x;
```

```
    plan    |      name       | total_spent | rank_in_plan
------------+-----------------+-------------+--------------
 enterprise | MegaRetail      |      448.00 |            1
 enterprise | RocketShip      |      448.00 |            1
 enterprise | DataHouse       |      348.00 |            3
 enterprise | Acme Corp       |      348.00 |            3
 enterprise | GigaCorp        |      299.00 |            5
 pro        | CloudNine       |       99.00 |            1
 pro        | Berlin Analytics|      138.00 |            1
 starter    | Quick Books Ltd |       29.00 |            1
 ...
```

`PARTITION BY plan` creates separate windows for each plan. The ranking restarts within each partition.

Think of it as: `GROUP BY` collapses into one row per group. `PARTITION BY` keeps all rows but computes separately per group.

---

## LAG and LEAD: Previous and Next Row

"Month-over-month revenue growth."

```sql
SELECT
    month,
    revenue,
    lag(revenue) OVER (ORDER BY month) AS prev_month,
    round(
        (revenue - lag(revenue) OVER (ORDER BY month))
        / lag(revenue) OVER (ORDER BY month) * 100, 1
    ) AS growth_pct
FROM (
    SELECT
        date_trunc('month', order_date) AS month,
        sum(total_cents) / 100.0 AS revenue
    FROM orders
    WHERE status = 'completed'
    GROUP BY date_trunc('month', order_date)
) monthly;
```

```
        month        | revenue | prev_month | growth_pct
---------------------+---------+------------+------------
 2024-01-01 00:00:00 |  299.00 |       NULL |       NULL
 2024-02-01 00:00:00 |   99.00 |     299.00 |      -66.9
 2024-03-01 00:00:00 |  167.00 |      99.00 |       68.7
 2024-04-01 00:00:00 |  477.00 |     167.00 |      185.6
 ...
```

| Function | Returns |
|---|---|
| `LAG(col, n)` | Value from n rows BEFORE current (default n=1) |
| `LEAD(col, n)` | Value from n rows AFTER current |
| `LAG(col, 1, 0)` | Third arg = default if no previous row |

First row has no previous month → NULL. That's correct.

---

## FIRST_VALUE, LAST_VALUE, NTH_VALUE

"What was each customer's first purchase?"

```sql
SELECT DISTINCT
    c.name,
    first_value(p.name) OVER (
        PARTITION BY c.id
        ORDER BY o.order_date
    ) AS first_product_purchased
FROM customers c
JOIN orders o ON o.customer_id = c.id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id
WHERE o.status = 'completed';
```

---

## Frame Clauses: Controlling the Window

By default, `SUM() OVER (ORDER BY ...)` sums from the first row to the current row. You can change this:

```sql
-- 3-month moving average
SELECT
    month,
    revenue,
    round(avg(revenue) OVER (
        ORDER BY month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) AS moving_avg_3m
FROM monthly_revenue;
```

### Frame Options

```
ROWS BETWEEN ... AND ...

Options:
  UNBOUNDED PRECEDING  → from the very first row
  n PRECEDING          → n rows before current
  CURRENT ROW          → this row
  n FOLLOWING          → n rows after current
  UNBOUNDED FOLLOWING  → to the very last row
```

```sql
-- Running total (default): UNBOUNDED PRECEDING to CURRENT ROW
-- Moving average (3 months): 2 PRECEDING to CURRENT ROW
-- Centered average: 1 PRECEDING to 1 FOLLOWING
-- Total of entire partition: UNBOUNDED PRECEDING to UNBOUNDED FOLLOWING
```

---

## Practical: Hank's Board Report

Putting it all together:

```sql
WITH monthly AS (
    SELECT
        date_trunc('month', order_date) AS month,
        sum(total_cents) / 100.0 AS revenue,
        count(*) AS orders
    FROM orders
    WHERE status = 'completed'
    GROUP BY date_trunc('month', order_date)
)
SELECT
    to_char(month, 'Mon YYYY') AS period,
    revenue,
    sum(revenue) OVER (ORDER BY month) AS cumulative_revenue,
    lag(revenue) OVER (ORDER BY month) AS prev_month,
    CASE
        WHEN lag(revenue) OVER (ORDER BY month) IS NULL THEN NULL
        ELSE round((revenue - lag(revenue) OVER (ORDER BY month))
             / lag(revenue) OVER (ORDER BY month) * 100, 1)
    END AS growth_pct,
    orders,
    round(avg(revenue) OVER (
        ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) AS moving_avg_3m
FROM monthly
ORDER BY month;
```

Revenue per month, cumulative total, month-over-month growth, order count, and 3-month moving average. One query. Hank's board slide is done.

---

## Quick Reference

```
────────────────────────┬──────────────────────────────────────────────
Function                │ What It Does
────────────────────────┼──────────────────────────────────────────────
ROW_NUMBER() OVER(...)  │ Sequential number (no ties)
RANK() OVER(...)        │ Rank with gaps on ties
DENSE_RANK() OVER(...)  │ Rank without gaps on ties
SUM() OVER(...)         │ Running/cumulative sum
AVG() OVER(...)         │ Moving/running average
LAG(col, n) OVER(...)   │ Value from n rows before
LEAD(col, n) OVER(...)  │ Value from n rows after
FIRST_VALUE(col) OVER() │ First value in the window
NTILE(n) OVER(...)      │ Divide into n equal buckets
────────────────────────┼──────────────────────────────────────────────
PARTITION BY            │ Separate windows per group
ORDER BY (in OVER)      │ Row ordering within window
ROWS BETWEEN ... AND ...│ Frame: which rows to include
────────────────────────┴──────────────────────────────────────────────
```

---

## What's Next

That board report query is getting long. Nested subqueries, repeated window definitions, hard to read. Maya looks at it and says:

"Break this into pieces. Use CTEs. Make it readable."

---

[← Chapter 5: Data Integrity](chapter-05-constraints.md) | [Chapter 7: Subqueries & CTEs →](chapter-07-subqueries-ctes.md)

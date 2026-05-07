# Chapter 10: "Work With Dates Properly"

[← Chapter 9: Conditional Logic](chapter-09-case-expressions.md) | [Chapter 11: Performance →](chapter-11-performance.md)

---

## The Request

Priya's board presentation needs cohort analysis. "For each signup month, how many customers placed an order within 30 days? 60 days? 90 days?"

You also need to fill in months with zero revenue (the dashboard shows gaps). And calculate time-to-resolution for support tickets.

All of this requires understanding how PostgreSQL handles dates and times.

---

## Date/Time Types

| Type | Stores | Example |
|---|---|---|
| `DATE` | Calendar date only | `2024-09-15` |
| `TIME` | Time of day only | `14:30:00` |
| `TIMESTAMP` | Date + time (no timezone) | `2024-09-15 14:30:00` |
| `TIMESTAMPTZ` | Date + time + timezone | `2024-09-15 14:30:00+00` |
| `INTERVAL` | Duration | `3 days 2 hours` |

**Rule**: Always use `TIMESTAMPTZ` for timestamps. `TIMESTAMP` without timezone is ambiguous — "2024-09-15 14:30:00" in which timezone? Postgres stores `TIMESTAMPTZ` in UTC and converts on display.

---

## Current Date/Time

```sql
SELECT
    CURRENT_DATE,                    -- 2024-09-16 (date only)
    CURRENT_TIMESTAMP,               -- 2024-09-16 14:30:00+00 (with tz)
    now(),                           -- same as CURRENT_TIMESTAMP
    CURRENT_DATE - interval '7 days' -- 7 days ago
;
```

---

## Interval Arithmetic

```sql
-- Add/subtract intervals
SELECT
    CURRENT_DATE + interval '30 days' AS thirty_days_from_now,
    CURRENT_DATE - interval '1 month' AS last_month,
    now() - interval '2 hours' AS two_hours_ago;

-- Difference between two dates = integer (days)
SELECT '2024-09-15'::date - '2024-09-01'::date AS days_between;
-- → 14

-- Difference between two timestamps = interval
SELECT '2024-09-15 14:00:00'::timestamp - '2024-09-15 09:30:00'::timestamp;
-- → 04:30:00
```

---

## date_trunc: Rounding Down

Truncates a timestamp to a specified precision:

```sql
SELECT
    date_trunc('month', TIMESTAMP '2024-09-15 14:30:00'),  -- 2024-09-01 00:00:00
    date_trunc('week', TIMESTAMP '2024-09-15 14:30:00'),   -- 2024-09-09 00:00:00 (Monday)
    date_trunc('year', TIMESTAMP '2024-09-15 14:30:00'),   -- 2024-01-01 00:00:00
    date_trunc('hour', TIMESTAMP '2024-09-15 14:30:00');   -- 2024-09-15 14:00:00
```

Essential for grouping by time periods:

```sql
SELECT
    date_trunc('week', order_date) AS week,
    count(*) AS orders
FROM orders
GROUP BY date_trunc('week', order_date)
ORDER BY week;
```

---

## EXTRACT: Pulling Parts Out

```sql
SELECT
    extract(year FROM TIMESTAMP '2024-09-15 14:30:00'),    -- 2024
    extract(month FROM TIMESTAMP '2024-09-15 14:30:00'),   -- 9
    extract(dow FROM TIMESTAMP '2024-09-15 14:30:00'),     -- 0 (Sunday)
    extract(epoch FROM TIMESTAMP '2024-09-15 14:30:00'),   -- Unix timestamp
    extract(hour FROM interval '3 hours 45 minutes');      -- 3
```

| Field | Returns |
|---|---|
| `year` | Year |
| `month` | Month (1-12) |
| `day` | Day of month (1-31) |
| `dow` | Day of week (0=Sunday, 6=Saturday) |
| `hour`, `minute`, `second` | Time components |
| `epoch` | Seconds since 1970-01-01 |

---

## to_char: Formatting for Display

```sql
SELECT
    to_char(CURRENT_DATE, 'Mon YYYY'),           -- 'Sep 2024'
    to_char(CURRENT_DATE, 'YYYY-MM-DD'),         -- '2024-09-16'
    to_char(CURRENT_DATE, 'Day, DD Month YYYY'), -- 'Monday   , 16 September 2024'
    to_char(12345.6, '$99,999.99');              -- ' $12,345.60'
```

Use `to_char` for display only. Keep dates as proper types for calculations.

---

## generate_series: Filling Gaps

The revenue chart has gaps — months with no orders show nothing instead of zero. You need a continuous series of months.

```sql
SELECT generate_series(
    '2024-01-01'::date,
    '2024-09-01'::date,
    '1 month'::interval
) AS month;
```

```
        month
---------------------
 2024-01-01 00:00:00
 2024-02-01 00:00:00
 2024-03-01 00:00:00
 ...
 2024-09-01 00:00:00
```

### Fill Gaps in Revenue Report

```sql
WITH months AS (
    SELECT generate_series(
        '2024-01-01'::date,
        '2024-09-01'::date,
        '1 month'::interval
    )::date AS month
),
revenue AS (
    SELECT
        date_trunc('month', order_date)::date AS month,
        sum(total_cents) / 100.0 AS revenue
    FROM orders
    WHERE status = 'completed'
    GROUP BY date_trunc('month', order_date)
)
SELECT
    to_char(m.month, 'Mon YYYY') AS period,
    COALESCE(r.revenue, 0) AS revenue
FROM months m
LEFT JOIN revenue r ON r.month = m.month
ORDER BY m.month;
```

Every month appears, even if revenue is zero. The `LEFT JOIN` + `COALESCE` pattern fills the gaps.

---

## Practical: Ticket Resolution Time

"How long does it take to resolve tickets, by priority?"

```sql
SELECT
    priority,
    count(*) AS total,
    count(resolved_at) AS resolved,
    round(
        avg(extract(epoch FROM (resolved_at - created_at)) / 3600)
        FILTER (WHERE resolved_at IS NOT NULL), 1
    ) AS avg_hours,
    round(
        max(extract(epoch FROM (resolved_at - created_at)) / 3600)
        FILTER (WHERE resolved_at IS NOT NULL), 1
    ) AS max_hours
FROM tickets
GROUP BY priority
ORDER BY
    CASE priority
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
    END;
```

```
 priority | total | resolved | avg_hours | max_hours
----------+-------+----------+-----------+-----------
 critical |     1 |        1 |       1.3 |       1.3
 high     |     3 |        2 |       5.0 |       6.0
 medium   |     3 |        2 |      12.5 |      19.0
 low      |     2 |        0 |           |
```

Critical tickets: resolved in 1.3 hours average. Low tickets: none resolved yet. Priya will want to talk about that.

---

## Practical: Cohort Retention

Priya's board request. "For each signup month, what percentage placed an order within 30/60/90 days?"

```sql
WITH cohorts AS (
    SELECT
        id AS customer_id,
        date_trunc('month', signed_up) AS cohort_month
    FROM customers
),
activity AS (
    SELECT DISTINCT
        customer_id,
        date_trunc('month', order_date) AS active_month
    FROM orders
    WHERE status = 'completed'
)
SELECT
    to_char(c.cohort_month, 'Mon YYYY') AS cohort,
    count(DISTINCT c.customer_id) AS cohort_size,
    count(DISTINCT CASE
        WHEN a.active_month <= c.cohort_month + interval '30 days'
        THEN c.customer_id
    END) AS active_30d,
    count(DISTINCT CASE
        WHEN a.active_month <= c.cohort_month + interval '60 days'
        THEN c.customer_id
    END) AS active_60d,
    count(DISTINCT CASE
        WHEN a.active_month <= c.cohort_month + interval '90 days'
        THEN c.customer_id
    END) AS active_90d
FROM cohorts c
LEFT JOIN activity a ON a.customer_id = c.customer_id
GROUP BY c.cohort_month
ORDER BY c.cohort_month;
```

```
  cohort   | cohort_size | active_30d | active_60d | active_90d
-----------+-------------+------------+------------+------------
 Jan 2024  |           1 |          1 |          1 |          1
 Feb 2024  |           1 |          1 |          1 |          1
 Mar 2024  |           2 |          2 |          2 |          2
 Apr 2024  |           2 |          2 |          2 |          2
 ...
```

This is the kind of query that makes boards nod approvingly.

---

## Date Pitfalls

### Timezone Traps

```sql
-- ❌ Comparing TIMESTAMP with TIMESTAMPTZ silently converts
-- Results depend on server timezone setting
SELECT * FROM orders WHERE order_date = '2024-09-15';

-- ✅ Be explicit
SELECT * FROM orders
WHERE order_date >= '2024-09-15'::date
  AND order_date < '2024-09-16'::date;
```

### Month Arithmetic Surprises

```sql
-- What's one month after January 31?
SELECT '2024-01-31'::date + interval '1 month';
-- → 2024-02-29 (Postgres handles leap years)

SELECT '2024-03-31'::date + interval '1 month';
-- → 2024-04-30 (capped to last day of month)
```

### Inclusive vs Exclusive Ranges

```sql
-- ❌ BETWEEN includes both endpoints — midnight issues
SELECT * FROM orders WHERE order_date BETWEEN '2024-09-01' AND '2024-09-30';
-- Misses orders on 2024-09-30 after midnight if using timestamps

-- ✅ Half-open range
SELECT * FROM orders
WHERE order_date >= '2024-09-01'
  AND order_date < '2024-10-01';
```

---

## Useful Date Recipes

```sql
-- First day of current month
SELECT date_trunc('month', CURRENT_DATE);

-- Last day of current month
SELECT (date_trunc('month', CURRENT_DATE) + interval '1 month - 1 day')::date;

-- Start of current week (Monday)
SELECT date_trunc('week', CURRENT_DATE);

-- Age in years
SELECT extract(year FROM age(signed_up)) AS years_as_customer
FROM customers;

-- Business days between two dates (rough)
SELECT
    (DATE '2024-09-30' - DATE '2024-09-01') -
    2 * ((DATE '2024-09-30' - DATE '2024-09-01') / 7) AS approx_business_days;
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Function                        │ What It Does
────────────────────────────────┼──────────────────────────────────────
CURRENT_DATE                    │ Today's date
now() / CURRENT_TIMESTAMP       │ Current date+time+tz
date_trunc('unit', ts)          │ Round down to unit
extract(field FROM ts)          │ Pull out year/month/day/etc
to_char(ts, 'format')           │ Format for display
age(ts1, ts2)                   │ Interval between two timestamps
generate_series(start,end,step) │ Create a series of dates
interval '3 days'               │ Duration literal
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

You've built views, written complex queries, handled dates. Everything works. Then Monday morning, Hank runs his report and it takes 47 seconds. The dashboard times out. Silent Sasha sends you a single message:

```
EXPLAIN ANALYZE
```

Time to make it fast.

---

[← Chapter 9: Conditional Logic](chapter-09-case-expressions.md) | [Chapter 11: Performance →](chapter-11-performance.md)

# Chapter 11: "The Dashboard Is Slow"

[← Chapter 10: Dates & Times](chapter-10-dates.md) | [Chapter 12: Transactions →](chapter-12-transactions.md)

---

## The Incident

Monday morning. 9:01 AM. Priya's dashboard takes 47 seconds to load. Hank's report times out. The sales team can't pull customer data before their 9:30 calls.

Silent Sasha sends you one message:

```
EXPLAIN ANALYZE your queries. Then we talk.
```

---

## EXPLAIN: Reading the Query Plan

Every query has a plan — the steps Postgres takes to find your data. `EXPLAIN` shows the plan without running the query. `EXPLAIN ANALYZE` runs it and shows actual timing.

```sql
EXPLAIN ANALYZE
SELECT c.name, sum(o.total_cents) / 100.0 AS revenue
FROM customers c
JOIN orders o ON o.customer_id = c.id
WHERE o.status = 'completed'
GROUP BY c.id, c.name
ORDER BY revenue DESC;
```

```
 Sort  (cost=45.12..45.15 rows=13 width=40) (actual time=0.892..0.895 rows=13 loops=1)
   Sort Key: (sum(o.total_cents) / 100.0) DESC
   ->  HashAggregate  (cost=44.75..44.95 rows=13 width=40) (actual time=0.856..0.863 rows=13)
         ->  Hash Join  (cost=1.34..44.50 rows=19 width=22) (actual time=0.089..0.812 rows=19)
               Hash Cond: (o.customer_id = c.id)
               ->  Seq Scan on orders o  (cost=0.00..43.00 rows=19 width=8) (actual time=0.012..0.750 rows=19)
                     Filter: (status = 'completed')
                     Rows Removed by Filter: 3
               ->  Hash  (cost=1.15..1.15 rows=15 width=18) (actual time=0.030..0.031 rows=15)
                     ->  Seq Scan on customers c  (cost=0.00..1.15 rows=15 width=18) (actual time=0.005..0.008 rows=15)
 Planning Time: 0.250 ms
 Execution Time: 0.950 ms
```

### Reading the Plan

Read bottom-up. Each indented line is a step:

| Term | Meaning |
|---|---|
| `Seq Scan` | Full table scan — reads every row |
| `Index Scan` | Uses an index — fast lookup |
| `Hash Join` | Joins by building a hash table |
| `Nested Loop` | Joins by looping (good for small sets) |
| `Sort` | Sorts results |
| `cost=X..Y` | Estimated startup..total cost (arbitrary units) |
| `actual time=X..Y` | Real milliseconds |
| `rows=N` | Number of rows processed |
| `Rows Removed by Filter` | Rows read but discarded |

The key metric: **Execution Time**. Under 10ms is great. Over 1 second is a problem. 47 seconds is a fire.

---

## The Slow Query

You find it. The dashboard's main query:

```sql
EXPLAIN ANALYZE
SELECT
    c.name,
    c.plan,
    count(o.id) AS orders,
    sum(o.total_cents) / 100.0 AS revenue,
    max(o.order_date) AS last_order,
    (SELECT count(*) FROM tickets t WHERE t.customer_id = c.id) AS ticket_count
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
GROUP BY c.id, c.name, c.plan
ORDER BY revenue DESC NULLS LAST;
```

On 15 rows, it's fast. But in production with 50,000 customers and 2 million orders? The correlated subquery runs once per customer. That's 50,000 subqueries. Each one does a sequential scan on tickets.

---

## Indexes: The Fix

An index is like a book's index — instead of reading every page to find "PostgreSQL," you look up "P" in the index and jump to page 342.

### Creating Indexes

```sql
-- Index on foreign keys (should ALWAYS exist)
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_tickets_customer_id ON tickets(customer_id);

-- Index on frequently filtered columns
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_order_date ON orders(order_date);

-- Composite index (multiple columns)
CREATE INDEX idx_orders_customer_status ON orders(customer_id, status);
```

### Before and After

```sql
-- Before index: Seq Scan on orders (reads all 2M rows)
-- After index:  Index Scan using idx_orders_customer_id (reads 40 rows)
```

The query drops from 47 seconds to 200 milliseconds.

### Which Columns to Index

| Always Index | Why |
|---|---|
| Foreign keys | JOINs use them constantly |
| Columns in WHERE | Filters need fast lookup |
| Columns in ORDER BY | Avoids sorting |
| Columns in GROUP BY | Can enable index-only scans |

| Don't Index | Why |
|---|---|
| Columns with few distinct values | Boolean, status with 3 values — not selective enough |
| Tiny tables | Seq scan is faster than index overhead |
| Columns rarely queried | Indexes slow down writes |

---

## Index Types

### B-tree (Default)

```sql
CREATE INDEX idx_name ON table(column);
-- Good for: =, <, >, <=, >=, BETWEEN, IN, ORDER BY
```

The default. Handles equality and range queries. Use for 90% of cases.

### Hash

```sql
CREATE INDEX idx_email_hash ON customers USING hash(email);
-- Good for: = only (exact match)
-- Smaller than B-tree for equality-only lookups
```

### GIN (Generalized Inverted Index)

```sql
CREATE INDEX idx_payload_gin ON orders USING gin(payload jsonb_path_ops);
-- Good for: JSONB containment, arrays, full-text search
```

### GiST (Generalized Search Tree)

```sql
CREATE INDEX idx_location_gist ON stores USING gist(location);
-- Good for: geometric data, ranges, nearest-neighbor
```

---

## Composite Indexes: Column Order Matters

```sql
CREATE INDEX idx_orders_status_date ON orders(status, order_date);
```

This index helps:
- `WHERE status = 'completed'` ✅
- `WHERE status = 'completed' AND order_date > '2024-01-01'` ✅
- `WHERE order_date > '2024-01-01'` ❌ (can't skip the first column)

**Rule**: Put the most selective column first. Put equality conditions before range conditions.

```sql
-- ✅ Good: equality first, range second
CREATE INDEX idx_orders_status_date ON orders(status, order_date);
-- Helps: WHERE status = 'completed' AND order_date > '2024-06-01'

-- ❌ Less useful: range first
CREATE INDEX idx_orders_date_status ON orders(order_date, status);
-- Can't efficiently use status after a range scan on date
```

---

## Partial Indexes: Index Only What Matters

"Most queries filter for completed orders. Why index cancelled ones?"

```sql
CREATE INDEX idx_orders_completed ON orders(customer_id, order_date)
WHERE status = 'completed';
```

Smaller index. Faster lookups. Only includes rows where `status = 'completed'`.

```sql
-- This query uses the partial index:
SELECT * FROM orders WHERE status = 'completed' AND customer_id = 5;

-- This query CANNOT use it:
SELECT * FROM orders WHERE status = 'pending' AND customer_id = 5;
```

---

## Covering Indexes (INCLUDE)

If the index contains all columns the query needs, Postgres doesn't need to visit the table at all — an "index-only scan."

```sql
CREATE INDEX idx_orders_covering ON orders(customer_id, status)
INCLUDE (total_cents, order_date);
```

```sql
-- This can be answered entirely from the index:
SELECT total_cents, order_date
FROM orders
WHERE customer_id = 5 AND status = 'completed';
```

---

## Fixing The Slow Query

Step by step:

### 1. Add Missing Indexes

```sql
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_tickets_customer_id ON tickets(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
```

### 2. Eliminate the Correlated Subquery

```sql
-- Before: correlated subquery (runs 50,000 times)
(SELECT count(*) FROM tickets t WHERE t.customer_id = c.id)

-- After: LEFT JOIN with aggregate (runs once)
WITH ticket_counts AS (
    SELECT customer_id, count(*) AS ticket_count
    FROM tickets
    GROUP BY customer_id
)
SELECT
    c.name,
    c.plan,
    count(o.id) AS orders,
    sum(o.total_cents) / 100.0 AS revenue,
    max(o.order_date) AS last_order,
    COALESCE(tc.ticket_count, 0) AS ticket_count
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id AND o.status = 'completed'
LEFT JOIN ticket_counts tc ON tc.customer_id = c.id
GROUP BY c.id, c.name, c.plan, tc.ticket_count
ORDER BY revenue DESC NULLS LAST;
```

### 3. Verify

```sql
EXPLAIN ANALYZE ...
-- Execution Time: 12ms (down from 47,000ms)
```

Silent Sasha sends 👍.

---

## Common Performance Killers

| Problem | Symptom | Fix |
|---|---|---|
| Missing index on FK | Seq Scan on large table | Add index |
| Correlated subquery | Nested Loop with high loops count | Rewrite as JOIN or CTE |
| `SELECT *` | Reads unnecessary columns | Select only needed columns |
| Function on indexed column | Index not used | Rewrite condition |
| Implicit type cast | Index not used | Match types exactly |
| `LIKE '%prefix'` | Can't use B-tree index | Use trigram index or full-text |

### Function on Indexed Column

```sql
-- ❌ Index on order_date NOT used (function wraps the column)
SELECT * FROM orders WHERE extract(year FROM order_date) = 2024;

-- ✅ Index on order_date IS used (column is bare)
SELECT * FROM orders WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01';
```

---

## ANALYZE: Keep Statistics Fresh

Postgres uses statistics about your data to choose the best plan. After bulk inserts or deletes, update them:

```sql
ANALYZE orders;
ANALYZE customers;
-- Or analyze everything:
ANALYZE;
```

Without fresh statistics, Postgres might choose a sequential scan when an index scan would be faster.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Command                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
EXPLAIN query                   │ Show query plan (no execution)
EXPLAIN ANALYZE query           │ Show plan + actual timing
CREATE INDEX name ON tbl(col)   │ B-tree index (default)
CREATE INDEX ... WHERE cond     │ Partial index
CREATE INDEX ... INCLUDE (cols) │ Covering index
DROP INDEX name                 │ Remove an index
ANALYZE table                   │ Update planner statistics
────────────────────────────────┼──────────────────────────────────────
Seq Scan                        │ Full table scan (slow on big tables)
Index Scan                      │ Uses index to find rows
Index Only Scan                 │ Answered entirely from index
Bitmap Index Scan               │ Index → bitmap → table (multiple matches)
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The dashboard is fast. Then two reports run at the same time. One updates a customer's plan. The other reads the same customer's revenue. The revenue report shows stale data — or worse, partially updated data.

You need transactions. Isolation levels. Locking.

---

[← Chapter 10: Dates & Times](chapter-10-dates.md) | [Chapter 12: Transactions →](chapter-12-transactions.md)

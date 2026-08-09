# Chapter 44: SQL with PostgreSQL — From Basics to High-Performance Queries

## What you'll learn

- SQL fundamentals: SELECT, WHERE, JOIN, GROUP BY, ORDER BY
- Data definition: CREATE TABLE, constraints, data types
- PostgreSQL-specific features: CTEs, window functions, JSONB, arrays
- Indexing: how indexes work, when to add them, composite indexes
- Query analysis: EXPLAIN ANALYZE, reading execution plans
- Performance: avoiding N+1, query optimisation patterns, partitioning
- Build: design and query a real schema (e-commerce with orders, products, users)

---

## PART 1: SQL Fundamentals

## 44.1 Setup

```sql
-- Connect to PostgreSQL
psql -U postgres -d mydb

-- Create a database
CREATE DATABASE ecommerce;
\c ecommerce  -- connect to it
```

## 44.2 Create tables

```sql
-- Users
CREATE TABLE users (
    id          SERIAL PRIMARY KEY,          -- auto-increment integer
    email       VARCHAR(255) UNIQUE NOT NULL,
    name        VARCHAR(100) NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW(),
    is_active   BOOLEAN DEFAULT true
);

-- Products
CREATE TABLE products (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    description TEXT,
    price       DECIMAL(10, 2) NOT NULL,     -- 10 digits total, 2 after decimal
    stock       INTEGER NOT NULL DEFAULT 0,
    category    VARCHAR(50),
    tags        TEXT[],                       -- PostgreSQL array
    metadata    JSONB,                        -- PostgreSQL JSON
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Orders
CREATE TABLE orders (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    status      VARCHAR(20) NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending', 'paid', 'shipped', 'delivered', 'cancelled')),
    total       DECIMAL(10, 2) NOT NULL,
    ordered_at  TIMESTAMP DEFAULT NOW(),
    shipped_at  TIMESTAMP
);

-- Order items (many-to-many: orders ↔ products)
CREATE TABLE order_items (
    id          SERIAL PRIMARY KEY,
    order_id    INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id  INTEGER NOT NULL REFERENCES products(id),
    quantity    INTEGER NOT NULL CHECK (quantity > 0),
    unit_price  DECIMAL(10, 2) NOT NULL       -- price at time of purchase
);

-- Reviews
CREATE TABLE reviews (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    product_id  INTEGER NOT NULL REFERENCES products(id),
    rating      INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment     TEXT,
    created_at  TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, product_id)              -- one review per user per product
);
```

**Key constraints:**
| Constraint | Purpose |
|-----------|---------|
| `PRIMARY KEY` | Unique identifier, auto-indexed |
| `NOT NULL` | Column must have a value |
| `UNIQUE` | No duplicate values |
| `REFERENCES` (FK) | Must exist in referenced table |
| `CHECK` | Custom validation |
| `DEFAULT` | Value when not specified |
| `ON DELETE CASCADE` | Delete children when parent is deleted |

## 44.3 INSERT data

```sql
-- Single row
INSERT INTO users (email, name) VALUES ('alice@example.com', 'Alice');

-- Multiple rows
INSERT INTO products (name, price, category, stock, tags) VALUES
    ('Laptop Pro', 1299.99, 'electronics', 50, ARRAY['computer', 'portable']),
    ('Wireless Mouse', 29.99, 'electronics', 200, ARRAY['peripheral', 'wireless']),
    ('Desk Lamp', 45.00, 'furniture', 100, ARRAY['lighting', 'office']),
    ('Notebook', 12.50, 'stationery', 500, ARRAY['paper', 'writing']),
    ('Mechanical Keyboard', 149.99, 'electronics', 75, ARRAY['peripheral', 'mechanical']);

-- Insert with RETURNING (get the generated ID back)
INSERT INTO orders (user_id, status, total)
VALUES (1, 'paid', 1329.98)
RETURNING id;
```

## 44.4 SELECT — querying data

```sql
-- All columns, all rows
SELECT * FROM products;

-- Specific columns
SELECT name, price, category FROM products;

-- WHERE clause (filtering)
SELECT * FROM products WHERE category = 'electronics';
SELECT * FROM products WHERE price > 100 AND stock > 0;
SELECT * FROM products WHERE category IN ('electronics', 'furniture');
SELECT * FROM products WHERE name ILIKE '%keyboard%';  -- case-insensitive
SELECT * FROM products WHERE tags @> ARRAY['wireless'];  -- array contains

-- Sorting
SELECT * FROM products ORDER BY price DESC;
SELECT * FROM products ORDER BY category ASC, price DESC;

-- Limit + Offset (pagination)
SELECT * FROM products ORDER BY id LIMIT 10 OFFSET 20;  -- page 3 (0-indexed)

-- Aliases
SELECT name AS product_name, price * 1.1 AS price_with_tax FROM products;

-- DISTINCT
SELECT DISTINCT category FROM products;

-- NULL handling
SELECT * FROM orders WHERE shipped_at IS NULL;
SELECT COALESCE(shipped_at, 'Not shipped') FROM orders;  -- default if null
```

## 44.5 JOINs — combining tables

```sql
-- INNER JOIN: only matching rows from both tables
SELECT o.id AS order_id, u.name, o.total, o.status
FROM orders o
INNER JOIN users u ON o.user_id = u.id;

-- LEFT JOIN: all rows from left + matching from right (NULL if no match)
SELECT u.name, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.name;
-- Shows users WITH and WITHOUT orders (0 count for those with none)

-- Multiple JOINs (order details)
SELECT
    o.id AS order_id,
    u.name AS customer,
    p.name AS product,
    oi.quantity,
    oi.unit_price,
    oi.quantity * oi.unit_price AS line_total
FROM orders o
JOIN users u ON o.user_id = u.id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
WHERE o.status = 'delivered'
ORDER BY o.ordered_at DESC;
```

**JOIN types:**
```
INNER JOIN:  only rows that match in BOTH tables
LEFT JOIN:   all rows from LEFT + matches from right (NULL if none)
RIGHT JOIN:  all rows from RIGHT + matches from left (NULL if none)
FULL JOIN:   all rows from BOTH (NULL where no match)
CROSS JOIN:  every row × every row (cartesian product — rarely useful)
```

## 44.6 Aggregation — GROUP BY

```sql
-- Count orders per status
SELECT status, COUNT(*) AS count
FROM orders
GROUP BY status
ORDER BY count DESC;

-- Revenue per category
SELECT p.category, SUM(oi.quantity * oi.unit_price) AS revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.id
GROUP BY p.category
ORDER BY revenue DESC;

-- Average rating per product
SELECT p.name, AVG(r.rating)::DECIMAL(3,1) AS avg_rating, COUNT(r.id) AS review_count
FROM products p
LEFT JOIN reviews r ON p.id = r.product_id
GROUP BY p.id, p.name
HAVING COUNT(r.id) >= 3  -- only products with 3+ reviews
ORDER BY avg_rating DESC;

-- Aggregate functions: COUNT, SUM, AVG, MIN, MAX, STRING_AGG, ARRAY_AGG
SELECT
    category,
    COUNT(*) AS product_count,
    MIN(price) AS cheapest,
    MAX(price) AS most_expensive,
    AVG(price)::DECIMAL(10,2) AS avg_price,
    STRING_AGG(name, ', ') AS product_list
FROM products
GROUP BY category;
```

## 44.7 Subqueries

```sql
-- Scalar subquery (returns single value)
SELECT name, price,
    price - (SELECT AVG(price) FROM products) AS diff_from_avg
FROM products;

-- IN subquery (returns a list)
SELECT * FROM users
WHERE id IN (SELECT DISTINCT user_id FROM orders WHERE total > 500);

-- EXISTS (check if related rows exist — usually faster than IN)
SELECT * FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o
    WHERE o.user_id = u.id AND o.status = 'delivered'
);

-- Correlated subquery (references outer query)
SELECT p.name, p.price,
    (SELECT COUNT(*) FROM order_items oi WHERE oi.product_id = p.id) AS times_ordered
FROM products p
ORDER BY times_ordered DESC;
```

---

## PART 2: Intermediate — CTEs, Window Functions, PostgreSQL Features

## 44.8 CTEs (Common Table Expressions) — readable complex queries

```sql
-- CTE = named temporary result set (like a variable for queries)
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', o.ordered_at) AS month,
        SUM(o.total) AS revenue
    FROM orders o
    WHERE o.status != 'cancelled'
    GROUP BY DATE_TRUNC('month', o.ordered_at)
)
SELECT month, revenue,
    LAG(revenue) OVER (ORDER BY month) AS prev_month,
    revenue - LAG(revenue) OVER (ORDER BY month) AS growth
FROM monthly_revenue
ORDER BY month;

-- Multiple CTEs
WITH
top_customers AS (
    SELECT user_id, SUM(total) AS lifetime_value
    FROM orders
    WHERE status != 'cancelled'
    GROUP BY user_id
    ORDER BY lifetime_value DESC
    LIMIT 100
),
their_favorite_category AS (
    SELECT tc.user_id, p.category, COUNT(*) AS purchases
    FROM top_customers tc
    JOIN orders o ON tc.user_id = o.user_id
    JOIN order_items oi ON o.id = oi.order_id
    JOIN products p ON oi.product_id = p.id
    GROUP BY tc.user_id, p.category
)
SELECT u.name, tc.lifetime_value, tfc.category AS favorite_category
FROM top_customers tc
JOIN users u ON tc.user_id = u.id
JOIN LATERAL (
    SELECT category FROM their_favorite_category
    WHERE user_id = tc.user_id
    ORDER BY purchases DESC LIMIT 1
) tfc ON true;
```

## 44.9 Window functions — analytics without GROUP BY

```sql
-- ROW_NUMBER: rank each product within its category by price
SELECT name, category, price,
    ROW_NUMBER() OVER (PARTITION BY category ORDER BY price DESC) AS rank_in_category
FROM products;

-- Running total
SELECT ordered_at, total,
    SUM(total) OVER (ORDER BY ordered_at) AS running_total
FROM orders
WHERE status != 'cancelled';

-- Moving average (last 7 orders)
SELECT ordered_at, total,
    AVG(total) OVER (ORDER BY ordered_at ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS moving_avg_7
FROM orders;

-- Percentage of total
SELECT category, SUM(price) AS category_total,
    SUM(price) * 100.0 / SUM(SUM(price)) OVER () AS percentage
FROM products
GROUP BY category;

-- LAG/LEAD (previous/next row value)
SELECT ordered_at, total,
    LAG(total) OVER (ORDER BY ordered_at) AS prev_order_total,
    total - LAG(total) OVER (ORDER BY ordered_at) AS diff_from_prev
FROM orders;

-- DENSE_RANK (no gaps in ranking)
SELECT name, price,
    DENSE_RANK() OVER (ORDER BY price DESC) AS price_rank
FROM products;

-- NTILE (divide into N equal groups)
SELECT name, price,
    NTILE(4) OVER (ORDER BY price) AS price_quartile
FROM products;
```

**Window function anatomy:**
```sql
function() OVER (
    PARTITION BY column     -- group rows (like GROUP BY but without collapsing)
    ORDER BY column         -- sort within partition
    ROWS BETWEEN ... AND ... -- frame (which rows to include in calculation)
)
```

## 44.10 PostgreSQL-specific features

```sql
-- JSONB (store and query JSON documents)
INSERT INTO products (name, price, category, stock, metadata)
VALUES ('Smart Watch', 299.99, 'electronics', 30,
    '{"brand": "TechCo", "specs": {"battery": "48h", "waterproof": true}, "colors": ["black", "silver"]}');

-- Query JSONB
SELECT name, metadata->>'brand' AS brand                    -- text extraction
FROM products WHERE metadata @> '{"specs": {"waterproof": true}}';  -- contains

SELECT name FROM products
WHERE metadata->'specs'->>'battery' = '48h';               -- nested access

-- JSONB indexing (GIN)
CREATE INDEX idx_products_metadata ON products USING GIN (metadata);

-- Array operations
SELECT name FROM products WHERE 'wireless' = ANY(tags);    -- any element matches
SELECT name FROM products WHERE tags && ARRAY['portable', 'wireless']; -- overlap

-- Generate series (useful for filling gaps in time-series)
SELECT generate_series('2024-01-01'::date, '2024-12-31'::date, '1 month'::interval) AS month;

-- LATERAL JOIN (correlated subquery in FROM clause)
SELECT u.name, latest_order.total, latest_order.ordered_at
FROM users u
CROSS JOIN LATERAL (
    SELECT total, ordered_at FROM orders
    WHERE user_id = u.id
    ORDER BY ordered_at DESC LIMIT 1
) latest_order;

-- UPSERT (INSERT or UPDATE on conflict)
INSERT INTO reviews (user_id, product_id, rating, comment)
VALUES (1, 5, 4, 'Great product!')
ON CONFLICT (user_id, product_id)
DO UPDATE SET rating = EXCLUDED.rating, comment = EXCLUDED.comment;
```

---

## PART 3: Indexing & Performance

## 44.11 How indexes work

```
Without index (Sequential Scan):
  Table: [row1, row2, row3, ..., row1000000]
  Query: WHERE email = 'alice@example.com'
  → Scan ALL 1,000,000 rows. O(n).

With B-Tree index:
  Index: balanced tree sorted by email
         ┌─── "m" ───┐
        /              \
   "alice"..."liam"   "nancy"..."zoe"
      /                    \
  "alice" → row 42       "zoe" → row 999

  → Find in O(log n). For 1M rows: ~20 comparisons instead of 1M.
```

## 44.12 Creating indexes

```sql
-- Single-column index
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_products_category ON products(category);

-- Composite index (multi-column — order matters!)
CREATE INDEX idx_orders_user_status ON orders(user_id, status);
-- Supports: WHERE user_id = 1
--           WHERE user_id = 1 AND status = 'paid'
-- Does NOT help: WHERE status = 'paid' (first column must be used)

-- Partial index (only index rows matching a condition)
CREATE INDEX idx_active_orders ON orders(user_id)
WHERE status NOT IN ('delivered', 'cancelled');
-- Smaller index, faster for queries that filter on active orders

-- Expression index
CREATE INDEX idx_products_name_lower ON products(LOWER(name));
-- Supports: WHERE LOWER(name) = 'laptop pro'

-- GIN index (for JSONB, arrays, full-text search)
CREATE INDEX idx_products_tags ON products USING GIN(tags);
CREATE INDEX idx_products_metadata ON products USING GIN(metadata jsonb_path_ops);

-- Unique index (also enforces uniqueness)
CREATE UNIQUE INDEX idx_users_email ON users(email);

-- Covering index (INCLUDE: extra columns stored in index — avoids table lookup)
CREATE INDEX idx_orders_user_covering ON orders(user_id)
INCLUDE (status, total, ordered_at);
-- Index-only scan: all data comes from the index, never touches the table
```

## 44.13 EXPLAIN ANALYZE — understand query execution

```sql
EXPLAIN ANALYZE
SELECT u.name, COUNT(o.id), SUM(o.total)
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.status = 'delivered'
GROUP BY u.name
ORDER BY SUM(o.total) DESC
LIMIT 10;
```

**Reading the output:**
```
Limit  (cost=1234..1235 rows=10) (actual time=45.2..45.3 rows=10 loops=1)
  -> Sort  (cost=1234..1245 rows=500) (actual time=45.1..45.2 rows=10 loops=1)
        Sort Key: sum(o.total) DESC
        -> HashAggregate  (cost=1100..1150 rows=500) (actual time=44.0..44.5 rows=500 loops=1)
              -> Hash Join  (cost=50..1000 rows=5000) (actual time=1.2..40.0 rows=5000 loops=1)
                    Hash Cond: (o.user_id = u.id)
                    -> Seq Scan on orders o  (cost=0..800 rows=5000) (actual time=0.1..30.0 rows=5000)
                          Filter: (status = 'delivered')
                          Rows Removed by Filter: 15000
                    -> Hash  (cost=30..30 rows=1000) (actual time=0.5..0.5 rows=1000 loops=1)
                          -> Seq Scan on users u (cost=0..30 rows=1000)
Planning Time: 0.5 ms
Execution Time: 45.5 ms
```

**What to look for:**
| Bad sign | Meaning | Fix |
|----------|---------|-----|
| `Seq Scan` on large table | Full table scan (no index used) | Add appropriate index |
| `Rows Removed by Filter: 15000` | Scanned 20K, kept 5K | Index on filter column |
| `Sort` with high cost | Sorting in memory/disk | Index matching ORDER BY |
| `Nested Loop` with many rows | O(n×m) join | Check join condition has index |
| `actual rows` >> `rows` estimate | Bad statistics | Run `ANALYZE tablename` |

## 44.14 Index selection decision tree

```
Does your query:

Filter (WHERE)?
├── Equality (= 'value') → B-Tree index on that column
├── Range (BETWEEN, >, <) → B-Tree (column must be leftmost in composite)
├── LIKE 'prefix%' → B-Tree (only prefix matches, not '%middle%')
├── LIKE '%anywhere%' → pg_trgm GIN index (trigram)
├── Array contains (@>) → GIN index
├── JSONB contains (@>) → GIN index (jsonb_path_ops)
└── Full-text search → GIN index (tsvector)

JOIN (ON a.id = b.foreign_id)?
└── Index on the foreign key column (b.foreign_id)

ORDER BY?
└── Index matching the sort order (can combine with WHERE in composite index)

GROUP BY + aggregate?
└── Consider covering index (INCLUDE aggregated columns)
```

---

## PART 4: High-Performance Patterns

## 44.15 Avoiding common performance killers

```sql
-- ❌ SELECT * (fetches all columns — wastes I/O if you only need 2)
SELECT * FROM orders WHERE user_id = 1;

-- ✅ Select only what you need
SELECT id, status, total FROM orders WHERE user_id = 1;

-- ❌ N+1 problem (one query per user to get their orders)
-- Application code: for each user → SELECT * FROM orders WHERE user_id = ?

-- ✅ Batch in one query
SELECT u.id, u.name, o.id AS order_id, o.total
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.id IN (1, 2, 3, 4, 5);

-- ❌ Function on indexed column (index not used)
SELECT * FROM users WHERE LOWER(email) = 'alice@example.com';

-- ✅ Expression index or store lowercase
CREATE INDEX idx_users_email_lower ON users(LOWER(email));
-- or just store email as lowercase

-- ❌ OFFSET for deep pagination (scans all skipped rows)
SELECT * FROM products ORDER BY id LIMIT 20 OFFSET 100000; -- scans 100,020 rows!

-- ✅ Cursor-based pagination (keyset pagination)
SELECT * FROM products WHERE id > 100000 ORDER BY id LIMIT 20; -- seeks directly

-- ❌ Counting with COUNT(*) on huge table
SELECT COUNT(*) FROM orders; -- scans entire table

-- ✅ Approximate count (instant)
SELECT reltuples::bigint FROM pg_class WHERE relname = 'orders';

-- ❌ OR on different columns (can't use single index efficiently)
SELECT * FROM products WHERE category = 'electronics' OR price < 10;

-- ✅ Use UNION ALL (each branch uses its own index)
SELECT * FROM products WHERE category = 'electronics'
UNION ALL
SELECT * FROM products WHERE price < 10 AND category != 'electronics';
```

## 44.16 Batch operations

```sql
-- Batch INSERT (much faster than individual inserts)
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
VALUES
    (1, 1, 2, 1299.99),
    (1, 2, 1, 29.99),
    (1, 5, 1, 149.99);

-- Batch UPDATE with VALUES list
UPDATE products SET stock = v.new_stock
FROM (VALUES (1, 48), (2, 199), (3, 95)) AS v(id, new_stock)
WHERE products.id = v.id;

-- COPY for bulk loading (fastest: bypasses SQL parser)
COPY products(name, price, category, stock)
FROM '/path/to/products.csv' WITH (FORMAT csv, HEADER true);
```

## 44.17 Materialized views (pre-computed queries)

```sql
-- Slow query you run often: revenue dashboard
CREATE MATERIALIZED VIEW mv_daily_revenue AS
SELECT
    DATE_TRUNC('day', ordered_at) AS day,
    COUNT(*) AS order_count,
    SUM(total) AS revenue,
    AVG(total) AS avg_order_value
FROM orders
WHERE status != 'cancelled'
GROUP BY DATE_TRUNC('day', ordered_at);

-- Query the materialized view (instant — pre-computed)
SELECT * FROM mv_daily_revenue WHERE day >= NOW() - INTERVAL '30 days';

-- Refresh (run periodically — e.g., every hour via cron)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_revenue;
-- CONCURRENTLY: doesn't lock reads during refresh (requires unique index)
CREATE UNIQUE INDEX ON mv_daily_revenue(day);
```

## 44.18 Partitioning (huge tables)

```sql
-- Partition by range (time-based — most common)
CREATE TABLE orders_partitioned (
    id          SERIAL,
    user_id     INTEGER NOT NULL,
    status      VARCHAR(20) NOT NULL,
    total       DECIMAL(10, 2) NOT NULL,
    ordered_at  TIMESTAMP NOT NULL
) PARTITION BY RANGE (ordered_at);

-- Create partitions
CREATE TABLE orders_2024_q1 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');
CREATE TABLE orders_2024_q2 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');
CREATE TABLE orders_2024_q3 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2024-07-01') TO ('2024-10-01');
CREATE TABLE orders_2024_q4 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2024-10-01') TO ('2025-01-01');

-- Queries automatically target correct partition:
SELECT * FROM orders_partitioned WHERE ordered_at >= '2024-06-01';
-- PostgreSQL only scans Q2 + Q3 (partition pruning)
```

**When to partition:**
- Table > 100GB
- Queries always filter by the partition key (date, region)
- Need to efficiently drop old data (`DROP TABLE orders_2022_q1` — instant vs DELETE)

---

## PART 5: Real-World Queries

## 44.19 E-commerce analytics queries

```sql
-- Top 10 customers by lifetime value
SELECT u.name, u.email,
    COUNT(o.id) AS total_orders,
    SUM(o.total) AS lifetime_value,
    MAX(o.ordered_at) AS last_order
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.status != 'cancelled'
GROUP BY u.id, u.name, u.email
ORDER BY lifetime_value DESC
LIMIT 10;

-- Products never ordered
SELECT p.name, p.price, p.stock
FROM products p
LEFT JOIN order_items oi ON p.id = oi.product_id
WHERE oi.id IS NULL;

-- Revenue by month with year-over-year comparison
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', ordered_at) AS month,
        SUM(total) AS revenue
    FROM orders WHERE status != 'cancelled'
    GROUP BY DATE_TRUNC('month', ordered_at)
)
SELECT
    month,
    revenue,
    LAG(revenue, 12) OVER (ORDER BY month) AS same_month_last_year,
    CASE WHEN LAG(revenue, 12) OVER (ORDER BY month) > 0
         THEN ((revenue - LAG(revenue, 12) OVER (ORDER BY month)) /
               LAG(revenue, 12) OVER (ORDER BY month) * 100)::DECIMAL(5,1)
         ELSE NULL
    END AS yoy_growth_pct
FROM monthly
ORDER BY month DESC;

-- Cohort retention (users who ordered in month X, how many reorder in month X+1, X+2, ...)
WITH first_order AS (
    SELECT user_id, DATE_TRUNC('month', MIN(ordered_at)) AS cohort_month
    FROM orders GROUP BY user_id
),
activity AS (
    SELECT o.user_id,
        fo.cohort_month,
        DATE_TRUNC('month', o.ordered_at) AS activity_month,
        EXTRACT(MONTH FROM AGE(DATE_TRUNC('month', o.ordered_at), fo.cohort_month)) AS months_since
    FROM orders o
    JOIN first_order fo ON o.user_id = fo.user_id
)
SELECT
    cohort_month,
    months_since,
    COUNT(DISTINCT user_id) AS active_users
FROM activity
GROUP BY cohort_month, months_since
ORDER BY cohort_month, months_since;
```

---

## Summary

✅ SQL basics: SELECT, WHERE, JOIN (INNER/LEFT/RIGHT), GROUP BY, ORDER BY, LIMIT
✅ Table design: types, constraints (PK, FK, UNIQUE, CHECK, DEFAULT, CASCADE)
✅ Subqueries: scalar, IN, EXISTS, correlated
✅ CTEs: readable multi-step queries with WITH
✅ Window functions: ROW_NUMBER, SUM OVER, LAG/LEAD, RANK, NTILE, moving averages
✅ PostgreSQL features: JSONB queries, arrays, LATERAL, UPSERT, generate_series
✅ Indexing: B-Tree, GIN, partial, expression, covering — and WHEN to use each
✅ EXPLAIN ANALYZE: reading execution plans, spotting Seq Scans, bad estimates
✅ Performance killers: SELECT *, N+1, OFFSET pagination, functions on indexed columns
✅ Advanced: batch operations, materialized views, partitioning
✅ Real analytics: lifetime value, cohort retention, year-over-year comparison

## Key takeaways

**Indexes make or break performance.** A query scanning 1M rows in 500ms drops to 0.1ms with the right index. But indexes slow writes and consume storage — don't blindly index everything.

**EXPLAIN ANALYZE is your best friend.** Don't guess why a query is slow — look at the plan. Seq Scan on a large table? Add an index. Nested Loop with 10K iterations? Check join conditions.

**Window functions replace self-joins.** Any time you need "previous row", "running total", "rank within group", or "compare to average" — window functions do it in one pass without JOINs.

**Cursor pagination > OFFSET pagination.** `WHERE id > last_seen ORDER BY id LIMIT 20` is O(1) regardless of page number. `OFFSET 100000 LIMIT 20` still scans 100,020 rows.

---

→ [Back to Chapter 43: JavaScript Physics](./43-JAVASCRIPT-PHYSICS.md)

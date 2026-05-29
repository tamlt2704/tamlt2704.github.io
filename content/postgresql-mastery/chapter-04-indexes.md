[prev: Intermediate Queries](chapter-03-queries.md) | [next: Advanced Features](chapter-05-advanced-features.md)

# Chapter 4: Indexes

## Why Indexes Matter

Without an index, PostgreSQL performs a sequential scan — reading every row. Indexes let it jump directly to matching rows.

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    status VARCHAR(20) NOT NULL,
    total NUMERIC(10, 2),
    created_at TIMESTAMP DEFAULT now(),
    metadata JSONB DEFAULT '{}'
);

INSERT INTO orders (customer_id, status, total, created_at)
SELECT
    (random() * 1000)::int,
    (ARRAY['pending','shipped','delivered','cancelled'])[1 + (random()*3)::int],
    (random() * 500)::numeric(10,2),
    now() - (random() * interval '365 days')
FROM generate_series(1, 100000);

ANALYZE orders;
```

## EXPLAIN ANALYZE

```sql
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 42;
```

Without index:

```
Seq Scan on orders  (cost=0.00..2137.00 rows=98 width=64) (actual time=0.021..12.345 rows=102 loops=1)
  Filter: (customer_id = 42)
  Rows Removed by Filter: 99898
Execution Time: 12.401 ms
```

## B-tree Index (Default)

Best for: equality and range queries.

```sql
CREATE INDEX idx_orders_customer_id ON orders (customer_id);

EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 42;
```

With index:

```
Index Scan using idx_orders_customer_id on orders  (cost=0.29..10.52 rows=98 width=64) (actual time=0.025..0.156 rows=102 loops=1)
  Index Cond: (customer_id = 42)
Execution Time: 0.198 ms
```

## Hash Index

Equality-only lookups:

```sql
CREATE INDEX idx_orders_status_hash ON orders USING hash (status);

EXPLAIN ANALYZE SELECT * FROM orders WHERE status = 'shipped';
```

## GIN Index (Generalized Inverted Index)

Best for: JSONB, arrays, full-text search.

```sql
UPDATE orders SET metadata = jsonb_build_object(
    'priority', CASE WHEN random() > 0.5 THEN 'high' ELSE 'low' END
) WHERE id <= 50000;

CREATE INDEX idx_orders_metadata_gin ON orders USING gin (metadata);

EXPLAIN ANALYZE
SELECT * FROM orders WHERE metadata @> '{"priority": "high"}';
```

## GiST Index (Generalized Search Tree)

Best for: geometric data, ranges, nearest-neighbor.

```sql
CREATE TABLE reservations (
    id SERIAL PRIMARY KEY,
    room_id INT,
    during TSRANGE NOT NULL
);

CREATE INDEX idx_reservations_during ON reservations USING gist (during);

SELECT * FROM reservations
WHERE during && tsrange('2024-01-15 10:00', '2024-01-15 12:00');
```

## BRIN Index (Block Range Index)

Best for: large, physically ordered tables (time-series). Very small.

```sql
CREATE INDEX idx_orders_created_brin ON orders USING brin (created_at);

EXPLAIN ANALYZE
SELECT * FROM orders WHERE created_at > now() - interval '7 days';
```

## Partial Indexes

Index only a subset of rows:

```sql
CREATE INDEX idx_orders_pending ON orders (customer_id)
WHERE status = 'pending';

EXPLAIN ANALYZE
SELECT * FROM orders WHERE status = 'pending' AND customer_id = 42;
```

## Expression Indexes

```sql
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL
);

CREATE INDEX idx_accounts_email_lower ON accounts (lower(email));

SELECT * FROM accounts WHERE lower(email) = 'alice@example.com';
```

## Covering Indexes (INCLUDE)

Enable index-only scans by including extra columns:

```sql
CREATE INDEX idx_orders_customer_covering
ON orders (customer_id) INCLUDE (status, total);

EXPLAIN ANALYZE
SELECT customer_id, status, total FROM orders WHERE customer_id = 42;
```

Look for "Index Only Scan" in the output.

## Multicolumn Indexes

```sql
CREATE INDEX idx_orders_status_created ON orders (status, created_at);

-- Uses index (leftmost prefix):
EXPLAIN ANALYZE
SELECT * FROM orders WHERE status = 'pending' ORDER BY created_at;

-- Does NOT use this index efficiently:
EXPLAIN ANALYZE
SELECT * FROM orders WHERE created_at > '2024-01-01';
```

Column order matters: filter on leftmost column(s) first.

## When NOT to Index

Avoid indexing when:

- Table is small (under 10k rows)
- Column has very low cardinality (boolean 50/50)
- Table is write-heavy, rarely queried on that column
- A covering index already includes the column

Find unused indexes:

```sql
SELECT schemaname, relname AS table_name,
    indexrelname AS index_name, idx_scan AS times_used,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
```

## Managing Indexes

```sql
-- Create without locking the table
CREATE INDEX CONCURRENTLY idx_orders_total ON orders (total);

-- Drop
DROP INDEX idx_orders_total;

-- Rebuild
REINDEX INDEX idx_orders_customer_id;

-- Check size
SELECT pg_size_pretty(pg_relation_size('idx_orders_customer_id'));
```

## Exercises

1. Create a 100k-row table and compare EXPLAIN ANALYZE before/after adding a B-tree index

2. Create a partial index for `status = 'pending'` and verify it's used

3. Create a GIN index on JSONB and query with `@>`

4. Create a multicolumn index and test which patterns use it

5. Find unused indexes using `pg_stat_user_indexes`

6. Create a covering index with INCLUDE and verify "Index Only Scan"

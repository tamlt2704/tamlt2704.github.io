[prev: JSONB](chapter-06-jsonb.md) | [next: Security](chapter-08-security.md)

# Chapter 7: Performance Tuning

## Reading EXPLAIN ANALYZE

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM orders WHERE customer_id = 42 AND status = 'pending';
```

Key things to look for:

- **Seq Scan** vs **Index Scan** — sequential is slow on large tables
- **actual time** — first row time..last row time in ms
- **rows** — estimated vs actual (big mismatch = stale statistics)
- **Buffers: shared hit/read** — hit = from cache, read = from disk

```
Index Scan using idx_orders_customer_id on orders
  (cost=0.42..8.44 rows=1 width=64)
  (actual time=0.028..0.035 rows=3 loops=1)
  Index Cond: (customer_id = 42)
  Filter: (status = 'pending')
  Buffers: shared hit=4
Planning Time: 0.12 ms
Execution Time: 0.06 ms
```

## Memory Configuration

### shared_buffers

PostgreSQL's main cache. Set to 25% of total RAM:

```
shared_buffers = 4GB   -- for a 16GB server
```

### work_mem

Memory per sort/hash operation. Be careful — multiplied by concurrent queries:

```
work_mem = 16MB   -- default 4MB is often too low
```

Check if queries spill to disk:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders ORDER BY total DESC;
-- Look for "Sort Method: external merge" = spilling to disk
```

### effective_cache_size

Tells the planner how much memory is available (OS cache + shared_buffers). Set to 75% of RAM:

```
effective_cache_size = 12GB   -- for a 16GB server
```

## Connection Pooling with PgBouncer

PostgreSQL forks a process per connection. At 200+ connections, use a pooler.

PgBouncer config (`pgbouncer.ini`):

```
[databases]
myapp = host=localhost port=5432 dbname=myapp

[pgbouncer]
listen_port = 6432
listen_addr = 0.0.0.0
auth_type = scram-sha-256
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
```

Application connects to port 6432 instead of 5432.

## VACUUM and ANALYZE

PostgreSQL uses MVCC — dead rows accumulate after updates/deletes.

```sql
-- Manual vacuum
VACUUM orders;

-- Vacuum and reclaim space (locks table briefly)
VACUUM FULL orders;

-- Update statistics only
ANALYZE orders;

-- Both
VACUUM ANALYZE orders;

-- Check dead tuples
SELECT relname, n_dead_tup, n_live_tup,
    round(n_dead_tup::numeric / GREATEST(n_live_tup, 1) * 100, 2) AS dead_pct
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;
```

## Autovacuum Tuning

Default autovacuum triggers at 20% dead rows. For large tables, tune per-table:

```sql
ALTER TABLE orders SET (
    autovacuum_vacuum_threshold = 1000,
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_threshold = 500,
    autovacuum_analyze_scale_factor = 0.02
);
```

Global settings in `postgresql.conf`:

```
autovacuum_max_workers = 4
autovacuum_naptime = 30s
autovacuum_vacuum_cost_limit = 1000
```

## Query Optimization Patterns

### Avoid SELECT \*

```sql
-- Bad: fetches all columns, can't use index-only scan
SELECT * FROM orders WHERE customer_id = 42;

-- Good: only what you need
SELECT id, total, status FROM orders WHERE customer_id = 42;
```

### Use EXISTS instead of IN for subqueries

```sql
-- Slower with large subquery result
SELECT * FROM customers
WHERE id IN (SELECT customer_id FROM orders WHERE total > 100);

-- Faster: stops at first match
SELECT * FROM customers c
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id AND o.total > 100);
```

### Batch operations

```sql
-- Instead of 1000 individual INSERTs, use multi-row:
INSERT INTO orders (customer_id, status, total)
VALUES (1, 'pending', 50), (2, 'pending', 75), (3, 'pending', 100);

-- Or COPY for bulk loading:
COPY orders (customer_id, status, total) FROM '/tmp/orders.csv' CSV HEADER;
```

### Pagination with keyset instead of OFFSET

```sql
-- Bad: OFFSET scans and discards rows
SELECT * FROM orders ORDER BY id LIMIT 20 OFFSET 10000;

-- Good: keyset pagination
SELECT * FROM orders WHERE id > 10000 ORDER BY id LIMIT 20;
```

## pg_stat_statements

Track query performance across all executions:

```sql
CREATE EXTENSION pg_stat_statements;

-- Top 10 slowest queries by total time
SELECT
    calls,
    round(total_exec_time::numeric, 2) AS total_ms,
    round(mean_exec_time::numeric, 2) AS avg_ms,
    query
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
```

## Slow Query Log

In `postgresql.conf`:

```
log_min_duration_statement = 500   -- log queries taking > 500ms
log_statement = 'none'             -- don't log all statements in prod
log_line_prefix = '%t [%p] %u@%d '
```

## Exercises

1. Run EXPLAIN ANALYZE on a query and identify whether it uses an index or seq scan

2. Check `pg_stat_user_tables` for tables with high dead tuple counts

3. Configure `work_mem` and verify a sort no longer spills to disk

4. Enable `pg_stat_statements` and find your slowest queries

5. Rewrite a query using `EXISTS` instead of `IN` and compare plans

6. Implement keyset pagination and compare with OFFSET using EXPLAIN ANALYZE

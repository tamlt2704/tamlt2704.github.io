[prev: Indexes](chapter-04-indexes.md) | [next: JSONB](chapter-06-jsonb.md)

# Chapter 5: Advanced Features

## Views

A view is a saved query:

```sql
CREATE VIEW active_orders AS
SELECT o.id, o.customer_id, o.total, o.created_at
FROM orders o
WHERE o.status = 'pending';

-- Use like a table
SELECT * FROM active_orders WHERE total > 100;

-- Drop
DROP VIEW active_orders;
```

## Materialized Views

Stores the result physically — faster reads, must be refreshed:

```sql
CREATE MATERIALIZED VIEW monthly_sales AS
SELECT
    date_trunc('month', created_at) AS month,
    COUNT(*) AS order_count,
    SUM(total) AS revenue
FROM orders
GROUP BY date_trunc('month', created_at)
ORDER BY month;

-- Query (fast, reads stored data)
SELECT * FROM monthly_sales;

-- Refresh when data changes
REFRESH MATERIALIZED VIEW monthly_sales;

-- Refresh without locking reads
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_sales;
```

For CONCURRENTLY, you need a unique index:

```sql
CREATE UNIQUE INDEX idx_monthly_sales_month ON monthly_sales (month);
```

## Stored Procedures (PL/pgSQL)

### Functions

```sql
CREATE OR REPLACE FUNCTION get_department_budget(dept_id INT)
RETURNS NUMERIC AS $$
DECLARE
    total_budget NUMERIC;
BEGIN
    SELECT SUM(salary) INTO total_budget
    FROM employees
    WHERE department_id = dept_id;

    RETURN COALESCE(total_budget, 0);
END;
$$ LANGUAGE plpgsql;

-- Call it
SELECT get_department_budget(1);
```

### Procedures (no return value, can manage transactions)

```sql
CREATE OR REPLACE PROCEDURE transfer_employee(
    emp_id INT,
    new_dept_id INT
)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE employees SET department_id = new_dept_id WHERE id = emp_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Employee % not found', emp_id;
    END IF;
END;
$$;

-- Call with CALL
CALL transfer_employee(1, 2);
```

## Triggers

Execute a function automatically on table events:

```sql
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name TEXT,
    action TEXT,
    row_id INT,
    changed_at TIMESTAMP DEFAULT now(),
    old_data JSONB,
    new_data JSONB
);

CREATE OR REPLACE FUNCTION log_employee_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (table_name, action, row_id, old_data, new_data)
        VALUES ('employees', 'UPDATE', OLD.id, to_jsonb(OLD), to_jsonb(NEW));
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (table_name, action, row_id, old_data)
        VALUES ('employees', 'DELETE', OLD.id, to_jsonb(OLD));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_employee_audit
AFTER UPDATE OR DELETE ON employees
FOR EACH ROW EXECUTE FUNCTION log_employee_changes();
```

## Generated Columns

Computed automatically from other columns:

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    price NUMERIC(10, 2),
    tax_rate NUMERIC(4, 3) DEFAULT 0.08,
    total_price NUMERIC(10, 2) GENERATED ALWAYS AS (price * (1 + tax_rate)) STORED
);

INSERT INTO products (price) VALUES (100.00);
SELECT * FROM products;
```

Output:

```
 id | price  | tax_rate | total_price
----+--------+----------+-------------
  1 | 100.00 |    0.080 |      108.00
```

## Table Inheritance

```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    event_type TEXT,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE click_events (
    url TEXT,
    element TEXT
) INHERITS (events);

CREATE TABLE purchase_events (
    amount NUMERIC(10, 2),
    product_id INT
) INHERITS (events);

-- Query all events
SELECT * FROM events;

-- Query only clicks
SELECT * FROM ONLY click_events;
```

## Partitioning

### Range Partitioning

```sql
CREATE TABLE measurements (
    id SERIAL,
    sensor_id INT,
    value NUMERIC,
    recorded_at TIMESTAMP NOT NULL
) PARTITION BY RANGE (recorded_at);

CREATE TABLE measurements_2024_q1 PARTITION OF measurements
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE measurements_2024_q2 PARTITION OF measurements
    FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');

CREATE TABLE measurements_2024_q3 PARTITION OF measurements
    FOR VALUES FROM ('2024-07-01') TO ('2024-10-01');

-- Insert goes to correct partition automatically
INSERT INTO measurements (sensor_id, value, recorded_at)
VALUES (1, 23.5, '2024-02-15 10:00:00');
```

### List Partitioning

```sql
CREATE TABLE logs (
    id SERIAL,
    level TEXT NOT NULL,
    message TEXT,
    created_at TIMESTAMP DEFAULT now()
) PARTITION BY LIST (level);

CREATE TABLE logs_info PARTITION OF logs FOR VALUES IN ('info');
CREATE TABLE logs_warn PARTITION OF logs FOR VALUES IN ('warn');
CREATE TABLE logs_error PARTITION OF logs FOR VALUES IN ('error');
```

### Hash Partitioning

```sql
CREATE TABLE sessions (
    id UUID DEFAULT gen_random_uuid(),
    user_id INT,
    data JSONB
) PARTITION BY HASH (id);

CREATE TABLE sessions_0 PARTITION OF sessions FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE sessions_1 PARTITION OF sessions FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE sessions_2 PARTITION OF sessions FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE sessions_3 PARTITION OF sessions FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

## Foreign Data Wrappers

Query external data sources as if they were local tables:

```sql
-- Install the extension
CREATE EXTENSION postgres_fdw;

-- Define the remote server
CREATE SERVER remote_db
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host 'remote-host', port '5432', dbname 'other_db');

-- Map local user to remote user
CREATE USER MAPPING FOR appuser
SERVER remote_db
OPTIONS (user 'remote_user', password 'remote_pass');

-- Import a remote table
CREATE FOREIGN TABLE remote_customers (
    id INT,
    name TEXT,
    email TEXT
) SERVER remote_db OPTIONS (table_name 'customers');

-- Query it like a local table
SELECT * FROM remote_customers WHERE id = 42;
```

## Exercises

1. Create a view that shows employees with their department name and salary rank

2. Create a materialized view for monthly order statistics and refresh it

3. Write a PL/pgSQL function that returns the top N earners in a department

4. Create a trigger that prevents salary decreases (raises an exception)

5. Create a range-partitioned table for daily logs and insert data spanning multiple partitions

6. Create a generated column that computes `full_name` from `first_name` and `last_name`

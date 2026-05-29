[prev: Setup](chapter-01-setup.md) | [next: Intermediate Queries](chapter-03-queries.md)

# Chapter 2: SQL Basics

## CREATE TABLE and Data Types

```sql
CREATE TABLE users (
    id          SERIAL PRIMARY KEY,
    username    VARCHAR(50) NOT NULL UNIQUE,
    email       TEXT NOT NULL,
    age         INT,
    balance     NUMERIC(10, 2) DEFAULT 0.00,
    is_active   BOOLEAN DEFAULT true,
    created_at  TIMESTAMP DEFAULT now(),
    external_id UUID DEFAULT gen_random_uuid(),
    metadata    JSONB DEFAULT '{}',
    tags        TEXT[] DEFAULT '{}'
);
```

### Type Reference

| Type           | Description                   | Example                 |
| -------------- | ----------------------------- | ----------------------- |
| `SERIAL`       | Auto-incrementing integer     | `1, 2, 3...`            |
| `VARCHAR(n)`   | Variable-length string, max n | `'hello'`               |
| `TEXT`         | Unlimited-length string       | `'any length...'`       |
| `INT`          | 4-byte integer                | `42`                    |
| `NUMERIC(p,s)` | Exact decimal                 | `99999.99`              |
| `BOOLEAN`      | true/false                    | `true`                  |
| `TIMESTAMP`    | Date and time                 | `'2024-01-15 10:30:00'` |
| `UUID`         | Universally unique identifier | `'a0eebc99-9c0b-...'`   |
| `JSONB`        | Binary JSON                   | `'{"key": "value"}'`    |
| `TEXT[]`       | Array of text                 | `'{"a","b","c"}'`       |

## INSERT

```sql
-- Single row
INSERT INTO users (username, email, age)
VALUES ('alice', 'alice@example.com', 30);

-- Multiple rows
INSERT INTO users (username, email, age, tags)
VALUES
    ('bob', 'bob@example.com', 25, '{"developer","golang"}'),
    ('carol', 'carol@example.com', 35, '{"manager"}');

-- Insert and return the created row
INSERT INTO users (username, email)
VALUES ('dave', 'dave@example.com')
RETURNING id, username, created_at;
```

Output of RETURNING:

```
 id | username |         created_at
----+----------+----------------------------
  4 | dave     | 2024-01-15 10:30:00.123456
```

## SELECT

```sql
-- All columns
SELECT * FROM users;

-- Specific columns
SELECT username, email, age FROM users;

-- With alias
SELECT username AS name, age * 12 AS age_in_months FROM users;

-- Distinct values
SELECT DISTINCT is_active FROM users;
```

## WHERE Clause

```sql
SELECT * FROM users WHERE age > 30;
SELECT * FROM users WHERE username = 'alice';
SELECT * FROM users WHERE age >= 25 AND is_active = true;
SELECT * FROM users WHERE age IS NULL;
SELECT * FROM users WHERE email LIKE '%@example.com';
SELECT * FROM users WHERE username ILIKE 'A%';  -- case-insensitive
SELECT * FROM users WHERE username IN ('alice', 'bob', 'carol');
SELECT * FROM users WHERE age BETWEEN 25 AND 35;
SELECT * FROM users WHERE 'developer' = ANY(tags);
```

## UPDATE

```sql
UPDATE users SET age = 31 WHERE username = 'alice';

UPDATE users
SET is_active = false, metadata = '{"reason": "inactive"}'
WHERE age < 20;

-- Update with RETURNING
UPDATE users SET balance = balance + 100
WHERE username = 'bob'
RETURNING username, balance;
```

## DELETE

```sql
DELETE FROM users WHERE is_active = false;

-- Delete and return what was deleted
DELETE FROM users WHERE username = 'dave'
RETURNING *;

-- Delete all rows (careful!)
DELETE FROM users;
```

## ORDER BY

```sql
SELECT * FROM users ORDER BY age;
SELECT * FROM users ORDER BY created_at DESC;
SELECT * FROM users ORDER BY is_active DESC, username ASC;
SELECT * FROM users ORDER BY age NULLS LAST;
```

## LIMIT and OFFSET

```sql
-- First 10 rows
SELECT * FROM users ORDER BY id LIMIT 10;

-- Pagination: page 2, 10 per page
SELECT * FROM users ORDER BY id LIMIT 10 OFFSET 10;
```

## Combining It All

```sql
SELECT username, email, age
FROM users
WHERE is_active = true AND age IS NOT NULL
ORDER BY age DESC
LIMIT 5;
```

## Exercises

1. Create a `products` table with: `id` (serial), `name` (varchar 100), `price` (numeric 8,2), `in_stock` (boolean), `created_at` (timestamp with default)

2. Insert 5 products with varying prices and stock status

3. Select all products in stock costing less than 50, ordered by price descending

4. Update the cheapest product price by 10 percent using RETURNING

5. Delete all out-of-stock products and show what was deleted

6. Create a table with a `UUID` primary key and a `JSONB` column. Insert a row and query it.

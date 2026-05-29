[prev: Advanced Features](chapter-05-advanced-features.md) | [next: Performance Tuning](chapter-07-performance.md)

# Chapter 6: JSONB

## Storing JSONB

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    attrs JSONB DEFAULT '{}'
);

INSERT INTO products (name, attrs) VALUES
    ('Laptop', '{"brand": "Dell", "ram": 16, "storage": "512GB", "ports": ["USB-C", "HDMI"]}'),
    ('Phone', '{"brand": "Apple", "ram": 8, "storage": "256GB", "color": "black"}'),
    ('Monitor', '{"brand": "LG", "size": 27, "resolution": "4K", "ports": ["HDMI", "DP"]}');
```

## Querying JSONB

### Extract operators

```sql
-- -> returns JSONB element
SELECT name, attrs->'brand' FROM products;
-- Result: "Dell" (with quotes, it's JSONB)

-- ->> returns TEXT
SELECT name, attrs->>'brand' AS brand FROM products;
-- Result: Dell (no quotes, it's text)

-- Nested access
SELECT attrs->'ports'->>0 AS first_port FROM products WHERE name = 'Laptop';
-- Result: USB-C
```

### Containment operator `@>`

```sql
-- Find products with brand = Apple
SELECT * FROM products WHERE attrs @> '{"brand": "Apple"}';

-- Find products with 16GB RAM
SELECT * FROM products WHERE attrs @> '{"ram": 16}';
```

### Existence operator `?`

```sql
-- Has a "color" key?
SELECT * FROM products WHERE attrs ? 'color';

-- Has any of these keys?
SELECT * FROM products WHERE attrs ?| array['color', 'size'];

-- Has all of these keys?
SELECT * FROM products WHERE attrs ?& array['brand', 'ram'];
```

### Path queries

```sql
-- jsonpath (PostgreSQL 12+)
SELECT * FROM products
WHERE attrs @? '$.ports[*] ? (@ == "HDMI")';
```

## Indexing JSONB with GIN

```sql
-- Index all keys and values
CREATE INDEX idx_products_attrs ON products USING gin (attrs);

-- Now containment queries use the index:
EXPLAIN ANALYZE
SELECT * FROM products WHERE attrs @> '{"brand": "Dell"}';

-- Index a specific path for equality lookups
CREATE INDEX idx_products_brand ON products ((attrs->>'brand'));

SELECT * FROM products WHERE attrs->>'brand' = 'Dell';
```

## JSONB Aggregation Functions

### jsonb_agg

```sql
SELECT jsonb_agg(name) AS all_names FROM products;
-- Result: ["Laptop", "Phone", "Monitor"]
```

### jsonb_build_object

```sql
SELECT jsonb_build_object(
    'product', name,
    'brand', attrs->>'brand'
) AS summary
FROM products;
```

Output:

```
              summary
-----------------------------------
 {"brand": "Dell", "product": "Laptop"}
 {"brand": "Apple", "product": "Phone"}
 {"brand": "LG", "product": "Monitor"}
```

### jsonb_object_agg

```sql
SELECT jsonb_object_agg(name, attrs->>'brand') FROM products;
-- Result: {"Laptop": "Dell", "Phone": "Apple", "Monitor": "LG"}
```

## Modifying JSONB

```sql
-- Set a key
UPDATE products
SET attrs = attrs || '{"warranty": "2 years"}'
WHERE name = 'Laptop';

-- Remove a key
UPDATE products
SET attrs = attrs - 'color'
WHERE name = 'Phone';

-- Set nested value
UPDATE products
SET attrs = jsonb_set(attrs, '{ram}', '32')
WHERE name = 'Laptop';
```

## When to Use JSONB vs Normalized Tables

Use JSONB when:

- Schema varies per row (product attributes, user preferences)
- You receive external JSON and need to store it flexibly
- You query by a few known keys but the full schema is unpredictable
- Rapid prototyping where schema is evolving

Use normalized tables when:

- You need referential integrity (foreign keys)
- You frequently query/filter/join on the data
- You need unique constraints on fields
- Data structure is stable and well-known

## Hybrid Approach

Best of both worlds — structured columns for common fields, JSONB for the rest:

```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT now(),
    -- Structured, indexed, constrained
    payload JSONB DEFAULT '{}'
    -- Flexible per event type
);

CREATE INDEX idx_events_type ON events (event_type);
CREATE INDEX idx_events_user ON events (user_id);
CREATE INDEX idx_events_payload ON events USING gin (payload);

-- Different event types, different payloads
INSERT INTO events (event_type, user_id, payload) VALUES
    ('page_view', 1, '{"url": "/home", "duration_ms": 3200}'),
    ('purchase', 1, '{"product_id": 42, "amount": 29.99}'),
    ('signup', 2, '{"referrer": "google", "plan": "free"}');
```

## Exercises

1. Create a table with a JSONB column and insert 5 rows with varying structures

2. Query using `@>` to find rows matching a specific key-value pair

3. Use `?` to find rows that have a specific key

4. Create a GIN index and verify it's used with EXPLAIN ANALYZE

5. Use `jsonb_set` to update a nested value without replacing the entire object

6. Design a hybrid table for a multi-tenant SaaS where each tenant has custom fields

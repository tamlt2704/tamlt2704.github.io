# Chapter 15: "Store Flexible Product Attributes"

[← Chapter 14: Partitioning](chapter-14-partitioning.md) | [Chapter 16: Access Control →](chapter-16-access-control.md)

---

## The Request

Priya: "Products need flexible attributes. T-shirts have color and size. Electronics have weight and warranty. Enterprise customers want custom fields. I don't want a table with 50 nullable columns."

You could create a key-value table (EAV pattern). But that's slow, hard to query, and impossible to validate.

PostgreSQL has a better answer: JSONB.

---

## JSONB: Structured Flexibility

```sql
ALTER TABLE products ADD COLUMN attributes JSONB DEFAULT '{}';

UPDATE products SET attributes = '{"color": "blue", "size": "L", "material": "cotton"}'
WHERE name = 'Basic Dashboard';

UPDATE products SET attributes = '{"integrations": ["slack", "teams", "email"], "max_users": 50}'
WHERE name = 'Pro Dashboard';

UPDATE products SET attributes = '{"sla_hours": 4, "dedicated_support": true, "max_users": null}'
WHERE name = 'Enterprise Suite';
```

### Querying JSONB

```sql
-- Get a specific key
SELECT name, attributes->>'color' AS color
FROM products
WHERE attributes->>'color' IS NOT NULL;

-- Filter by JSONB value
SELECT name, attributes
FROM products
WHERE attributes->>'max_users' IS NOT NULL;

-- Check if a key exists
SELECT name FROM products
WHERE attributes ? 'integrations';

-- Check if JSONB contains a value
SELECT name FROM products
WHERE attributes @> '{"dedicated_support": true}';
```

### JSONB Operators

| Operator | Meaning | Example |
|---|---|---|
| `->` | Get JSON value (as JSON) | `attributes->'color'` → `"blue"` |
| `->>` | Get JSON value (as text) | `attributes->>'color'` → `blue` |
| `#>` | Get nested path (as JSON) | `attributes#>'{address,city}'` |
| `#>>` | Get nested path (as text) | `attributes#>>'{address,city}'` |
| `?` | Key exists? | `attributes ? 'color'` |
| `?|` | Any key exists? | `attributes ?| array['color','size']` |
| `?&` | All keys exist? | `attributes ?& array['color','size']` |
| `@>` | Contains? | `attributes @> '{"color":"blue"}'` |
| `<@` | Contained by? | `'{"color":"blue"}' <@ attributes` |
| `||` | Merge/concatenate | `attributes || '{"new_key": "val"}'` |
| `-` | Remove key | `attributes - 'color'` |

### Modifying JSONB

```sql
-- Add/update a key
UPDATE products
SET attributes = attributes || '{"weight_kg": 0.5}'
WHERE name = 'Basic Dashboard';

-- Remove a key
UPDATE products
SET attributes = attributes - 'color'
WHERE name = 'Basic Dashboard';

-- Set a nested value
UPDATE products
SET attributes = jsonb_set(attributes, '{max_users}', '100')
WHERE name = 'Pro Dashboard';
```

---

## Indexing JSONB

Without an index, JSONB queries do sequential scans. Add a GIN index:

```sql
-- Index all keys and values (most flexible)
CREATE INDEX idx_products_attributes ON products USING gin(attributes);

-- Index for containment queries (@>)
CREATE INDEX idx_products_attrs_path ON products USING gin(attributes jsonb_path_ops);
```

| Index Type | Supports | Size |
|---|---|---|
| `gin(col)` | `?`, `?|`, `?&`, `@>`, `<@` | Larger |
| `gin(col jsonb_path_ops)` | `@>` only | Smaller, faster |

For a specific key you query often:

```sql
-- Expression index on a specific JSONB key
CREATE INDEX idx_products_max_users ON products ((attributes->>'max_users'));
```

---

## JSONB Aggregation

```sql
-- Build a JSON object from query results
SELECT jsonb_object_agg(name, price_cents / 100.0) AS price_list
FROM products
WHERE active = true;

-- → {"Basic Dashboard": 39.00, "Pro Dashboard": 99.00, ...}

-- Expand JSONB array into rows
SELECT name, integration
FROM products,
     jsonb_array_elements_text(attributes->'integrations') AS integration
WHERE attributes ? 'integrations';
```

```
     name      | integration
---------------+-------------
 Pro Dashboard | slack
 Pro Dashboard | teams
 Pro Dashboard | email
```

---

## Arrays: When JSONB Is Overkill

For simple lists of the same type, PostgreSQL arrays are lighter than JSONB:

```sql
ALTER TABLE products ADD COLUMN tags TEXT[] DEFAULT '{}';

UPDATE products SET tags = ARRAY['popular', 'featured']
WHERE name = 'Pro Dashboard';

UPDATE products SET tags = ARRAY['enterprise', 'sla', 'priority']
WHERE name = 'Enterprise Suite';
```

### Array Operations

```sql
-- Contains element?
SELECT name FROM products WHERE 'popular' = ANY(tags);

-- Contains all elements?
SELECT name FROM products WHERE tags @> ARRAY['enterprise', 'sla'];

-- Array length
SELECT name, array_length(tags, 1) AS tag_count FROM products;

-- Append to array
UPDATE products SET tags = array_append(tags, 'new-tag')
WHERE name = 'Pro Dashboard';

-- Remove from array
UPDATE products SET tags = array_remove(tags, 'featured')
WHERE name = 'Pro Dashboard';

-- Unnest (expand array into rows)
SELECT name, unnest(tags) AS tag FROM products;
```

### Indexing Arrays

```sql
CREATE INDEX idx_products_tags ON products USING gin(tags);
-- Now @> and && (overlap) queries use the index
```

---

## Full-Text Search

Hank: "Customers want to search tickets by keyword. Not exact match — fuzzy. 'dashboard loading' should find 'Dashboard not loading' and 'slow dashboard load'."

### The Basics

```sql
-- Convert text to searchable tokens
SELECT to_tsvector('english', 'Dashboard not loading after update');
-- → 'dashboard':1 'load':3 'updat':5

-- Create a search query
SELECT to_tsquery('english', 'dashboard & loading');
-- → 'dashboard' & 'load'

-- Match: does the document match the query?
SELECT to_tsvector('english', 'Dashboard not loading') @@ to_tsquery('english', 'dashboard & loading');
-- → true
```

### Searching Tickets

```sql
-- Add a tsvector column for fast searching
ALTER TABLE tickets ADD COLUMN search_vector tsvector;

-- Populate it
UPDATE tickets
SET search_vector = to_tsvector('english', subject);

-- Keep it updated with a trigger
CREATE TRIGGER tickets_search_update
    BEFORE INSERT OR UPDATE ON tickets
    FOR EACH ROW EXECUTE FUNCTION
    tsvector_update_trigger(search_vector, 'pg_catalog.english', subject);

-- Index it
CREATE INDEX idx_tickets_search ON tickets USING gin(search_vector);
```

### Querying

```sql
-- Simple search
SELECT subject, priority, status
FROM tickets
WHERE search_vector @@ to_tsquery('english', 'dashboard');

-- Phrase search
SELECT subject
FROM tickets
WHERE search_vector @@ phraseto_tsquery('english', 'not loading');

-- Ranked results
SELECT
    subject,
    ts_rank(search_vector, to_tsquery('english', 'dashboard')) AS relevance
FROM tickets
WHERE search_vector @@ to_tsquery('english', 'dashboard')
ORDER BY relevance DESC;
```

### Search Query Syntax

| Syntax | Meaning |
|---|---|
| `word1 & word2` | Both words must appear |
| `word1 | word2` | Either word |
| `!word` | Word must NOT appear |
| `word1 <-> word2` | Words must be adjacent |
| `word:*` | Prefix match (starts with) |

```sql
-- "dashboard" AND ("slow" OR "loading")
SELECT * FROM tickets
WHERE search_vector @@ to_tsquery('english', 'dashboard & (slow | loading)');

-- Prefix search: anything starting with "dash"
SELECT * FROM tickets
WHERE search_vector @@ to_tsquery('english', 'dash:*');
```

### Searching Multiple Columns

```sql
-- Combine subject and description with different weights
ALTER TABLE tickets ADD COLUMN description TEXT;

UPDATE tickets
SET search_vector =
    setweight(to_tsvector('english', COALESCE(subject, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(description, '')), 'B');
```

Weight A (subject) ranks higher than weight B (description) in `ts_rank`.

---

## Fuzzy Matching: pg_trgm

For typo-tolerant search (Hank types "dashbord" instead of "dashboard"):

```sql
-- Enable the extension
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Similarity search
SELECT name, similarity(name, 'dashbord') AS sim
FROM products
WHERE similarity(name, 'dashbord') > 0.3
ORDER BY sim DESC;

-- Trigram index for LIKE/ILIKE
CREATE INDEX idx_customers_name_trgm ON customers USING gin(name gin_trgm_ops);

-- Now ILIKE uses the index:
SELECT * FROM customers WHERE name ILIKE '%mega%';
```

---

## When to Use What

| Need | Use |
|---|---|
| Flexible key-value attributes | JSONB |
| Simple list of same-type values | Array |
| Keyword search with ranking | Full-text search (tsvector) |
| Typo-tolerant / fuzzy match | pg_trgm |
| Exact structured data | Regular columns |

**Rule**: If you query a JSONB key in every single query, it should probably be a regular column. JSONB is for truly flexible, schema-less data.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Feature                         │ Key Syntax
────────────────────────────────┼──────────────────────────────────────
JSONB access                    │ col->>'key', col#>>'{nested,path}'
JSONB containment               │ col @> '{"key": "val"}'
JSONB modify                    │ col || '{}', col - 'key', jsonb_set()
JSONB index                     │ USING gin(col) or gin(col jsonb_path_ops)
────────────────────────────────┼──────────────────────────────────────
Array contains                  │ 'val' = ANY(col), col @> ARRAY[...]
Array modify                    │ array_append(), array_remove()
Array index                     │ USING gin(col)
────────────────────────────────┼──────────────────────────────────────
Full-text vector                │ to_tsvector('english', text)
Full-text query                 │ to_tsquery('english', 'word & word')
Full-text match                 │ tsvector @@ tsquery
Full-text rank                  │ ts_rank(vector, query)
Full-text index                 │ USING gin(vector_col)
────────────────────────────────┼──────────────────────────────────────
Fuzzy match                     │ similarity(a, b), a % b
Trigram index                   │ USING gin(col gin_trgm_ops)
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Priya: "The sales team shouldn't see customer emails. The intern shouldn't be able to delete anything. Maya needs read access to everything but write access to nothing."

Role-based access control. Row-level security. The database as gatekeeper.

---

[← Chapter 14: Partitioning](chapter-14-partitioning.md) | [Chapter 16: Access Control →](chapter-16-access-control.md)

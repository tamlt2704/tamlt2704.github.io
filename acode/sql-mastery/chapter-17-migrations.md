# Chapter 17: "Migrate Without Downtime"

[← Chapter 16: Access Control](chapter-16-access-control.md) | [Chapter 18: Backups & Replication →](chapter-18-backups-replication.md)

---

## The Request

Priya: "We're adding a `company_size` field to customers. And renaming `total_cents` to `amount_cents` in orders. And splitting the `name` column into `first_name` and `last_name`."

You: "I'll just ALTER TABLE—"

Maya: "The app is serving 500 requests per second. If you lock the table for 30 seconds, that's 15,000 failed requests. Do it without downtime."

---

## Safe vs Dangerous ALTER TABLE

### Safe (No Lock or Brief Lock)

```sql
-- Add a nullable column (instant, no rewrite)
ALTER TABLE customers ADD COLUMN company_size TEXT;

-- Add a column with a default (PG 11+: instant, no rewrite)
ALTER TABLE customers ADD COLUMN tier TEXT DEFAULT 'standard';

-- Drop a column (marks as invisible, no rewrite)
ALTER TABLE customers DROP COLUMN legacy_field;

-- Rename a column (instant)
ALTER TABLE customers RENAME COLUMN company_size TO org_size;

-- Add a constraint as NOT VALID (doesn't scan existing rows)
ALTER TABLE customers ADD CONSTRAINT valid_tier
    CHECK (tier IN ('standard', 'premium', 'vip')) NOT VALID;
```

### Dangerous (Locks Table, Rewrites, or Blocks)

```sql
-- ❌ Adding NOT NULL without a default (scans all rows)
ALTER TABLE customers ALTER COLUMN company_size SET NOT NULL;

-- ❌ Changing column type (rewrites entire table)
ALTER TABLE orders ALTER COLUMN total_cents TYPE BIGINT;

-- ❌ Adding a unique constraint (scans + locks)
ALTER TABLE customers ADD CONSTRAINT unique_email UNIQUE (email);

-- ❌ Creating an index (locks writes on older PG versions)
CREATE INDEX idx_customers_tier ON customers(tier);
```

---

## Safe Migration Patterns

### Pattern 1: Add NOT NULL Safely

```sql
-- Step 1: Add column as nullable (instant)
ALTER TABLE customers ADD COLUMN company_size TEXT;

-- Step 2: Backfill in batches (no lock)
UPDATE customers SET company_size = 'unknown' WHERE company_size IS NULL AND id BETWEEN 1 AND 10000;
UPDATE customers SET company_size = 'unknown' WHERE company_size IS NULL AND id BETWEEN 10001 AND 20000;
-- ... repeat until all rows are filled

-- Step 3: Add NOT NULL constraint with NOT VALID (instant)
ALTER TABLE customers ADD CONSTRAINT customers_company_size_nn
    CHECK (company_size IS NOT NULL) NOT VALID;

-- Step 4: Validate the constraint (scans but doesn't lock writes)
ALTER TABLE customers VALIDATE CONSTRAINT customers_company_size_nn;

-- Step 5: Now safe to set NOT NULL (Postgres knows all rows pass)
ALTER TABLE customers ALTER COLUMN company_size SET NOT NULL;
```

### Pattern 2: Create Index Without Locking

```sql
-- ❌ Locks writes until complete
CREATE INDEX idx_customers_tier ON customers(tier);

-- ✅ Doesn't lock writes (takes longer but safe)
CREATE INDEX CONCURRENTLY idx_customers_tier ON customers(tier);
```

⚠️ `CONCURRENTLY` can't run inside a transaction. If it fails, you get an invalid index:

```sql
-- Check for invalid indexes
SELECT indexrelname, idx_scan
FROM pg_stat_user_indexes
WHERE indexrelname LIKE '%invalid%';

-- Drop and retry
DROP INDEX CONCURRENTLY idx_customers_tier;
CREATE INDEX CONCURRENTLY idx_customers_tier ON customers(tier);
```

### Pattern 3: Rename a Column Safely

You can't just rename — the app is using the old name.

```sql
-- Step 1: Add new column
ALTER TABLE orders ADD COLUMN amount_cents INTEGER;

-- Step 2: Backfill
UPDATE orders SET amount_cents = total_cents WHERE amount_cents IS NULL;

-- Step 3: Add trigger to keep both in sync during transition
CREATE OR REPLACE FUNCTION sync_amount_cents()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR NEW.total_cents IS DISTINCT FROM OLD.total_cents THEN
        NEW.amount_cents = NEW.total_cents;
    END IF;
    IF NEW.amount_cents IS DISTINCT FROM OLD.amount_cents THEN
        NEW.total_cents = NEW.amount_cents;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER sync_columns BEFORE INSERT OR UPDATE ON orders
FOR EACH ROW EXECUTE FUNCTION sync_amount_cents();

-- Step 4: Deploy app code to use new column name
-- Step 5: Remove trigger and old column
DROP TRIGGER sync_columns ON orders;
ALTER TABLE orders DROP COLUMN total_cents;
```

### Pattern 4: Change Column Type Safely

```sql
-- ❌ Rewrites entire table, locks it
ALTER TABLE orders ALTER COLUMN total_cents TYPE BIGINT;

-- ✅ Safe approach: new column + backfill + swap
ALTER TABLE orders ADD COLUMN total_cents_new BIGINT;
-- Backfill in batches...
-- Add sync trigger...
-- Deploy app to use new column...
-- Drop old column
```

### Pattern 5: Add Unique Constraint Safely

```sql
-- ❌ Scans and locks
ALTER TABLE customers ADD CONSTRAINT unique_email UNIQUE (email);

-- ✅ Create unique index concurrently, then add constraint using it
CREATE UNIQUE INDEX CONCURRENTLY idx_customers_email_unique ON customers(email);
ALTER TABLE customers ADD CONSTRAINT unique_email UNIQUE USING INDEX idx_customers_email_unique;
```

---

## Migration Tools

Don't run raw SQL in production. Use a migration tool that tracks what's been applied:

| Tool | Language | Style |
|---|---|---|
| Flyway | Java/any | Numbered SQL files |
| Liquibase | Java/any | XML/YAML/SQL changesets |
| Alembic | Python | Python migration scripts |
| golang-migrate | Go | SQL up/down files |
| sqitch | Any | Dependency-based SQL |
| Prisma Migrate | Node.js | Schema-driven |

### Migration File Structure

```
migrations/
├── V001__create_customers.sql
├── V002__create_orders.sql
├── V003__add_company_size.sql
├── V004__add_tier_column.sql
└── V005__create_index_concurrently.sql
```

Each file runs once, in order. The tool tracks which have been applied.

---

## Rollback Strategies

### Reversible Migrations

```sql
-- V003__add_company_size.sql (UP)
ALTER TABLE customers ADD COLUMN company_size TEXT;

-- V003__add_company_size_rollback.sql (DOWN)
ALTER TABLE customers DROP COLUMN company_size;
```

### Expand-Contract Pattern

For breaking changes, use three phases:

```
Phase 1 (Expand): Add new structure alongside old
Phase 2 (Migrate): Move app code to use new structure
Phase 3 (Contract): Remove old structure
```

```sql
-- Phase 1: Add new columns (backward compatible)
ALTER TABLE customers ADD COLUMN first_name TEXT;
ALTER TABLE customers ADD COLUMN last_name TEXT;

-- Phase 2: Backfill + deploy app using new columns
UPDATE customers SET
    first_name = split_part(name, ' ', 1),
    last_name = split_part(name, ' ', 2)
WHERE first_name IS NULL;

-- Phase 3: Drop old column (after app is fully migrated)
ALTER TABLE customers DROP COLUMN name;
```

Between phases, both old and new code work. No downtime.

---

## Lock Monitoring

If a migration does take a lock, monitor it:

```sql
-- See what's blocking what
SELECT
    blocked.pid AS blocked_pid,
    blocked_activity.query AS blocked_query,
    blocking.pid AS blocking_pid,
    blocking_activity.query AS blocking_query
FROM pg_catalog.pg_locks blocked
JOIN pg_catalog.pg_locks blocking
    ON blocking.locktype = blocked.locktype
    AND blocking.database IS NOT DISTINCT FROM blocked.database
    AND blocking.relation IS NOT DISTINCT FROM blocked.relation
    AND blocking.page IS NOT DISTINCT FROM blocked.page
    AND blocking.tuple IS NOT DISTINCT FROM blocked.tuple
    AND blocking.transactionid IS NOT DISTINCT FROM blocked.transactionid
    AND blocking.pid != blocked.pid
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking.pid
WHERE NOT blocked.granted;
```

### Set Lock Timeout

```sql
-- If you can't get a lock in 5 seconds, abort (don't wait forever)
SET lock_timeout = '5s';
ALTER TABLE customers ADD CONSTRAINT ...;
-- If it can't acquire the lock in 5s, it fails instead of blocking
```

---

## Quick Reference

```
────────────────────────────────────┬──────────────────────────────────────
Operation                           │ Safe?
────────────────────────────────────┼──────────────────────────────────────
ADD COLUMN (nullable)               │ ✅ Instant
ADD COLUMN with DEFAULT (PG 11+)    │ ✅ Instant
DROP COLUMN                         │ ✅ Instant (marks invisible)
RENAME COLUMN                       │ ✅ Instant
ADD CHECK ... NOT VALID             │ ✅ No scan
VALIDATE CONSTRAINT                 │ ✅ Scans but no write lock
CREATE INDEX CONCURRENTLY           │ ✅ No write lock
────────────────────────────────────┼──────────────────────────────────────
ALTER COLUMN TYPE                   │ ❌ Rewrites table
ADD NOT NULL (without check trick)  │ ❌ Scans all rows
ADD UNIQUE (without concurrent idx) │ ❌ Locks table
CREATE INDEX (without CONCURRENTLY) │ ⚠️ Locks writes
────────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

3 AM. Your phone buzzes. Silent Sasha: "DB crashed. Disk full. Last backup: 3 days ago."

Backups. Replication. Point-in-time recovery. The things you wish you'd set up before the crash.

---

[← Chapter 16: Access Control](chapter-16-access-control.md) | [Chapter 18: Backups & Replication →](chapter-18-backups-replication.md)

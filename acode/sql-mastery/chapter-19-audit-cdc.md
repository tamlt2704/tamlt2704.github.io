# Chapter 19: "Show Me Everything That Happened"

[← Chapter 18: Backups & Replication](chapter-18-backups-replication.md) | [Chapter 20: Final Review →](chapter-20-final-review.md)

---

## The Request

Priya, after the deletion incident: "I need to know WHO changed WHAT, WHEN, and from WHERE. Every table. Every change. Permanently."

And Maya adds: "The data warehouse team needs a real-time feed of changes. When an order is created or updated, they need to know within seconds — not wait for the nightly ETL."

Two problems. One chapter.

---

## Audit Trail: Trigger-Based

We built a basic audit trigger in Chapter 13. Let's make it production-grade:

```sql
-- Audit log table
CREATE TABLE audit_log (
    id          BIGSERIAL PRIMARY KEY,
    table_name  TEXT NOT NULL,
    operation   TEXT NOT NULL,  -- INSERT, UPDATE, DELETE
    row_id      TEXT,           -- primary key of affected row
    old_data    JSONB,
    new_data    JSONB,
    changed_fields TEXT[],      -- which columns changed (UPDATE only)
    changed_at  TIMESTAMPTZ DEFAULT now(),
    changed_by  TEXT DEFAULT current_user,
    app_user    TEXT,           -- application-level user (from session var)
    client_ip   INET DEFAULT inet_client_addr()
);

-- Index for common queries
CREATE INDEX idx_audit_table_time ON audit_log(table_name, changed_at DESC);
CREATE INDEX idx_audit_row ON audit_log(table_name, row_id);
```

### The Audit Function

```sql
CREATE OR REPLACE FUNCTION audit_trigger_func()
RETURNS TRIGGER AS $$
DECLARE
    row_id TEXT;
    changed TEXT[];
    col TEXT;
BEGIN
    -- Get the primary key value
    IF TG_OP = 'DELETE' THEN
        row_id := OLD.id::TEXT;
    ELSE
        row_id := NEW.id::TEXT;
    END IF;

    -- For updates, track which columns changed
    IF TG_OP = 'UPDATE' THEN
        FOR col IN SELECT column_name FROM information_schema.columns
                   WHERE table_name = TG_TABLE_NAME AND table_schema = TG_TABLE_SCHEMA
        LOOP
            IF to_jsonb(OLD) -> col IS DISTINCT FROM to_jsonb(NEW) -> col THEN
                changed := array_append(changed, col);
            END IF;
        END LOOP;

        -- Skip if nothing actually changed
        IF changed IS NULL OR array_length(changed, 1) IS NULL THEN
            RETURN NEW;
        END IF;
    END IF;

    INSERT INTO audit_log (table_name, operation, row_id, old_data, new_data, changed_fields, app_user)
    VALUES (
        TG_TABLE_NAME,
        TG_OP,
        row_id,
        CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN to_jsonb(OLD) END,
        CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN to_jsonb(NEW) END,
        changed,
        current_setting('app.current_user', true)  -- application user, if set
    );

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
```

### Apply to All Important Tables

```sql
CREATE TRIGGER audit_customers
    AFTER INSERT OR UPDATE OR DELETE ON customers
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

CREATE TRIGGER audit_orders
    AFTER INSERT OR UPDATE OR DELETE ON orders
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

CREATE TRIGGER audit_products
    AFTER INSERT OR UPDATE OR DELETE ON products
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();
```

### Querying the Audit Trail

```sql
-- "Who changed customer 2's plan?"
SELECT
    operation,
    changed_fields,
    old_data->>'plan' AS old_plan,
    new_data->>'plan' AS new_plan,
    changed_by,
    app_user,
    changed_at
FROM audit_log
WHERE table_name = 'customers' AND row_id = '2'
ORDER BY changed_at DESC;

-- "What happened in the last hour?"
SELECT table_name, operation, row_id, changed_by, changed_at
FROM audit_log
WHERE changed_at > now() - interval '1 hour'
ORDER BY changed_at DESC;

-- "Show me all deletes by user 'hank'"
SELECT *
FROM audit_log
WHERE operation = 'DELETE' AND (changed_by = 'hank' OR app_user = 'hank')
ORDER BY changed_at DESC;
```

### Setting Application User

Your app connects as `app_backend`, but you want to track which end-user made the change:

```sql
-- Application sets this before each request
SET LOCAL app.current_user = 'hank@datapulse.com';

-- Now any changes in this transaction are attributed to hank
UPDATE customers SET plan = 'enterprise' WHERE id = 2;
-- audit_log.app_user = 'hank@datapulse.com'
```

`SET LOCAL` only lasts for the current transaction — safe for connection pooling.

---

## Logical Replication: Streaming Changes

Physical replication copies everything. Logical replication lets you selectively stream changes to other systems.

### Setup: Publication and Subscription

**On the source database:**

```sql
-- Publish changes from specific tables
CREATE PUBLICATION datapulse_changes
    FOR TABLE customers, orders, order_items;

-- Or publish everything:
CREATE PUBLICATION all_changes FOR ALL TABLES;
```

**On the destination database:**

```sql
-- Subscribe to the publication
CREATE SUBSCRIPTION warehouse_sync
    CONNECTION 'host=source-db dbname=datapulse user=replicator password=...'
    PUBLICATION datapulse_changes;
```

Now every INSERT, UPDATE, DELETE on the source is replicated to the destination in near-real-time.

### Use Cases

| Scenario | How |
|---|---|
| Data warehouse sync | Publish → Subscribe on warehouse DB |
| Read replicas (selective) | Publish specific tables to read-only DB |
| Cross-service data sharing | Publish → Subscribe between microservices |
| Migration (zero-downtime) | Publish old DB → Subscribe on new DB |

---

## Change Data Capture (CDC)

CDC captures every change as an event stream. Tools like Debezium read PostgreSQL's WAL and emit events to Kafka, enabling real-time data pipelines.

### How It Works

```
PostgreSQL WAL → Debezium → Kafka → Consumers
                                      ├── Data Warehouse
                                      ├── Search Index (Elasticsearch)
                                      ├── Cache Invalidation
                                      └── Real-time Dashboard
```

### PostgreSQL Setup for CDC

```sql
-- postgresql.conf
-- wal_level = logical  (required for logical decoding)

-- Create a replication slot
SELECT pg_create_logical_replication_slot('debezium_slot', 'pgoutput');

-- Check active slots
SELECT slot_name, active, restart_lsn
FROM pg_replication_slots;
```

### Logical Decoding (Native)

You can read changes directly without external tools:

```sql
-- Create a slot
SELECT pg_create_logical_replication_slot('test_slot', 'test_decoding');

-- Make some changes
INSERT INTO customers (name, email, plan, country)
VALUES ('CDC Test', 'cdc@test.com', 'free', 'US');

-- Read the changes
SELECT * FROM pg_logical_slot_get_changes('test_slot', NULL, NULL);
```

```
    lsn    | xid |                          data
-----------+-----+-------------------------------------------------------
 0/1A2B3C4 | 742 | table public.customers: INSERT: id[integer]:16 name[text]:'CDC Test' ...
```

### Cleanup

```sql
-- Drop a replication slot (important! Unreferenced slots prevent WAL cleanup)
SELECT pg_drop_replication_slot('test_slot');
```

⚠️ Unused replication slots prevent WAL files from being recycled. This fills your disk. Always drop slots you're not using.

---

## Event Sourcing Pattern

Instead of storing current state, store every event that led to the current state:

```sql
CREATE TABLE customer_events (
    id          BIGSERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    event_type  TEXT NOT NULL,
    event_data  JSONB NOT NULL,
    occurred_at TIMESTAMPTZ DEFAULT now(),
    version     INTEGER NOT NULL
);

-- Unique constraint ensures no conflicting events
CREATE UNIQUE INDEX idx_customer_events_version
    ON customer_events(customer_id, version);

-- Insert events
INSERT INTO customer_events (customer_id, event_type, event_data, version) VALUES
(1, 'plan_changed', '{"from": "pro", "to": "enterprise", "reason": "upgrade"}', 1),
(1, 'address_updated', '{"country": "US", "city": "New York"}', 2),
(1, 'plan_changed', '{"from": "enterprise", "to": "pro", "reason": "downgrade"}', 3);

-- Rebuild current state from events
SELECT
    customer_id,
    event_type,
    event_data,
    occurred_at
FROM customer_events
WHERE customer_id = 1
ORDER BY version;
```

---

## Audit Retention and Archiving

The audit table grows forever. Manage it:

```sql
-- Partition audit_log by month for easy archiving
CREATE TABLE audit_log_partitioned (
    LIKE audit_log INCLUDING ALL
) PARTITION BY RANGE (changed_at);

-- Keep 3 months online, archive the rest
CREATE TABLE audit_log_2024_07 PARTITION OF audit_log_partitioned
    FOR VALUES FROM ('2024-07-01') TO ('2024-08-01');
-- ...

-- Archive old partitions
ALTER TABLE audit_log_partitioned DETACH PARTITION audit_log_2024_01;
-- Export to S3/cold storage, then drop
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Feature                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
Audit trigger                   │ Log every change with who/what/when
SET LOCAL app.current_user      │ Track application-level user
────────────────────────────────┼──────────────────────────────────────
CREATE PUBLICATION              │ Define which tables to stream
CREATE SUBSCRIPTION             │ Receive changes from a publication
────────────────────────────────┼──────────────────────────────────────
Logical replication slot        │ Track position in WAL for consumers
pg_logical_slot_get_changes()   │ Read decoded changes
wal_level = logical             │ Required for logical decoding/CDC
────────────────────────────────┼──────────────────────────────────────
Debezium / CDC                  │ Stream DB changes to Kafka
Event sourcing                  │ Store events, derive state
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Friday. The board meeting. Priya needs the database to be fast, correct, and reliable. You've built all the pieces. Time to put them together and prove it works.

---

[← Chapter 18: Backups & Replication](chapter-18-backups-replication.md) | [Chapter 20: Final Review →](chapter-20-final-review.md)
